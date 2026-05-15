"""Farmer ORM model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from core.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    district = Column(String(50), nullable=True)
    acreage = Column(Float, nullable=True)
    language_preference = Column(String(10), default="en")
    discord_user_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
