import pandas as pd
import subprocess
import os
import json
import tempfile
import git


def code_duplication(df, url_repo):
    print("Cloning repo in temp directory...")

    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        repo = git.Repo.clone_from(
            url_repo, temp_dir, multi_options=["--filter=blob:none"]
        )

        for commit in df["hash"]:
            print(f"Processing {commit}")

            try:
                # Checkout commit inside repo
                subprocess.run(["git", "checkout", commit], cwd=temp_dir, check=True)

                # Run jscpd
                subprocess.run(
                    [
                        "npx",
                        "jscpd",
                        ".",
                        "--reporters",
                        "json",
                        "--output",
                        "reports",
                        "--pattern",
                        "**/*.ts",
                    ],
                    cwd=temp_dir,
                    check=True,
                )

                report_path = os.path.join(temp_dir, "reports/jscpd-report.json")
                duplication = None

                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        data = json.load(f)
                    duplication = data["statistics"]["total"]["percentage"]

                results.append({"hash": commit, "duplication_percentage": duplication})

            except subprocess.CalledProcessError:
                print(f"Failed on commit {commit}")
                results.append({"hash": commit, "duplication_percentage": None})

        # Optional: return to branch
        subprocess.run(["git", "checkout", "develop"], cwd=temp_dir, check=False)

    # Save results
    output_df = pd.DataFrame(results)
    df_final = df.merge(output_df, on="hash", how="left")
    print("Completed!")
    return df_final
