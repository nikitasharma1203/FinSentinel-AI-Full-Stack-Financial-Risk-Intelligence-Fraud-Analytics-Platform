"""Customer Risk Intelligence — API Routes."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from database.connection import get_db
from models.orm_models import Customer, Transaction, FraudPrediction

router = APIRouter()


@router.get("/")
async def get_customers(
    skip: int = 0,
    limit: int = 50,
    risk_tier: Optional[str] = None,
    segment: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Customer)
    if risk_tier:
        query = query.filter(Customer.risk_tier == risk_tier.upper())
    if segment:
        query = query.filter(Customer.customer_segment == segment.upper())

    customers = query.order_by(desc(Customer.risk_score)).offset(skip).limit(limit).all()
    return [
        {
            "customer_id": str(c.customer_id),
            "name": c.name,
            "email": c.email,
            "risk_score": c.risk_score,
            "risk_tier": c.risk_tier,
            "customer_segment": c.customer_segment,
            "churn_probability": c.churn_probability,
            "total_transactions": c.total_transactions,
            "total_volume": c.total_volume,
            "avg_transaction_amount": c.avg_transaction_amount,
        }
        for c in customers
    ]


@router.get("/risk-distribution")
async def get_risk_distribution(db: Session = Depends(get_db)):
    """Customer count per risk tier."""
    rows = (
        db.query(Customer.risk_tier, func.count(Customer.customer_id).label("count"))
        .group_by(Customer.risk_tier)
        .all()
    )
    return [{"tier": r.risk_tier, "count": r.count} for r in rows]


@router.get("/{customer_id}")
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.customer_id == uuid.UUID(customer_id)).first()
    if not c:
        raise HTTPException(404, "Customer not found")

    recent_txns = (
        db.query(Transaction)
        .filter(Transaction.customer_id == c.customer_id)
        .order_by(desc(Transaction.timestamp))
        .limit(10)
        .all()
    )

    return {
        "customer_id": str(c.customer_id),
        "name": c.name,
        "email": c.email,
        "country": c.country,
        "risk_score": c.risk_score,
        "risk_tier": c.risk_tier,
        "customer_segment": c.customer_segment,
        "churn_probability": c.churn_probability,
        "total_transactions": c.total_transactions,
        "total_volume": c.total_volume,
        "avg_transaction_amount": c.avg_transaction_amount,
        "recent_transactions": [
            {
                "transaction_id": str(t.transaction_id),
                "amount": t.amount,
                "timestamp": t.timestamp.isoformat(),
                "merchant_category": t.merchant_category,
                "fraud_label": t.fraud_label,
            }
            for t in recent_txns
        ],
    }
