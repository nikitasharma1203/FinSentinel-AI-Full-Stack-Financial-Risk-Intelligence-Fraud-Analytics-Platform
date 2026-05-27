# 🛡️ FinSentinel AI

<img src="https://img.shields.io/badge/Deployment-Netlify%20%7C%20Render-black?style=for-the-badge" />

### Full-Stack Financial Risk Intelligence & Fraud Analytics Platform

> Enterprise-grade fintech intelligence platform combining fraud detection, anomaly analytics, behavioral risk intelligence, explainable AI, forecasting, and financial network analysis.

---

# 🔗 Live Demo

### 🌐 Frontend  
https://finsentinelai.netlify.app/overview

---

# ✨ Features

## 🔍 Real-Time Fraud Intelligence
- Fraud probability scoring using XGBoost
- Velocity anomaly detection
- Merchant & geo-risk monitoring
- Isolation Forest anomaly detection

---

## 👤 Behavioral Financial Intelligence
- Customer segmentation using clustering
- Spending pattern analysis
- Churn-risk prediction
- Risk migration tracking

---

## 🧠 Explainable AI Engine
- SHAP-based feature contribution analysis
- Prediction confidence scoring
- “Why was this transaction flagged?” insights
- Transparent model interpretation

---

## 🌐 Financial Network Intelligence
- Fraud ring detection
- Transaction relationship mapping
- Centrality-based suspicious entity detection
- Interactive graph visualizations using PyVis + NetworkX

---

## 📈 Forecasting & Scenario Simulation
- Inflation and liquidity stress simulations
- Fraud surge modeling
- Prophet & SARIMA forecasting
- Dynamic portfolio risk recomputation

---

## 🤖 Analyst Copilot
- AI-generated insight summaries
- Automated trend detection
- Risk alert generation
- Executive-level reporting assistance

---

# 🏗️ Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, Tailwind CSS, Recharts, Framer Motion |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| Machine Learning | XGBoost, Scikit-Learn, SHAP, Isolation Forest |
| Forecasting | Prophet, SARIMA |
| Graph Analytics | NetworkX, PyVis |
| Authentication | Firebase Auth |
| Deployment | Netlify, Render |
| Data Processing | Pandas, NumPy |

---

# 📂 Project Structure

```bash
finsentinel-ai/
│
├── frontend/                  # React dashboard
├── backend/                   # FastAPI backend
├── ml/                        # ML pipelines & notebooks
├── data/                      # Raw & processed datasets
├── scripts/                   # ETL and data collection scripts
├── reports/                   # Generated reports
│
├── README.md
└── requirements.txt
```

---

# ⚙️ System Architecture

```text
User Dashboard (React)
        │
        ▼
 FastAPI Backend APIs
        │
 ┌───────────────┬────────────────┬────────────────┐
 ▼               ▼                ▼
Fraud ML     Risk Engine     Forecast Engine
(XGBoost)    (Clustering)    (Prophet/SARIMA)
        │
        ▼
 PostgreSQL + Analytics Layer
        │
        ▼
 Interactive Insights & Reports
```

---

# 🚀 Quick Start

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourname/finsentinel-ai.git
cd finsentinel-ai
```

---

## 2️⃣ Backend Setup

```bash
cd backend

python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

uvicorn main:app --reload
```

---

## 3️⃣ Frontend Setup

```bash
cd frontend

npm install

cp .env.example .env.local

npm run dev
```

---

## 4️⃣ ML Pipeline

```bash
cd ml

python pipelines/train_fraud_model.py
python pipelines/train_anomaly_model.py
python pipelines/generate_risk_scores.py
```

---

## 5️⃣ Data Collection Scripts

```bash
cd scripts

python fetch_usd_inr.py
python fetch_rbi_indicators.py
python fetch_global_macro.py
python fetch_market_data.py
python fetch_news_sentiment.py
python generate_synthetic_txns.py
```

---

# 📊 Core Dashboard Modules

| Module | Description |
|---|---|
| Executive Overview | Portfolio-wide financial intelligence |
| Transaction Monitoring | Live fraud & anomaly tracking |
| Fraud Analytics | Fraud scoring and detection insights |
| Customer Risk Intelligence | Behavioral risk segmentation |
| Network Intelligence | Fraud ring & transaction graph analysis |
| AI Explainability | SHAP explainability dashboards |
| Scenario Simulator | Stress-testing & forecasting |
| Reports Center | Downloadable AI-generated reports |

---

# 🗄️ Database Design

Core tables:

```text
transactions
customers
fraud_predictions
merchant_risk
network_edges
reports
risk_scores
```

See:

```bash
backend/database/schema.sql
```

---

# 📈 ML Models Used

| Model | Purpose |
|---|---|
| XGBoost | Fraud prediction |
| Isolation Forest | Anomaly detection |
| K-Means | Customer segmentation |
| DBSCAN | Behavioral clustering |
| Prophet | Time-series forecasting |
| SARIMA | Financial trend modeling |

---

# 🔐 Authentication

- Firebase Authentication
- Protected dashboard routes
- Session-based access management

---

# 📦 Deployment

| Service | Platform |
|---|---|
| Frontend | Netlify |
| Backend APIs | Render |
| Database | PostgreSQL |
| Authentication | Firebase |

---

# 🧪 Future Enhancements

- Kafka real-time streaming
- LLM-powered fraud investigation assistant
- Graph Neural Networks (GNNs)
- Real-time transaction ingestion
- Multi-tenant enterprise support
- PDF intelligence reporting

---
