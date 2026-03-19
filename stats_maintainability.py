import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from scipy.stats import mannwhitneyu

# Load AI / non-AI reverted commits
ai = pd.read_csv("csv/ts/ai_commits_reverted.csv")
non_ai = pd.read_csv("csv/ts/No_ai_commits_reverted.csv")

# Compute ratio of True
ai_ratio = ai["is_reverted"].mean()
non_ai_ratio = non_ai["is_reverted"].mean()

print(f"AI commits reverted: {ai_ratio*100:.2f}%")
print(f"Non-AI commits reverted: {non_ai_ratio*100:.2f}%")

a = ai["is_reverted"].sum()
b = len(ai) - a
c = non_ai["is_reverted"].sum()
d = len(non_ai) - c

table = [[a, b], [c, d]]

oddsratio, p = fisher_exact(table, alternative='two-sided')
print(f"Fisher exact test p-value = {p:.6f}")

risk_diff = ai_ratio - non_ai_ratio
odds_ai = a / b if b > 0 else np.nan
odds_non_ai = c / d if d > 0 else np.nan
odds_ratio = odds_ai / odds_non_ai if odds_non_ai > 0 else np.nan

print(f"Risk difference: {risk_diff:.3f}")
print(f"Odds ratio: {odds_ratio:.3f}")

# Number of changes in a month
ai_changes = pd.read_csv("csv/ts/changes_in_30_days_AI.csv")
non_ai_changes = pd.read_csv("csv/ts/changes_in_30_days_nonAI.csv")
print(ai_changes["changes_in_30_days"].describe())
print(non_ai_changes["changes_in_30_days"].describe())

stat, p = mannwhitneyu(
    ai_changes["changes_in_30_days"],
    non_ai_changes["changes_in_30_days"],
    alternative="two-sided"
)

print("Mann–Whitney U test for changes_in_30_days")
print(f"U statistic = {stat:.2f}")
print(f"p-value = {p:.6f}")


def cliffs_delta(x, y):
    x = np.array(x)
    y = np.array(y)
    n_x = len(x)
    n_y = len(y)
    more = np.sum([xi > yj for xi in x for yj in y])
    less = np.sum([xi < yj for xi in x for yj in y])
    return (more - less) / (n_x * n_y)

delta = cliffs_delta(
    ai_changes["changes_in_30_days"],
    non_ai_changes["changes_in_30_days"]
)

print(f"Cliff's delta = {delta:.3f}")