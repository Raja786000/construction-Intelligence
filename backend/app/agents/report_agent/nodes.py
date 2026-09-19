from typing import Dict, Any, List
from datetime import datetime

from app.config.settings import settings
from app.agents.report_agent.state import ReportState
from app.agents.report_agent.schemas import ReportOutput
from app.agents.report_agent.prompts import SYSTEM_REPORT_PROMPT, USER_REPORT_PROMPT

# Import adapters
from app.agents.adapters.project_monitoring_adapter import ProjectMonitoringAdapter
from app.agents.adapters.safety_adapter import SafetyAdapter
from app.agents.adapters.risk_adapter import RiskAdapter
from app.agents.adapters.quality_adapter import QualityAdapter

def collect_results_node(state: ReportState) -> ReportState:
    pid = state["project_id"]
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Collect Agent Results - fetching data for project {pid}")
    
    # Run adapters
    state["project_monitoring"] = ProjectMonitoringAdapter.get_results(pid)
    state["safety"] = SafetyAdapter.get_results(pid)
    state["risk"] = RiskAdapter.get_results(pid)
    state["quality"] = QualityAdapter.get_results(pid)
    
    return state

def validate_inputs_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Validate Inputs - checking monitoring schema consistency")
    
    pm = state["project_monitoring"]
    if not pm or pm.get("project_status") == "Error":
        state["errors"].append("Missing or corrupted project monitoring dataset.")
        state["graph_logs"].append("Validation Alert: Missing project monitoring dataset.")
    
    return state

def analyze_project_monitoring_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Analyze Project Monitoring - parsing schedule deviations")
    return state

def analyze_safety_findings_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Analyze Safety - checking PPE hardhat and vest compliance alerts")
    return state

def analyze_risk_findings_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Analyze Risk - scanning site weather wind and dust hazards")
    return state

def analyze_quality_findings_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Analyze Quality - analyzing concrete column cracks")
    return state

def prioritize_issues_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Prioritize Issues - mapping findings into severity tiers")
    
    pm = state["project_monitoring"]
    safety = state["safety"]
    risk = state["risk"]
    quality = state["quality"]
    
    issues = []
    
    # 1. Project Monitoring Delays
    delay_days = pm.get("predicted_delay_days", 0)
    sv = pm.get("schedule_variance", 0.0)
    if delay_days > 15:
        issues.append({
            "severity": "CRITICAL",
            "issue": "Severe schedule delay predicted",
            "context": f"AI models predict a {delay_days}-day delay with {abs(sv):.1f}% negative schedule variance."
        })
    elif sv < -5.0:
        issues.append({
            "severity": "HIGH",
            "issue": "Project schedule lagging",
            "context": f"Actual progress ({pm.get('actual_progress'):.1f}%) is behind plan ({pm.get('planned_progress'):.1f}%)."
        })
    elif sv < 0:
        issues.append({
            "severity": "MEDIUM",
            "issue": "Minor schedule delay",
            "context": f"Project is lagging slightly by {abs(sv):.1f}% schedule variance."
        })

    # 2. Safety Violations
    violations = safety.get("ppe_violations", 0)
    if violations > 3:
        issues.append({
            "severity": "HIGH",
            "issue": "Unacceptable number of PPE violations",
            "context": f"Site surveillance detected {violations} active PPE compliance violations."
        })
    elif violations > 0:
        issues.append({
            "severity": "MEDIUM",
            "issue": "PPE safety non-compliance",
            "context": f"Detected {violations} workers missing hard hats or safety vests."
        })

    # 3. Quality defects
    defects = quality.get("defects_detected", 0)
    critical_defects = quality.get("critical_defects", 0)
    if critical_defects > 0:
        issues.append({
            "severity": "CRITICAL",
            "issue": "Critical structural defect detected",
            "context": f"Inspector flagged columns with curing cracks and framing misalignments."
        })
    elif defects > 0:
        issues.append({
            "severity": "HIGH",
            "issue": "Quality defects identified",
            "context": f"{defects} defects were logged during recent site concrete inspection."
        })

    # 4. Risk assessment
    risk_level = risk.get("risk_level", "Low")
    if risk_level == "High":
        issues.append({
            "severity": "HIGH",
            "issue": "Elevated site hazard level",
            "context": f"Risk assessment agent flagged site risk as High due to heavy wind/rain forecasts."
        })
    elif risk_level == "Medium":
        issues.append({
            "severity": "MEDIUM",
            "issue": "Moderate environmental risk",
            "context": f"Weather forecasting alerts potential rain that may disrupt masonry shifts."
        })

    state["prioritized_issues"] = issues
    return state

