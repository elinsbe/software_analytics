import pandas as pd
import subprocess
import os
import json
import tempfile
import git
from concurrent.futures import ThreadPoolExecutor, as_completed

from pydriller import Repository


def get_changed_files_map(url_repo, hashes):
    commit_files = {}

    for commit in Repository(url_repo).traverse_commits():
        if commit.hash in hashes:
            files = [
                m.new_path
                for m in commit.modified_files
                if m.new_path and m.new_path.endswith(".ts")
            ]
            commit_files[commit.hash] = files

    return commit_files


def code_duplication(df, url_repo, max_workers=None):
    print("Running duplication analysis (changed files only)...")

    if max_workers is None:
        import os

        max_workers = min(8, os.cpu_count() or 4)

    hashes = df["hash"].tolist()
    commit_files_map = get_changed_files_map(url_repo, set(hashes))

    def worker(commits_chunk):
        results = []

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                git.Repo.clone_from(
                    url_repo, temp_dir, multi_options=["--filter=blob:none"]
                )

                for commit in commits_chunk:
                    try:
                        files = commit_files_map.get(commit, [])

                        # Skip if no relevant files
                        if not files:
                            results.append(
                                {"hash": commit, "duplication_percentage": 0}
                            )
                            continue

                        subprocess.run(
                            ["git", "checkout", commit],
                            cwd=temp_dir,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )

                        # Only keep files that exist in this checkout
                        existing_files = [
                            f
                            for f in files
                            if os.path.exists(os.path.join(temp_dir, f))
                        ]

                        if not existing_files:
                            results.append(
                                {"hash": commit, "duplication_percentage": 0}
                            )
                            continue

                        subprocess.run(
                            [
                                "jscpd",
                                *existing_files,
                                "--reporters",
                                "json",
                                "--output",
                                "reports",
                                "--silent",
                            ],
                            cwd=temp_dir,
                            check=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )

                        report_path = os.path.join(
                            temp_dir, "reports/jscpd-report.json"
                        )

                        duplication = 0

                        if os.path.exists(report_path):
                            with open(report_path, "r") as f:
                                data = json.load(f)

                            duplication = data["statistics"]["total"]["percentage"]

                        results.append(
                            {"hash": commit, "duplication_percentage": duplication}
                        )

                    except Exception:
                        results.append({"hash": commit, "duplication_percentage": None})

            except Exception:
                for commit in commits_chunk:
                    results.append({"hash": commit, "duplication_percentage": None})

        return results

    # Chunking
    commits = hashes
    chunk_size = max(1, len(commits) // max_workers)
    chunks = [commits[i : i + chunk_size] for i in range(0, len(commits), chunk_size)]

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, chunk) for chunk in chunks]
        for f in as_completed(futures):
            results.extend(f.result())

    output_df = pd.DataFrame(results)
    print("Completed!")

    return df.merge(output_df, on="hash", how="left")
