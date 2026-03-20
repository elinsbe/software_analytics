import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

COLUMNS = ["files", "insertions", "deletions", "lines"]


def remove_outliers_iqr(df, columns, threshold=1.5):
    mask = pd.Series(True, index=df.index)
    bounds = {}

    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR

        bounds[col] = (lower, upper)

        mask &= (df[col] >= lower) & (df[col] <= upper)

    cleaned = df[mask]
    outliers = df[~mask]

    return cleaned, outliers, bounds


def plot_distributions(df, title):
    fig, axes = plt.subplots(2, len(COLUMNS), figsize=(16, 6))

    for i, col in enumerate(COLUMNS):
        # Histogram
        df[col].hist(ax=axes[0, i], bins=50)
        axes[0, i].set_title(f"{col} histogram")
        axes[0, i].set_xlabel(col)
        axes[0, i].set_ylabel("Frequency")

        # Boxplot
        axes[1, i].boxplot(df[col], vert=False)
        axes[1, i].set_title(f"{col} boxplot")
        axes[1, i].set_xlabel(col)

    fig.suptitle(title)
    plt.tight_layout()
    plt.show()


def main(ai_input_path, non_ai_input_path, repo, language):

    # AI

    input_path = Path(ai_input_path)
    df = pd.read_csv(input_path)

    print("Original dataset:", len(df), "rows")

    # visualize before
    plot_distributions(df, "Before Outlier Removal AI")

    # remove outliers
    cleaned, outliers, bounds = remove_outliers_iqr(df, COLUMNS)

    print("Cleaned dataset:", len(cleaned), "rows")
    print("Outliers removed:", len(outliers))

    print("\nBounds used:")
    for k, v in bounds.items():
        print(k, v)

    # visualize after
    plot_distributions(cleaned, "After Outlier Removal AI")

    # save results
    cleaned.to_csv(f"csv/{language}/{repo}/cleaned_dataset_AI.csv", index=False)
    outliers.to_csv(f"csv/{language}/{repo}/removed_outliers_AI.csv", index=False)

    print("\nSaved:")
    print(f"csv/{language}/{repo}/cleaned_dataset_AI.csv")
    print(f"csv/{language}/{repo}/removed_outliers_AI.csv")

    # non-AI

    input_path = Path(non_ai_input_path)
    df = pd.read_csv(input_path)

    print("Original dataset:", len(df), "rows")

    # visualize before
    plot_distributions(df, "Before Outlier Removal non-AI")

    # remove outliers
    cleaned, outliers, bounds = remove_outliers_iqr(df, COLUMNS)

    print("Cleaned dataset:", len(cleaned), "rows")
    print("Outliers removed:", len(outliers))

    print("\nBounds used:")
    for k, v in bounds.items():
        print(k, v)

    # visualize after
    plot_distributions(cleaned, "After Outlier Removal non-AI")

    # save resul{language}
    cleaned.to_csv(f"csv/{language}/{repo}/cleaned_dataset_nonAI.csv", index=False)
    outliers.to_csv(f"csv/{language}/{repo}/removed_outliers_nonAI.csv", index=False)

    print("\nSaved:")
    print(f"csv/{language}/{repo}/cleaned_dataset_nonAI.csv")
    print(f"csv/{language}/{repo}/removed_outliers_nonAI.csv")


if __name__ == "__main__":
    main()
