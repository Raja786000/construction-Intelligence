# Milestone 4 Professional — Start Here

## What this version does
This is the reporting and decision layer for Construction Intelligence. It keeps separate project workspaces, accepts normalized outputs from Quality, Safety, Compliance, Schedule, Cost, Weather and Resource agents, aggregates them into an executive dashboard and risk register, and produces management-ready PDF/JSON/CSV reports.

## 1. Start backend
Windows:
```bat
cd %USERPROFILE%\Downloads\construction-intelligence-milestone-4-professional-v4\backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## 2. Start frontend in a second terminal
```bat
cd %USERPROFILE%\Downloads\construction-intelligence-milestone-4-professional-v4\frontend
npm install
npm run dev
```
Open `http://localhost:5174`.

## 3. Recommended first test
1. Click **New project**.
2. Enter Project ID `PROJECT-002`, Project name `Airport Expansion Project`, Site ID `SITE-B`. Location can be `Ludhiana, India`.
3. Click **Create project**.
4. You will be taken to **Data Intake** automatically.
5. Click **Quality → Template → Submit result**.
6. Confirm the input is cleared and a success message appears.
7. Repeat with Safety, Compliance, Schedule, Cost, Weather and Resource.
8. Open **Executive** to see the dashboard.
9. Open **Risk Register** for consolidated findings.
10. Open **Agent Health** for seven-agent coverage.
11. Open **Reports → Generate executive report**.

## Where real agent outputs go
Use **Data Intake** for manual testing. For production integration, send the normalized event contract to `POST /api/v1/reporting/events` or multiple events to `POST /api/v1/reporting/events/batch`.

The current project is automatically attached by the UI for batch imports when `project_id` is omitted.

## Batch JSON example
```json
[
  {
    "agent": "quality",
    "event_type": "quality_inspection_completed",
    "status": "REVIEW_REQUIRED",
    "severity": "HIGH",
    "score": 82,
    "findings": [
      {
        "severity": "HIGH",
        "title": "Concrete crack",
        "description": "Linear crack detected in concrete element.",
        "recommended_action": "Measure crack width and verify structural significance."
      }
    ],
    "recommendations": ["Schedule engineering review."]
  },
  {
    "agent": "safety",
    "event_type": "safety_inspection_completed",
    "status": "ACTION_REQUIRED",
    "severity": "CRITICAL",
    "score": 68,
    "findings": [
      {
        "severity": "CRITICAL",
        "title": "PPE compliance risk",
        "description": "Required PPE was not confidently visible.",
        "recommended_action": "Stop work and verify PPE before continuing."
      }
    ]
  }
]
```

## Storage
Standalone development uses SQLite at `backend/data/reporting.db`. The enterprise integration should replace this store with MongoDB while keeping the same service/API contract.
