import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# files


def duplication(df_ai, df_no_ai, path):
    mean_change_ai = df_ai["duplication_percentage"].mean()
    mean_change_no_ai = df_no_ai["duplication_percentage"].mean()

    print(f"Mean value of code duplication for AI: {mean_change_ai}")
    print(f"Mean value of code duplication for non-AI: {mean_change_no_ai}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Mean value of code duplication for AI: {mean_change_ai}\n")
        f.write(f"Mean value of code duplication for non-AI: {mean_change_no_ai}\n")
        f.write("\n \n")
        f.close()

    data = [
        df_ai["duplication_percentage"].dropna(),
        df_no_ai["duplication_percentage"].dropna(),
    ]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Duplication percentage")
    plt.title("Distribution of duplication percentage")

    plt.savefig(f"{path}/duplication.png")
    plt.clf()


def changes_in_30_days(df_ai, df_no_ai, path):
    mean_change_ai = df_ai["changes_in_30_days"].mean()
    mean_change_no_ai = df_no_ai["changes_in_30_days"].mean()

    print(f"Mean_value of AI for # of changes in 30 days: {mean_change_ai}")
    print(f"Mean_value of non AI for # of changes in 30 days:: {mean_change_no_ai}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Mean_value of AI for # of changes in 30 days: {mean_change_ai}\n")
        f.write(
            f"Mean_value of non AI for # of changes in 30 days: {mean_change_no_ai}\n"
        )
        f.write("\n \n")
        f.close()

    data = [
        df_ai["changes_in_30_days"].dropna(),
        df_no_ai["changes_in_30_days"].dropna(),
    ]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Number of changes in 30 days")
    plt.title("Distribution of changes in 30 days")

    plt.savefig(f"{path}/changes_in_30_days.png")
    plt.clf()


def files(df_ai, df_no_ai, path):
    mean_value_AI = df_ai["files"].mean()
    mean_value_NO_AI = df_no_ai["lines"].mean()

    print(f"Mean_value of AI for files changed: {mean_value_AI}")
    print(f"Mean_value of NON AI for files changed: {mean_value_NO_AI}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Mean_value of AI for files changed: {mean_value_AI}\n")
        f.write(f"Mean_value of NON AI for files changed: {mean_value_NO_AI}\n")
        f.write("\n \n")
        f.close()

    data = [df_ai["files"].dropna(), df_no_ai["files"].dropna()]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Files changed")
    plt.title("Distribution of files changed")

    plt.savefig(f"{path}/files.png")
    plt.clf()


def mean_lines(df_ai, df_no_ai, path):
    mean_value_AI = df_ai["lines"].mean()
    mean_value_NO_AI = df_no_ai["lines"].mean()

    print(f"Mean_value of AI for average lines changed: {mean_value_AI}")
    print(f"Mean_value of NON AI for average lines changed: {mean_value_NO_AI}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Mean_value of AI for average lines changed: {mean_value_AI}\n")
        f.write(f"Mean_value of NON AI for average lines changed: {mean_value_NO_AI}\n")
        f.write("\n \n")
        f.close()

    data = [df_ai["lines"].dropna(), df_no_ai["lines"].dropna()]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Lines changed")
    plt.title("Distribution of Lines changed")

    plt.savefig(f"{path}/lines.png")
    plt.clf()


def insertion_deletion_ratio(df_ai, df_no_ai, path):
    # Ratio of inserts and deletetions

    df_ai["ratio_insertion_deletion"] = df_ai["insertions"] / df_ai[
        "deletions"
    ].replace(0, np.nan)
    df_no_ai["ratio_insertion_deletion"] = df_no_ai["insertions"] / df_no_ai[
        "deletions"
    ].replace(0, np.nan)

    ratio_value_AI = df_ai["ratio_insertion_deletion"].mean()
    ratio_NO_AI = df_no_ai["ratio_insertion_deletion"].mean()

    print(f"Ratio of insertion/deletion for AI: {ratio_value_AI}")
    print(f"Ratio of insertion/deletion for NON AI: {ratio_NO_AI}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Ratio of insertion/deletion for AI: {ratio_value_AI}\n")
        f.write(f"Ratio of insertion/deletion for NON AI: {ratio_NO_AI}\n")
        f.write("\n \n")
        f.close()

    data = [
        df_ai["ratio_insertion_deletion"].dropna(),
        df_no_ai["ratio_insertion_deletion"].dropna(),
    ]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Insertion / Deletion Ratio")
    plt.title("Distribution of Insertion/Deletion Ratio")

    plt.savefig(f"{path}/ratio.png")
    plt.clf()


