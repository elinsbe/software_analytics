import subprocess
import pandas as pd
import numpy as np

DATASET_PATH = "reports/pancake-frontend/cleaned_dataset_nonAI.csv" 
OUTPUT_PATH = "cc_results_nonAI.csv"

INCLUDE_EXT = ".ts"
EXCLUDE_PATTERNS = [".test.ts", ".d.ts"]

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def is_valid_ts_file(file):
    if not file.endswith(INCLUDE_EXT):
        return False
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file:
            return False
    return True

def get_modified_ts_files(commit):
    cmd = f"git diff --name-only {commit}^ {commit}"
    out, _ = run_cmd(cmd)
    files = out.split("\n") if out else []
    return [f for f in files if is_valid_ts_file(f)]

def checkout(commit):
    run_cmd(f"git checkout -f {commit}")

def run_lizard(files):
    if not files:
        return []

    files_str = " ".join(files)
    cmd = f"python3 -m lizard {files_str}"
    out, err = run_cmd(cmd)

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

def process_commit(commit, insertions, deletions):
    print(f"Processing {commit}...")

    files = get_modified_ts_files(commit)

    if not files:
        return None

    # BEFORE
    checkout(f"{commit}^")
    cc_before_list = run_lizard(files)
    n_before = len(cc_before_list)
    cc_before = compute_avg(cc_before_list)

    # AFTER
    checkout(commit)
    cc_after_list = run_lizard(files)
    n_after = len(cc_after_list)
    cc_after = compute_avg(cc_after_list)

    if n_before == 0 and n_after == 0:
        print(f"Skipping {commit} (no functions found)")
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

    for _, row in df.iterrows():
        commit = row["hash"]
        insertions = row.get("insertions", 0)
        deletions = row.get("deletions", 0)

        try:
            res = process_commit(commit, insertions, deletions)
            if res:  # only append commits with at least one function
                results.append(res)
        except Exception as e:
            print(f"Error processing {commit}: {e}")

    # Restore branch
    checkout("develop")

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved results to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()