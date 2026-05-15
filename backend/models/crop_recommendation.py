"""Crop recommendation ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from core.database import Base


class CropRecommendation(Base):
    __tablename__ = "crop_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    reading_id = Column(Integer, ForeignKey("sensor_readings.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False, index=True)
    rank1_crop = Column(String(50))
    rank1_ml_score = Column(Float)
    rank1_final_score = Column(Float)
    rank2_crop = Column(String(50))
    rank2_ml_score = Column(Float)
    rank2_final_score = Column(Float)
    rank3_crop = Column(String(50))
    rank3_ml_score = Column(Float)
    rank3_final_score = Column(Float)
    msp_data = Column(Text)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)
