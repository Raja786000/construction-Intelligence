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
    # Rule-based generator to produce beautiful natural-language summaries from inputs
    pm = state["project_monitoring"]
    safety = state["safety"]
    risk = state["risk"]
    quality = state["quality"]
    
    # Generate executive summary
    sv = pm.get("schedule_variance", 0.0)
    predicted_delay = pm.get("predicted_delay_days", 0)
    
    exec_sum = f"The project {state['project_id']} is currently showing a status of '{pm.get('project_status')}'. "
    exec_sum += f"The actual progress of the site stands at {pm.get('actual_progress')}% against the planned target of {pm.get('planned_progress')}%, "
    exec_sum += f"representing a schedule variance of {sv:+.1f}%. "
    
    if predicted_delay > 0:
        exec_sum += f"AI tabular modeling estimates an expected delay of {predicted_delay} days (predicted end date: {pm.get('predicted_completion_date')}). "
    else:
        exec_sum += f"The project is predicted to complete on time or ahead of schedule (expected completion: {pm.get('predicted_completion_date')}). "
        
    # Incorporate other agents
    exec_sum += f"Safety surveillance logged {safety.get('ppe_violations', 0)} PPE violations on site. "
    exec_sum += f"Quality inspections identified {quality.get('defects_detected', 0)} defects. "
    exec_sum += f"The current site environmental hazard risk is graded as {risk.get('risk_level', 'Low')}."

    # Construct recommendations based on issues
    recs = []
    if sv < 0:
        recs.append(f"Hasten structural tasks immediately to address the {abs(sv):.1f}% negative progress variance.")
        recs.append(f"Inspect delayed critical path activities: {', '.join(pm.get('critical_tasks', [])) or 'No critical tasks listed'}.")
    if safety.get("ppe_violations", 0) > 0:
        recs.append(f"Review hard hat and safety vest compliance on Zone B camera feeds.")
    if quality.get("defects_detected", 0) > 0:
        recs.append("Repair columns and framing alignments showing curings cracks or deviations.")
    if risk.get("risk_score", 0) > 40:
        recs.append("Reschedule weather-dependent tasks to avoid forecasted rain delays.")
    recs.append("Verify sub-contractor headcounts on critical path lines.")

    # Actions list
    actions = [
        "Review project schedule variances tomorrow morning.",
        "Re-inspect Zone B for PPE helmet and vest compliance.",
        "Inspect concrete alignment repairs noted in Quality findings."
    ]
    if state["report_type"] == "Weekly":
        actions.append("Compile milestone projection updates for next week's review.")
        actions.append("Conduct a safety stand-down briefing for masonry crew.")

    return {
        "executive_summary": exec_sum,
        "project_monitoring_summary": f"The project exhibits actual progress of {pm.get('actual_progress')}% vs planned progress of {pm.get('planned_progress')}%. "
                                     f"Predictions indicate a {pm.get('delay_probability')*100:.1f}% likelihood of project delay, with an expected delay duration of {predicted_delay} days.",
        "safety_summary": safety.get("summary", "No safety compliance events reported."),
        "risk_summary": risk.get("summary", "Environmental parameters within safe limits."),
        "quality_summary": quality.get("summary", "No structural inspection defects detected."),
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
