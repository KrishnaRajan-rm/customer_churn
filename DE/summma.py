import pandas as pd

# dataset=pd.read_csv("customer_features_20260814_151822.csv")
# print(dataset.columns)

# datasets=dataset.drop(columns=['gender', 'senior_citizen', 'partner', 'dependents',
#          'phone_service', 'multiple_lines',
#        'online_security', 'online_backup', 'device_protection', 'tech_support',
#        'streaming_tv', 'streaming_movies', 'paperless_billing','payment_method'])
# datasets.to_csv("customer_ml_features.csv",index=False)


dataset=pd.read_csv("customer_ml_features.csv")
print(dataset.columns)
