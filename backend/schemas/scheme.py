"""Pydantic schemas — Government schemes."""
from pydantic import BaseModel
from datetime import date


class SchemeOut(BaseModel):
    id: int
    name: str
    description: str | None
    benefit_amount: str | None
    eligibility: str | None
    documents_required: str | None
    apply_url: str | None
    scheme_type: str | None
    last_updated: date | None

    model_config = {"from_attributes": True}


class EMIRequest(BaseModel):
    principal: float
    rate: float
    tenure_months: int


class EMIResponse(BaseModel):
    monthly_emi: float
    total_payment: float
    total_interest: float
    principal: float
    rate: float
    tenure_months: int
