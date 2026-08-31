import pandas as pd

def analyze_critical_path(project_id, tasks_df, current_date_str="2025-06-01"):
    """
    Analyzes tasks on the critical path for a given project.
    """
    p_tasks = tasks_df[tasks_df["Project ID"] == project_id]
    if p_tasks.empty:
        return {
            "project_id": project_id,
            "critical_tasks": [],
            "delayed_critical_tasks": [],
            "critical_path_completion_pct": 0.0
        }
        
    crit_tasks = p_tasks[p_tasks["Critical Path"] == "Yes"]
    total_crit = len(crit_tasks)
    
    # Completed critical tasks
    completed_crit = crit_tasks[crit_tasks["Task Status"] == "Completed"]
    completed_crit_ids = completed_crit["Task ID"].tolist()
    
    # Delayed critical tasks
    # Delayed if:
    # 1. Not completed and current_date > planned_end_date
    # 2. Completed but actual_end_date > planned_end_date
    delayed_crit = crit_tasks[
        ((crit_tasks["Task Status"] != "Completed") & (crit_tasks["Planned End Date"] < current_date_str)) |
        ((crit_tasks["Task Status"] == "Completed") & (crit_tasks["Actual End Date"] > crit_tasks["Planned End Date"]))
    ]
    delayed_crit_list = delayed_crit[["Task ID", "Task Name", "Planned End Date", "Actual End Date", "Task Status"]].to_dict(orient="records")
    
    crit_comp_pct = (len(completed_crit) / total_crit * 100) if total_crit > 0 else 100.0
    
    return {
        "project_id": project_id,
        "total_critical_tasks": total_crit,
        "critical_tasks": crit_tasks[["Task ID", "Task Name", "Task Status", "Task Priority"]].to_dict(orient="records"),
        "delayed_critical_tasks": delayed_crit_list,
        "critical_path_completion_pct": round(crit_comp_pct, 2)
    }
