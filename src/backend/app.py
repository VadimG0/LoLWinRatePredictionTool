from typing import Union

from fastapi.middleware.cors import CORSMiddleware 
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from fastapi.responses import JSONResponse
import json
import os

# from src.backend.api.predict import get_prediction

app = FastAPI()

app.add_middleware(
 CORSMiddleware,
 allow_origins=["http://localhost:3000"], # Add your frontend origin here
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
 )

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAMPION_DATA_URL = os.path.join(BASE_DIR, '../../static_data/champions.json')

@app.get('/')
def homepage():
    return {'message':'Welcome to League of Legends Prediction Tool'}

# @app.post('/predict')
# def predict(data: dict):
#     try:
#         prediction = get_prediction(data)
#         return {'message':'Prediction is successful {prediction}'}
#     except Exception as e:
#         return HTTPException(status_code=400, detail=str(e))
    

@app.get('/greet/{name}')
async def greet(name: str):
    greeting = f'Hello, {name}. This is a personalized greeting!'
    return {'message': greeting}    


@app.get('/champions')
async def get_champions():
    with open(CHAMPION_DATA_URL, 'r', encoding='utf-8') as file:
        champion_data = json.load(file)
    return JSONResponse(content=champion_data)

@app.get('/champions/{champion_name}')
async def get_champion(champion_name: str):
    try:
        with open(CHAMPION_DATA_URL, 'r', encoding='utf-8') as file:
            champion_data = json.load(file)
        
        # Normalize the champion name to lowercase for case-insensitive search
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
        raise HTTPException(status_code=502, detail="Champion data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    


