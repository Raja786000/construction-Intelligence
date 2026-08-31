import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime, timedelta

class CompletionDateRegressor:
    def __init__(self, model_type="xgboost"):
        self.model_type = model_type
        if model_type == "xgboost":
            self.model = XGBRegressor(n_estimators=100, max_depth=6, random_state=42)
        else:
            self.model = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
            
        self.type_encoder = LabelEncoder()
        self.feature_cols = [
            "Project Type", "Planned Duration (Days)", "Days Elapsed", "Days Remaining",
            "Planned Progress (%)", "Actual Progress (%)", "Schedule Variance", 
            "Planned Completion Ratio", "Actual Completion Ratio",
            "Percentage of Tasks Completed", "Percentage of Delayed Tasks", 
            "Percentage of Milestones Completed", "Critical Task Ratio", 
            "Average Task Completion Time", "Critical Path Completion (%)", 
            "Delayed Critical Tasks Count"
        ]
        self.is_trained = False
        
    def prepare_data(self, df_projects, is_training=True):
        df = df_projects.copy()
        
        # Categorical encode Project Type
        if is_training:
            df["Project Type"] = self.type_encoder.fit_transform(df["Project Type"].astype(str))
        else:
            classes = set(self.type_encoder.classes_)
            df["Project Type"] = df["Project Type"].apply(lambda x: x if x in classes else 'Unknown')
            if 'Unknown' not in self.type_encoder.classes_:
                self.type_encoder.classes_ = np.append(self.type_encoder.classes_, 'Unknown')
            df["Project Type"] = self.type_encoder.transform(df["Project Type"].astype(str))
            
        # Target: Delay (Days)
        if is_training:
            return df[self.feature_cols], df["Delay (Days)"]
            
        return df[self.feature_cols], df
        
    def fit(self, df_projects):
        X, y = self.prepare_data(df_projects, is_training=True)
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict_completion(self, df_projects):
        if not self.is_trained:
            raise ValueError("Model not trained yet.")
            
        X, df_orig = self.prepare_data(df_projects, is_training=False)
        pred_delays = self.model.predict(X)
        
        # Predicted delay in days
        df_orig["Predicted Delay (Days)"] = np.round(pred_delays).astype(int)
        
        # Calculate predicted completion date
        pred_dates = []
        for idx, row in df_orig.iterrows():
            planned_end = pd.to_datetime(row["Planned End Date"])
            pred_delay = row["Predicted Delay (Days)"]
            pred_date = planned_end + timedelta(days=int(pred_delay))
            pred_dates.append(pred_date.strftime("%Y-%m-%d"))
            
        df_orig["Predicted Completion Date"] = pred_dates
        
        return df_orig["Predicted Delay (Days)"].values, df_orig["Predicted Completion Date"].values
        
    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        joblib.dump(self.model, os.path.join(filepath_dir, "completion_regressor.pkl"))
        joblib.dump(self.type_encoder, os.path.join(filepath_dir, "completion_type_encoder.pkl"))
        
    def load(self, filepath_dir):
        self.model = joblib.load(os.path.join(filepath_dir, "completion_regressor.pkl"))
        self.type_encoder = joblib.load(os.path.join(filepath_dir, "completion_type_encoder.pkl"))
        self.is_trained = True
