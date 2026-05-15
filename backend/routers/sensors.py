"""Sensor data router — POST readings, GET history."""
import csv
import io
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_farmer_id
from core.mqtt_client import publish_reading
from models.sensor_reading import SensorReading
from schemas.sensor import SensorReadingIn, SensorReadingOut
from services.weather_service import get_rainfall

router = APIRouter(tags=["Sensors"])


@router.post("/reading", response_model=SensorReadingOut)
async def post_reading(
    body: SensorReadingIn,
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    # Fetch rainfall if lat/lng provided
    rainfall = None
    if body.latitude and body.longitude:
        rainfall = await get_rainfall(body.latitude, body.longitude)

    reading = SensorReading(
        farmer_id=farmer_id,
        nitrogen=body.nitrogen,
        phosphorus=body.phosphorus,
        potassium=body.potassium,
        ph=body.ph,
        moisture=body.moisture,
        temperature=body.temperature,
        humidity=body.humidity,
        rainfall=rainfall,
        latitude=body.latitude,
        longitude=body.longitude,
        source="manual",
    )
    db.add(reading)
    db.commit()
    db.refresh(reading)

    # Publish to MQTT for live subscribers
    publish_reading(farmer_id, {
        "reading_id": reading.id,
        "n": reading.nitrogen, "p": reading.phosphorus, "k": reading.potassium,
        "ph": reading.ph, "moisture": reading.moisture,
        "temperature": reading.temperature, "rainfall": reading.rainfall,
    })

    return reading


@router.get("/history", response_model=list[SensorReadingOut])
def get_history(
    days: int = 30,
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(SensorReading)
        .filter(SensorReading.farmer_id == farmer_id, SensorReading.timestamp >= cutoff)
        .order_by(SensorReading.timestamp.desc())
        .all()
    )


@router.get("/latest", response_model=SensorReadingOut | None)
def get_latest(
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.farmer_id == farmer_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )
    if not reading:
        raise HTTPException(404, "No readings found")
    return reading


@router.get("/export")
def export_csv(
    farmer_id: int = Depends(get_current_farmer_id),
    db: Session = Depends(get_db),
):
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.farmer_id == farmer_id)
        .order_by(SensorReading.timestamp.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "N", "P", "K", "pH", "Moisture", "Temperature", "Humidity", "Rainfall", "Source"])
    for r in readings:
        writer.writerow([
            r.timestamp.isoformat() if r.timestamp else "",
            r.nitrogen, r.phosphorus, r.potassium, r.ph,
            r.moisture, r.temperature, r.humidity, r.rainfall, r.source,
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=soil_readings.csv"},
    )
