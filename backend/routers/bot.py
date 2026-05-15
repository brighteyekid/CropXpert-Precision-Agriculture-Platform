from fastapi import APIRouter, Form, HTTPException
from services.ml_service import predict
import re

router = APIRouter(tags=["CropBot"])

@router.post("/sms")
def handle_sms(
    Body: str = Form(...),
    From: str = Form(...)
):
    """
    Simulates a Twilio/MSG91 SMS webhook.
    Accepts text format: CROP N90 P42 K43 PH6.5 DIST PUNE
    Returns a <160 char string.
    """
    text = Body.upper().strip()
    
    # Parse format: CROP N90 P42 K43 PH6.5 DIST PUNE
    # We use regex to be flexible with spaces
    try:
        n_match = re.search(r'N(\d+)', text)
        p_match = re.search(r'P(\d+)', text)
        k_match = re.search(r'K(\d+)', text)
        ph_match = re.search(r'PH([\d\.]+)', text)
        
        if not all([n_match, p_match, k_match, ph_match]):
            return {"reply": "Format error. Send: CROP N90 P42 K43 PH6.5 DIST PUNE"}
            
        n = float(n_match.group(1))
        p = float(p_match.group(1))
        k = float(k_match.group(1))
        ph = float(ph_match.group(1))
        
        # Default mock values for SMS speed (since SMS has no sensors)
        moisture = 50.0
        temperature = 28.0
        rainfall = 100.0
        humidity = 70.0
        
        # Run prediction pipeline (2.3ms)
        results = predict(
            nitrogen=n, phosphorus=p, potassium=k,
            ph=ph, moisture=moisture, temperature=temperature,
            rainfall=rainfall, humidity=humidity
        )
        
        top_crop = results[0]
        crop_name = top_crop["crop"].upper()
        confidence = int(top_crop["ml_confidence"] * 100)
        msp = top_crop.get("msp_inr_per_quintal", 0)
        mandi = int(msp * 1.01) if msp else 0
        
        # Format the 160 character SMS
        reply = f"{crop_name} {confidence}% MSP {msp}/q MANDI {mandi}. Sow {top_crop.get('sowing_months', ['Now'])[0][:3]}. Good profit."
        
        return {"reply": reply[:160]}
        
    except Exception as e:
        return {"reply": "System Error. Please try again."}
