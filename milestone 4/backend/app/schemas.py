from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

class AgentEvent(BaseModel):
    project_id: str = Field(min_length=1)
    site_id: str = ""
    agent: str = Field(min_length=1)
    event_type: str = "agent_result"
    status: str = "REVIEW_REQUIRED"
    severity: str = "NONE"
    score: Optional[float] = None
    findings_count: int = 0
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    @field_validator('score')
    @classmethod
    def score_range(cls, v):
        if v is not None and not 0 <= float(v) <= 100:
            raise ValueError('Score must be between 0 and 100')
        return v

class ProjectCreate(BaseModel):
    project_id: str = Field(min_length=2)
    name: str = Field(min_length=1)
    site_id: str = Field(min_length=1)
    project_type: str = "commercial"
    location: str = ""
    owner: str = ""
    manager: str = ""

class ReportRequest(BaseModel):
    project_id: str = Field(min_length=1)
    report_type: str = "executive"
    include_events: bool = True
    date_from: str = ""
    date_to: str = ""

class DashboardRequest(BaseModel):
    project_id: Optional[str] = None
