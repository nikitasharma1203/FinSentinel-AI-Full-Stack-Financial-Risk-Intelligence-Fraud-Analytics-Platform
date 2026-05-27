"""
FinSentinel AI — Synthetic Transaction Generator
Generates realistic fraudulent & legitimate transactions for ML training.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import random

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────
CITIES = [
    ("Mumbai", "Maharashtra", 19.0760, 72.8777),
    ("Delhi", "Delhi", 28.6139, 77.2090),
    ("Bangalore", "Karnataka", 12.9716, 77.5946),
    ("Hyderabad", "Telangana", 17.3850, 78.4867),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707),
    ("Kolkata", "West Bengal", 22.5726, 88.3639),
    ("Pune", "Maharashtra", 18.5204, 73.8567),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873),
    ("Rajkot", "Gujarat", 22.3039, 70.8022),
]

MERCHANT_CATEGORIES = [
    "RETAIL", "FOOD_DINING", "TRAVEL", "ELECTRONICS", "HEALTHCARE",
    "UTILITIES", "ENTERTAINMENT", "EDUCATION", "FUEL", "GROCERY",
    "CLOTHING", "BANKING", "CRYPTO", "GAMBLING", "FOREIGN_EXCHANGE",
    "WIRE_TRANSFER", "MONEY_ORDER", "INSURANCE", "REAL_ESTATE",
]

HIGH_RISK_CATS = {"CRYPTO", "GAMBLING", "FOREIGN_EXCHANGE", "WIRE_TRANSFER", "MONEY_ORDER"}

PAYMENT_METHODS = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NETBANKING", "WALLET", "UPI_QR"]
DEVICE_TYPES    = ["MOBILE", "WEB", "POS", "ATM"]
SEGMENTS        = ["RETAIL", "SME", "HNI", "STUDENT", "SENIOR"]

FRAUD_PATTERNS = [
    "card_not_present",
    "account_takeover",
    "money_mule",
    "identity_theft",
    "merchant_fraud",
]


def random_amount(is_fraud: bool, segment: str) -> float:
    """Generate transaction amount based on fraud status & customer segment."""
    base_ranges = {
        "RETAIL":  (200,  25_000),
        "SME":     (1000, 200_000),
        "HNI":     (5000, 500_000),
        "STUDENT": (50,   5_000),
        "SENIOR":  (100,  20_000),
    }
    lo, hi = base_ranges.get(segment, (200, 25_000))
    if is_fraud:
        # Fraud: either very large or micro transactions
        if random.random() < 0.7:
            return round(random.uniform(hi * 0.7, hi * 2.5), 2)
        else:
            return round(random.uniform(1, 50), 2)
    return round(random.uniform(lo, hi), 2)


def generate_transaction(
    customer_id: str,
    segment: str,
    base_city: tuple,
    base_timestamp: datetime,
    is_fraud: bool = False,
    fraud_pattern: str = None,
) -> dict:
    """Generate a single synthetic transaction record."""

    # Location — fraud often from different city
    if is_fraud and random.random() < 0.55:
        city_data = random.choice(CITIES)
    else:
        city_data = base_city
    city_name, _, lat, lon = city_data

    # Time — fraud more common at odd hours
    if is_fraud:
        hour_bias = random.choices(
            list(range(24)),
            weights=[3,3,3,3,2,1,1,1,2,3,3,3,3,3,3,3,3,3,3,3,2,2,3,3],
        )[0]
        ts = base_timestamp.replace(hour=hour_bias, minute=random.randint(0, 59))
    else:
        ts = base_timestamp + timedelta(minutes=random.randint(-120, 120))

    is_international = (is_fraud and random.random() < 0.35)
    category = (
        random.choice(list(HIGH_RISK_CATS))
        if is_fraud and random.random() < 0.5
        else random.choice(MERCHANT_CATEGORIES)
    )
    payment = random.choice(PAYMENT_METHODS)
    device  = random.choice(DEVICE_TYPES)
    amount  = random_amount(is_fraud, segment)

    return {
        "transaction_id":   str(uuid.uuid4()),
        "customer_id":      customer_id,
        "merchant_id":      str(uuid.uuid4()),
        "amount":           amount,
        "currency":         "INR" if not is_international else random.choice(["USD","EUR","GBP"]),
        "timestamp":        ts.strftime("%Y-%m-%d %H:%M:%S"),
        "location_city":    city_name,
        "location_country": "India" if not is_international else random.choice(["USA","UK","UAE"]),
        "location_lat":     round(lat + random.uniform(-0.5, 0.5), 4),
        "location_lon":     round(lon + random.uniform(-0.5, 0.5), 4),
        "device_type":      device,
        "merchant_category":category,
        "payment_method":   payment,
        "is_international": is_international,
        "fraud_label":      is_fraud,
        "fraud_pattern":    fraud_pattern if is_fraud else None,
        "status":           "COMPLETED" if not is_fraud or random.random() > 0.15 else "FAILED",
        "customer_segment": segment,
    }


def generate_customers(n: int = 2000):
    customers = []
    for _ in range(n):
        cid     = str(uuid.uuid4())
        segment = random.choice(SEGMENTS)
        city    = random.choice(CITIES)
        customers.append({
            "customer_id": cid,
            "segment":     segment,
            "base_city":   city,
        })
    return customers


def generate_and_save(
    n_customers: int = 2000,
    n_transactions: int = 200_000,
    fraud_rate: float = 0.025,
    output_path: str = None,
) -> pd.DataFrame:
    """Generate synthetic dataset and save to CSV."""
    print(f"\n🎲 Generating {n_transactions:,} synthetic transactions")
    print(f"   Customers: {n_customers:,} | Fraud rate: {fraud_rate:.1%}")

    customers  = generate_customers(n_customers)
    records    = []
    n_fraud    = int(n_transactions * fraud_rate)
    n_legit    = n_transactions - n_fraud

    start_date = datetime(2020, 1, 1)
    end_date   = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    # Legitimate transactions
    print("   Generating legitimate transactions...")
    for _ in range(n_legit):
        cust = random.choice(customers)
        ts   = start_date + timedelta(days=random.randint(0, date_range))
        records.append(generate_transaction(
            cust["customer_id"], cust["segment"], cust["base_city"], ts, is_fraud=False
        ))

    # Fraudulent transactions
    print("   Generating fraudulent transactions...")
    for _ in range(n_fraud):
        cust    = random.choice(customers)
        ts      = start_date + timedelta(days=random.randint(0, date_range))
        pattern = random.choice(FRAUD_PATTERNS)
        records.append(generate_transaction(
            cust["customer_id"], cust["segment"], cust["base_city"], ts,
            is_fraud=True, fraud_pattern=pattern
        ))

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "transactions_features.csv")

    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved {len(df):,} transactions → {output_path}")
    print(f"   Fraud: {df['fraud_label'].sum():,} | Legit: {(~df['fraud_label']).sum():,}")
    return df


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000
    generate_and_save(n_transactions=n)
