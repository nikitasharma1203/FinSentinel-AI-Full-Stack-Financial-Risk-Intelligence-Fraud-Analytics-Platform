#!/bin/bash
# FinSentinel AI — Master Setup & Run Script
set -e

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         🛡️  FinSentinel AI Setup              ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() { echo -e "\n${CYAN}▶ $1${NC}"; }
ok()   { echo -e "${GREEN}  ✓ $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠ $1${NC}"; }

# ── Backend ────────────────────────────────────────────────────────────────
step "Setting up Python backend..."
cd backend
python -m venv venv 2>/dev/null || true
source venv/bin/activate

pip install -q --upgrade pip
pip install -q -r requirements.txt
ok "Python dependencies installed"

if [ ! -f .env ]; then
  cp .env.example .env
  warn ".env created from example — fill in your API keys"
fi

cd ..

# ── ML Pipeline ───────────────────────────────────────────────────────────
step "Running ML pipeline..."
cd ml
python pipelines/generate_synthetic_transactions.py 50000
ok "Synthetic transactions generated"
python pipelines/train_fraud_model.py
ok "Fraud model trained"
python pipelines/generate_risk_scores.py
ok "Customer risk scores computed"
cd ..

# ── Data Scripts ──────────────────────────────────────────────────────────
step "Fetching datasets..."
cd scripts
python fetch_usd_inr.py &
python fetch_rbi_indicators.py &
python fetch_global_macro.py &
python fetch_market_data.py &
wait
python fetch_news_sentiment.py
python run_etl_pipeline.py
ok "All datasets fetched and merged"
cd ..

# ── Frontend ──────────────────────────────────────────────────────────────
step "Setting up React frontend..."
cd frontend
npm install --silent
if [ ! -f .env.local ]; then
  cp .env.example .env.local
  ok ".env.local created"
fi
cd ..

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      ✅  Setup Complete — Start Commands      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo "  Backend:   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "  Frontend:  cd frontend && npm run dev"
echo "  Docker:    docker-compose up"
echo ""
echo "  API Docs:  http://localhost:8000/docs"
echo "  Dashboard: http://localhost:3000"
echo ""
