from datetime import datetime

from pydantic import BaseModel, Field


class EstimateParseRequest(BaseModel):
    reference_id: str | None = Field(default=None, max_length=80)
    customer_name: str | None = Field(default=None, max_length=120)
    vehicle: str | None = Field(default=None, max_length=160)
    workflow_notes: str = Field(min_length=10, max_length=8000)
    source_records: dict[str, str] = Field(default_factory=dict)
    attachments: list[str] = Field(default_factory=list, max_length=25)
    requested_by: str | None = Field(default=None, max_length=120)


class EstimateParseAssessment(BaseModel):
    labor_totals: dict[str, str] = Field(default_factory=dict)
    parts_total: str
    paint_material_total: str
    missing_fields: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    review_checklist: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class EstimateParseResponse(BaseModel):
    request_id: str
    assessment: EstimateParseAssessment
    model: str


class StoredEstimateParse(BaseModel):
    request_id: str
    created_at: datetime
    model: str
    request: EstimateParseRequest
    assessment: EstimateParseAssessment


class StoredEstimateParseSummary(BaseModel):
    request_id: str
    created_at: datetime
    model: str
    reference_id: str | None
    vehicle: str | None
    confidence: float


class EstimateParseListResponse(BaseModel):
    records: list[StoredEstimateParseSummary]
