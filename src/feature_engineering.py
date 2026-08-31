import pandas as pd
import numpy as np
from datetime import datetime

def engineer_project_features(projects_df, tasks_df, milestones_df):
    """
    Engineers project-level features from projects, tasks, and milestones dataframes.
    Returns a dataframe of projects with engineered features.
    """
    df_proj = projects_df.copy()
    
    # Pre-parse dates
    df_proj["Project Start Date"] = pd.to_datetime(df_proj["Project Start Date"])
    df_proj["Planned End Date"] = pd.to_datetime(df_proj["Planned End Date"])
    df_proj["Current Date"] = pd.to_datetime(df_proj["Current Date"])
    
    # 1. Days Elapsed & Days Remaining
    df_proj["Days Elapsed"] = (df_proj["Current Date"] - df_proj["Project Start Date"]).dt.days
    df_proj["Days Elapsed"] = df_proj["Days Elapsed"].clip(lower=0)
    
    df_proj["Days Remaining"] = (df_proj["Planned End Date"] - df_proj["Current Date"]).dt.days
    df_proj["Days Remaining"] = df_proj["Days Remaining"].clip(lower=0)
    
    # Add lists to hold engineered features
    actual_progress_list = []
    planned_progress_list = []
    pct_tasks_completed = []
    pct_delayed_tasks = []
    pct_milestones_completed = []
    critical_task_ratio = []
    avg_task_completion_time = []
    critical_path_completion = []
    delayed_critical_tasks_count = []
    
    # Group tasks by project
    tasks_grouped = tasks_df.groupby("Project ID")
    milestones_grouped = milestones_df.groupby("Project ID") if milestones_df is not None else {}
    
    for idx, row in df_proj.iterrows():
        pid = row["Project ID"]
        
        # Tasks features
        if pid in tasks_grouped.groups:
            p_tasks = tasks_grouped.get_group(pid)
            total_tasks = len(p_tasks)
            
            # Progress
            act_prog = p_tasks["Actual Progress (%)"].mean()
            pl_prog = p_tasks["Planned Progress (%)"].mean()
            
            # Task counts by status
            completed_tasks = p_tasks[p_tasks["Task Status"] == "Completed"]
            num_completed = len(completed_tasks)
            
            # Delayed tasks: In Progress or Not Started, but Current Date > Planned End Date
            # Or task took longer to complete than planned
            current_dt_str = row["Current Date"].strftime("%Y-%m-%d")
            delayed_tasks = p_tasks[
                ((p_tasks["Task Status"] != "Completed") & (p_tasks["Planned End Date"] < current_dt_str)) |
                ((p_tasks["Task Status"] == "Completed") & (p_tasks["Actual End Date"] > p_tasks["Planned End Date"]))
            ]
            num_delayed = len(delayed_tasks)
            
            # Critical tasks
            crit_tasks = p_tasks[p_tasks["Critical Path"] == "Yes"]
            num_crit = len(crit_tasks)
            crit_ratio = (num_crit / total_tasks * 100) if total_tasks > 0 else 0
            
            # Critical path completion
            completed_crit = crit_tasks[crit_tasks["Task Status"] == "Completed"]
            crit_comp_pct = (len(completed_crit) / num_crit * 100) if num_crit > 0 else 100.0
            
            # Delayed critical tasks
            delayed_crit = crit_tasks[
                ((crit_tasks["Task Status"] != "Completed") & (crit_tasks["Planned End Date"] < current_dt_str)) |
                ((crit_tasks["Task Status"] == "Completed") & (crit_tasks["Actual End Date"] > crit_tasks["Planned End Date"]))
            ]
            num_delayed_crit = len(delayed_crit)
            
            # Completion times
            avg_comp_time = completed_tasks["Actual Duration"].mean() if num_completed > 0 else 0.0
            
            actual_progress_list.append(act_prog)
            planned_progress_list.append(pl_prog)
            pct_tasks_completed.append(num_completed / total_tasks * 100)
            pct_delayed_tasks.append(num_delayed / total_tasks * 100)
            critical_task_ratio.append(crit_ratio)
            avg_task_completion_time.append(avg_comp_time)
            critical_path_completion.append(crit_comp_pct)
            delayed_critical_tasks_count.append(num_delayed_crit)
        else:
            actual_progress_list.append(0.0)
            planned_progress_list.append(0.0)
            pct_tasks_completed.append(0.0)
            pct_delayed_tasks.append(0.0)
            critical_task_ratio.append(0.0)
            avg_task_completion_time.append(0.0)
            critical_path_completion.append(0.0)
            delayed_critical_tasks_count.append(0)
            
        # Milestones features
        if milestones_df is not None and pid in milestones_grouped.groups:
            p_milestones = milestones_grouped.get_group(pid)
            total_m = len(p_milestones)
            comp_m = len(p_milestones[p_milestones["Completion Status"] == "Completed"])
            pct_m_comp = (comp_m / total_m * 100) if total_m > 0 else 100.0
            pct_milestones_completed.append(pct_m_comp)
        else:
            pct_milestones_completed.append(0.0)
            
    df_proj["Actual Progress (%)"] = actual_progress_list
    df_proj["Planned Progress (%)"] = planned_progress_list
    
    # 2. Completion Ratios
    df_proj["Planned Completion Ratio"] = (df_proj["Days Elapsed"] / df_proj["Planned Duration (Days)"]).clip(upper=1.0)
    df_proj["Actual Completion Ratio"] = df_proj["Actual Progress (%)"] / 100.0
    
    # 3. Schedule & Progress Variances
    df_proj["Schedule Variance"] = df_proj["Actual Progress (%)"] - df_proj["Planned Progress (%)"]
    df_proj["Progress Variance"] = df_proj["Actual Progress (%)"] - df_proj["Planned Progress (%)"]
    df_proj["Percentage Difference"] = (df_proj["Schedule Variance"] / (df_proj["Planned Progress (%)"] + 1e-6)) * 100
    
    df_proj["Percentage of Tasks Completed"] = pct_tasks_completed
    df_proj["Percentage of Delayed Tasks"] = pct_delayed_tasks
    df_proj["Percentage of Milestones Completed"] = pct_milestones_completed
    df_proj["Critical Task Ratio"] = critical_task_ratio
    df_proj["Average Task Completion Time"] = avg_task_completion_time
    df_proj["Critical Path Completion (%)"] = critical_path_completion
    df_proj["Delayed Critical Tasks Count"] = delayed_critical_tasks_count
    
    # Classify projects based on Schedule Variance
    # Ahead: SV > 2%
    # Behind: SV < -2%
    # On Schedule: -2% <= SV <= 2%
    conditions = [
        (df_proj["Schedule Variance"] > 2.0),
        (df_proj["Schedule Variance"] < -2.0)
    ]
    choices = ["Ahead of Schedule", "Behind of Schedule"] # behind of schedule isBehind
    df_proj["Schedule Status"] = np.select(conditions, choices, default="On Schedule")
    
    # Project Delay prediction target (for regression: Actual Duration - Planned Duration)
    df_proj["Delay (Days)"] = df_proj["Actual Duration (Days)"] - df_proj["Planned Duration (Days)"]
    
    # Project Delay classification target:
    # On Time: delay <= 0
    # Slightly Delayed: 1-10 days
    # Moderately Delayed: 11-30 days
    # Severely Delayed: > 30 days
    delay_conditions = [
        (df_proj["Delay (Days)"] <= 0),
        (df_proj["Delay (Days)"] > 0) & (df_proj["Delay (Days)"] <= 10),
        (df_proj["Delay (Days)"] > 10) & (df_proj["Delay (Days)"] <= 30),
        (df_proj["Delay (Days)"] > 30)
    ]
    delay_classes = ["On Time", "Slightly Delayed", "Moderately Delayed", "Severely Delayed"]
    df_proj["Delay Classification"] = np.select(delay_conditions, delay_classes, default="On Time")
    
    return df_proj
