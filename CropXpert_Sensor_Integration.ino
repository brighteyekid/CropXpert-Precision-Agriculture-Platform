/*
 * CropXpert Sensor Integration for Arduino Uno R3
 * 
 * This code integrates:
 * 1. Soil NPK Sensor (RS485 Modbus RTU communication)
 * 2. Soil Moisture Sensor (Analog input)
 * 3. pH Sensor ELC1057 from ThinkRobotics
 * 
 * Author: CropXpert System
 * Compatible with: Arduino Uno R3
 * Serial Baud Rate: 9600
 */

#include <SoftwareSerial.h>
#include <Wire.h>

// ========== PIN DEFINITIONS ==========
// RS485 transceiver control pins (using working configuration)
#define DE_PIN 2
#define RE_PIN 3
#define MOISTURE_PIN A0   // Soil moisture sensor analog pin
#define PH_PIN A1         // pH sensor analog pin

// ========== RS485 COMMUNICATION SETUP ==========
// SoftwareSerial object for RS485 communication (using working pins)
SoftwareSerial mod(10, 11); // RX, TX

// ========== NPK SENSOR MODBUS COMMANDS ==========
// Modbus RTU requests for reading NPK values (using working commands)
const byte nitro[] = {0x01,0x03, 0x00, 0x1E, 0x00, 0x01, 0xE4, 0x0C};
const byte phos[] = {0x01,0x03, 0x00, 0x1F, 0x00, 0x01, 0xB5, 0xCC};
const byte pota[] = {0x01,0x03, 0x00, 0x20, 0x00, 0x01, 0x85, 0xC0};

// ========== GLOBAL VARIABLES ==========
// NPK sensor values and buffers
byte nitrogen_val = 0;
byte phosphorus_val = 0;
byte potassium_val = 0;
byte nitroBuffer[11];
byte phospBuffer[11];
byte potasBuffer[11];

// Other sensor values
int moisturePercent = 0;
float phValue = 0.0;

// ========== pH SENSOR CALIBRATION (ELC1057) ==========
// Based on ThinkRobotics ELC1057 sample code with improved stability
float calibration_value = 21.34 - 0.7; // Calibration offset
int phval = 0; 
unsigned long int avgval; 
int buffer_arr[20], temp; // Increased buffer size for better averaging
float ph_readings[5]; // Store last 5 pH readings for moving average
int ph_reading_index = 0;
float previous_ph = 7.0; // Initialize with neutral pH
bool ph_initialized = false;

void setup() {
  // Set the baud rate for the Serial port
  Serial.begin(9600);
  
  // Set the baud rate for the RS485 communication
  mod.begin(9600);
  
  // Define pin modes for DE and RE (using working configuration)
  pinMode(DE_PIN, OUTPUT);
  pinMode(RE_PIN, OUTPUT);
  digitalWrite(DE_PIN, LOW); // Set DE and RE pins to receive mode
  digitalWrite(RE_PIN, LOW);
  
  Serial.println("=== CropXpert Sensor Integration Started ===");
  Serial.println("Using working NPK sensor configuration");
  Serial.println("Initializing sensors...");
  delay(500);
}

void loop() {
  // Read NPK values using working method
  sendNPKRequest();
  
  // Read other sensors
  readMoistureSensor();
  readPHSensor();
  
  // Display all sensor values
  displaySensorValues();
  
  // Wait before next reading
  delay(2000);
}

// ========== NPK SENSOR FUNCTIONS (WORKING VERSION) ==========

/**
 * Send request for NPK levels using working configuration
 */
void sendNPKRequest() {
  nitrogen_val = getNitro();
  delay(250);
  phosphorus_val = getPhosp();
  delay(250);
  potassium_val = getPotass();
  delay(250);
}

/**
 * Read Nitrogen value from NPK sensor (working version)
 */
