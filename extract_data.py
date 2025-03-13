import os
from dotenv import load_dotenv
import requests
import numpy as np
import pandas as pd

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}
REGION = "americas"
MAX_MATCHES = 1500  # Target total number of unique matches
MATCHES_PER_PUUID = 7   # Higher Number results in more processed matches but increases bias
SAVE_INTERVAL = 1  # Save to CSV every match
RANKED_SOLO_DUO_QUEUE_ID = 420  # Queue ID for Ranked Solo/Duo
CSV_FILENAME = "data/ranked_solo_duo_matchups.csv"
REMAKE_THRESHOLD = 180  # Minimum game duration in seconds to consider a match valid (3 minutes)

def get_match_ids(puuid, count=MATCHES_PER_PUUID) -> dict:
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"queue": RANKED_SOLO_DUO_QUEUE_ID, "count": count}  # Filter by Ranked Solo/Duo

    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        return

def get_match_details(match_id) -> dict:
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
        return

def extract_lane_matchups(match_data, match_id) -> list[dict]:
    lane_matchups = {'TOP': [], 'MIDDLE': [], 'JUNGLE': [], 'BOTTOM': [], 'UTILITY': []}

    # Extract bans from teams
    teams = match_data['info']['teams']
    winner_bans = []
    loser_bans = []
    for team in teams:
        bans = [ban['championId'] for ban in team['bans']]  # List of champion IDs banned by this team
        if team['win']:
            winner_bans = bans
        else:
            loser_bans = bans

    # Step through each participant and categorize by lane
    for participant in match_data['info']['participants']:
        lane = participant['individualPosition']
        champion = participant['championName']
        puuid = participant['puuid']
        win = participant['win']
        
        # Extract additional features
        perks = participant['perks']
        primary_style = perks['styles'][0]['style']
        primary_selections = [selection['perk'] for selection in perks['styles'][0]['selections']]
        sub_style = perks['styles'][1]['style']
        sub_selections = [selection['perk'] for selection in perks['styles'][1]['selections']]
        stat_perks = perks['statPerks']
        
        items = {
            'item0': participant['item0'],
            'item1': participant['item1'],
            'item2': participant['item2'],
            'item3': participant['item3'],
            'item4': participant['item4'],
            'item5': participant['item5']
        }
        
        summoner_spells = {
            'summoner1Id': participant['summoner1Id'],
            'summoner2Id': participant['summoner2Id']
        }
        
        if lane in lane_matchups:
            lane_matchups[lane].append({
                'champion': champion,
                'puuid': puuid,
                'win': win,
                'primary_style': primary_style,
                'primary_selections': primary_selections,
                'sub_style': sub_style,
                'sub_selections': sub_selections,
                'stat_perks': stat_perks,
                'items': items,
                'summoner_spells': summoner_spells
            })

    # Match champions in the same lane with opposite win values
    lane_pairings = []
    for lane, participants in lane_matchups.items():
        if len(participants) > 1:
            winners = [p for p in participants if p['win'] == True]
            losers = [p for p in participants if p['win'] == False]
            
            for winner in winners:
                for loser in losers:
                    lane_pairings.append({
                        'match_id': match_id,
                        'lane': lane,
                        'winner_puuid': winner['puuid'],
                        'winner_champion': winner['champion'],
                        'loser_puuid': loser['puuid'],
                        'loser_champion': loser['champion'],
                        'winner_primary_style': winner['primary_style'],
                        'winner_primary_selections': winner['primary_selections'],
                        'winner_sub_style': winner['sub_style'],
                        'winner_sub_selections': winner['sub_selections'],
                        'winner_stat_perks': winner['stat_perks'],
                        'winner_items': winner['items'],
                        'winner_summoner_spells': winner['summoner_spells'],
                        'loser_primary_style': loser['primary_style'],
                        'loser_primary_selections': loser['primary_selections'],
                        'loser_sub_style': loser['sub_style'],
                        'loser_sub_selections': loser['sub_selections'],
                        'loser_stat_perks': loser['stat_perks'],
                        'loser_items': loser['items'],
                        'loser_summoner_spells': loser['summoner_spells'],
                        'winner_bans': winner_bans,
                        'loser_bans': loser_bans
                    })
    
    return lane_pairings

