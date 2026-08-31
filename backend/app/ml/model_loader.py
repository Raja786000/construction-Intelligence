import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Try importing from src. If fails, add to path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:
    import joblib
    from src.preprocessing import clean_dataframe
    from src.feature_engineering import engineer_project_features
    from src.models.delay_model import DelayClassifier
    from src.models.completion_date_model import CompletionDateRegressor
    from src.models.milestone_model import MilestonePredictor, monitor_milestones
    from src.models.health_score import calculate_project_health_score
    from src.models.critical_path import analyze_critical_path
    from src.models.explainability import ProjectExplainer
    HAS_ML_SRC = True
except Exception as e:
    print(f"Warning: Failed to import ML pipeline components ({e}). Using mock ML fallbacks.")
    HAS_ML_SRC = False

class ModelLoader:
    def __init__(self):
        self.workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        self.models_dir = os.path.join(self.workspace_dir, "models_saved")
        self.is_mock = not HAS_ML_SRC or not os.path.exists(os.path.join(self.models_dir, "delay_classifier.pkl"))
        
        if not self.is_mock:
            try:
                self.delay_classifier = DelayClassifier(model_type="xgboost")
                self.delay_classifier.load(self.models_dir)
                
                self.completion_regressor = CompletionDateRegressor(model_type="xgboost")
                self.completion_regressor.load(self.models_dir)
                
                self.milestone_predictor = MilestonePredictor()
                self.milestone_predictor.load(os.path.join(self.models_dir, "milestone_model.pkl"))
                
                self.explainer = ProjectExplainer(
                    classifier_model=self.delay_classifier.model,
                    regressor_model=self.completion_regressor.model,
                    feature_cols=self.delay_classifier.feature_cols
                )
                self.feature_cols = self.delay_classifier.feature_cols
                print("Successfully loaded all Project Monitoring ML models!")
            except Exception as e:
                print(f"Warning: Error loading model pickle binaries ({e}). Falling back to rule-based prediction engine.")
                self.is_mock = True

    def get_predictions(self, project_data: dict, tasks: list, milestones: list) -> dict:
        if self.is_mock:
            return self._get_mock_predictions(project_data, tasks, milestones)
            
        try:
            # Map DB fields to what engineered pipeline expects
            p_data_mapped = {
                "Project ID": project_data["_id"],
                "Project Name": project_data["name"],
                "Project Type": project_data["type"],
                "Project Start Date": project_data["start_date"],
                "Planned End Date": project_data["planned_end_date"],
                "Current Date": project_data.get("current_date", "2023-01-22"),
                "Planned Duration (Days)": project_data.get("planned_duration", 30),
                "Actual Duration (Days)": project_data.get("actual_duration", 30),
                "Actual Progress (%)": project_data["actual_progress"],
                "Planned Progress (%)": project_data["planned_progress"],
                "Schedule Variance": project_data["schedule_variance"],
                "Schedule Status": project_data["schedule_status"]
            }
            
            tasks_mapped = []
            for t in tasks:
                tasks_mapped.append({
                    "Task ID": t["_id"],
                    "Project ID": t["project_id"],
                    "Task Name": t["name"],
                    "Actual Start Date": t["start_date"],
                    "Actual End Date": t["end_date"],
                    "Planned Start Date": t["planned_start"],
                    "Planned End Date": t["planned_end"],
                    "Actual Progress (%)": t["progress"],
                    "Planned Progress (%)": t.get("planned_progress", t["progress"]),
                    "Task Status": t["status"],
                    "Critical Path": "Yes" if t["is_critical"] else "No",
                    "Task Priority": t.get("priority", "Medium"),
                    "Actual Duration": t.get("actual_duration", 5),
                    "Task Duration": t.get("task_duration", 5),
                    "Time Deviation": t["time_deviation"]
                })
                
            milestones_mapped = []
            for m in milestones:
                milestones_mapped.append({
                    "Milestone ID": m["_id"],
                    "Project ID": m["project_id"],
                    "Milestone Name": m["name"],
                    "Planned Date": m["due_date"],
                    "Completion Status": m["status"],
                    "Actual Date": m["completion_date"]
                })

            df_p_raw = pd.DataFrame([p_data_mapped])
            df_tasks_raw = pd.DataFrame(tasks_mapped)
            df_milestones_raw = pd.DataFrame(milestones_mapped)
            
            df_p = clean_dataframe(df_p_raw)
            df_t = clean_dataframe(df_tasks_raw)
            df_m = clean_dataframe(df_milestones_raw)
            
            df_proj_feat = engineer_project_features(df_p, df_t, df_m)
            
            p_row = df_proj_feat.iloc[0]
            health_score, health_status = calculate_project_health_score(p_row, df_t, df_m)
            
            cp_analysis = analyze_critical_path(project_data["_id"], df_t)
            m_monitoring = monitor_milestones(project_data["_id"], df_m)
            
            pred_labels, delay_probs, _ = self.delay_classifier.predict(df_proj_feat)
            pred_delays, pred_comp_dates = self.completion_regressor.predict_completion(df_proj_feat)
            
            df_proj_feat_expl = df_proj_feat.copy()
            df_proj_feat_expl["Predicted Delay (Days)"] = pred_delays
            df_proj_feat_expl["Predicted Completion Date"] = pred_comp_dates
            df_proj_feat_expl["Predicted Delay Class"] = pred_labels
            df_proj_feat_expl["Delay Classification"] = pred_labels
            
            encoded_proj_feat = df_proj_feat.copy()
            encoded_features, _ = self.delay_classifier.prepare_data(df_proj_feat, is_training=False)
            encoded_proj_feat[self.feature_cols] = encoded_features
            
            xai_report = self.explainer.explain_project(project_data["_id"], encoded_proj_feat, df_proj_feat_expl)
            
            delay_prob_val = float(delay_probs[0])
            if delay_prob_val > 1.0:
                delay_prob_val /= 100.0

            completed_tasks_count = sum(1 for t in tasks if t["status"] == "Completed")
            delayed_tasks_count = sum(1 for t in tasks if t["time_deviation"] > 0)
            active_tasks_count = len(tasks) - completed_tasks_count

            return {
                "project_id": project_data["_id"],
                "project_status": str(pred_labels[0]),
                "planned_progress": round(float(p_row["Planned Progress (%)"]), 2),
                "actual_progress": round(float(p_row["Actual Progress (%)"]), 2),
                "schedule_variance": round(float(p_row["Schedule Variance"]), 2),
                "completed_tasks": completed_tasks_count,
                "active_tasks": active_tasks_count,
                "delayed_tasks": delayed_tasks_count,
                "milestone_completion": round(float(m_monitoring["completion_percentage"]), 2),
                "delay_probability": round(delay_prob_val, 2),
                "predicted_delay_days": int(pred_delays[0]),
                "planned_completion_date": str(p_row["Planned End Date"]),
                "predicted_completion_date": str(pred_comp_dates[0]),
                "critical_tasks": [t["Task Name"] for t in cp_analysis["delayed_critical_tasks"]][:5],
                "project_health_score": round(float(health_score), 2),
                "explainable_ai_summary": str(xai_report["explanation_summary"])
            }
        except Exception as e:
            print(f"Prediction error ({e}). Falling back to rule-based fallback predictions.")
            return self._get_mock_predictions(project_data, tasks, milestones)

    def _get_mock_predictions(self, project_data: dict, tasks: list, milestones: list) -> dict:
        actual_progress = project_data["actual_progress"]
        planned_progress = project_data["planned_progress"]
        sv = actual_progress - planned_progress
        
        # Simple heuristics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t["status"] == "Completed")
        active_tasks = sum(1 for t in tasks if t["status"] == "In Progress")
        delayed_tasks = sum(1 for t in tasks if t["time_deviation"] > 0)
        critical_tasks = [t for t in tasks if t["is_critical"]]
        delayed_critical = [t for t in critical_tasks if t["time_deviation"] > 0]
        
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m["status"] == "Completed")
        m_completion = (completed_milestones / total_milestones * 100.0) if total_milestones > 0 else 0.0
        
        # Status Mapping
        if sv < -10:
            status = "Critically Delayed"
            delay_prob = 0.95
            predicted_delay = int(abs(sv) * 3)
        elif sv < -2:
            status = "Behind Schedule"
            delay_prob = 0.80
            predicted_delay = int(abs(sv) * 2)
        elif sv <= 2:
            status = "On Schedule"
            delay_prob = 0.25
            predicted_delay = 0
        else:
            status = "Ahead of Schedule"
            delay_prob = 0.05
            predicted_delay = int(-sv * 1)
            
        planned_end = datetime.strptime(project_data["planned_end_date"], "%Y-%m-%d")
        predicted_end = planned_end + timedelta(days=predicted_delay)
        
        # Calculate Health Score
        health = 100.0 - (abs(sv) * 1.5) - (delayed_tasks / total_tasks * 20.0 if total_tasks > 0 else 0.0)
        health = max(min(health, 100.0), 0.0)
        
        # Explanations
        xai_summary = f"The project is predicted to be {status.lower()} primarily because the actual progress is {abs(sv):.1f}% "
        xai_summary += "below" if sv < 0 else "above"
        xai_summary += f" planned progress, {delayed_tasks} tasks are delayed, and critical path activities are lagging."

        return {
            "project_id": project_data["_id"],
            "project_status": status,
            "planned_progress": round(planned_progress, 2),
            "actual_progress": round(actual_progress, 2),
            "schedule_variance": round(sv, 2),
            "completed_tasks": completed_tasks,
            "active_tasks": active_tasks,
            "delayed_tasks": delayed_tasks,
            "milestone_completion": round(m_completion, 2),
            "delay_probability": round(delay_prob, 2),
            "predicted_delay_days": predicted_delay,
            "planned_completion_date": project_data["planned_end_date"],
            "predicted_completion_date": predicted_end.strftime("%Y-%m-%d"),
            "critical_tasks": [t["name"] for t in delayed_critical],
            "project_health_score": round(health, 2),
            "explainable_ai_summary": xai_summary
        }

model_loader = ModelLoader()