byte getNitro(){
  digitalWrite(DE_PIN,HIGH);
  digitalWrite(RE_PIN,HIGH);
  delay(10);
  if(mod.write(nitro,sizeof(nitro))==8){
    digitalWrite(DE_PIN,LOW);
    digitalWrite(RE_PIN,LOW);
    for(byte i=0;i<7;i++){
      nitroBuffer[i] = mod.read();
      Serial.print(nitroBuffer[i],HEX);
      Serial.print("\t");
    }
    Serial.println();
  }
  return nitroBuffer[4];
}

/**
 * Read Phosphorous value from NPK sensor (working version)
 */
byte getPhosp(){
  digitalWrite(DE_PIN,HIGH);
  digitalWrite(RE_PIN,HIGH);
  delay(10);
  if(mod.write(phos,sizeof(phos))==8){
    digitalWrite(DE_PIN,LOW);
    digitalWrite(RE_PIN,LOW);
    for(byte i=0;i<7;i++){
      phospBuffer[i] = mod.read();
      Serial.print(phospBuffer[i],HEX);
      Serial.print("\t");
    }
    Serial.println();
  }
  return phospBuffer[4];
}

/**
 * Read Potassium value from NPK sensor (working version)
 */
byte getPotass(){
  digitalWrite(DE_PIN,HIGH);
  digitalWrite(RE_PIN,HIGH);
  delay(10);
  if(mod.write(pota,sizeof(pota))==8){
    digitalWrite(DE_PIN,LOW);
    digitalWrite(RE_PIN,LOW);
    for(byte i=0;i<7;i++){
      potasBuffer[i] = mod.read();
      Serial.print(potasBuffer[i],HEX);
      Serial.print("\t");
    }
    Serial.println();
  }
  return potasBuffer[4];
}

// ========== MOISTURE SENSOR FUNCTIONS ==========

/**
 * Read soil moisture sensor value and convert to percentage
 * Assumes sensor outputs 0-1023 (dry to wet)
 */
void readMoistureSensor() {
  int moistureRaw = analogRead(MOISTURE_PIN);
  
  // Convert to percentage (adjust these values based on your sensor calibration)
  // Typical values: 1023 = completely dry (0%), 300 = completely wet (100%)
  moisturePercent = map(moistureRaw, 1023, 300, 0, 100);
  
  // Constrain to valid percentage range
  moisturePercent = constrain(moisturePercent, 0, 100);
}

// ========== pH SENSOR FUNCTIONS ==========

/**
 * Read pH sensor value using improved ELC1057 implementation
 * Enhanced with better noise filtering and stability
 */
void readPHSensor() {
  // Take 20 analog readings for better averaging (increased from 10)
  for(int i = 0; i < 20; i++) { 
    buffer_arr[i] = analogRead(PH_PIN);
    delay(50); // Increased delay for more stable readings
  }
  
  // Sort the analog readings to remove noise
  for(int i = 0; i < 19; i++) {
    for(int j = i + 1; j < 20; j++) {
      if(buffer_arr[i] > buffer_arr[j]) {
        temp = buffer_arr[i];
        buffer_arr[i] = buffer_arr[j];
        buffer_arr[j] = temp;
      }
    }
  }
  
  // Average the middle 10 values (remove 5 highest and 5 lowest)
  avgval = 0;
  for(int i = 5; i < 15; i++) {
    avgval += buffer_arr[i];
  }
  
  // Calculate raw pH value using calibration
  float volt = (float)avgval * 5.0 / 1024 / 10; // Divide by 10 instead of 6
  float raw_ph = -5.70 * volt + calibration_value;
  
  // Ensure raw pH is within valid range
  if(raw_ph < 0) raw_ph = 0;
  if(raw_ph > 14) raw_ph = 14;
  
  // Initialize pH readings array on first run
  if(!ph_initialized) {
    for(int i = 0; i < 5; i++) {
      ph_readings[i] = raw_ph;
    }
    ph_initialized = true;
    phValue = raw_ph;
    previous_ph = raw_ph;
    return;
  }
  
  // Apply change rate limiting (prevent sudden jumps)
  float max_change = 0.5; // Maximum pH change per reading
  if(abs(raw_ph - previous_ph) > max_change) {
    if(raw_ph > previous_ph) {
      raw_ph = previous_ph + max_change;
    } else {
      raw_ph = previous_ph - max_change;
    }
  }
  
  // Store reading in circular buffer
  ph_readings[ph_reading_index] = raw_ph;
  ph_reading_index = (ph_reading_index + 1) % 5;
  
  // Calculate moving average of last 5 readings
  float sum = 0;
  for(int i = 0; i < 5; i++) {
    sum += ph_readings[i];
  }
  
  // Apply exponential smoothing for additional stability
  float new_ph = sum / 5.0;
  phValue = (previous_ph * 0.7) + (new_ph * 0.3); // 70% previous, 30% new
  
  // Update previous pH for next iteration
  previous_ph = phValue;
  
  // Final range check
  if(phValue < 0) phValue = 0;
  if(phValue > 14) phValue = 14;
}

