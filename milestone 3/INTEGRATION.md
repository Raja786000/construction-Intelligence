# Integrating Milestone 3 into the main Construction Intelligence Hub

## Recommended location

Move/copy:
`backend/app/compliance_agent/`

to:
`main-project/backend/agents/compliance/`

The standalone frontend is only a test UI and should not be merged into the production frontend.

## Stable interface

```python
from agents.compliance.agent import ComplianceInsuranceAgent

agent = ComplianceInsuranceAgent()
result = agent.inspect({
    "project_id": "...",
    "site_id": "...",
    "project_name": "...",
    "jurisdiction": "...",
    "inspection_date": "YYYY-MM-DD",
    "project_type": "commercial",
    "notes": "...",
    "required_documents": ["permit", "license", "insurance"],
    "required_coverages": ["General Liability"],
    "minimum_liability_limit": 5000000,
    "renewal_window_days": 30,
    "documents": [...]
})
```

## Main event

The result uses:
`event_type = compliance_inspection_completed`

Persist it to MongoDB and expose it to the central LangGraph orchestrator.

## Future enterprise integrations

Recommended later additions:
- MongoDB document register/history
- Cloud object storage
- Enterprise OCR
- LLM clause/coverage extraction
- Jurisdiction-specific rule packs
- Email/Teams/Slack alerts
- renewal calendar
- insurer/broker integrations
- audit trail
- role-based access control
- signed-document verification
- policy endorsement and exclusion analysis
