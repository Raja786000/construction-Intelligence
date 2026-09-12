from typing import Any, TypedDict

class QualityState(TypedDict, total=False):
    inspection_id: str
    request: dict[str, Any]
    findings: list[dict]
    errors: list[str]
    warnings: list[str]
    quality_score: float
    status: str
    severity: str
    recommendations: list[str]
    final_result: dict
