"""
FinSentinel AI — Geopolitical & News Sentiment Pipeline
NLP-based scoring using NewsAPI + VADER + HuggingFace transformers.
Creates: sentiment_score, volatility_score, event_shock_score
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import warnings

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Search topics for NLP scoring
SEARCH_TOPICS = [
    "India inflation",
    "Rupee depreciation",
    "RBI intervention",
    "Middle East oil",
    "India GDP",
    "US Federal Reserve",
    "India current account deficit",
    "Crude oil prices India",
    "FII outflows India",
    "India forex reserves",
]

GEOPOLITICAL_SHOCKS = [
    {"date": "2022-02-24", "event": "Russia-Ukraine War Outbreak",       "severity": 0.95},
    {"date": "2022-05-04", "event": "US Fed 50bps Rate Hike",            "severity": 0.72},
    {"date": "2022-10-19", "event": "UK Mini-Budget Crisis",             "severity": 0.68},
    {"date": "2023-03-10", "event": "Silicon Valley Bank Collapse",      "severity": 0.81},
    {"date": "2023-07-26", "event": "US Fed Raises to 5.25-5.50%",       "severity": 0.70},
    {"date": "2023-10-07", "event": "Israel-Gaza War Outbreak",          "severity": 0.91},
    {"date": "2024-01-15", "event": "Red Sea Shipping Disruption",       "severity": 0.74},
    {"date": "2024-04-01", "event": "Iran Strikes Israel (Direct)",      "severity": 0.88},
    {"date": "2024-07-31", "event": "Japan Rate Hike Triggers Selloff",  "severity": 0.77},
    {"date": "2020-03-23", "event": "COVID-19 Global Market Crash",      "severity": 0.99},
    {"date": "2020-04-20", "event": "Oil Prices Go Negative (WTI)",      "severity": 0.93},
    {"date": "2021-11-25", "event": "Omicron Variant Discovered",        "severity": 0.76},
]


def fetch_news_sentiment_newsapi(topics: list, days: int = 30) -> list:
    """Fetch articles from NewsAPI and score sentiment."""
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        return []

    try:
        from newsapi import NewsApiClient
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        newsapi = NewsApiClient(api_key=api_key)
        analyzer = SentimentIntensityAnalyzer()
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        articles = []
        for topic in topics:
            try:
                response = newsapi.get_everything(
                    q=topic,
                    from_param=from_date,
                    language="en",
                    sort_by="relevancy",
                    page_size=20,
                )
                for art in response.get("articles", []):
                    text = f"{art.get('title', '')} {art.get('description', '')}"
                    scores = analyzer.polarity_scores(text)
                    articles.append({
                        "date":        art.get("publishedAt", "")[:10],
                        "topic":       topic,
                        "title":       art.get("title", ""),
                        "source":      art.get("source", {}).get("name", ""),
                        "sentiment":   scores["compound"],
                        "positive":    scores["pos"],
                        "negative":    scores["neg"],
                        "neutral":     scores["neu"],
                    })
            except Exception:
                continue
        return articles
    except ImportError:
        return []


def compute_sentiment_scores(
    articles: list,
    start: str = "2010-01-01",
    end: str = None,
) -> pd.DataFrame:
    """Aggregate article-level scores to daily time series."""
    end = end or datetime.today().strftime("%Y-%m-%d")
    dates = pd.date_range(start=start, end=end, freq="B")

    if articles:
        art_df = pd.DataFrame(articles)
        art_df["date"] = pd.to_datetime(art_df["date"])
        daily = (
            art_df.groupby("date")
            .agg(
                sentiment_score=("sentiment", "mean"),
                article_count=("title", "count"),
                negative_ratio=("negative", "mean"),
            )
            .reindex(dates, method="ffill")
        )
    else:
        # Simulate realistic sentiment time series
        print("🎲 Generating synthetic sentiment scores...")
        n = len(dates)
        np.random.seed(77)

        sentiment = np.zeros(n)
        sentiment[0] = 0.05
        for i in range(1, n):
            sentiment[i] = sentiment[i-1] * 0.95 + np.random.normal(0, 0.12)

        # Apply shock events
        shock_df = pd.DataFrame(GEOPOLITICAL_SHOCKS)
        shock_df["date"] = pd.to_datetime(shock_df["date"])

        for _, shock in shock_df.iterrows():
            idx = dates.searchsorted(shock["date"])
            if idx < n:
                impact = -shock["severity"] * 0.8
                decay  = np.exp(-0.1 * np.arange(min(30, n - idx)))
                end_i  = min(idx + len(decay), n)
                sentiment[idx:end_i] += impact * decay[:end_i - idx]

        sentiment = np.clip(sentiment, -1, 1)

        daily = pd.DataFrame({
            "sentiment_score": np.round(sentiment, 4),
            "article_count":   np.random.poisson(45, n),
            "negative_ratio":  np.clip((0.5 - sentiment * 0.3 + np.random.normal(0, 0.05, n)), 0, 1),
        }, index=dates)

    daily.index.name = "date"

    # Derived scores
    daily["volatility_score"]    = daily["sentiment_score"].rolling(5).std().fillna(0.1).clip(0, 1)
    daily["fear_index"]          = ((-daily["sentiment_score"] + 1) / 2 * 0.6
                                    + daily["negative_ratio"] * 0.4).clip(0, 1)
    daily["geopolitical_risk"]   = daily["fear_index"].ewm(span=10).mean().clip(0, 1)
    daily["sentiment_ma_7d"]     = daily["sentiment_score"].rolling(7).mean()
    daily["sentiment_momentum"]  = daily["sentiment_score"] - daily["sentiment_ma_7d"]

    # Shock events
    shock_df = pd.DataFrame(GEOPOLITICAL_SHOCKS)
    shock_df["date"] = pd.to_datetime(shock_df["date"])
    daily["event_shock_score"] = 0.0
    for _, shock in shock_df.iterrows():
        idx = daily.index.searchsorted(shock["date"])
        if idx < len(daily):
            daily.iloc[idx, daily.columns.get_loc("event_shock_score")] = shock["severity"]

    return daily


def fetch_news_sentiment(start: str = "2010-01-01") -> pd.DataFrame:
    """Main pipeline: fetch news + compute NLP sentiment scores."""
    print("\n" + "="*60)
    print("   FinSentinel AI — News Sentiment Pipeline")
    print("="*60 + "\n")

    # Try live news for recent 30 days
    articles = fetch_news_sentiment_newsapi(SEARCH_TOPICS, days=30)
    if articles:
        print(f"   ✅ Fetched {len(articles)} articles from NewsAPI")
    else:
        print("   ℹ️  Using synthetic sentiment generation (set NEWS_API_KEY for live data)")

    df = compute_sentiment_scores(articles, start=start)

    # Save articles
    if articles:
        pd.DataFrame(articles).to_csv(os.path.join(OUTPUT_DIR, "news_articles.csv"), index=False)

    output_path = os.path.join(OUTPUT_DIR, "sentiment_scores.csv")
    df.to_csv(output_path)
    print(f"\n✅ Sentiment scores saved → {output_path}")
    print(f"   Rows: {len(df)} | Columns: {len(df.columns)}")
    print(f"   Mean sentiment: {df['sentiment_score'].mean():.4f}")
    print(f"   Mean geopolitical risk: {df['geopolitical_risk'].mean():.4f}")

    # Save shock events
    shock_path = os.path.join(OUTPUT_DIR, "geopolitical_shocks.json")
    with open(shock_path, "w") as f:
        json.dump(GEOPOLITICAL_SHOCKS, f, indent=2)
    print(f"   Shock events saved → {shock_path}")

    return df


if __name__ == "__main__":
    df = fetch_news_sentiment(start="2010-01-01")
    print(df.tail())
