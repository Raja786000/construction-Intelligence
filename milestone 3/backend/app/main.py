from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.compliance import router

BASE = Path(__file__).resolve().parents[2]
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = FastAPI(
    title="Construction Compliance & Insurance Intelligence",
    version="2.0.0",
    description="Milestone 3 professional compliance, document and insurance screening agent."
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS)), name="uploads")
app.include_router(router, prefix="/api/v1/compliance")

@app.get("/health")
def health():
    return {"status": "ok", "agent": "compliance_insurance_agent", "milestone": 3, "version": "2.0.0"}
