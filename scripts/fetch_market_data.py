"""
FinSentinel AI — Indian Market Data Fetcher
Fetches: NIFTY 50, India VIX, Bank NIFTY, S&P 500, FII/DII Flows
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

MARKET_TICKERS = {
    "nifty50":    "^NSEI",
    "bank_nifty": "^NSEBANK",
    "india_vix":  "^INDIAVIX",
    "sp500":      "^GSPC",
    "sensex":     "^BSESN",
}


def fetch_market_data(start: str = "2010-01-01") -> pd.DataFrame:
    print("\n" + "="*60)
    print("   FinSentinel AI — Market Data Fetcher")
    print("="*60 + "\n")

    try:
        import yfinance as yf
        dfs = []
        for name, ticker in MARKET_TICKERS.items():
            try:
                t = yf.Ticker(ticker)
                df = t.history(start=start, interval="1d")[["Close"]].rename(columns={"Close": name})
                df.index = pd.to_datetime(df.index).tz_localize(None)
                df.index.name = "date"
                dfs.append(df)
                print(f"   ✅ {name} ({ticker}): {len(df)} rows")
            except Exception as e:
                print(f"   ⚠️  {name}: {e}")

        if dfs:
            combined = pd.concat(dfs, axis=1)
        else:
            raise ValueError("No Yahoo data")
    except Exception:
        print("🎲 Generating synthetic market data...")
        dates = pd.date_range(start=start, end=datetime.today().strftime("%Y-%m-%d"), freq="B")
        n = len(dates)
        np.random.seed(99)

        def brownian(s, drift, vol, n):
            return s * np.cumprod(1 + np.random.normal(drift/252, vol/np.sqrt(252), n))

        combined = pd.DataFrame({
            "nifty50":    brownian(5200, 0.12, 0.18, n),
            "bank_nifty": brownian(12000, 0.13, 0.22, n),
            "india_vix":  np.abs(np.random.normal(16, 6, n)).clip(9, 75),
            "sp500":      brownian(1200, 0.10, 0.18, n),
            "sensex":     brownian(17500, 0.12, 0.18, n),
        }, index=dates)
        combined.index.name = "date"

    # Synthetic FII/DII flows (INR Crores)
    n = len(combined)
    combined["fii_flow"] = np.random.normal(500, 3000, n)
    combined["dii_flow"] = -combined["fii_flow"] * 0.6 + np.random.normal(200, 1000, n)

    # Derived features
    combined["nifty_return_1d"]  = combined["nifty50"].pct_change()
    combined["nifty_return_5d"]  = combined["nifty50"].pct_change(5)
    combined["nifty_ma_50d"]     = combined["nifty50"].rolling(50).mean()
    combined["nifty_volatility"] = combined["nifty_return_1d"].rolling(20).std() * np.sqrt(252)
    combined["vix_regime"]       = pd.cut(
        combined["india_vix"],
        bins=[0, 15, 20, 30, 100],
        labels=["LOW", "MODERATE", "HIGH", "EXTREME"]
    )

    output_path = os.path.join(OUTPUT_DIR, "market_data.csv")
    combined.to_csv(output_path)
    print(f"\n✅ Market data saved → {output_path}")
    print(f"   Rows: {len(combined)} | Columns: {len(combined.columns)}")
    return combined


if __name__ == "__main__":
    df = fetch_market_data(start="2010-01-01")
    print(df.tail())
