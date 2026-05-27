"""
FinSentinel AI — Fraud Detection Model Training Pipeline
Models: XGBoost + Isolation Forest + SHAP
"""

import os
import sys
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    classification_report, roc_auc_score, average_precision_score,
    confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
import shap
import warnings

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "..", "data", "processed")
MODEL_DIR   = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


# ── Feature Engineering ───────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features for fraud detection."""
    print("🔧 Engineering features...")
    df = df.copy()

    # Time features
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"]       = df["timestamp"].dt.hour
    df["day_of_week"]= df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_night"]   = ((df["hour"] < 6) | (df["hour"] > 22)).astype(int)
    df["month"]      = df["timestamp"].dt.month

    # Amount features
    df["log_amount"] = np.log1p(df["amount"])
    df.sort_values(["customer_id", "timestamp"], inplace=True)

    # Rolling customer stats
    df["customer_avg_amount"] = (
        df.groupby("customer_id")["amount"]
        .transform(lambda x: x.expanding().mean().shift(1))
        .fillna(df["amount"])
    )
    df["amount_deviation"] = (
        (df["amount"] - df["customer_avg_amount"]) /
        (df["customer_avg_amount"].replace(0, 1))
    )

    # Velocity features
    df["txn_count_1h"] = (
        df.groupby("customer_id")["timestamp"]
        .transform(lambda x: x.expanding().count().shift(1))
        .fillna(0)
        .clip(upper=50)
    )

    # Time since last transaction
    df["time_since_last_txn_min"] = (
        df.groupby("customer_id")["timestamp"]
        .transform(lambda x: x.diff().dt.total_seconds() / 60)
        .fillna(60)
        .clip(upper=10080)  # Cap at 1 week
    )

    # Device & location
    df["is_international"] = df.get("is_international", pd.Series(0, index=df.index)).fillna(0).astype(int)

    # Merchant category encoding
    if "merchant_category" in df.columns:
        high_risk_cats = ["CRYPTO", "GAMBLING", "FOREIGN_EXCHANGE", "WIRE_TRANSFER", "MONEY_ORDER"]
        df["is_high_risk_category"] = df["merchant_category"].isin(high_risk_cats).astype(int)
        le = LabelEncoder()
        df["merchant_category_enc"] = le.fit_transform(df["merchant_category"].fillna("UNKNOWN"))
    else:
        df["is_high_risk_category"] = 0
        df["merchant_category_enc"] = 0

    # Payment method risk
    high_risk_payment = ["CRYPTO_WALLET", "WIRE"]
    if "payment_method" in df.columns:
        df["is_high_risk_payment"] = df["payment_method"].isin(high_risk_payment).astype(int)
        le2 = LabelEncoder()
        df["payment_method_enc"] = le2.fit_transform(df["payment_method"].fillna("UNKNOWN"))
    else:
        df["is_high_risk_payment"] = 0
        df["payment_method_enc"] = 0

    print(f"   ✅ Features: {df.shape[1]} columns")
    return df


FEATURE_COLS = [
    "log_amount", "amount_deviation", "hour", "day_of_week",
    "is_weekend", "is_night", "month", "txn_count_1h",
    "time_since_last_txn_min", "is_international",
    "is_high_risk_category", "merchant_category_enc",
    "is_high_risk_payment", "payment_method_enc",
]


