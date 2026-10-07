from sqlalchemy import create_engine,text
import pandas as pd
 
DATABASE_URL = "mysql+pymysql://root:root@localhost/ml_churn"
engine = create_engine(DATABASE_URL)
 
def build_features(engine):
 
    cleaned_df = pd.read_sql("select * from cleaned_customers",engine)
    
 
    df = cleaned_df.copy()
 
    #Feature 1
    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0,12,24,48,72],
        labels = ["0-12","13-24","25-48","49-72"],
        include_lowest = True
    )
 
    median = df["monthly_charges"].median()
 
    # Feature 2
 
    df["high_charge_flag"] = (
        df["monthly_charges"] > median
    ).astype(int)
 
    # Feature 3
 
    service_columns = [
        "online_security",
        "online_backup",
        "device_protection",
        "tech_support",
        "streaming_tv",
        "streaming_movies"
    ]
 
 
    df["service_count"] = df[service_columns].sum(axis=1).astype(int)
    # Feature 4
 
    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)
 
    # Feature 5
 
    df["has_streaming_bundle"] = (
        (df["streaming_tv"]==1) & (df["streaming_movies"] == 1)
    ).astype(int)
 
    # Feature 6
 
    df["auto_pay_flag"] = (
        df["payment_method"].str.contains("automatic",case = False)
    ).astype(int)
 
 
    df.to_sql(
        "customer_ml_features",
        engine,
        if_exists = "replace",
        index = False
    )
 
    try:
        assert len(df) == len(cleaned_df),(
            "Rows count does not match"
        )
 
    except AssertionError as e:
        print(e)
        raise
 
    df.to_sql(
        "customer_ml_feature",
        engine,
        if_exists = "replace",
        index = False
    )
 
    with engine.connect() as connection:
 
        db_df = pd.read_sql(
                    text("""
                SELECT
                customer_id,
                service_count,
                tenure_bucket,
                high_charge_flag,
                is_long_term_customer,
                has_streaming_bundle,
                auto_pay_flag
            FROM customer_ml_features
            limit 10
        """),connection
        )
 
    print(db_df)
 
 
 
 
 
if __name__ == "__main__":
 
    try:
        build_features(engine)
 
    except Exception:
        print("Failed in Customer_ML_FEATURES")