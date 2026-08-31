import shap
import pandas as pd
import numpy as np

class ProjectExplainer:
    def __init__(self, classifier_model, regressor_model, feature_cols):
        self.classifier_model = classifier_model
        self.regressor_model = regressor_model
        self.feature_cols = feature_cols
        
        # Initialize explainers (tree models can use TreeExplainer for efficiency)
        self.reg_explainer = shap.TreeExplainer(self.regressor_model)
        self.clf_explainer = shap.TreeExplainer(self.classifier_model)
        
    def get_feature_importance(self):
        """
        Returns global feature importance for both classifier and regressor.
        """
        reg_importances = self.regressor_model.feature_importances_
        clf_importances = self.classifier_model.feature_importances_
        
        df_imp = pd.DataFrame({
            "Feature": self.feature_cols,
            "Regressor_Importance": reg_importances,
            "Classifier_Importance": clf_importances
        }).sort_values("Regressor_Importance", ascending=False)
        
        return df_imp
        
    def explain_project(self, project_id, df_projects_encoded, df_projects_raw):
        """
        Generates local SHAP explanations and text explanations for a specific project.
        """
        # Find project row in encoded dataframe
        proj_idx = df_projects_encoded[df_projects_encoded["Project ID"] == project_id].index
        if len(proj_idx) == 0:
            return f"Project {project_id} not found."
            
        proj_idx = proj_idx[0]
        row_encoded = df_projects_encoded.loc[[proj_idx], self.feature_cols]
        row_raw = df_projects_raw[df_projects_raw["Project ID"] == project_id].iloc[0]
        
        # Calculate SHAP values for the regressor (delay in days)
        shap_values_reg = self.reg_explainer(row_encoded)
        shap_reg = shap_values_reg.values[0]
        
        # Calculate SHAP values for the classifier (multiclass delay status)
        # Class probabilities shape: (num_samples, num_features, num_classes) or list
        shap_values_clf = self.clf_explainer(row_encoded)
        if isinstance(shap_values_clf.values, list):
            # For list of classes (binary or multi-output/multiclass SHAP)
            shap_clf = shap_values_clf.values[0] # first class or target class
        else:
            shap_clf = shap_values_clf.values[0]
            
        # Get top contributing features (magnitude of SHAP values)
        # For regressor:
        top_indices = np.argsort(np.abs(shap_reg))[::-1]
        top_features = [self.feature_cols[i] for i in top_indices[:3]]
        
        # Construct plain-English explanation based on the top features and project metrics
        reasons = []
        
        # Retrieve actual prediction values
        pred_delay = row_raw.get("Predicted Delay (Days)")
        if pred_delay is None:
            pred_delay = row_raw["Delay (Days)"] # fallback
            
        pred_class = row_raw.get("Predicted Delay Class")
        if pred_class is None:
            pred_class = row_raw["Delay Classification"]
            
        for f in top_features:
            if f == "Schedule Variance" or f == "Actual Progress (%)" or f == "Planned Progress (%)":
                sv = row_raw["Schedule Variance"]
                if sv < -2.0:
                    reasons.append(f"the actual progress is consistently below the planned progress (Schedule Variance of {sv:.1f}%)")
                elif sv > 2.0:
                    reasons.append(f"the actual progress is ahead of the planned progress (Schedule Variance of +{sv:.1f}%)")
            elif f == "Delayed Critical Tasks Count" or f == "Critical Path Completion (%)" or f == "Critical Task Ratio":
                crit_pct = row_raw["Critical Path Completion (%)"]
                delayed_crit = int(row_raw["Delayed Critical Tasks Count"])
                if delayed_crit > 0:
                    reasons.append(f"multiple critical-path activities are delayed ({delayed_crit} delayed critical tasks)")
                elif crit_pct < 100.0:
                    reasons.append(f"critical path completion is currently lagging at {crit_pct:.1f}%")
            elif f == "Percentage of Milestones Completed":
                m_pct = row_raw["Percentage of Milestones Completed"]
                if m_pct < 70.0:
                    reasons.append(f"milestone completion is behind schedule ({m_pct:.1f}% milestones completed)")
            elif f == "Percentage of Delayed Tasks":
                delayed_tasks = row_raw["Percentage of Delayed Tasks"]
                if delayed_tasks > 15.0:
                    reasons.append(f"a significant portion of tasks are delayed ({delayed_tasks:.1f}% of all tasks)")
            elif f == "Average Task Completion Time":
                avg_time = row_raw["Average Task Completion Time"]
                reasons.append(f"the average task completion time is {avg_time:.1f} days")
                
        # Build explanation text
        if len(reasons) == 0:
            reasons.append("the project is progressing close to planning baselines")
            
        reasons_text = ", ".join(reasons[:-1]) + (f", and {reasons[-1]}" if len(reasons) > 1 else reasons[0])
        
        if pred_delay > 0:
            explanation = f"The project is predicted to finish {int(pred_delay)} days late ({pred_class}) because {reasons_text}."
        elif pred_delay < 0:
            explanation = f"The project is predicted to finish {int(abs(pred_delay))} days ahead of schedule ({pred_class}) because {reasons_text}."
        else:
            explanation = f"The project is predicted to finish on time ({pred_class}) because {reasons_text}."
            
        # Compile local explanation report
        local_report = {
            "project_id": project_id,
            "project_name": row_raw["Project Name"],
            "predicted_delay_days": int(pred_delay),
            "predicted_delay_classification": pred_class,
            "explanation_summary": explanation,
            "top_features": [
                {"feature": self.feature_cols[i], "shap_value": float(shap_reg[i])}
                for i in top_indices[:5]
            ]
        }
        
        return local_report
