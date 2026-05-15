/*
 * ╔══════════════════════════════════════════════════════════════╗
 * ║          CropXpert ESP32 + 2.8" TFT MQTT DISPLAY             ║
 * ║                                                              ║
 * ║  Role: Connects via WiFi to the CropXpert MQTT Broker.       ║
 * ║  Subscribes to sensor topics and updates display in          ║
 * ║  real-time. NO sensors directly connected to ESP32!          ║
 * ║                                                              ║
 * ║  TFT Wiring (TFT ↔ ESP32):                                   ║
 * ║  VCC → 3.3V  |  GND → GND                                    ║
 * ║  CS  → 17    |  DC  → 16                                     ║
 * ║  MOSI→ 23    |  SCK → 18   |  MISO→ 19                       ║
 * ║  LED → 32 (PWM)            |  RST → 5                        ║
 * ║                                                              ║
 * ║  Libraries (install via Arduino Library Manager):            ║
 * ║  ▸ PubSubClient (by Nick O'Leary)                            ║
 * ║  ▸ ArduinoJson (v6 or v7)                                    ║
 * ║  ▸ Adafruit GFX Library                                      ║
 * ║  ▸ Adafruit ILI9341                                          ║
 * ╚══════════════════════════════════════════════════════════════╝
 */

#include <SPI.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>

// ═══════════════════════ CONFIGURATION ═══════════════════════════

const char* WIFI_SSID     = "YourWiFiSSID";       // <-- CHANGE THIS
const char* WIFI_PASSWORD = "YourWiFiPassword";   // <-- CHANGE THIS

const char* MQTT_BROKER   = "192.168.1.100";      // <-- IP OF YOUR BACKEND PC
const int   MQTT_PORT     = 1883;                 // Default Mosquitto port
const char* MQTT_TOPIC    = "cropxpert/farm/+/sensors";

// ── TFT & Touch & SD Pins (2.8" ILI9341 SPI) ───────────────────────
// Exact requested wiring:
#define TFT_CS    17
#define TFT_DC    16   // D/C
#define TFT_RST    5   // RESET
#define TFT_MOSI  23   // MOSI & T_DI & SD_MOSI
#define TFT_CLK   18   // SCK & T_CLK & SD_SCK
#define TFT_MISO  19   // MISO & T_DO & SD_MISO
#define TFT_LED   32   // LED
#define T_CS      21   // Touch CS
#define SD_CS     12   // SD Card CS

// ═══════════════════════ COLOUR PALETTE ══════════════════════════
#define C_BG        0x18A3
#define C_SURFACE   0x2124
#define C_ACCENT    0x3FE0
#define C_TEXT      0xFFFF
#define C_MUTED     0xAD75
#define C_GREEN     0x07E0
#define C_AMBER     0xFD20
#define C_RED       0xF800
#define C_RULE      0x2965

// ═══════════════════════════ GLOBALS & STRUCTS ════════════════════

struct Range { float low; float high; };
const Range R_N    = {  80, 140 };
const Range R_P    = {  20,  60 };
const Range R_K    = { 150, 280 };
const Range R_PH   = { 6.0, 7.5 };
const Range R_MOIS = {  40,  70 };
const Range R_TEMP = {  20,  35 };
const Range R_HUM  = {  50,  85 };

struct RowDef { const char* label; float value; const char* unit; Range range; bool isInt; };

Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_MOSI, TFT_CLK, TFT_RST, TFT_MISO);

WiFiClient espClient;
PubSubClient mqtt(espClient);

// Sensor Data
float N = 0, P = 0, K = 0;
float phValue = 0, temperature = 0, humidity = 0;
int   moisture = 0;

int updatesReceived = 0;

// ═══════════════════════════ SETUP ═══════════════════════════════

