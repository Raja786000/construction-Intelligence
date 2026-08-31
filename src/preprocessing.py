import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

def load_all_data(data_dir):
    """Loads all generated CSV files from data directory."""
    files = {
        "projects": "projects.csv",
        "tasks": "tasks.csv",
        "milestones": "milestones.csv",
        "daily": "daily_reports.csv",
        "weekly": "weekly_reports.csv"
    }
    
    data = {}
    for name, filename in files.items():
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            data[name] = pd.read_csv(filepath)
            print(f"Loaded {filename} with shape {data[name].shape}")
        else:
            print(f"Warning: {filename} not found in {data_dir}")
            data[name] = None
    return data

def clean_dataframe(df):
    """Removes duplicates and handles missing values."""
    if df is None:
        return None
    
    # Remove duplicates
    initial_shape = df.shape
    df = df.drop_duplicates()
    if df.shape != initial_shape:
        print(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows.")
        
    # Handle missing values
    # For categorical columns, fill with 'Unknown'
    cat_cols = df.select_dtypes(include=['object']).columns
    df[cat_cols] = df[cat_cols].fillna("Unknown")
    
    # For numerical columns, fill with median
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
            
    return df

def convert_dates_to_numeric(df, date_cols, ref_date_col=None):
    """Converts date fields to numerical representation (days from a reference date)."""
    df = df.copy()
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
        
    if ref_date_col:
        ref_date = pd.to_datetime(df[ref_date_col])
        for col in date_cols:
            if col != ref_date_col:
                df[f"{col}_Days_From_Ref"] = (df[col] - ref_date).dt.days
    else:
        # Default: days since the minimum date in the column
        for col in date_cols:
            min_date = df[col].min()
            df[f"{col}_Elapsed_Days"] = (df[col] - min_date).dt.days
            
    return df

class MultiColumnLabelEncoder:
    """Label encodes multiple columns and stores encoders for inverse transform."""
    def __init__(self, columns=None):
        self.columns = columns
        self.encoders = {}
        
    def fit(self, df):
        columns = self.columns if self.columns else df.select_dtypes(include=['object']).columns
        for col in columns:
            le = LabelEncoder()
            # Handle unseen classes by adding an 'Unknown' class
            unique_vals = list(df[col].unique())
            if 'Unknown' not in unique_vals:
                unique_vals.append('Unknown')
            le.fit(unique_vals)
            self.encoders[col] = le
        return self
        
    def transform(self, df):
        df = df.copy()
        columns = self.columns if self.columns else df.select_dtypes(include=['object']).columns
        for col in columns:
            if col in self.encoders:
                # Map unseen classes to 'Unknown'
                le = self.encoders[col]
                classes = set(le.classes_)
                df[col] = df[col].apply(lambda x: x if x in classes else 'Unknown')
                df[col] = le.transform(df[col])
        return df

def split_projects_train_val_test(projects_df, train_size=0.7, val_size=0.15, test_size=0.15, random_state=42):
    """Splits project IDs into train, validation, and test sets to avoid data leakage."""
    project_ids = projects_df["Project ID"].unique()
    
    train_ids, test_val_ids = train_test_split(project_ids, test_size=(val_size + test_size), random_state=random_state)
    val_ids, test_ids = train_test_split(test_val_ids, test_size=(test_size / (val_size + test_size)), random_state=random_state)
    
    return set(train_ids), set(val_ids), set(test_ids)

def filter_by_project_ids(df, project_ids):
    """Filters a dataframe to only contain rows belonging to specific Project IDs."""
    if df is None:
        return None
    return df[df["Project ID"].isin(project_ids)].copy()
