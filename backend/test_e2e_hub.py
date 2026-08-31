import os
import sys

# Ensure backend/app can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.init_db import seed_database
from app.db.connection import db
from app.ml.model_loader import model_loader
from app.api.report import run_report_agent
from app.reports.pdf_generator import generate_report_pdf

def test_e2e():
    print("="*60)
    print("Starting End-to-End Construction Intelligence Hub Test")
    print("="*60)

    # 1. Database Seeding
    print("\n--- Test 1: Database Seeding ---")
    seeding_ok = seed_database()
    assert seeding_ok, "Database seeding failed!"
    print("[SUCCESS] Seeding completed successfully.")

    # 2. Check Demo Projects are Seeded
    print("\n--- Test 2: Checking Seeded Projects ---")
    for pid in ["P001", "P002", "P003"]:
        project = db["projects"].find_one({"_id": pid})
        assert project is not None, f"Demo project {pid} missing from database!"
        print(f"[SUCCESS] Found project {pid}: {project['name']} | Status: {project['schedule_status']}")

    # 3. Model Loader Prediction Check
    print("\n--- Test 3: Project Monitoring ML Predictions ---")
    for pid in ["P001", "P002", "P003"]:
        project = db["projects"].find_one({"_id": pid})
        tasks = list(db["tasks"].find({"project_id": pid}))
        milestones = list(db["milestones"].find({"project_id": pid}))
        
        pred = model_loader.get_predictions(project, tasks, milestones)
        assert pred["project_id"] == pid, "Prediction project ID mismatch!"
        assert "predicted_delay_days" in pred, "Predicted delay days missing!"
        assert "project_health_score" in pred, "Health score missing!"
        
        print(f"[SUCCESS] Project {pid} ML Predictions:")
        print(f"  - Health: {pred['project_health_score']}/100")
        print(f"  - Status: {pred['project_status']}")
        print(f"  - Expected Delay: {pred['predicted_delay_days']} days")
        print(f"  - Explainable AI: {pred['explainable_ai_summary'][:80]}...")

    # 4. LangGraph Report Agent Check
    print("\n--- Test 4: LangGraph Consolidation Agent ---")
    # Generate daily report for P001 (Behind Schedule)
    daily_rep = run_report_agent("P001", "Daily")
    assert daily_rep["project_id"] == "P001", "Daily report project ID mismatch!"
    assert daily_rep["report_type"] == "Daily", "Daily report type mismatch!"
    assert len(daily_rep["recommendations"]) > 0, "No recommendations generated in report!"
    
    print("[SUCCESS] LangGraph Report compiled successfully:")
    print(f"  - Report ID: {daily_rep['id']}")
    print(f"  - Exec Summary: {daily_rep['executive_summary'][:100]}...")
    print(f"  - Recommendations Count: {len(daily_rep['recommendations'])}")

    # 5. PDF Generation Check
    print("\n--- Test 5: PDF Generation & Export ---")
    pdf_path = os.path.join(os.path.dirname(__file__), "test_report.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        
    generate_report_pdf(daily_rep, pdf_path)
    assert os.path.exists(pdf_path), "PDF file was not created!"
    print(f"[SUCCESS] PDF report exported successfully to: {pdf_path}")
    
    # Cleanup pdf
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    print("\n" + "="*60)
    print("All E2E Hub Tests Completed Successfully!")
    print("="*60)

if __name__ == "__main__":
    test_e2e()
