# Construction Intelligence — Milestone 4 Professional v4

A professional reporting and decision platform for a construction intelligence ecosystem.

## Core workflow
**Projects → Data Intake → Executive Dashboard → Risk Register → Agent Health → Reports**

### Projects
- Persistent project list in the sidebar
- Create and switch between projects
- Project-specific event history and reporting

### Data Intake
- Guided templates for seven agents
- Manual normalized-event entry
- Multiple findings per event
- Batch JSON import
- Automatic project/site association
- Successful submission clears the input form

### Intelligence dashboard
- Overall project score and status
- Agent coverage
- Findings and high-risk indicators
- Priority risks
- Recommended actions
- Recent event stream

### Agent Health
Shows the latest reporting state, score, severity, finding count and event count for:
- Quality
- Safety
- Compliance
- Schedule
- Cost
- Weather
- Resource

### Reporting
Management-ready executive PDF plus JSON and CSV exports. The PDF includes:
- Project metadata
- Executive position
- KPI summary
- Agent coverage and health
- Prioritized risk register
- Recommended actions
- Data coverage / decision notes
- Page numbers and report footer

## API
- `GET /health`
- `GET /api/v1/reporting/projects`
- `POST /api/v1/reporting/projects`
- `GET /api/v1/reporting/projects/{project_id}`
- `DELETE /api/v1/reporting/projects/{project_id}`
- `POST /api/v1/reporting/events`
- `POST /api/v1/reporting/events/batch`
- `POST /api/v1/reporting/dashboard`
- `POST /api/v1/reporting/report`
- `GET /api/v1/reporting/reports`
- `GET /api/v1/reporting/download/{filename}`
- `POST /api/v1/reporting/demo`

## Architecture
The standalone UI is a test/operator interface. In the final Construction Intelligence Hub, Quality, Safety, Compliance, Schedule, Cost, Weather and Resource agents should publish the normalized event contract directly to this reporting service through the master orchestration layer. MongoDB, authentication/RBAC, audit logs, alerts and scheduled reporting can then be added behind the same interfaces.

This platform is decision support and does not replace qualified engineering, safety, legal, insurance or contractual review.


## v4.1.0 reliability fixes

This package includes the frontend parser fix that prevented the React application from compiling (the `update` state handler had an unmatched object brace). The missing `Database` icon import is also fixed.

Before starting the app, if you previously ran an older copy, stop the old Vite/uvicorn processes and run this package from its own folder. The frontend must compile before any buttons can work.

### Clean end-to-end smoke test

1. Start the backend and confirm `http://127.0.0.1:8000/health` returns `status: ok`.
2. Start the frontend and confirm the Vite page loads without a red Babel/parser overlay.
3. Click **New project**.
4. Enter Project ID, Project name and Site ID.
5. Click **Create project**.
6. Confirm the project appears in the sidebar and Data Intake opens.
7. Load a Quality template and submit it. The form clears after a successful save.
8. Open Executive and confirm the score/findings update.
9. Generate the report and verify PDF/JSON/CSV downloads.
