import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class ProgressPredictor:
    def __init__(self, model_type="xgboost"):
        self.model_type = model_type
        if model_type == "xgboost":
            self.model_next_week = XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
            self.model_next_month = XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
        else:
            self.model_next_week = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
            self.model_next_month = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
            
        self.type_encoder = LabelEncoder()
        self.feature_cols = [
            "Project Type", "Planned Duration (Days)", "Days Elapsed", 
            "Planned Progress (%)", "Current Progress (%)", "Schedule Variance",
            "Tasks Completed Ratio", "Delayed Tasks Ratio"
        ]
        self.is_trained = False
        
    def prepare_data(self, weekly_df, projects_df, is_training=True):
        """
        Creates features and targets for each project-week observation.
        """
        # Join weekly reports with project details
        df = weekly_df.merge(
            projects_df[["Project ID", "Project Type", "Planned Duration (Days)", "Actual Duration (Days)"]],
            on="Project ID",
            how="left"
        )
        
        # Calculate days elapsed (Week Number * 7)
        df["Days Elapsed"] = df["Week Number"] * 7
        df["Current Progress (%)"] = df["Actual Weekly Progress"]
        df["Planned Progress (%)"] = df["Planned Weekly Progress"]
        df["Schedule Variance"] = df["Weekly Schedule Variance"]
        
        # Compute tasks status at this week from tasks or approximate
        # Let's approximate based on progress
        df["Tasks Completed Ratio"] = (df["Current Progress (%)"] / 100.0) * 0.9 # approximation
        df["Delayed Tasks Ratio"] = np.where(df["Schedule Variance"] < 0, np.abs(df["Schedule Variance"]) / 100.0, 0.0)
        
        # Categorical encode Project Type
        if is_training:
            df["Project Type"] = self.type_encoder.fit_transform(df["Project Type"].astype(str))
        else:
            classes = set(self.type_encoder.classes_)
            df["Project Type"] = df["Project Type"].apply(lambda x: x if x in classes else 'Unknown')
            if 'Unknown' not in self.type_encoder.classes_:
                self.type_encoder.classes_ = np.append(self.type_encoder.classes_, 'Unknown')
            df["Project Type"] = self.type_encoder.transform(df["Project Type"].astype(str))
            
        if is_training:
            # Shift targets: target for row of week w is the progress at week w + 1, and w + 4
            next_week_target = []
            next_month_target = []
            
            # Group by Project ID
            for pid, group in df.groupby("Project ID"):
                group = group.sort_values("Week Number")
                progress_vals = group["Current Progress (%)"].values
                weeks = group["Week Number"].values
                
                for idx in range(len(group)):
                    # Next week progress (w+1 index)
                    if idx + 1 < len(group):
                        next_week_target.append(progress_vals[idx + 1])
                    else:
                        next_week_target.append(100.0)
                        
                    # Next month progress (w+4 index)
                    if idx + 4 < len(group):
                        next_month_target.append(progress_vals[idx + 4])
                    else:
                        next_month_target.append(100.0)
                        
            df["Target_Next_Week"] = next_week_target
            df["Target_Next_Month"] = next_month_target
            
            return df[self.feature_cols], df["Target_Next_Week"], df["Target_Next_Month"]
            
        return df[self.feature_cols], df
        
    def fit(self, weekly_df, projects_df):
        X, y_week, y_month = self.prepare_data(weekly_df, projects_df, is_training=True)
        self.model_next_week.fit(X, y_week)
        self.model_next_month.fit(X, y_month)
        self.is_trained = True
        
    def predict_progress(self, current_state_df):
        """
        Takes current state of projects and predicts next week and next month progress.
        current_state_df should have features: 
        ['Project Type', 'Planned Duration (Days)', 'Days Elapsed', 'Planned Progress (%)', 
         'Current Progress (%)', 'Schedule Variance', 'Tasks Completed Ratio', 'Delayed Tasks Ratio']
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
            
        # Encode Project Type
        df = current_state_df.copy()
        if "Project Type" in df.columns and not pd.api.types.is_integer_dtype(df["Project Type"]):
            classes = set(self.type_encoder.classes_)
            df["Project Type"] = df["Project Type"].apply(lambda x: x if x in classes else 'Unknown')
            df["Project Type"] = self.type_encoder.transform(df["Project Type"].astype(str))
            
        X = df[self.feature_cols].fillna(0)
        
        pred_week = self.model_next_week.predict(X)
        pred_month = self.model_next_month.predict(X)
        
        # Clip outputs to range [current_progress, 100.0]
        curr_prog = df["Current Progress (%)"].values
        pred_week = np.clip(pred_week, curr_prog, 100.0)
        pred_month = np.clip(pred_month, curr_prog, 100.0)
        
        # Ensure month progress >= week progress
        pred_month = np.maximum(pred_month, pred_week)
        
        return np.round(pred_week, 2), np.round(pred_month, 2)
        
    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        joblib.dump(self.model_next_week, os.path.join(filepath_dir, "progress_week.pkl"))
        joblib.dump(self.model_next_month, os.path.join(filepath_dir, "progress_month.pkl"))
        joblib.dump(self.type_encoder, os.path.join(filepath_dir, "progress_encoder.pkl"))
        
    def load(self, filepath_dir):
        self.model_next_week = joblib.load(os.path.join(filepath_dir, "progress_week.pkl"))
        self.model_next_month = joblib.load(os.path.join(filepath_dir, "progress_month.pkl"))
        self.type_encoder = joblib.load(os.path.join(filepath_dir, "progress_encoder.pkl"))
        self.is_trained = True
