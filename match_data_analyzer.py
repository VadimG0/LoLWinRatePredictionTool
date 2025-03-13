from pathlib import Path
import pandas as pd
from collections import defaultdict
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

class MatchDataAnalyzer:
    def __init__(self, dataset_path):
        """Initialize with the path to the dataset."""
        self.dataset_path = Path(dataset_path)
        self.df = pd.read_csv(self.dataset_path)
        # Preprocess data for efficiency
        self.match_data = self.df.groupby('match_id').agg({
            'winner_champion': list,
            'loser_champion': list
        }).reset_index()

    def calculate_win_rates(self):
        """Calculate win rates for champion-opponent pairs."""
        wins = defaultdict(int)
        total = defaultdict(int)

        # Process each match
        for _, row in self.match_data.iterrows():
            winners = set(row['winner_champion'])
            losers = set(row['loser_champion'])
            
            # Count wins and total matches
            for X in winners:
                for Y in losers:
                    wins[(X, Y)] += 1
                    total[(X, Y)] += 1
            for X in losers:
                for Y in winners:
                    total[(X, Y)] += 1

        # Build results
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

        # Convert to DataFrame and sort
        win_rates_df = pd.DataFrame(results).sort_values(by=['Total Matches', 'Win Rate (%)'], ascending=False)
        return win_rates_df

    def compute_association_rules(self, min_support=0.005, min_threshold=0.1):
        """Compute association rules for winning teams."""
        # Group by match_id to get winning teams
        winning_teams = self.df.groupby('match_id')['winner_champion'].apply(list).reset_index(name='champions')

        # One-hot encode the data
        te = TransactionEncoder()
        te_ary = te.fit(winning_teams['champions']).transform(winning_teams['champions'])
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)

        # Apply Apriori algorithm
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)

        # Filter and sort rules
        single_consequent_rules = rules[rules['consequents'].apply(lambda x: len(x) == 1)]
        top_rules = single_consequent_rules.sort_values(by=['support', 'confidence'], ascending=False)
        return top_rules

    def save_to_csv(self, df, filename):
        """Save a DataFrame to a CSV file."""
        output_path = self.dataset_path.parent / filename
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Initialize the analyzer with the dataset
    analyzer = MatchDataAnalyzer('datasets/ranked_solo_duo_matchups.csv')

    # Calculate win rates and save
    win_rates = analyzer.calculate_win_rates()
    analyzer.save_to_csv(win_rates, 'win_rates.csv')

    # Compute association rules and save
    association_rules_df = analyzer.compute_association_rules()
    analyzer.save_to_csv(association_rules_df, 'association_rules.csv')

    # Optional: Display results
    print("Win Rates (Top 5):")
    print(win_rates.head())
    print("\nAssociation Rules (Top 5):")
    print(association_rules_df[['antecedents', 'consequents', 'support', 'confidence', 'lift']].head())