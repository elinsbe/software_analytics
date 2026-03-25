import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu

def cliffs_delta(x, y):
    x = np.array(x)
    y = np.array(y)
    n_x = len(x)
    n_y = len(y)
    more = np.sum([xi > yj for xi in x for yj in y])
    less = np.sum([xi < yj for xi in x for yj in y])
    return (more - less) / (n_x * n_y)

# Store results in a list
results = []

# Load datasets
ai = pd.read_csv("csv/ts/pancake-frontend/cleaned_dataset_AI.csv")
non_ai = pd.read_csv("csv/ts/pancake-frontend/cleaned_dataset_nonAI.csv")

# Basic metrics
metrics = ["files", "deletions", "insertions", "lines"]
for metric in metrics:
    stat, p = mannwhitneyu(ai[metric], non_ai[metric], alternative="two-sided")
    delta = cliffs_delta(ai[metric], non_ai[metric])
    results.append({
        "metric": metric,
        "U": stat,
        "p_value": p,
        "cliffs_delta": delta
    })

# Deletions / Insertions ratio
ai_ratio = ai["deletions"] / ai["insertions"].replace(0, np.nan)
non_ai_ratio = non_ai["deletions"] / non_ai["insertions"].replace(0, np.nan)
ai_ratio = ai_ratio.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
non_ai_ratio = non_ai_ratio.replace([np.inf, -np.inf], np.nan).dropna().astype(float)

stat, p = mannwhitneyu(ai_ratio, non_ai_ratio, alternative="two-sided")
delta = cliffs_delta(ai_ratio, non_ai_ratio)
results.append({
    "metric": "deletions/insertions_ratio",
    "U": stat,
    "p_value": p,
    "cliffs_delta": delta
})

# Duplication percentage
stat, p = mannwhitneyu(
    ai["duplication_percentage"],
    non_ai["duplication_percentage"],
    alternative="two-sided"
)
delta = cliffs_delta(
    ai["duplication_percentage"],
    non_ai["duplication_percentage"]
)
results.append({
    "metric": "duplication_percentage",
    "U": stat,
    "p_value": p,
    "cliffs_delta": delta
})

# Cyclomatic Complexity
cc_ai = pd.read_csv("csv/ts/pancake-frontend/cc_results_AI.csv")
cc_non_ai = pd.read_csv("csv/ts/pancake-frontend/cc_results_nonAI.csv")

for metric in ["delta_cc", "delta_cc_norm"]:
    stat, p = mannwhitneyu(cc_ai[metric], cc_non_ai[metric], alternative="two-sided")
    delta = cliffs_delta(cc_ai[metric], cc_non_ai[metric])
    results.append({
        "metric": f"cyclomatic_complexity_{metric}",
        "U": stat,
        "p_value": p,
        "cliffs_delta": delta
    })

results_df = pd.DataFrame(results)
results_df.to_csv("csv/ts/pancake-frontend/statistical_results_complexity.csv", index=False)
print("Saved statistical results to csv/ts/pancake-frontend/statistical_results_complexity.csv")