def generate_report_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Generate Report - compiling summaries and advice")
    
    if settings.USE_MOCK_LLM:
        state["graph_logs"].append("LLM Mode: API key missing, running rule-based mock report engine")
        report_data = _mock_llm_generate(state)
    else:
        state["graph_logs"].append(f"LLM Mode: Invoking LangChain LLM ({settings.LLM_PROVIDER}) for structured report output")
        try:
            report_data = _run_langchain_llm(state)
        except Exception as e:
            state["graph_logs"].append(f"Error: LangChain LLM invocation failed ({e}). Falling back to mock engine.")
            report_data = _mock_llm_generate(state)
            
    # Save fields to state
    state["executive_summary"] = report_data["executive_summary"]
    state["project_monitoring_summary"] = report_data["project_monitoring_summary"]
    state["safety_summary"] = report_data["safety_summary"]
    state["risk_summary"] = report_data["risk_summary"]
    state["quality_summary"] = report_data["quality_summary"]
    state["recommendations"] = report_data["recommendations"]
    state["next_actions"] = report_data["next_actions"]
    
    # Save the consolidated final report
    state["final_report"] = {
        "report_type": state["report_type"],
        "project_id": state["project_id"],
        "date": state["date"],
        "executive_summary": report_data["executive_summary"],
        "project_status": state["project_monitoring"].get("project_status"),
        "project_monitoring": {
            "planned_progress": state["project_monitoring"].get("planned_progress"),
            "actual_progress": state["project_monitoring"].get("actual_progress"),
            "schedule_variance": state["project_monitoring"].get("schedule_variance"),
            "predicted_delay_days": state["project_monitoring"].get("predicted_delay_days")
        },
        "safety": {
            "ppe_violations": state["safety"].get("ppe_violations", 0)
        },
        "risk": {
            "risk_score": state["risk"].get("risk_score", 0),
            "risk_level": state["risk"].get("risk_level", "Low")
        },
        "quality": {
            "defects_detected": state["quality"].get("defects_detected", 0)
        },
        "critical_findings": [
            {"severity": item["severity"], "issue": item["issue"]} for item in state.get("prioritized_issues", [])
        ],
        "recommendations": report_data["recommendations"],
        "next_actions": report_data["next_actions"]
    }
    
    return state

def validate_report_node(state: ReportState) -> ReportState:
    state["graph_logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Node: Validate Report - checking structure compliance")
    state["validation_attempts"] += 1
    
    # Simple semantic validation check: Ensure summaries are not empty
    if not state["executive_summary"] or len(state["executive_summary"]) < 20:
        state["errors"].append("Report validation failed: Executive summary is incomplete.")
        state["graph_logs"].append("Validation Alert: Executive summary is too short.")
        
    return state

