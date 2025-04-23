from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
HEADERS = {"X-Riot-Token": RIOT_API_KEY}
REGION = "americas"
MAX_MATCHES = 15000
MATCHES_PER_PUUID = 30
RANKED_SOLO_DUO_QUEUE_ID = 420
REMAKE_THRESHOLD = 180

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ranked_solo_duo_matchups.db"