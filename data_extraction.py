from datetime import timedelta
import pandas as pd
from pydriller import Repository
import re
import remove_outliers
import os
import tempfile
import git


LANGAUGE = "ts"
FULL_REPO = "pancakeswap/pancake-frontend"
REPO = "pancake-frontend"

url_repos = ["https://github.com/pancakeswap/pancake-frontend"]
COLUMNS = ["files", "insertions", "deletions", "lines"]


def get_ai_commits(repo_name: str):
    # these columns are in the original dataset, but not needed for out analysis so that are removed.
    print(f"Getting all commits from research dataset for repo: {repo_name}")
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


def add_reverts(df, url_repo):
    print("Adding revert field!")

    hashes_set = set(df["hash"])
    reverted_commits = set()

    for commit in Repository(url_repo).traverse_commits():
        if "reverts commit" in (commit.msg or "").lower():
            match = re.search(r"reverts commit (\w+)", commit.msg, re.IGNORECASE)
            if match:
                reverted_hash = match.group(1)
                if reverted_hash in hashes_set:
                    reverted_commits.add(reverted_hash)

    # Add column instead of replacing dataframe
    df["is_reverted"] = df["hash"].isin(reverted_commits)

    print("Complete!")
    return df


def extract_non_ai(all_commits, ai_commits):
    merged = all_commits.merge(
        ai_commits, left_on="hash", right_on="commit_id", how="left", indicator=True
    )

    df2_unmatched = merged[merged["_merge"] == "left_only"]
    df2_unmatched = df2_unmatched.drop(
        columns=["_merge", "programming_language", "repo_name", "commit_id", "tool"]
    )

    print(f"Number of lines in NON AI, within timeframe! {len(df2_unmatched)}")
    return df2_unmatched


def extract_ai(all_commits, ai_commits):
    print("Extract AI commits")
    merged = all_commits.merge(
        ai_commits, left_on="hash", right_on="commit_id", how="left", indicator=True
    )

    df2_ai = merged[merged["_merge"] == "both"]
    df2_ai = df2_ai.drop(
        columns=["_merge", "programming_language", "repo_name", "commit_id", "tool"]
    )
    print("Complete!")
    return df2_ai


def extract_data(url_repo, repo):

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
    df_original_dataset = add_reverts(repo_commits, url_repo=url_repo)

    df_no_ai = extract_non_ai(df_original_dataset, ai_commits)
    df_ai = extract_ai(df_original_dataset, ai_commits)

    print(f"Ratio: {len(df_ai) / len(df_no_ai)}")
    no_ai_path = f"csv/{LANGAUGE}/{repo.split('/')[-1]}/with_outliers_no_ai.csv"
    ai_path = f"csv/{LANGAUGE}/{repo.split('/')[-1]}/with_outliers_ai.csv"

    df_original_dataset.to_csv(no_ai_path)
    df_ai.to_csv(ai_path)
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
