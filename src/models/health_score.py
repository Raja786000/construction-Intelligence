import pandas as pd
import numpy as np

def calculate_project_health_score(project_row, tasks_df=None, milestones_df=None, current_date_str="2025-06-01"):
    """
    Computes a project health score between 0 and 100.
    Based on:
    - Schedule adherence (SV)
    - Progress completion ratio (Actual / Planned)
    - Milestone completion ratio
    - Delayed task percentage
    - Critical path task completion percentage
    """
    pid = project_row["Project ID"]
    
    # 1. Schedule Adherence (Weight: 25%)
    sv = project_row["Schedule Variance"]
    if sv >= 0:
        score_sched = 100.0
    else:
        # Subtract 2 points for every 1% behind schedule
        score_sched = max(100.0 + sv * 2.0, 0.0)
        
    # 2. Progress Completion Ratio (Weight: 20%)
    act_prog = project_row["Actual Progress (%)"]
    pl_prog = project_row["Planned Progress (%)"]
    if pl_prog == 0:
        score_prog = 100.0
    else:
        score_prog = min((act_prog / pl_prog) * 100.0, 100.0)
        
    # 3. Milestone Completion Ratio (Weight: 20%)
    if milestones_df is not None:
        p_milestones = milestones_df[milestones_df["Project ID"] == pid]
        if p_milestones.empty:
            score_miles = 100.0
        else:
            # Milestones that should be completed by now
            should_be_done = p_milestones[p_milestones["Planned Date"] <= current_date_str]
            if should_be_done.empty:
                score_miles = 100.0
            else:
                done = should_be_done[should_be_done["Completion Status"] == "Completed"]
                score_miles = (len(done) / len(should_be_done)) * 100.0
    else:
        score_miles = project_row["Percentage of Milestones Completed"]
        
    # 4. Task Delay Score (Weight: 15%)
    delayed_pct = project_row["Percentage of Delayed Tasks"]
    score_delay = max(100.0 - delayed_pct, 0.0)
    
    # 5. Critical Path Completion (Weight: 20%)
    score_crit = project_row["Critical Path Completion (%)"]
    
    # Weighted Average
    health_score = (
        0.25 * score_sched +
        0.20 * score_prog +
        0.20 * score_miles +
        0.15 * score_delay +
        0.20 * score_crit
    )
    
    health_score = round(health_score, 2)
    
    # Health Status
    if health_score >= 80:
        status = "Healthy"
    elif health_score >= 50:
        status = "Warning"
    else:
        status = "Critical"
        
    return health_score, status
