from datetime import timedelta
import pandas as pd
from pydriller import Repository
import re
import remove_outliers
import os
import tempfile
import git
from github import Github, Auth
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import duplication

LANGAUGE = "ts"
FULL_REPO = "pancakeswap/pancake-frontend"
REPO = "pancake-frontend"

url_repos = ["https://github.com/pancakeswap/pancake-frontend"]
FINAL_COLUMNS = [
    "hash",
    "date",
    "files",
    "deletions",
    "insertions",
    "lines",
    "is_reverted",
    "failed_pipeline",
    "changes_in_30_days",
    "duplication_percentage",
]


def get_ai_commits(repo_name: str):
    # these columns are in the original dataset, but not needed for out analysis so that are removed.
    print(f"Getting all commits from research dataset for repo: {repo_name}")
    repo_name = repo_name.lower()
    unwanted_colums_in_original = [
        "branch",
        "committer",
        "author",
        "mention_language",
        "github_link",
        "mention",
    ]
    df = pd.read_csv("commit_mentions.csv")
    df.drop(columns=unwanted_colums_in_original, inplace=True)
    df = df[df["repo_name"].isin([repo_name])]
    print(f"Analyzing {repo}!")

    return df


def get_all_commits_from_repo(url_repo, start_date, end_date):
    print(f"Getting all commits from online repo for {url_repo}")
    rows = []

    for commit in Repository(
        url_repo, since=start_date, to=end_date
    ).traverse_commits():
        rows.append(
            {
                "hash": commit.hash,
                "date": commit.author_date,
                "files": len(commit.modified_files),
                "deletions": commit.deletions,
                "insertions": commit.insertions,
                "lines": commit.lines,
            }
        )
    print("Completed!")
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


def add_reverts(df, url_repo, start_date, end_date):
    print("Adding revert field!")

    hashes_set = set(df["hash"])
    reverted_commits = set()

    for commit in Repository(
        url_repo, since=start_date, to=end_date
    ).traverse_commits():
        if "reverts commit" in (commit.msg or "").lower():
            match = re.search(r"reverts commit (\w+)", commit.msg, re.IGNORECASE)
            if match:
                reverted_hash = match.group(1)
                if reverted_hash in hashes_set:
                    reverted_commits.add(reverted_hash)
    df["is_reverted"] = df["hash"].isin(reverted_commits).astype(int)

    print("Complete!")
    return df


def annotate_failed_pipelines(
    df,
    repo_name,
    max_workers=10,
):
    print("Calculate failed pipelines")
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token)
    g = Github(auth=auth)

    df_commits = df
    repo = g.get_repo(repo_name)

    def check_failed(commit_sha):
        try:
            runs = repo.get_workflow_runs(head_sha=commit_sha)
            for run in runs:
                if run.conclusion == "failure":
                    return commit_sha, True
            return commit_sha, False
        except Exception as e:
            print(f"Error checking commit {commit_sha}: {e}")
            return commit_sha, False

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sha = {
            executor.submit(check_failed, sha): sha for sha in df_commits["hash"]
        }
        for future in as_completed(future_to_sha):
            results.append(future.result())
    df_results = pd.DataFrame(results, columns=["hash", "failed_pipeline"])
    df_commits = df_commits.merge(df_results, on="hash", how="left")
    print("Completed")

    return df_commits


def changes_after_30_days(df_old, url_repo, start_date, end_date):
    print("Add number of changes in 30 days!")

    function_data = {}
    valid_hashes = set(df_old["hash"])

    for commit in Repository(
        url_repo, since=start_date, to=end_date
    ).traverse_commits():
        if commit.hash not in valid_hashes:
            continue

        for mod in commit.modified_files:
            if not mod.new_path or not mod.methods:
                continue

            for m in mod.methods:
                name = (m.name or "").strip().lower()

                if (
                    not name
                    or name == "<anonymous>"
                    or name == "anonymous"
                    or "lambda" in name
                    or "=>" in name
                ):
                    continue

                key = (commit.hash, mod.new_path, m.name)

                if key not in function_data:
                    function_data[key] = {
                        "hash": commit.hash,
                        "start_date": commit.author_date,
                        "changes": 0,
                    }

                start = function_data[key]["start_date"]

                if commit.author_date <= start + timedelta(days=30):
                    function_data[key]["changes"] += 1

    df = pd.DataFrame(function_data.values())

    if df.empty:
        df_old["changes_in_30_days"] = 0
        return df_old

    df_changes = (
        df.groupby("hash")["changes"]
        .sum()
        .reset_index()
        .rename(columns={"changes": "changes_in_30_days"})
    )

    df_final = df_old.merge(df_changes, on="hash", how="left")

    df_final["changes_in_30_days"] = (
        df_final["changes_in_30_days"].fillna(0).astype(int)
    )

    print("Complete!")
    return df_final


