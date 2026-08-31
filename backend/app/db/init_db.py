import os
import pandas as pd
from app.db.connection import db
from src.preprocessing import clean_dataframe
from src.feature_engineering import engineer_project_features

def seed_database(workspace_dir=None):
    if not workspace_dir:
        workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    data_dir = os.path.join(workspace_dir, "data")
    print(f"Seeding database using data from: {data_dir}")

    # Read CSV files
    projects_csv = os.path.join(data_dir, "projects.csv")
    tasks_csv = os.path.join(data_dir, "tasks.csv")
    milestones_csv = os.path.join(data_dir, "milestones.csv")

    if not os.path.exists(projects_csv) or not os.path.exists(tasks_csv) or not os.path.exists(milestones_csv):
        print("Error: Seeding source CSV files not found. Please run src/data_generator.py first.")
        return False

    df_p = clean_dataframe(pd.read_csv(projects_csv))
    df_t = clean_dataframe(pd.read_csv(tasks_csv))
    df_m = clean_dataframe(pd.read_csv(milestones_csv))

    # Calculate engineered project features so we have progress and schedule variance pre-calculated!
    print("Calculating engineered project features for database seeding...")
    df_proj_feat = engineer_project_features(df_p, df_t, df_m)

    # Clean existing collections
    db["projects"].delete_many({})
    db["tasks"].delete_many({})
    db["milestones"].delete_many({})
    db["predictions"].delete_many({})
    db["reports"].delete_many({})

    # Process Projects from engineered features
    projects_list = []
    for _, row in df_proj_feat.iterrows():
        p_id = str(row["Project ID"])
        projects_list.append({
            "_id": p_id,
            "name": str(row["Project Name"]),
            "type": str(row["Project Type"]),
            "start_date": str(row["Project Start Date"]),
            "planned_end_date": str(row["Planned End Date"]),
            "current_date": str(row["Current Date"]),
            "planned_duration": int(row["Planned Duration (Days)"]),
            "actual_duration": int(row["Actual Duration (Days)"]),
            "actual_progress": float(row["Actual Progress (%)"]),
            "planned_progress": float(row["Planned Progress (%)"]),
            "schedule_variance": float(row["Schedule Variance"]),
            "schedule_status": str(row["Schedule Status"])
        })

    # Process Tasks
    tasks_list = []
    for _, row in df_t.iterrows():
        time_dev = int(row["Actual Duration"] - row["Task Duration"])
        tasks_list.append({
            "_id": str(row["Task ID"]),
            "project_id": str(row["Project ID"]),
            "name": str(row["Task Name"]),
            "start_date": str(row["Actual Start Date"]),
            "end_date": str(row["Actual End Date"]),
            "planned_start": str(row["Planned Start Date"]),
            "planned_end": str(row["Planned End Date"]),
            "progress": float(row["Actual Progress (%)"]),
            "planned_progress": float(row["Planned Progress (%)"]),
            "status": str(row["Task Status"]),
            "is_critical": bool(row["Critical Path"] == "Yes" or row["Critical Path"] == True),
            "actual_duration": int(row["Actual Duration"]),
            "task_duration": int(row["Task Duration"]),
            "time_deviation": time_dev,
            "priority": str(row["Task Priority"])
        })

    # Process Milestones
    milestones_list = []
    for _, row in df_m.iterrows():
        milestones_list.append({
            "_id": str(row["Milestone ID"]),
            "project_id": str(row["Project ID"]),
            "name": str(row["Milestone Name"]),
            "due_date": str(row["Planned Date"]),
            "status": str(row["Completion Status"]),
            "completion_date": str(row["Actual Date"]) if pd.notna(row["Actual Date"]) else None
        })

    # Insert into collections
    db["projects"].insert_many(projects_list)
    db["tasks"].insert_many(tasks_list)
    db["milestones"].insert_many(milestones_list)

    print(f"Successfully seeded {len(projects_list)} projects, {len(tasks_list)} tasks, and {len(milestones_list)} milestones.")

    # Create the 3 mandatory demonstration projects: P001, P002, P003
    create_demo_projects()
    return True

