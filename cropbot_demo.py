import httpx
import time

def run_cropbot_demo():
    print("="*60)
    print("  🌾 CROPBOT SMS/WHATSAPP DEMONSTRATOR 🌾")
    print("="*60)
    print("Simulating a farmer with a basic ₹500 keypad phone in Pune.")
    print("Farmer types an SMS to the shortcode 55444...\n")
    
    # The raw SMS payload format mentioned in the slide
    sms_text = "CROP N90 P42 K43 PH6.5 DIST PUNE"
    
    print(f"📱 OUTGOING SMS: '{sms_text}'")
    print("📡 Sending to Twilio/MSG91 Webhook (FastAPI: /api/bot/sms)...\n")
    
    start_time = time.time()
    
    try:
        # Hitting the backend API we just created
        response = httpx.post(
            "http://localhost:8000/api/bot/sms", 
            data={"Body": sms_text, "From": "+919876543210"},
            timeout=5.0
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            reply = response.json().get("reply", "")
            
            print("="*60)
            print(f"⏱️  Inference + Network time: {elapsed:.2f}ms")
            print(f"📏 SMS Character Count: {len(reply)}/160")
            print("="*60)
            print(f"💬 INCOMING SMS REPLY:\n\n{reply}")
            print("="*60)
            print("\nDemo completed successfully. The exact same ML pipeline was used!")
        else:
            print(f"❌ Error: Backend returned status code {response.status_code}")
            print("Make sure your uvicorn server is running on port 8000!")
            
    except httpx.RequestError:
        print("❌ Error: Could not connect to the backend.")
        print("Make sure your uvicorn server is running (uvicorn main:app --host 0.0.0.0 --port 8000)")

if __name__ == "__main__":
    run_cropbot_demo()
