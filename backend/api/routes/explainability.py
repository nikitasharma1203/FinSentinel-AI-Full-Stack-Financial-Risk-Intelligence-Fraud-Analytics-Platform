"""Explainable AI Engine — API Routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from database.connection import get_db
from models.orm_models import FraudPrediction, Transaction

router = APIRouter()


@router.get("/{prediction_id}")
async def get_explanation(prediction_id: str, db: Session = Depends(get_db)):
    """Return full SHAP explanation for a prediction."""
    pred = db.query(FraudPrediction).filter(
        FraudPrediction.prediction_id == uuid.UUID(prediction_id)
    ).first()
    if not pred:
        raise HTTPException(404, "Prediction not found")

    return {
        "prediction_id": str(pred.prediction_id),
        "transaction_id": str(pred.transaction_id),
        "fraud_probability": pred.fraud_probability,
        "risk_level": pred.risk_level,
        "explanation": pred.explanation,
        "top_features": pred.top_features,
        "shap_values": pred.shap_values,
        "model_name": pred.model_name,
        "model_version": pred.model_version,
    }


@router.get("/feature-importance/global")
async def get_global_feature_importance():
    """Return global model feature importance (pre-computed)."""
    # In production, load from saved model artifacts
    return {
        "model": "XGBoost Fraud Classifier v1.0",
        "feature_importance": [
            {"feature": "transaction_velocity_1h",      "importance": 0.187, "description": "Number of transactions in last 1 hour"},
            {"feature": "amount_deviation_from_avg",    "importance": 0.164, "description": "How much amount deviates from customer average"},
            {"feature": "merchant_risk_score",          "importance": 0.141, "description": "Historical fraud rate for this merchant"},
            {"feature": "geographic_distance_km",       "importance": 0.118, "description": "Distance from customer's usual location"},
            {"feature": "hour_of_day",                  "importance": 0.096, "description": "Hour of transaction (night=higher risk)"},
            {"feature": "device_switch_frequency",      "importance": 0.083, "description": "How often customer switches devices"},
            {"feature": "failed_txn_last_24h",          "importance": 0.071, "description": "Failed transaction count in last 24h"},
            {"feature": "is_international",             "importance": 0.058, "description": "International transaction flag"},
            {"feature": "merchant_category_rarity",     "importance": 0.047, "description": "How rare this merchant category is for customer"},
            {"feature": "time_since_last_transaction",  "importance": 0.035, "description": "Minutes since previous transaction"},
        ]
    }
