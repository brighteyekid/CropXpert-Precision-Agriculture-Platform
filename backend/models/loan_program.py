"""Loan program + OTP store + Market cache ORM models."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from core.database import Base


class LoanProgram(Base):
    __tablename__ = "loan_programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    provider = Column(String(100))
    interest_rate = Column(Float)
    max_amount = Column(Float)
    tenure_months_max = Column(Integer)
    eligibility = Column(String(500))
    apply_url = Column(String(500))


class OTPStore(Base):
    __tablename__ = "otp_store"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(10), nullable=False, index=True)
    otp_hash = Column(String(128), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)


class MarketCache(Base):
    __tablename__ = "market_cache"

    id = Column(Integer, primary_key=True, index=True)
    crop = Column(String(50), nullable=False, index=True)
    msp_inr = Column(Float)
    mandi_price = Column(Float)
    district = Column(String(50))
    fetched_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
