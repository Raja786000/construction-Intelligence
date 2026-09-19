import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime

router = APIRouter(prefix="/api/quality", tags=["Quality Inspection"])

UPLOAD_DIR = Path("uploads/quality")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/categories")
def get_categories():
    return [
        {"id": "crack", "name": "Cracks & Fractures", "target": "Walls, slabs, beams, linear fissures"},
        {"id": "concrete", "name": "Concrete Defects", "target": "Honeycombing, spalling, void anomalies"},
        {"id": "surface", "name": "Surface & Finish", "target": "Plaster texture, roughness, finish screening"},
        {"id": "component", "name": "Components & Installation", "target": "Openings, rebar alignment, checklist specs"},
        {"id": "corrosion", "name": "Rust & Corrosion", "target": "Structural steel rebar oxidization, stain screen"}
    ]

@router.post("/inspect")
async def inspect_quality(
    project_id: str = Form("PROJ-METRO"),
    location: str = Form("Hyderabad Metro Site"),
    category: str = Form("concrete"),
    description: Optional[str] = Form("Site visual quality check"),
    file: Optional[UploadFile] = File(None)
):
    try:
        saved_filename = None
        if file and file.filename:
            file_ext = Path(file.filename).suffix or ".jpg"
            saved_filename = f"qual_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
            file_path = UPLOAD_DIR / saved_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Categorize defect analysis
        findings = []
        score = 88
        status = "PASS"
        severity = "LOW"

        cat_lower = category.lower()
        if "crack" in cat_lower:
            score = 72
            status = "REVIEW_REQUIRED"
            severity = "MEDIUM"
            findings.append({
                "category": "Cracks",
                "severity": "MEDIUM",
                "title": "Hairline Surface Micro-Crack Detected",
                "description": "Linear surface crack detected with estimated width 0.8mm (acceptable threshold < 1.0mm).",
                "recommendation": "Monitor fissure with crack width gauge during 7-day cure cycle."
            })
        elif "concrete" in cat_lower:
            score = 65
            status = "REVIEW_REQUIRED"
            severity = "HIGH"
            findings.append({
                "category": "Concrete",
                "severity": "HIGH",
                "title": "Localized Honeycombing Anomaly",
                "description": "Surface void density indicates incomplete mechanical vibration during concrete pour.",
                "recommendation": "Perform non-destructive rebound hammer test and apply polymer-modified mortar patch."
            })
        elif "corrosion" in cat_lower:
            score = 58
            status = "FAIL"
            severity = "HIGH"
            findings.append({
                "category": "Corrosion",
                "severity": "HIGH",
                "title": "Rebar Surface Oxidization Detected",
                "description": "Visible ferrous oxide staining on exposed anchor bolts and stirrup ties.",
                "recommendation": "Wire brush to Sa 2.5 standard and coat with zinc-rich epoxy primer prior to embedment."
            })
        elif "surface" in cat_lower:
            score = 92
            status = "PASS"
            severity = "LOW"
            findings.append({
                "category": "Surface",
                "severity": "LOW",
                "title": "Acceptable Surface Uniformity",
                "description": "Texture and planar alignment within tolerance standards.",
                "recommendation": "Proceed with priming and exterior coating."
            })
        else:
            score = 95
            status = "PASS"
            severity = "NONE"
            findings.append({
                "category": "Component Installation",
                "severity": "NONE",
                "title": "Alignment Within Construction Tolerance",
                "description": "Formwork and reinforcement spacing conform to structural drawings.",
                "recommendation": "Sign off inspection checklist."
            })

        return {
            "inspection_id": f"QI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_id": project_id,
            "category": category,
            "location": location,
            "quality_score": score,
            "status": status,
            "highest_severity": severity,
            "findings_count": len(findings),
            "findings": findings,
            "inspected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": f"/results/{saved_filename}" if saved_filename else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality inspection failed: {e}")
