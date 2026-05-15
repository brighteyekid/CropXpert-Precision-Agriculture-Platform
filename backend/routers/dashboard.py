"""Dashboard aggregation router."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_farmer_id
from core.config import get_settings
from models.sensor_reading import SensorReading
from models.crop_recommendation import CropRecommendation
from models.government_scheme import GovernmentScheme

router = APIRouter(tags=["Dashboard"])
settings = get_settings()


def _status(value: float, low: float, high: float) -> str:
    if value < low:
        return "amber" if value >= low * 0.75 else "red"
    elif value > high:
        return "red"
    return "green"


@router.get("/summary")
def dashboard_summary(
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    # Latest reading
    latest = (
        db.query(SensorReading)
        .filter(SensorReading.farmer_id == farmer_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    latest_data = None
    soil_health = {}
    if latest:
        latest_data = {
            "n": latest.nitrogen, "p": latest.phosphorus, "k": latest.potassium,
            "ph": latest.ph, "moisture": latest.moisture, "temp": latest.temperature,
            "rainfall": latest.rainfall,
        }
        ranges = settings.ICAR_RANGES
        for key, col in [("nitrogen", "nitrogen"), ("phosphorus", "phosphorus"),
                         ("potassium", "potassium"), ("ph", "ph"), ("moisture", "moisture")]:
            r = ranges[key]
            val = getattr(latest, col, 0) or 0
            soil_health[key] = {
                "value": val,
                "status": _status(val, r["low"], r["high"]),
                "optimal_range": [r["low"], r["high"]],
            }

    # Last recommendation
    last_rec = (
        db.query(CropRecommendation)
        .filter(CropRecommendation.farmer_id == farmer_id)
        .order_by(CropRecommendation.timestamp.desc())
        .first()
    )
    rec_data = None
    if last_rec:
        msp = settings.MSP_FALLBACK.get(last_rec.rank1_crop, 0)
        rec_data = {
            "crop": last_rec.rank1_crop,
            "confidence": last_rec.rank1_ml_score,
            "msp": msp,
            "timestamp": last_rec.timestamp.isoformat() if last_rec.timestamp else None,
        }

    # 12-month trend data
    twelve_months_ago = datetime.utcnow() - timedelta(days=365)
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.farmer_id == farmer_id, SensorReading.timestamp >= twelve_months_ago)
        .order_by(SensorReading.timestamp.asc())
        .all()
    )
    
    # Aggregate by month to fix overcrowded graphs
    monthly_data = {}
    for r in readings:
        if not r.timestamp:
            continue
        label = r.timestamp.strftime("%b %Y")
        if label not in monthly_data:
            monthly_data[label] = {"n": [], "p": [], "k": []}
        monthly_data[label]["n"].append(r.nitrogen or 0)
        monthly_data[label]["p"].append(r.phosphorus or 0)
        monthly_data[label]["k"].append(r.potassium or 0)

    trend_labels = list(monthly_data.keys())
    trend_n = [sum(data["n"]) / len(data["n"]) for data in monthly_data.values()]
    trend_p = [sum(data["p"]) / len(data["p"]) for data in monthly_data.values()]
    trend_k = [sum(data["k"]) / len(data["k"]) for data in monthly_data.values()]

    # Schemes count
    schemes_count = db.query(GovernmentScheme).count()

    # Profit estimate (simplified)
    profit = None
    if rec_data:
        msp = rec_data["msp"]
        input_cost = 15000  # avg input cost per acre
        yield_per_acre = 20  # quintals
        profit = {
            "crop": rec_data["crop"],
            "net_profit_per_acre": msp * yield_per_acre - input_cost,
            "input_cost": input_cost,
        }

    return {
        "latest_reading": latest_data,
        "soil_health": soil_health,
        "last_recommendation": rec_data,
        "trend_data": {"labels": trend_labels, "n": trend_n, "p": trend_p, "k": trend_k},
        "schemes_available": schemes_count,
        "profit_estimate": profit,
    }
