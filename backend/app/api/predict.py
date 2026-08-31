from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.db.connection import db
from app.ml.model_loader import model_loader

router = APIRouter(prefix="/api/project-monitoring", tags=["project-monitoring"])

class PredictionRequest(BaseModel):
    project_id: str

@router.post("/predict")
def predict_project(request: PredictionRequest):
    try:
        project_id = request.project_id
        
        # Load from database
        project = db["projects"].find_one({"_id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found.")
            
        tasks = list(db["tasks"].find({"project_id": project_id}))
        milestones = list(db["milestones"].find({"project_id": project_id}))
        
        # Make ML predictions
        pred_res = model_loader.get_predictions(project, tasks, milestones)
        
        # Save predictions to DB
        db["predictions"].update_one(
            {"project_id": project_id},
            {
                "$set": {
                    "predicted_delay_days": pred_res["predicted_delay_days"],
                    "predicted_completion_date": pred_res["predicted_completion_date"],
                    "delay_probability": pred_res["delay_probability"],
                    "delay_class": pred_res["project_status"],
                    "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            },
            upsert=True
        )
        
        return pred_res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
