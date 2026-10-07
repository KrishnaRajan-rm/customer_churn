Index(['customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents',
       'tenure', 'PhoneService', 'MultipleLines', 'InternetService',
       'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport',
       'StreamingTV', 'StreamingMovies', 'Contract', 'PaperlessBilling',
       'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn'],
      dtype='str')

customers (identity):
    customerID
    gender
    SeniorCitizen
    Partner	
    Dependents	

contracts (subscription terms):
    tenure	
    PhoneService	
    MultipleLines

services (what they subscribe to):
    InternetService
    OnlineSecurity
    OnlineBackup
    DeviceProtection
    TechSupport
    StreamingTV
    StreamingMovies

billing (charges):
    Contract
    PaperlessBilling
    PaymentMethod
    MonthlyCharges
    TotalCharges

customer_status (churn):
    Churn
