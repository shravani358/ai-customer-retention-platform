from sqlalchemy import Column, Integer, String, Float
from database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, default="")
    tenure_months = Column(Integer, default=0)
    monthly_charges = Column(Float, default=0.0)
    support_tickets = Column(Integer, default=0)
    last_login_days = Column(Integer, default=0)
    churn_risk = Column(Float, default=0.0)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst")  # "admin", "manager", or "analyst"