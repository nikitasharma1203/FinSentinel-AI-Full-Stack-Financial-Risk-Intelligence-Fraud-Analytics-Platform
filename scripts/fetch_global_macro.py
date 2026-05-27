"""
FinSentinel AI — Global Macro Variables Fetcher
Fetches: Crude Oil (Brent), DXY, Gold, US Fed Rate, US CPI, Treasury Yields, S&P 500
Sources: FRED + Yahoo Finance
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── FRED Series Mapping ───────────────────────────────────────────────────────
FRED_SERIES = {
    "us_fed_rate":        "FEDFUNDS",        # Federal Funds Rate
    "us_cpi":             "CPIAUCSL",        # US CPI All Items
    "treasury_yield_10y": "DGS10",           # 10-Year Treasury Yield
    "treasury_yield_2y":  "DGS2",            # 2-Year Treasury Yield
    "treasury_yield_3m":  "DTB3",            # 3-Month T-Bill
    "us_inflation_yoy":   "FPCPITOTLZGUSA",  # US Inflation YoY
    "us_m2_money":        "M2SL",            # US M2 Money Supply
    "vix_index":          "VIXCLS",          # CBOE VIX
    "crude_oil_wti":      "DCOILWTICO",      # WTI Crude Oil
    "gold_price":         "GOLDAMGBD228NLBM",# Gold Price London
    "dxy":                "DTWEXBGS",        # Trade-Weighted USD Index
    "us_unemployment":    "UNRATE",          # US Unemployment Rate
}

# ── Yahoo Finance Tickers ─────────────────────────────────────────────────────
YAHOO_TICKERS = {
    "sp500":         "^GSPC",
    "crude_brent":   "BZ=F",
    "gold_futures":  "GC=F",
    "dxy_futures":   "DX-Y.NYB",
    "vix":           "^VIX",
}


def fetch_fred_series(start: str = "2010-01-01") -> pd.DataFrame:
    """Fetch multiple FRED series and merge."""
    try:
        from fredapi import Fred
        api_key = os.environ.get("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY not set")

        fred = Fred(api_key=api_key)
        print("📡 Fetching FRED macro series...")
        dfs = []
        for name, series_id in FRED_SERIES.items():
            try:
                s = fred.get_series(series_id, observation_start=start)
                df = s.to_frame(name=name)
                df.index = pd.to_datetime(df.index)
                dfs.append(df)
                print(f"   ✅ {name} ({series_id}): {len(df)} rows")
            except Exception as e:
                print(f"   ⚠️  {name}: {e}")

        if dfs:
            combined = pd.concat(dfs, axis=1)
            combined.index.name = "date"
            return combined
    except Exception as e:
        print(f"   ❌ FRED failed: {e}")
    return pd.DataFrame()


def fetch_yahoo_series(start: str = "2010-01-01") -> pd.DataFrame:
    """Fetch Yahoo Finance series."""
    try:
        import yfinance as yf
        print("📡 Fetching Yahoo Finance macro series...")
        dfs = []
        for name, ticker in YAHOO_TICKERS.items():
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
            return combined
    except Exception as e:
        print(f"   ❌ Yahoo failed: {e}")
    return pd.DataFrame()


def generate_synthetic_macro(start: str = "2010-01-01", end: str = None) -> pd.DataFrame:
    """Synthetic fallback for all global macro variables."""
    print("🎲 Generating synthetic global macro data...")
    end = end or datetime.today().strftime("%Y-%m-%d")
    dates = pd.date_range(start=start, end=end, freq="B")
    n = len(dates)
    np.random.seed(42)

    def brownian(start_val, drift, vol, n):
        returns = np.random.normal(drift / 252, vol / np.sqrt(252), n)
        return start_val * np.cumprod(1 + returns)

    df = pd.DataFrame(index=dates)
    df["crude_brent"]       = np.clip(brownian(60,  0.02, 0.35, n), 20, 140)
    df["crude_oil_wti"]     = df["crude_brent"] * 0.97
    df["gold_price"]        = brownian(1100, 0.04, 0.12, n)
    df["dxy"]               = np.clip(brownian(80, 0.01, 0.06, n), 70, 115)
    df["sp500"]             = brownian(1200, 0.10, 0.18, n)
    df["vix_index"]         = np.abs(np.random.normal(18, 8, n)).clip(9, 80)
    df["us_fed_rate"]       = np.interp(np.arange(n), [0, n//3, n//2, 3*n//4, n-1], [0.25, 2.5, 0.1, 4.5, 5.25])
    df["treasury_yield_10y"]= np.interp(np.arange(n), [0, n//3, n//2, 3*n//4, n-1], [2.5, 3.0, 0.6, 3.5, 4.2])
    df["treasury_yield_2y"] = df["treasury_yield_10y"] - np.random.normal(0.5, 0.3, n)
    df["us_cpi"]            = np.interp(np.arange(n), [0, n//2, n-1], [220, 260, 310])
    df["us_inflation_yoy"]  = np.interp(np.arange(n), [0, n//3, 5*n//8, n-1], [2.0, 2.5, 9.1, 3.5])
    df["us_unemployment"]   = np.interp(np.arange(n), [0, n//5, n//3, n//2, n-1], [9.8, 5.0, 4.0, 14.7, 3.7])

    # Yield curve spread
    df["yield_curve_spread"] = df["treasury_yield_10y"] - df["treasury_yield_2y"]

    df.index.name = "date"
    print(f"   ✅ Synthetic global macro: {len(df)} rows, {len(df.columns)} features")
    return df


def fetch_global_macro(start: str = "2010-01-01") -> pd.DataFrame:
    """Main pipeline: fetch, merge, forward-fill, save."""
    print("\n" + "="*60)
    print("   FinSentinel AI — Global Macro Fetcher")
    print("="*60 + "\n")

    fred_df  = fetch_fred_series(start)
    yahoo_df = fetch_yahoo_series(start)

    if not fred_df.empty and not yahoo_df.empty:
        df = fred_df.merge(yahoo_df, left_index=True, right_index=True, how="outer")
    elif not fred_df.empty:
        df = fred_df
    elif not yahoo_df.empty:
        df = yahoo_df
    else:
        df = generate_synthetic_macro(start)

    if df.empty:
        df = generate_synthetic_macro(start)

    # Forward-fill weekly/monthly series
    df = df.sort_index()
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="B"))
    df = df.ffill().bfill()
    df.index.name = "date"

    # Derived features
    if "crude_brent" in df.columns:
        df["oil_shock"] = (df["crude_brent"].pct_change().abs() > 0.05).astype(int)
    if "treasury_yield_10y" in df.columns and "treasury_yield_2y" in df.columns:
        df["yield_inversion"] = (df["treasury_yield_10y"] < df["treasury_yield_2y"]).astype(int)

    output_path = os.path.join(OUTPUT_DIR, "global_macro.csv")
    df.to_csv(output_path)
    print(f"\n✅ Global macro saved → {output_path}")
    print(f"   Rows: {len(df)} | Columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    df = fetch_global_macro(start="2010-01-01")
    print(df.tail())
