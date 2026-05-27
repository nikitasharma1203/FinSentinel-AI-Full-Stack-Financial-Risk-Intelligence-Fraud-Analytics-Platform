"""
FinSentinel AI — USD/INR Historical Exchange Rate Fetcher
Sources: Yahoo Finance (yfinance) + FRED (DEXINUS)
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_from_yfinance(start: str = "2010-01-01", end: str = None) -> pd.DataFrame:
    """Fetch USD/INR from Yahoo Finance using yfinance."""
    try:
        import yfinance as yf
        end = end or datetime.today().strftime("%Y-%m-%d")
        print(f"📡 Fetching USD/INR from Yahoo Finance ({start} → {end})...")
        ticker = yf.Ticker("INR=X")
        df = ticker.history(start=start, end=end, interval="1d")
        if df.empty:
            raise ValueError("Empty response")
        df = df[["Close"]].rename(columns={"Close": "usd_inr"})
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.index.name = "date"
        print(f"   ✅ Yahoo Finance: {len(df)} rows")
        return df
    except Exception as e:
        print(f"   ⚠️  Yahoo Finance failed: {e}")
        return pd.DataFrame()


def fetch_from_fred(start: str = "2010-01-01") -> pd.DataFrame:
    """Fetch USD/INR from FRED (DEXINUS series)."""
    try:
        from fredapi import Fred
        api_key = os.environ.get("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY not set")

        print("📡 Fetching USD/INR from FRED (DEXINUS)...")
        fred = Fred(api_key=api_key)
        series = fred.get_series("DEXINUS", observation_start=start)
        df = series.dropna().to_frame(name="usd_inr")
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        print(f"   ✅ FRED: {len(df)} rows")
        return df
    except Exception as e:
        print(f"   ⚠️  FRED failed: {e}")
        return pd.DataFrame()


def generate_synthetic_usd_inr(start: str = "2010-01-01", end: str = None) -> pd.DataFrame:
    """Generate synthetic USD/INR rate for development use."""
    print("🎲 Generating synthetic USD/INR time series...")
    end = end or datetime.today().strftime("%Y-%m-%d")
    dates = pd.date_range(start=start, end=end, freq="B")

    np.random.seed(42)
    # Start around 45, realistic drift upward to ~83
    n = len(dates)
    drift = np.linspace(0, 38, n)
    noise = np.random.normal(0, 0.25, n).cumsum()
    # Add some structural shocks
    shocks = np.zeros(n)
    for shock_idx in np.random.choice(n, 20):
        shocks[shock_idx:shock_idx+10] += np.random.choice([-3, 3])

    rates = 45 + drift + noise + shocks
    rates = np.clip(rates, 44, 87)

    df = pd.DataFrame({"usd_inr": np.round(rates, 4)}, index=dates)
    df.index.name = "date"
    print(f"   ✅ Synthetic: {len(df)} rows | Range: {rates.min():.2f}–{rates.max():.2f}")
    return df


def compute_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add technical indicators and derived features."""
    df = df.copy().sort_index()

    # Returns
    df["daily_return"]    = df["usd_inr"].pct_change()
    df["log_return"]      = np.log(df["usd_inr"] / df["usd_inr"].shift(1))

    # Moving averages
    for w in [5, 10, 20, 50, 200]:
        df[f"ma_{w}d"] = df["usd_inr"].rolling(w).mean()

    # Volatility
    df["volatility_20d"]  = df["log_return"].rolling(20).std() * np.sqrt(252)
    df["volatility_60d"]  = df["log_return"].rolling(60).std() * np.sqrt(252)

    # Momentum
    df["momentum_5d"]     = df["usd_inr"] / df["usd_inr"].shift(5) - 1
    df["momentum_20d"]    = df["usd_inr"] / df["usd_inr"].shift(20) - 1

    # RSI (14-day)
    delta = df["usd_inr"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi_14d"] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))

    # Bollinger Bands
    ma20  = df["usd_inr"].rolling(20).mean()
    std20 = df["usd_inr"].rolling(20).std()
    df["bb_upper"] = ma20 + 2 * std20
    df["bb_lower"] = ma20 - 2 * std20
    df["bb_pct"]   = (df["usd_inr"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    # Depreciation flags
    df["is_depreciation_day"] = (df["daily_return"] > 0).astype(int)
    df["sharp_move"]          = (df["daily_return"].abs() > 0.01).astype(int)

    return df.dropna(subset=["daily_return"])


def fetch_usd_inr(start: str = "2010-01-01", end: str = None) -> pd.DataFrame:
    """Main fetcher — tries Yahoo Finance → FRED → synthetic fallback."""
    df = fetch_from_yfinance(start, end)
    if df.empty:
        df = fetch_from_fred(start)
    if df.empty:
        df = generate_synthetic_usd_inr(start, end)

    df = compute_derived_features(df)

    output_path = os.path.join(OUTPUT_DIR, "usd_inr_historical.csv")
    df.to_csv(output_path)
    print(f"\n✅ USD/INR data saved → {output_path}")
    print(f"   Rows: {len(df)} | Columns: {len(df.columns)}")
    print(f"   Date range: {df.index[0].date()} → {df.index[-1].date()}")
    return df


if __name__ == "__main__":
    df = fetch_usd_inr(start="2010-01-01")
    print(df.tail())
