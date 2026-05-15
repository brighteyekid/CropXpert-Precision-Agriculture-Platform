"""Gemini LLM integration for enhanced crop recommendations."""
import os
import logging
from google import genai
from google.genai import types
from core.config import get_settings

logger = logging.getLogger("cropxpert.gemini")
settings = get_settings()

def enhance_recommendation(farmer_info: dict, sensor_data: dict, ml_results: list[dict], geo_data: dict = None) -> list[dict]:
    """Uses Gemini to provide an agronomist rationale for the ML predictions."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        logger.warning("GEMINI_API_KEY not set. Skipping Gemini enhancement.")
        return ml_results
        
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an expert agronomist AI for the CropXpert platform in India.
Your task is to analyze the farmer's real-time soil sensor data, location, and a list of preliminary candidate crops, and provide the absolute best final recommendation and rationale.

Farmer Location: {farmer_info.get('district', 'Unknown')}, {farmer_info.get('state', 'Unknown')}
Farm Size: {farmer_info.get('acreage', 'Unknown')} acres

Real-Time Soil Sensor Readings:
Nitrogen (N): {sensor_data.get('nitrogen', 'N/A')} mg/kg
Phosphorus (P): {sensor_data.get('phosphorus', 'N/A')} mg/kg
Potassium (K): {sensor_data.get('potassium', 'N/A')} mg/kg
pH: {sensor_data.get('ph', 'N/A')}
Moisture: {sensor_data.get('moisture', 'N/A')}%
Temperature: {sensor_data.get('temperature', 'N/A')}°C
Rainfall (Live 7-Day Forecast Avg): {sensor_data.get('rainfall', 'N/A')} mm

Geo-Spatial Intelligence (Live Scan):
- Sentinel Hub: NDVI Index {geo_data.get('sentinel_hub', {}).get('ndvi_index', 'N/A')}, Vegetation Health: {geo_data.get('sentinel_hub', {}).get('vegetation_health', 'N/A')}, Moisture Anomaly: {geo_data.get('sentinel_hub', {}).get('surface_moisture_anomaly', 'N/A')}
- Earth Engine: Elevation {geo_data.get('earth_engine', {}).get('elevation_m', 'N/A')}m, Heat Stress Risk: {geo_data.get('earth_engine', {}).get('heat_stress_risk', 'N/A')}
- Bhuvan ISRO: Groundwater Prospect: {geo_data.get('bhuvan_isro', {}).get('groundwater_prospect', 'N/A')}, Soil Erosion Risk: {geo_data.get('bhuvan_isro', {}).get('soil_erosion_risk', 'N/A')}

Preliminary Candidate Crops:
1. {ml_results[0]['crop']}
2. {ml_results[1]['crop'] if len(ml_results) > 1 else 'N/A'}
3. {ml_results[2]['crop'] if len(ml_results) > 2 else 'N/A'}

Analyze the real-time soil data, location, and geo-spatial intelligence to determine the best crop. 
IMPORTANT CONTEXT: The Rainfall value provided is a LIVE 7-DAY FORECAST AVERAGE, meaning a value of 0 mm simply indicates it is not raining this week. Do not assume the region is a permanent desert. Rely on your inherent knowledge of the district's actual annual climate, traditional seasons, and the provided Geo-Spatial data (Bhuvan/Sentinel/Earth Engine).

Evaluate the #1 candidate. If it is highly unrealistic for the farmer's location (for example, suggesting Kidney Beans in the hot climate of Chennai just because the soil numbers aligned), completely ignore the candidates and pivot to the most realistic, profitable crop for that specific district. 
Explain exactly why your chosen crop thrives in their specific region. If the real-time soil values are not perfect for your chosen realistic crop, suggest exactly what fertilizers or amendments the farmer should mix into the soil to achieve the optimal state.

CRITICAL RULE: Do NOT mention "Machine Learning", "ML model", "scores", "candidates", or "algorithms" in your response. The response must flow smoothly as if you are the sole expert independently providing this recommendation based on the real-time sensor data. Speak directly to the farmer as a wildly enthusiastic, deeply passionate, and highly energetic human Agronomist. Bring intense energy to your advice—treat this farm like an absolute masterpiece waiting to happen! Use exciting, highly encouraging language about maximizing yields, unlocking the soil's ultimate potential, and achieving legendary harvests. Make it CRAZY good, incredibly motivating, and highly engaging! Do not use markdown headers, just plain text or simple bullet points.
"""
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_level="HIGH",
            ),
        )

        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=prompt,
            config=generate_content_config,
        )
        text = response.text.strip()
        
        if ml_results:
            ml_results[0]["gemini_rationale"] = text
            
        return ml_results
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return ml_results
