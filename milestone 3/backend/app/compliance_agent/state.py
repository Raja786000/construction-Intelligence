from typing import TypedDict, Any

class ComplianceState(TypedDict, total=False):
    request: dict
    documents: list
    extracted: list
    classified: list
    findings: list
    score: float
    status: str
    highest_severity: str
    recommendations: list
    errors: list
