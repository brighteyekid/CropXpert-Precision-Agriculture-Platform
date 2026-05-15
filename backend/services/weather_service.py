"""
CropXpert — OpenWeatherMap rainfall service.
Fetches 7-day average rainfall for a lat/lng coordinate.
Caches in SQLite for 6 hours.
"""
import logging
import httpx
from core.config import get_settings

logger = logging.getLogger("cropxpert.weather")
settings = get_settings()

# In-memory 6-hour cache: key=(lat_rounded, lng_rounded) → (rainfall_mm, timestamp)
_cache: dict[tuple, tuple[float, float]] = {}


async def get_rainfall(lat: float, lng: float) -> float | None:
    """
    Fetch 7-day average rainfall from OpenWeatherMap One Call API.
    Returns mm/day average, or None if API key missing / request fails.
    """
    import time

    if not settings.OPENWEATHERMAP_API_KEY:
        logger.info("No OpenWeatherMap API key — rainfall will be None")
        return None

    # Round coordinates for cache key
    cache_key = (round(lat, 2), round(lng, 2))
    cached = _cache.get(cache_key)
    if cached:
        rainfall, ts = cached
        if time.time() - ts < 6 * 3600:  # 6-hour TTL
            return rainfall

    try:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            "lat": lat,
            "lon": lng,
            "appid": settings.OPENWEATHERMAP_API_KEY,
            "exclude": "minutely,hourly,alerts",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", [])
        rain_values = []
        for day in daily[:7]:
            rain_mm = day.get("rain", 0)
            if isinstance(rain_mm, dict):
                rain_mm = rain_mm.get("1h", 0)
            rain_values.append(float(rain_mm))

        avg_rainfall = sum(rain_values) / len(rain_values) if rain_values else 0
        avg_rainfall = round(avg_rainfall, 2)

        # Cache
        _cache[cache_key] = (avg_rainfall, time.time())
        logger.info("Rainfall for (%.2f, %.2f): %.2f mm", lat, lng, avg_rainfall)
        return avg_rainfall

    except Exception as e:
        logger.warning("OpenWeatherMap fetch failed: %s", e)
        return None
