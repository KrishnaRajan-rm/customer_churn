CREATE DATABASE churn_db;

USE churn_db;

CREATE TABLE customers (
    customerID VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    SeniorCitizen INTEGER,
    Partner VARCHAR(5),
    Dependents VARCHAR(5)
);
CREATE TABLE contracts (
    customerID VARCHAR(20) PRIMARY KEY,
    tenure INTEGER,
    Contract VARCHAR(30),
    FOREIGN KEY (customerID) REFERENCES customers(customerID)
);
CREATE TABLE services (
    customerID VARCHAR(20) PRIMARY KEY,
    PhoneService VARCHAR(5),
    MultipleLines VARCHAR(30),
    InternetService VARCHAR(30),
    OnlineSecurity VARCHAR(5),
    OnlineBackup VARCHAR(5),
    DeviceProtection VARCHAR(5),
    TechSupport VARCHAR(5),
    StreamingTV VARCHAR(5),
    StreamingMovies VARCHAR(5),
    FOREIGN KEY (customerID) REFERENCES customers(customerID)
);
CREATE TABLE billing (
    customerID VARCHAR(20) PRIMARY KEY,
    PaperlessBilling VARCHAR(5),
    PaymentMethod VARCHAR(50),
    MonthlyCharges DECIMAL(10,2),
    TotalCharges DECIMAL(10,2),
    FOREIGN KEY (customerID) REFERENCES customers(customerID)
);
CREATE TABLE customer_status (
    customerID VARCHAR(20) PRIMARY KEY,
    Churn VARCHAR(5),
    FOREIGN KEY (customerID) REFERENCES customers(customerID)
);