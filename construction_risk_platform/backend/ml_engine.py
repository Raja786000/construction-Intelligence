import math
from typing import Dict, List, Any

class ConstructionMLPredictor:
    def __init__(self):
        pass

    def predict_schedule_delay(self, 
                               planned_days: int, 
                               completed_milestones: int, 
                               total_milestones: int, 
                               weather_rainfall_mm: float, 
                               active_workers: int) -> Dict[str, Any]:
        """Predicts estimated delay in days using risk regression heuristics."""
        progress_pct = (completed_milestones / max(1, total_milestones)) * 100.0
        
        # Weather impact factor
        weather_delay = 0.0
        if weather_rainfall_mm > 25.0:
            weather_delay = (weather_rainfall_mm / 10.0) * 1.2
        
        # Worker shortage impact
        workforce_factor = 1.0
        if active_workers < 50:
            workforce_factor = 1.5

        estimated_delay_days = round((weather_delay * workforce_factor) + max(0, (100 - progress_pct) * 0.05), 1)

        risk_category = "CRITICAL" if estimated_delay_days > 10 else "HIGH" if estimated_delay_days > 5 else "MEDIUM" if estimated_delay_days > 2 else "LOW"

        return {
            "predicted_delay_days": estimated_delay_days,
            "delay_risk_level": risk_category,
            "weather_impact_days": round(weather_delay, 1),
            "workforce_capacity_index": round(active_workers / 80.0, 2),
            "confidence_score": 0.91,
            "mitigation_recommendation": "Shift critical concrete work to night shift & add 15 workers to floor formwork." if estimated_delay_days > 3 else "Maintain current milestone pace."
        }

    def predict_cost_overrun(self, 
                             budget: float, 
                             spent: float, 
                             schedule_delay_days: float, 
                             material_shortage_risk: str) -> Dict[str, Any]:
        """Predicts budget variance and total cost overrun percentage."""
        burn_rate = spent / max(1.0, budget)
        
        shortage_multiplier = 1.08 if material_shortage_risk == "HIGH" else 1.03 if material_shortage_risk == "MEDIUM" else 1.0

        projected_total_cost = (spent + (budget - spent) * (1.0 + (schedule_delay_days * 0.015))) * shortage_multiplier
        predicted_overrun = projected_total_cost - budget
        overrun_percentage = round((predicted_overrun / budget) * 100.0, 2)

        return {
            "projected_final_cost": round(projected_total_cost, 2),
            "predicted_overrun_amount": round(max(0.0, predicted_overrun), 2),
            "overrun_percentage": overrun_percentage,
            "risk_rating": "HIGH" if overrun_percentage > 10.0 else "MEDIUM" if overrun_percentage > 4.0 else "LOW",
            "key_drivers": [
                f"Schedule delay of {schedule_delay_days} days adding indirect overhead costs.",
                f"Material supply chain risk level: {material_shortage_risk}."
            ]
        }

    def predict_equipment_failure(self, 
                                  operating_hours: float, 
                                  vibration_mm_s: float, 
                                  days_since_maintenance: int) -> Dict[str, Any]:
        """Predicts machine breakdown probability using sensor telemetry."""
        # Baseline failure odds
        base_risk = (operating_hours / 2000.0) * 20.0
        
        # Vibration anomaly multiplier
        vib_risk = 0.0
        if vibration_mm_s > 7.0:
            vib_risk = (vibration_mm_s - 7.0) * 15.0

        maint_risk = (days_since_maintenance / 30.0) * 10.0

        failure_probability = min(99.0, max(2.0, base_risk + vib_risk + maint_risk))
        health_score = round(max(0.0, 100.0 - failure_probability), 1)

        status = "CRITICAL_MAINTENANCE_REQUIRED" if failure_probability > 50 else "WARNING" if failure_probability > 25 else "HEALTHY"

        return {
            "equipment_health_score": health_score,
            "failure_probability_pct": round(failure_probability, 1),
            "vibration_telemetry_status": "HIGH_ANOMALY" if vibration_mm_s > 7.0 else "NORMAL",
            "status": status,
            "recommended_action": "Halt machinery immediately for bearing lube & alignment check." if failure_probability > 45 else "Schedule routine filter service."
        }
