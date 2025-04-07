import requests
from config import REGION, HEADERS, MATCHES_PER_PUUID, RANKED_SOLO_DUO_QUEUE_ID

def get_match_ids(puuid, count=MATCHES_PER_PUUID):
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {"queue": RANKED_SOLO_DUO_QUEUE_ID, "count": count}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json() if response.status_code == 200 else []

def get_match_details(match_id):
    url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else None

def extract_player_data(match_data, match_id):
    # Same as in Modified Version 1
    player_data = []
    teams = match_data['info']['teams']
    team_bans = {team['teamId']: [ban['championId'] for ban in team['bans']] for team in teams}
    for participant in match_data['info']['participants']:
        perks = participant['perks']
        player_data.append({
            'match_id': match_id,
            'lane': participant['individualPosition'],
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