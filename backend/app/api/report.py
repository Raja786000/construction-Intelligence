from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.db.connection import db
from app.agents.report_agent.graph import report_graph

router = APIRouter(prefix="/api/reports", tags=["reports"])

class ReportRequest(BaseModel):
    project_id: str

@router.post("/daily")
def generate_daily_report(request: ReportRequest):
    return run_report_agent(request.project_id, "Daily")

@router.post("/weekly")
def generate_weekly_report(request: ReportRequest):
    return run_report_agent(request.project_id, "Weekly")

@router.post("/monthly")
def generate_monthly_report(request: ReportRequest):
    return run_report_agent(request.project_id, "Monthly")

@router.get("/{report_id}")
def get_report(report_id: str):
    try:
        report = db["reports"].find_one({"_id": report_id})
        if not report:
            raise HTTPException(status_code=404, detail="Report not found.")
        return report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

def run_report_agent(project_id: str, report_type: str) -> dict:
    try:
        # Check if project exists
        project = db["projects"].find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found.")

        # Initialize ReportState
        initial_state = {
            "project_id": project_id,
            "report_type": report_type,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "project_monitoring": {},
            "safety": {},
            "risk": {},
            "quality": {},
            "prioritized_issues": [],
            "executive_summary": "",
            "project_monitoring_summary": "",
            "safety_summary": "",
            "risk_summary": "",
            "quality_summary": "",
            "recommendations": [],
            "next_actions": [],
            "validation_attempts": 0,
            "errors": [],
            "graph_logs": [],
            "final_report": {}
        }
        
        # Invoke LangGraph workflow
        print(f"Starting LangGraph Report Agent flow ({report_type}) for project {project_id}...")
        result = report_graph.invoke(initial_state)
        
        # Check if validation errors blocked execution
        if result.get("errors") and not result.get("final_report"):
            raise HTTPException(status_code=400, detail=f"Report generation validation failed: {result['errors']}")

        # Generate a unique report ID
        report_id = f"REP_{report_type[:1]}_{project_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        final_report = result["final_report"]
        final_report["_id"] = report_id
        final_report["id"] = report_id
        final_report["graph_logs"] = result["graph_logs"]
        
        # Save to database
        db["reports"].update_one(
            {"_id": report_id},
            {"$set": final_report},
            upsert=True
        )
        
        print(f"Report {report_id} generated and saved successfully!")
        return final_report
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report agent execution failed: {e}")
