from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.connection import db

router = APIRouter(prefix="/api/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    client: str
    budget: float  # In Crores
    spent: Optional[float] = 0.0
    location: str
    start_date: str
    end_date: str
    project_type: Optional[str] = "Infrastructure"
    actual_progress: Optional[float] = 0.0
    planned_progress: Optional[float] = 0.0

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    project_type: Optional[str] = None
    actual_progress: Optional[float] = None
    planned_progress: Optional[float] = None
    schedule_status: Optional[str] = None

@router.get("")
@router.get("/")
def get_projects():
    try:
        projects = list(db["projects"].find())
        for p in projects:
            p["id"] = str(p.get("_id", ""))
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{project_id}")
def get_project_by_id(project_id: str):
    try:
        project = db["projects"].find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        
        tasks = list(db["tasks"].find({"project_id": project_id}))
        milestones = list(db["milestones"].find({"project_id": project_id}))
        
        project["id"] = str(project.get("_id", ""))
        return {
            "project": project,
            "tasks": tasks,
            "milestones": milestones
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("")
@router.post("/")
def create_project(req: ProjectCreate):
    try:
        proj_id = f"PROJ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        project_doc = {
            "_id": proj_id,
            "id": proj_id,
            "name": req.name,
            "client": req.client,
            "budget": req.budget,
            "spent": req.spent or 0.0,
            "budget_currency": "₹ Cr",
            "location": req.location,
            "start_date": req.start_date,
            "planned_end_date": req.end_date,
            "end_date": req.end_date,
            "type": req.project_type,
            "actual_progress": req.actual_progress or 0.0,
            "planned_progress": req.planned_progress or 0.0,
            "schedule_variance": (req.actual_progress or 0.0) - (req.planned_progress or 0.0),
            "schedule_status": "On Schedule" if (req.actual_progress or 0.0) >= (req.planned_progress or 0.0) else "Behind Schedule",
            "risk_score": 35.0,
            "risk_level": "Medium",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db["projects"].insert_one(project_doc)
        return {"success": True, "project": project_doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create project: {e}")

@router.put("/{project_id}")
def update_project(project_id: str, req: ProjectUpdate):
    try:
        existing = db["projects"].find_one({"_id": project_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Project not found")

        updates = {}
        if req.name is not None: updates["name"] = req.name
        if req.client is not None: updates["client"] = req.client
        if req.budget is not None: updates["budget"] = req.budget
        if req.spent is not None: updates["spent"] = req.spent
        if req.location is not None: updates["location"] = req.location
        if req.start_date is not None: updates["start_date"] = req.start_date
        if req.end_date is not None:
            updates["end_date"] = req.end_date
            updates["planned_end_date"] = req.end_date
        if req.project_type is not None: updates["type"] = req.project_type
        if req.actual_progress is not None: updates["actual_progress"] = req.actual_progress
        if req.planned_progress is not None: updates["planned_progress"] = req.planned_progress
        if req.schedule_status is not None: updates["schedule_status"] = req.schedule_status

        db["projects"].update_one({"_id": project_id}, {"$set": updates})
        updated = db["projects"].find_one({"_id": project_id})
        updated["id"] = str(updated.get("_id", ""))
        return {"success": True, "project": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update project: {e}")

@router.delete("/{project_id}")
def delete_project(project_id: str):
    try:
        db["projects"].delete_many({"_id": project_id})
        db["tasks"].delete_many({"project_id": project_id})
        db["milestones"].delete_many({"project_id": project_id})
        return {"success": True, "deleted_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {e}")