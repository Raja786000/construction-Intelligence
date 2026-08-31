from langgraph.graph import StateGraph, START, END
from app.agents.report_agent.state import ReportState
from app.agents.report_agent.nodes import (
    collect_results_node,
    validate_inputs_node,
    analyze_project_monitoring_node,
    analyze_safety_findings_node,
    analyze_risk_findings_node,
    analyze_quality_findings_node,
    prioritize_issues_node,
    generate_report_node,
    validate_report_node
)

# 1. Routing function after validation
def route_after_input_validation(state: ReportState) -> str:
    if state.get("errors"):
        return "end_node"
    return "analyze_project_monitoring"

# 2. Routing function after report validation
def route_after_report_validation(state: ReportState) -> str:
    if state.get("errors") and state.get("validation_attempts", 0) < 2:
        # Clear errors for retry
        state["errors"] = []
        return "generate_report"
    return END

# 3. Construct Graph
workflow = StateGraph(ReportState)

# Add Nodes
workflow.add_node("collect_results", collect_results_node)
workflow.add_node("validate_inputs", validate_inputs_node)
workflow.add_node("analyze_project_monitoring", analyze_project_monitoring_node)
workflow.add_node("analyze_safety", analyze_safety_findings_node)
workflow.add_node("analyze_risk", analyze_risk_findings_node)
workflow.add_node("analyze_quality", analyze_quality_findings_node)
workflow.add_node("prioritize_issues", prioritize_issues_node)
workflow.add_node("generate_report", generate_report_node)
workflow.add_node("validate_report", validate_report_node)

# Dummy node for validation failed state
def validation_failed_node(state: ReportState) -> ReportState:
    state["graph_logs"].append("Graph Exit: Input validation failed. Aborting report compilation.")
    return state
workflow.add_node("validation_failed", validation_failed_node)

# Set edges
workflow.add_edge(START, "collect_results")
workflow.add_edge("collect_results", "validate_inputs")

# Conditional Router on Validation
workflow.add_conditional_edges(
    "validate_inputs",
    route_after_input_validation,
    {
        "end_node": "validation_failed",
        "analyze_project_monitoring": "analyze_project_monitoring"
    }
)

# Sequential edges
workflow.add_edge("analyze_project_monitoring", "analyze_safety")
workflow.add_edge("analyze_safety", "analyze_risk")
workflow.add_edge("analyze_risk", "analyze_quality")
workflow.add_edge("analyze_quality", "prioritize_issues")
workflow.add_edge("prioritize_issues", "generate_report")
workflow.add_edge("generate_report", "validate_report")

# Conditional Router on report validation
workflow.add_conditional_edges(
    "validate_report",
    route_after_report_validation,
    {
        "generate_report": "generate_report",
        END: END
    }
)

workflow.add_edge("validation_failed", END)

# Compile Graph
report_graph = workflow.compile()
print("LangGraph Report Agent compiled successfully!")
