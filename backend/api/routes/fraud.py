"""Fraud Detection & Scoring — API Routes."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from database.connection import get_db
from models.orm_models import Transaction, FraudPrediction, Customer

router = APIRouter()


class ScoreRequest(BaseModel):
    transaction_id: str


class BatchScoreRequest(BaseModel):
    transaction_ids: List[str]


def risk_level_from_prob(prob: float) -> str:
    if prob < 0.3:
        return "LOW"
    elif prob < 0.6:
        return "MEDIUM"
    elif prob < 0.85:
        return "HIGH"
    return "CRITICAL"


@router.post("/score")
async def score_transaction(
    req: ScoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Score a single transaction for fraud probability."""
    t = db.query(Transaction).filter(
        Transaction.transaction_id == uuid.UUID(req.transaction_id)
    ).first()
    if not t:
        raise HTTPException(404, "Transaction not found")

    # In production: load saved ML model and run inference
    # Here we simulate the scoring pipeline
    from services.fraud_scorer import score_single_transaction
    result = score_single_transaction(t)

    pred = FraudPrediction(
        transaction_id=t.transaction_id,
        fraud_probability=result["fraud_probability"],
        anomaly_score=result["anomaly_score"],
        risk_level=risk_level_from_prob(result["fraud_probability"]),
        model_version="1.0.0",
        model_name="XGBoost+IsolationForest",
        top_features=result.get("top_features"),
        explanation=result.get("explanation"),
        flagged=result["fraud_probability"] > 0.6,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    return {
        "prediction_id": str(pred.prediction_id),
        "transaction_id": req.transaction_id,
        "fraud_probability": pred.fraud_probability,
        "anomaly_score": pred.anomaly_score,
        "risk_level": pred.risk_level,
        "flagged": pred.flagged,
        "explanation": pred.explanation,
        "top_features": pred.top_features,
    }


@router.get("/alerts")
async def get_fraud_alerts(
    hours: int = 24,
    min_probability: float = 0.6,
    db: Session = Depends(get_db),
):
    """Get recent high-probability fraud alerts."""
    since = datetime.utcnow() - timedelta(hours=hours)

    alerts = (
        db.query(FraudPrediction, Transaction)
        .join(Transaction)
        .filter(
            FraudPrediction.predicted_at >= since,
            FraudPrediction.fraud_probability >= min_probability,
        )
        .order_by(desc(FraudPrediction.fraud_probability))
        .limit(100)
        .all()
    )

    return [
        {
            "prediction_id": str(p.prediction_id),
            "transaction_id": str(t.transaction_id),
            "customer_id": str(t.customer_id),
            "amount": t.amount,
            "currency": t.currency,
            "timestamp": t.timestamp.isoformat(),
            "location_city": t.location_city,
            "merchant_category": t.merchant_category,
            "fraud_probability": p.fraud_probability,
            "risk_level": p.risk_level,
            "flagged": p.flagged,
            "reviewed": p.reviewed,
            "explanation": p.explanation,
        }
        for p, t in alerts
    ]


@router.get("/heatmap")
async def get_fraud_heatmap(days: int = 30, db: Session = Depends(get_db)):
    """Fraud by merchant category."""
    since = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            Transaction.merchant_category,
            func.count(Transaction.transaction_id).label("total"),
            func.sum(func.cast(Transaction.fraud_label, Integer)).label("fraud_count"),
            func.avg(FraudPrediction.fraud_probability).label("avg_prob"),
        )
        .join(FraudPrediction)
        .filter(Transaction.timestamp >= since)
        .group_by(Transaction.merchant_category)
        .order_by(desc("fraud_count"))
        .all()
    )

    return [
        {
            "category": row.merchant_category or "Unknown",
            "total": row.total,
            "fraud_count": row.fraud_count or 0,
            "fraud_rate": round((row.fraud_count or 0) / row.total * 100, 2) if row.total else 0,
            "avg_fraud_probability": round(float(row.avg_prob or 0), 4),
        }
        for row in rows
    ]


@router.get("/by-payment-method")
async def get_fraud_by_payment_method(days: int = 30, db: Session = Depends(get_db)):
    """Fraud breakdown by payment method."""
    since = datetime.utcnow() - timedelta(days=days)

    rows = (
        db.query(
            Transaction.payment_method,
            func.count(Transaction.transaction_id).label("total"),
            func.sum(func.cast(Transaction.fraud_label, Integer)).label("fraud_count"),
        )
        .filter(Transaction.timestamp >= since)
        .group_by(Transaction.payment_method)
        .all()
    )

    return [
        {
            "payment_method": row.payment_method or "Unknown",
            "total": row.total,
            "fraud_count": row.fraud_count or 0,
            "fraud_rate": round((row.fraud_count or 0) / row.total * 100, 2) if row.total else 0,
        }
        for row in rows
    ]


@router.post("/review/{prediction_id}")
async def review_prediction(
    prediction_id: str,
    outcome: str,  # CONFIRMED_FRAUD | FALSE_POSITIVE
    reviewer_id: str,
    db: Session = Depends(get_db),
):
    """Mark a prediction as reviewed by an analyst."""
    pred = db.query(FraudPrediction).filter(
        FraudPrediction.prediction_id == uuid.UUID(prediction_id)
    ).first()
    if not pred:
        raise HTTPException(404, "Prediction not found")

    pred.reviewed = True
    pred.review_outcome = outcome
    pred.reviewer_id = uuid.UUID(reviewer_id)
    db.commit()

    return {"message": "Review recorded", "outcome": outcome}
