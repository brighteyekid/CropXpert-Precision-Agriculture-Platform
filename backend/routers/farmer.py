"""Farmer profile router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_farmer_id
from models.farmer import Farmer
from schemas.farmer import FarmerProfile, FarmerOut

router = APIRouter(tags=["Farmer"])


@router.get("/profile", response_model=FarmerOut)
def get_profile(farmer_id: int = Depends(get_current_farmer_id), db: Session = Depends(get_db)):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(404, "Farmer not found")
    return farmer


@router.put("/profile", response_model=FarmerOut)
def update_profile(
    body: FarmerProfile,
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(404, "Farmer not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(farmer, key, value)

    db.commit()
    db.refresh(farmer)
    return farmer
