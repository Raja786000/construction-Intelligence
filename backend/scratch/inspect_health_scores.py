import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.connection import db
from app.ml.model_loader import model_loader

def inspect_health():
    print("Inspecting health scores of first 10 projects:")
    projects = list(db["projects"].find().limit(10))
    for p in projects:
        pid = p["_id"]
        tasks = list(db["tasks"].find({"project_id": pid}))
        milestones = list(db["milestones"].find({"project_id": pid}))
        
        pred = model_loader.get_predictions(p, tasks, milestones)
        print(f"Project ID: {pid} | Name: {p['name']} | Health Score: {pred['project_health_score']} | Status: {pred['project_status']}")

if __name__ == "__main__":
    inspect_health()
