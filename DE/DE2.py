import pandas as pd
import os
import shutil
import csv
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
 
DATABASE_URL = "mysql+pymysql://root:root@localhost/ml_churn"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind = engine)
session = Session()
 
def create_log_ingestion_table():
    query = text("""
        create table if not exists log_ingestion(
          id int auto_increment primary key,
          filename varchar(100),
          status varchar(20),
          total_rows int,
          reason varchar(200)
 
        );
    """)
 
    session.execute(query)
    session.commit()
 
EXPECTED_COLS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]
 
def detect_files():
 
    files=[]
 
 
    for file in os.listdir("./landing"):
        if file.endswith(".csv"):
            filepath = os.path.join("./landing/",file)
            files.append(filepath)
 
    return files
 
def validate_schema(filepath):
 
    with open(
        filepath,
        "r",
        newline = "",
        encoding = "utf-8-sig"
        ) as f:
        header = next(csv.reader(f))
 
        return header == EXPECTED_COLS , header
 
def load_to_staging(filepath,engine):
 
    df = pd.read_csv(filepath)
 
    df.to_sql(
        "stg_customer_raw",
        engine,
        if_exists = "replace",
        index = False
 
    )
 
    return len(df)
 
def log_ingestion(filename,status,rows,reason):
    query = text("""
           insert into log_ingestion
           (filename,status,total_rows,reason)
           values(
            :filename,
            :status,
            :rows,
            :reason
           )
    """)
 
    session.execute(query,{
        "filename" : filename,
        "status" : status,
        "rows" : rows,
        "reason" : reason
    })
 
    session.commit()
 
 
def process_landing():
 
    filepaths = detect_files()
 
    for filepath in filepaths:
 
        filename = os.path.basename(filepath)
 
        try :
            valid,_ = validate_schema(filepath)
 
 
        except Exception as e:
            log_ingestion(filename,"Rejected",0,f"Error in opening the file : {e}")
            continue
 
 
        if not valid :
            log_ingestion(filename,"Rejected",0,"Column condition not satisfied")
 
            rejected_path = os.path.join("./rejected/",filename)
            shutil.move(filepath,rejected_path)
            continue
 
        try:
            rows = load_to_staging(filepath,engine)
 
            log_ingestion(filename,"Success",rows,"Succesfully staged the data into the table")
            raw_path = os.path.join("./raw/",filename)
            shutil.move(filepath,raw_path)
 
        except Exception as e:
            log_ingestion(filename,"Rejected",0,f"Error in staging the data : {e}")
 
 
if __name__ == "__main__":
    create_log_ingestion_table()
    process_landing()    