void setupCode() {
  Serial.begin(115200);
  Serial.println("\n╔══ CropXpert MQTT TFT Display ══╗");

  // Deactivate Touch and SD Card to free the SPI bus for the TFT Screen
  pinMode(T_CS, OUTPUT);
  digitalWrite(T_CS, HIGH);
  pinMode(SD_CS, OUTPUT);
  digitalWrite(SD_CS, HIGH);

  pinMode(TFT_LED, OUTPUT);
  analogWrite(TFT_LED, 200);

  tft.begin();
  tft.setRotation(1);
  showBootScreen();

  // Connect WiFi
  tftStatus("Connecting to WiFi...", C_AMBER);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries++ < 20) { delay(500); }
  
  if (WiFi.status() == WL_CONNECTED) {
    tftStatus("WiFi Connected! IP: " + WiFi.localIP().toString(), C_GREEN);
  } else {
    tftStatus("WiFi Failed!", C_RED);
  }
  delay(1500);
  
  drawDashboardFrame();
  updateDashboard();

  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqttCallback);
}

void setup() { setupCode(); }

// ════════════════════════════ LOOP ═══════════════════════════════
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!mqtt.connected()) {
      reconnectMQTT();
    }
    mqtt.loop();
  }
}

// ════════════════════════ MQTT LOGIC ════════════════════════════

void reconnectMQTT() {
  static unsigned long lastTry = 0;
  if (millis() - lastTry < 5000) return; // Try every 5s
  lastTry = millis();

  updateStatusBar();
  Serial.print("Connecting to MQTT...");
  if (mqtt.connect("ESP32_CropXpert_Display")) {
    Serial.println("connected");
    mqtt.subscribe(MQTT_TOPIC);
    updateStatusBar();
  } else {
    Serial.print("failed, rc=");
    Serial.println(mqtt.state());
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Convert payload to string
  String msg = "";
  for (unsigned int i = 0; i < length; i++) {
    msg += (char)payload[i];
  }
  Serial.printf("Message arrived [%s]: %s\n", topic, msg.c_str());

  // Parse JSON
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, msg);
  
  if (!err) {
    // CropXpert backend uses these keys (matching sensors schema)
    if (!doc["nitrogen"].isNull()) N = doc["nitrogen"];
    if (!doc["phosphorus"].isNull()) P = doc["phosphorus"];
    if (!doc["potassium"].isNull()) K = doc["potassium"];
    if (!doc["ph"].isNull()) phValue = doc["ph"];
    if (!doc["moisture"].isNull()) moisture = doc["moisture"];
    if (!doc["temperature"].isNull()) temperature = doc["temperature"];
    if (!doc["humidity"].isNull()) humidity = doc["humidity"];
    
    // Also support short keys in case raw uno data comes through bypass
    if (!doc["N"].isNull()) N = doc["N"];
    if (!doc["P"].isNull()) P = doc["P"];
    if (!doc["K"].isNull()) K = doc["K"];
    
    updatesReceived++;
    updateDashboard(); // Instantly update screen
  }
}

// ═══════════════════════ GUI DRAWING ════════════════════════════

void showBootScreen() {
  tft.fillScreen(C_BG);
  tft.fillRect(10, 40, 300, 60, C_SURFACE);
  tft.drawRect(10, 40, 300, 60, C_ACCENT);
  tft.setTextColor(C_ACCENT);
  tft.setTextSize(3);
  tft.setCursor(38, 56);
  tft.print("CropXpert");
  tft.setTextSize(1);
  tft.setTextColor(C_MUTED);
  tft.setCursor(60, 90);
  tft.print("MQTT Live Display Node");

  tft.drawRect(20, 175, 280, 10, C_MUTED);
  for (int i = 0; i <= 280; i += 28) { tft.fillRect(21, 176, i, 8, C_ACCENT); delay(20); }
}

