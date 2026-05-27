-- FinSentinel AI — PostgreSQL Schema
-- Run: psql -U user -d finsentinel -f schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────
-- CUSTOMERS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS customers (
    customer_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20),
    country         VARCHAR(100) DEFAULT 'India',
    risk_score      FLOAT DEFAULT 0.0,        -- 0..1
    risk_tier       VARCHAR(20) DEFAULT 'LOW', -- LOW/MEDIUM/HIGH/CRITICAL
    customer_segment VARCHAR(50),              -- e.g. RETAIL, HNI, SME
    churn_probability FLOAT DEFAULT 0.0,
    total_transactions INT DEFAULT 0,
    total_volume    FLOAT DEFAULT 0.0,
    avg_transaction_amount FLOAT DEFAULT 0.0,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- MERCHANTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255),
    category        VARCHAR(100),              -- MCC category
    country         VARCHAR(100),
    risk_score      FLOAT DEFAULT 0.0,
    fraud_rate      FLOAT DEFAULT 0.0,
    total_volume    FLOAT DEFAULT 0.0,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- TRANSACTIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id     UUID REFERENCES customers(customer_id),
    merchant_id     UUID REFERENCES merchants(merchant_id),
    amount          FLOAT NOT NULL,
    currency        VARCHAR(10) DEFAULT 'INR',
    timestamp       TIMESTAMP NOT NULL,
    location_lat    FLOAT,
    location_lon    FLOAT,
    location_city   VARCHAR(100),
    location_country VARCHAR(100),
    device_id       VARCHAR(255),
    device_type     VARCHAR(50),               -- MOBILE/WEB/ATM/POS
    ip_address      VARCHAR(45),
    merchant_category VARCHAR(100),
    payment_method  VARCHAR(50),               -- UPI/CARD/NETBANKING/WALLET
    is_international BOOLEAN DEFAULT FALSE,
    fraud_label     BOOLEAN DEFAULT FALSE,     -- Ground truth
    status          VARCHAR(20) DEFAULT 'COMPLETED', -- COMPLETED/FAILED/REVERSED
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- FRAUD PREDICTIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fraud_predictions (
    prediction_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id  UUID REFERENCES transactions(transaction_id),
    fraud_probability FLOAT NOT NULL,
    anomaly_score   FLOAT,
    risk_level      VARCHAR(20),               -- LOW/MEDIUM/HIGH/CRITICAL
    model_version   VARCHAR(50),
    model_name      VARCHAR(100),
    shap_values     JSONB,                     -- Feature contributions
    top_features    JSONB,                     -- Top N contributing features
    explanation     TEXT,                      -- Human-readable reason
    flagged         BOOLEAN DEFAULT FALSE,
    reviewed        BOOLEAN DEFAULT FALSE,
    reviewer_id     UUID,
    review_outcome  VARCHAR(20),               -- CONFIRMED_FRAUD/FALSE_POSITIVE
    predicted_at    TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- NETWORK EDGES (Transaction Graph)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS network_edges (
    edge_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id       UUID NOT NULL,             -- customer or merchant
    target_id       UUID NOT NULL,
    source_type     VARCHAR(20),               -- CUSTOMER/MERCHANT
    target_type     VARCHAR(20),
    transaction_count INT DEFAULT 1,
    total_amount    FLOAT DEFAULT 0.0,
    risk_score      FLOAT DEFAULT 0.0,
    is_suspicious   BOOLEAN DEFAULT FALSE,
    first_seen      TIMESTAMP,
    last_seen       TIMESTAMP
);

-- ─────────────────────────────────────────
-- MACRO INDICATORS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS macro_indicators (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    usd_inr         FLOAT,
    repo_rate       FLOAT,
    reverse_repo    FLOAT,
    cpi_inflation   FLOAT,
    forex_reserves  FLOAT,                     -- USD Billions
    current_account_deficit FLOAT,
    trade_balance   FLOAT,
    money_supply_m3 FLOAT,
    crude_oil_brent FLOAT,
    us_fed_rate     FLOAT,
    dxy             FLOAT,
    gold_price      FLOAT,
    us_cpi          FLOAT,
    treasury_yield_10y FLOAT,
    nifty50         FLOAT,
    india_vix       FLOAT,
    sp500           FLOAT,
    bank_nifty      FLOAT,
    fii_flow        FLOAT,
    dii_flow        FLOAT,
    geopolitical_risk_score FLOAT,
    news_sentiment_score FLOAT,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(date)
);

-- ─────────────────────────────────────────
-- REPORTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reports (
    report_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         VARCHAR(255),
    title           VARCHAR(500),
    report_type     VARCHAR(50),               -- FRAUD/CUSTOMER/NETWORK/SCENARIO
    parameters      JSONB,
    file_path       VARCHAR(500),
    generated_at    TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- SCENARIO SIMULATIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scenario_simulations (
    simulation_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         VARCHAR(255),
    scenario_name   VARCHAR(255),
    parameters      JSONB NOT NULL,            -- inflation%, fraud_surge%, etc.
    results         JSONB NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_transactions_customer   ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant   ON transactions(merchant_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp  ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud      ON transactions(fraud_label);
CREATE INDEX IF NOT EXISTS idx_fraud_pred_transaction  ON fraud_predictions(transaction_id);
CREATE INDEX IF NOT EXISTS idx_fraud_pred_flagged      ON fraud_predictions(flagged);
CREATE INDEX IF NOT EXISTS idx_macro_date              ON macro_indicators(date);
CREATE INDEX IF NOT EXISTS idx_network_source          ON network_edges(source_id);
CREATE INDEX IF NOT EXISTS idx_network_target          ON network_edges(target_id);
