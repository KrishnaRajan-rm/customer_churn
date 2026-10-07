from sqlalchemy import create_engine, Column, String, Numeric, Integer, func
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Payment(Base):
    __tablename__ = "dim_payment"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_method = Column(String(50), unique=True)


class FactCustomerAccount(Base):
    __tablename__ = "fact_customer_account"

    customerID = Column(String(20), primary_key=True)
    contract_id = Column(Integer)
    payment_id = Column(Integer)
    tenure = Column(Integer)
    monthly_charges = Column(Numeric(10, 2))
    total_charges = Column(Numeric(10, 2))
    churn = Column(Integer)


class Customer(Base):
    __tablename__ = "customers"

    customerID = Column(String(20), primary_key=True)
    gender = Column(String(10))
    SeniorCitizen = Column(Integer)
    Partner = Column(Integer)
    Dependents = Column(Integer)


class Contract(Base):
    __tablename__ = "dim_contract"

    contract_id = Column(Integer, primary_key=True, autoincrement=True)
    contract_type = Column(String(30), unique=True)


engine = create_engine("mysql+pymysql://root:root@localhost/churn_db")


if __name__ == "__main__":
    with engine.connect() as connection:
        print("Connected to MySQL successfully!")

    Sessions = sessionmaker(bind=engine)
    session = Sessions()

    customer = session.query(Customer).filter_by(
        customerID="0003-MKNFE"
    ).first()

    print(customer.customerID, customer.gender, customer.SeniorCitizen)

    ######################################################################################

    result = (
        session.query(
            Contract.contract_type,
            func.avg(FactCustomerAccount.churn).label("churn_rate")
        )
        .join(
            FactCustomerAccount,
            FactCustomerAccount.contract_id == Contract.contract_id
        )
        .group_by(Contract.contract_type)
        .order_by(func.avg(FactCustomerAccount.churn).desc())
        .all()
    )

    for contract_type, churn_rate in result:
        print(contract_type, churn_rate)

    ########################################################################################
    print("="*69)
    #######################################################################################

    result = (
        session.query(
            Payment.payment_method,
            func.avg(FactCustomerAccount.churn).label("churn_rate")
        )
        .join(
            FactCustomerAccount,
            FactCustomerAccount.payment_id == Payment.payment_id
        )
        .group_by(Payment.payment_method)
        .order_by(func.avg(FactCustomerAccount.churn).desc())
        .all()
    )

    for payment_method, churn_rate in result:
        print(payment_method, churn_rate)

    ########################################################################################
    print("="*69)
    #######################################################################################

    result = (
        session.query(
            FactCustomerAccount.churn,
            func.avg(FactCustomerAccount.monthly_charges).label("avg_monthly_charges")
        )
        .group_by(FactCustomerAccount.churn)
        .all()
    )

    for churn, avg_charges in result:
        print(churn, avg_charges)

    ########################################################################################
    print("="*69)
    #######################################################################################

    result = (
        session.query(
            FactCustomerAccount.customerID,
            FactCustomerAccount.tenure,
            FactCustomerAccount.monthly_charges,
            Contract.contract_type
        )
        .join(
            Contract,
            FactCustomerAccount.contract_id == Contract.contract_id
        )
        .filter(
            Contract.contract_type == "Month-to-month",
            FactCustomerAccount.tenure < 12,
            FactCustomerAccount.monthly_charges > session.query(
                func.avg(FactCustomerAccount.monthly_charges)
            ).scalar_subquery()
        )
        .all()
    )

    print("Risky customer count:", len(result))

    for row in result[:5]:
        print(row)

    ########################################################################################
    print("="*69)
    #######################################################################################

    result = (
        session.query(
            func.count(FactCustomerAccount.customerID).label("customer_count"),
            func.avg(FactCustomerAccount.tenure).label("avg_tenure")
        )
        .filter(
            FactCustomerAccount.churn == 1,
            FactCustomerAccount.total_charges > 2000
        )
        .first()
    )

    print("Customer count:", result.customer_count)
    print("Average tenure:", result.avg_tenure)

    ########################################################################################
    print("="*69)
    #######################################################################################

    result = (
        session.query(
            Contract.contract_type,
            func.avg(FactCustomerAccount.monthly_charges).label("avg_monthly_charges"),
            func.avg(FactCustomerAccount.tenure).label("avg_tenure"),
            func.avg(FactCustomerAccount.churn).label("churn_rate")
        )
        .join(
            FactCustomerAccount,
            FactCustomerAccount.contract_id == Contract.contract_id
        )
        .group_by(Contract.contract_type)
        .order_by(func.avg(FactCustomerAccount.churn).desc())
        .all()
    )

    for row in result:
        print(row)

    ########################################################################################
    print("="*69)
    #######################################################################################
