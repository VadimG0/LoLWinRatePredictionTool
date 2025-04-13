import sqlite3
import json

def migrate_champions():
    # Paths relative to project root
    json_path = 'static_data/champions.json'
    db_path = 'data/champions.db'

    # Read champions.json
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            champions_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: {json_path} not found")
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to decode {json_path}")
        return

    # Ensure data directory exists
    import os
    os.makedirs('data', exist_ok=True)

    # Connect to SQLite database
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create champions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS champions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                title TEXT,
                tags TEXT,
                stats TEXT,
                data TEXT
            )
        ''')

        # Insert champions
        if 'data' in champions_data:
            for champ_key, champ_data in champions_data['data'].items():
                cursor.execute('''
                    INSERT OR REPLACE INTO champions (id, name, title, tags, stats, data)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    champ_data.get('id', champ_key),
                    champ_data.get('name', champ_key),
                    champ_data.get('title', ''),
                    json.dumps(champ_data.get('tags', [])),
                    json.dumps(champ_data.get('stats', {})),
                    json.dumps(champ_data)
                ))

        # Commit and close
        conn.commit()
        print(f"Successfully migrated champions to {db_path}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_champions()