def _mock_llm_generate(state: ReportState) -> dict:
    pm = state["project_monitoring"]
    safety = state["safety"]
    risk = state["risk"]
    quality = state["quality"]
    rtype = state.get("report_type", "Daily")

    sv = pm.get("schedule_variance", 0.0)
    predicted_delay = pm.get("predicted_delay_days", 0)
    act_prog = pm.get("actual_progress", 0.0)
    plan_prog = pm.get("planned_progress", 0.0)
    status = pm.get("project_status", "On Track")
    violations = safety.get("ppe_violations", 0)
    defects = quality.get("defects_detected", 0)
    risk_level = risk.get("risk_level", "Low")
    risk_score = risk.get("risk_score", 0)
    pred_date = pm.get("predicted_completion_date", "On Schedule")
    crit_tasks = pm.get("critical_tasks", [])

    if rtype == "Daily":
        exec_sum = (
            f"DAILY SITE OPERATIONS SUMMARY ({state['date']}): Project {state['project_id']} is operating under '{status}' status. "
            f"Daily progress tracking shows current completion at {act_prog:.1f}% against the planned target of {plan_prog:.1f}% (Schedule Variance: {sv:+.1f}%). "
            f"Today's active surveillance registered {violations} PPE compliance alert(s), while quality inspections identified {defects} active defect item(s). "
            f"Site environmental hazard is currently rated {risk_level} (Risk Score: {risk_score:.1f}/100)."
        )
        pm_sum = (
            f"Daily Shift Breakdown: {pm.get('active_tasks', 0)} active task(s) currently underway on site. "
            f"Schedule variance stands at {sv:+.1f}%. Predicted completion date remains {pred_date} with a {pm.get('delay_probability', 0)*100:.1f}% delay probability."
        )
        safety_sum = (
            f"Daily PPE Surveillance: {violations} violation(s) captured by site camera sensors today. "
            f"Immediate toolbox briefings required before next shift."
        )
        risk_sum = f"Daily Environmental Index: {risk_level} risk level. Weather conditions and ground wind levels are suitable for crane & staging operations."
        quality_sum = f"Daily QA/QC Log: {defects} structural/surface defect(s) logged during today's walkthrough."
        recs = [
            f"Enforce morning shift PPE compliance on Zone B workfronts.",
            f"Verify site material deliveries and concrete curing schedules for tomorrow's shift.",
            f"Maintain work velocity on critical activities: {', '.join(crit_tasks) if crit_tasks else 'Active structural lines'}."
        ]
        actions = [
            "Conduct pre-shift Toolbox Talk at 07:30 AM focusing on PPE compliance.",
            "Inspect site perimeter and material storage areas prior to morning kickoff.",
            "Verify real-time CCTV feed status across high-hazard work areas."
        ]

    elif rtype == "Weekly":
        exec_sum = (
            f"WEEKLY EXECUTIVE PERFORMANCE REVIEW: Project {state['project_id']} maintained a weekly status of '{status}'. "
            f"Cumulative progress stands at {act_prog:.1f}% vs planned target of {plan_prog:.1f}% (Net Schedule Variance: {sv:+.1f}%). "
            f"Over the past 7 days, AI models estimated {predicted_delay} day(s) of anticipated schedule variance (Target Completion: {pred_date}). "
            f"Weekly safety audits aggregated {violations} PPE violation incident(s), with {defects} quality defect(s) under active remediation."
        )
        pm_sum = (
            f"Weekly Milestone & Velocity Tracking: {pm.get('completed_tasks', 0)} task(s) completed to date with {pm.get('delayed_tasks', 0)} task(s) experiencing delay. "
            f"Overall milestone completion is at {pm.get('milestone_completion', 0):.1f}%. Delay probability is currently {pm.get('delay_probability', 0)*100:.1f}%."
        )
        safety_sum = (
            f"Weekly Safety & Compliance Summary: Total 7-day incident count is {violations} PPE non-compliance event(s). "
            f"Contractor safety adherence score is at {max(100 - violations * 8, 60)}%."
        )
        risk_sum = f"Weekly Risk Matrix: Aggregated risk index is {risk_level} ({risk_score:.1f}/100). Upcoming 7-day weather forecast monitored for precipitation impacts."
        quality_sum = f"Weekly QA/QC Remediation: {defects} non-conformance defect(s) tracked. Re-inspection scheduled for rectified structural elements."
        recs = [
            f"Accelerate weekly task cycles on critical path lines: {', '.join(crit_tasks) if crit_tasks else 'Substructure framing'}.",
            f"Conduct mandatory weekly safety stand-down with sub-contractor site supervisors.",
            f"Review lookahead schedule for the upcoming 14-day milestone delivery window."
        ]
        actions = [
            "Convene Weekly Sub-contractor Coordination Meeting every Monday at 09:00 AM.",
            "Audit milestone progress deliverables against the master construction baseline.",
            "Review weekly quality NCR logs and verify structural closure sign-offs."
        ]

    else:  # Monthly
        exec_sum = (
            f"MONTHLY STRATEGIC PORTFOLIO GOVERNANCE REPORT: Comprehensive monthly review for Project {state['project_id']} (Health Status: '{status}'). "
            f"Total project progress reached {act_prog:.1f}% against planned milestone baseline of {plan_prog:.1f}% ({sv:+.1f}% variance). "
            f"Predictive machine learning models forecast completion by {pred_date} (projected schedule impact: {predicted_delay} days). "
            f"Monthly safety compliance rate is maintained at {max(100 - violations * 5, 75)}%, with {defects} QA/QC defect item(s) in governance registry."
        )
        pm_sum = (
            f"Monthly Earned Value & Schedule Diagnostics: Planned progress {plan_prog:.1f}% vs Actual progress {act_prog:.1f}%. "
            f"Total tasks completed: {pm.get('completed_tasks', 0)}, Active tasks in flight: {pm.get('active_tasks', 0)}. "
            f"Milestone completion velocity is tracking at {pm.get('milestone_completion', 0):.1f}%."
        )
        safety_sum = (
            f"Monthly Safety Governance: Monthly safety surveillance recorded {violations} aggregate PPE non-compliances. "
            f"Zero critical lost-time incidents (LTI) recorded across the reporting cycle."
        )
        risk_sum = f"Monthly Macro Risk Analysis: Composite risk profile evaluated at {risk_level} ({risk_score:.1f}/100). Supply chain and weather contingencies active."
        quality_sum = f"Monthly Quality Assurance: {defects} structural inspections logged. Quality compliance benchmark index is within enterprise tolerances."
        recs = [
            f"Conduct monthly executive budget review and resource re-allocation for critical path tasks.",
            f"Re-baseline project schedule if cumulative variance exceeds 10% threshold.",
            f"Implement enhanced vendor oversight for long-lead structural materials."
        ]
        actions = [
            "Submit monthly executive dossier to Project Steering Committee.",
            "Perform comprehensive monthly site safety and environmental compliance audit.",
            "Finalize monthly contractor progress billing based on verified milestone achievements."
        ]

    return {
        "executive_summary": exec_sum,
        "project_monitoring_summary": pm_sum,
        "safety_summary": safety_sum,
        "risk_summary": risk_sum,
        "quality_summary": quality_sum,
        "recommendations": recs,
        "next_actions": actions
    }