// ========== DISPLAY FUNCTIONS ==========

/**
 * Display all sensor values on Serial Monitor
 */
void displaySensorValues() {
  Serial.println("========================================");
  Serial.println("        CROPXPERT SENSOR READINGS      ");
  Serial.println("========================================");
  
  // NPK Values (using working format)
  Serial.println("--- NPK SENSOR (mg/kg) ---");
  Serial.print("Soil N: ");
  Serial.print(nitrogen_val);
  Serial.println(" mg/kg");
  
  Serial.print("Soil P: ");
  Serial.print(phosphorus_val);
  Serial.println(" mg/kg");
  
  Serial.print("Soil K: ");
  Serial.print(potassium_val);
  Serial.println(" mg/kg");
  
  // Moisture Value
  Serial.println("\n--- SOIL MOISTURE ---");
  Serial.print("Moisture Level: ");
  Serial.print(moisturePercent);
  Serial.println("%");
  
  // pH Value
  Serial.println("\n--- pH SENSOR ---");
  Serial.print("pH Value: ");
  Serial.println(phValue, 2);
  
  // Soil condition summary
  Serial.println("\n--- SOIL CONDITION SUMMARY ---");
  printSoilCondition();
  
  Serial.println("========================================\n");
}

/**
 * Provide basic soil condition interpretation
 */
void printSoilCondition() {
  // pH interpretation
  Serial.print("pH Status: ");
  if(phValue < 6.0) {
    Serial.println("ACIDIC (Consider lime application)");
  } else if(phValue > 7.5) {
    Serial.println("ALKALINE (Consider sulfur application)");
  } else {
    Serial.println("OPTIMAL (6.0-7.5)");
  }
  
  // Moisture interpretation
  Serial.print("Moisture Status: ");
  if(moisturePercent < 30) {
    Serial.println("DRY (Irrigation needed)");
  } else if(moisturePercent > 70) {
    Serial.println("WET (Good moisture level)");
  } else {
    Serial.println("MODERATE");
  }
  
  // NPK interpretation (basic thresholds)
  Serial.print("NPK Status: ");
  if(nitrogen_val < 50 || phosphorus_val < 20 || potassium_val < 150) {
    Serial.println("LOW NUTRIENTS (Fertilization recommended)");
  } else {
    Serial.println("ADEQUATE NUTRIENTS");
  }
}

// ========== UTILITY FUNCTIONS ==========

/**
 * Print raw sensor data for debugging
 */
void printDebugInfo() {
  Serial.println("=== DEBUG INFO ===");
  Serial.print("Raw Moisture Reading: ");
  Serial.println(analogRead(MOISTURE_PIN));
  Serial.print("Raw pH Reading: ");
  Serial.println(analogRead(PH_PIN));
  Serial.print("NPK Raw Values: N=");
  Serial.print(nitrogen_val);
  Serial.print(", P=");
  Serial.print(phosphorus_val);
  Serial.print(", K=");
  Serial.println(potassium_val);
  Serial.println("==================");
}