"""
CropXpert — Application configuration.
All env vars loaded via pydantic-settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./cropxpert.db"

    # MQTT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_TOPIC: str = "cropxpert/farm/+/sensors"

    # External APIs
    OPENWEATHERMAP_API_KEY: str = ""
    DATA_GOV_IN_API_KEY: str = ""
    MSG91_AUTH_KEY: str = ""
    MSG91_TEMPLATE_ID: str = ""
    GEMINI_API_KEY: str = ""

    # Discord
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_GUILD_ID: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    # ML model paths
    ML_MODEL_PATH: str = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "random_forest.joblib")
    ML_SCALER_PATH: str = os.path.join(os.path.dirname(__file__), "..", "ml", "models", "scaler.joblib")

    # Crop label ordering (matches training label encoder)
    CROP_LABELS: list[str] = [
        "Apple", "Banana", "Black Gram", "Chickpea", "Coconut",
        "Coffee", "Cotton", "Grapes", "Jute", "Kidney Beans",
        "Lentil", "Maize", "Mango", "Moth Beans", "Mung Beans",
        "Muskmelon", "Orange", "Papaya", "Pigeon Peas", "Pomegranate",
        "Rice", "Watermelon"
    ]

    # ICAR optimal ranges per parameter
    ICAR_RANGES: dict = {
        "nitrogen":    {"low": 80,  "high": 120, "unit": "mg/kg"},
        "phosphorus":  {"low": 50,  "high": 80,  "unit": "mg/kg"},
        "potassium":   {"low": 60,  "high": 100, "unit": "mg/kg"},
        "ph":          {"low": 5.5, "high": 7.5, "unit": "pH"},
        "moisture":    {"low": 40,  "high": 70,  "unit": "%"},
        "temperature": {"low": 22,  "high": 32,  "unit": "°C"},
    }

    # Hardcoded MSP fallback (INR/quintal, 2024-25 prices)
    MSP_FALLBACK: dict = {
        "Rice": 2183, "Wheat": 2275, "Maize": 2090, "Cotton": 6620,
        "Soybean": 4600, "Groundnut": 5850, "Jute": 5050, "Chickpea": 5440,
        "Lentil": 6000, "Pigeon Peas": 7000, "Mung Beans": 8558,
        "Black Gram": 6950, "Kidney Beans": 6000, "Moth Beans": 7500,
        "Coconut": 3200, "Coffee": 12000, "Apple": 5500, "Banana": 3500,
        "Mango": 4500, "Grapes": 4000, "Papaya": 2500,
        "Pomegranate": 6000, "Orange": 3800, "Watermelon": 2000,
        "Muskmelon": 2500, "Sugarcane": 3150,
    }

    # Sowing season data
    CROP_SEASONS: dict = {
        "Rice": {"sowing": ["June", "July"], "harvest": ["October", "November"], "season": "kharif"},
        "Wheat": {"sowing": ["November", "December"], "harvest": ["March", "April"], "season": "rabi"},
        "Maize": {"sowing": ["June", "July"], "harvest": ["September", "October"], "season": "kharif"},
        "Cotton": {"sowing": ["April", "May"], "harvest": ["October", "November"], "season": "kharif"},
        "Soybean": {"sowing": ["June", "July"], "harvest": ["September", "October"], "season": "kharif"},
        "Chickpea": {"sowing": ["October", "November"], "harvest": ["February", "March"], "season": "rabi"},
        "Lentil": {"sowing": ["October", "November"], "harvest": ["February", "March"], "season": "rabi"},
        "Jute": {"sowing": ["March", "April"], "harvest": ["July", "August"], "season": "kharif"},
        "Coffee": {"sowing": ["May", "June"], "harvest": ["November", "December"], "season": "kharif"},
        "Apple": {"sowing": ["December", "January"], "harvest": ["August", "September"], "season": "rabi"},
        "Banana": {"sowing": ["February", "March"], "harvest": ["November", "December"], "season": "zaid"},
        "Mango": {"sowing": ["July", "August"], "harvest": ["May", "June"], "season": "kharif"},
        "Grapes": {"sowing": ["January", "February"], "harvest": ["April", "May"], "season": "rabi"},
        "Pomegranate": {"sowing": ["June", "July"], "harvest": ["February", "March"], "season": "kharif"},
        "Watermelon": {"sowing": ["January", "February"], "harvest": ["April", "May"], "season": "zaid"},
        "Muskmelon": {"sowing": ["February", "March"], "harvest": ["May", "June"], "season": "zaid"},
        "Orange": {"sowing": ["July", "August"], "harvest": ["December", "January"], "season": "kharif"},
        "Papaya": {"sowing": ["February", "March"], "harvest": ["November", "December"], "season": "zaid"},
        "Coconut": {"sowing": ["June", "July"], "harvest": ["year-round"], "season": "kharif"},
        "Pigeon Peas": {"sowing": ["June", "July"], "harvest": ["December", "January"], "season": "kharif"},
        "Mung Beans": {"sowing": ["March", "April"], "harvest": ["June", "July"], "season": "zaid"},
        "Black Gram": {"sowing": ["June", "July"], "harvest": ["October", "November"], "season": "kharif"},
        "Kidney Beans": {"sowing": ["June", "July"], "harvest": ["October", "November"], "season": "kharif"},
        "Moth Beans": {"sowing": ["July", "August"], "harvest": ["October", "November"], "season": "kharif"},
    }

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
