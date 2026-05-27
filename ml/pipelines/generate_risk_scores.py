"""
FinSentinel AI — Customer Risk Scoring Pipeline
Segments customers using K-Means + DBSCAN and scores churn risk.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
import warnings

warnings.filterwarnings("ignore")

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "..", "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def compute_customer_features(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate transaction-level data to customer-level features."""
    print("📊 Computing customer-level risk features...")
    df = transactions_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    grp = df.groupby("customer_id")

    features = pd.DataFrame({
        "total_transactions":      grp["transaction_id"].count(),
        "total_volume":            grp["amount"].sum(),
        "avg_amount":              grp["amount"].mean(),
        "std_amount":              grp["amount"].std().fillna(0),
        "max_amount":              grp["amount"].max(),
        "min_amount":              grp["amount"].min(),
        "fraud_count":             grp["fraud_label"].sum(),
        "fraud_rate":              grp["fraud_label"].mean(),
        "international_count":     grp["is_international"].sum(),
        "international_rate":      grp["is_international"].mean(),
        "unique_merchants":        grp["merchant_id"].nunique(),
        "unique_categories":       grp["merchant_category"].nunique(),
        "unique_devices":          grp["device_type"].nunique(),
        "unique_cities":           grp["location_city"].nunique(),
        "days_active":             grp["timestamp"].apply(
            lambda x: (x.max() - x.min()).days + 1
        ),
        "avg_daily_transactions":  grp["timestamp"].apply(
            lambda x: len(x) / max((x.max() - x.min()).days + 1, 1)
        ),
        "night_transaction_rate":  grp["timestamp"].apply(
            lambda x: ((x.dt.hour < 6) | (x.dt.hour > 22)).mean()
        ),
        "weekend_rate":            grp["timestamp"].apply(
            lambda x: (x.dt.dayofweek >= 5).mean()
        ),
        "high_risk_cat_rate":      grp["merchant_category"].apply(
            lambda x: x.isin(["CRYPTO","GAMBLING","WIRE_TRANSFER","FOREIGN_EXCHANGE"]).mean()
        ),
        "failed_transaction_rate": grp["status"].apply(
            lambda x: (x == "FAILED").mean()
        ),
        "segment": grp["customer_segment"].first(),
    }).reset_index()

    # Composite risk score (heuristic)
    features["risk_score"] = (
        features["fraud_rate"] * 0.35
        + features["international_rate"] * 0.15
        + features["night_transaction_rate"] * 0.10
        + features["high_risk_cat_rate"] * 0.20
        + features["failed_transaction_rate"] * 0.10
        + (features["unique_devices"] / features["unique_devices"].max()) * 0.10
    ).clip(0, 1)

    # Risk tier
    features["risk_tier"] = pd.cut(
        features["risk_score"],
        bins=[-0.001, 0.25, 0.50, 0.75, 1.01],
        labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    )

    # Churn probability (simplified RFM-based)
    features["churn_probability"] = (
        (1 - (features["avg_daily_transactions"] / features["avg_daily_transactions"].max()).clip(0,1)) * 0.5
        + features["failed_transaction_rate"] * 0.3
        + (1 - features["total_volume"] / features["total_volume"].max()).clip(0,1) * 0.2
    ).clip(0, 1)

    print(f"   ✅ Customer features: {len(features)} customers")
    return features


def cluster_customers(features_df: pd.DataFrame) -> pd.DataFrame:
    """Apply K-Means and DBSCAN clustering."""
    print("\n🎯 Clustering customers...")
    CLUSTER_FEATURES = [
        "total_transactions", "avg_amount", "std_amount",
        "fraud_rate", "international_rate", "night_transaction_rate",
        "high_risk_cat_rate", "unique_merchants", "unique_devices",
        "days_active", "avg_daily_transactions", "churn_probability",
    ]

    df = features_df.copy()
    available = [f for f in CLUSTER_FEATURES if f in df.columns]
    X = df[available].fillna(0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means
    best_k, best_score = 4, -1
    for k in range(3, 8):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        if len(set(labels)) > 1:
            score = silhouette_score(X_scaled, labels, sample_size=min(1000, len(X_scaled)))
            if score > best_score:
                best_score, best_k = score, k

    print(f"   Best K={best_k} (silhouette={best_score:.3f})")
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df["kmeans_cluster"] = kmeans.fit_predict(X_scaled)

    # DBSCAN for anomaly detection
    dbscan = DBSCAN(eps=0.8, min_samples=5)
    db_labels = dbscan.fit_predict(X_scaled)
    df["is_anomaly_cluster"] = (db_labels == -1).astype(int)
    n_anomalies = (db_labels == -1).sum()
    print(f"   DBSCAN anomalies: {n_anomalies} ({n_anomalies/len(df):.1%})")

    # Label clusters by risk
    cluster_risk = df.groupby("kmeans_cluster")["risk_score"].mean().sort_values(ascending=False)
    risk_labels  = {c: l for c, l in zip(cluster_risk.index, ["CRITICAL","HIGH","MEDIUM","LOW"] + ["LOW"]*(best_k))}
    df["cluster_risk_label"] = df["kmeans_cluster"].map(risk_labels)

    # Save models
    joblib.dump(kmeans, os.path.join(MODEL_DIR, "customer_kmeans.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "customer_scaler.pkl"))
    joblib.dump(dbscan,  os.path.join(MODEL_DIR, "customer_dbscan.pkl"))
    print("   ✅ Clustering models saved")
    return df


def run_customer_scoring(data_path: str = None):
    """End-to-end customer risk scoring pipeline."""
    print("\n" + "="*60)
    print("   FinSentinel AI — Customer Risk Scoring Pipeline")
    print("="*60 + "\n")

    if data_path is None:
        data_path = os.path.join(DATA_DIR, "transactions_features.csv")

    if not os.path.exists(data_path):
        print(f"❌ Data not found at {data_path}")
        print("   Run: python generate_synthetic_transactions.py first")
        return

    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    customer_features = compute_customer_features(df)
    customer_features = cluster_customers(customer_features)

    output = os.path.join(DATA_DIR, "customer_risk_scores.csv")
    customer_features.to_csv(output, index=False)
    print(f"\n✅ Customer risk scores saved → {output}")

    print("\n📊 Risk Tier Distribution:")
    print(customer_features["risk_tier"].value_counts().to_string())
    return customer_features


if __name__ == "__main__":
    run_customer_scoring()
