import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core_python1.customer_cleaner import CustomerCleaner
import pandas as pd
from sqlalchemy import create_engine, text
 
 
DATABASE_URL = "mysql+pymysql://root:root@localhost/ml_churn"
engine = create_engine(DATABASE_URL)


# def ensure_database_exists():
#     admin_engine = create_engine("mysql+pymysql://root:root@localhost")
#     with admin_engine.begin() as conn:
#         conn.execute(text("CREATE DATABASE IF NOT EXISTS ml_churn"))


# ensure_database_exists()



def clean_staging(engine):

    raw_df = pd.read_sql("select * from stg_customer_raw", engine)

    cleaner = CustomerCleaner(raw_df)
    cleaner.clean()
    cleaned_df = cleaner.get_dataframe()

    try:
        assert len(raw_df) == len(cleaned_df), (
            "Raw df row count doesn't match with cleaned_df rows count"
        )
 
        print("Raw df row count does match with cleaned_df rows count : PASS")
 
        assert cleaned_df["customer_id"].isna().sum() == 0,(
            "Customer ID has null values"
        )
 
        print("Customer ID has no null values : PASS")
 
        assert cleaned_df["monthly_charges"].isna().sum() == 0,(
            "Monthly charges has null values"
        )
 
        print("Monthly charges has no null values : PASS")
 
        assert cleaned_df["churn"].isin([0,1]).all(),(
            "Churn values is invalid"
        )
 
        print("Churn values is valid : PASS")
 
    except AssertionError as e:
        print(e)
        raise
 
    cleaned_df.to_sql(
        "cleaned_customers",
        engine,
        if_exists = "replace",
        index = False,
    )
 
def build_curated_tables(engine):
 
    df = pd.read_sql("select * from cleaned_customers",engine)
 
    contract_df = df[["contract"]]
    contract_df = df[["contract"]].drop_duplicates().dropna().reset_index(drop = True)
    contract_df["contract_id"] = (
        contract_df.index+1
    )
    contract_df = contract_df.rename(
        columns={
            "contract" : "contract_name"
        }
    )
 
    contract_df = contract_df[[
        "contract_id","contract_name"
    ]]
 
    contract_df.to_sql(
        "dim_contract",
        engine,
        if_exists = "replace",
        index = False
    )
 
    payment_df = df[["payment_method"]]
    payment_df = df[["payment_method"]].drop_duplicates().dropna().reset_index(drop = True)
    payment_df["payment_id"] = (
        payment_df.index+1
    )
 
    payment_df = payment_df[[
        "payment_id","payment_method"
    ]]
 
    payment_df.to_sql(
        "dim_payment",
        engine,
        if_exists = "replace",
        index = False
    )
 
    customer_columns = [
        "customer_id",
        "gender",
        "senior_citizen",
        "partner",
        "dependents",
        "phone_service",
        "multiple_lines",
        "internet_service",
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies",
        "paperless_billing"
    ]
 
    customer_df = (
        df[customer_columns].drop_duplicates(
            subset = ["customer_id"]
        )
    )
 
    customer_df.to_sql(
        "customers",
        engine,
        if_exists = "replace",
        index = False
    )
 
    fact_df = df[
        [
            "customer_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn",
            "contract",
            "payment_method"
        ]
    ].copy()
 
    contract_mapping = dict(
        zip(contract_df["contract_name"],contract_df["contract_id"])
    )
 
    fact_df["contract_id"] = fact_df["contract"].map(contract_mapping)
 
    payment_mapping = dict(
            zip(payment_df["payment_method"],payment_df["payment_id"])
        )
   
    fact_df["payment_id"] = fact_df["payment_method"].map(payment_mapping)
 
    fact_df = fact_df.drop(
        columns = [
            "contract","payment_method"
        ]
    )
 
    fact_df = fact_df[
        [
            "customer_id",
            "tenure",
            "monthly_charges",
            "total_charges",
            "churn",
            "contract_id",
            "payment_id"
        ]
    ]
 
    fact_df.to_sql(
        "fact_customer_account",
        engine,
        if_exists = "replace",
        index = False
    )
 
 
if __name__ == "__main__":
 
    # try :
    clean_staging(engine)
    build_curated_tables(engine)