from fastapi import APIRouter, HTTPException
from app.db.connection import db

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("")
@router.get("/")
def get_projects():
    try:
        # Retrieve all projects from the database
        projects = list(db["projects"].find())
        # Convert _id to string or representation if necessary
        for p in projects:
            p["id"] = p["_id"]
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{project_id}")
def get_project_by_id(project_id: str):
    try:
        project = db["projects"].find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load tasks and milestones
        tasks = list(db["tasks"].find({"project_id": project_id}))
        milestones = list(db["milestones"].find({"project_id": project_id}))
        
        project["id"] = project["_id"]
        return {
            "project": project,
            "tasks": tasks,
            "milestones": milestones
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")