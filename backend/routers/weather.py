"""Weather router — GET /api/weather/current?city=Pune (no API key needed, uses open-meteo)."""
import logging
import httpx
from fastapi import APIRouter, Query

logger = logging.getLogger("cropxpert.weather_router")
router = APIRouter(tags=["Weather"])

# Simple in-memory 30-min cache: city → data
_weather_cache: dict[str, tuple[dict, float]] = {}


async def _geocode(city: str) -> tuple[float, float] | None:
    """Geocode city name to lat/lon using Nominatim (no API key)."""
    try:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "CropXpert/1.0"}) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": city, "format": "json", "limit": 1},
            )
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logger.warning("Geocode failed for %s: %s", city, e)
    return None


async def _fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from open-meteo.com (free, no API key)."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,precipitation",
                    "daily": "precipitation_sum",
                    "timezone": "auto",
                    "forecast_days": 7,
                },
            )
            data = resp.json()
        current = data.get("current", {})
        daily = data.get("daily", {})
        precip_sum = daily.get("precipitation_sum", [])
        avg_rainfall = round(sum(precip_sum) / len(precip_sum), 1) if precip_sum else 0.0

        return {
            "temperature": round(current.get("temperature_2m", 0), 1),
            "humidity": round(current.get("relative_humidity_2m", 0)),
            "rainfall": avg_rainfall,
            "lat": lat,
            "lon": lon,
        }
    except Exception as e:
        logger.warning("open-meteo fetch failed: %s", e)
        return {"temperature": None, "humidity": None, "rainfall": None}


@router.get("/current")
async def get_weather(city: str = Query(..., description="City or district name")):
    """Return current temperature, humidity, and 7-day avg rainfall for a city."""
    import time

    # Cache check (30 minutes)
    cached = _weather_cache.get(city.lower())
    if cached:
        data, ts = cached
        if time.time() - ts < 1800:
            return data

    coords = await _geocode(city)
    if not coords:
        return {"temperature": None, "humidity": None, "rainfall": None, "error": "City not found"}

    lat, lon = coords
    data = await _fetch_weather(lat, lon)
    _weather_cache[city.lower()] = (data, time.time())
    logger.info("Weather for %s: %s", city, data)
    return data