# ── Training ──────────────────────────────────────────────────────────────────
def train(data_path: str = None):
    print("\n" + "="*60)
    print("   FinSentinel AI — Fraud Model Training Pipeline")
    print("="*60 + "\n")

    # Load data
    if data_path is None:
        data_path = os.path.join(DATA_DIR, "transactions_features.csv")

    if not os.path.exists(data_path):
        print("⚠️  No processed data found. Generating synthetic data...")
        from generate_synthetic_transactions import generate_and_save
        df = generate_and_save()
        df = engineer_features(df)
    else:
        print(f"📂 Loading data from: {data_path}")
        df = pd.read_csv(data_path, parse_dates=["timestamp"])
        df = engineer_features(df)

    # Validate features
    available_features = [f for f in FEATURE_COLS if f in df.columns]
    X = df[available_features].fillna(0)
    y = df["fraud_label"].astype(int)

    print(f"\n📊 Dataset: {len(df):,} transactions | Fraud rate: {y.mean():.2%}")
    print(f"   Features: {len(available_features)}")
    print(f"   Fraud: {y.sum():,} | Legit: {(y==0).sum():,}\n")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # ── XGBoost Classifier ────────────────────────────────────────────────────
    print("🚀 Training XGBoost fraud classifier...")
    scale_pos_weight = (y == 0).sum() / max((y == 1).sum(), 1)

    xgb = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric="aucpr",
        random_state=42,
        n_jobs=-1,
    )
    xgb.fit(
        X_train_scaled, y_train,
        eval_set=[(X_test_scaled, y_test)],
        verbose=50,
    )

    y_pred      = xgb.predict(X_test_scaled)
    y_prob      = xgb.predict_proba(X_test_scaled)[:, 1]
    auc_roc     = roc_auc_score(y_test, y_prob)
    auc_pr      = average_precision_score(y_test, y_prob)
    f1          = f1_score(y_test, y_pred)
    precision   = precision_score(y_test, y_pred)
    recall      = recall_score(y_test, y_pred)

    print(f"\n   📈 XGBoost Results:")
    print(f"      AUC-ROC:   {auc_roc:.4f}")
    print(f"      AUC-PR:    {auc_pr:.4f}")
    print(f"      F1:        {f1:.4f}")
    print(f"      Precision: {precision:.4f}")
    print(f"      Recall:    {recall:.4f}")
    print("\n" + classification_report(y_test, y_pred, target_names=["Legit", "Fraud"]))

    # ── Isolation Forest ──────────────────────────────────────────────────────
    print("🌲 Training Isolation Forest anomaly detector...")
    iso = IsolationForest(
        n_estimators=200,
        contamination=float(y.mean()),
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X_train_scaled)
    iso_scores = iso.score_samples(X_test_scaled)
    print(f"   Isolation Forest trained. Mean score: {iso_scores.mean():.4f}")

    # ── SHAP Explainability ───────────────────────────────────────────────────
    print("\n🔍 Computing SHAP values for explainability...")
    background = shap.sample(X_train_scaled, 100)
    explainer  = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X_test_scaled[:200])

    feature_importance = dict(zip(
        available_features,
        np.abs(shap_values).mean(axis=0).tolist()
    ))
    sorted_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    print("\n   Top SHAP Features:")
    for feat, imp in sorted_importance[:10]:
        print(f"      {feat:<35} {imp:.4f}")

    # ── Save Artifacts ────────────────────────────────────────────────────────
    print("\n💾 Saving model artifacts...")
    joblib.dump(xgb,              os.path.join(MODEL_DIR, "xgb_fraud_classifier.pkl"))
    joblib.dump(iso,              os.path.join(MODEL_DIR, "isolation_forest.pkl"))
    joblib.dump(scaler,           os.path.join(MODEL_DIR, "feature_scaler.pkl"))
    joblib.dump(available_features, os.path.join(MODEL_DIR, "feature_columns.pkl"))

    metrics = {
        "trained_at":   datetime.utcnow().isoformat(),
        "model":        "XGBoost + IsolationForest",
        "version":      "1.0.0",
        "dataset_size": len(df),
        "fraud_rate":   float(y.mean()),
        "features":     available_features,
        "metrics": {
            "auc_roc":   round(auc_roc, 4),
            "auc_pr":    round(auc_pr, 4),
            "f1":        round(f1, 4),
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
        },
        "feature_importance": dict(sorted_importance),
    }
    with open(os.path.join(MODEL_DIR, "model_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n✅ All artifacts saved to: {MODEL_DIR}")
    print("="*60)
    return metrics


if __name__ == "__main__":
    data_path = sys.argv[1] if len(sys.argv) > 1 else None
    train(data_path)
