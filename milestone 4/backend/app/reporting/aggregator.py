from collections import Counter
from datetime import datetime

AGENTS = ["quality", "safety", "compliance", "schedule", "cost", "weather", "resource"]
SEV_WEIGHT = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

def norm_agent(a):
    a = (a or "").lower().replace("_", " ")
    for x in AGENTS:
        if x in a:
            return x
    return a.strip() or "other"

def aggregate(project_id, events):
    events = sorted(events, key=lambda e: e.get("timestamp", ""))
    agent_latest = {}
    agent_events = Counter()
    all_findings = []
    for e in events:
        a = norm_agent(e.get("agent")); agent_latest[a] = e; agent_events[a] += 1
        for f in e.get("findings", []) or []:
            sev = str(f.get("severity") or e.get("severity") or "NONE").upper()
            all_findings.append({
                "agent": a, "severity": sev,
                "title": f.get("title") or f.get("finding_type") or "Finding",
                "description": f.get("description", ""),
                "recommended_action": f.get("recommended_action") or f.get("action", ""),
                "source_event": e.get("event_type", ""), "timestamp": e.get("timestamp", "")
            })
    sev = Counter(x["severity"] for x in all_findings)
    high = sum(SEV_WEIGHT.get(x["severity"], 0) >= 3 for x in all_findings)
    critical = sum(x["severity"] == "CRITICAL" for x in all_findings)
    scores = [float(e["score"]) for e in events if e.get("score") is not None]
    overall = round(sum(scores) / len(scores), 1) if scores else max(0, 100 - high * 10 - critical * 20)
    overall = max(0, min(100, overall))
    if critical: status = "CRITICAL"
    elif high: status = "HIGH_RISK"
    elif all_findings: status = "REVIEW_REQUIRED"
    elif events: status = "HEALTHY"
    else: status = "NO_DATA"
    recommendations = []
    for e in events:
        for r in e.get("recommendations", []) or []:
            if r and r not in recommendations: recommendations.append(r)
    for f in all_findings:
        r = f["recommended_action"]
        if r and r not in recommendations: recommendations.append(r)
    agent_matrix = {}
    for a in AGENTS:
        v = agent_latest.get(a)
        agent_matrix[a] = {
            "reporting": bool(v),
            "status": v.get("status", "NOT_REPORTING") if v else "NOT_REPORTING",
            "score": v.get("score") if v else None,
            "findings_count": len(v.get("findings", []) or []) if v else 0,
            "severity": str(v.get("severity", "NONE")).upper() if v else "NONE",
            "last_timestamp": v.get("timestamp") if v else None,
            "event_count": agent_events.get(a, 0)
        }
    timeline = []
    for e in events[-12:][::-1]:
        timeline.append({"agent": norm_agent(e.get("agent")), "event_type": e.get("event_type"), "status": e.get("status"), "severity": e.get("severity", "NONE"), "score": e.get("score"), "timestamp": e.get("timestamp")})
    return {
        "project_id": project_id, "overall_score": overall, "overall_status": status,
        "agent_count": sum(1 for a in AGENTS if agent_matrix[a]["reporting"]), "expected_agent_count": len(AGENTS),
        "total_events": len(events), "total_findings": len(all_findings), "high_risk_findings": high,
        "critical_findings": critical, "severity_counts": dict(sev), "agents": agent_matrix,
        "findings": all_findings, "recommendations": recommendations[:30], "timeline": timeline,
        "data_completeness": round(100 * sum(1 for a in AGENTS if agent_matrix[a]["reporting"]) / len(AGENTS), 1)
    }
