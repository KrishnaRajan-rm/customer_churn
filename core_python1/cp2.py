import pandas as pd

from customer_cleaner import CustomerCleaner

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def main():
    print("========================================")
    print("CP2 - Build a Reusable Cleaning Utility")
    print("========================================")

    df = pd.read_csv(DATASET_PATH)
    print("\nBefore cleaning:")
    print(f"Shape: {df.shape}")
    print(df.dtypes)

    cleaner = CustomerCleaner(df)
    cleaned_df = cleaner.clean().get_dataframe()

    print("\nAfter cleaning:")
    print(f"Shape: {cleaned_df.shape}")
    print(cleaned_df.dtypes)
    print("\nSample rows:")
    print(cleaned_df.head(5).to_string(index=False))

    print("\nMissing TotalCharges after cleaning:", cleaned_df["total_charges"].isna().sum())


if __name__ == "__main__":
    main()
