# Integration into Construction Intelligence Hub

Milestone 4 should consume normalized events from the other agents rather than duplicating their detection logic.

```text
Quality ───────┐
Safety ────────┤
Compliance ────┤
Schedule ──────┤
Cost ──────────┤ → Normalized Agent Events → Reporting Intelligence → Dashboard / Risk / Reports
Weather ───────┤
Resource ──────┘
```

Recommended production migration:

1. Keep the `AgentEvent` schema as the common contract.
2. Move the EventStore implementation from SQLite to MongoDB.
3. Add tenant/project authorization and RBAC.
4. Add audit events and immutable event history.
5. Add object storage for source documents and inspection evidence.
6. Add notification adapters for email, Teams/Slack and in-app alerts.
7. Add scheduled executive reports.
8. Connect the master LangGraph orchestrator to the reporting service.
