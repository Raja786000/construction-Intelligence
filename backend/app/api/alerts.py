from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.db.connection import db

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

class AlertCreate(BaseModel):
    title: str
    message: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    source_agent: str = "Safety Agent"

@router.get("")
@router.get("/")
def get_alerts(unresolved_only: bool = False, severity: Optional[str] = None):
    try:
        alerts = list(db["alerts"].find())
        result = []
        for a in alerts:
            a["id"] = str(a.get("_id", ""))
            if unresolved_only and a.get("is_resolved", False):
                continue
            if severity and a.get("severity", "").upper() != severity.upper():
                continue
            result.append(a)

        # Sort with CRITICAL first, then HIGH, then MEDIUM, then LOW
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        result.sort(key=lambda x: (sev_order.get(x.get("severity", "MEDIUM"), 4), x.get("is_resolved", False)))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("")
@router.post("/")
def create_alert(req: AlertCreate):
    try:
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        doc = {
            "_id": alert_id,
            "id": alert_id,
            "title": req.title,
            "message": req.message,
            "severity": req.severity.upper(),
            "source_agent": req.source_agent,
            "is_resolved": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db["alerts"].insert_one(doc)
        return {"success": True, "alert": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {e}")

@router.put("/{alert_id}/resolve")
def resolve_alert(alert_id: str):
    try:
        db["alerts"].update_one(
            {"_id": alert_id},
            {"$set": {"is_resolved": True, "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        return {"success": True, "alert_id": alert_id, "is_resolved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {e}")

@router.delete("/{alert_id}")
def delete_alert(alert_id: str):
    try:
        db["alerts"].delete_many({"_id": alert_id})
        return {"success": True, "deleted_id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {e}")
