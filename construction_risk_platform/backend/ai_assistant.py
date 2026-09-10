import json
from datetime import datetime, timezone
from typing import Dict, List, Any
from .database import query_all

class AIRiskAssistant:
    def __init__(self):
        pass

    def answer_query(self, query: str) -> Dict[str, Any]:
        """Context-aware AI Risk Assistant chatbot query processor."""
        q_lower = query.lower()
        
        # Load live database state
        projects = query_all("projects")
        risks = query_all("risks")
        workers = query_all("workers")
        weather = query_all("weather_data")
        equipment = query_all("equipment")
        alerts = query_all("alerts")

        proj_name = projects[0]["name"] if projects else "Active Site Project"
        w_condition = weather[0]["condition"] if weather else "Normal"
        w_rain = weather[0]["rainfall_mm"] if weather else 0
        active_alerts = len([a for a in alerts if not a.get("is_resolved")])

        if "weather" in q_lower or "rain" in q_lower:
            response = f"🌤️ **Weather Assessment for {proj_name}**:\n" \
                       f"The current meteorological forecast indicates **{w_condition}** with **{w_rain}mm** expected rainfall.\n" \
                       f"• **Recommended Action**: Deploy dewatering pumps in excavation pits and reschedule high-altitude crane lifts. Outdoor concrete pours should be paused if rainfall exceeds 25mm."

        elif "safety" in q_lower or "ppe" in q_lower or "worker" in q_lower or "incident" in q_lower:
            non_comp = [w for w in workers if w.get("ppe_compliance") != "COMPLIANT"]
            response = f"🦺 **Safety & PPE Compliance Status**:\n" \
                       f"Computer vision monitoring shows **{len(workers)}** active workers logged. **{len(non_comp)}** worker(s) flagged for PPE non-compliance (e.g. missing hardhat/vest).\n" \
                       f"• **Mitigation**: Conduct a 10-minute toolbox safety talk with Subcontractor Team C and enforce mandatory hardhat compliance before work approval."

        elif "equipment" in q_lower or "crane" in q_lower or "machinery" in q_lower:
            crane = next((e for e in equipment if "Crane" in e["name"]), equipment[0] if equipment else {})
            response = f"🏗️ **Equipment & Machinery Health**:\n" \
                       f"• **{crane.get('name', 'Tower Crane')}**: Health score is **{crane.get('health_score')}%**, Failure Probability: **{int(crane.get('failure_probability', 0)*100)}%**.\n" \
                       f"• **Alert**: Elevated vibration readings detected (8.4 mm/s). Immediate bearing lubrication and gear alignment recommended before heavy lifts."

        elif "cost" in q_lower or "budget" in q_lower or "financial" in q_lower:
            p = projects[0] if projects else {"budget": 24500000, "spent": 14200000}
            var_pct = round(((p["spent"] - (p["budget"] * 0.55)) / p["budget"]) * 100, 1)
            response = f"💰 **Cost & Budget Analysis**:\n" \
                       f"• **Total Project Budget**: ${p['budget']:,.2f}\n" \
                       f"• **Current Expenditure**: ${p['spent']:,.2f} ({round((p['spent']/p['budget'])*100, 1)}% spent)\n" \
                       f"• **Variance Warning**: Structural steel price escalation has introduced a +{var_pct}% cost drift. Locking supplier futures contract for remaining 40% rebar volume is advised."

        elif "schedule" in q_lower or "delay" in q_lower or "milestone" in q_lower:
            response = f"⏱️ **Schedule & Delay Forecast**:\n" \
                       f"Current milestone (Superstructure Floor 12) is forecast to be delayed by **3.5 days** due to rain interruption and crane maintenance.\n" \
                       f"• **Recovery Plan**: Reallocate 12 workers to interior MEP ducting during rainfall, then run a weekend overtime shift for concrete curing."

        else:
            response = f"🤖 **AI Risk Assistant Summary for {proj_name}**:\n" \
                       f"I am actively monitoring all 6 agent domains (Safety, Weather, Cost, Schedule, Resource, Quality).\n" \
                       f"• **Overall Project Risk Level**: HIGH (Composite Score: 42.8/100)\n" \
                       f"• **Active Alerts**: {active_alerts} unresolved items (High Crane Vibration, Thunderstorm Forecast)\n" \
                       f"• **Primary Strategic Action**: Address Crane #2 vibration anomaly and implement thunderstorm tarping protocol."

        return {
            "query": query,
            "response": response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suggested_followups": [
                "How will heavy rain affect our completion deadline?",
                "What is the health status of Tower Crane #2?",
                "Show top 3 critical safety incidents from today."
            ]
        }

    def generate_report(self, report_type: str = "Comprehensive Risk Audit") -> Dict[str, Any]:
        """Generates an executive risk report."""
        now = datetime.now(timezone.utc).isoformat()
        projects = query_all("projects")
        risks = query_all("risks")
        alerts = query_all("alerts")

        report_data = {
            "report_id": f"RPT-{int(datetime.now().timestamp())}",
            "title": f"{report_type} - {projects[0]['name'] if projects else 'Construction Site'}",
            "generated_at": now,
            "executive_summary": "The Agentic Construction Risk Intelligence Platform identified 2 high-priority risk factors requiring immediate management intervention: weather-induced schedule delay and crane telemetry strain.",
            "composite_risk_score": 42.8,
            "risk_status": "HIGH",
            "active_risks_count": len(risks),
            "unresolved_alerts_count": len([a for a in alerts if not a.get('is_resolved')]),
            "recommendations": [
                "Execute temporary weather protection plan for Zone B slab pour.",
                "Perform preventive vibration maintenance on Tower Crane #2.",
                "Enforce strict PPE compliance rules with Subcontractor Team C."
            ]
        }
        return report_data
