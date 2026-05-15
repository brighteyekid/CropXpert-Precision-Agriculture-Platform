"""Pydantic schemas — Prediction."""
from pydantic import BaseModel


class PredictRequest(BaseModel):
    reading_id: int | None = None
    nitrogen: float | None = None
    phosphorus: float | None = None
    potassium: float | None = None
    ph: float | None = None
    moisture: float | None = None
    temperature: float | None = None
    rainfall: float | None = None


class FertilizerDose(BaseModel):
    urea: str
    dap: str


class CropPrediction(BaseModel):
    rank: int
    crop: str
    ml_confidence: float
    msp_inr_per_quintal: float | None
    mandi_price: float | None
    mandi_trend: str | None
    final_score: float
    sowing_tip: str
    sowing_months: list[str]
    fertilizer_dose: FertilizerDose
    gemini_rationale: str | None = None


class PredictResponse(BaseModel):
    top3: list[CropPrediction]
    feature_importances: dict[str, float]
    reading_id: int | None = None
    timestamp: str
