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
PUUID = "iqclScuTpL1qEaHBL6o-VxUmtH-YHr97lIOvGIeP8j8QCnnBwv5CEwrUrKruD60evV-bBuEkq4H72w"

# Make the request to get Riot ID (gameName and tagLine)
response = requests.get(
    f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{PUUID}",
    headers=HEADERS
)

# Check if the request was successful
if response.status_code == 200:
    print(response.json())
    account_info = response.json()
    game_name = account_info["gameName"]
    tag_line = account_info["tagLine"]
    print(f"Riot ID: {game_name}#{tag_line}")
    print(f"Riot ID: {game_name}/{tag_line}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)