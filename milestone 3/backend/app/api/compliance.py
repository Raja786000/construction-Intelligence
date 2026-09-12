from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import json
from app.services.file_store import save_uploads
from app.compliance_agent.agent import ComplianceInsuranceAgent

router = APIRouter(tags=["Compliance & Insurance"])
agent = ComplianceInsuranceAgent()

@router.get("/capabilities")
def capabilities():
    return agent.capabilities()

@router.post("/inspect")
async def inspect(
    project_id: str = Form(...),
    site_id: str = Form(""),
    project_name: str = Form(""),
    jurisdiction: str = Form(""),
    inspection_date: str = Form(""),
    project_type: str = Form("commercial"),
    notes: str = Form(""),
    required_documents: str = Form(""),
    required_coverages: str = Form(""),
    minimum_liability_limit: str = Form(""),
    renewal_window_days: str = Form("30"),
    files: List[UploadFile] = File(default=[]),
):
    try:
        req = json.loads(required_documents) if required_documents else None
        cov = json.loads(required_coverages) if required_coverages else []
        docs = await save_uploads(files)
        request = {
            "project_id": project_id, "site_id": site_id, "project_name": project_name,
            "jurisdiction": jurisdiction, "inspection_date": inspection_date,
            "project_type": project_type, "notes": notes,
            "required_documents": req, "required_coverages": cov,
            "minimum_liability_limit": float(minimum_liability_limit) if minimum_liability_limit else None,
            "renewal_window_days": int(renewal_window_days or 30),
            "documents": docs,
        }
        return agent.inspect(request)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid input: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
