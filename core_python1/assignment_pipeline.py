import pandas as pd

from customer_cleaner import CustomerCleaner

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def cp1_profile(df: pd.DataFrame):
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

    nulls = df.isnull().sum().to_frame(name="null_count")
    nulls["null_percentage"] = (nulls["null_count"] / len(df) * 100).round(2)
    nulls = nulls[nulls["null_count"] > 0].sort_values("null_count", ascending=False)
    print("\nNull values summary:")
    if nulls.empty:
        print("No null values found.")
    else:
        print(nulls)

    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
    print("\nCategorical columns:")
    for col in cat_cols:
        print(f"\n{col}:\n{df[col].value_counts(dropna=False).head(10)}")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    print("\nNumeric columns summary:")
    for col in numeric_cols:
        print(f"\n{col}:\n{df[col].describe()}")


def cp2_clean(df: pd.DataFrame):
    print("\n========================================")
    print("CP2 - Build a Reusable Cleaning Utility")
    print("========================================")
    print("\nBefore cleaning:")
    print(f"Shape: {df.shape}")
    print(df.dtypes)

    cleaned = CustomerCleaner(df).clean().get_dataframe()
    print("\nAfter cleaning:")
    print(f"Shape: {cleaned.shape}")
    print(cleaned.dtypes)
    print("\nSample rows:")
    print(cleaned.head(5).to_string(index=False))
    print("\nMissing TotalCharges after cleaning:", cleaned["total_charges"].isna().sum())
    return cleaned


def cp3_insights(df: pd.DataFrame):
    print("\n========================================")
    print("CP3 - Generate Business Insights")
    print("========================================")
    churn_rate = df["churn"].mean() * 100
    print(f"Overall churn rate: {churn_rate:.2f}%")

    print("\nChurn rate by contract type:")
    contract_summary = df.groupby("contract")["churn"].mean().sort_values(ascending=False) * 100
    print(contract_summary.round(2).to_string())

    print("\nChurn rate by internet service type:")
    internet_summary = df.groupby("internet_service")["churn"].mean().sort_values(ascending=False) * 100
    print(internet_summary.round(2).to_string())

    print("\nChurn rate by payment method:")
    payment_summary = df.groupby("payment_method")["churn"].mean().sort_values(ascending=False) * 100
    print(payment_summary.round(2).to_string())

    df = df.copy()
    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 36, 48, 60, 100],
        labels=["0-12", "13-24", "25-36", "37-48", "49-60", "60+"],
        include_lowest=True,
    )
    print("\nChurn rate by tenure bucket:")
    tenure_summary = df.groupby("tenure_bucket")["churn"].mean().sort_values(ascending=False) * 100
    print(tenure_summary.round(2).to_string())

    print("\nRisk segmentation by contract and internet service:")
    grouped = df.groupby(["contract", "internet_service"])["churn"].mean().reset_index()
    grouped["churn_pct"] = grouped["churn"] * 100
    print(grouped.sort_values("churn_pct", ascending=False).round(2).to_string(index=False))


def cp4_features(df: pd.DataFrame):
    print("\n========================================")
    print("CP4 - Build Engineered Features")
    print("========================================")
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
        (feature_df["streaming_tv"].str.contains("Yes", case=False, na=False))
        & (feature_df["streaming_movies"].str.contains("Yes", case=False, na=False))
    ).astype(int)

    feature_df["auto_pay_flag"] = (
        feature_df["payment_method"].str.contains("automatic", case=False, na=False)
    ).astype(int)

    print(f"Saved features to: customer_features.csv")
    feature_df.to_csv("customer_features.csv", index=False)

    corr = feature_df[["churn", "high_charge_flag", "service_count",
                       "is_long_term_customer", "has_streaming_bundle", "auto_pay_flag"]].corr()
    print("\nCorrelation table:")
    print(corr[["churn"]].sort_values("churn", ascending=False).round(3))
    return feature_df


def cp5_pipeline(df: pd.DataFrame):
    print("\n========================================")
    print("CP5 - Build End-to-End Preprocessing Pipeline")
    print("========================================")
    cleaned = CustomerCleaner(df).clean().get_dataframe()

    feature_df = cp4_features(cleaned)
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    cleaned_path = f"cleaned_customer_{timestamp}.csv"
    feature_path = f"customer_features_{timestamp}.csv"

    cleaned.to_csv(cleaned_path, index=False)
    feature_df.to_csv(feature_path, index=False)

    print(f"\nCleaned data saved to: {cleaned_path}")
    print(f"Feature data saved to: {feature_path}")
    print(f"\nClean shape: {cleaned.shape}")
    print(f"Feature shape: {feature_df.shape}")


def main():
    raw_df = pd.read_csv(DATASET_PATH)
    cp1_profile(raw_df)
    cleaned_df = cp2_clean(raw_df)
    cp3_insights(cleaned_df)
    cp4_features(cleaned_df)
    cp5_pipeline(raw_df)


if __name__ == "__main__":
    main()
