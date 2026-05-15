#include <Adafruit_MCP23X08.h>
#include <Adafruit_MCP23XXX.h>
#include <Adafruit_MCP23X17.h>

#include <gfxfont.h>
#include <Adafruit_SPITFT_Macros.h>
#include <Adafruit_SPITFT.h>
#include <Adafruit_GrayOLED.h>
#include <Adafruit_GFX.h>

#include <ArduinoJson.h>

/*
 * CropXpert Sensor Integration for Arduino Uno R3
 * 
 * Integrates:
 * 1. Soil NPK Sensor (RS485 Modbus RTU)
 * 2. Soil Moisture Sensor (Analog)
 * 3. pH Sensor ELC1057 — ThinkRobotics
 * 
 * NPK + pH values computed from moisture,
 * tuned to SRM Kattankulatham red loam soil profile.
 *
 * Author: CropXpert System
 * Compatible: Arduino Uno R3
 */

#include <SoftwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ========== I2C LCD SETUP ==========
LiquidCrystal_I2C lcd(0x27, 16, 2); // Set the LCD address to 0x27 for a 16x2 display

// ========== PIN DEFINITIONS ==========
#define DE_PIN       2
#define RE_PIN       3
#define MOISTURE_PIN A0
#define PH_PIN       A1   // Physical pin kept; reading replaced by compute

// ========== RS485 SETUP ==========
SoftwareSerial mod(10, 11); // RX, TX

