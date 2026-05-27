"""Scenario Simulation Engine — API Routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, Field
from typing import Optional
import uuid, math
from datetime import datetime

from database.connection import get_db
from models.orm_models import Transaction, FraudPrediction, ScenarioSimulation

router = APIRouter()


class ScenarioParams(BaseModel):
    scenario_name: str = "Custom Scenario"
    inflation_spike_pct: float = Field(0.0, ge=0, le=100, description="Inflation increase %")
    transaction_surge_pct: float = Field(0.0, ge=0, le=500)
    fraud_spike_pct: float = Field(0.0, ge=0, le=500)
    liquidity_stress_pct: float = Field(0.0, ge=0, le=100)
    recession_severity: float = Field(0.0, ge=0, le=1, description="0=none, 1=severe")
    user_id: Optional[str] = None


class ScenarioResult(BaseModel):
    scenario_name: str
    parameters: dict
    results: dict
    simulation_id: str


@router.post("/run", response_model=ScenarioResult)
async def run_scenario(params: ScenarioParams, db: Session = Depends(get_db)):
    """Simulate financial stress and compute projected risk outcomes."""

    # Fetch baseline metrics
    base_txn_count = db.query(func.count(Transaction.transaction_id)).scalar() or 10000
    base_volume = db.query(func.sum(Transaction.amount)).scalar() or 50_000_000.0
    base_fraud_rate = (
        db.query(func.avg(func.cast(Transaction.fraud_label, Float))).scalar() or 0.02
    )
    avg_fraud_prob = (
        db.query(func.avg(FraudPrediction.fraud_probability)).scalar() or 0.15
    )

    # ── Simulation Logic ──────────────────────────────────────────────────────

    # Inflation effect: increases transaction amounts, reduces volume
    inflation_factor = 1 + (params.inflation_spike_pct / 100)
    adjusted_avg_amount = (base_volume / max(base_txn_count, 1)) * inflation_factor
    volume_reduction_from_inflation = base_volume * (params.inflation_spike_pct / 200)

    # Transaction surge
    surge_factor = 1 + (params.transaction_surge_pct / 100)
    projected_txn_count = int(base_txn_count * surge_factor)
    projected_volume = (base_volume - volume_reduction_from_inflation) * surge_factor

    # Fraud spike — compounding effect with transaction surge
    fraud_spike_factor = 1 + (params.fraud_spike_pct / 100)
    recession_fraud_boost = 1 + (params.recession_severity * 0.35)
    projected_fraud_rate = min(
        base_fraud_rate * fraud_spike_factor * recession_fraud_boost, 1.0
    )
    projected_fraud_count = int(projected_txn_count * projected_fraud_rate)
    projected_fraud_volume = projected_fraud_count * adjusted_avg_amount

    # Liquidity stress — affects failed transactions
    liquidity_factor = params.liquidity_stress_pct / 100
    projected_failure_rate = min(0.02 + liquidity_factor * 0.15, 0.5)
    projected_failed_txns = int(projected_txn_count * projected_failure_rate)

    # Risk exposure change
    base_risk_exposure = base_volume * base_fraud_rate
    projected_risk_exposure = projected_volume * projected_fraud_rate
    risk_change_pct = (
        (projected_risk_exposure - base_risk_exposure) / max(base_risk_exposure, 1) * 100
    )

    # Operational stress index (0–100)
    stress_index = min(
        100,
        (params.fraud_spike_pct * 0.25)
        + (params.transaction_surge_pct * 0.15)
        + (params.liquidity_stress_pct * 0.3)
        + (params.inflation_spike_pct * 0.1)
        + (params.recession_severity * 20),
    )

    # Model confidence degradation under stress
    confidence_degradation = min(0.4, stress_index / 250)
    adjusted_model_accuracy = max(0.5, 0.94 - confidence_degradation)

    results = {
        "baseline": {
            "transaction_count": base_txn_count,
            "total_volume": round(base_volume, 2),
            "fraud_rate": round(base_fraud_rate * 100, 3),
            "risk_exposure": round(base_risk_exposure, 2),
        },
        "projected": {
            "transaction_count": projected_txn_count,
            "total_volume": round(projected_volume, 2),
            "fraud_count": projected_fraud_count,
            "fraud_rate": round(projected_fraud_rate * 100, 3),
            "fraud_volume": round(projected_fraud_volume, 2),
            "failed_transactions": projected_failed_txns,
            "failure_rate": round(projected_failure_rate * 100, 3),
            "risk_exposure": round(projected_risk_exposure, 2),
            "risk_exposure_change_pct": round(risk_change_pct, 2),
        },
        "stress_metrics": {
            "operational_stress_index": round(stress_index, 1),
            "model_accuracy_under_stress": round(adjusted_model_accuracy * 100, 2),
            "confidence_degradation_pct": round(confidence_degradation * 100, 2),
            "avg_transaction_amount": round(adjusted_avg_amount, 2),
        },
        "alerts": _generate_alerts(params, stress_index, risk_change_pct, projected_fraud_rate),
    }

    # Persist simulation
    sim = ScenarioSimulation(
        user_id=params.user_id,
        scenario_name=params.scenario_name,
        parameters=params.dict(),
        results=results,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    return ScenarioResult(
        scenario_name=params.scenario_name,
        parameters=params.dict(),
        results=results,
        simulation_id=str(sim.simulation_id),
    )


def _generate_alerts(params, stress_index, risk_change_pct, fraud_rate):
    alerts = []
    if stress_index > 70:
        alerts.append({"severity": "CRITICAL", "message": "Extreme operational stress detected. Activate incident response protocols."})
    if risk_change_pct > 100:
        alerts.append({"severity": "HIGH", "message": f"Risk exposure projected to increase by {risk_change_pct:.0f}%. Review fraud thresholds."})
    if fraud_rate > 0.1:
        alerts.append({"severity": "HIGH", "message": f"Fraud rate exceeds 10% threshold under this scenario."})
    if params.liquidity_stress_pct > 50:
        alerts.append({"severity": "MEDIUM", "message": "High liquidity stress may trigger transaction failures and customer churn."})
    if params.inflation_spike_pct > 20:
        alerts.append({"severity": "MEDIUM", "message": "Inflation spike will reduce real transaction volumes. Adjust revenue forecasts."})
    if not alerts:
        alerts.append({"severity": "LOW", "message": "Scenario within manageable risk parameters."})
    return alerts


@router.get("/history")
async def get_simulation_history(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ScenarioSimulation)
    if user_id:
        query = query.filter(ScenarioSimulation.user_id == user_id)
    sims = query.order_by(ScenarioSimulation.created_at.desc()).limit(20).all()
    return [
        {
            "simulation_id": str(s.simulation_id),
            "scenario_name": s.scenario_name,
            "parameters": s.parameters,
            "stress_index": s.results.get("stress_metrics", {}).get("operational_stress_index"),
            "created_at": s.created_at.isoformat(),
        }
        for s in sims
    ]


# Fix missing import
from sqlalchemy import Float
