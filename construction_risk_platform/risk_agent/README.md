# Risk Agent
Separate orchestration/alert layer. It consumes CV risk results, applies thresholds, suppresses duplicate alerts with cooldown, prints alerts, and can POST JSON to a webhook.

Run from project root:
`python -m risk_agent.run_camera --source 0`
`python -m risk_agent.run_camera --source test.mp4 --save monitored.mp4`
`uvicorn risk_agent.api:app --reload --port 8002`

Optional PowerShell webhook:
`$env:RISK_ALERT_WEBHOOK="https://your-alert-service/webhook"`
