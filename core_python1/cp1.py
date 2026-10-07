import pandas as pd

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def profile_dataframe(df: pd.DataFrame):
    print("========================================")
    print("CP1 - Profile the Customer Churn Dataset")
    print("========================================")
    print(f"Shape: {df.shape}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print("\nColumn names:")
    print(list(df.columns))

    print("\nData types:")
    print(df.dtypes)

    null_summary = df.isnull().sum().to_frame(name="null_count")
    null_summary["null_percentage"] = (
        null_summary["null_count"] / len(df) * 100
    ).round(2)
    null_summary = null_summary[null_summary["null_count"] > 0].sort_values(
        by="null_count", ascending=False
    )

    print("\nNull values summary:")
    if null_summary.empty:
        print("No null values found.")
    else:
        print(null_summary)

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    print("\nCategorical columns:")
    if not categorical_cols:
        print("No categorical columns found.")
    else:
        for col in categorical_cols:
            print(f"\n{col}:")
            print(df[col].value_counts(dropna=False).head(10))

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    print("\nNumeric columns:")
    if not numeric_cols:
        print("No numeric columns found.")
    else:
        for col in numeric_cols:
            print(f"\n{col} summary:")
            print(df[col].describe())


if __name__ == "__main__":
    df = load_data(DATASET_PATH)
    profile_dataframe(df)
