from pathlib import Path
import sqlite3
import pandas as pd
from collections import defaultdict, Counter
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from config import DB_PATH
import numpy as np
from multiprocessing import Pool, cpu_count

def _process_match(row):
    """Helper function for parallel processing of match data to calculate win rates."""
    champions = row['champion']
    lanes = row['lane']
    winners = [champ for champ, win in zip(champions, row['winner']) if win == 1]
    losers = [champ for champ, win in zip(champions, row['winner']) if win == 0]
    wins = defaultdict(int)
    total = defaultdict(int)
    # Matchup win rates (same-lane opponents)
    for idx, X in enumerate(winners):
        lane_X = lanes[idx]
        for jdx, Y in enumerate(losers):
            lane_Y = lanes[jdx]
            if lane_X == lane_Y:
                wins[(X, Y, lane_X)] += 1
                total[(X, Y, lane_X)] += 1
    for idx, X in enumerate(losers):
        lane_X = lanes[idx]
        for jdx, Y in enumerate(winners):
            lane_Y = lanes[jdx]
            if lane_X == lane_Y:
                total[(X, Y, lane_X)] += 1
    # Per-champion-lane win rates
    for idx, champ in enumerate(champions):
        lane = lanes[idx]
        win = row['winner'][idx]
        key = (champ, None, lane)  # None opponent for overall win rate
        total[key] += 1
        if win == 1:
            wins[key] += 1
    return wins, total

