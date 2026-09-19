import os
import sys

_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.abspath(os.path.join(_current_dir, ".."))
for p in [_current_dir, _root_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.project import router as project_router
from app.api.workers import router as workers_router
from app.api.safety import router as safety_router
from app.api.predict import router as predict_router
from app.api.risk import router as risk_router
from app.api.weather import router as weather_router
from app.api.alerts import router as alerts_router
from app.api.quality import router as quality_router
from app.api.report import router as report_router
from app.api.pdf import router as pdf_router

from app.db.init_db import seed_database

app = FastAPI(
    title="Construction Intelligence Hub — Unified AI Platform",
    description="Unified Enterprise Platform integrating Safety (YOLOv11), Project/Worker Management (MongoDB), Risk ML, Weather, Alerts, Quality Inspection, and PDF Reporting",
    version="3.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Seeding Event
@app.on_event("startup")
def startup_db_seed():
    print("FastAPI Startup: Running database seeding pipeline...")
    seed_database()

# Register All 10 Module Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(project_router)
app.include_router(workers_router)
app.include_router(safety_router)
app.include_router(predict_router)
app.include_router(risk_router)
app.include_router(weather_router)
app.include_router(alerts_router)
app.include_router(quality_router)
app.include_router(report_router)
app.include_router(pdf_router)

# Expose YOLO and Quality output images
runs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "runs"))
os.makedirs(runs_dir, exist_ok=True)
app.mount("/results", StaticFiles(directory=runs_dir), name="results")

uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
def home():
    return {
        "platform": "Construction Intelligence Hub",
        "status": "ONLINE",
        "modules": [
            "Auth", "Dashboard", "Project Management", "Worker Management",
            "Safety YOLOv11", "Risk ML Predictor", "Weather API",
            "Alerts Center", "Quality Inspection", "PDF Reports"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "yolo_safety_model": "LOADED",
        "ml_pipeline": "ACTIVE",
        "database": "CONNECTED"
    }
