import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_synthetic_data(workspace_dir):
    data_dir = os.path.join(workspace_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    np.random.seed(42)
    
    # Load user's dataset
    user_csv = os.path.join(workspace_dir, "construction_project_dataset.csv")
    if not os.path.exists(user_csv):
        raise FileNotFoundError(f"User dataset not found at {user_csv}")
        
    df_user = pd.read_csv(user_csv)
    print("Loaded user dataset of shape:", df_user.shape)
    
    # We have 50,000 rows. We group them into 500 projects, 100 tasks each
    num_projects = 500
    tasks_per_project = 100
    
    project_types = ["Commercial", "Residential", "Infrastructure", "Industrial", "Institutional"]
    project_phases = ["Planning", "Excavation", "Foundation", "Structural", "MEP", "Finishing", "Commissioning", "Handover"]
    
    # Global current date: set to the middle of the user's project log
    current_date = datetime(2023, 1, 22)
    
    projects = []
    tasks = []
    milestones = []
    
    milestone_counter = 1
    
    print("Generating projects, tasks, and milestones from user dataset...")
    for p in range(1, num_projects + 1):
        pid = f"PRJ_{p:03d}"
        
        # Rows for this project: from (p-1)*100 to p*100 - 1
        p_start_row = (p - 1) * tasks_per_project
        p_end_row = p * tasks_per_project
        df_p_user = df_user.iloc[p_start_row:p_end_row]
        
        # Project start date comes from the first timestamp of this project
        p_start_str = df_p_user.iloc[0]["timestamp"]
        p_start = datetime.strptime(p_start_str, "%Y-%m-%d %H:%M:%S")
        p_start = datetime(p_start.year, p_start.month, p_start.day)
        
        # Planned duration in days (say, 30 days)
        planned_duration = 30
        planned_end_date = p_start + timedelta(days=planned_duration)
        
        # Determine critical tasks and priority mix for project delay calculation
        # Sum critical path task deviations to simulate delay accumulation
        critical_deviations = []
        critical_count = 0
        
        # We pre-calculate details to compute project delay
        proj_tasks_meta = []
        for j in range(tasks_per_project):
            row = df_p_user.iloc[j]
            is_critical = "Yes" if (row["optimization_suggestion"] == "Adjust Schedule" or j % 3 == 0) else "No"
            t_deviation = int(row["time_deviation"])
            
            proj_tasks_meta.append({
                "is_critical": is_critical,
                "t_deviation": t_deviation,
                "row": row
            })
            
            if is_critical == "Yes":
                critical_deviations.append(t_deviation)
                critical_count += 1
                
        # Project Delay = Sum of deviations on the Critical Path
        # We multiply by 1.5 to make delays range from short (e.g. 5 days) to long (e.g. 80 days)
        project_delay = int(sum(critical_deviations) * 1.5)
        # Clip project delay between -15 days (ahead) and +85 days (delayed)
        project_delay = max(min(project_delay, 85), -15)
        
        actual_duration = planned_duration + project_delay
        actual_end_date = p_start + timedelta(days=actual_duration)
        
        # Status and Phase
        avg_progress = df_p_user["task_progress"].mean()
        
        if avg_progress >= 100.0:
            status = "Completed"
            phase = "Handover"
        elif avg_progress <= 0.0:
            status = "Not Started"
            phase = "Planning"
        else:
            status = "In Progress"
            phase_idx = min(int((avg_progress / 100.0) * len(project_phases)), len(project_phases) - 1)
            phase = project_phases[phase_idx]
            
        projects.append({
            "Project ID": pid,
            "Project Name": f"Construction Project {p}",
            "Project Type": np.random.choice(project_types),
            "Project Start Date": p_start.strftime("%Y-%m-%d"),
            "Planned End Date": planned_end_date.strftime("%Y-%m-%d"),
            "Actual End Date": actual_end_date.strftime("%Y-%m-%d"),
            "Current Date": current_date.strftime("%Y-%m-%d"),
            "Planned Duration (Days)": planned_duration,
            "Actual Duration (Days)": actual_duration,
            "Current Project Phase": phase,
            "Project Status": status,
            "Delay Factor": 1.0 + (project_delay / planned_duration)
        })
        
        # Tasks for this project
        task_id_list = []
        for j in range(tasks_per_project):
            meta = proj_tasks_meta[j]
            row = meta["row"]
            t_id = f"TSK_{p:03d}_{j:02d}"
            
            # Map optimization suggestions to categories
            opt_sug = row["optimization_suggestion"]
            if opt_sug == "Reallocate Workers":
                cat = "Excavation"
            elif opt_sug == "Increase Machinery":
                cat = "Foundation"
            elif opt_sug == "Optimize Material Usage":
                cat = "MEP"
            else:
                cat = "Finishing"
                
            priority = np.random.choice(["Low", "Medium", "High", "Critical"])
            wbs_level = np.random.choice([1, 2, 3])
            
            is_critical = meta["is_critical"]
            t_deviation = meta["t_deviation"]
            
            # Dates
            t_planned_start = p_start + timedelta(days=int(j * 0.3))
            t_planned_end = t_planned_start + timedelta(days=5)
            
            # Actual dates influenced by time_deviation scaled by overall project delay
            actual_t_deviation = int(t_deviation * (1.0 + abs(project_delay) / 10.0))
            # Clip actual task deviation to avoid weird chronological dates
            actual_t_deviation = max(min(actual_t_deviation, 15), -4)
            
            t_actual_start = t_planned_start + timedelta(days=int(actual_t_deviation // 2))
            t_actual_end = t_planned_end + timedelta(days=actual_t_deviation)
            
            t_act_dur = max((t_actual_end - t_actual_start).days, 1)
            t_pl_dur = 5
            
            # Progress and status dynamically calculated relative to current_date
            if current_date < t_actual_start:
                t_status = "Not Started"
                act_progress = 0.0
                remaining_duration = t_pl_dur
            elif current_date >= t_actual_end:
                t_status = "Completed"
                act_progress = 100.0
                remaining_duration = 0
            else:
                t_status = "In Progress"
                act_progress = ((current_date - t_actual_start).days / t_act_dur) * 100.0
                act_progress = min(max(act_progress, 0.0), 99.0)
                remaining_duration = max((t_actual_end - current_date).days, 1)
                
            # Planned progress dynamically calculated based on current_date
            if current_date < t_planned_start:
                pl_progress = 0.0
            elif current_date >= t_planned_end:
                pl_progress = 100.0
            else:
                pl_progress = ((current_date - t_planned_start).days / t_pl_dur) * 100.0
                pl_progress = min(max(pl_progress, 0.0), 100.0)
            
            # Dependency
            dependency = task_id_list[-1] if len(task_id_list) > 0 else ""
            
            tasks.append({
                "Project ID": pid,
                "Task ID": t_id,
                "Task Name": f"Task {cat} - {j}",
                "WBS Level": wbs_level,
                "Task Category": cat,
                "Planned Start Date": t_planned_start.strftime("%Y-%m-%d"),
                "Planned End Date": t_planned_end.strftime("%Y-%m-%d"),
                "Actual Start Date": t_actual_start.strftime("%Y-%m-%d"),
                "Actual End Date": t_actual_end.strftime("%Y-%m-%d"),
                "Task Status": t_status,
                "Planned Progress (%)": round(pl_progress, 2),
                "Actual Progress (%)": round(act_progress, 2),
                "Task Duration": t_pl_dur,
                "Actual Duration": t_act_dur,
                "Remaining Duration": remaining_duration,
                "Task Dependency": dependency,
                "Critical Path": is_critical,
                "Task Priority": priority
            })
            
            task_id_list.append(t_id)
            
            # Milestones: exactly 10 milestones per project
            if j % 10 == 9:
                m_id = f"MLS_{milestone_counter:04d}"
                milestone_counter += 1
                
                m_status = "Pending"
                if act_progress >= 100.0:
                    m_status = "Completed"
                elif actual_t_deviation > 0:
                    m_status = "Delayed"
                    
                milestones.append({
                    "Project ID": pid,
                    "Milestone ID": m_id,
                    "Milestone Name": f"Milestone Completion of Task {j}",
                    "Planned Date": t_planned_end.strftime("%Y-%m-%d"),
                    "Actual Date": t_actual_end.strftime("%Y-%m-%d"),
                    "Completion Status": m_status,
                    "Associated Task ID": t_id
                })

    df_projects = pd.DataFrame(projects)
    df_projects.to_csv(os.path.join(data_dir, "projects.csv"), index=False)
    print("Generated projects.csv:", df_projects.shape)

    df_tasks = pd.DataFrame(tasks)
    df_tasks.to_csv(os.path.join(data_dir, "tasks.csv"), index=False)
    print("Generated tasks.csv:", df_tasks.shape)
    
    df_milestones = pd.DataFrame(milestones)
    df_milestones.to_csv(os.path.join(data_dir, "milestones.csv"), index=False)
    print("Generated milestones.csv:", df_milestones.shape)

    # 3. Vectorized Daily & Weekly Progress Reports
    daily_reports = []
    weekly_reports = []
    
    print("Computing daily and weekly reports (vectorized)...")
    for proj in projects:
        pid = proj["Project ID"]
        p_start = datetime.strptime(proj["Project Start Date"], "%Y-%m-%d")
        
        proj_tasks = df_tasks[df_tasks["Project ID"] == pid]
        if proj_tasks.empty:
            continue
            
        total_days = (current_date - p_start).days
        if total_days < 0:
            continue
            
        dates = [p_start + timedelta(days=d) for d in range(total_days + 1)]
        dates_np = np.array([d.toordinal() for d in dates])
        
        # Convert task dates to ordinals
        t_act_starts = np.array([datetime.strptime(d, "%Y-%m-%d").toordinal() for d in proj_tasks["Actual Start Date"]])[:, np.newaxis]
        t_act_ends = np.array([datetime.strptime(d, "%Y-%m-%d").toordinal() for d in proj_tasks["Actual End Date"]])[:, np.newaxis]
        t_pl_ends = np.array([datetime.strptime(d, "%Y-%m-%d").toordinal() for d in proj_tasks["Planned End Date"]])[:, np.newaxis]
        t_pl_starts = np.array([datetime.strptime(d, "%Y-%m-%d").toordinal() for d in proj_tasks["Planned Start Date"]])[:, np.newaxis]
        
        t_act_durations = t_act_ends - t_act_starts
        t_act_durations[t_act_durations == 0] = 1
        
        t_pl_durations = t_pl_ends - t_pl_starts
        t_pl_durations[t_pl_durations == 0] = 1
        
        # Broadcasting metrics across dates_np (shape: num_tasks, num_days)
        is_completed = (dates_np >= t_act_ends)
        is_in_progress = (dates_np >= t_act_starts) & (dates_np < t_act_ends)
        is_delayed = (dates_np > t_pl_ends) & (dates_np < t_act_ends)
        
        # Progress matrix
        progress_matrix = np.zeros((len(proj_tasks), len(dates)))
        progress_matrix[is_completed] = 100.0
        
        in_progress_idx = np.where(is_in_progress)
        if len(in_progress_idx[0]) > 0:
            task_idx = in_progress_idx[0]
            day_idx = in_progress_idx[1]
            progress_matrix[task_idx, day_idx] = (dates_np[day_idx] - t_act_starts[task_idx, 0]) / t_act_durations[task_idx, 0] * 100.0
            
        num_completed_days = is_completed.sum(axis=0)
        num_in_progress_days = is_in_progress.sum(axis=0)
        num_delayed_days = is_delayed.sum(axis=0)
        daily_progress_pct = progress_matrix.mean(axis=0)
        
        for d_idx, d_date in enumerate(dates):
            daily_reports.append({
                "Project ID": pid,
                "Report Date": d_date.strftime("%Y-%m-%d"),
                "Number of Tasks Completed": num_completed_days[d_idx],
                "Number of Tasks In Progress": num_in_progress_days[d_idx],
                "Number of Delayed Tasks": num_delayed_days[d_idx],
                "Daily Progress Percentage": round(daily_progress_pct[d_idx], 2)
            })
            
            # Weekly reports
            if d_idx > 0 and d_idx % 7 == 0:
                week_num = d_idx // 7
                
                is_pl_completed = (dates_np[d_idx] >= t_pl_ends[:, 0])
                is_pl_in_progress = (dates_np[d_idx] >= t_pl_starts[:, 0]) & (dates_np[d_idx] < t_pl_ends[:, 0])
                
                pl_progress = np.zeros(len(proj_tasks))
                pl_progress[is_pl_completed] = 100.0
                
                pl_in_prog_idx = np.where(is_pl_in_progress)[0]
                if len(pl_in_prog_idx) > 0:
                    pl_progress[pl_in_prog_idx] = (dates_np[d_idx] - t_pl_starts[pl_in_prog_idx, 0]) / t_pl_durations[pl_in_prog_idx, 0] * 100.0
                    
                planned_weekly_prog = pl_progress.mean()
                actual_weekly_prog = daily_progress_pct[d_idx]
                weekly_schedule_variance = actual_weekly_prog - planned_weekly_prog
                
                weekly_reports.append({
                    "Project ID": pid,
                    "Week Number": week_num,
                    "Planned Weekly Progress": round(planned_weekly_prog, 2),
                    "Actual Weekly Progress": round(actual_weekly_prog, 2),
                    "Weekly Schedule Variance": round(weekly_schedule_variance, 2)
                })

    df_daily = pd.DataFrame(daily_reports)
    df_daily.to_csv(os.path.join(data_dir, "daily_reports.csv"), index=False)
    print("Generated daily_reports.csv:", df_daily.shape)
    
    df_weekly = pd.DataFrame(weekly_reports)
    df_weekly.to_csv(os.path.join(data_dir, "weekly_reports.csv"), index=False)
    print("Generated weekly_reports.csv:", df_weekly.shape)

if __name__ == "__main__":
    import sys
    workspace = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\Hi\OneDrive\Desktop\infosys"
    generate_synthetic_data(workspace)
