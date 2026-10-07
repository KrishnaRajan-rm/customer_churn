import os
from datetime import datetime

import pandas as pd

from customer_cleaner import CustomerCleaner

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()

    feature_df["tenure_bucket"] = pd.cut(
        feature_df["tenure"],
        bins=[0, 12, 24, 48, 72, 1000],
        labels=["0-12", "13-24", "25-48", "49-72", "73+"],
        include_lowest=True,
    )

    feature_df["high_charge_flag"] = (
        feature_df["monthly_charges"] > feature_df["monthly_charges"].median()
    ).astype(int)

    service_cols = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
    ]

    feature_df["service_count"] = feature_df[service_cols].apply(
        lambda row: row.map({"Yes": 1, "No": 0, "No internet service": 0}).fillna(0).sum(),
        axis=1,
    )

    feature_df["is_long_term_customer"] = (feature_df["tenure"] >= 24).astype(int)

    feature_df["has_streaming_bundle"] = (
        (feature_df["streaming_tv"].str.contains("Yes", case=False, na=False)) &
        (feature_df["streaming_movies"].str.contains("Yes", case=False, na=False))
    ).astype(int)

    feature_df["auto_pay_flag"] = (
        feature_df["payment_method"].str.contains("automatic", case=False, na=False)
    ).astype(int)

    return feature_df


def save_outputs(clean_df: pd.DataFrame, feature_df: pd.DataFrame):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    cleaned_path = f"cleaned_customer_{timestamp}.csv"
    features_path = f"customer_features_{timestamp}.csv"

    clean_df.to_csv(cleaned_path, index=False)
    feature_df.to_csv(features_path, index=False)

    print(f"Cleaned data saved to: {cleaned_path}")
    print(f"Feature data saved to: {features_path}")


def main():
    print("========================================")
    print("CP5 - Build End-to-End Preprocessing Pipeline")
    print("========================================")

    raw_df = load_data(DATASET_PATH)
    cleaned_df = CustomerCleaner(raw_df).clean().get_dataframe()

    assert cleaned_df["total_charges"].notna().all(), "Total charges still contain null values"
    assert cleaned_df["monthly_charges"].notna().all(), "Monthly charges column has null values"

    feature_df = engineer_features(cleaned_df)
    save_outputs(cleaned_df, feature_df)

    print("\nPipeline completed successfully.")
    print(f"Clean shape: {cleaned_df.shape}")
    print(f"Feature shape: {feature_df.shape}")


if __name__ == "__main__":
    main()
