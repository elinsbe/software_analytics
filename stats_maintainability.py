import pandas as pd
import numpy as np
from scipy.stats import fisher_exact, mannwhitneyu

# Load AI / non-AI datasets
ai = pd.read_csv("csv/ts/pancake-frontend/cleaned_dataset_AI.csv")
non_ai = pd.read_csv("csv/ts/pancake-frontend/cleaned_dataset_nonAI.csv")

# Cliff's delta
def cliffs_delta(x, y):
    x = np.array(x)
    y = np.array(y)
    n_x = len(x)
    n_y = len(y)
    more = np.sum([xi > yj for xi in x for yj in y])
    less = np.sum([xi < yj for xi in x for yj in y])
    return (more - less) / (n_x * n_y)

results = []

# Reverted commits
ai_ratio = ai["is_reverted"].mean()
non_ai_ratio = non_ai["is_reverted"].mean()
a = ai["is_reverted"].sum()
b = len(ai) - a
c = non_ai["is_reverted"].sum()
d = len(non_ai) - c
table = [[a, b], [c, d]]

oddsratio, fisher_p = fisher_exact(table, alternative='two-sided')
risk_diff = ai_ratio - non_ai_ratio
odds_ai = a / b if b > 0 else np.nan
odds_non_ai = c / d if d > 0 else np.nan
odds_ratio = odds_ai / odds_non_ai if odds_non_ai > 0 else np.nan

results.append({
    "metric": "reverted_commits",
    "AI_ratio": ai_ratio,
    "nonAI_ratio": non_ai_ratio,
    "risk_difference": risk_diff,
    "odds_ratio": odds_ratio,
    "fisher_p": fisher_p
})

# Changes in 30 days
stat, p = mannwhitneyu(ai["changes_in_30_days"], non_ai["changes_in_30_days"], alternative="two-sided")
delta = cliffs_delta(ai["changes_in_30_days"], non_ai["changes_in_30_days"])

results.append({
    "metric": "changes_in_30_days",
    "AI_mean": ai["changes_in_30_days"].mean(),
    "nonAI_mean": non_ai["changes_in_30_days"].mean(),
    "U_stat": stat,
    "p_value": p,
    "cliffs_delta": delta
})

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("csv/ts/pancake-frontend/statistical_results_maintainability.csv", index=False)

print("Saved statistical results to csv/ts/pancake-frontend/statistical_results_maintainability.csv")