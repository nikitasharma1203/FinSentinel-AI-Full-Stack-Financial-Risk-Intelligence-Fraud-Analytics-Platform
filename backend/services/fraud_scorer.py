"""
Fraud Scoring Service
Wraps the trained ML models for inference.
"""

import os
import joblib
import numpy as np
from typing import Optional


MODEL_PATH = os.environ.get("MODEL_PATH", "./ml/models/")

_xgb_model = None
_iso_model = None
_scaler = None
_feature_cols = None


def _load_models():
    global _xgb_model, _iso_model, _scaler, _feature_cols
    try:
        _xgb_model   = joblib.load(os.path.join(MODEL_PATH, "xgb_fraud_classifier.pkl"))
        _iso_model   = joblib.load(os.path.join(MODEL_PATH, "isolation_forest.pkl"))
        _scaler      = joblib.load(os.path.join(MODEL_PATH, "feature_scaler.pkl"))
        _feature_cols = joblib.load(os.path.join(MODEL_PATH, "feature_columns.pkl"))
    except FileNotFoundError:
        pass  # Models not trained yet — use heuristic fallback


def _extract_features(transaction) -> np.ndarray:
    """Extract ML features from a Transaction ORM object."""
    hour = transaction.timestamp.hour if transaction.timestamp else 12
    is_night = 1 if hour < 6 or hour > 22 else 0
    is_international = 1 if transaction.is_international else 0
    amount = transaction.amount or 0.0

    return np.array([[
        amount,
        is_night,
        is_international,
        hour,
        0.0,   # transaction_velocity_1h  (requires history lookup)
        0.0,   # amount_deviation_from_avg (requires customer history)
        0.0,   # merchant_risk_score
        0.0,   # geographic_distance_km
        0.0,   # device_switch_frequency
        0.0,   # failed_txn_last_24h
    ]])


def _heuristic_score(transaction) -> dict:
    """Fallback heuristic scorer when ML models aren't available."""
    score = 0.05
    if transaction.amount > 100_000:
        score += 0.25
    if transaction.is_international:
        score += 0.15
    if transaction.timestamp and (transaction.timestamp.hour < 5 or transaction.timestamp.hour > 23):
        score += 0.20
    if transaction.merchant_category in ["CRYPTO", "GAMBLING", "FOREIGN_EXCHANGE"]:
        score += 0.30

    score = min(score, 0.99)
    reasons = []
    if score > 0.6:
        if transaction.amount > 100_000:
            reasons.append("unusually high transaction amount")
        if transaction.is_international:
            reasons.append("international transaction")
        if transaction.timestamp and transaction.timestamp.hour < 5:
            reasons.append("transaction at unusual hour (late night)")
        if transaction.merchant_category in ["CRYPTO", "GAMBLING"]:
            reasons.append(f"high-risk merchant category: {transaction.merchant_category}")

    explanation = (
        "Transaction flagged due to: " + ", ".join(reasons) + "."
        if reasons else "Transaction within normal parameters."
    )

    top_features = [
        {"feature": "amount",             "contribution": 0.25 if transaction.amount > 100_000 else 0.02},
        {"feature": "is_international",   "contribution": 0.15 if transaction.is_international else 0.0},
        {"feature": "hour_of_day",        "contribution": 0.20 if transaction.timestamp and transaction.timestamp.hour < 5 else 0.01},
        {"feature": "merchant_category",  "contribution": 0.30 if transaction.merchant_category in ["CRYPTO","GAMBLING"] else 0.02},
    ]

    return {
        "fraud_probability": round(score, 4),
        "anomaly_score": round(score * 0.85, 4),
        "explanation": explanation,
        "top_features": sorted(top_features, key=lambda x: x["contribution"], reverse=True),
    }


def score_single_transaction(transaction) -> dict:
    """Score a transaction using ML models or heuristic fallback."""
    if _xgb_model is None:
        _load_models()

    if _xgb_model is None:
        return _heuristic_score(transaction)

    features = _extract_features(transaction)
    if _scaler:
        features = _scaler.transform(features)

    fraud_prob = float(_xgb_model.predict_proba(features)[0][1])
    anomaly_score = float(-_iso_model.score_samples(features)[0])

    # Normalize anomaly score to 0-1
    anomaly_norm = min(max((anomaly_score + 0.5) / 1.0, 0), 1)

    # Blend: 70% XGB + 30% Isolation Forest
    blended_score = 0.7 * fraud_prob + 0.3 * anomaly_norm

    return {
        "fraud_probability": round(blended_score, 4),
        "anomaly_score": round(anomaly_norm, 4),
        "explanation": f"Model confidence: {blended_score:.1%}. XGB: {fraud_prob:.1%}, Anomaly: {anomaly_norm:.1%}",
        "top_features": [],  # Populated by SHAP in production
    }