class MatchDataAnalyzer:
    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self._setup_tables()
        self._optimize_database()
        self.df = pd.read_sql_query("SELECT * FROM matchups", self.conn)
        self.match_data = self.df.groupby('match_id').agg({
            'champion': list,
            'lane': list,
            'winner': list
        }).reset_index()
        self.all_champions = sorted(self.df['champion'].unique())

        # Check if match count has changed
        current_match_count = len(self.match_data)
        previous_match_count = self._get_previous_match_count()
        if previous_match_count is None or current_match_count != previous_match_count:
            print(f"Match count changed (previous: {previous_match_count or 'none'}, current: {current_match_count}). Updating caches...")
            self.update_win_rates()
            self.update_association_rules()
            self._save_match_count(current_match_count)
        else:
            print("Match count unchanged. Using existing caches.")

    def _setup_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS win_rates (
                champion TEXT,
                opponent TEXT,
                lane TEXT,
                wins INTEGER,
                total_matches INTEGER,
                win_rate REAL,
                PRIMARY KEY (champion, opponent, lane)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                antecedents TEXT,
                consequents TEXT,
                support REAL,
                confidence REAL,
                lift REAL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        self.conn.commit()

    def _optimize_database(self):
        """Optimize SQLite database with indexes for faster queries."""
        cursor = self.conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_match_id ON matchups (match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_champion ON matchups (champion)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lane ON matchups (lane)")
        self.conn.commit()

    def _get_previous_match_count(self):
        """Retrieve the stored match count from the metadata table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'match_count'")
        result = cursor.fetchone()
        return result[0] if result else None

    def _save_match_count(self, match_count):
        """Save the current match count to the metadata table."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('match_count', ?)", (match_count,))
        self.conn.commit()
        print(f"Saved match count: {match_count}")

    def update_win_rates(self):
        """Calculate and store lane-specific win rates."""
        win_rates_df = self.calculate_win_rates()
        win_rates_df.to_sql('win_rates', self.conn, if_exists='replace', index=False)
        print("Updated win_rates table")

    def calculate_win_rates(self):
        """Calculate lane-specific win rates using parallel processing."""
        with Pool(cpu_count()) as pool:
            results = pool.map(_process_match, [row for _, row in self.match_data.iterrows()])

        wins = defaultdict(int)
        total = defaultdict(int)
        for win_dict, total_dict in results:
            for key in win_dict:
                wins[key] += win_dict[key]
            for key in total_dict:
                total[key] += total_dict[key]

        prior_win_rate = 0.5  # Neutral prior (50%)
        prior_weight = 10     # Equivalent to 10 matches
        results = []
        for (champion, opponent, lane), win_count in wins.items():
            total_count = total[(champion, opponent, lane)]
            if total_count > 0:
                win_rate = ((win_count + prior_weight * prior_win_rate) / (total_count + prior_weight)) * 100
                results.append({
                    'champion': champion,
                    'opponent': opponent,
                    'lane': lane,
                    'wins': win_count,
                    'total_matches': total_count,
                    'win_rate': win_rate
                })
        return pd.DataFrame(results)

    def update_association_rules(self, min_support=0.005, min_threshold=0.1):
        """Compute and store association rules for winning team compositions."""
        rules_df = self.compute_association_rules(min_support, min_threshold)
        rules_df['antecedents'] = rules_df['antecedents'].apply(lambda x: ','.join(x))
        rules_df['consequents'] = rules_df['consequents'].apply(lambda x: ','.join(x))
        rules_df[['antecedents', 'consequents', 'support', 'confidence', 'lift']].to_sql('rules', self.conn, if_exists='replace', index=False)
        print("Updated rules table")

    def compute_association_rules(self, min_support=0.005, min_threshold=0.1):
        """Compute association rules for champions in winning teams."""
        winning_teams = self.df[self.df['winner'] == 1].groupby('match_id')['champion'].apply(list).reset_index(name='champions')
        te = TransactionEncoder()
        te_ary = te.fit(winning_teams['champions']).transform(winning_teams['champions'])
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)
        single_consequent_rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
        return single_consequent_rules

    def analyze_champion_matchup(self, my_champion: str, enemy_champion: str, lane: str):
        """Analyze win rate and suggested allies for a champion matchup in a specific lane."""
        my_champion = my_champion.replace(" ", "")
        enemy_champion = enemy_champion.replace(" ", "")
        query = "SELECT wins, total_matches, win_rate FROM win_rates WHERE champion = ? AND opponent = ? AND lane = ?"
        result = pd.read_sql_query(query, self.conn, params=(my_champion, enemy_champion, lane))
        if not result.empty:
            wins, total, win_rate = result.iloc[0]
        else:
            query = "SELECT wins, total_matches, win_rate FROM win_rates WHERE champion = ? AND opponent IS NULL AND lane = ?"
            result = pd.read_sql_query(query, self.conn, params=(my_champion, lane))
            if not result.empty:
                wins, total, win_rate = result.iloc[0]
            else:
                wins, total, win_rate = 0, 0, 50.0

        query = "SELECT consequents, confidence FROM rules WHERE antecedents LIKE ? ORDER BY confidence DESC LIMIT 5"
        rules_df = pd.read_sql_query(query, self.conn, params=(f'%{my_champion}%',))
        suggestions = [{row['consequents']: row['confidence']} for _, row in rules_df.iterrows()]

        return {
            'my_champion': my_champion,
            'enemy_champion': enemy_champion,
            'lane': lane,
            'win_rate': win_rate,
            'matches_analyzed': total,
            'suggested_allies': suggestions
        }

    def estimate_team_win_rate(self, my_team: list[str], enemy_team: list[str], lanes=['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']):
        """Estimate team win rate as the average of champion-lane win rates vs. opponents."""
        if len(my_team) != 5 or len(enemy_team) != 5 or len(lanes) != 5:
            raise ValueError("Each team and lanes list must have exactly 5 elements")

        my_team = [champ.replace(" ", "") for champ in my_team]
        enemy_team = [champ.replace(" ", "") for champ in enemy_team]

        my_team_win_rates = []
        for champ, lane, opp_champ in zip(my_team, lanes, enemy_team):
            query = "SELECT win_rate FROM win_rates WHERE champion = ? AND opponent = ? AND lane = ?"
            result = pd.read_sql_query(query, self.conn, params=(champ, opp_champ, lane))
            if not result.empty:
                win_rate = result.iloc[0]['win_rate']
            else:
                query = "SELECT win_rate FROM win_rates WHERE champion = ? AND opponent IS NULL AND lane = ?"
                result = pd.read_sql_query(query, self.conn, params=(champ, lane))
                win_rate = result.iloc[0]['win_rate'] if not result.empty else 50.0
            my_team_win_rates.append(win_rate)

        enemy_team_win_rates = []
        for champ, lane, opp_champ in zip(enemy_team, lanes, my_team):
            query = "SELECT win_rate FROM win_rates WHERE champion = ? AND opponent = ? AND lane = ?"
            result = pd.read_sql_query(query, self.conn, params=(champ, opp_champ, lane))
            if not result.empty:
                win_rate = result.iloc[0]['win_rate']
            else:
                query = "SELECT win_rate FROM win_rates WHERE champion = ? AND opponent IS NULL AND lane = ?"
                result = pd.read_sql_query(query, self.conn, params=(champ, lane))
                win_rate = result.iloc[0]['win_rate'] if not result.empty else 50.0
            enemy_team_win_rates.append(win_rate)

        my_avg_win_rate = sum(my_team_win_rates) / len(my_team_win_rates) if my_team_win_rates else 50.0
        return my_avg_win_rate

    def save_to_csv(self, df, filename):
        """Save DataFrame to CSV in the database directory."""
        output_path = self.db_path.parent / filename
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    analyzer = MatchDataAnalyzer()
    my_team = ["Garen", "Lee Sin", "Ahri", "Jinx", "Thresh"]
    enemy_team = ["Darius", "Vi", "Zed", "Ezreal", "Nami"]
    win_rate = analyzer.estimate_team_win_rate(my_team, enemy_team)
    print(f"Estimated Team Win Rate: {win_rate:.2f}%")

    matchup_analysis = analyzer.analyze_champion_matchup('Jhin', 'Caitlyn', 'BOTTOM')
    print(matchup_analysis)