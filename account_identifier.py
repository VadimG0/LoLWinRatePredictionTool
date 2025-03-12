import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {
    "X-Riot-Token": RIOT_API_KEY
}
REGION = "americas"  # Use "americas", "asia", or "europe" for the account endpoint

def convert_puuid_to_riotid(puuid):     # (e.g. "iqclScuTpL1qEaHBL6o-VxUmtH-YHr97lIOvGIeP8j8QCnnBwv5CEwrUrKruD60evV-bBuEkq4H72w")
    # Make the request to get Riot ID (gameName and tagLine)
    response = requests.get(
        f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}",
        headers=HEADERS
    )

    # Check if the request was successful
    if response.status_code == 200:
        account_info = response.json()
        game_name = account_info["gameName"]
        tag_line = account_info["tagLine"]
        return f"Riot ID: {game_name}/{tag_line}"
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
def convert_riotid_to_puuid(gameName, tagLine):     # (e.g. Ballas, 5555)
    # Make the request to get PUUID
    response = requests.get(
        f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}",  
        headers=HEADERS
    )

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()["puuid"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__=="__main__":
    # print(convert_riotid_to_puuid("Ballas", "5555"))
    print(convert_puuid_to_riotid("sMVtZA2m58r5ASnydGO7Xkz0XTZ5p1D8DXoOKiP58dtGdls-5K7dKBCmRwkzmOLpkQMvGB-2e1AtCw"))