"""Transaction Intelligence Engine — API Routes."""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from database.connection import get_db
from models.orm_models import Transaction, FraudPrediction, Customer, Merchant

router = APIRouter()


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    customer_id: str
    merchant_id: Optional[str] = None
    amount: float
    currency: str = "INR"
    timestamp: datetime
    location_city: Optional[str] = None
    location_country: Optional[str] = "India"
    device_type: Optional[str] = None
    merchant_category: Optional[str] = None
    payment_method: Optional[str] = None
    is_international: bool = False


class TransactionResponse(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    timestamp: datetime
    location_city: Optional[str]
    merchant_category: Optional[str]
    payment_method: Optional[str]
    fraud_label: bool
    status: str
    fraud_probability: Optional[float] = None
    risk_level: Optional[str] = None

    class Config:
        from_attributes = True


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[dict])
async def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=500),
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    flagged_only: bool = False,
    days: int = Query(30, description="Last N days"),
    db: Session = Depends(get_db),
):
    """Fetch paginated transactions with optional filters."""
    since = datetime.utcnow() - timedelta(days=days)
    query = db.query(Transaction).filter(Transaction.timestamp >= since)

    if min_amount:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount:
        query = query.filter(Transaction.amount <= max_amount)
    if flagged_only:
        query = query.join(FraudPrediction).filter(FraudPrediction.flagged == True)

    transactions = query.order_by(desc(Transaction.timestamp)).offset(skip).limit(limit).all()

    result = []
    for t in transactions:
        pred = t.predictions[-1] if t.predictions else None
        result.append({
            "transaction_id": str(t.transaction_id),
            "customer_id": str(t.customer_id),
            "amount": t.amount,
            "currency": t.currency,
            "timestamp": t.timestamp.isoformat(),
            "location_city": t.location_city,
            "location_country": t.location_country,
            "merchant_category": t.merchant_category,
            "payment_method": t.payment_method,
            "device_type": t.device_type,
            "is_international": t.is_international,
            "fraud_label": t.fraud_label,
            "status": t.status,
            "fraud_probability": pred.fraud_probability if pred else None,
            "risk_level": pred.risk_level if pred else None,
            "flagged": pred.flagged if pred else False,
        })
    return result


@router.get("/kpis")
async def get_kpis(days: int = 30, db: Session = Depends(get_db)):
    """Executive KPIs for the dashboard."""
    since = datetime.utcnow() - timedelta(days=days)

    total_txns = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.timestamp >= since
    ).scalar() or 0

    total_volume = db.query(func.sum(Transaction.amount)).filter(
        Transaction.timestamp >= since
    ).scalar() or 0.0

    fraud_count = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.timestamp >= since,
        Transaction.fraud_label == True,
    ).scalar() or 0

    flagged_count = db.query(func.count(FraudPrediction.prediction_id)).filter(
        FraudPrediction.flagged == True,
        FraudPrediction.predicted_at >= since,
    ).scalar() or 0

    high_risk_customers = db.query(func.count(Customer.customer_id)).filter(
        Customer.risk_tier.in_(["HIGH", "CRITICAL"])
    ).scalar() or 0

    fraud_rate = (fraud_count / total_txns * 100) if total_txns > 0 else 0
    risk_exposure = db.query(func.sum(Transaction.amount)).join(FraudPrediction).filter(
        FraudPrediction.flagged == True,
        Transaction.timestamp >= since,
    ).scalar() or 0.0

    return {
        "total_transactions": total_txns,
        "total_volume": round(total_volume, 2),
        "fraud_count": fraud_count,
        "fraud_rate": round(fraud_rate, 3),
        "flagged_count": flagged_count,
        "high_risk_customers": high_risk_customers,
        "risk_exposure": round(risk_exposure, 2),
        "period_days": days,
    }


@router.get("/trends")
async def get_trends(days: int = 30, db: Session = Depends(get_db)):
    """Daily transaction volume & fraud trends."""
    since = datetime.utcnow() - timedelta(days=days)

    daily = (
        db.query(
            func.date(Transaction.timestamp).label("day"),
            func.count(Transaction.transaction_id).label("total"),
            func.sum(Transaction.amount).label("volume"),
            func.sum(func.cast(Transaction.fraud_label, Integer)).label("fraud"),
        )
        .filter(Transaction.timestamp >= since)
        .group_by(func.date(Transaction.timestamp))
        .order_by(func.date(Transaction.timestamp))
        .all()
    )

    return [
        {
            "date": str(row.day),
            "total": row.total,
            "volume": round(float(row.volume or 0), 2),
            "fraud": row.fraud or 0,
            "fraud_rate": round((row.fraud or 0) / row.total * 100, 3) if row.total else 0,
        }
        for row in daily
    ]


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get a single transaction with full details."""
    t = db.query(Transaction).filter(
        Transaction.transaction_id == uuid.UUID(transaction_id)
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")

    pred = t.predictions[-1] if t.predictions else None
    return {
        "transaction_id": str(t.transaction_id),
        "customer_id": str(t.customer_id),
        "merchant_id": str(t.merchant_id) if t.merchant_id else None,
        "amount": t.amount,
        "currency": t.currency,
        "timestamp": t.timestamp.isoformat(),
        "location": {
            "lat": t.location_lat,
            "lon": t.location_lon,
            "city": t.location_city,
            "country": t.location_country,
        },
        "device": {"id": t.device_id, "type": t.device_type},
        "ip_address": t.ip_address,
        "merchant_category": t.merchant_category,
        "payment_method": t.payment_method,
        "is_international": t.is_international,
        "fraud_label": t.fraud_label,
        "status": t.status,
        "prediction": {
            "fraud_probability": pred.fraud_probability if pred else None,
            "anomaly_score": pred.anomaly_score if pred else None,
            "risk_level": pred.risk_level if pred else None,
            "explanation": pred.explanation if pred else None,
            "top_features": pred.top_features if pred else None,
            "flagged": pred.flagged if pred else False,
        } if pred else None,
    }
