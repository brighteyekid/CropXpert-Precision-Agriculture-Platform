"""Pydantic schemas — Farmer."""
from pydantic import BaseModel
from datetime import datetime


class FarmerProfile(BaseModel):
    name: str | None = None
    state: str | None = None
    district: str | None = None
    acreage: float | None = None
    language_preference: str = "en"


class FarmerOut(BaseModel):
    id: int
    mobile: str
    name: str | None = None
    state: str | None = None
    district: str | None = None
    acreage: float | None = None
    language_preference: str
    created_at: datetime

    model_config = {"from_attributes": True}
