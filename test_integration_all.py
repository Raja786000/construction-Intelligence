import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_all():
    print("=== RUNNING FULL INTEGRATION TEST SUITE ===")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✓ Health check OK:", res.json())

    # 2. Auth Login
    res = client.post("/api/auth/login", json={"username": "admin@construction.ai", "password": "password123"})
    assert res.status_code == 200, f"Auth login failed: {res.text}"
    print("✓ Auth Login OK:", res.json()["user"]["name"])

    # 3. Dashboard Stats (Handwritten Note #2)
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200, f"Dashboard stats failed: {res.text}"
    d = res.json()
    print("✓ Dashboard Stats OK:")
    print(f"   - Total projects: {d['total_projects']}")
    print(f"   - Progress: {d['project_progress']}%")
    print(f"   - Workers: {d['workers_count']}")
    print(f"   - Safety violations: {d['safety_violations_count']}")
    print(f"   - Risk Score: {d['ai_risk_score']} ({d['risk_level']})")
    print(f"   - Weather: {d['weather_status']['condition']}, Tmrw: {d['weather_status']['tomorrow_forecast']}")
    print(f"   - Budget: {d['budget']['formatted_display']}")
    print(f"   - Recent alerts: {len(d['recent_alerts'])} items")

    # 4. Project Management CRUD (Handwritten Note #3)
    res = client.get("/api/projects")
    assert res.status_code == 200
    projects = res.json()
    print(f"✓ Project List OK: {len(projects)} projects in MongoDB")

    # Create new project
    res = client.post("/api/projects", json={
        "name": "Integration Test Flyover",
        "client": "National Highway Corp",
        "budget": 45.0,
        "spent": 5.2,
        "location": "Hyderabad Outer Ring",
        "start_date": "2024-03-01",
        "end_date": "2025-12-31",
        "project_type": "Infrastructure",
        "actual_progress": 25.0,
        "planned_progress": 30.0
    })
    assert res.status_code == 200
    new_proj = res.json()["project"]
    proj_id = new_proj["id"]
    print(f"✓ Add Project OK: Created {proj_id}")

    # View project details
    res = client.get(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    print(f"✓ View Project OK: {res.json()['project']['name']}")

    # Edit project
    res = client.put(f"/api/projects/{proj_id}", json={"actual_progress": 28.0})
    assert res.status_code == 200
    assert res.json()["project"]["actual_progress"] == 28.0
    print(f"✓ Edit Project OK: Progress updated to 28.0%")

    # Delete project
    res = client.delete(f"/api/projects/{proj_id}")
    assert res.status_code == 200
    print("✓ Delete Project OK: Cleaned up test project")

    # 5. Worker Management CRUD (Handwritten Note #4)
    res = client.get("/api/workers")
    assert res.status_code == 200
    workers = res.json()
    print(f"✓ Worker List OK: {len(workers)} site workers in MongoDB")

    # Toggle PPE for W101
    res = client.patch("/api/workers/W101/toggle-ppe?ppe_type=helmet")
    assert res.status_code == 200
    print(f"✓ Toggle PPE OK: W101 helmet toggled to {res.json()['worker']['helmet']}")

    # Toggle back to original
    client.patch("/api/workers/W101/toggle-ppe?ppe_type=helmet")

    # 6. Weather Integration (Handwritten Note #7)
    res = client.get("/api/weather")
    assert res.status_code == 200
    w = res.json()
    print(f"✓ Weather Integration OK: {w['location']} - {w['temperature_c']}°C, Rain: {w['rainfall_mm']}mm, Wind: {w['wind_speed_kmh']}km/h, Humidity: {w['humidity_pct']}%")

    # 7. Alerts Center (Handwritten Note #8)
    res = client.get("/api/alerts")
    assert res.status_code == 200
    alerts = res.json()
    print(f"✓ Alerts Center OK: {len(alerts)} active alerts in MongoDB")

    # 8. ML Risk Prediction (Handwritten Note #6)
    res = client.post("/api/risk/predict-delay", json={
        "planned_days": 30,
        "completed_milestones": 7,
        "total_milestones": 12,
        "weather_rainfall_mm": 38.0,
        "active_workers": 64
    })
    assert res.status_code == 200
    r_delay = res.json()
    print(f"✓ Delay ML Predictor OK: Delay +{r_delay['predicted_delay_days']} days (Prob: {r_delay['delay_probability']})")

    res = client.post("/api/risk/predict-cost", json={
        "budget": 20.0,
        "spent": 1.8,
        "schedule_delay_days": 3.5,
        "material_shortage_risk": "HIGH"
    })
    assert res.status_code == 200
    r_cost = res.json()
    print(f"✓ Cost ML Predictor OK: Overrun Risk {r_cost['overrun_probability']*100}%")

    res = client.post("/api/risk/predict-equipment", json={
        "operating_hours": 1420.5,
        "vibration_mm_s": 8.4,
        "days_since_maintenance": 24
    })
    assert res.status_code == 200
    r_eq = res.json()
    print(f"✓ Equipment ML Predictor OK: Failure Risk {r_eq['failure_probability']*100}% ({r_eq['status']})")

    # 9. Quality Inspection (from Friend B)
    res = client.post("/api/quality/inspect", data={"category": "crack", "project_id": "PROJ-METRO"})
    assert res.status_code == 200
    qi = res.json()
    print(f"✓ Quality Inspection OK: Score {qi['quality_score']}/100, Status: {qi['status']}, Findings: {qi['findings_count']}")

    print("\n==============================================")
    print("ALL INTEGRATION TESTS PASSED PERFECTLY (100%)!")
    print("==============================================")

if __name__ == "__main__":
    test_all()
