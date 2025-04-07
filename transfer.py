import csv
import sqlite3
from pathlib import Path
from database import DB_PATH, setup_database, save_to_database, load_existing_match_ids

def transform_csv_to_database_format(csv_file_path, existing_match_ids):
    """
    Transforms CSV data to match the database schema, skipping existing matches.
    Returns a list of dictionaries in the correct format for save_to_database().
    """
    transformed_data = []
    new_match_count = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            match_id = row['match_id']
            
            # Skip if this match already exists in database
            if match_id in existing_match_ids:
                continue
                
            new_match_count += 1
                
            # Create winner entry
            winner_entry = {
                'match_id': match_id,
                'lane': row['lane'],
                'puuid': row['winner_puuid'],
                'champion': row['winner_champion'],
                'winner': 1,  # True/1 for winner
                'primary_style': row['winner_primary_style'],
                'primary_selections': row['winner_primary_selections'],
                'sub_style': row['winner_sub_style'],
                'sub_selections': row['winner_sub_selections'],
                'stat_perks': row['winner_stat_perks'],
                'items': row['winner_items'],
                'summoner_spells': row['winner_summoner_spells'],
                'team_bans': row['winner_bans']
            }
            transformed_data.append(winner_entry)
            
            # Create loser entry
            loser_entry = {
                'match_id': match_id,
                'lane': row['lane'],
                'puuid': row['loser_puuid'],
                'champion': row['loser_champion'],
                'winner': 0,  # False/0 for loser
                'primary_style': row['loser_primary_style'],
                'primary_selections': row['loser_primary_selections'],
                'sub_style': row['loser_sub_style'],
                'sub_selections': row['loser_sub_selections'],
                'stat_perks': row['loser_stat_perks'],
                'items': row['loser_items'],
                'summoner_spells': row['loser_summoner_spells'],
                'team_bans': row['loser_bans']
            }
            transformed_data.append(loser_entry)
    
    print(f"Found {new_match_count} new matches in CSV (creating {len(transformed_data)} participant records)")
    return transformed_data

def import_csv_to_database_once(csv_file_path, db_path=DB_PATH):
    """
    Main function to import CSV data into the database.
    Will only import data for matches that don't already exist in the database.
    """
    # Ensure database exists and is set up
    if not Path(db_path).exists():
        setup_database(db_path)
    
    # Load existing match IDs to avoid duplicates
    existing_match_ids = load_existing_match_ids(db_path)
    print(f"Database contains {len(existing_match_ids)} existing matches")
    
    # Transform CSV data to database format (skipping existing matches)
    player_data = transform_csv_to_database_format(csv_file_path, existing_match_ids)
    
    if not player_data:
        print("No new matches to import - all CSV data already exists in database")
        return
    
    # Save to database using the existing function
    save_to_database(player_data, db_path)
    
    print(f"Successfully imported {len(player_data)} new participant records")

# Example usage with safety check:
if __name__ == "__main__":
    csv_file_path = "data\\ranked_solo_duo_matchups.csv"  # Replace with your CSV file path
    
    # Safety confirmation for one-time run
    confirm = input("This script should only run once. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Import cancelled")
        exit()
    
    import_csv_to_database_once(csv_file_path)
    print("Import completed. Do not run this script again with the same CSV file.")