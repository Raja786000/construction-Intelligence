import os
import sys
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from datetime import datetime

# Import modules from src
from src.preprocessing import load_all_data, clean_dataframe, split_projects_train_val_test, filter_by_project_ids
from src.feature_engineering import engineer_project_features
from src.models.critical_path import analyze_critical_path
from src.models.health_score import calculate_project_health_score
from src.models.milestone_model import MilestonePredictor, monitor_milestones
from src.models.progress_model import ProgressPredictor
from src.models.delay_model import DelayClassifier
from src.models.completion_date_model import CompletionDateRegressor
from src.models.forecasting_model import ProgressForecaster
from src.models.explainability import ProjectExplainer

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def run_ml_pipeline(workspace_dir):
    data_dir = os.path.join(workspace_dir, "data")
    models_dir = os.path.join(workspace_dir, "models_saved")
    os.makedirs(models_dir, exist_ok=True)
    
    print("="*60)
    print("AI-Powered Construction Project Monitoring Pipeline Starting")
    print("="*60)
    
    # 1. Load Data
    raw_data = load_all_data(data_dir)
    df_p = clean_dataframe(raw_data["projects"])
    df_t = clean_dataframe(raw_data["tasks"])
    df_m = clean_dataframe(raw_data["milestones"])
    df_d = clean_dataframe(raw_data["daily"])
    df_w = clean_dataframe(raw_data["weekly"])
    
    if df_p is None or df_t is None or df_m is None:
        print("Error: Missing core datasets (projects, tasks, milestones). Run data_generator.py first.")
        return
        
    # 2. Feature Engineering
    print("\nEngineering project features...")
    df_proj_feat = engineer_project_features(df_p, df_t, df_m)
    print("Engineered project features shape:", df_proj_feat.shape)
    
    # 3. Train/Val/Test Split (Project-Level to avoid leakage)
    print("\nSplitting projects train/val/test sets...")
    train_ids, val_ids, test_ids = split_projects_train_val_test(df_proj_feat, train_size=0.7, val_size=0.15, test_size=0.15)
    print(f"Split sizes: Train={len(train_ids)} projects, Val={len(val_ids)} projects, Test={len(test_ids)} projects")
    
    # Filter datasets for train/val/test
    train_proj = filter_by_project_ids(df_proj_feat, train_ids)
    test_proj = filter_by_project_ids(df_proj_feat, test_ids)
    val_proj = filter_by_project_ids(df_proj_feat, val_ids)
    
    train_tasks = filter_by_project_ids(df_t, train_ids)
    test_tasks = filter_by_project_ids(df_t, test_ids)
    
    train_milestones = filter_by_project_ids(df_m, train_ids)
    test_milestones = filter_by_project_ids(df_m, test_ids)
    
    train_weekly = filter_by_project_ids(df_w, train_ids)
    test_weekly = filter_by_project_ids(df_w, test_ids)
    
    train_daily = filter_by_project_ids(df_d, train_ids)
    test_daily = filter_by_project_ids(df_d, test_ids)
    
    # 4. Train Models
    print("\nTraining Milestone predictor...")
    milestone_predictor = MilestonePredictor()
    milestone_predictor.fit(train_milestones, train_tasks, train_proj)
    milestone_predictor.save(os.path.join(models_dir, "milestone_model.pkl"))
    
    print("Training Progress predictor (Next Week & Next Month)...")
    progress_predictor = ProgressPredictor(model_type="xgboost")
    progress_predictor.fit(train_weekly, train_proj)
    progress_predictor.save(models_dir)
    
    print("Training Project Delay classifier...")
    delay_classifier = DelayClassifier(model_type="xgboost")
    delay_classifier.fit(train_proj)
    delay_classifier.save(models_dir)
    
    print("Training Completion Date regressor...")
    completion_regressor = CompletionDateRegressor(model_type="xgboost")
    completion_regressor.fit(train_proj)
    completion_regressor.save(models_dir)
    
    print("Training Progress Forecaster...")
    progress_forecaster = ProgressForecaster()
    progress_forecaster.fit(train_daily, train_proj)
    progress_forecaster.save(models_dir)
    
    # 5. Evaluate Models on Test Set
    print("\n" + "="*50)
    print("Model Evaluation on Test Dataset")
    print("="*50)
    
    # Evaluation 1: Delay Classification
    print("\nEvaluating Project Delay Classifier...")
    test_features_clf, test_y_clf = delay_classifier.prepare_data(test_proj, is_training=True)
    pred_labels, delay_probs, probs_clf = delay_classifier.predict(test_proj)
    
    test_y_clf_labels = delay_classifier.target_encoder.inverse_transform(test_y_clf)
    
    acc = accuracy_score(test_y_clf_labels, pred_labels)
    prec = precision_score(test_y_clf_labels, pred_labels, average="weighted")
    rec = recall_score(test_y_clf_labels, pred_labels, average="weighted")
    f1 = f1_score(test_y_clf_labels, pred_labels, average="weighted")
    
    # Compute multi-class ROC-AUC
    try:
        roc_auc = roc_auc_score(test_y_clf, probs_clf, multi_class="ovr")
        print(f"ROC-AUC: {roc_auc:.4f}")
    except Exception as e:
        roc_auc = "N/A"
        print(f"ROC-AUC calculation skipped: {e}")
        
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    # Evaluation 2: Completion Date / Delay Regressor
    print("\nEvaluating Project Completion Date Regressor...")
    test_features_reg, test_y_reg = completion_regressor.prepare_data(test_proj, is_training=True)
    pred_delays, pred_comp_dates = completion_regressor.predict_completion(test_proj)
    
    mae = mean_absolute_error(test_y_reg, pred_delays)
    mse = mean_squared_error(test_y_reg, pred_delays)
    rmse = np.sqrt(mse)
    r2 = r2_score(test_y_reg, pred_delays)
    
    print(f"MAE:  {mae:.4f} days")
    print(f"MSE:  {mse:.4f}")
    print(f"RMSE: {rmse:.4f} days")
    print(f"R²:   {r2:.4f}")
    
    # Evaluation 3: Progress Predictor (Next Week & Next Month)
    print("\nEvaluating Progress Predictor...")
    test_weekly_feat, test_w_y_week, test_w_y_month = progress_predictor.prepare_data(test_weekly, test_proj, is_training=True)
    pred_week, pred_month = progress_predictor.predict_progress(test_weekly_feat)
    
    mae_w = mean_absolute_error(test_w_y_week, pred_week)
    rmse_w = np.sqrt(mean_squared_error(test_w_y_week, pred_week))
    mae_m = mean_absolute_error(test_w_y_month, pred_month)
    rmse_m = np.sqrt(mean_squared_error(test_w_y_month, pred_month))
    
    print(f"Next Week Progress MAE:  {mae_w:.4f}%  (RMSE: {rmse_w:.4f}%)")
    print(f"Next Month Progress MAE: {mae_m:.4f}%  (RMSE: {rmse_m:.4f}%)")

    # Evaluation 4: Milestone Delay Classifier
    print("\nEvaluating Milestone Delay Classifier...")
    X_m_test, y_m_test = milestone_predictor.prepare_features(test_milestones, test_tasks, test_proj, is_training=True)
    m_merged = milestone_predictor.predict_delay_probability(test_milestones, test_tasks, test_proj)
    pred_m_labels = m_merged["Predicted Status"]
    y_m_labels = np.where(y_m_test == 1, "Delayed", "On Time")
    
    m_acc = accuracy_score(y_m_labels, pred_m_labels)
    m_f1 = f1_score(y_m_labels, pred_m_labels, average="weighted")
    print(f"Milestone Delay Accuracy: {m_acc:.4f}  (F1 Score: {m_f1:.4f})")

    # Evaluation 5: Progress Forecaster (Next Day, Week, Month, Days to Finish)
    print("\nEvaluating Daily Progress Forecaster...")
    test_daily_lags, y_fd, y_fw, y_fm, y_ff = progress_forecaster.prepare_lags(test_daily, test_proj, is_training=True)
    fc_results = progress_forecaster.forecast(test_daily_lags)
    
    fc_day_mae = mean_absolute_error(y_fd, fc_results["Next Day Progress (%)"])
    fc_week_mae = mean_absolute_error(y_fw, fc_results["Next Week Progress (%)"])
    fc_month_mae = mean_absolute_error(y_fm, fc_results["Next Month Progress (%)"])
    fc_days_mae = mean_absolute_error(y_ff, fc_results["Estimated Days to Completion"])
    
    print(f"Next Day Progress MAE:     {fc_day_mae:.4f}%")
    print(f"Next Week Progress MAE:    {fc_week_mae:.4f}%")
    print(f"Next Month Progress MAE:   {fc_month_mae:.4f}%")
    print(f"Days to Completion MAE:    {fc_days_mae:.4f} days")
    
    # 6. Apply Health Score and Predictions on Sample Projects
    print("\n" + "="*50)
    print("Project Monitoring and Health Score Execution Demonstration")
    print("="*50)
    
    # Run predictions on a couple of test projects and print detail
    sample_pids = list(test_ids)[:3]
    
    # Update test projects raw df with predictions for SHAP XAI reports
    test_proj_raw = test_proj.copy()
    test_proj_raw["Predicted Delay (Days)"] = pred_delays
    test_proj_raw["Predicted Completion Date"] = pred_comp_dates
    test_proj_raw["Predicted Delay Class"] = pred_labels
    test_proj_raw["Delay Classification"] = pred_labels # mapping
    
    # Instantiate explainer
    explainer = ProjectExplainer(
        classifier_model=delay_classifier.model,
        regressor_model=completion_regressor.model,
        feature_cols=delay_classifier.feature_cols
    )
    
    # Encode test_proj for explainability
    encoded_test_proj_features, _ = delay_classifier.prepare_data(test_proj, is_training=False)
    encoded_test_proj = test_proj.copy()
    encoded_test_proj[delay_classifier.feature_cols] = encoded_test_proj_features
    
    all_test_reports = []
    
    for idx, pid in enumerate(test_ids):
        p_row = test_proj_raw[test_proj_raw["Project ID"] == pid].iloc[0]
        
        # Calculate Health Score
        health_score, health_status = calculate_project_health_score(p_row, test_tasks, test_milestones)
        
        # Analyze critical path
        cp_analysis = analyze_critical_path(pid, test_tasks)
        
        # Monitor milestones
        m_monitoring = monitor_milestones(pid, test_milestones)
        
        # Explain prediction
        xai_report = explainer.explain_project(pid, encoded_test_proj, test_proj_raw)
        
        # Compile record for the CSV report
        all_test_reports.append({
            "Project ID": pid,
            "Project Name": p_row['Project Name'],
            "Project Type": p_row['Project Type'],
            "Project Health Score": health_score,
            "Project Health Status": health_status,
            "Planned Progress (%)": round(p_row['Planned Progress (%)'], 2),
            "Actual Progress (%)": round(p_row['Actual Progress (%)'], 2),
            "Schedule Variance (%)": round(p_row['Schedule Variance'], 2),
            "Schedule Status": p_row['Schedule Status'],
            "Completed Milestones (%)": round(m_monitoring['completion_percentage'], 2),
            "Completed Tasks (%)": round(p_row['Percentage of Tasks Completed'], 2),
            "Critical Path Completion (%)": round(cp_analysis['critical_path_completion_pct'], 2),
            "Delayed Critical Tasks Count": len(cp_analysis['delayed_critical_tasks']),
            "Predicted Completion Date": p_row['Predicted Completion Date'],
            "Predicted Delay (Days)": int(p_row['Predicted Delay (Days)']),
            "Explainable AI Report": xai_report['explanation_summary']
        })
        
        # Print only the first 3 to the console
        if idx < 3:
            print(f"\nProject ID:         {pid}")
            print(f"Project Name:       {p_row['Project Name']}")
            print(f"Project Type:       {p_row['Project Type']}")
            print(f"Project Health:     {health_score} / 100 ({health_status})")
            print(f"Planned Progress:   {p_row['Planned Progress (%)']:.1f}%")
            print(f"Actual Progress:     {p_row['Actual Progress (%)']:.1f}%")
            print(f"Schedule Variance:   {p_row['Schedule Variance']:.1f}% ({p_row['Schedule Status']})")
            print(f"Completion Stats:   Completed Milestones={m_monitoring['completion_percentage']:.1f}%, Completed Tasks={p_row['Percentage of Tasks Completed']:.1f}%")
            print(f"Critical Path:      Critical Path Completed={cp_analysis['critical_path_completion_pct']:.1f}%, Delayed Critical Tasks={len(cp_analysis['delayed_critical_tasks'])}")
            print(f"Predictions:        Predicted Completion Date={p_row['Predicted Completion Date']}, Expected Delay={p_row['Predicted Delay (Days)']} Days")
            print(f"Explainable AI:     {xai_report['explanation_summary']}")
            print("-"*50)
            
    # Save the full report for all test projects to CSV
    df_report = pd.DataFrame(all_test_reports)
    report_path = os.path.join(data_dir, "test_predictions_report.csv")
    df_report.to_csv(report_path, index=False)
    print(f"\nSaved detailed predictions and XAI explanations for all {len(test_ids)} test projects to '{report_path}'.")
    print("\nPipeline execution completed. Models are saved in:", models_dir)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\Hi\OneDrive\Desktop\infosys"
    run_ml_pipeline(workspace)
