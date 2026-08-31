from app.ml.model_loader import model_loader
from app.db.connection import db

class ProjectMonitoringAdapter:
    @staticmethod
    def get_results(project_id: str) -> dict:
        try:
            # Query project data and children
            project = db["projects"].find_one({"_id": project_id})
            if not project:
                return {
                    "project_id": project_id,
                    "project_status": "Data Unavailable",
                    "actual_progress": 0.0,
                    "planned_progress": 0.0,
                    "schedule_variance": 0.0,
                    "completed_tasks": 0,
                    "active_tasks": 0,
                    "delayed_tasks": 0,
                    "milestone_completion": 0.0,
                    "delay_probability": 0.0,
                    "predicted_delay_days": 0,
                    "planned_completion_date": "",
                    "predicted_completion_date": "",
                    "critical_tasks": [],
                    "project_health_score": 100.0,
                    "explainable_ai_summary": "No data available."
                }
            
            tasks = list(db["tasks"].find({"project_id": project_id}))
            milestones = list(db["milestones"].find({"project_id": project_id}))
            
            # Predict
            return model_loader.get_predictions(project, tasks, milestones)
        except Exception as e:
            print(f"Error in ProjectMonitoringAdapter: {e}")
            return {"project_id": project_id, "project_status": "Error", "explainable_ai_summary": f"Failed: {e}"}
