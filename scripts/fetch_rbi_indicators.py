"""
FinSentinel AI — RBI Macroeconomic Indicators Fetcher
Sources: FRED India series + Synthetic fallback
Indicators: Repo Rate, CPI, Forex Reserves, Trade Balance, M3 Money Supply
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

RBI_FRED_SERIES = {
    "cpi_inflation":       "INDCPIALLMINMEI",   # India CPI
    "forex_reserves":      "TRESEGBLINQ188N",   # India Forex Reserves (USD B)
    "current_account":     "INDB6BLTT02STSAQ",  # Current Account Balance
    "trade_balance":       "XTIMVA01INM667S",   # Trade Balance
    "money_supply_m3":     "MYAGM3INM189N",     # M3 Money Supply
    "gdp_growth":          "INDGDPRQPSMEI",     # India GDP Growth
    "lending_rate":        "INDLEND0025MBI",    # India Lending Rate
    "wpi_inflation":       "INDPIEAPI01IXOBSAM",# WPI Inflation
}


def generate_synthetic_rbi(start: str = "2010-01-01", end: str = None) -> pd.DataFrame:
    """Synthetic RBI indicators for development."""
    print("🎲 Generating synthetic RBI indicators...")
    end = end or datetime.today().strftime("%Y-%m-%d")
    dates = pd.date_range(start=start, end=end, freq="MS")  # Monthly
    n = len(dates)
    np.random.seed(123)

    df = pd.DataFrame(index=dates)

    # Repo rate — ranges from 4% to 6.5%
    df["repo_rate"]      = np.interp(np.arange(n), [0, n//4, n//2, 3*n//4, n-1],
                                     [6.5, 4.0, 4.0, 6.5, 6.5]) + np.random.normal(0, 0.1, n)
    df["reverse_repo"]   = df["repo_rate"] - 0.25

    # CPI Inflation
    df["cpi_inflation"]  = np.interp(np.arange(n), [0, n//3, n//2, 5*n//8, n-1],
                                     [9.5, 4.0, 3.4, 7.8, 5.5]) + np.random.normal(0, 0.5, n)

    # Forex Reserves (USD Billions) — ranges from 280B to 650B
    df["forex_reserves"] = np.interp(np.arange(n), [0, n//2, n-1],
                                     [280, 620, 600]) + np.random.normal(0, 10, n)

    # Current Account Deficit (% GDP)
    df["current_account_pct_gdp"] = np.random.normal(-2.0, 0.8, n)

    # Trade Balance (USD Billions)
    df["trade_balance"]  = np.random.normal(-15, 5, n)

    # Money Supply M3 (INR Trillions)
    df["money_supply_m3"] = np.linspace(70, 220, n) + np.random.normal(0, 2, n)

    # FX Intervention (USD Billions — positive=buying, negative=selling)
    df["fx_intervention"] = np.random.normal(0, 3, n)

    # India WPI
    df["wpi_inflation"]   = df["cpi_inflation"] - np.random.normal(1.5, 0.5, n)

    df.index.name = "date"
    print(f"   ✅ Synthetic RBI: {len(df)} monthly rows")
    return df


def fetch_rbi_indicators(start: str = "2010-01-01") -> pd.DataFrame:
    """Fetch RBI indicators, fallback to synthetic."""
    print("\n" + "="*60)
    print("   FinSentinel AI — RBI Indicators Fetcher")
    print("="*60 + "\n")

    try:
        from fredapi import Fred
        api_key = os.environ.get("FRED_API_KEY")
        if not api_key:
            raise ValueError("No FRED API key")

        fred = Fred(api_key=api_key)
        dfs = []
        for name, series_id in RBI_FRED_SERIES.items():
            try:
                s = fred.get_series(series_id, observation_start=start)
                df = s.to_frame(name=name)
                df.index = pd.to_datetime(df.index)
                dfs.append(df)
                print(f"   ✅ {name}: {len(df)} rows")
            except Exception as e:
                print(f"   ⚠️  {name}: {e}")

        if dfs:
            combined = pd.concat(dfs, axis=1)
            combined.index.name = "date"
            # Add synthetic repo rate (not available in FRED)
            synthetic = generate_synthetic_rbi(start)
            for col in ["repo_rate", "reverse_repo", "fx_intervention"]:
                if col not in combined.columns:
                    combined[col] = synthetic.reindex(combined.index).ffill()[col]
            df_final = combined
        else:
            df_final = generate_synthetic_rbi(start)
    except Exception:
        df_final = generate_synthetic_rbi(start)

    # Resample to business daily frequency
    df_final = df_final.sort_index().resample("B").ffill().bfill()
    df_final.index.name = "date"

    output_path = os.path.join(OUTPUT_DIR, "rbi_indicators.csv")
    df_final.to_csv(output_path)
    print(f"\n✅ RBI indicators saved → {output_path}")
    print(f"   Rows: {len(df_final)} | Columns: {len(df_final.columns)}")
    return df_final


if __name__ == "__main__":
    df = fetch_rbi_indicators(start="2010-01-01")
    print(df.tail())
