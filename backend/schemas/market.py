"""Pydantic schemas — Market data."""
from pydantic import BaseModel


class MSPOut(BaseModel):
    crop: str
    msp_inr: float
    mandi_price: float | None = None
    delta_pct: float | None = None


class TrendPoint(BaseModel):
    date: str
    price: float


class MarketTrendOut(BaseModel):
    crop: str
    district: str | None
    labels: list[str]
    data: list[float]
