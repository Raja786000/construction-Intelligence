import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class ProgressForecaster:
    def __init__(self):
        # We train regressors for Next Day, Next Week, Next Month, and Days to Completion
        self.model_next_day = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.model_next_week = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.model_next_month = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.model_days_to_finish = XGBRegressor(n_estimators=100, max_depth=5, random_state=42)
        
        self.type_encoder = LabelEncoder()
        self.is_trained = False
        
    def prepare_lags(self, daily_df, projects_df, is_training=True):
        """
        Creates lag features for the time-series forecasting.
        Lags: y(t), y(t-1), y(t-2), y(t-3) days.
        """
        # Join with project type and planned duration
        df = daily_df.merge(
            projects_df[["Project ID", "Project Type", "Planned Duration (Days)", "Actual Duration (Days)"]],
            on="Project ID",
            how="left"
        )
        
        # Encode Project Type
        if is_training:
            df["Project Type"] = self.type_encoder.fit_transform(df["Project Type"].astype(str))
        else:
            classes = set(self.type_encoder.classes_)
            df["Project Type"] = df["Project Type"].apply(lambda x: x if x in classes else 'Unknown')
            if 'Unknown' not in self.type_encoder.classes_:
                self.type_encoder.classes_ = np.append(self.type_encoder.classes_, 'Unknown')
            df["Project Type"] = self.type_encoder.transform(df["Project Type"].astype(str))
            
        # Group by Project ID and create lags
        X_list = []
        y_day_list = []
        y_week_list = []
        y_month_list = []
        y_finish_list = []
        
        feature_cols = ["Project Type", "Planned Duration (Days)", "Prog_t", "Prog_t_1", "Prog_t_2", "Prog_t_3"]
        
        for pid, group in df.groupby("Project ID"):
            group = group.sort_values("Report Date")
            prog = group["Daily Progress Percentage"].values
            act_duration = group["Actual Duration (Days)"].iloc[0]
            proj_type = group["Project Type"].iloc[0]
            planned_dur = group["Planned Duration (Days)"].iloc[0]
            
            # We need at least 4 daily reports to create lags (t, t-1, t-2, t-3)
            if len(group) < 4:
                continue
                
            for t in range(3, len(group)):
                # Lags
                prog_t = prog[t]
                prog_t_1 = prog[t-1]
                prog_t_2 = prog[t-2]
                prog_t_3 = prog[t-3]
                
                # We only predict/train for points where progress is < 100%
                if prog_t >= 100.0 and is_training:
                    continue
                    
                features = [proj_type, planned_dur, prog_t, prog_t_1, prog_t_2, prog_t_3]
                X_list.append(features)
                
                if is_training:
                    # Target Next Day (t + 1)
                    y_day = prog[t+1] if t+1 < len(group) else 100.0
                    
                    # Target Next Week (t + 7)
                    y_week = prog[t+7] if t+7 < len(group) else 100.0
                    
                    # Target Next Month (t + 30)
                    y_month = prog[t+30] if t+30 < len(group) else 100.0
                    
                    # Days to completion: act_duration - elapsed days at t
                    days_elapsed = t
                    y_finish = max(act_duration - days_elapsed, 0)
                    
                    y_day_list.append(y_day)
                    y_week_list.append(y_week)
                    y_month_list.append(y_month)
                    y_finish_list.append(y_finish)
                    
        X_df = pd.DataFrame(X_list, columns=feature_cols)
        
        if is_training:
            return X_df, np.array(y_day_list), np.array(y_week_list), np.array(y_month_list), np.array(y_finish_list)
        return X_df
        
    def fit(self, daily_df, projects_df):
        X, y_day, y_week, y_month, y_finish = self.prepare_lags(daily_df, projects_df, is_training=True)
        
        print("Training Next Day Forecaster...")
        self.model_next_day.fit(X, y_day)
        
        print("Training Next Week Forecaster...")
        self.model_next_week.fit(X, y_week)
        
        print("Training Next Month Forecaster...")
        self.model_next_month.fit(X, y_month)
        
        print("Training Days to Finish Forecaster...")
        self.model_days_to_finish.fit(X, y_finish)
        
        self.is_trained = True
        
    def forecast(self, current_forecast_df):
        """
        current_forecast_df schema:
        ['Project Type', 'Planned Duration (Days)', 'Prog_t', 'Prog_t_1', 'Prog_t_2', 'Prog_t_3']
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")
            
        df = current_forecast_df.copy()
        
        # Encode Project Type
        if "Project Type" in df.columns and not pd.api.types.is_integer_dtype(df["Project Type"]):
            classes = set(self.type_encoder.classes_)
            df["Project Type"] = df["Project Type"].apply(lambda x: x if x in classes else 'Unknown')
            df["Project Type"] = self.type_encoder.transform(df["Project Type"].astype(str))
            
        feature_cols = ["Project Type", "Planned Duration (Days)", "Prog_t", "Prog_t_1", "Prog_t_2", "Prog_t_3"]
        X = df[feature_cols].fillna(0)
        
        pred_day = self.model_next_day.predict(X)
        pred_week = self.model_next_week.predict(X)
        pred_month = self.model_next_month.predict(X)
        pred_finish_days = self.model_days_to_finish.predict(X)
        
        # Clip progress predictions
        curr_prog = df["Prog_t"].values
        pred_day = np.clip(pred_day, curr_prog, 100.0)
        pred_week = np.clip(pred_week, pred_day, 100.0)
        pred_month = np.clip(pred_month, pred_week, 100.0)
        pred_finish_days = np.clip(pred_finish_days, 0, None)
        
        return {
            "Next Day Progress (%)": np.round(pred_day, 2),
            "Next Week Progress (%)": np.round(pred_week, 2),
            "Next Month Progress (%)": np.round(pred_month, 2),
            "Estimated Days to Completion": np.round(pred_finish_days).astype(int)
        }
        
    def save(self, filepath_dir):
        os.makedirs(filepath_dir, exist_ok=True)
        joblib.dump(self.model_next_day, os.path.join(filepath_dir, "forecaster_day.pkl"))
        joblib.dump(self.model_next_week, os.path.join(filepath_dir, "forecaster_week.pkl"))
        joblib.dump(self.model_next_month, os.path.join(filepath_dir, "forecaster_month.pkl"))
        joblib.dump(self.model_days_to_finish, os.path.join(filepath_dir, "forecaster_finish.pkl"))
        joblib.dump(self.type_encoder, os.path.join(filepath_dir, "forecaster_encoder.pkl"))
        
    def load(self, filepath_dir):
        self.model_next_day = joblib.load(os.path.join(filepath_dir, "forecaster_day.pkl"))
        self.model_next_week = joblib.load(os.path.join(filepath_dir, "forecaster_week.pkl"))
        self.model_next_month = joblib.load(os.path.join(filepath_dir, "forecaster_month.pkl"))
        self.model_days_to_finish = joblib.load(os.path.join(filepath_dir, "forecaster_finish.pkl"))
        self.type_encoder = joblib.load(os.path.join(filepath_dir, "forecaster_encoder.pkl"))
        self.is_trained = True
