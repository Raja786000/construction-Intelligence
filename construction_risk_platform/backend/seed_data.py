from datetime import datetime, timezone
import json
from .database import init_db, insert_item, query_all

def seed_database():
    init_db()
    
    # Check if already seeded
    if len(query_all("projects")) > 0:
        print("Database already populated with seed data.")
        return

    now = datetime.now(timezone.utc).isoformat()

    # 1. Projects
    insert_item("projects", {
        "id": "PROJ-101",
        "name": "SkyTower Commercial Complex",
        "location": "Metro City Sector 4",
        "client": "Apex Global Infrastructure",
        "budget": 24500000.0,
        "spent": 14200000.0,
        "start_date": "2025-03-01",
        "end_date": "2027-06-30",
        "progress": 58.5,
        "risk_score": 42.8,
        "status": "ACTIVE"
    })

    # 2. Construction Site
    insert_item("sites", {
        "id": "SITE-A1",
        "project_id": "PROJ-101",
        "name": "SkyTower Main Podium & Tower Zone",
        "location": "Sector 4 Block B",
        "zones_count": 5,
        "active_workers": 64,
        "ambient_status": "MODERATE_WIND_RISK"
    })

    # 3. Risks
    risks = [
        {"id": "RSK-001", "project_id": "PROJ-101", "title": "Foundation Concrete Curing Delay Due to Heavy Rainfall", "category": "Schedule", "severity": "HIGH", "probability": 0.75, "impact_score": 78.0, "status": "ACTIVE", "mitigation_plan": "Deploy temporary rain tarps and pump dewatering units.", "owner_agent": "Weather Agent", "created_at": now},
        {"id": "RSK-002", "project_id": "PROJ-101", "title": "Tower Crane #2 Bearing Strain Anomaly", "category": "Equipment", "severity": "CRITICAL", "probability": 0.85, "impact_score": 92.0, "status": "ACTIVE", "mitigation_plan": "Schedule immediate emergency vibration analysis & gear lube.", "owner_agent": "Resource Agent", "created_at": now},
        {"id": "RSK-003", "project_id": "PROJ-101", "title": "PPE Non-Compliance on Floor 12 Shear Wall", "category": "Safety", "severity": "MEDIUM", "probability": 0.60, "impact_score": 55.0, "status": "IDENTIFIED", "mitigation_plan": "Issue safety brief to Subcontractor Team C & enforce hardhat rule.", "owner_agent": "Safety Agent", "created_at": now},
        {"id": "RSK-004", "project_id": "PROJ-101", "title": "Structural Steel Price Escalation Variance", "category": "Cost", "severity": "HIGH", "probability": 0.70, "impact_score": 68.0, "status": "MONITORING", "mitigation_plan": "Lock batch 4 steel supply contract at current futures rate.", "owner_agent": "Cost Agent", "created_at": now}
    ]
    for r in risks: insert_item("risks", r)

    # 4. AI Agents
    agents = [
        {"id": "AGT-SAFE", "name": "Safety Monitoring Agent", "role": "Computer Vision & Incident Auditor", "status": "ONLINE", "last_active": now, "summary_insight": "Monitoring live feeds. PPE compliance score at 87.5% across active zones."},
        {"id": "AGT-WEATH", "name": "Weather Risk Agent", "role": "Meteorological Forecast Predictor", "status": "ONLINE", "last_active": now, "summary_insight": "Heavy rain forecast in 48 hrs. 35mm precipitation expected."},
        {"id": "AGT-COST", "name": "Cost Analysis Agent", "role": "Budget & Variance Tracker", "status": "ONLINE", "last_active": now, "summary_insight": "Budget variance is currently +4.2% over target due to steel costs."},
        {"id": "AGT-SCHED", "name": "Schedule Tracking Agent", "role": "Critical Path & Delay Forecaster", "status": "ONLINE", "last_active": now, "summary_insight": "Current milestone is delayed by 3.5 days. Mitigation action recommended."},
        {"id": "AGT-RSRC", "name": "Resource & Equipment Agent", "role": "Machinery & Labor Allocator", "status": "ONLINE", "last_active": now, "summary_insight": "Crane #2 exhibiting high vibration. Equipment failure probability 42%."},
        {"id": "AGT-QUAL", "name": "Quality Inspection Agent", "role": "BIM & Structural Integrity Monitor", "status": "ONLINE", "last_active": now, "summary_insight": "Concrete slump test passed. Structural strain sensors within normal range."}
    ]
    for a in agents: insert_item("ai_agents", a)

    # 5. Workers
    workers = [
        {"id": "WRK-101", "site_id": "SITE-A1", "name": "Rajesh Kumar", "trade": "Steel Fixer", "assigned_task": "Floor 12 Rebar Grid", "certification": "OSHA-30 Certified", "ppe_compliance": "COMPLIANT", "risk_flag": "LOW"},
        {"id": "WRK-102", "site_id": "SITE-A1", "name": "Michael Chang", "trade": "Crane Operator", "assigned_task": "Tower Crane #2 Operation", "certification": "Master Heavy Equipment", "ppe_compliance": "COMPLIANT", "risk_flag": "LOW"},
        {"id": "WRK-103", "site_id": "SITE-A1", "name": "David Miller", "trade": "Formwork Carpenter", "assigned_task": "Zone B Decking", "certification": "OSHA-10", "ppe_compliance": "VIOLATION_NO_HELMET", "risk_flag": "HIGH"},
        {"id": "WRK-104", "site_id": "SITE-A1", "name": "Amina Said", "trade": "Safety Inspector", "assigned_task": "Zone A Safety Audit", "certification": "Certified Safety Professional", "ppe_compliance": "COMPLIANT", "risk_flag": "LOW"}
    ]
    for w in workers: insert_item("workers", w)

    # 6. Equipment
    equip = [
        {"id": "EQP-001", "site_id": "SITE-A1", "name": "Tower Crane #2 (Liebherr 280)", "category": "Heavy Crane", "status": "IN_USE", "maintenance_schedule": "2026-09-15", "operating_hours": 1420.5, "health_score": 72.0, "failure_probability": 0.38},
        {"id": "EQP-002", "site_id": "SITE-A1", "name": "Caterpillar Excavator 330", "category": "Earthmoving", "status": "OPERATIONAL", "maintenance_schedule": "2026-10-01", "operating_hours": 890.0, "health_score": 94.0, "failure_probability": 0.05},
        {"id": "EQP-003", "site_id": "SITE-A1", "name": "Concrete Pump Truck P88", "category": "Pumping", "status": "STANDBY", "maintenance_schedule": "2026-09-20", "operating_hours": 610.0, "health_score": 88.5, "failure_probability": 0.12}
    ]
    for e in equip: insert_item("equipment", e)

    # 7. Material
    mats = [
        {"id": "MAT-01", "site_id": "SITE-A1", "name": "Structural Rebar Fe550", "inventory_level": 45.0, "unit": "Tons", "required_qty": 60.0, "shortage_risk": "MEDIUM", "quality_score": 98.0},
        {"id": "MAT-02", "site_id": "SITE-A1", "name": "Ready-Mix Concrete M40", "inventory_level": 120.0, "unit": "m³", "required_qty": 100.0, "shortage_risk": "LOW", "quality_score": 94.5},
        {"id": "MAT-03", "site_id": "SITE-A1", "name": "Safety Mesh & Tarpaulins", "inventory_level": 15.0, "unit": "Rolls", "required_qty": 40.0, "shortage_risk": "HIGH", "quality_score": 90.0}
    ]
    for m in mats: insert_item("materials", m)

    # 8. Task
    tasks = [
        {"id": "TSK-01", "project_id": "PROJ-101", "title": "Superstructure Floor 12 Pouring", "status": "IN_PROGRESS", "completion_pct": 65.0, "planned_start": "2026-09-01", "planned_end": "2026-09-12", "delay_days": 2, "dependencies": "TSK-00"},
        {"id": "TSK-02", "project_id": "PROJ-101", "title": "MEP Ducting Installation Zone 3", "status": "IN_PROGRESS", "completion_pct": 40.0, "planned_start": "2026-09-05", "planned_end": "2026-09-20", "delay_days": 0, "dependencies": "TSK-01"},
        {"id": "TSK-03", "project_id": "PROJ-101", "title": "Curtain Wall Glazing Installation", "status": "PLANNED", "completion_pct": 0.0, "planned_start": "2026-09-18", "planned_end": "2026-10-15", "delay_days": 0, "dependencies": "TSK-01"}
    ]
    for t in tasks: insert_item("tasks", t)

    # 9. Safety Incidents
    incidents = [
        {"id": "INC-001", "site_id": "SITE-A1", "incident_type": "PPE Violation", "violation_details": "Worker detected without protective hardhat near lifting zone.", "worker_id": "WRK-103", "severity": "HIGH", "corrective_action": "Worker escorted to site office & provided approved helmet.", "timestamp": now},
        {"id": "INC-002", "site_id": "SITE-A1", "incident_type": "Unsafe Scaffolding Guardrail", "violation_details": "Missing secondary toe-board on east elevation scaffold.", "worker_id": "WRK-101", "severity": "MEDIUM", "corrective_action": "Scaffold supervisor fixed toe-board immediately.", "timestamp": now}
    ]
    for i in incidents: insert_item("safety_incidents", i)

    # 10. Weather Data
    insert_item("weather_data", {
        "id": "WTH-01",
        "location": "Metro City Sector 4",
        "temperature_c": 28.5,
        "rainfall_mm": 38.0,
        "wind_speed_kmh": 32.5,
        "condition": "Heavy Thunderstorm Forecast",
        "weather_alert_level": "ORANGE_ALERT",
        "recorded_at": now
    })

    # 11. Cost Record
    insert_item("cost_records", {
        "id": "CST-01",
        "project_id": "PROJ-101",
        "category": "Structural Materials & Concrete",
        "planned_cost": 5000000.0,
        "actual_cost": 5350000.0,
        "variance": 350000.0,
        "overrun_risk_pct": 7.0
    })

    # 12. Schedule
    insert_item("schedules", {
        "id": "SCH-01",
        "project_id": "PROJ-101",
        "total_milestones": 12,
        "completed_milestones": 7,
        "target_completion": "2027-06-30",
        "forecast_delay_days": 4
    })

    # 13. Sensor Data
    sensors = [
        {"id": "SNS-01", "site_id": "SITE-A1", "sensor_type": "Vibration (Tower Crane #2)", "reading_value": 8.4, "unit": "mm/s", "alert_triggered": 1, "timestamp": now},
        {"id": "SNS-02", "site_id": "SITE-A1", "sensor_type": "Structural Strain (Column C4)", "reading_value": 310.0, "unit": "microstrain", "alert_triggered": 0, "timestamp": now},
        {"id": "SNS-03", "site_id": "SITE-A1", "sensor_type": "Ambient Dust PM10", "reading_value": 45.0, "unit": "µg/m³", "alert_triggered": 0, "timestamp": now}
    ]
    for s in sensors: insert_item("sensor_data", s)

    # 14. Alert
    alerts = [
        {"id": "ALT-001", "severity": "CRITICAL", "title": "High Crane Vibration Detected", "message": "Tower Crane #2 vibration reading exceeded threshold (8.4 mm/s). Risk of mechanical failure.", "source_agent": "Resource Agent", "is_resolved": 0, "created_at": now},
        {"id": "ALT-002", "severity": "HIGH", "title": "Severe Rainfall Forecast Alert", "message": "38mm rain expected within 48h. High risk of site inundation and concrete delay.", "source_agent": "Weather Agent", "is_resolved": 0, "created_at": now}
    ]
    for a in alerts: insert_item("alerts", a)

    # 15. Report
    report_content = json.dumps({
        "summary": "Project SkyTower shows elevated risk due to upcoming heavy rainfall and crane maintenance strain.",
        "risk_level": "HIGH",
        "overall_score": 42.8,
        "recommendations": [
            "Pause external crane lifts during thunderstorm warning.",
            "Deploy dewatering pumps in foundation pit B.",
            "Enforce 100% hardhat compliance on floor 12."
        ]
    })
    insert_item("reports", {
        "id": "RPT-001",
        "title": "Weekly Construction Risk Intelligence Audit",
        "report_type": "Weekly Audit",
        "generated_by": "Autonomous Agent Ensemble",
        "content_json": report_content,
        "created_at": now
    })

    print("Successfully populated database with seed data for all 15 construction risk entities!")

if __name__ == "__main__":
    seed_database()
