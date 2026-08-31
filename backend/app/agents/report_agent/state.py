from typing import TypedDict, List, Dict, Any

class ReportState(TypedDict):
    # Inputs
    project_id: str
    report_type: str  # "Daily" or "Weekly"
    date: str
    
    # Raw Agent Results
    project_monitoring: Dict[str, Any]
    safety: Dict[str, Any]
    risk: Dict[str, Any]
    quality: Dict[str, Any]
    
    # Intermediate Processing States
    prioritized_issues: List[Dict[str, Any]]
    
    # Generated Outputs
    executive_summary: str
    project_monitoring_summary: str
    safety_summary: str
    risk_summary: str
    quality_summary: str
    recommendations: List[str]
    next_actions: List[str]
    
    # Metadata / Execution logs
    validation_attempts: int
    errors: List[str]
    graph_logs: List[str]
    final_report: Dict[str, Any]
