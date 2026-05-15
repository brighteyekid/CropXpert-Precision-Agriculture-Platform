"""
CropXpert — FastAPI application entry point.

Start:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import init_db, SessionLocal
from core.mqtt_client import start_mqtt, stop_mqtt, set_on_reading_callback
from services.ml_service import load_model
from services.scheme_service import seed_schemes
from services.discord_bot import start_discord_bot, stop_discord_bot, set_session_factory

from routers.auth import router as auth_router
from routers.farmer import router as farmer_router
from routers.sensors import router as sensors_router
from routers.predict import router as predict_router
from routers.market import router as market_router
from routers.schemes import router as schemes_router
from routers.dashboard import router as dashboard_router
from routers.websocket import router as ws_router
from routers.weather import router as weather_router
from routers.bot import router as bot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-24s | %(levelname)-5s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cropxpert")

settings = get_settings()


def _on_mqtt_reading(farm_id: str | None, payload: dict):
    """Callback for MQTT messages → store reading + auto-predict."""
    from models.sensor_reading import SensorReading
    from services.ml_service import predict
    from routers.websocket import broadcast_to_farmer

    db = SessionLocal()
    try:
        # Find farmer by farm_id (could be farmer.id or a mapped value)
        farmer_id = int(farm_id) if farm_id and farm_id.isdigit() else 1

        reading = SensorReading(
            farmer_id=farmer_id,
            nitrogen=payload.get("N", payload.get("n", 0)),
            phosphorus=payload.get("P", payload.get("p", 0)),
            potassium=payload.get("K", payload.get("k", 0)),
            ph=payload.get("ph", 7.0),
            moisture=payload.get("moisture", 50),
            temperature=payload.get("temperature", payload.get("temp", 25)),
            humidity=payload.get("humidity", 70),
            rainfall=payload.get("rainfall", 100),
            source="mqtt",
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)

        # Push sensor update to WebSocket
        broadcast_to_farmer(farmer_id, {
            "type": "sensor_update",
            "data": {
                "reading_id": reading.id,
                "n": reading.nitrogen, "p": reading.phosphorus, "k": reading.potassium,
                "ph": reading.ph, "moisture": reading.moisture,
                "temperature": reading.temperature, "rainfall": reading.rainfall,
            },
        })

        # Auto-trigger prediction
        try:
            results = predict(
                nitrogen=reading.nitrogen, phosphorus=reading.phosphorus,
                potassium=reading.potassium, ph=reading.ph,
                moisture=reading.moisture, temperature=reading.temperature,
                rainfall=reading.rainfall or 100, humidity=reading.humidity or 70,
            )
            broadcast_to_farmer(farmer_id, {
                "type": "recommendation_ready",
                "data": {
                    "top_crop": results[0]["crop"],
                    "confidence": results[0]["ml_confidence"],
                },
            })
        except Exception as e:
            logger.warning("Auto-prediction failed: %s", e)

    except Exception as e:
        logger.error("MQTT reading processing error: %s", e)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""

    # 1. Initialize database
    logger.info("Initializing database...")
    init_db()

    # 2. Seed government schemes
    db = SessionLocal()
    try:
        seed_schemes(db)
        logger.info("Government schemes seeded")
    finally:
        db.close()

    # 3. Load ML model
    logger.info("Loading ML model...")
    load_model()

    # 4. Start MQTT subscriber
    logger.info("Starting MQTT subscriber...")
    set_on_reading_callback(_on_mqtt_reading)
    start_mqtt()

    # 5. Start Discord bot
    set_session_factory(SessionLocal)
    discord_task = asyncio.create_task(start_discord_bot())

    logger.info("=" * 50)
    logger.info("  CropXpert API running on %s:%d", settings.HOST, settings.PORT)
    logger.info("  Docs: http://%s:%d/docs", settings.HOST, settings.PORT)
    logger.info("=" * 50)

    yield

    # Shutdown
    logger.info("Shutting down...")
    stop_mqtt()
    await stop_discord_bot()
    discord_task.cancel()


app = FastAPI(
    title="CropXpert API",
    description="Precision agriculture backend — ML crop recommendations, AGMARKNET market intel, government scheme advisory",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router,      prefix="/api/auth")
app.include_router(farmer_router,    prefix="/api/farmer")
app.include_router(sensors_router,   prefix="/api/sensors")
app.include_router(predict_router,   prefix="/api/predict")
app.include_router(market_router,    prefix="/api/market")
app.include_router(schemes_router,   prefix="/api/schemes")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(weather_router,   prefix="/api/weather")
app.include_router(bot_router,       prefix="/api/bot")
app.include_router(ws_router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok", "service": "CropXpert API", "version": "1.0.0"}
