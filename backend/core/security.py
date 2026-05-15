"""
CropXpert — JWT token creation/validation + OTP hashing.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from core.config import get_settings
from core.database import get_db

settings = get_settings()
bearer_scheme = HTTPBearer()


def hash_otp(otp: str) -> str:
    """Hash OTP using SHA-256 (OTPs are short-lived, no need for bcrypt)."""
    salt = secrets.token_hex(8)
    h = hashlib.sha256(f"{salt}:{otp}".encode()).hexdigest()
    return f"{salt}${h}"


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """Verify OTP against salted SHA-256 hash."""
    try:
        salt, stored_hash = hashed_otp.split("$", 1)
        h = hashlib.sha256(f"{salt}:{plain_otp}".encode()).hexdigest()
        return h == stored_hash
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_farmer_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    """FastAPI dependency — extracts farmer_id from JWT."""
    payload = decode_access_token(credentials.credentials)
    farmer_id = payload.get("farmer_id")
    if farmer_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return int(farmer_id)
