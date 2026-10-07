import pandas as pd

from customer_cleaner import CustomerCleaner

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUTPUT_PATH = "customer_features.csv"


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


def main():
    print("========================================")
    print("CP4 - Build Engineered Features")
    print("========================================")

    df = pd.read_csv(DATASET_PATH)
    df = CustomerCleaner(df).clean().get_dataframe()

    features = engineer_features(df)
    features.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved features to: {OUTPUT_PATH}")
    print("\nFeature summary:")
    print(features[["churn", "high_charge_flag", "service_count", "is_long_term_customer",
                   "has_streaming_bundle", "auto_pay_flag"]].head().to_string(index=False))

    corr = features[["churn", "high_charge_flag", "service_count", "is_long_term_customer",
                     "has_streaming_bundle", "auto_pay_flag"]].corr()
    print("\nCorrelation table:")
    print(corr[["churn"]].sort_values("churn", ascending=False).round(3))


if __name__ == "__main__":
    main()
