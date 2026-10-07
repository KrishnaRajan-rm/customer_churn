import pandas as pd

from customer_cleaner import CustomerCleaner

DATASET_PATH = "WA_Fn-UseC_-Telco-Customer-Churn.csv"


def build_churn_summary(df: pd.DataFrame):
    churn_rate = df["churn"].mean() * 100
    print("========================================")
    print("CP3 - Generate Business Insights")
    print("========================================")
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

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 36, 48, 60, 100],
        labels=["0-12", "13-24", "25-36", "37-48", "49-60", "60+"],
        include_lowest=True
    )

    print("\nChurn rate by tenure bucket:")
    tenure_summary = df.groupby("tenure_bucket")["churn"].mean().sort_values(ascending=False) * 100
    print(tenure_summary.round(2).to_string())

    print("\nRisk segmentation by contract and internet service:")
    grouped = df.groupby(["contract", "internet_service"])["churn"].mean().reset_index()
    grouped["churn_pct"] = grouped["churn"] * 100
    print(grouped.sort_values("churn_pct", ascending=False).round(2).to_string(index=False))


def main():
    df = pd.read_csv(DATASET_PATH)
    cleaned_df = CustomerCleaner(df).clean().get_dataframe()
    build_churn_summary(cleaned_df)


if __name__ == "__main__":
    main()
