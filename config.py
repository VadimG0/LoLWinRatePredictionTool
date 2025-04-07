from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}
REGION = "americas"
MAX_MATCHES = 1500
MATCHES_PER_PUUID = 10
RANKED_SOLO_DUO_QUEUE_ID = 420
REMAKE_THRESHOLD = 180
DB_PATH = Path("data/ranked_solo_duo_matchups.db")