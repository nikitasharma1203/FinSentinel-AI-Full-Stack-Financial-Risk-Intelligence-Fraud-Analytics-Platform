"""SQLAlchemy ORM Models for FinSentinel AI."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, Integer,
    DateTime, Date, ForeignKey, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database.connection import Base


def generate_uuid():
    return str(uuid.uuid4())


class Customer(Base):
    __tablename__ = "customers"

    customer_id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name                 = Column(String(255))
    email                = Column(String(255), unique=True)
    phone                = Column(String(20))
    country              = Column(String(100), default="India")
    risk_score           = Column(Float, default=0.0)
    risk_tier            = Column(String(20), default="LOW")
    customer_segment     = Column(String(50))
    churn_probability    = Column(Float, default=0.0)
    total_transactions   = Column(Integer, default=0)
    total_volume         = Column(Float, default=0.0)
    avg_transaction_amount = Column(Float, default=0.0)
    created_at           = Column(DateTime, default=datetime.utcnow)
    updated_at           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="customer")


class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name          = Column(String(255))
    category      = Column(String(100))
    country       = Column(String(100))
    risk_score    = Column(Float, default=0.0)
    fraud_rate    = Column(Float, default=0.0)
    total_volume  = Column(Float, default=0.0)
    created_at    = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="merchant")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id       = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"))
    merchant_id       = Column(UUID(as_uuid=True), ForeignKey("merchants.merchant_id"))
    amount            = Column(Float, nullable=False)
    currency          = Column(String(10), default="INR")
    timestamp         = Column(DateTime, nullable=False)
    location_lat      = Column(Float)
    location_lon      = Column(Float)
    location_city     = Column(String(100))
    location_country  = Column(String(100))
    device_id         = Column(String(255))
    device_type       = Column(String(50))
    ip_address        = Column(String(45))
    merchant_category = Column(String(100))
    payment_method    = Column(String(50))
    is_international  = Column(Boolean, default=False)
    fraud_label       = Column(Boolean, default=False)
    status            = Column(String(20), default="COMPLETED")
    created_at        = Column(DateTime, default=datetime.utcnow)

    customer    = relationship("Customer", back_populates="transactions")
    merchant    = relationship("Merchant", back_populates="transactions")
    predictions = relationship("FraudPrediction", back_populates="transaction")


class FraudPrediction(Base):
    __tablename__ = "fraud_predictions"

    prediction_id     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id    = Column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id"))
    fraud_probability = Column(Float, nullable=False)
    anomaly_score     = Column(Float)
    risk_level        = Column(String(20))
    model_version     = Column(String(50))
    model_name        = Column(String(100))
    shap_values       = Column(JSONB)
    top_features      = Column(JSONB)
    explanation       = Column(Text)
    flagged           = Column(Boolean, default=False)
    reviewed          = Column(Boolean, default=False)
    reviewer_id       = Column(UUID(as_uuid=True))
    review_outcome    = Column(String(20))
    predicted_at      = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="predictions")


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    date                      = Column(Date, nullable=False, unique=True)
    usd_inr                   = Column(Float)
    repo_rate                 = Column(Float)
    reverse_repo              = Column(Float)
    cpi_inflation             = Column(Float)
    forex_reserves            = Column(Float)
    current_account_deficit   = Column(Float)
    trade_balance             = Column(Float)
    money_supply_m3           = Column(Float)
    crude_oil_brent           = Column(Float)
    us_fed_rate               = Column(Float)
    dxy                       = Column(Float)
    gold_price                = Column(Float)
    us_cpi                    = Column(Float)
    treasury_yield_10y        = Column(Float)
    nifty50                   = Column(Float)
    india_vix                 = Column(Float)
    sp500                     = Column(Float)
    bank_nifty                = Column(Float)
    fii_flow                  = Column(Float)
    dii_flow                  = Column(Float)
    geopolitical_risk_score   = Column(Float)
    news_sentiment_score      = Column(Float)
    created_at                = Column(DateTime, default=datetime.utcnow)


class NetworkEdge(Base):
    __tablename__ = "network_edges"

    edge_id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id         = Column(UUID(as_uuid=True), nullable=False)
    target_id         = Column(UUID(as_uuid=True), nullable=False)
    source_type       = Column(String(20))
    target_type       = Column(String(20))
    transaction_count = Column(Integer, default=1)
    total_amount      = Column(Float, default=0.0)
    risk_score        = Column(Float, default=0.0)
    is_suspicious     = Column(Boolean, default=False)
    first_seen        = Column(DateTime)
    last_seen         = Column(DateTime)


class Report(Base):
    __tablename__ = "reports"

    report_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(String(255))
    title        = Column(String(500))
    report_type  = Column(String(50))
    parameters   = Column(JSONB)
    file_path    = Column(String(500))
    generated_at = Column(DateTime, default=datetime.utcnow)


class ScenarioSimulation(Base):
    __tablename__ = "scenario_simulations"

    simulation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id       = Column(String(255))
    scenario_name = Column(String(255))
    parameters    = Column(JSONB, nullable=False)
    results       = Column(JSONB, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
