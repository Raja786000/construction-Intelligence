from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.quality import router as quality_router
from .api.live import router as live_router

BASE = Path(__file__).resolve().parents[2]
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)

app = FastAPI(title="Construction Quality Inspection Agent", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS), name="uploads")
app.include_router(quality_router, prefix="/api/v1/quality")
app.include_router(live_router, prefix="/api/v1/quality/live")

@app.get("/health")
def health():
    return {"status":"ok","agent":"quality_inspection_agent","version":"3.2.0"}
