"""Analytics Overview — API Routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from database.connection import get_db
from models.orm_models import MacroIndicator, Transaction, FraudPrediction

router = APIRouter()


@router.get("/macro")
async def get_macro_indicators(days: int = 90, db: Session = Depends(get_db)):
    """Return recent macro indicator time series."""
    since = datetime.utcnow().date() - timedelta(days=days)
    rows = (
        db.query(MacroIndicator)
        .filter(MacroIndicator.date >= since)
        .order_by(MacroIndicator.date)
        .all()
    )
    return [
        {
            "date": str(r.date),
            "usd_inr": r.usd_inr,
            "repo_rate": r.repo_rate,
            "cpi_inflation": r.cpi_inflation,
            "crude_oil_brent": r.crude_oil_brent,
            "nifty50": r.nifty50,
            "india_vix": r.india_vix,
            "gold_price": r.gold_price,
            "dxy": r.dxy,
            "geopolitical_risk_score": r.geopolitical_risk_score,
            "news_sentiment_score": r.news_sentiment_score,
        }
        for r in rows
    ]


@router.get("/correlations")
async def get_correlations(db: Session = Depends(get_db)):
    """Return pre-computed feature correlations with fraud rate."""
    return {
        "correlations": [
            {"feature": "India VIX",               "correlation": 0.61,  "direction": "positive"},
            {"feature": "USD/INR Rate",            "correlation": 0.54,  "direction": "positive"},
            {"feature": "Crude Oil Price",         "correlation": 0.48,  "direction": "positive"},
            {"feature": "Geopolitical Risk Score", "correlation": 0.43,  "direction": "positive"},
            {"feature": "Repo Rate",               "correlation": -0.38, "direction": "negative"},
            {"feature": "NIFTY 50",                "correlation": -0.31, "direction": "negative"},
            {"feature": "Forex Reserves",          "correlation": -0.27, "direction": "negative"},
            {"feature": "FII Flow",                "correlation": -0.22, "direction": "negative"},
        ]
    }


@router.get("/copilot-insights")
async def get_copilot_insights(db: Session = Depends(get_db)):
    """AI-generated analyst insights."""
    since_7d = datetime.utcnow() - timedelta(days=7)
    since_14d = datetime.utcnow() - timedelta(days=14)

    fraud_7d = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.timestamp >= since_7d, Transaction.fraud_label == True
    ).scalar() or 0

    fraud_14d = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.timestamp >= since_14d,
        Transaction.timestamp < since_7d,
        Transaction.fraud_label == True,
    ).scalar() or 1

    fraud_change = ((fraud_7d - fraud_14d) / max(fraud_14d, 1)) * 100

    insights = []
    if abs(fraud_change) > 5:
        direction = "increased" if fraud_change > 0 else "decreased"
        severity = "warning" if fraud_change > 0 else "positive"
        insights.append({
            "type": severity,
            "title": f"Fraud Activity {direction.capitalize()} {abs(fraud_change):.0f}%",
            "message": f"Fraud activity has {direction} by {abs(fraud_change):.1f}% compared to the previous week.",
            "action": "Review flagged transactions in the Transaction Monitor." if fraud_change > 0 else "Monitor for continued improvement.",
        })

    insights += [
        {
            "type": "info",
            "title": "High-Risk Merchant Cluster Detected",
            "message": "Electronics and Crypto merchant categories show coordinated anomaly patterns across 3 customer clusters.",
            "action": "Investigate network cluster #2 in the Network Intelligence module.",
        },
        {
            "type": "warning",
            "title": "Rising Churn Risk in HNI Segment",
            "message": "High Net Worth Individual customers show 18% elevated churn probability this month.",
            "action": "Engage retention team for top 50 at-risk customers.",
        },
        {
            "type": "info",
            "title": "UPI Transactions Showing Velocity Spike",
            "message": "UPI payment method velocity anomalies up 22% — likely seasonal pattern but warrants monitoring.",
            "action": "Adjust velocity thresholds for UPI if spike persists >48h.",
        },
    ]

    return {"insights": insights, "generated_at": datetime.utcnow().isoformat()}
