import pandas as pd

dataset=pd.read_csv("customer_ml_features.csv")

y=dataset["churn"]

x=dataset.drop(columns=["customer_id","churn"])


x=pd.get_dummies(x,columns=["contract","internet_service"],drop_first=False)

print(x.columns)
print(y.value_counts())
print(x.head())