def create_demo_projects():
    print("Creating E2E demo projects: P001 (Behind), P002 (On Schedule), P003 (Ahead)...")

    # P001: Behind Schedule
    db["projects"].delete_many({"_id": "P001"})
    db["projects"].insert_one({
        "_id": "P001",
        "name": "Commercial Plaza Plaza (P001)",
        "type": "Commercial",
        "start_date": "2023-01-01",
        "planned_end_date": "2023-01-31",
        "current_date": "2023-01-22",
        "planned_duration": 30,
        "actual_duration": 30,
        "actual_progress": 42.0,
        "planned_progress": 55.0,
        "schedule_variance": -13.0,
        "schedule_status": "Behind of Schedule"
    })
    
    # Clean and add tasks for P001
    db["tasks"].delete_many({"project_id": "P001"})
    p001_tasks = [
        {"_id": "T_P001_1", "project_id": "P001", "name": "Excavation and Site Prep", "start_date": "2023-01-01", "end_date": "2023-01-08", "planned_start": "2023-01-01", "planned_end": "2023-01-06", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 7, "task_duration": 5, "time_deviation": 2, "priority": "High"},
        {"_id": "T_P001_2", "project_id": "P001", "name": "Foundation Concrete Pouring", "start_date": "2023-01-08", "end_date": "2023-01-20", "planned_start": "2023-01-06", "planned_end": "2023-01-14", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 12, "task_duration": 8, "time_deviation": 4, "priority": "High"},
        {"_id": "T_P001_3", "project_id": "P001", "name": "Steel Framing Erection", "start_date": "2023-01-20", "end_date": "2023-02-05", "planned_start": "2023-01-14", "planned_end": "2023-01-22", "progress": 30.0, "planned_progress": 80.0, "status": "In Progress", "is_critical": True, "actual_duration": 16, "task_duration": 8, "time_deviation": 8, "priority": "Critical"},
        {"_id": "T_P001_4", "project_id": "P001", "name": "Brickwork and Masonry", "start_date": "2023-01-22", "end_date": "2023-02-12", "planned_start": "2023-01-20", "planned_end": "2023-01-28", "progress": 10.0, "planned_progress": 40.0, "status": "In Progress", "is_critical": False, "actual_duration": 21, "task_duration": 8, "time_deviation": 13, "priority": "Medium"}
    ]
    db["tasks"].insert_many(p001_tasks)

    # Clean and add milestones for P001
    db["milestones"].delete_many({"project_id": "P001"})
    p001_milestones = [
        {"_id": "M_P001_1", "project_id": "P001", "name": "Substructure Complete", "due_date": "2023-01-14", "status": "Completed", "completion_date": "2023-01-20"},
        {"_id": "M_P001_2", "project_id": "P001", "name": "Framing Complete", "due_date": "2023-01-22", "status": "In Progress", "completion_date": None}
    ]
    db["milestones"].insert_many(p001_milestones)


    # P002: On Schedule
    db["projects"].delete_many({"_id": "P002"})
    db["projects"].insert_one({
        "_id": "P002",
        "name": "Community Health Center (P002)",
        "type": "Institutional",
        "start_date": "2023-01-05",
        "planned_end_date": "2023-02-04",
        "current_date": "2023-01-22",
        "planned_duration": 30,
        "actual_duration": 30,
        "actual_progress": 50.0,
        "planned_progress": 50.0,
        "schedule_variance": 0.0,
        "schedule_status": "On Schedule"
    })
    
    db["tasks"].delete_many({"project_id": "P002"})
    p002_tasks = [
        {"_id": "T_P002_1", "project_id": "P002", "name": "Land Survey & Grading", "start_date": "2023-01-05", "end_date": "2023-01-10", "planned_start": "2023-01-05", "planned_end": "2023-01-10", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 5, "task_duration": 5, "time_deviation": 0, "priority": "Medium"},
        {"_id": "T_P002_2", "project_id": "P002", "name": "Foundation Footings", "start_date": "2023-01-10", "end_date": "2023-01-20", "planned_start": "2023-01-10", "planned_end": "2023-01-20", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 10, "task_duration": 10, "time_deviation": 0, "priority": "High"},
        {"_id": "T_P002_3", "project_id": "P002", "name": "Exterior Wall Framing", "start_date": "2023-01-20", "end_date": "2023-01-30", "planned_start": "2023-01-20", "planned_end": "2023-01-30", "progress": 50.0, "planned_progress": 50.0, "status": "In Progress", "is_critical": True, "actual_duration": 10, "task_duration": 10, "time_deviation": 0, "priority": "Medium"}
    ]
    db["tasks"].insert_many(p002_tasks)

    db["milestones"].delete_many({"project_id": "P002"})
    p002_milestones = [
        {"_id": "M_P002_1", "project_id": "P002", "name": "Foundation Approved", "due_date": "2023-01-20", "status": "Completed", "completion_date": "2023-01-20"},
        {"_id": "M_P002_2", "project_id": "P002", "name": "Walls Framed", "due_date": "2023-01-30", "status": "In Progress", "completion_date": None}
    ]
    db["milestones"].insert_many(p002_milestones)


    # P003: Ahead of Schedule
    db["projects"].delete_many({"_id": "P003"})
    db["projects"].insert_one({
        "_id": "P003",
        "name": "Highway Overpass B (P003)",
        "type": "Infrastructure",
        "start_date": "2023-01-02",
        "planned_end_date": "2023-02-01",
        "current_date": "2023-01-22",
        "planned_duration": 30,
        "actual_duration": 30,
        "actual_progress": 70.0,
        "planned_progress": 55.0,
        "schedule_variance": 15.0,
        "schedule_status": "Ahead of Schedule"
    })
    
    db["tasks"].delete_many({"project_id": "P003"})
    p003_tasks = [
        {"_id": "T_P003_1", "project_id": "P003", "name": "Soil Boring & Testing", "start_date": "2023-01-02", "end_date": "2023-01-05", "planned_start": "2023-01-02", "planned_end": "2023-01-07", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 3, "task_duration": 5, "time_deviation": -2, "priority": "Medium"},
        {"_id": "T_P003_2", "project_id": "P003", "name": "Subgrade Compaction", "start_date": "2023-01-05", "end_date": "2023-01-12", "planned_start": "2023-01-07", "planned_end": "2023-01-16", "progress": 100.0, "planned_progress": 100.0, "status": "Completed", "is_critical": True, "actual_duration": 7, "task_duration": 9, "time_deviation": -2, "priority": "Medium"},
        {"_id": "T_P003_3", "project_id": "P003", "name": "Abutment Concrete Reinforcement", "start_date": "2023-01-12", "end_date": "2023-01-25", "planned_start": "2023-01-16", "planned_end": "2023-01-28", "progress": 75.0, "planned_progress": 70.0, "status": "In Progress", "is_critical": True, "actual_duration": 13, "task_duration": 12, "time_deviation": 1, "priority": "High"}
    ]
    db["tasks"].insert_many(p003_tasks)

    db["milestones"].delete_many({"project_id": "P003"})
    p003_milestones = [
        {"_id": "M_P003_1", "project_id": "P003", "name": "Subgrade Pass", "due_date": "2023-01-16", "status": "Completed", "completion_date": "2023-01-12"},
        {"_id": "M_P003_2", "project_id": "P003", "name": "Piers Completed", "due_date": "2023-01-28", "status": "In Progress", "completion_date": None}
    ]
    db["milestones"].insert_many(p003_milestones)

    print("Successfully created demo projects (P001, P002, P003) in database.")

if __name__ == "__main__":
    seed_database()
