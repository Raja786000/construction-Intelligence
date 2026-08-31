import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class MilestonePredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoders = {}
        self.is_trained = False
        
    def prepare_features(self, milestones_df, tasks_df, projects_df, is_training=True):
        """
        Merges milestone data with task and project data to build a feature matrix.
        """
        # Join milestones with their associated tasks
        df = milestones_df.merge(
            tasks_df[["Task ID", "WBS Level", "Task Duration", "Critical Path", "Task Priority"]],
            left_on="Associated Task ID",
            right_on="Task ID",
            how="left"
        )
        
        # Join with project information
        df = df.merge(
            projects_df[["Project ID", "Project Type", "Schedule Variance", "Delay Factor"]],
            on="Project ID",
            how="left"
        )
        
        # Target variable (for training): did actual date exceed planned date?
        if is_training:
            df["is_delayed"] = (pd.to_datetime(df["Actual Date"]) > pd.to_datetime(df["Planned Date"])).astype(int)
            
        # Categorical columns to encode
        cat_cols = ["Project Type", "Critical Path", "Task Priority"]
        
        for col in cat_cols:
            if is_training:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
            else:
                le = self.encoders.get(col)
                if le:
                    # handle unseen categories
                    classes = set(le.classes_)
                    df[col] = df[col].apply(lambda x: x if x in classes else 'Unknown')
                    # Add Unknown to encoder classes if it wasn't there
                    if 'Unknown' not in le.classes_:
                        le.classes_ = np.append(le.classes_, 'Unknown')
                    df[col] = le.transform(df[col].astype(str))
                    
        # Feature columns
        feature_cols = ["WBS Level", "Task Duration", "Critical Path", "Task Priority", "Project Type", "Schedule Variance"]
        
        # Fill missing values
        df[feature_cols] = df[feature_cols].fillna(0)
        
        if is_training:
            return df[feature_cols], df["is_delayed"]
        return df[feature_cols], df
        
    def fit(self, milestones_df, tasks_df, projects_df):
        X, y = self.prepare_features(milestones_df, tasks_df, projects_df, is_training=True)
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict_delay_probability(self, milestones_df, tasks_df, projects_df):
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
        X, df_merged = self.prepare_features(milestones_df, tasks_df, projects_df, is_training=False)
        probs = self.model.predict_proba(X)[:, 1]
        df_merged["Predicted Delay Probability (%)"] = np.round(probs * 100, 2)
        df_merged["Predicted Status"] = np.where(probs > 0.5, "Delayed", "On Time")
        return df_merged
        
    def save(self, filepath):
        joblib.dump({"model": self.model, "encoders": self.encoders, "is_trained": self.is_trained}, filepath)
        
    def load(self, filepath):
        data = joblib.load(filepath)
        self.model = data["model"]
        self.encoders = data["encoders"]
        self.is_trained = data["is_trained"]

def monitor_milestones(project_id, milestones_df, current_date_str="2025-06-01"):
    """
    Returns counts and statuses of milestones for a given project.
    """
    p_milestones = milestones_df[milestones_df["Project ID"] == project_id]
    if p_milestones.empty:
        return {
            "completed": [],
            "delayed": [],
            "pending": [],
            "completion_percentage": 100.0
        }
        
    total = len(p_milestones)
    completed = p_milestones[p_milestones["Completion Status"] == "Completed"]
    delayed = p_milestones[p_milestones["Completion Status"] == "Delayed"]
    pending = p_milestones[p_milestones["Completion Status"] == "Pending"]
    
    completion_pct = (len(completed) / total * 100.0) if total > 0 else 100.0
    
    return {
        "total_milestones": total,
        "completed": completed[["Milestone ID", "Milestone Name", "Planned Date", "Actual Date"]].to_dict(orient="records"),
        "delayed": delayed[["Milestone ID", "Milestone Name", "Planned Date"]].to_dict(orient="records"),
        "pending": pending[["Milestone ID", "Milestone Name", "Planned Date"]].to_dict(orient="records"),
        "completion_percentage": round(completion_pct, 2)
    }
