import requests
import time
from config import REGION, HEADERS, MATCHES_PER_PUUID, RANKED_SOLO_DUO_QUEUE_ID

class RateLimitExceeded(Exception):
    """Custom exception for persistent rate limit issues."""
    pass

def api_request(url, headers=HEADERS, params=None, retries=3):
    """Generic API request handler with rate limit retry logic."""
    for attempt in range(retries):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:  # Rate limit exceeded
            retry_after = int(response.headers.get('Retry-After', 1))  # Default to 1s if header missing
            print(f"Rate limit exceeded. Waiting {retry_after} seconds (Attempt {attempt + 1}/{retries})")
            time.sleep(retry_after)
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return None
    raise RateLimitExceeded(f"Rate limit exceeded after {retries} retries")

def get_match_ids(puuid, count=MATCHES_PER_PUUID):
    """Get match IDs for a PUUID with rate limit handling."""
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"queue": RANKED_SOLO_DUO_QUEUE_ID, "count": count}
    try:
        return api_request(url, params=params)
    except RateLimitExceeded as e:
        print(e)
        return []

def get_match_details(match_id):
    """Get match details for a match ID with rate limit handling."""
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    try:
        return api_request(url)
    except RateLimitExceeded as e:
        print(e)
        return None

def extract_player_data(match_data, match_id):
    """Extract player data from match details, replacing 'Invalid' lanes with the missing lane."""
    player_data = []
    teams = match_data['info']['teams']
    team_bans = {team['teamId']: [ban['championId'] for ban in team['bans']] for team in teams}
    
    # Define valid lanes
    all_lanes = {'TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY'}
    
    # Collect lanes for each team
    team1_lanes = []  # First 5 participants (teamId 100 typically)
    team2_lanes = []  # Last 5 participants (teamId 200 typically)
    for i, participant in enumerate(match_data['info']['participants']):
        lane = participant['individualPosition']
        if i < 5:
            team1_lanes.append(lane)
        else:
            team2_lanes.append(lane)
    
    # Replace 'Invalid' with missing lane for each team
    for i, participant in enumerate(match_data['info']['participants']):
        lane = participant['individualPosition']
        if lane == 'Invalid':
            # Determine team and fix lane
            if i < 5:  # Team 1
                used_lanes = set(team1_lanes) - {'Invalid'}
                missing_lane = (all_lanes - used_lanes).pop()
                lane = missing_lane
                team1_lanes[i] = lane  # Update the list for consistency
                print(f"Match {match_id}: Replaced 'Invalid' with '{lane}' for Team 1 participant {i+1}")
            else:  # Team 2
                used_lanes = set(team2_lanes) - {'Invalid'}
                missing_lane = (all_lanes - used_lanes).pop()
                lane = missing_lane
                team2_lanes[i - 5] = lane  # Update the list for consistency
                print(f"Match {match_id}: Replaced 'Invalid' with '{lane}' for Team 2 participant {i-4}")
        
        perks = participant['perks']
        player_data.append({
            'match_id': match_id,
            'lane': lane,
            'puuid': participant['puuid'],
            'champion': participant['championName'],
            'winner': 1 if participant['win'] else 0,
            'primary_style': perks['styles'][0]['style'],
            'primary_selections': str([s['perk'] for s in perks['styles'][0]['selections']]),
            'sub_style': perks['styles'][1]['style'],
            'sub_selections': str([s['perk'] for s in perks['styles'][1]['selections']]),
            'stat_perks': str(perks['statPerks']),
            'items': str({f'item{i}': participant[f'item{i}'] for i in range(6)}),
            'summoner_spells': str({
                'summoner1Id': participant['summoner1Id'],
                'summoner2Id': participant['summoner2Id']
            }),
            'team_bans': str(team_bans[participant['teamId']])
        })
    
    return player_data