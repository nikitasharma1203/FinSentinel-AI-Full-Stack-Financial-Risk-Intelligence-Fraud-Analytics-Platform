"""
FinSentinel AI — FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

from database.connection import engine, Base
from api.routes import (
    transactions,
    fraud,
    customers,
    network,
    scenarios,
    explainability,
    reports,
    analytics,
    sentiment,
)
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FinSentinel AI",
    description="Full-Stack Financial Risk Intelligence & Fraud Analytics Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("🛡️  FinSentinel AI starting up...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅  Database tables ready")


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(transactions.router,   prefix="/api/v1/transactions",   tags=["Transactions"])
app.include_router(fraud.router,          prefix="/api/v1/fraud",           tags=["Fraud"])
app.include_router(customers.router,      prefix="/api/v1/customers",       tags=["Customers"])
app.include_router(network.router,        prefix="/api/v1/network",         tags=["Network"])
app.include_router(scenarios.router,      prefix="/api/v1/scenarios",       tags=["Scenarios"])
app.include_router(explainability.router, prefix="/api/v1/explainability",  tags=["Explainability"])
app.include_router(reports.router,        prefix="/api/v1/reports",         tags=["Reports"])
app.include_router(analytics.router,      prefix="/api/v1/analytics",       tags=["Analytics"])
app.include_router(sentiment.router,      prefix="/api/v1/sentiment",       tags=["Sentiment"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "FinSentinel AI", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
