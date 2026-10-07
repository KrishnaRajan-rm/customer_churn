from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import MetaData, Table, create_engine, func,text
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware

from database.database_model import Contract, Customer, FactCustomerAccount


DATABASE_URL = "mysql+pymysql://root:root@localhost/churn_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData()
services = Table("services", metadata, autoload_with=engine)

app = FastAPI(title="Telco Churn API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomerFeatureResponse(BaseModel):
    customer_id: str
    service_count: int
    tenure_bucket: str
    high_charge_flag: bool
    is_long_term_customer: bool
    has_streaming_bundle: bool
    auto_pay_flag: bool
    monthly_charges: float
    total_charges: float

class HighRiskResponseModel(BaseModel):
    customer_id: str
    tenure: int
    monthly_charges: float
    contract_type: str
    risk_reason: str

class CustomerResponse(BaseModel):
    customer_id: str
    tenure: int
    contract_type: str
    internet_service: str
    monthly_charges: float
    churn: str


class PredictChurnRequest(BaseModel):
    tenure: int = Field(..., ge=0)
    monthly_charges: float = Field(..., ge=0)
    contract_type: str
    service_count: int = Field(..., ge=0, le=6)


class PredictChurnResponse(BaseModel):
    risk_score: float
    prediction: str
    confidence_level: str


class ContractChurnRate(BaseModel):
    contract_type: str = Field(..., example="Month-to-month")
    churn_rate: float = Field(..., example=0.4271)


class InternetServiceChurnRate(BaseModel):
    internet_service: str = Field(..., example="Fiber optic")
    churn_rate: float = Field(..., example=0.4189)


class ChurnSummaryResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_customers": 7043,
                "total_churned": 1869,
                "churn_rate": 0.2654,
                "by_contract_type": [
                    {"contract_type": "Month-to-month", "churn_rate": 0.4271},
                    {"contract_type": "One year", "churn_rate": 0.1127},
                    {"contract_type": "Two year", "churn_rate": 0.0283},
                ],
                "by_internet_service_type": [
                    {"internet_service": "Fiber optic", "churn_rate": 0.4189},
                    {"internet_service": "DSL", "churn_rate": 0.1896},
                    {"internet_service": "No", "churn_rate": 0.074},
                ],
            }
        }
    )

    total_customers: int = Field(..., example=7043)
    total_churned: int = Field(..., example=1869)
    churn_rate: float = Field(..., example=0.2654)
    by_contract_type: list[ContractChurnRate]
    by_internet_service_type: list[InternetServiceChurnRate]


def get_churn_summary(db):
    db = SessionLocal()

    """Service layer function to get churn summary statistics."""
    totals = (
        db.query(
            func.count(FactCustomerAccount.customerID).label("total_customers"),
            func.sum(FactCustomerAccount.churn).label("total_churned"),
        ).first()
    )

    total_customers = totals.total_customers or 0
    total_churned = totals.total_churned or 0
    churn_rate = (total_churned / total_customers) if total_customers > 0 else 0.0

    contract_breakdown = (
        db.query(
            Contract.contract_type,
            func.avg(FactCustomerAccount.churn).label("churn_rate"),
        )
        .join(
            FactCustomerAccount,
            FactCustomerAccount.contract_id == Contract.contract_id,
        )
        .group_by(Contract.contract_type)
        .order_by(func.avg(FactCustomerAccount.churn).desc())
        .all()
    )

    by_contract_type = [
        {
            "contract_type": row.contract_type,
            "churn_rate": round(float(row.churn_rate or 0.0), 4),
        }
        for row in contract_breakdown
    ]

    internet_service_breakdown = (
        db.query(
            services.c.InternetService.label("internet_service"),
            func.avg(FactCustomerAccount.churn).label("churn_rate"),
        )
        .join(
            FactCustomerAccount,
            services.c.customerID == FactCustomerAccount.customerID,
        )
        .group_by(services.c.InternetService)
        .order_by(func.avg(FactCustomerAccount.churn).desc())
        .all()
    )

    by_internet_service_type = [
        {
            "internet_service": row.internet_service,
            "churn_rate": round(float(row.churn_rate or 0.0), 4),
        }
        for row in internet_service_breakdown
    ]

    return ChurnSummaryResponse(
        total_customers=total_customers,
        total_churned=total_churned,
        churn_rate=round(churn_rate, 4),
        by_contract_type=by_contract_type,
        by_internet_service_type=by_internet_service_type,
    )