void drawDashboardFrame() {
  tft.fillScreen(C_BG);
  tft.fillRect(0, 0, 320, 24, C_SURFACE);
  tft.setTextColor(C_ACCENT); tft.setTextSize(1); tft.setCursor(6, 8);
  tft.print("CROPXPERT");
  tft.setTextColor(C_MUTED); tft.setCursor(90, 8);
  tft.print("Live MQTT Readings");

  tft.setTextColor(C_MUTED); tft.setCursor(6, 32);  tft.print("PARAMETER");
  tft.setCursor(170, 32); tft.print("VALUE");
  tft.setCursor(235, 32); tft.print("STATUS");
  tft.drawFastHLine(0, 41, 320, C_RULE);
  for (int i = 0; i < 9; i++) tft.drawFastHLine(0, 42 + i * 22, 320, C_RULE);
  tft.fillRect(0, 222, 320, 18, C_SURFACE);
}

uint16_t statusColor(float val, Range r) {
  if (val == 0) return C_MUTED;
  if (val < r.low  * 0.75f) return C_RED;
  if (val < r.low  || val > r.high) return C_AMBER;
  return C_GREEN;
}

const char* statusLabel(float val, Range r) {
  if (val == 0) return "WAITING";
  if (val < r.low  * 0.75f) return "CRITICAL";
  if (val < r.low)           return "LOW";
  if (val > r.high)          return "HIGH";
  return "OPTIMAL";
}

void drawRow(int rowIdx, RowDef row) {
  int y = 44 + rowIdx * 22;
  tft.fillRect(1, y + 1, 318, 20, C_BG);
  
  tft.setTextColor(C_TEXT); tft.setTextSize(1); tft.setCursor(6, y + 7);
  tft.print(row.label);

  tft.setTextColor(C_TEXT); tft.setTextSize(2); tft.setCursor(156, y + 4);
  if (row.isInt) tft.print((int)row.value); else tft.print(row.value, 1);
  
  tft.setTextSize(1); tft.setTextColor(C_MUTED); tft.print(" "); tft.print(row.unit);

  uint16_t col = statusColor(row.value, row.range);
  const char* lbl = statusLabel(row.value, row.range);
  tft.fillRect(232, y + 4, 80, 14, col);
  tft.setTextColor(C_BG); tft.setTextSize(1);
  tft.setCursor(232 + (80 - strlen(lbl) * 6) / 2, y + 8);
  tft.print(lbl);
}

void updateDashboard() {
  RowDef rows[] = {
    { "N  Nitrogen",    N,           "mg", R_N,    true  },
    { "P  Phosphorus",  P,           "mg", R_P,    true  },
    { "K  Potassium",   K,           "mg", R_K,    true  },
    { "pH Acidity",     phValue,     "",   R_PH,   false },
    { "H2O Moisture",   (float)moisture, "%", R_MOIS, true  },
    { "T  Temperature", temperature, "C",  R_TEMP, false },
    { "RH Humidity",    humidity,    "%",  R_HUM,  true  },
  };
  for (int i = 0; i < 7; i++) drawRow(i, rows[i]);

  tft.fillRect(1, 43 + 7 * 22 + 1, 318, 20, C_BG);
  tft.setTextColor(C_MUTED); tft.setTextSize(1); tft.setCursor(6, 43 + 7 * 22 + 8);
  tft.printf("MQTT Msgs: %d   Uptime: %lus", updatesReceived, millis() / 1000);
  updateStatusBar();
}

void updateStatusBar() {
  tft.fillRect(0, 222, 320, 18, C_SURFACE); tft.setTextSize(1); tft.setCursor(6, 229);
  if (!mqtt.connected()) {
    tft.setTextColor(C_AMBER); tft.print("MQTT: reconnecting...");
  } else {
    tft.setTextColor(C_GREEN); tft.printf("MQTT: OK  |  Topic: %s", MQTT_TOPIC);
  }
}

void tftStatus(String msg, uint16_t col) {
  tft.fillRect(0, 200, 320, 20, C_BG);
  tft.setTextColor(col); tft.setTextSize(1); tft.setCursor(6, 207); tft.print(msg);
}
