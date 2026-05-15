"""
CropXpert — ML inference service.
Loads trained model + scaler, runs prediction, computes final scores.
"""
import logging
import os
from datetime import datetime, timezone

import joblib
import numpy as np
from core.config import get_settings

logger = logging.getLogger("cropxpert.ml")
settings = get_settings()

# Singleton model state
_model = None
_scaler = None
_feature_names = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]


def load_model():
    """Load trained model and scaler into memory."""
    global _model, _scaler
    model_path = os.path.abspath(settings.ML_MODEL_PATH)
    scaler_path = os.path.abspath(settings.ML_SCALER_PATH)

    if os.path.exists(model_path):
        _model = joblib.load(model_path)
        logger.info("ML model loaded from %s", model_path)
    else:
        logger.warning("ML model not found at %s — predictions will fail", model_path)

    if os.path.exists(scaler_path):
        _scaler = joblib.load(scaler_path)
        logger.info("Scaler loaded from %s", scaler_path)
    else:
        logger.warning("Scaler not found at %s", scaler_path)


def get_feature_importances() -> dict[str, float]:
    """Return feature importance dict from the loaded model."""
    if _model is None:
        return {}
    try:
        importances = _model.feature_importances_
        return {name: round(float(imp), 4) for name, imp in zip(_feature_names, importances)}
    except AttributeError:
        return {}


def compute_final_score(
    ml_prob: float,
    msp_index: float,
    season_demand: float,
    alpha: float = 0.60,
    beta: float = 0.25,
    gamma: float = 0.15,
) -> float:
    """Market-adjusted final score."""
    return alpha * ml_prob + beta * msp_index + gamma * season_demand


def get_season_demand(crop: str) -> float:
    """Return season multiplier based on current month and crop season."""
    current_month = datetime.now().strftime("%B")
    season_info = settings.CROP_SEASONS.get(crop, {})
    sowing_months = season_info.get("sowing", [])
    harvest_months = season_info.get("harvest", [])

    if current_month in sowing_months:
        return 1.0  # peak demand
    elif current_month in harvest_months:
        return 0.7
    else:
        return 0.5  # off-season


def get_msp_index(crop: str) -> float:
    """Normalize MSP to 0-1 scale across all 22 crops."""
    msp_map = settings.MSP_FALLBACK
    crop_msp = msp_map.get(crop, 0)
    max_msp = max(msp_map.values()) if msp_map else 1
    return crop_msp / max_msp if max_msp > 0 else 0


def get_sowing_tip(crop: str) -> str:
    """Generate sowing tip."""
    info = settings.CROP_SEASONS.get(crop, {})
    months = info.get("sowing", [])
    if months:
        return f"Optimal sowing window: {', '.join(months)}. Prepare seedbed 2 weeks before."
    return "Consult local agronomist for region-specific sowing guidance."


def get_fertilizer_dose(crop: str) -> dict:
    """Return recommended fertilizer doses."""
    doses = {
        "Rice": {"urea": "120 kg/acre", "dap": "50 kg/acre"},
        "Wheat": {"urea": "100 kg/acre", "dap": "60 kg/acre"},
        "Maize": {"urea": "110 kg/acre", "dap": "55 kg/acre"},
        "Cotton": {"urea": "80 kg/acre", "dap": "40 kg/acre"},
    }
    return doses.get(crop, {"urea": "100 kg/acre", "dap": "50 kg/acre"})


def predict(
    nitrogen: float, phosphorus: float, potassium: float,
    ph: float, moisture: float, temperature: float,
    rainfall: float, humidity: float = 0.0,
) -> list[dict]:
    """
    Run inference and return top-3 crops with final scores.
    Feature order must match training: N, P, K, temperature, humidity, ph, rainfall
    """
    if _model is None or _scaler is None:
        raise RuntimeError("ML model not loaded — run `python ml/train.py` first")

    features = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
    features_scaled = _scaler.transform(features)
    probabilities = _model.predict_proba(features_scaled)[0]

    labels = settings.CROP_LABELS
    crop_probs = sorted(
        zip(labels, probabilities),
        key=lambda x: x[1],
        reverse=True,
    )

    results = []
    for rank, (crop, ml_prob) in enumerate(crop_probs[:3], start=1):
        msp = settings.MSP_FALLBACK.get(crop, 0)
        msp_idx = get_msp_index(crop)
        season = get_season_demand(crop)
        final = compute_final_score(float(ml_prob), msp_idx, season)
        season_info = settings.CROP_SEASONS.get(crop, {})

        mandi_price = int(msp * 1.01)  # simulated 1% above MSP
        delta_pct = round((mandi_price - msp) / msp * 100, 1) if msp > 0 else 0

        results.append({
            "rank": rank,
            "crop": crop,
            "ml_confidence": round(float(ml_prob), 4),
            "msp_inr_per_quintal": msp,
            "mandi_price": mandi_price,
            "mandi_trend": f"+{delta_pct}% above MSP" if delta_pct >= 0 else f"{delta_pct}% below MSP",
            "final_score": round(final, 4),
            "sowing_tip": get_sowing_tip(crop),
            "sowing_months": season_info.get("sowing", []),
            "fertilizer_dose": get_fertilizer_dose(crop),
        })

    return results
