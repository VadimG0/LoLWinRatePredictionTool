import sqlite3
import pandas as pd
from pathlib import Path
import json

# Set up paths
PROJECT_ROOT = Path.cwd()
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "lol_data.db"
CSV_PATH = DATA_DIR / "winner_data.csv"

def init_db():
    """Initialize database with schema matching your CSV"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS winners (
            match_id TEXT,
            lane TEXT,
            winner_puuid TEXT,
            winner_champion TEXT,
            winner_primary_style INTEGER,
            winner_primary_selections TEXT,
            winner_sub_style INTEGER,
            winner_sub_selections TEXT,
            winner_stat_perks TEXT,
            winner_items TEXT,
            winner_summoner_spells TEXT,
            winner_bans TEXT,
            winner BOOLEAN,
            PRIMARY KEY (match_id, winner_puuid)
        )
        ''')
        conn.commit()
        print("Database initialized with correct schema")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def clean_csv_headers(df):
    """Rename columns to match our database schema"""
    column_mapping = {
        df.columns[0]: 'match_id',
        df.columns[1]: 'lane',
        df.columns[2]: 'winner_puuid',
        df.columns[3]: 'winner_champion',
        df.columns[4]: 'winner_primary_style',
        df.columns[5]: 'winner_primary_selections',
        df.columns[6]: 'winner_sub_style',
        df.columns[7]: 'winner_sub_selections',
        df.columns[8]: 'winner_stat_perks',
        df.columns[9]: 'winner_items',
        df.columns[10]: 'winner_summoner_spells',
        df.columns[11]: 'winner_bans',
        df.columns[12]: 'winner'
    }
    return df.rename(columns=column_mapping)

def csv_to_db():
    """Import CSV data with header cleaning"""
    try:
        # Read CSV and clean headers
        df = pd.read_csv(CSV_PATH)
        df = clean_csv_headers(df)
        
        # Connect to DB and import
        conn = sqlite3.connect(str(DB_PATH))
        df.to_sql('winners', conn, if_exists='replace', index=False)
        print("Data imported successfully with cleaned headers!")
        return True
    except Exception as e:
        print(f"Error during import: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Starting database setup...")
    
    # Delete old database if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
    
    if init_db() and csv_to_db():
        print("\n✅ Success! Database created with proper schema.")
    else:
        print("\n❌ Operation failed. See errors above.")