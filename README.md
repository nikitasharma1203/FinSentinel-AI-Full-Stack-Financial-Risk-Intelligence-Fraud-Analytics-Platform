# FinSentinel AI
### Financial Risk Intelligence & Fraud Analytics Platform

[![Live Demo](https://img.shields.io/badge/Live-Demo-black?style=flat-square)](https://finsentinelai.netlify.app/overview)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square)](https://reactjs.org)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-FF6600?style=flat-square)](https://xgboost.readthedocs.io/)

Enterprise-grade fintech intelligence platform combining real-time fraud detection, behavioral risk scoring, explainable AI, financial network analysis, and forward-looking risk forecasting — built on a 500K+ transaction dataset.

---

## Overview

Financial fraud detection at production scale requires more than a single model. FinSentinel integrates five analytical layers — fraud prediction, anomaly detection, behavioral intelligence, network graph analysis, and time-series forecasting — into a unified risk intelligence platform with a compliance-ready explainability layer.

The platform is designed around the real operational constraints of financial risk systems: severe class imbalance, the high cost of false negatives, regulatory requirements for model explainability, and the need for sub-100ms inference at transaction time.

---

## Architecture

```
React Dashboard (Frontend)
        │
        ▼
FastAPI REST APIs
        │
   ┌────┴─────────────────────┐
   ▼                          ▼
Fraud ML Layer           Risk Engine
XGBoost (scoring)        K-Means + DBSCAN
Isolation Forest         Behavioral clustering
SHAP explainability      Churn-risk prediction
        │                    │
        └────────┬───────────┘
                 ▼
     PostgreSQL + Analytics Layer
                 │
         ┌───────┴────────┐
         ▼                ▼
  Forecast Engine    Network Layer
  Prophet / SARIMA   NetworkX + PyVis
  Stress simulation  Fraud ring detection
```

---

## ML Design Decisions

### Fraud Detection: Why XGBoost + Isolation Forest ensemble

The dataset carries approximately 1% fraud prevalence — a class imbalance severe enough to make accuracy meaningless as an evaluation metric. Two deliberate choices address this:

**Model selection:** XGBoost handles tabular financial features (transaction velocity, merchant category, time-of-day patterns) with strong performance on imbalanced data via `scale_pos_weight`. Isolation Forest runs in parallel as an unsupervised anomaly scorer, catching novel fraud patterns that fall outside the supervised model's training distribution. The ensemble flags a transaction when either model exceeds its calibrated threshold.

**Evaluation:** The platform uses AUC-PR (precision-recall curve area) as the primary metric, not AUC-ROC. At 1% fraud rate, a model predicting "no fraud" always achieves 99% accuracy and ~0.5 AUC-ROC — AUC-PR surfaces the real tradeoff between catching fraud and generating false positive alerts that create customer friction.

**Threshold calibration:** Rather than using the default 0.5 probability cutoff, thresholds are tuned against a cost matrix reflecting the asymmetric business cost of a missed fraud event vs. a wrongly blocked transaction.

### Explainability: SHAP for compliance

Every fraud flag surfaces a SHAP waterfall breakdown showing which features drove the prediction and by how much. This satisfies the practical compliance requirement that a risk officer must be able to explain and defend any declined transaction — a requirement that black-box neural networks cannot meet without significant additional tooling.

### Network Analysis: Fraud ring detection

Transactions are modeled as a graph where edges represent shared entities (device ID, IP address, merchant, card BIN). NetworkX centrality measures (betweenness, degree) identify nodes with anomalously high connectivity — a signal of synthetic identity fraud rings and account takeover networks. PyVis renders these interactively in the dashboard.

---

## Key Metrics

| Component | Metric | Value |
|---|---|---|
| Fraud detection | Precision | 94% |
| API inference | Latency | < 100ms |
| Dataset scale | Transactions | 500K+ |
| Anomaly detection | Method | Isolation Forest + IQR |
| Explainability | Engine | SHAP (per-prediction) |

---

## Dashboard Modules

| Module | Description |
|---|---|
| Executive Overview | Portfolio-wide risk KPIs and alert summary |
| Transaction Monitoring | Live fraud scoring and anomaly tracking |
| Fraud Analytics | Model predictions, threshold analysis, precision-recall curves |
| Customer Risk Intelligence | Behavioral segmentation, churn risk, spend pattern shifts |
| Network Intelligence | Fraud ring visualisation, entity relationship graphs |
| AI Explainability | SHAP contribution dashboards per flagged transaction |
| Scenario Simulator | Stress-testing under inflation, liquidity, and fraud-surge scenarios |
| Reports Centre | AI-generated executive risk summaries |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Tailwind CSS, Recharts, Framer Motion |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Fraud ML | XGBoost, Isolation Forest, Scikit-learn |
| Explainability | SHAP |
| Forecasting | Prophet, SARIMA |
| Network Analysis | NetworkX, PyVis |
| Authentication | Firebase Auth |
| Deployment | Netlify (frontend), Render (backend) |

---

## Repository Structure

```
finsentinel-ai/
├── frontend/                  # React 18 dashboard
├── backend/                   # FastAPI application
│   ├── main.py                # API entry point
│   ├── database/
│   │   └── schema.sql         # Core table definitions
│   └── routers/               # Fraud, risk, forecast, network endpoints
├── ml/
│   ├── pipelines/
│   │   ├── train_fraud_model.py
│   │   ├── train_anomaly_model.py
│   │   └── generate_risk_scores.py
│   └── notebooks/             # Exploratory analysis
├── data/                      # Raw and processed datasets
├── scripts/                   # ETL and external data ingestion
└── requirements.txt
```

---

## Local Setup

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload

# Frontend
cd frontend
npm install && cp .env.example .env.local
npm run dev

# ML pipelines
cd ml
python pipelines/train_fraud_model.py
python pipelines/train_anomaly_model.py
python pipelines/generate_risk_scores.py
```

---

*Built as part of an M.Sc. Data Science portfolio — DA-IICT Gandhinagar*