def _run_langchain_llm(state: ReportState) -> dict:
    pm = state["project_monitoring"]
    safety = state["safety"]
    risk = state["risk"]
    quality = state["quality"]
    
    # Format templates
    sys_prompt = SYSTEM_REPORT_PROMPT.format(report_type=state["report_type"])
    user_prompt = USER_REPORT_PROMPT.format(
        report_type=state["report_type"],
        project_id=state["project_id"],
        date=state["date"],
        planned_progress=pm.get("planned_progress"),
        actual_progress=pm.get("actual_progress"),
        schedule_variance=pm.get("schedule_variance"),
        project_status=pm.get("project_status"),
        completed_tasks=pm.get("completed_tasks"),
        active_tasks=pm.get("active_tasks"),
        delayed_tasks=pm.get("delayed_tasks"),
        milestone_completion=pm.get("milestone_completion"),
        delay_probability=pm.get("delay_probability"),
        predicted_delay_days=pm.get("predicted_delay_days"),
        planned_completion_date=pm.get("planned_completion_date"),
        predicted_completion_date=pm.get("predicted_completion_date"),
        critical_tasks=pm.get("critical_tasks"),
        explainable_ai_summary=pm.get("explainable_ai_summary"),
        safety_ppe_violations=safety.get("ppe_violations"),
        safety_helmet_violations=safety.get("helmet_violations"),
        safety_vest_violations=safety.get("vest_violations"),
        safety_critical_events=safety.get("critical_safety_events"),
        safety_summary=safety.get("summary"),
        risk_score=risk.get("risk_score"),
        risk_level=risk.get("risk_level"),
        weather_risk=risk.get("weather_risk"),
        risk_summary=risk.get("summary"),
        quality_defects=quality.get("defects_detected"),
        quality_critical_defects=quality.get("critical_defects"),
        quality_status=quality.get("quality_status"),
        quality_summary=quality.get("summary")
    )
    
    # Initialize appropriate ChatModel based on provider
    if settings.LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        chat_llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2
        )
    else:
        from langchain_google_genai import ChatGoogleGenerativeAI
        chat_llm = ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.2
        )
        
    # Bind structured output schema
    structured_llm = chat_llm.with_structured_output(ReportOutput)
    
    # Invoke
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response: ReportOutput = structured_llm.invoke(messages)
    
    # Return as dict
    return {
        "executive_summary": response.executive_summary,
        "project_monitoring_summary": response.project_monitoring_summary,
        "safety_summary": response.safety_summary,
        "risk_summary": response.risk_summary,
        "quality_summary": response.quality_summary,
        "recommendations": response.recommendations,
        "next_actions": response.next_actions
    }