def get_dates(url_repo, df):
    print("Cloning repo in temp directory")
    with tempfile.TemporaryDirectory() as temp_dir:
        repo = git.Repo.clone_from(
            url_repo, temp_dir, multi_options=["--filter=blob:none", "--no-checkout"]
        )
        print(f"Cloned in {temp_dir}")

        hashes = df["commit_id"].dropna().astype(str).tolist()
        if not hashes:
            return None, None

        # Get only dates
        print("Getting dates!")
        output = repo.git.show(hashes, s=True, format="%ci")

        dates = pd.to_datetime(output.splitlines(), utc=True)

        start = dates.min()
        end = dates.max()

        print(f"Earliest date: {start}")
        print(f"Latest date: {end}")

        return start, end


def extract_data(url_repo, repo):
    ai_commits = get_ai_commits(repo)
    start_date, end_date = get_dates(url_repo=url_repo, df=ai_commits)
    # find max/min dates
    repo_commits = get_all_commits_from_repo(
        url_repo=url_repo, start_date=start_date, end_date=end_date
    )

    # Add to see if it was reverted
    df_original_dataset = add_reverts(
        repo_commits, url_repo=url_repo, start_date=start_date, end_date=end_date
    )

    df_original_dataset = annotate_failed_pipelines(
        df=df_original_dataset, repo_name=repo
    )

    df_original_dataset = changes_after_30_days(
        df_old=df_original_dataset,
        url_repo=url_repo,
        start_date=start_date,
        end_date=end_date,
    )
    df_original_dataset = duplication.code_duplication(
        df=df_original_dataset,
        url_repo=url_repo,
    )

    # Ensure matching types and strip whitespace
    df_original_dataset["hash"] = df_original_dataset["hash"].astype(str).str.strip()
    ai_commits["commit_id"] = ai_commits["commit_id"].astype(str).str.strip()

    # Extract non-AI commits
    df_no_ai = df_original_dataset[
        ~df_original_dataset["hash"].isin(ai_commits["commit_id"])
    ].copy()

    # Extract AI commits for completeness
    df_ai = df_original_dataset[
        df_original_dataset["hash"].isin(ai_commits["commit_id"])
    ].copy()

    print(f"Number of non-AI commits: {len(df_no_ai)}, AI commits: {len(df_ai)}")
    print(f"Ratio: {len(df_ai) / len(df_no_ai) if len(df_no_ai) > 0 else 'N/A'}")

    no_ai_path = f"csv/{LANGAUGE}/{repo.split('/')[-1]}/with_outliers_no_ai.csv"
    ai_path = f"csv/{LANGAUGE}/{repo.split('/')[-1]}/with_outliers_ai.csv"

    df_no_ai = df_no_ai[FINAL_COLUMNS].copy()
    df_ai = df_ai[FINAL_COLUMNS].copy()

    # Save the filtered DataFrames
    df_no_ai.to_csv(no_ai_path, index=False)
    df_ai.to_csv(ai_path, index=False)

    return no_ai_path, ai_path


if __name__ == "__main__":
    # add /change to change analysis repo
    for url_repo in url_repos:
        if not os.path.exists(f"csv/{LANGAUGE}/{url_repo.split('/')[-1]}"):
            print("Making directory path...")
            os.makedirs(f"csv/{LANGAUGE}/{url_repo.split('/')[-1]}")
        repo = f"{url_repo.split('/')[-2]}/{url_repo.split('/')[-1]}"
        no_ai_path, ai_path = extract_data(url_repo, repo)
        print("Extracting date done. Removing outliers...")

        remove_outliers.main(
            ai_input_path=ai_path,
            non_ai_input_path=no_ai_path,
            repo=repo.split("/")[-1],
            language=LANGAUGE,
        )
