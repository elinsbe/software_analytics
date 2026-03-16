import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu

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

    print(f"{metric}")
    print(f"  U statistic = {stat:.2f}")
    print(f"  p-value     = {p:.6f}\n")

# Compute ratio safely
ai_ratio = ai["deletions"] / ai["insertions"].replace(0, np.nan)
non_ai_ratio = non_ai["deletions"] / non_ai["insertions"].replace(0, np.nan)

# Remove NaN and infinite values
ai_ratio = ai_ratio.replace([np.inf, -np.inf], np.nan).dropna()
non_ai_ratio = non_ai_ratio.replace([np.inf, -np.inf], np.nan).dropna()

# Ensure numeric type
ai_ratio = ai_ratio.astype(float)
non_ai_ratio = non_ai_ratio.astype(float)

# Now run test
stat, p = mannwhitneyu(
    ai_ratio,
    non_ai_ratio,
    alternative="two-sided"
)

print("Ratio test")
print("U statistic =", stat)
print("p-value =", p)