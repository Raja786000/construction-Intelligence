import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any
from .config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Project
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        client TEXT NOT NULL,
        budget REAL NOT NULL,
        spent REAL DEFAULT 0,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        progress REAL DEFAULT 0.0,
        risk_score REAL DEFAULT 0.0,
        status TEXT DEFAULT 'ACTIVE'
    )
    """)

    # 2. Construction Site
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sites (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        zones_count INTEGER DEFAULT 1,
        active_workers INTEGER DEFAULT 0,
        ambient_status TEXT DEFAULT 'NORMAL',
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )
    """)

    # 3. Risk
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        probability REAL NOT NULL,
        impact_score REAL NOT NULL,
        status TEXT DEFAULT 'IDENTIFIED',
        mitigation_plan TEXT,
        owner_agent TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # 4. AI Agent
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT DEFAULT 'ONLINE',
        last_active TEXT NOT NULL,
        summary_insight TEXT
    )
    """)

    # 5. Worker
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        name TEXT NOT NULL,
        trade TEXT NOT NULL,
        assigned_task TEXT,
        certification TEXT,
        ppe_compliance TEXT DEFAULT 'COMPLIANT',
        risk_flag TEXT DEFAULT 'LOW'
    )
    """)

    # 6. Equipment
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipment (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        status TEXT DEFAULT 'OPERATIONAL',
        maintenance_schedule TEXT NOT NULL,
        operating_hours REAL DEFAULT 0.0,
        health_score REAL DEFAULT 100.0,
        failure_probability REAL DEFAULT 0.05
    )
    """)

    # 7. Material
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        name TEXT NOT NULL,
        inventory_level REAL NOT NULL,
        unit TEXT NOT NULL,
        required_qty REAL NOT NULL,
        shortage_risk TEXT DEFAULT 'LOW',
        quality_score REAL DEFAULT 95.0
    )
    """)

    # 8. Task
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'IN_PROGRESS',
        completion_pct REAL DEFAULT 0.0,
        planned_start TEXT NOT NULL,
        planned_end TEXT NOT NULL,
        delay_days INTEGER DEFAULT 0,
        dependencies TEXT
    )
    """)

    # 9. Safety Incident
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safety_incidents (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        incident_type TEXT NOT NULL,
        violation_details TEXT NOT NULL,
        worker_id TEXT,
        severity TEXT NOT NULL,
        corrective_action TEXT,
        timestamp TEXT NOT NULL
    )
    """)

    # 10. Weather Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id TEXT PRIMARY KEY,
        location TEXT NOT NULL,
        temperature_c REAL NOT NULL,
        rainfall_mm REAL NOT NULL,
        wind_speed_kmh REAL NOT NULL,
        condition TEXT NOT NULL,
        weather_alert_level TEXT DEFAULT 'CLEAR',
        recorded_at TEXT NOT NULL
    )
    """)

    # 11. Cost Record
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cost_records (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        category TEXT NOT NULL,
        planned_cost REAL NOT NULL,
        actual_cost REAL NOT NULL,
        variance REAL NOT NULL,
        overrun_risk_pct REAL DEFAULT 0.0
    )
    """)

    # 12. Schedule
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        total_milestones INTEGER NOT NULL,
        completed_milestones INTEGER NOT NULL,
        target_completion TEXT NOT NULL,
        forecast_delay_days INTEGER DEFAULT 0
    )
    """)

    # 13. Sensor Data
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        sensor_type TEXT NOT NULL,
        reading_value REAL NOT NULL,
        unit TEXT NOT NULL,
        alert_triggered INTEGER DEFAULT 0,
        timestamp TEXT NOT NULL
    )
    """)

    # 14. Alert
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        source_agent TEXT NOT NULL,
        is_resolved INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # 15. Report
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        report_type TEXT NOT NULL,
        generated_by TEXT NOT NULL,
        content_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def query_all(table_name: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def insert_item(table_name: str, item_dict: Dict[str, Any]):
    conn = get_db()
    cursor = conn.cursor()
    columns = ", ".join(item_dict.keys())
    placeholders = ", ".join(["?"] * len(item_dict))
    values = list(item_dict.values())
    cursor.execute(f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()
