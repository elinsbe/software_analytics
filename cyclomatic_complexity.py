import subprocess
import pandas as pd
import numpy as np
import tempfile
import git
import os

# use cleaned_dataset_AI.csv to get results for the AI commits
# use cleaned_dataset_nonAI.csv to get results for the human-written commits
DATASET_PATH = "csv/cs/Chatdollkit/cleaned_dataset_AI.csv"
OUTPUT_PATH = "csv/cs/Chatdollkit/cc_results_AI.csv"
# REPO_URL = "https://github.com/pancakeswap/pancake-frontend"
REPO_URL = "https://github.com/uezo/ChatdollKit"

INCLUDE_EXT = ".cs"
EXCLUDE_PATTERNS = [".test.cs", ".d.cs"]


def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip(), result.stderr.strip()


def is_valid_ts_file(file):
    if not file.endswith(INCLUDE_EXT):
        return False
    return not any(p in file for p in EXCLUDE_PATTERNS)


def get_modified_ts_files(commit, cwd):
    cmd = f"git diff --name-only {commit}^ {commit}"
    out, _ = run_cmd(cmd, cwd=cwd)
    files = out.split("\n") if out else []
    return [f for f in files if is_valid_ts_file(f)]


def run_lizard(files, cwd):
    if not files:
        return []

    existing_files = [
        f for f in files if os.path.exists(os.path.join(cwd, f))
    ]

    if not existing_files:
        return []

    files_str = " ".join(existing_files)
    cmd = f"python3 -m lizard {files_str}"
    out, _ = run_cmd(cmd, cwd=cwd)

    cc_values = []

    for line in out.split("\n"):
        parts = line.strip().split()
        if len(parts) > 2:
            try:
                cc = int(parts[1])
                cc_values.append(cc)
            except:
                continue

    return cc_values


def compute_avg(cc_list):
    return float(np.mean(cc_list)) if cc_list else 0.0


def process_commit(commit, insertions, deletions, repo_dir):
    print(f"Processing {commit}...")

    files = get_modified_ts_files(commit, repo_dir)

    if not files:
        return None

    # BEFORE
    run_cmd(f"git checkout {commit}^", cwd=repo_dir)
    cc_before_list = run_lizard(files, repo_dir)
    n_before = len(cc_before_list)
    cc_before = compute_avg(cc_before_list)

    # AFTER
    run_cmd(f"git checkout {commit}", cwd=repo_dir)
    cc_after_list = run_lizard(files, repo_dir)
    n_after = len(cc_after_list)
    cc_after = compute_avg(cc_after_list)

    if n_before == 0 and n_after == 0:
        return None

    delta_cc = cc_after - cc_before
    total_changes = insertions + deletions
    delta_cc_norm = delta_cc / total_changes if total_changes > 0 else 0

    return {
        "hash": commit,
        "cc_before": cc_before,
        "cc_after": cc_after,
        "delta_cc": delta_cc,
        "delta_cc_norm": delta_cc_norm,
        "n_functions_before": n_before,
        "n_functions_after": n_after
    }


def main():
    df = pd.read_csv(DATASET_PATH)
    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        print("Cloning repo...")
        git.Repo.clone_from(REPO_URL, temp_dir, multi_options=["--filter=blob:none"])

        for _, row in df.iterrows():
            commit = row["hash"]
            insertions = row.get("insertions", 0)
            deletions = row.get("deletions", 0)

            try:
                res = process_commit(commit, insertions, deletions, temp_dir)
                if res:
                    results.append(res)
            except Exception as e:
                print(f"Error processing {commit}: {e}")

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved results to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()