def save_to_csv(all_matchups, filename, append=True) -> None:
    df = pd.DataFrame(all_matchups)
    mode = 'a' if append and os.path.exists(filename) else 'w'
    header = not (append and os.path.exists(filename))
    df.to_csv(filename, mode=mode, header=header, index=False)
    print(f"Data appended to {filename}")

def load_existing_match_ids(filename) -> set[np.ndarray]:
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        if 'match_id' in df.columns and not df.empty:
            return set(df['match_id'].unique())
    else:
        print(f"CSV file {filename} does not exist. Creating with column names.")
        # Create an empty DataFrame with the expected columns
        columns = [
            'match_id', 'lane', 'winner_puuid', 'winner_champion', 'loser_puuid', 'loser_champion',
            'winner_primary_style', 'winner_primary_selections', 'winner_sub_style', 'winner_sub_selections',
            'winner_stat_perks', 'winner_items', 'winner_summoner_spells',
            'loser_primary_style', 'loser_primary_selections', 'loser_sub_style', 'loser_sub_selections',
            'loser_stat_perks', 'loser_items', 'loser_summoner_spells',
            'winner_bans', 'loser_bans'
        ]
        pd.DataFrame(columns=columns).to_csv(filename, index=False)
    return set()

def extract_matches_data(puuid, all_match_ids, all_puuids) -> tuple[set[str], set[str]]:
    all_matchups = []
    # Step 1: Get match IDs (Ranked Solo/Duo only)
    match_ids = get_match_ids(puuid)
    if not match_ids:
        return None, None

    print(f"Ranked Solo/Duo Match IDs: {match_ids}")

    # Step 2: Process matches
    for match_id in match_ids:
        if match_id in all_match_ids:
            print(f"Match ID {match_id} already exists in CSV")
            continue

        match_details = get_match_details(match_id)
        if not match_details:
            return None, None
        
        if match_details and match_details['info']['queueId'] != RANKED_SOLO_DUO_QUEUE_ID:
            print(f"Skipping match ID {match_id} (not Ranked Solo/Duo or error)")
            continue

        if match_details['info']['gameDuration'] < REMAKE_THRESHOLD:
            print(f"Skipping match ID {match_id} (remade, duration: {match_details['info']['gameDuration']}s)")
            continue
        
        lane_matchups = extract_lane_matchups(match_details, match_id)
        if lane_matchups:
            all_matchups.extend(lane_matchups)
            all_match_ids.add(match_id)
            print(f"Processed Ranked Solo/Duo match: {match_id}")
            
            # Collect PUUIDs from this match
            for matchup in lane_matchups:
                all_puuids.add(matchup['winner_puuid'])
                all_puuids.add(matchup['loser_puuid'])

            # Save every 5 matches
            if len(all_match_ids) % SAVE_INTERVAL == 0:
                save_to_csv(all_matchups, CSV_FILENAME)
                all_matchups = []  # Clear after saving to avoid duplicates in memory

    return all_match_ids, all_puuids
    
def extract_ranked_solo_duo_data(riot_id) -> None:
    all_match_ids = load_existing_match_ids(CSV_FILENAME)  # Load existing match IDs from CSV
    all_puuids = set()
    processed_puuids = set()  # Track processed PUUIDs to avoid duplicates

    # Step 1: Get initial PUUID
    response = requests.get(
        f'https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id}',
        headers=HEADERS
    )

    if response.status_code == 200:
        data = response.json()
        puuid = data['puuid']
        print(f"Initial PUUID: {puuid}")
        all_puuids.add(puuid)
    else:
        response.raise_for_status()
        return

    # Step 2: Expand to 1500 unique Ranked Solo/Duo matches
    while len(all_match_ids) < MAX_MATCHES and all_puuids:
        current_puuid = all_puuids.pop()  # Get a PUUID to process
        if current_puuid in processed_puuids:
            continue
        
        all_match_ids, all_puuids = extract_matches_data(current_puuid, all_match_ids, all_puuids)
        
        processed_puuids.add(current_puuid)
        print(f"Total unique Ranked Solo/Duo matches processed: {len(all_match_ids)}, PUUIDs left to process: {len(all_puuids)}")

if __name__ == "__main__":
    extract_ranked_solo_duo_data("Tammior/NA1")