"""
CropXpert — OTP service via MSG91.
"""
import logging
import random
import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from core.config import get_settings
from core.security import hash_otp, verify_otp
from models.loan_program import OTPStore
from models.farmer import Farmer

logger = logging.getLogger("cropxpert.otp")
settings = get_settings()


def generate_otp() -> str:
    """Generate 6-digit OTP."""
    return str(random.randint(100000, 999999))


async def send_otp_msg91(mobile: str, otp: str) -> bool:
    """Send OTP via MSG91 API. Returns True if successful."""
    if not settings.MSG91_AUTH_KEY:
        logger.info("MSG91 not configured — OTP for %s is %s (dev mode)", mobile, otp)
        return True  # Dev mode: treat as successful

    try:
        url = "https://api.msg91.com/api/v5/otp"
        headers = {"authkey": settings.MSG91_AUTH_KEY}
        params = {
            "template_id": settings.MSG91_TEMPLATE_ID,
            "mobile": f"91{mobile}",
            "otp": otp,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers, params=params)
            resp.raise_for_status()
            logger.info("OTP sent to %s via MSG91", mobile)
            return True
    except Exception as e:
        logger.error("MSG91 send failed: %s", e)
        return False


def store_otp(db: Session, mobile: str, otp: str):
    """Hash and store OTP with 10-minute TTL."""
    # Invalidate any existing unused OTPs for this mobile
    db.query(OTPStore).filter(
        OTPStore.mobile == mobile, OTPStore.used == False
    ).update({"used": True})

    entry = OTPStore(
        mobile=mobile,
        otp_hash=hash_otp(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db.add(entry)
    db.commit()


def verify_stored_otp(db: Session, mobile: str, otp: str) -> bool:
    """Verify OTP against stored hash. In dev mode (no MSG91), accept any OTP."""
    # Dev mode bypass — accept any OTP when MSG91 is not configured
    if not settings.MSG91_AUTH_KEY:
        logger.info("Dev mode — accepting any OTP for %s", mobile)
        # Mark existing OTPs as used
        db.query(OTPStore).filter(
            OTPStore.mobile == mobile, OTPStore.used == False
        ).update({"used": True})
        db.commit()
        return True

    now = datetime.now(timezone.utc)
    entries = (
        db.query(OTPStore)
        .filter(
            OTPStore.mobile == mobile,
            OTPStore.used == False,
            OTPStore.expires_at > now,
        )
        .order_by(OTPStore.id.desc())
        .all()
    )

    for entry in entries:
        if verify_otp(otp, entry.otp_hash):
            entry.used = True
            db.commit()
            return True

    return False


def get_or_create_farmer(db: Session, mobile: str) -> Farmer:
    """Get existing farmer or create a new one from mobile number."""
    farmer = db.query(Farmer).filter(Farmer.mobile == mobile).first()
    if not farmer:
        farmer = Farmer(mobile=mobile)
        db.add(farmer)
        db.commit()
        db.refresh(farmer)
    return farmer
