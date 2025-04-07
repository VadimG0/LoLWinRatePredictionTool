import requests
from api import get_match_ids, get_match_details, extract_player_data
from database import setup_database, save_to_database, load_existing_match_ids
from config import REGION, HEADERS, MAX_MATCHES, REMAKE_THRESHOLD, RANKED_SOLO_DUO_QUEUE_ID, DB_PATH

def extract_matches_data(puuid, all_match_ids, all_puuids, db_path):
    match_ids = get_match_ids(puuid)
    if not match_ids:
        return all_match_ids, all_puuids

    print(f"Ranked Solo/Duo Match IDs: {match_ids}")
    for match_id in match_ids:
        if match_id in all_match_ids:
            print(f"Match ID {match_id} already processed")
            continue

        match_details = get_match_details(match_id)
        if not match_details or match_details['info']['queueId'] != RANKED_SOLO_DUO_QUEUE_ID:
            print(f"Skipping match ID {match_id} (not Ranked Solo/Duo or error)")
            continue

        if match_details['info']['gameDuration'] < REMAKE_THRESHOLD:
            print(f"Skipping match ID {match_id} (remade, duration: {match_details['info']['gameDuration']}s)")
            continue

        player_data = extract_player_data(match_details, match_id)
        save_to_database(player_data, db_path)
        all_match_ids.add(match_id)
        for player in player_data:
            all_puuids.add(player['puuid'])
        print(f"Processed match: {match_id}")

    return all_match_ids, all_puuids

def extract_ranked_solo_duo_data(riot_id):
    setup_database()
    all_match_ids = load_existing_match_ids()
    all_puuids = set()
    processed_puuids = set()

    try:
        game_name, tag_line = riot_id.split('/')
    except ValueError:
        print(f"Invalid riot_id format: {riot_id}. Expected 'gameName/tagLine' (e.g., 'AkemiMoon8/NA1')")
        return

    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    print(f"Requesting PUUID from: {url}")
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        return

    puuid = response.json()['puuid']
    print(f"Initial PUUID: {puuid}")
    all_puuids.add(puuid)

    while len(all_match_ids) < MAX_MATCHES and all_puuids:
        current_puuid = all_puuids.pop()
        if current_puuid in processed_puuids:
            continue

        all_match_ids, all_puuids = extract_matches_data(current_puuid, all_match_ids, all_puuids, DB_PATH)
        processed_puuids.add(current_puuid)
        print(f"Total unique matches processed: {len(all_match_ids)}\n")

if __name__ == "__main__":
    extract_ranked_solo_duo_data("AkemiMoon8/NA1")