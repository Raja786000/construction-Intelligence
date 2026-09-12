from typing import Any
from pydantic import BaseModel, Field

class InspectionRequest(BaseModel):
    project_id: str
    site_id: str | None = None
    zone: str | None = None
    area: str | None = None
    inspection_mode: str = "comprehensive"
    inspection_categories: list[str] = Field(default_factory=list)
    description: str | None = None
    measurements: dict[str, Any] = Field(default_factory=dict)
    images: list[str] = Field(default_factory=list)
