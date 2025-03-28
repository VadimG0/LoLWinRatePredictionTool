import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests
import pandas as pd

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}
REGION = "americas"

# Set up proper file paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)  # Creates directory if it doesn't exist
CSV_FILENAME = DATA_DIR / "winner_data.csv"

def get_match_ids(puuid, count=10):
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"count": count}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else None

def get_match_details(match_id):
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

def extract_winner_data(match_data):
    winners = []
    for participant in match_data['info']['participants']:
        if participant['win']:
            winners.append({
                'match_id': match_data['metadata']['matchId'],
                'lane': participant['individualPosition'],
                'winner_puuid': participant['puuid'],
                'winner_champion': participant['championName'],
                'winner_primary_style': participant['perks']['styles'][0]['style'],
                'winner_primary_selections': json.dumps([s['perk'] for s in participant['perks']['styles'][0]['selections']]),
                'winner_sub_style': participant['perks']['styles'][1]['style'],
                'winner_sub_selections': json.dumps([s['perk'] for s in participant['perks']['styles'][1]['selections']]),
                'winner_stat_perks': json.dumps(participant['perks']['statPerks']),
                'winner_items': json.dumps({f'item{i}': participant[f'item{i}'] for i in range(6)}),
                'winner_summoner_spells': json.dumps({
                    'summoner1Id': participant['summoner1Id'],
                    'summoner2Id': participant['summoner2Id']
                }),
                'winner_bans': json.dumps([ban['championId'] for team in match_data['info']['teams'] if team['win'] for ban in team['bans']]),
                'winner': True
            })
    return winners

def save_to_csv(data, filename):
    """Save data to CSV file, creating directory if needed"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pd.DataFrame(data).to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)
    print(f"Data saved to {filename}")

def main(riot_id):
    # Get PUUID
    response = requests.get(
        f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{riot_id}",
        headers=HEADERS
    )
    if response.status_code != 200:
        print(f"Error getting PUUID: {response.status_code}")
        return
    
    puuid = response.json()['puuid']
    print(f"Processing matches for PUUID: {puuid}")
    
    # Get match IDs
    match_ids = get_match_ids(puuid)
    if not match_ids:
        print("No matches found")
        return
    
    # Process each match
    for match_id in match_ids:
        match_data = get_match_details(match_id)
        if not match_data:
            continue
            
        winner_data = extract_winner_data(match_data)
        if winner_data:
            save_to_csv(winner_data, str(CSV_FILENAME))

if __name__ == "__main__":
    main("AkemiMoon8/NA1")