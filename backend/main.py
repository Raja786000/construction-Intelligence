import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.safety import router as safety_router
from app.api.project import router as project_router
from app.api.predict import router as predict_router
from app.api.report import router as report_router
from app.api.pdf import router as pdf_router
from app.db.init_db import seed_database

app = FastAPI(
    title="AI Construction Monitoring System"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for E2E demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Seeding Event
@app.on_event("startup")
def startup_db_seed():
    print("FastAPI Startup: Running database seeding pipeline...")
    seed_database()

# Register Routers
app.include_router(safety_router)
app.include_router(project_router)
app.include_router(predict_router)
app.include_router(report_router)
app.include_router(pdf_router)

# Expose YOLO output images
os_runs_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), "runs")
os.makedirs(os_runs_dir, exist_ok=True)
app.mount("/results", StaticFiles(directory="runs"), name="results")


@app.get("/")
def home():
    return "AI-powered Construction Monitoring System"


@app.get("/health")
def health():
    return {"status": "Healthy"}

