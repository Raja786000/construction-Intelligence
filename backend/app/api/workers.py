from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.db.connection import db

router = APIRouter(prefix="/api/workers", tags=["Worker Management"])

class WorkerCreate(BaseModel):
    worker_id: str
    name: str
    assigned_task: str
    helmet: str = "Yes"  # "Yes" or "No"
    vest: str = "Yes"    # "Yes" or "No"
    mobile: Optional[str] = ""
    certification: Optional[str] = "Certified Construction Worker"
    project_id: Optional[str] = "PROJ-METRO"

class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    assigned_task: Optional[str] = None
    helmet: Optional[str] = None
    vest: Optional[str] = None
    mobile: Optional[str] = None
    certification: Optional[str] = None
    project_id: Optional[str] = None
    ppe_status: Optional[str] = None

@router.get("")
@router.get("/")
def get_workers(
    search: Optional[str] = None,
    ppe_violation_only: Optional[bool] = False,
    project_id: Optional[str] = None
):
    try:
        query = {}
        if project_id:
            query["project_id"] = project_id

        workers = list(db["workers"].find(query))
        
        # Apply in-memory filtering if needed
        result = []
        for w in workers:
            w["id"] = str(w.get("_id", w.get("worker_id", "")))
            
            # Determine PPE violation
            is_violation = (w.get("helmet") == "No" or w.get("vest") == "No" or w.get("ppe_status") == "VIOLATION")
            w["ppe_status"] = "VIOLATION" if is_violation else "COMPLIANT"
            
            if ppe_violation_only and not is_violation:
                continue

            if search:
                s = search.lower()
                matches = (
                    s in w.get("name", "").lower() or
                    s in w.get("worker_id", "").lower() or
                    s in w.get("assigned_task", "").lower() or
                    s in w.get("certification", "").lower()
                )
                if not matches:
                    continue

            result.append(w)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{worker_id}")
def get_worker(worker_id: str):
    try:
        worker = db["workers"].find_one({"_id": worker_id}) or db["workers"].find_one({"worker_id": worker_id})
        if not worker:
            raise HTTPException(status_code=404, detail=f"Worker {worker_id} not found")
        worker["id"] = str(worker.get("_id", worker.get("worker_id", "")))
        return worker
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("")
@router.post("/")
def create_worker(req: WorkerCreate):
    try:
        # Check if worker_id exists
        existing = db["workers"].find_one({"_id": req.worker_id}) or db["workers"].find_one({"worker_id": req.worker_id})
        if existing:
            raise HTTPException(status_code=400, detail=f"Worker ID {req.worker_id} already exists.")

        is_violation = (req.helmet == "No" or req.vest == "No")
        worker_doc = {
            "_id": req.worker_id,
            "worker_id": req.worker_id,
            "name": req.name,
            "assigned_task": req.assigned_task,
            "helmet": req.helmet,
            "vest": req.vest,
            "mobile": req.mobile or "",
            "certification": req.certification or "General Construction",
            "project_id": req.project_id or "PROJ-METRO",
            "ppe_status": "VIOLATION" if is_violation else "COMPLIANT",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db["workers"].insert_one(worker_doc)
        worker_doc["id"] = req.worker_id

        # If violation on creation, automatically add alert
        if is_violation:
            db["alerts"].insert_one({
                "_id": f"ALT-W-{req.worker_id}",
                "title": f"Worker {req.worker_id} PPE Non-Compliance",
                "message": f"{req.name} ({req.assigned_task}) registered with missing PPE (Helmet: {req.helmet}, Vest: {req.vest}).",
                "severity": "CRITICAL" if req.helmet == "No" else "HIGH",
                "source_agent": "Worker Management Hub",
                "is_resolved": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return {"success": True, "worker": worker_doc}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create worker: {e}")

@router.put("/{worker_id}")
def update_worker(worker_id: str, req: WorkerUpdate):
    try:
        existing = db["workers"].find_one({"_id": worker_id}) or db["workers"].find_one({"worker_id": worker_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Worker not found")

        doc_id = existing["_id"]
        updates = {}
        if req.name is not None: updates["name"] = req.name
        if req.assigned_task is not None: updates["assigned_task"] = req.assigned_task
        if req.helmet is not None: updates["helmet"] = req.helmet
        if req.vest is not None: updates["vest"] = req.vest
        if req.mobile is not None: updates["mobile"] = req.mobile
        if req.certification is not None: updates["certification"] = req.certification
        if req.project_id is not None: updates["project_id"] = req.project_id

        # Re-evaluate PPE
        new_helmet = updates.get("helmet", existing.get("helmet", "Yes"))
        new_vest = updates.get("vest", existing.get("vest", "Yes"))
        is_violation = (new_helmet == "No" or new_vest == "No")
        updates["ppe_status"] = "VIOLATION" if is_violation else "COMPLIANT"

        db["workers"].update_one({"_id": doc_id}, {"$set": updates})
        updated = db["workers"].find_one({"_id": doc_id})
        updated["id"] = str(updated.get("_id", updated.get("worker_id", "")))
        return {"success": True, "worker": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update worker: {e}")

@router.patch("/{worker_id}/toggle-ppe")
def toggle_worker_ppe(worker_id: str, ppe_type: str = Query("helmet", pattern="^(helmet|vest)$")):
    try:
        existing = db["workers"].find_one({"_id": worker_id}) or db["workers"].find_one({"worker_id": worker_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Worker not found")

        doc_id = existing["_id"]
        current_val = existing.get(ppe_type, "Yes")
        new_val = "No" if current_val == "Yes" else "Yes"

        updates = {ppe_type: new_val}
        h = new_val if ppe_type == "helmet" else existing.get("helmet", "Yes")
        v = new_val if ppe_type == "vest" else existing.get("vest", "Yes")
        updates["ppe_status"] = "VIOLATION" if (h == "No" or v == "No") else "COMPLIANT"

        db["workers"].update_one({"_id": doc_id}, {"$set": updates})
        updated = db["workers"].find_one({"_id": doc_id})
        updated["id"] = str(updated.get("_id", updated.get("worker_id", "")))
        return {"success": True, "worker": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Toggle PPE failed: {e}")

@router.delete("/{worker_id}")
def delete_worker(worker_id: str):
    try:
        db["workers"].delete_many({"_id": worker_id})
        db["workers"].delete_many({"worker_id": worker_id})
        return {"success": True, "deleted_id": worker_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete worker: {e}")
