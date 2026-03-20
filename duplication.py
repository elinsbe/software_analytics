import pandas as pd
import subprocess
import os
import json

# Load hashes
df = pd.read_csv("reports/cleaned_dataset_nonAI.csv")

results = []

for commit in df["hash"]:

    print(f"Processing {commit}")

    # Checkout commit
    subprocess.run(["git", "checkout", commit], check=True)

    # Run jscpd (TypeScript only)
    subprocess.run([
        "npx", "jscpd", ".",
        "--reporters", "json",
        "--output", "reports",
        "--pattern", "**/*.ts"
    ], check=True)

    # Path to report
    report_path = "reports/jscpd-report.json"

    duplication = None

    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            data = json.load(f)

        # Extract total duplication percentage
        duplication = data["statistics"]["total"]["percentage"]

    results.append({
        "hash": commit,
        "duplication_percentage": duplication
    })

# Return to main branch
subprocess.run(["git", "checkout", "develop"], check=True)

# Save results
output_df = pd.DataFrame(results)
output_df.to_csv("per_commit_duplication_nonAI.csv", index=False)

print("Saved to per_commit_duplication_nonAI.csv")