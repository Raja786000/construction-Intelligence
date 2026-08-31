from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CriticalFinding(BaseModel):
    severity: str = Field(description="Severity levels: CRITICAL, HIGH, MEDIUM, LOW")
    issue: str = Field(description="Title of the issue or finding")
    context: str = Field(description="Direct numeric or observation details context for the finding")

class ReportOutput(BaseModel):
    executive_summary: str = Field(description="A concise professional summary of the construction site status.")
    project_status: str = Field(description="Project monitoring schedule status (Ahead, On, Behind, Critically Delayed).")
    critical_findings: List[CriticalFinding] = Field(description="List of prioritized safety, progress, quality, or risk issues.")
    project_monitoring_summary: str = Field(description="Summary detailing schedule, delay days, and progress statistics.")
    safety_summary: str = Field(description="Summary of hard hat compliance, vest violations, or image alerts.")
    risk_summary: str = Field(description="Summary of weather conditions, wind, or environmental concerns.")
    quality_summary: str = Field(description="Summary of cracks, surface defect inspections, or Capstone tests.")
    recommendations: List[str] = Field(description="List of actionable recommendations based only on findings.")
    next_actions: List[str] = Field(description="Immediate next steps to complete tomorrow or during the week.")
