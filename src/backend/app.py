import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, Dict
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os

# Add the project root (two levels up) to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent  # Navigate to project/
sys.path.append(str(project_root))

from match_data_analyzer import MatchDataAnalyzer
from config import DB_PATH

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAMPION_DATA_URL = os.path.join(BASE_DIR, '../../static_data/champions.json')

# Debug: Print the resolved path
print(f"BASE_DIR: {BASE_DIR}")
print(f"CHAMPION_DATA_URL: {CHAMPION_DATA_URL}")
print(f"File exists: {os.path.exists(CHAMPION_DATA_URL)}")

# Initialize MatchDataAnalyzer
analyzer = MatchDataAnalyzer(db_path=DB_PATH)

# Pydantic models for request validation
class TeamRequest(BaseModel):
    blue_team: Dict[str, Union[str, None]]
    red_team: Dict[str, Union[str, None]]

class AllyRequest(BaseModel):
    champion: str
    enemy_champion: str
    lane: str

@app.get('/')
def homepage():
    return {'message': 'Welcome to League of Legends Prediction Tool'}

@app.get('/greet/{name}')
async def greet(name: str):
    greeting = f'Hello, {name}. This is a personalized greeting!'
    return {'message': greeting}

@app.get('/champions')
async def get_champions():
    try:
        print(f"Attempting to read file: {CHAMPION_DATA_URL}")
        with open(CHAMPION_DATA_URL, 'r', encoding='utf-8') as file:
            champion_data = json.load(file)
        print("File read successfully")
        return JSONResponse(content=champion_data)
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        raise HTTPException(status_code=404, detail="Champions file not found")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=500, detail="Error decoding champions JSON data")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get('/champions/{champion_name}')
async def get_champion(champion_name: str):
    try:
        with open(CHAMPION_DATA_URL, 'r', encoding='utf-8') as file:
            champion_data = json.load(file)
        
        query = champion_name.lower()
        matches = []
        if "data" in champion_data:
            for champ_key, champ_data in champion_data["data"].items():
                champ_name = champ_data.get("name", champ_key).lower()
                if query in champ_name or query in champ_key.lower():
                    matches.append([champ_name, champ_data])
        
        if matches:
            return JSONResponse(content=matches)
        else:
            raise HTTPException(status_code=404, detail="No champions found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Champions file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding champions JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post('/predict_team_win_rate')
async def predict_team_win_rate(request: TeamRequest):
    try:
        lanes = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
        blue_team = [request.blue_team.get(role, None) for role in ['Top', 'Jungle', 'Mid', 'Bottom', 'Support']]
        red_team = [request.red_team.get(role, None) for role in ['Top', 'Jungle', 'Mid', 'Bottom', 'Support']]

        blue_team_champs = [champ for champ in blue_team if champ]
        red_team_champs = [champ for champ in red_team if champ]

        if not blue_team_champs or not red_team_champs:
            return {'win_rate': 50.0, 'message': 'Not enough champions selected to predict win rate'}

        blue_team_full = blue_team + [None] * (5 - len(blue_team))
        red_team_full = red_team + [None] * (5 - len(red_team))

        win_rate = analyzer.estimate_team_win_rate(blue_team_full, red_team_full, lanes)
        return {'win_rate': win_rate, 'message': 'Win rate prediction successful'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error predicting win rate: {str(e)}")

@app.post('/suggest_allies')
async def suggest_allies(request: AllyRequest):
    try:
        matchup_analysis = analyzer.analyze_champion_matchup(
            request.champion, request.enemy_champion, request.lane
        )
        return {
            'my_champion': matchup_analysis['my_champion'],
            'enemy_champion': matchup_analysis['enemy_champion'],
            'lane': matchup_analysis['lane'],
            'win_rate': matchup_analysis['win_rate'],
            'matches_analyzed': matchup_analysis['matches_analyzed'],
            'suggested_allies': matchup_analysis['suggested_allies']
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error suggesting allies: {str(e)}")