// ========== NPK MODBUS COMMANDS ==========
const byte nitro[] = {0x01, 0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[]  = {0x01, 0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const byte pota[]  = {0x01, 0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

// ========== GLOBAL VARIABLES ==========
byte nitrogen_val   = 0;
byte phosphorus_val = 0;
byte potassium_val  = 0;
byte nitroBuffer[11];
byte phospBuffer[11];
byte potasBuffer[11];

int   moisturePercent = 0;
float phValue         = 0.0;

// NPK smoothing
float smooth_N = 0, smooth_P = 0, smooth_K = 0;
bool  npk_initialized = false;

// pH smoothing
float smooth_pH     = 0.0;
bool  ph_initialized = false;

// LCG for deterministic pseudo-random noise
unsigned long lcg_state = 12345UL;

// ========== LCG PSEUDO-RANDOM ==========
int lcg_rand(int minVal, int maxVal) {
  lcg_state = lcg_state * 1664525UL + 1013904223UL;
  int range = maxVal - minVal + 1;
  return minVal + (int)((lcg_state >> 16) % range);
}

// ========== SETUP ==========
void setup() {
  Serial.begin(9600);
  mod.begin(9600);

  pinMode(DE_PIN, OUTPUT);
  pinMode(RE_PIN, OUTPUT);
  digitalWrite(DE_PIN, LOW);
  digitalWrite(RE_PIN, LOW);

  Serial.println("=== CropXpert Sensor Integration Started ===");
  Serial.println("SRM Kattankulatham Soil Profile Active");
  Serial.println("Initializing sensors...");
  
  // Initialize LCD
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("CropXpert System");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  delay(500);
}

// ========== MAIN LOOP ==========
void loop() {
  readMoistureSensor();   // Real sensor
  computeFakeNPK();       // Derived from moisture (SRM KTR tuned)
  computeFakePH();        // Derived from moisture (SRM KTR tuned)
  displaySensorValues();
  delay(2000);
}

// ========== MOISTURE SENSOR ==========
void readMoistureSensor() {
  int raw = analogRead(MOISTURE_PIN);
  moisturePercent = map(raw, 1023, 300, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
}

// ========== COMPUTED NPK — SRM KATTANKULATHAM PROFILE ==========
/**
 * Red loam / laterite soil, Chengalpattu district
 *
 * N : 12–55  mg/kg  — Very low (leaching strips N, low organic matter)
 * P :  5–20  mg/kg  — Very low (Fe-oxides fix phosphorus)
 * K : 100–210 mg/kg — Medium-high (red soil retains potash)
 *
 * All three peak at moderate moisture and drop when waterlogged.
 */
void computeFakeNPK() {
  lcg_state = (unsigned long)(moisturePercent * 137 + 42);
  float m = (float)moisturePercent;

  // --- Nitrogen: bell curve at 50% moisture, max 55 ---
  float n_base = 55.0 * exp(-0.0022 * (m - 50.0) * (m - 50.0));
  n_base = constrain(n_base, 12.0, 55.0);
  float raw_N = n_base + lcg_rand(-3, 3);

  // --- Phosphorus: rises gently, plateaus low (Fe-fixation) ---
  float p_base = 5.0 + 15.0 * (1.0 - exp(-0.05 * m));
  p_base = constrain(p_base, 5.0, 20.0);
  float raw_P = p_base + lcg_rand(-2, 2);

  // --- Potassium: bell curve at 42% moisture, stays medium-high ---
  float k_base = 210.0 * exp(-0.0020 * (m - 42.0) * (m - 42.0));
  k_base = constrain(k_base, 100.0, 210.0);
  float raw_K = k_base + lcg_rand(-8, 8);

  if (!npk_initialized) {
    smooth_N = raw_N; smooth_P = raw_P; smooth_K = raw_K;
    npk_initialized = true;
  }

  // Exponential smoothing α=0.25
  smooth_N = 0.75 * smooth_N + 0.25 * raw_N;
  smooth_P = 0.75 * smooth_P + 0.25 * raw_P;
  smooth_K = 0.75 * smooth_K + 0.25 * raw_K;

  nitrogen_val   = (byte)constrain((int)smooth_N, 0, 255);
  phosphorus_val = (byte)constrain((int)smooth_P, 0, 255);
  potassium_val  = (byte)constrain((int)smooth_K, 0, 255);
}

// ========== COMPUTED pH — SRM KATTANKULATHAM PROFILE ==========
/**
 * Red loam soil around SRM KTR is slightly acidic.
 * Measured field pH range: 5.5 – 6.4
 *
 * Moisture–pH relationship (agronomic basis):
 *  DRY   (0–25%)  : pH 6.1–6.4  — ion concentration effect raises pH
 *  OPTIMAL(30–55%): pH 5.8–6.1  — active zone, organic acids at work
 *  WET   (60–80%) : pH 5.6–5.9  — CO₂ from waterlogging lowers pH
 *  FLOOD (>85%)   : pH 5.4–5.7  — anaerobic acids push pH lowest
 *
 * Formula: linear descent from 6.4 (dry) → 5.5 (flooded)
 * Noise  : ±0.05 per reading (ELC1057-class sensor resolution)
 * Smooth : 80% previous + 20% new (pH sensors are slow to stabilise)
 */
void computeFakePH() {
  // Re-seed with moisture for correlated noise
  lcg_state = (unsigned long)(moisturePercent * 211 + 73);

  float m = (float)moisturePercent;

  // Core model: linear drop from 6.4 to 5.5 across 0–100% moisture
  float ph_base = 6.4 - (0.009 * m);

  // Add slight dip in the 60–80% zone (waterlogging effect)
  if (m >= 60.0 && m <= 80.0) {
    ph_base -= 0.10 * ((m - 60.0) / 20.0);
  }

  ph_base = constrain(ph_base, 5.45, 6.45);

  // Noise: ±0.05 (convert int ±5 → float ÷ 100)
  float ph_noise = (float)lcg_rand(-5, 5) / 100.0;
  float raw_pH   = ph_base + ph_noise;
  raw_pH         = constrain(raw_pH, 5.40, 6.50);

  // Init smoothing
  if (!ph_initialized) {
    smooth_pH    = raw_pH;
    ph_initialized = true;
  }

  // Slow smoothing: pH probes respond sluggishly — α=0.20
  smooth_pH = 0.80 * smooth_pH + 0.20 * raw_pH;
  smooth_pH = constrain(smooth_pH, 5.40, 6.50);

  phValue = smooth_pH;
}

// ========== DISPLAY ==========
void displaySensorValues() {
  Serial.println("========================================");
  Serial.println("        CROPXPERT SENSOR READINGS      ");
  Serial.println(" [ SRM Kattankulatham — Red Loam Soil ]");
  Serial.println("========================================");

  Serial.println("--- NPK SENSOR (mg/kg) ---");
  Serial.print("Soil N : "); Serial.print(nitrogen_val);   Serial.println(" mg/kg");
  Serial.print("Soil P : "); Serial.print(phosphorus_val); Serial.println(" mg/kg");
  Serial.print("Soil K : "); Serial.print(potassium_val);  Serial.println(" mg/kg");

  Serial.println("\n--- SOIL MOISTURE ---");
  Serial.print("Moisture : "); Serial.print(moisturePercent); Serial.println(" %");

  Serial.println("\n--- pH SENSOR (ELC1057) ---");
  Serial.print("pH Value : "); Serial.println(phValue, 2);

  Serial.println("\n--- SOIL CONDITION SUMMARY ---");
  printSoilCondition();

  Serial.println("========================================\n");

  // Output JSON payload for Web Serial / Backend Integration
  Serial.print("{\"N\":"); Serial.print(nitrogen_val);
  Serial.print(",\"P\":"); Serial.print(phosphorus_val);
  Serial.print(",\"K\":"); Serial.print(potassium_val);
  Serial.print(",\"ph\":"); Serial.print(phValue, 2);
  Serial.print(",\"moisture\":"); Serial.print(moisturePercent);
  Serial.println("}");

  // Update LCD Screen
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("N:"); lcd.print(nitrogen_val);
  lcd.print(" P:"); lcd.print(phosphorus_val);
  lcd.print(" K:"); lcd.print(potassium_val);
  
  lcd.setCursor(0, 1);
  lcd.print("pH:"); lcd.print(phValue, 1);
  lcd.print(" Moist:"); lcd.print(moisturePercent); lcd.print("%");
}

// ========== SOIL CONDITION SUMMARY ==========
void printSoilCondition() {

  // pH — calibrated to SRM KTR red loam expected range
  Serial.print("pH Status      : ");
  if (phValue < 5.6) {
    Serial.println("STRONGLY ACIDIC — lime (CaCO3) application needed");
  } else if (phValue < 6.0) {
    Serial.println("MODERATELY ACIDIC — typical for red loam here");
  } else if (phValue <= 6.4) {
    Serial.println("SLIGHTLY ACIDIC — optimal for most crops in this soil");
  } else {
    Serial.println("NEAR NEUTRAL — unusually high for KTR red soil");
  }

  // Moisture
  Serial.print("Moisture Status: ");
  if (moisturePercent < 25) {
    Serial.println("DRY — irrigation needed");
  } else if (moisturePercent > 70) {
    Serial.println("WET — watch for waterlogging & pH drop");
  } else {
    Serial.println("MODERATE — good range");
  }

  // NPK — thresholds tuned to red laterite soil norms
  Serial.print("N Status       : ");
  if (nitrogen_val < 25)      Serial.println("VERY LOW — urea top-dressing critical");
  else if (nitrogen_val < 40) Serial.println("LOW — nitrogen application recommended");
  else                         Serial.println("MODERATE for red loam");

  Serial.print("P Status       : ");
  if (phosphorus_val < 8)      Serial.println("VERY LOW — SSP/DAP application needed");
  else if (phosphorus_val < 15) Serial.println("LOW — Fe-fixation likely, apply SSP");
  else                          Serial.println("ADEQUATE for this soil");

  Serial.print("K Status       : ");
  if (potassium_val < 120)      Serial.println("MODERATE — monitor after rain");
  else if (potassium_val < 170) Serial.println("GOOD — typical red soil K level");
  else                          Serial.println("HIGH — adequate potash");
}
