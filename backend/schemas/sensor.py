"""Pydantic schemas — Sensor data."""
from pydantic import BaseModel, Field
from datetime import datetime


class SensorReadingIn(BaseModel):
    nitrogen: float = Field(..., ge=0, description="mg/kg")
    phosphorus: float = Field(..., ge=0)
    potassium: float = Field(..., ge=0)
    ph: float = Field(..., ge=0, le=14)
    moisture: float = Field(..., ge=0, le=100)
    temperature: float
    humidity: float = Field(default=0, ge=0, le=100)
    latitude: float | None = None
    longitude: float | None = None


class SensorReadingOut(BaseModel):
    id: int
    farmer_id: int
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    moisture: float
    temperature: float
    humidity: float | None
    rainfall: float | None
    latitude: float | None
    longitude: float | None
    source: str
    timestamp: datetime

    model_config = {"from_attributes": True}
