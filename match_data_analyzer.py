from pathlib import Path
import sqlite3
import pandas as pd
from collections import defaultdict
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from config import DB_PATH

class MatchDataAnalyzer:
    def __init__(self, db_path=DB_PATH):
        """Initialize with the path to the SQLite database."""
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.df = pd.read_sql_query("SELECT * FROM matchups", self.conn)
        self.match_data = self.df.groupby('match_id').agg({
            'champion': list,
            'winner': list
        }).reset_index()

    def calculate_win_rates(self) -> pd.DataFrame:
        """Calculate win rates for all champion-opponent pairs."""
        wins = defaultdict(int)
        total = defaultdict(int)
        for _, row in self.match_data.iterrows():
            champions = row['champion']
            winners = [champ for champ, win in zip(champions, row['winner']) if win == 1]
            losers = [champ for champ, win in zip(champions, row['winner']) if win == 0]
            for X in winners:
                for Y in losers:
                    wins[(X, Y)] += 1
                    total[(X, Y)] += 1
            for X in losers:
                for Y in winners:
                    total[(X, Y)] += 1
        results = []
        for (champion, opponent), win_count in wins.items():
            total_count = total[(champion, opponent)]
            if total_count > 0:
                win_rate = (win_count / total_count) * 100
                results.append({
                    'Champion': champion,
                    'Opponent': opponent,
                    'Wins': win_count,
                    'Total Matches': total_count,
                    'Win Rate (%)': win_rate
                })
        return pd.DataFrame(results).sort_values(by=['Total Matches', 'Win Rate (%)'], ascending=False)

    def compute_association_rules(self, min_support=0.005, min_threshold=0.1) -> pd.DataFrame:
        """Compute association rules for winning teams."""
        winning_teams = self.df[self.df['winner'] == 1].groupby('match_id')['champion'].apply(list).reset_index(name='champions')
        te = TransactionEncoder()
        te_ary = te.fit(winning_teams['champions']).transform(winning_teams['champions'])
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)
        single_consequent_rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
        return single_consequent_rules.sort_values(by=['support', 'confidence'], ascending=False)

    def analyze_champion_matchup(self, my_champion: str, enemy_champion: str) -> dict:
        """Analyze win rate and association rules for a specific champion vs. enemy champion."""
        query = """
        SELECT match_id, champion, winner
        FROM matchups
        WHERE match_id IN (
            SELECT match_id
            FROM matchups
            WHERE champion IN (?, ?)
            GROUP BY match_id
            HAVING COUNT(DISTINCT champion) = 2
        )
        """
        df_matchup = pd.read_sql_query(query, self.conn, params=(my_champion, enemy_champion))

        wins = 0
        total = 0
        for _, group in df_matchup.groupby('match_id'):
            champs = group['champion'].tolist()
            winners = group[group['winner'] == 1]['champion'].tolist()
            if my_champion in champs and enemy_champion in champs:
                total += 1
                if my_champion in winners:
                    wins += 1
        win_rate = (wins / total * 100) if total > 0 else 0

        winning_teams = self.df[self.df['winner'] == 1].groupby('match_id')['champion'].apply(list).reset_index(name='champions')
        te = TransactionEncoder()
        te_ary = te.fit(winning_teams['champions']).transform(winning_teams['champions'])
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        frequent_itemsets = apriori(df_encoded, min_support=0.005, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)
        relevant_rules = rules[rules['antecedents'].apply(lambda x: my_champion in x)].sort_values('confidence', ascending=False)

        top_suggestions = relevant_rules[['consequents', 'confidence']].head(5).to_dict('records')
        suggestions = [{list(rule['consequents'])[0]: rule['confidence']} for rule in top_suggestions]

        return {
            'my_champion': my_champion,
            'enemy_champion': enemy_champion,
            'win_rate': win_rate,
            'matches_analyzed': total,
            'suggested_allies': suggestions
        }

    def save_to_csv(self, df, filename) -> None:
        """Save a DataFrame to a CSV file."""
        output_path = self.db_path.parent / filename
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        self.conn.close()

if __name__ == "__main__":
    analyzer = MatchDataAnalyzer()
    # Test the new function
    result = analyzer.analyze_champion_matchup("Garen", "Darius")
    print(f"Win Rate for {result['my_champion']} vs {result['enemy_champion']}: {result['win_rate']:.2f}%")
    print(f"Matches Analyzed: {result['matches_analyzed']}")
    print("Suggested Allies:")
    for suggestion in result['suggested_allies']:
        for champ, confidence in suggestion.items():
            print(f"  {champ}: {confidence:.2%}")