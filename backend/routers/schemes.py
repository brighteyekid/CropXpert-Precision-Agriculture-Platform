"""Government schemes + loans router — with farmer-acreage eligibility filtering."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_farmer_id
from models.farmer import Farmer
from services.scheme_service import get_schemes, get_loans, calculate_emi
from schemas.scheme import EMIRequest, EMIResponse

router = APIRouter(tags=["Schemes"])


@router.get("")
def list_schemes(
    state: str = Query(None),
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    """Return schemes with real eligibility based on farmer's registered acreage."""
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    acreage_ha = farmer.acreage if farmer and farmer.acreage else None
    state_val = farmer.state if farmer and farmer.state else state
    return get_schemes(db, state=state_val, acreage_ha=acreage_ha)


@router.get("/loans")
def list_loans(db: Session = Depends(get_db)):
    loans = get_loans(db)
    return [
        {
            "id": l.id,
            "name": l.name,
            "provider": l.provider,
            "interest_rate": l.interest_rate,
            "max_amount": l.max_amount,
            "tenure_months_max": l.tenure_months_max,
            "eligibility": l.eligibility,
            "apply_url": l.apply_url,
        }
        for l in loans
    ]


@router.post("/emi-calculate", response_model=EMIResponse)
def emi_calculate(body: EMIRequest):
    return calculate_emi(body.principal, body.rate, body.tenure_months)