def insertions(df_ai, df_no_ai, path):
    # Insertions only

    df_AI = df_ai
    df_NO_AI = df_no_ai

    mean_insertions_AI = df_AI["insertions"].mean()
    mean_insertions_NO_AI = df_NO_AI["insertions"].mean()

    print(f"Average for insertions for AI: {mean_insertions_AI}")
    print(f"Average of insertions for NON AI: {mean_insertions_NO_AI}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Average for insertions for AI: {mean_insertions_AI}\n")
        f.write(f"Average of insertions for NON AI: {mean_insertions_NO_AI}\n")
        f.write("\n \n")
        f.close()

    data = [df_AI["insertions"].dropna(), df_NO_AI["insertions"].dropna()]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Insertions")
    plt.title("Distribution of insertions")

    plt.savefig(f"{path}/insertions.png")
    plt.clf()


def deletions(df_ai, df_no_ai, path):
    # Deletions only

    df_AI = df_ai
    df_NO_AI = df_no_ai
    mean_insertions_AI = df_AI["deletions"].mean()
    mean_insertions_NO_AI = df_NO_AI["deletions"].mean()

    print(f"Average for deletions for AI: {mean_insertions_AI}")
    print(f"Average of deletions for NON AI: {mean_insertions_NO_AI}")

    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Average for deletions for AI: {mean_insertions_AI}\n")
        f.write(f"Average of deletions for NON AI: {mean_insertions_NO_AI}\n")
        f.write("\n \n")
        f.close()

    data = [df_AI["deletions"].dropna(), df_NO_AI["deletions"].dropna()]

    plt.violinplot(data, showmeans=True)

    plt.xticks([1, 2], ["AI", "Non-AI"])
    plt.ylabel("Deletions")
    plt.title("Distribution of deletions")

    plt.savefig(f"{path}/deletions.png")
    plt.clf()


def reverted_commits(df_ai, df_no_ai, path):
    count_ai = df_ai["is_reverted"].sum()
    count_no_ai = df_no_ai["is_reverted"].sum()

    # Bar plot
    plt.figure(figsize=(6, 6))
    plt.bar(
        ["AI Commits", "Non-AI Commits"],
        [count_ai, count_no_ai],
        color=["blue", "orange"],
    )
    print(f"Number of reverted commits (AI): {count_ai}")
    print(f"Number of reverted commits (non-AI): {count_no_ai}")
    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Number of reverted commits (AI): {count_ai}\n")
        f.write(f"Number of reverted commits (non-AI): {count_no_ai}\n")
        f.write("\n \n")
        f.close()

    plt.ylabel("Number of Reverted Commits")
    plt.title("Reverted Commits: AI vs Non-AI")
    plt.savefig(f"{path}/reverted.png")
    plt.clf()


def failed_pipelines(df_ai, df_no_ai, path):
    count_ai = df_ai["failed_pipeline"].sum()
    count_no_ai = df_no_ai["failed_pipeline"].sum()

    # Bar plot
    plt.figure(figsize=(6, 6))
    plt.bar(
        ["AI Commits", "Non-AI Commits"],
        [count_ai, count_no_ai],
        color=["blue", "orange"],
    )
    print(f"Number of failed pipelines (AI): {count_ai}")
    print(f"Number of failed pipelines (non-AI): {count_no_ai}")
    with open(f"{path}summary.txt", "a") as f:
        f.write(f"Number of failed pipelines (AI): {count_ai}\n")
        f.write(f"Number of failed pipelines (non-AI): {count_no_ai}\n")
        f.write("\n \n")
        f.close()

    plt.ylabel("Number of Failed Pipelines")
    plt.title("Failed Pipelines: AI vs Non-AI")
    plt.savefig(f"{path}/failed_pipelines.png")
    plt.clf()


def main():
    for language in os.listdir("csv/"):
        for repos in os.listdir(f"csv/{language}/"):
            output_path = f"csv/{language}/{repos}/results/"
            f = None
            if not os.path.exists(output_path):
                os.mkdir(output_path)

            if os.path.exists(f"{output_path}summary.txt"):
                os.remove(f"{output_path}summary.txt")
                f = open(f"{output_path}summary.txt", "x")
                f.close()

            path_ai = f"csv/{language}/{repos}/cleaned_dataset_AI.csv"
            path_no_ai = f"csv/{language}/{repos}/cleaned_dataset_nonAI.csv"

            df_ai = pd.read_csv(path_ai)
            df_no_ai = pd.read_csv(path_no_ai)

            mean_lines(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            insertion_deletion_ratio(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            insertions(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            deletions(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            reverted_commits(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            failed_pipelines(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            changes_in_30_days(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            duplication(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)
            files(df_ai=df_ai, df_no_ai=df_no_ai, path=output_path)


if __name__ == "__main__":
    main()
