"""Geopolitical & News Sentiment — API Routes."""

from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import Optional
import random

router = APIRouter()


@router.get("/latest")
async def get_latest_sentiment(days: int = 30):
    """Return recent sentiment scores (NLP-derived from news)."""
    # In production: query MacroIndicator table for stored sentiment scores
    # Here we return example structure
    base_date = datetime.utcnow()
    series = []
    sentiment = 0.1
    for i in range(days):
        date = base_date - timedelta(days=days - i)
        sentiment += random.uniform(-0.08, 0.08)
        sentiment = max(-1.0, min(1.0, sentiment))
        series.append({
            "date": date.strftime("%Y-%m-%d"),
            "sentiment_score": round(sentiment, 4),
            "geopolitical_risk": round(abs(sentiment) * 0.7 + random.uniform(0, 0.3), 4),
            "volatility_score": round(random.uniform(0.1, 0.8), 4),
        })
    return {"series": series}


@router.get("/topics")
async def get_sentiment_topics():
    """Dominant news topics affecting risk sentiment."""
    return {
        "topics": [
            {"topic": "RBI Monetary Policy",     "sentiment": 0.12,  "volume": 847, "impact": "MEDIUM"},
            {"topic": "India Inflation CPI",     "sentiment": -0.31, "volume": 1203,"impact": "HIGH"},
            {"topic": "Rupee Depreciation",      "sentiment": -0.54, "volume": 962, "impact": "HIGH"},
            {"topic": "Middle East Oil Prices",  "sentiment": -0.41, "volume": 1548,"impact": "CRITICAL"},
            {"topic": "FII Outflows",            "sentiment": -0.28, "volume": 634, "impact": "MEDIUM"},
            {"topic": "India GDP Growth",        "sentiment": 0.38,  "volume": 712, "impact": "MEDIUM"},
            {"topic": "US Fed Rate Decision",    "sentiment": -0.19, "volume": 1891,"impact": "HIGH"},
            {"topic": "India Digital Payments",  "sentiment": 0.61,  "volume": 423, "impact": "LOW"},
        ]
    }


@router.get("/event-shocks")
async def get_event_shocks():
    """Major geopolitical/economic shock events."""
    return {
        "events": [
            {"date": "2024-04-15", "event": "Iran-Israel Tensions Escalate",     "shock_score": 0.82, "impact_on_inr": -1.2},
            {"date": "2024-02-01", "event": "US Fed Holds Rates",                 "shock_score": 0.45, "impact_on_inr": 0.3},
            {"date": "2024-01-05", "event": "RBI Surprise Repo Rate Hold",        "shock_score": 0.38, "impact_on_inr": 0.8},
            {"date": "2023-10-07", "event": "Israel-Gaza Conflict Outbreak",      "shock_score": 0.91, "impact_on_inr": -1.8},
            {"date": "2023-08-23", "event": "Brent Crude Hits 9-Month High",      "shock_score": 0.67, "impact_on_inr": -0.9},
            {"date": "2023-06-14", "event": "US Debt Ceiling Crisis Resolved",    "shock_score": 0.52, "impact_on_inr": 0.6},
        ]
    }
