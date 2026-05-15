"""Auth router — OTP login, JWT token."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.database import get_db
from core.security import create_access_token, get_current_farmer_id
from services.otp_service import generate_otp, send_otp_msg91, store_otp, verify_stored_otp, get_or_create_farmer
from schemas.farmer import FarmerOut

router = APIRouter(tags=["Auth"])


class SendOTPRequest(BaseModel):
    mobile: str


class VerifyOTPRequest(BaseModel):
    mobile: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer_id: int


@router.post("/send-otp")
async def send_otp(body: SendOTPRequest, db: Session = Depends(get_db)):
    if len(body.mobile) != 10 or not body.mobile.isdigit():
        raise HTTPException(400, "Mobile must be a 10-digit number")

    otp = generate_otp()
    success = await send_otp_msg91(body.mobile, otp)
    store_otp(db, body.mobile, otp)

    return {"message": "OTP sent", "success": success}


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    if not verify_stored_otp(db, body.mobile, body.otp):
        raise HTTPException(401, "Invalid or expired OTP")

    farmer = get_or_create_farmer(db, body.mobile)
    token = create_access_token({"farmer_id": farmer.id, "mobile": farmer.mobile})

    return TokenResponse(access_token=token, farmer_id=farmer.id)


@router.get("/me", response_model=FarmerOut)
def get_me(farmer_id: int = Depends(get_current_farmer_id), db: Session = Depends(get_db)):
    from models.farmer import Farmer
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(404, "Farmer not found")
    return farmer
