import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from sklearn.ensemble import RandomForestClassifier
# pyrefly: ignore [missing-import]
from xgboost import XGBClassifier
# pyrefly: ignore [missing-import]
from lightgbm import LGBMClassifier
from sklearn.preprocessing import LabelEncoder
# pyrefly: ignore [missing-import]
import joblib
import os

class DelayClassifier:
    def __init__(self, model_type="xgboost"):
        self.model_type = model_type
        if model_type == "xgboost":
            self.model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric="mlogloss")
        elif model_type == "lightgbm":
            self.model = LGBMClassifier(n_estimators=100, max_depth=6, random_state=42)
        else:
            self.model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
            
        self.type_encoder = LabelEncoder()
        self.target_encoder = LabelEncoder()
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
            
        # Target
        if is_training:
            # Map delay classes into integers starting from 0
            df["Target"] = self.target_encoder.fit_transform(df["Delay Classification"])
            return df[self.feature_cols], df["Target"]
            
        return df[self.feature_cols], df
        
    def fit(self, df_projects):
        X, y = self.prepare_data(df_projects, is_training=True)
        self.model.fit(X, y)
        self.is_trained = True
        
    def predict(self, df_projects):
        if not self.is_trained:
            raise ValueError("Model not trained yet.")
        X, df_orig = self.prepare_data(df_projects, is_training=False)
        preds = self.model.predict(X)
        probs = self.model.predict_proba(X)
        
        # Inverse transform classes
        pred_labels = self.target_encoder.inverse_transform(preds)
        
        # Calculate delay probability: sum of probabilities for Slightly, Moderately, Severely Delayed
        # Let's map delay classes to check which index corresponds to On Time
        classes_list = list(self.target_encoder.classes_)
        on_time_idx = classes_list.index("On Time") if "On Time" in classes_list else -1
        
        if on_time_idx != -1:
            delay_prob = (1.0 - probs[:, on_time_idx]) * 100.0
        else:
            delay_prob = np.max(probs, axis=1) * 100.0 # fallback
            
        return pred_labels, np.round(delay_prob, 2), probs
        
    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        joblib.dump(self.model, os.path.join(filepath_dir, "delay_classifier.pkl"))
        joblib.dump(self.type_encoder, os.path.join(filepath_dir, "delay_type_encoder.pkl"))
        joblib.dump(self.target_encoder, os.path.join(filepath_dir, "delay_target_encoder.pkl"))
        
    def load(self, filepath_dir):
        self.model = joblib.load(os.path.join(filepath_dir, "delay_classifier.pkl"))
        self.type_encoder = joblib.load(os.path.join(filepath_dir, "delay_type_encoder.pkl"))
        self.target_encoder = joblib.load(os.path.join(filepath_dir, "delay_target_encoder.pkl"))
        self.is_trained = True
