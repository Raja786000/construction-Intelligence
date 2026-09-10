from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from pathlib import Path

from .config import BASE_DIR
from .database import init_db, query_all, insert_item
from .seed_data import seed_database
from .cv_engine import ComputerVisionSafetyDetector
from .ml_engine import ConstructionMLPredictor
from .agents_orchestrator import AutonomousAgentsOrchestrator
from .ai_assistant import AIRiskAssistant

# Initialize DB
seed_database()

app = FastAPI(
    title="Agentic Construction Risk Intelligence Platform API",
    description="Backend AI Services for Construction Safety Monitoring, Risk Analysis & Multi-Agent Intelligence",
    version="2.0.0"
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
cv_detector = ComputerVisionSafetyDetector()
ml_predictor = ConstructionMLPredictor()
agents_orchestrator = AutonomousAgentsOrchestrator()
ai_assistant = AIRiskAssistant()

# Pydantic Schemas for API Requests
class ChatQueryRequest(BaseModel):
    query: str

class DelayPredictRequest(BaseModel):
    planned_days: int = 30
    completed_milestones: int = 7
    total_milestones: int = 12
    weather_rainfall_mm: float = 38.0
    active_workers: int = 64

class CostPredictRequest(BaseModel):
    budget: float = 24500000.0
    spent: float = 14200000.0
    schedule_delay_days: float = 3.5
    material_shortage_risk: str = "HIGH"

class EquipmentPredictRequest(BaseModel):
    operating_hours: float = 1420.5
    vibration_mm_s: float = 8.4
    days_since_maintenance: int = 24

# --- API ROUTES ---

@app.get("/api/health")
def health_check():
    return {
        "status": "ONLINE",
        "system": "Agentic Construction Risk Intelligence Platform",
        "database": "CONNECTED",
        "yolo_cv_mode": "ACTIVE" if cv_detector.use_yolo else "SIMULATED_PROD"
    }

# 1. Executive Dashboard Overview Endpoint
@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    projects = query_all("projects")
    sites = query_all("sites")
    risks = query_all("risks")
    workers = query_all("workers")
    equip = query_all("equipment")
    alerts = query_all("alerts")
    weather = query_all("weather_data")

    proj = projects[0] if projects else {}
    w_data = weather[0] if weather else {}

    # Calculate live compliance & metrics
    non_compliant_workers = sum(1 for w in workers if w.get("ppe_compliance") != "COMPLIANT")
    ppe_compliance_pct = round(max(0, 100 - (non_compliant_workers / max(1, len(workers)) * 100)), 1)

    high_risk_equip = sum(1 for e in equip if e.get("failure_probability", 0) > 0.30)
    unresolved_alerts = [a for a in alerts if not a.get("is_resolved")]

    return {
        "project": proj,
        "site": sites[0] if sites else {},
        "composite_risk_score": proj.get("risk_score", 42.8),
        "overall_risk_level": "HIGH" if proj.get("risk_score", 42.8) > 40 else "MEDIUM",
        "ppe_compliance_pct": ppe_compliance_pct,
        "active_workers_count": len(workers),
        "equipment_failure_flags": high_risk_equip,
        "unresolved_alerts_count": len(unresolved_alerts),
        "recent_alerts": unresolved_alerts[:3],
        "weather_summary": w_data,
        "active_risks_count": len(risks)
    }

# 2. Computer Vision Safety & PPE Analysis Endpoint
@app.post("/api/safety/analyze")
async def analyze_safety_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = cv_detector.analyze_image_file(content, filename=file.filename or "upload.jpg")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Computer vision analysis error: {str(e)}")

# 3. Autonomous Agents Orchestration Endpoint
@app.get("/api/agents/collaborate")
def get_agents_collaboration():
    return agents_orchestrator.run_agent_cycle()

# 4. Predictive Machine Learning Analytics Endpoints
@app.post("/api/predictive/schedule-delay")
def predict_schedule_delay(req: DelayPredictRequest):
    return ml_predictor.predict_schedule_delay(
        req.planned_days, req.completed_milestones, req.total_milestones,
        req.weather_rainfall_mm, req.active_workers
    )

@app.post("/api/predictive/cost-overrun")
def predict_cost_overrun(req: CostPredictRequest):
    return ml_predictor.predict_cost_overrun(
        req.budget, req.spent, req.schedule_delay_days, req.material_shortage_risk
    )

@app.post("/api/predictive/equipment-failure")
def predict_equipment_failure(req: EquipmentPredictRequest):
    return ml_predictor.predict_equipment_failure(
        req.operating_hours, req.vibration_mm_s, req.days_since_maintenance
    )

# 5. Entity Management API (Returns any of the 15 Entities)
@app.get("/api/entities/{entity_type}")
def get_entities(entity_type: str):
    valid_tables = {
        "projects": "projects",
        "sites": "sites",
        "risks": "risks",
        "ai_agents": "ai_agents",
        "workers": "workers",
        "equipment": "equipment",
        "materials": "materials",
        "tasks": "tasks",
        "incidents": "safety_incidents",
        "weather": "weather_data",
        "costs": "cost_records",
        "schedules": "schedules",
        "sensors": "sensor_data",
        "alerts": "alerts",
        "reports": "reports"
    }

    if entity_type not in valid_tables:
        raise HTTPException(status_code=400, detail=f"Invalid entity table. Choose from: {list(valid_tables.keys())}")

    table_name = valid_tables[entity_type]
    data = query_all(table_name)
    return {"entity": entity_type, "count": len(data), "data": data}

# 6. AI Risk Assistant Chat Endpoint
@app.post("/api/assistant/chat")
def chat_with_assistant(req: ChatQueryRequest):
    return ai_assistant.answer_query(req.query)

# 7. Executive Report Exporter Endpoint
@app.get("/api/reports/generate")
def generate_risk_report(report_type: str = "Weekly Risk Audit"):
    return ai_assistant.generate_report(report_type)

# Mount Frontend static files
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
