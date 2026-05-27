# 🛡️ FinSentinel AI

**Full-Stack Financial Risk Intelligence & Fraud Analytics Platform**

> Enterprise-grade fintech intelligence platform combining fraud detection, transaction anomaly analytics, customer risk scoring, behavioral financial intelligence, and explainable AI.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, Recharts, Framer Motion |
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| ML | XGBoost, Scikit-Learn, SHAP, Isolation Forest |
| Graphs | NetworkX, PyVis |
| Forecasting | Prophet, SARIMA |
| Auth | Firebase Auth |
| Deployment | Vercel (FE), Render (BE) |

---

## 📦 Project Structure

```
finsentinel-ai/
├── frontend/          # React dashboard
├── backend/           # FastAPI server
├── ml/                # ML pipelines & notebooks
├── data/              # Datasets (raw/processed/synthetic)
├── scripts/           # Data collection & ETL scripts
└── reports/           # Generated PDF reports
```

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourname/finsentinel-ai
cd finsentinel-ai
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your DB credentials
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local  # Fill in API URL
npm run dev
```

### 4. ML Pipeline

```bash
cd ml
python pipelines/train_fraud_model.py
python pipelines/train_anomaly_model.py
python pipelines/generate_risk_scores.py
```

### 5. Data Collection

```bash
cd scripts
python fetch_usd_inr.py          # USD/INR historical data
python fetch_rbi_indicators.py   # RBI macro indicators
python fetch_global_macro.py     # Oil, DXY, Gold, etc.
python fetch_market_data.py      # NIFTY, VIX, S&P500
python fetch_news_sentiment.py   # Geopolitical NLP scoring
python generate_synthetic_txns.py # Synthetic transaction data
```

---

## 🧠 Core Modules

### Module 1 — Transaction Intelligence Engine
- Real-time fraud probability scoring
- Velocity anomaly detection
- Merchant & geo risk analysis

### Module 2 — Behavioral Risk Analytics
- Customer spending pattern clustering
- Risk migration & churn-risk scoring
- K-Means, DBSCAN, Isolation Forest

### Module 3 — Explainable AI Engine
- SHAP feature contribution visualizations
- "Why was this flagged?" reasoning panel
- Confidence scoring per prediction

### Module 4 — Financial Network Intelligence
- Transaction relationship graphs
- Fraud ring detection with centrality analysis
- NetworkX + PyVis interactive visualization

### Module 5 — Scenario Simulation Engine
- Simulate: inflation spikes, fraud surges, liquidity stress
- Dynamic risk recomputation

### Module 6 — Analyst Copilot
- AI-generated insight summaries
- Trend detection & alert generation

---

## 📊 Dashboard Pages

1. Executive Overview
2. Transaction Monitoring
3. Fraud Analytics
4. Customer Risk Intelligence
5. Network Intelligence
6. AI Explainability
7. Scenario Simulator
8. My Reports

---

## 🗄️ Database Schema

See `backend/database/schema.sql` for full schema.

Core tables: `transactions`, `customers`, `fraud_predictions`, `reports`, `merchant_risk`, `network_edges`

---

## 📄 License

MIT License — For educational/portfolio use.
