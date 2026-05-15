"""Market intelligence router — live AGMARKNET prices with 4h in-memory cache."""
import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from services.market_service import (
    get_msp, get_mandi_price, get_trend_data, get_all_crops_msp,
    fetch_all_crops_concurrent, fetch_msp_from_agmarknet,
)
from core.config import get_settings

router = APIRouter(tags=["Market"])
settings = get_settings()


@router.get("/msp")
def msp(crop: str = Query(...), db: Session = Depends(get_db)):
    msp_val = get_msp(crop, db)
    mandi = int(msp_val * 1.01) if msp_val else 0
    delta = round((mandi - msp_val) / msp_val * 100, 1) if msp_val else 0
    return {"crop": crop, "msp_inr": msp_val, "mandi_price": mandi, "delta_pct": delta}


@router.get("/mandi-prices")
async def mandi_prices(
    crop: str = Query(...),
    district: str = Query(""),
    db: Session = Depends(get_db),
):
    """Live mandi price for a single crop+district, with MSP fallback."""
    msp_val = get_msp(crop, db)

    # Try live price (cache-first, then API)
    live = await asyncio.wait_for(
        fetch_msp_from_agmarknet(crop, district),
        timeout=8.0,
    ) if settings.DATA_GOV_IN_API_KEY else None

    mandi = int(live) if live and live > 0 else int(msp_val * 1.01)
    delta = round((mandi - msp_val) / msp_val * 100, 1) if msp_val else 0

    return {
        "crop": crop,
        "district": district,
        "msp_inr": msp_val,
        "mandi_price": mandi,
        "delta_pct": delta,
    }


@router.get("/trend")
def trend(crop: str = Query(...), days: int = Query(90)):
    return get_trend_data(crop, days)


@router.get("/all-crops")
async def all_crops(
    district: str = Query("", description="Farmer's district for live mandi prices"),
    db: Session = Depends(get_db),
):
    """
    Return MSP + live mandi prices for all 22 crops.
    Uses asyncio.gather to fetch ALL crops concurrently (~3s, not ~60s).
    Results are cached in-memory for 4 hours.
    """
    # Fetch all concurrently — returns dict of crop → live_price
    try:
        live_prices = await asyncio.wait_for(
            fetch_all_crops_concurrent(district),
            timeout=15.0,   # max 15s for all 22 crops
        )
    except asyncio.TimeoutError:
        live_prices = {}

    results = []
    for crop, msp_val in settings.MSP_FALLBACK.items():
        if crop not in settings.CROP_LABELS:
            continue
        live = live_prices.get(crop)
        mandi = int(live) if live and live > 0 else int(msp_val * 1.01)
        delta = round((mandi - msp_val) / msp_val * 100, 1) if msp_val > 0 else 0
        results.append({
            "crop": crop,
            "msp_inr": msp_val,
            "mandi_price": mandi,
            "delta_pct": delta,
        })

    return results
