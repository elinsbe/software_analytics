import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu

def cliffs_delta(x, y):
    """
    Compute Cliff's Delta effect size between two arrays.
    Returns value between -1 and 1.
    """
    x = np.array(x)
    y = np.array(y)
    n_x = len(x)
    n_y = len(y)

    # Pairwise comparisons
    more = np.sum([xi > yj for xi in x for yj in y])
    less = np.sum([xi < yj for xi in x for yj in y])
    delta = (more - less) / (n_x * n_y)
    return delta

# Load cleaned datasets
ai = pd.read_csv("csv/ts/cleaned_dataset_AI.csv")
non_ai = pd.read_csv("csv/ts/cleaned_dataset_nonAI.csv")

# Metrics to compare
metrics = ["files", "deletions", "insertions", "lines"]

for metric in metrics:
    stat, p = mannwhitneyu(
        ai[metric],
        non_ai[metric],
        alternative="two-sided"
    )

    delta = cliffs_delta(ai[metric], non_ai[metric])
    print(f"basic metrics: {metric}")
    print(f"U={stat:.2f}, p={p:.6f}, Cliff's δ={delta:.3f} \n")

# Compute ratio
ai_ratio = ai["deletions"] / ai["insertions"].replace(0, np.nan)
non_ai_ratio = non_ai["deletions"] / non_ai["insertions"].replace(0, np.nan)

# Remove NaN values
ai_ratio = ai_ratio.replace([np.inf, -np.inf], np.nan).dropna()
non_ai_ratio = non_ai_ratio.replace([np.inf, -np.inf], np.nan).dropna()

ai_ratio = ai_ratio.astype(float)
non_ai_ratio = non_ai_ratio.astype(float)

stat, p = mannwhitneyu(
    ai_ratio,
    non_ai_ratio,
    alternative="two-sided"
)

delta = cliffs_delta(ai_ratio, non_ai_ratio)
print("ratio test")
print(f"U={stat:.2f}, p={p:.6f}, Cliff's δ={delta:.3f}")

# Duplication results 
dup_ai = pd.read_csv("csv/ts/per_commit_duplication_AI.csv")
dup_non_ai = pd.read_csv("csv/ts/per_commit_duplication_nonAI.csv")

stat, p = mannwhitneyu(
    dup_ai["duplication_percentage"],
    dup_non_ai["duplication_percentage"],
    alternative="two-sided"
)
print("\n duplication percentage")
delta = cliffs_delta(dup_ai["duplication_percentage"], dup_non_ai["duplication_percentage"])
print(f"U={stat:.2f}, p={p:.6f}, Cliff's δ={delta:.3f}")

# Cyclometic Complexity
cc_ai = pd.read_csv("csv/ts/cc_results_AI.csv")
cc_non_ai = pd.read_csv("csv/ts/cc_results_nonAI.csv")

# Compare average CC per commit
for metric in ["delta_cc", "delta_cc_norm"]:
    stat, p = mannwhitneyu(
        cc_ai[metric],
        cc_non_ai[metric],
        alternative="two-sided"
    )
    print(f"\n cyclomatic complexity: {metric}")
    delta = cliffs_delta(cc_ai[metric], cc_non_ai[metric])
    print(f"U={stat:.2f}, p={p:.6f}, Cliff's δ={delta:.3f}")