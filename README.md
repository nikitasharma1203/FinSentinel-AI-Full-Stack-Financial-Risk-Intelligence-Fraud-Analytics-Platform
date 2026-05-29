# FinSentinel AI
### Financial Risk Intelligence & Fraud Analytics Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-finsentinelai.netlify.app-0D9488?style=flat-square&logo=netlify)](https://finsentinelai.netlify.app/overview)
[![Backend](https://img.shields.io/badge/API-onrender.com-7C3AED?style=flat-square&logo=render)](https://finsentinel-ai-full-stack-financial-risk.onrender.com/docs)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0-FF6600?style=flat-square)](https://xgboost.readthedocs.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](LICENSE)

---

Enterprise-grade fintech intelligence platform combining real-time fraud detection, behavioral risk scoring, explainable AI, financial network analysis, and geopolitical sentiment scoring — deployed full-stack with a production-grade React dashboard and FastAPI backend.

Built around the real operational constraints of financial risk systems: **severe class imbalance**, **sub-100ms inference requirements**, **regulatory explainability**, and **multi-source macroeconomic data integration**.

---

## Live Links

| Service | URL |
|---|---|
| Frontend Dashboard | https://finsentinelai.netlify.app/overview |
| Backend API | https://finsentinel-ai-full-stack-financial-risk.onrender.com |
| API Documentation | https://finsentinel-ai-full-stack-financial-risk.onrender.com/docs |

> The Render backend uses a free tier — first request after inactivity takes ~50s (cold start). Subsequent requests are fast.

---

## What This Project Is

Most fraud detection projects train a single model on Kaggle's credit card dataset and call it done. FinSentinel is built differently — it models the **full operational reality** of a fintech risk system:

- Fraud doesn't happen in isolation. It clusters around merchants, time windows, geographic anomalies, and shared device identifiers. The **network layer** surfaces these clusters.
- A single model misses novel attack patterns. The **Isolation Forest** runs alongside XGBoost to catch out-of-distribution transactions the supervised model hasn't seen before.
- Risk officers cannot approve or decline transactions without knowing why. Every prediction ships with a **SHAP explanation** that identifies contributing features and their magnitude.
- Macro conditions shift fraud rates. Rising inflation, currency depreciation, and liquidity shocks all correlate with fraud spikes. The **scenario simulator** stress-tests the portfolio under user-defined macro conditions.
- Customer risk isn't static. The **behavioral clustering** module tracks spend pattern shifts and risk migration across segments over time.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React 18 Dashboard (Netlify)                │
│  Executive · Transactions · Fraud · Customers · Network  │
│  Explainability · Scenario Simulator · Sentiment · Reports│
└────────────────────────┬────────────────────────────────┘
                         │ HTTPS / REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (Render)                    │
│                                                         │
│  /transactions  /fraud  /customers  /network            │
│  /scenarios     /explainability    /analytics           │
│  /sentiment     /reports                                │
└──────┬──────────────┬──────────────┬───────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌───────────────────────┐
│PostgreSQL│  │  ML Models   │  │   Data Pipeline       │
│(Render)  │  │  (pkl files) │  │                       │
│          │  │              │  │  USD/INR · RBI Macro  │
│transactions  XGBoost       │  │  Global Macro · VIX   │
│customers │  │IsolationForest  │  NIFTY · News NLP     │
│fraud_pred│  │SHAP          │  │  → master_dataset.csv │
│network   │  │K-Means       │  └───────────────────────┘
│macro_ind │  │DBSCAN        │
│scenarios │  └──────────────┘
└──────────┘
```

---

## ML Design

### Why XGBoost + Isolation Forest ensemble

The synthetic training dataset carries ~2.5% fraud prevalence — enough class imbalance to make accuracy a meaningless metric. Two deliberate model choices address this:

**XGBoost** handles tabular financial features (transaction velocity, merchant category risk, geographic deviation, time-of-day patterns) with strong performance on imbalanced data via `scale_pos_weight`. It's fast enough for sub-100ms inference and interpretable enough for SHAP.

**Isolation Forest** runs in parallel as an unsupervised anomaly scorer. It catches novel fraud patterns outside the supervised model's training distribution — the attack vectors XGBoost hasn't seen before. The ensemble flags a transaction when either model exceeds its calibrated threshold.

**Blending:** `final_score = 0.7 × XGBoost_prob + 0.3 × IsolationForest_normalized_score`

### Evaluation metric: AUC-PR, not AUC-ROC

At 2.5% fraud rate, a model that always predicts "not fraud" achieves 97.5% accuracy and misleadingly high AUC-ROC. AUC-PR (precision-recall area) surfaces the real tradeoff between catching fraud and generating false-positive alerts that create customer friction. This is the metric that matters in production.

### SHAP for compliance explainability

Every fraud flag generates a SHAP waterfall breakdown identifying which features drove the prediction and by how much. This satisfies the practical compliance requirement that a risk officer must be able to explain and defend any declined or flagged transaction to regulators — a requirement that black-box models cannot meet without significant additional tooling.

### Customer clustering: K-Means + DBSCAN

K-Means segments customers into behavioral cohorts (optimal K selected by silhouette score). DBSCAN identifies the ε-neighborhood outliers — customers whose transaction patterns don't fit any cluster, which are the highest-risk for account takeover. Each customer receives a composite risk score weighted across fraud history, international activity, night transaction rate, high-risk merchant exposure, and device switching frequency.

### Network fraud ring detection

Transactions are modeled as a directed graph where edges connect customers to merchants. NetworkX computes:
- **Betweenness centrality** — nodes on the most paths between other nodes (money mule indicators)
- **Degree centrality** — nodes with anomalously many connections (synthetic identity rings)
- **Connected components** — isolated suspicious clusters (coordinated fraud networks)

---

## Geopolitical & Macro Risk Integration

What separates FinSentinel from standard fraud detection projects is the **macro risk layer** — the recognition that fraud rates correlate with economic stress.

Five external data pipelines feed daily macro signals into the platform:

| Pipeline | Source | Signals |
|---|---|---|
| `fetch_usd_inr.py` | Yahoo Finance / FRED | USD/INR rate, MA, RSI, Bollinger, volatility |
| `fetch_rbi_indicators.py` | FRED India series | Repo rate, CPI, forex reserves, trade balance, M3 |
| `fetch_global_macro.py` | FRED + Yahoo Finance | Brent crude, DXY, gold, S&P 500, treasury yields, VIX |
| `fetch_market_data.py` | Yahoo Finance / NSE | NIFTY 50, Bank NIFTY, India VIX, FII/DII flows |
| `fetch_news_sentiment.py` | NewsAPI + VADER NLP | Per-topic sentiment, geopolitical risk score, shock events |

All five pipelines merge on date index via `run_etl_pipeline.py` into a unified `master_dataset.csv` with 60+ features per trading day.

The **Sentiment Dashboard** visualises these signals alongside labeled geopolitical shock events (Russia-Ukraine outbreak, Israel-Gaza war, COVID crash, Fed rate hikes) and their measured impact on INR and fraud rate.

---

## Dashboard Modules

| Module | What it shows |
|---|---|
| **Executive Overview** | 8 portfolio-wide KPIs, 30-day fraud trend chart, AI Copilot insight panel, live alert feed |
| **Transaction Monitor** | Live-updating transaction table (auto-refreshes every 5s), search/filter, probability bars per row |
| **Fraud Analytics** | Fraud by merchant category (bar), fraud by payment method, radar chart of risk vs probability |
| **Customer Risk** | Scatter risk map (volume vs risk score), risk tier distribution, high-risk customer table, detail panel |
| **Network Intelligence** | Interactive SVG transaction graph, animated pulse rings on critical nodes, fraud cluster detection |
| **AI Explainability** | SHAP feature importance chart, macro correlations, per-prediction waterfall breakdown |
| **Scenario Simulator** | 5-parameter stress test (inflation/surge/fraud spike/liquidity/recession), preset scenarios, live projection |
| **Sentiment & Macro** | NLP sentiment time series, topic breakdown, geopolitical shock event log |
| **Reports** | Report generation by type, saved report history, PDF download |

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | React | 18 |
| Styling | Tailwind CSS | 3.4 |
| Charts | Recharts | 2.12 |
| Animations | Framer Motion | 11 |
| Backend | FastAPI | 0.110 |
| ORM | SQLAlchemy | 2.0 |
| Database | PostgreSQL | 16 |
| Fraud ML | XGBoost | 2.0 |
| Anomaly detection | Scikit-learn (Isolation Forest) | 1.4 |
| Explainability | SHAP | 0.45 |
| Clustering | Scikit-learn (K-Means, DBSCAN) | 1.4 |
| Forecasting | Prophet, statsmodels (SARIMA) | — |
| Network analysis | NetworkX | 3.3 |
| NLP sentiment | VADER (vaderSentiment) | — |
| Deployment — Frontend | Netlify | — |
| Deployment — Backend | Render | — |

---

## Repository Structure

```
finsentinel-ai/
│
├── frontend/                          # React 18 dashboard
│   ├── src/
│   │   ├── App.jsx                    # Router — 9 page routes
│   │   ├── components/
│   │   │   └── dashboard/
│   │   │       ├── Sidebar.jsx        # Collapsible navigation
│   │   │       ├── Header.jsx         # Live clock, search, alerts
│   │   │       ├── KPICard.jsx        # Reusable metric card
│   │   │       └── UIElements.jsx     # RiskBadge, ProbabilityBar, TabGroup…
│   │   ├── pages/
│   │   │   ├── ExecutiveOverview.jsx  # KPIs + trends + Copilot
│   │   │   ├── TransactionMonitor.jsx # Live table + filters
│   │   │   ├── FraudAnalytics.jsx     # Category/payment/radar charts
│   │   │   ├── CustomerRisk.jsx       # Scatter map + cluster table
│   │   │   ├── NetworkIntelligence.jsx# SVG fraud graph + clusters
│   │   │   ├── Explainability.jsx     # SHAP charts + correlations
│   │   │   ├── ScenarioSimulator.jsx  # Stress test engine
│   │   │   ├── SentimentDashboard.jsx # NLP sentiment + macro
│   │   │   └── Reports.jsx            # Report generation
│   │   └── services/
│   │       ├── api.js                 # All backend API calls
│   │       └── mockData.js            # Demo data for UI development
│   ├── public/
│   │   └── _redirects                 # Netlify SPA routing fix
│   └── package.json
│
├── backend/                           # FastAPI application
│   ├── main.py                        # App entry point + route registration
│   ├── core/
│   │   └── config.py                  # Pydantic settings from .env
│   ├── database/
│   │   ├── connection.py              # SQLAlchemy engine + get_db()
│   │   └── schema.sql                 # All 7 table definitions
│   ├── models/
│   │   └── orm_models.py              # SQLAlchemy ORM classes
│   ├── api/routes/
│   │   ├── transactions.py            # KPIs, trends, pagination
│   │   ├── fraud.py                   # Scoring, alerts, heatmap
│   │   ├── customers.py               # Risk tiers, profiles
│   │   ├── network.py                 # Graph, centrality, clusters
│   │   ├── scenarios.py               # Stress simulation engine
│   │   ├── explainability.py          # SHAP values, feature importance
│   │   ├── analytics.py               # Macro data, correlations, Copilot
│   │   ├── sentiment.py               # NLP scores, topics, shocks
│   │   └── reports.py                 # Generate + download PDFs
│   ├── services/
│   │   └── fraud_scorer.py            # ML inference + heuristic fallback
│   ├── requirements.txt
│   └── Dockerfile
│
├── ml/                                # Machine learning pipelines
│   ├── pipelines/
│   │   ├── generate_synthetic_transactions.py  # 200K transaction generator
│   │   ├── train_fraud_model.py                # XGBoost + IsoForest + SHAP
│   │   └── generate_risk_scores.py             # Customer clustering pipeline
│   └── models/                        # Saved .pkl files (generated on training)
│
├── data/
│   ├── raw/                           # Output from fetch scripts
│   └── processed/                     # master_dataset.csv + merged features
│
├── scripts/                           # External data ingestion
│   ├── fetch_usd_inr.py               # Yahoo Finance / FRED / synthetic
│   ├── fetch_rbi_indicators.py        # RBI macro via FRED India series
│   ├── fetch_global_macro.py          # Oil, DXY, gold, yields, VIX
│   ├── fetch_market_data.py           # NIFTY, Bank NIFTY, India VIX
│   ├── fetch_news_sentiment.py        # NewsAPI + VADER NLP pipeline
│   └── run_etl_pipeline.py            # Master merge → master_dataset.csv
│
├── docker-compose.yml                 # Postgres + Redis + Backend + Frontend
├── setup.sh                           # One-command full local setup
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16 (or use Docker)

### One-command setup
```bash
git clone https://github.com/nikitasharma1203/FinSentinel-AI-Full-Stack-Financial-Risk-Intelligence-Fraud-Analytics-Platform
cd FinSentinel-AI-Full-Stack-Financial-Risk-Intelligence-Fraud-Analytics-Platform
chmod +x setup.sh && ./setup.sh
```

### Manual setup

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # Fill in your DB credentials
uvicorn main:app --reload
# → API running at http://localhost:8000
# → Docs at http://localhost:8000/docs
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env.local                         # Set VITE_API_URL=http://localhost:8000
npm run dev
# → Dashboard at http://localhost:3000
```

**ML pipelines** (run once to train models)
```bash
cd ml
python pipelines/generate_synthetic_transactions.py    # Creates 200K transaction dataset
python pipelines/train_fraud_model.py                  # Trains XGBoost + IsoForest, saves .pkl
python pipelines/generate_risk_scores.py               # Clusters customers, assigns risk tiers
```

**Data pipelines** (optional — for macro dashboard)
```bash
cd scripts
# Add FRED_API_KEY and NEWS_API_KEY to backend/.env first
python fetch_usd_inr.py
python fetch_rbi_indicators.py
python fetch_global_macro.py
python fetch_market_data.py
python fetch_news_sentiment.py
python run_etl_pipeline.py                             # Merges all into master_dataset.csv
```

### Docker (all services at once)
```bash
docker-compose up
# → Frontend: http://localhost:3000
# → Backend:  http://localhost:8000
# → Postgres: localhost:5432
```

---

## Environment Variables

**Backend `.env`**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/finsentinel
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=["http://localhost:3000","https://finsentinelai.netlify.app"]
FRED_API_KEY=your_fred_api_key           # https://fred.stlouisfed.org/docs/api
NEWS_API_KEY=your_newsapi_key            # https://newsapi.org
```

**Frontend `.env.local`**

```env
VITE_API_URL=http://localhost:8000       # or your Render URL for production
```

---

## Deployment

**Frontend → Netlify**

1. Push repo to GitHub
2. Connect repo on [netlify.com](https://netlify.com)
3. Build command: `npm run build` | Publish directory: `dist` | Base directory: `frontend`
4. Add environment variable: `VITE_API_URL=https://your-render-backend.onrender.com`
5. Ensure `frontend/public/_redirects` contains `/*    /index.html   200`

**Backend → Render**

1. New Web Service → connect GitHub repo
2. Environment: Docker | Root Directory: `backend`
3. Add all variables from `.env` in Render's Environment tab
4. Create a free Postgres instance in Render and copy its connection string to `DATABASE_URL`

---

## API Reference

Full interactive docs at `/docs` (Swagger UI) when the backend is running.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/transactions/kpis` | Portfolio KPIs (volume, fraud rate, exposure) |
| GET | `/api/v1/transactions/trends` | Daily transaction + fraud trend series |
| GET | `/api/v1/transactions/` | Paginated transaction list with filters |
| POST | `/api/v1/fraud/score` | Score a single transaction for fraud probability |
| GET | `/api/v1/fraud/alerts` | Recent high-probability fraud alerts |
| GET | `/api/v1/fraud/heatmap` | Fraud breakdown by merchant category |
| GET | `/api/v1/customers/` | Customer list filtered by risk tier / segment |
| GET | `/api/v1/customers/risk-distribution` | Customer count per risk tier |
| GET | `/api/v1/network/graph` | Transaction network nodes and edges |
| GET | `/api/v1/network/clusters` | Detected fraud ring clusters |
| GET | `/api/v1/network/centrality` | Top nodes by betweenness + degree centrality |
| POST | `/api/v1/scenarios/run` | Run a stress simulation with custom parameters |
| GET | `/api/v1/explainability/feature-importance/global` | Global SHAP feature importance |
| GET | `/api/v1/analytics/copilot-insights` | AI-generated analyst insight summaries |
| GET | `/api/v1/sentiment/latest` | NLP sentiment time series |
| GET | `/api/v1/sentiment/event-shocks` | Geopolitical shock event log |
| POST | `/api/v1/reports/generate` | Trigger PDF report generation |

---

## Key Design Decisions

**AUC-PR over AUC-ROC** — At low fraud prevalence, AUC-ROC is misleading. A model predicting "no fraud" always achieves near-perfect AUC-ROC. Precision-recall curves surface the real cost tradeoff between missed fraud and false positives.

**Threshold calibration via cost matrix** — The default 0.5 probability cutoff is wrong for fraud detection. Thresholds are tuned against an asymmetric cost matrix where a missed fraud event costs 10–50× more than a false positive alert.

**SHAP for regulatory compliance** — Neural networks would likely outperform XGBoost on raw AUC. But a risk officer who cannot explain why a transaction was declined cannot use a neural network in a regulated context. XGBoost + SHAP is the production-realistic choice.

**Fallback heuristic scoring** — When ML model files aren't available (fresh deployment, first boot), the fraud scorer falls back to a rule-based heuristic. The API never returns errors — it degrades gracefully.

**Mock data decoupled from API calls** — The frontend's `mockData.js` is a separate layer from `api.js`. Switching from demo mode to live backend requires changing one line per page — not restructuring components.

---

## Dataset

| Source | Description | Features |
|---|---|---|
| Synthetic generator | 200K transactions, 2.5% fraud rate, realistic patterns | 20 raw + 14 engineered |
| FRED (via fredapi) | US macro: fed rate, CPI, treasury yields, VIX | Daily, 2010–present |
| FRED India series | RBI macro: repo rate, forex reserves, trade balance | Monthly → interpolated daily |
| Yahoo Finance | NIFTY 50, Bank NIFTY, India VIX, S&P 500, crude oil, gold | Daily |
| NewsAPI + VADER | Financial news sentiment across 10 India-focused topics | Daily aggregated scores |

All datasets fall back to synthetic generation if API keys are not configured — the platform runs fully offline for development.

---

## Project Status

| Component | Status |
|---|---|
| React frontend (9 pages) | ✅ Deployed — Netlify |
| FastAPI backend (9 route groups) | ✅ Deployed — Render |
| PostgreSQL database | ✅ Live — Render Postgres |
| ML model training pipeline | ✅ Code complete — models need training run |
| Data ingestion pipelines | ✅ Code complete — requires API keys |
| Frontend ↔ backend live data | 🔄 Frontend uses mock data — switchover ready |
| PDF report generation | 🔄 Endpoint scaffolded — Celery task pending |

---
