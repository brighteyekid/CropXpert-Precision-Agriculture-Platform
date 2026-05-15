"""Prediction router — POST /predict."""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_farmer_id
from models.sensor_reading import SensorReading
from models.crop_recommendation import CropRecommendation
from models.farmer import Farmer
from schemas.prediction import PredictRequest, PredictResponse
from services.ml_service import predict, get_feature_importances
from services.gemini_service import enhance_recommendation
from services.geo_service import fetch_geo_intelligence

router = APIRouter(tags=["Predict"])


@router.post("", response_model=PredictResponse)
def run_prediction(
    body: PredictRequest,
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    # Get features either from reading_id or direct input
    if body.reading_id:
        reading = db.query(SensorReading).filter(SensorReading.id == body.reading_id).first()
        if not reading:
            raise HTTPException(404, "Reading not found")
        n, p, k = reading.nitrogen, reading.phosphorus, reading.potassium
        ph, moisture, temp = reading.ph, reading.moisture, reading.temperature
        rainfall = reading.rainfall or 100.0
        humidity = reading.humidity or 70.0
        reading_id = reading.id
    elif all([body.nitrogen, body.phosphorus, body.potassium, body.ph, body.moisture, body.temperature]):
        n, p, k = body.nitrogen, body.phosphorus, body.potassium
        ph, moisture, temp = body.ph, body.moisture, body.temperature
        rainfall = body.rainfall or 100.0
        humidity = 70.0
        reading_id = None
    else:
        raise HTTPException(400, "Provide either reading_id or all sensor values")

    # Fetch farmer context for LLM
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    farmer_info = {
        "state": farmer.state if farmer else "Unknown",
        "district": farmer.district if farmer else "Unknown",
        "acreage": farmer.acreage if farmer else "Unknown",
    }

    # Run inference
    try:
        results = predict(
            nitrogen=n, phosphorus=p, potassium=k,
            ph=ph, moisture=moisture, temperature=temp,
            rainfall=rainfall, humidity=humidity,
        )
        sensor_data = {
            "nitrogen": n, "phosphorus": p, "potassium": k,
            "ph": ph, "moisture": moisture, "temperature": temp,
            "rainfall": rainfall
        }
        
        # Fetch Geo-Spatial Data (mocking lat/lon roughly for the district)
        geo_data = fetch_geo_intelligence(13.08, 80.27, farmer_info["district"])
        
        results = enhance_recommendation(farmer_info, sensor_data, results, geo_data)
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    # Store recommendation
    rec = CropRecommendation(
        reading_id=reading_id or 0,
        farmer_id=farmer_id,
        rank1_crop=results[0]["crop"], rank1_ml_score=results[0]["ml_confidence"], rank1_final_score=results[0]["final_score"],
        rank2_crop=results[1]["crop"] if len(results) > 1 else None,
        rank2_ml_score=results[1]["ml_confidence"] if len(results) > 1 else None,
        rank2_final_score=results[1]["final_score"] if len(results) > 1 else None,
        rank3_crop=results[2]["crop"] if len(results) > 2 else None,
        rank3_ml_score=results[2]["ml_confidence"] if len(results) > 2 else None,
        rank3_final_score=results[2]["final_score"] if len(results) > 2 else None,
        msp_data=json.dumps({r["crop"]: r["msp_inr_per_quintal"] for r in results}),
    )
    db.add(rec)
    db.commit()

    return PredictResponse(
        top3=results,
        feature_importances=get_feature_importances(),
        reading_id=reading_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