def engineered_ml_features(session, customer_id: str):

    query = text(
        """select customerID, service_count, tenure_bucket,
                high_charge_flag, is_long_term_customer, has_streaming_bundle,
                auto_pay_flag, monthly_charges, total_charges
                from customer_ml_features where customerID=:customer_id"""
    )

    row = session.execute(query, {"customer_id": customer_id}).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Customer features for {customer_id} not found")

    return CustomerFeatureResponse(
        customer_id=row.customerID,
        service_count=row.service_count,
        tenure_bucket=row.tenure_bucket,
        high_charge_flag=row.high_charge_flag,
        is_long_term_customer=row.is_long_term_customer,
        has_streaming_bundle=row.has_streaming_bundle,
        auto_pay_flag=row.auto_pay_flag,
        monthly_charges=row.monthly_charges,
        total_charges=row.total_charges,
    )




@app.get("/customer/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str):
    db = SessionLocal()

    try:
        result = (
            db.query(
                FactCustomerAccount.customerID.label("customer_id"),
                FactCustomerAccount.tenure.label("tenure"),
                Contract.contract_type.label("contract_type"),
                services.c.InternetService.label("internet_service"),
                FactCustomerAccount.monthly_charges.label("monthly_charges"),
                FactCustomerAccount.churn.label("churn"),
            )
            .join(Customer, Customer.customerID == FactCustomerAccount.customerID)
            .join(Contract, FactCustomerAccount.contract_id == Contract.contract_id)
            .join(services, services.c.customerID == FactCustomerAccount.customerID)
            .filter(Customer.customerID == customer_id)
            .first()
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Customer {customer_id} not found",
            )

        return CustomerResponse(
            customer_id=result.customer_id,
            tenure=int(result.tenure),
            contract_type=result.contract_type,
            internet_service=result.internet_service or "Unknown",
            monthly_charges=float(result.monthly_charges),
            churn="Yes" if int(result.churn) == 1 else "No",
        )
    finally:
        db.close()


@app.get("/churn/summary", response_model=ChurnSummaryResponse)
def churn_summary():
    """Get overall churn summary statistics."""
    db = SessionLocal()
    try:
        return get_churn_summary(db)
    finally:
        db.close()

@app.get("/customers/high-risk", response_model=list[HighRiskResponseModel])
def get_high_risk_customers(
    limit: int = 50,
    min_tenure: int  | None=None,
    max_tenure: int  | None=None,
    ):

    try:
        session=SessionLocal()
    
        query=text("""
            select * from high_risk_customers where(:max_tenure is null
            or tenure <= :max_tenure) and (:min_tenure is null or tenure >= :min_tenure)
            limit :limit
            """)

        parameters = {
            "min_tenure": min_tenure,
            "max_tenure": max_tenure,
            "limit": limit
        }
        result=session.execute(query,parameters).fetchall()

        return [
            HighRiskResponseModel(
                customer_id=row.customerID,
                tenure=row.tenure,
                monthly_charges=row.monthly_charges,
                contract_type=row.contract_type,
                risk_reason=row.risk_reason
            )
            for row in result
        ]

    finally:
        session.close()


@app.post("/predict-churn", response_model=PredictChurnResponse)
def predict_churn(payload: PredictChurnRequest):
    # Temporary scoring logic for frontend integration until ML model is connected.
    risk_score = 0.1

    if payload.contract_type == "Month-to-month":
        risk_score += 0.25
    elif payload.contract_type == "One year":
        risk_score += 0.1
    else:
        risk_score += 0.02

    if payload.tenure < 12:
        risk_score += 0.25
    elif payload.tenure < 24:
        risk_score += 0.1

    if payload.monthly_charges > 80:
        risk_score += 0.2
    elif payload.monthly_charges > 60:
        risk_score += 0.1

    if payload.service_count >= 5:
        risk_score += 0.15
    elif payload.service_count <= 1:
        risk_score += 0.05

    risk_score = max(0.0, min(risk_score, 0.99))

    if risk_score > 0.6:
        prediction = "Likely to churn"
        confidence = "High"
    elif risk_score >= 0.3:
        prediction = "At risk"
        confidence = "Medium"
    else:
        prediction = "Likely to stay"
        confidence = "Low"

    return PredictChurnResponse(
        risk_score=round(risk_score, 4),
        prediction=prediction,
        confidence_level=confidence,
    )

@app.get("/customer/{customer_id}/features")
def engineered_features(customer_id:str):
    try:
        session=SessionLocal()
        return engineered_ml_features(session,customer_id)
    finally:
        session.close()




if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)