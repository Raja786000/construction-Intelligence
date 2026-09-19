from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.db.connection import db

router = APIRouter(prefix="/api/risk", tags=["Risk Prediction"])

class ScheduleDelayInput(BaseModel):
    planned_days: int = 30
    completed_milestones: int = 7
    total_milestones: int = 12
    weather_rainfall_mm: float = 38.0
    active_workers: int = 64

class CostRiskInput(BaseModel):
    budget: float = 20.0       # ₹ Cr
    spent: float = 1.8         # ₹ Cr
    schedule_delay_days: float = 3.5
    material_shortage_risk: str = "HIGH"

class EquipmentRiskInput(BaseModel):
    operating_hours: float = 1420.5
    vibration_mm_s: float = 8.4
    days_since_maintenance: int = 24

@router.get("/summary")
def get_risk_summary():
    """Returns composite risk assessment across Schedule, Cost, Safety, Equipment, and Weather."""
    return {
        "overall_risk_score": 42.8,
        "overall_risk_level": "High",
        "primary_threat": "Severe rainfall forecast causing concrete curing delays & Tower Crane vibration strain",
        "risk_breakdown": [
            {
                "category": "Weather Disruption",
                "risk_score": 85,
                "severity": "CRITICAL",
                "factor": "38mm rain forecast for tomorrow; flood risk in foundation pit B",
                "recommendation": "Deploy rain tarpaulins and activate dewatering pump units."
            },
            {
                "category": "Equipment Failure",
                "risk_score": 72,
                "severity": "HIGH",
                "factor": "Tower Crane #2 vibration reading 8.4 mm/s (threshold: 7.0 mm/s)",
                "recommendation": "Schedule urgent gearbox inspection and bearing lubrication."
            },
            {
                "category": "Schedule Delay",
                "risk_score": 64,
                "severity": "HIGH",
                "factor": "Steel framing erection milestone projected 3.5 to 5.0 days delay",
                "recommendation": "Authorize additional shift for rebar fixing crew."
            },
            {
                "category": "Cost Overrun",
                "risk_score": 58,
                "severity": "MEDIUM",
                "factor": "Structural steel procurement price fluctuation (+7.0% variance)",
                "recommendation": "Hedge supplier contract for remaining 45 tons of rebar."
            },
            {
                "category": "Safety Non-Compliance",
                "risk_score": 40,
                "severity": "MEDIUM",
                "factor": "3 workers registered with missing PPE (Hardhat/Vest)",
                "recommendation": "Conduct mandatory morning safety briefing and supply PPE."
            }
        ],
        "mitigation_plan": "Multi-agent autonomous collaboration protocol initiated. Weather tarps dispatched; Crane load limits lowered by 30% until inspection."
    }

@router.post("/predict-delay")
def predict_schedule_delay(req: ScheduleDelayInput):
    # Calculate ML delay prediction based on milestones progress, rain, and labor
    milestone_ratio = req.completed_milestones / max(1, req.total_milestones)
    base_delay = 0.0

    if milestone_ratio < 0.5:
        base_delay += 4.5
    elif milestone_ratio < 0.8:
        base_delay += 2.0

    if req.weather_rainfall_mm > 25.0:
        base_delay += (req.weather_rainfall_mm - 25.0) * 0.12

    if req.active_workers < 50:
        base_delay += 1.5

    delay_days = round(max(0.0, base_delay), 1)
    delay_prob = round(min(0.95, 0.35 + (delay_days * 0.08)), 2)
    status = "CRITICAL_DELAY" if delay_days > 5 else ("MODERATE_DELAY" if delay_days > 2 else "ON_TRACK")

    return {
        "predicted_delay_days": delay_days,
        "delay_probability": delay_prob,
        "projected_status": status,
        "key_risk_driver": "Precipitation & Milestones Lag" if req.weather_rainfall_mm > 25 else "Workforce Capacity",
        "suggested_mitigation": "Fast-track critical path activities and implement weekend makeup shift."
    }

@router.post("/predict-cost")
def predict_cost_overrun(req: CostRiskInput):
    variance_pct = round(((req.spent / max(0.1, req.budget)) * 100) - 50.0, 1) if req.budget > 0 else 0.0
    risk_factor = 0.2
    if req.material_shortage_risk.upper() == "HIGH":
        risk_factor += 0.35
    elif req.material_shortage_risk.upper() == "MEDIUM":
        risk_factor += 0.15

    risk_factor += (req.schedule_delay_days * 0.04)
    overrun_prob = round(min(0.98, max(0.05, risk_factor)), 2)
    projected_overrun_cr = round(req.budget * (overrun_prob * 0.12), 2)

    return {
        "budget_cr": req.budget,
        "spent_cr": req.spent,
        "overrun_probability": overrun_prob,
        "projected_cost_overrun_cr": projected_overrun_cr,
        "cost_health": "CRITICAL" if overrun_prob > 0.6 else ("WARNING" if overrun_prob > 0.35 else "HEALTHY"),
        "recommendation": "Review supplier commitments and enforce strict budget gates on Phase 2 concrete."
    }

@router.post("/predict-equipment")
def predict_equipment_failure(req: EquipmentRiskInput):
    vib_excess = max(0.0, req.vibration_mm_s - 5.0)
    fail_prob = min(0.95, 0.05 + (vib_excess * 0.12) + (req.days_since_maintenance * 0.015))
    fail_prob = round(fail_prob, 2)

    return {
        "equipment_name": "Tower Crane #2 (Liebherr 280)",
        "vibration_mm_s": req.vibration_mm_s,
        "threshold_mm_s": 7.0,
        "failure_probability": fail_prob,
        "status": "DANGER" if fail_prob > 0.5 else ("CAUTION" if fail_prob > 0.25 else "NORMAL"),
        "recommended_action": "Emergency gear lubrication & bearing vibration spectrum analysis required."
    }
