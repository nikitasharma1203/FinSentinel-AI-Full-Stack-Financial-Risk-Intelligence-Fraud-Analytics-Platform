"""
FinSentinel AI — Master ETL Pipeline
Merges all data sources into a unified dataset for ML training.
Run this after all individual fetchers.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RAW_DIR    = os.path.join(BASE_DIR, "..", "data", "raw")
PROC_DIR   = os.path.join(BASE_DIR, "..", "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


def load_or_generate(filename: str, fetch_fn, start: str = "2010-01-01") -> pd.DataFrame:
    path = os.path.join(RAW_DIR, filename)
    if os.path.exists(path):
        print(f"   📂 Loading: {filename}")
        df = pd.read_csv(path, index_col="date", parse_dates=True)
        return df
    else:
        print(f"   📡 Fetching: {filename}")
        return fetch_fn(start)


def run_etl(start: str = "2010-01-01"):
    print("\n" + "="*60)
    print("   FinSentinel AI — Master ETL Pipeline")
    print("="*60 + "\n")

    sys.path.insert(0, BASE_DIR)

    from fetch_usd_inr       import fetch_usd_inr
    from fetch_rbi_indicators import fetch_rbi_indicators
    from fetch_global_macro   import fetch_global_macro
    from fetch_market_data    import fetch_market_data
    from fetch_news_sentiment import fetch_news_sentiment

    print("📥 Loading all data sources...")
    usd_inr   = load_or_generate("usd_inr_historical.csv",  fetch_usd_inr,        start)
    rbi       = load_or_generate("rbi_indicators.csv",      fetch_rbi_indicators,  start)
    macro     = load_or_generate("global_macro.csv",        fetch_global_macro,    start)
    market    = load_or_generate("market_data.csv",         fetch_market_data,     start)
    sentiment = load_or_generate("sentiment_scores.csv",    fetch_news_sentiment,  start)

    print("\n🔗 Merging datasets on date index...")
    dfs = [usd_inr, rbi, macro, market, sentiment]
    combined = dfs[0]
    for df in dfs[1:]:
        combined = combined.merge(df, left_index=True, right_index=True, how="left", suffixes=("", "_dup"))
        # Drop duplicate columns
        combined = combined[[c for c in combined.columns if not c.endswith("_dup")]]

    # Forward-fill and back-fill missing values
    combined = combined.sort_index().ffill().bfill()

    # Filter to business days only
    combined = combined[combined.index.dayofweek < 5]

    # ── Final Feature Set ──────────────────────────────────────────────────────
    print("🔧 Computing final derived features...")

    # Real interest rate differential (India - US)
    if "repo_rate" in combined.columns and "us_fed_rate" in combined.columns:
        combined["rate_differential"] = combined["repo_rate"] - combined["us_fed_rate"]

    # Oil-INR sensitivity
    if "crude_brent" in combined.columns and "usd_inr" in combined.columns:
        combined["oil_inr_ratio"]       = combined["crude_brent"] / combined["usd_inr"]
        combined["oil_shock_on_inr"]    = (
            combined["crude_brent"].pct_change(5) * combined["usd_inr"].pct_change(5)
        )

    # Macro risk composite score
    macro_cols = []
    if "geopolitical_risk" in combined.columns:   macro_cols.append("geopolitical_risk")
    if "india_vix" in combined.columns:           macro_cols.append("india_vix")
    if "volatility_score" in combined.columns:    macro_cols.append("volatility_score")
    if macro_cols:
        # Normalize each to 0-1 and average
        normed = combined[macro_cols].apply(lambda x: (x - x.min()) / (x.max() - x.min() + 1e-9))
        combined["macro_risk_composite"] = normed.mean(axis=1)

    # Market stress flag
    if "india_vix" in combined.columns:
        combined["market_stress"] = (combined["india_vix"] > 25).astype(int)

    # Drop columns with all NaN
    combined.dropna(axis=1, how="all", inplace=True)

    # ── Save ──────────────────────────────────────────────────────────────────
    output_path = os.path.join(PROC_DIR, "master_dataset.csv")
    combined.to_csv(output_path)
    print(f"\n✅ Master dataset saved → {output_path}")
    print(f"   Rows: {len(combined):,}")
    print(f"   Columns: {len(combined.columns)}")
    print(f"   Date range: {combined.index[0].date()} → {combined.index[-1].date()}")
    print(f"   Missing values: {combined.isnull().sum().sum()}")

    # Save column manifest
    manifest = {
        "created_at": datetime.utcnow().isoformat(),
        "n_rows": len(combined),
        "n_columns": len(combined.columns),
        "date_range": [str(combined.index[0].date()), str(combined.index[-1].date())],
        "columns": list(combined.columns),
        "source_mapping": {
            "usd_inr": list(usd_inr.columns),
            "rbi": list(rbi.columns),
            "macro": list(macro.columns),
            "market": list(market.columns),
            "sentiment": list(sentiment.columns),
        }
    }
    import json
    with open(os.path.join(PROC_DIR, "dataset_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("   Manifest saved → dataset_manifest.json")
    return combined


if __name__ == "__main__":
    start = sys.argv[1] if len(sys.argv) > 1 else "2010-01-01"
    run_etl(start)
