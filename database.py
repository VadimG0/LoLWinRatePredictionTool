import sqlite3
from pathlib import Path
from config import DB_PATH

def setup_database(db_path=DB_PATH):
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matchups (
            match_id TEXT,
            lane TEXT,
            puuid TEXT,
            champion TEXT,
            winner INTEGER,
            primary_style INTEGER,
            primary_selections TEXT,
            sub_style INTEGER,
            sub_selections TEXT,
            stat_perks TEXT,
            items TEXT,
            summoner_spells TEXT,
            team_bans TEXT,
            PRIMARY KEY (match_id, puuid)
        )
    """)
    conn.commit()
    conn.close()

def save_to_database(player_data, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
        INSERT OR IGNORE INTO matchups (
            match_id, lane, puuid, champion, winner, primary_style, primary_selections,
            sub_style, sub_selections, stat_perks, items, summoner_spells, team_bans
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    for row in player_data:
        cursor.execute(query, (
            row['match_id'], row['lane'], row['puuid'], row['champion'], row['winner'],
            row['primary_style'], row['primary_selections'], row['sub_style'],
            row['sub_selections'], row['stat_perks'], row['items'],
            row['summoner_spells'], row['team_bans']
        ))
    conn.commit()
    conn.close()
    print(f"Saved {len(player_data)} rows to database")

def load_existing_match_ids(db_path=DB_PATH):
    if not db_path.exists():
        setup_database(db_path)
        return set()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT match_id FROM matchups")
    match_ids = set(row[0] for row in cursor.fetchall())
    conn.close()
    return match_ids

def display_database_contents(db_path=DB_PATH):
    """Display the contents of the matchups table in a readable format."""
    if not db_path.exists():
        print(f"No database found at {db_path}. Run the data extraction script first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matchups")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    if not rows:
        print("Database is empty.")
    else:
        print(f"\nDisplaying {len(rows)} rows from the 'matchups' table:\n")
        print("-" * 80)
        for row in rows:
            for name, value in zip(column_names, row):
                print(f"{name}: {value}")
            print("-" * 80)
    conn.close()

if __name__ == "__main__":
    display_database_contents()