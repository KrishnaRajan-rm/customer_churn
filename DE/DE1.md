# Customer Data Pipeline Architecture
 
## 1. Pipeline Architecture
 
```text
CRM Extract
     ↓
Raw File
     ↓
[Quality Gate 1: Schema Validation]
     ↓
Staging Table
     ↓
Cleaned Table
     ↓
[Quality Gate 2: Data Quality Check]
     ↓
Feature Table
     ↓
ML Scoring
     ↓
Dashboard / API
````
 
## 2. Layer and Tool Mapping
 
| Layer         | Data Format       | Main Tool             | Read By             |
| ------------- | ----------------- | --------------------- | ------------------- |
| CRM Extract   | CRM records / CSV | CRM system            | Ingestion           |
| Raw File      | CSV               | Python / File System  | Schema Validation   |
| Staging Table | SQL Table         | SQLAlchemy / Database | Cleaning            |
| Cleaned Table | SQL Table         | SQL / SQLAlchemy      | Feature Engineering |
| Feature Table | SQL Table         | Python / SQL          | ML Scoring          |
| ML Scoring    | JSON / SQL        | Python / ML Model     | FastAPI             |
| Dashboard/API | JSON / HTML       | FastAPI + React       | Retention Team      |
 
## 3. Quality Gates
 
### Quality Gate 1 — Schema Validation
 
This occurs before the raw data is loaded into the staging table.
 
The pipeline checks:
 
* Required columns exist.
* Column names are valid.
* Data types are compatible.
* Required identifiers such as `customer_id` are present.
* Unexpected or missing columns are detected.
* File structure is valid.
 
If validation fails:
 
```text
Raw File
   ↓
Schema Validation
   ↓
FAIL
   ↓
Stop Pipeline
   ↓
Log Error / Reject File
```
 
Bad data must not be loaded into the staging table.
 
### Quality Gate 2 — Data Quality Check
 
This occurs after cleaning and before feature engineering.
 
The pipeline checks:
 
* Required fields are not unexpectedly null.
* Duplicate customers are handled.
* Numeric values are valid.
* Values are within acceptable ranges.
* Customer identifiers are valid.
* Cleaning has produced the expected result.
 
If the check fails, the pipeline stops before creating the feature table and records the failure for investigation.
 
## 4. Incremental Processing Strategy
 
The pipeline should use an **upsert strategy** for daily CRM extracts.
 
The `customer_id` acts as the business key.
 
If a customer appears in two consecutive daily extracts:
 
```text
Day 1:
customer_id = 1001
monthly_charges = 70
 
Day 2:
customer_id = 1001
monthly_charges = 75
```
 
The Day 2 record should update the existing customer record rather than create a duplicate.
 
Conceptually:
 
```text
customer_id exists?
       │
   ┌───┴───┐
  YES      NO
   │        │
 UPDATE    INSERT
```
 
This makes the process **idempotent**: processing the same daily extract again should not create additional duplicate records.
 
Useful tracking fields include:
 
```text
customer_id
updated_at
source_date
```
 
These fields can help identify the latest version of a customer's data.
 
## 5. Layer-to-Lab Mapping
 
| Pipeline Layer           | Relevant Lab        | Purpose                                  |
| ------------------------ | ------------------- | ---------------------------------------- |
| CRM Extract              | CP5                 | Defines the source/customer data flow    |
| Raw File                 | CP5                 | Initial file-based customer data         |
| Staging Table            | CP5 / DE2           | Introduces structured database staging   |
| Ingestion                | DE2                 | Formalises loading raw data into staging |
| Cleaning                 | DE3                 | Standardises and cleans customer data    |
| Feature Engineering      | DE4                 | Creates ML-ready customer features       |
| ML Scoring               | ML4 / ML5           | Generates churn/risk predictions         |
| Dashboard/API            | API Labs / Frontend | Serves results to users                  |
| End-to-End Orchestration | DE7                 | Connects all stages using Airflow        |
 
## 6. Batch vs Incremental Processing
 
A full batch process reloads all customer records every time:
 
```text
Daily Extract
     ↓
Reload Everything
```
 
The preferred strategy for daily CRM extracts is **incremental processing**:
 
```text
Daily Extract
     ↓
Identify New/Changed Customers
     ↓
INSERT New Customers
     ↓
UPDATE Existing Customers
     ↓
Leave Unchanged Customers Unchanged
```
 
This reduces unnecessary processing and prevents duplicate customer records.
 
## 7. Source of Truth
 
Each layer has a defined input and output:
 
```text
CRM
 ↓
Raw File
 ↓
Staging Table
 ↓
Cleaned Table
 ↓
Feature Table
 ↓
ML Scores
 ↓
API / Dashboard
```
 
Each layer should consume the output of its upstream layer and provide a clearly defined format for the next layer.
 
The overall architecture separates:
 
* Ingestion
* Staging
* Cleaning
* Feature Engineering
* ML Scoring
* Serving
 
This makes the pipeline easier to validate, maintain, monitor, and orchestrate.