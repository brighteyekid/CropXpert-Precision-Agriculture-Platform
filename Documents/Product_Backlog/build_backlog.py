from openpyxl import load_workbook, Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                               GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.styles.fills import FILL_SOLID
import copy

# ── Colour palette ────────────────────────────────────────────────────────────
DARK_BLUE   = "1F3864"
MID_BLUE    = "2E5FA3"
LIGHT_BLUE  = "D6E4F7"
RED         = "C00000"
GREEN       = "1A7A1A"
AMBER       = "BF8F00"
GREY_HDR    = "404040"
WHITE       = "FFFFFF"
PALE_GREEN  = "E2EFDA"
PALE_RED    = "FCE4D6"
PALE_AMBER  = "FFF2CC"
PALE_BLUE   = "DEEAF1"
PALE_GREY   = "F2F2F2"

def fill(hex_color):
    return PatternFill(fill_type=FILL_SOLID, fgColor=hex_color)

def font(bold=False, color="000000", size=10, italic=False):
    return Font(name="Arial", bold=bold, color=color, size=size, italic=italic)

def align(h="left", v="top", wrap=True):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def border(style="thin", color="BFBFBF"):
    s = Side(style=style, color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def thick_border():
    thin  = Side(style="thin",   color="BFBFBF")
    thick = Side(style="medium", color=DARK_BLUE)
    return Border(left=thick, right=thick, top=thick, bottom=thick)

def apply(cell, fnt=None, fl=None, al=None, bdr=None):
    if fnt: cell.font      = fnt
    if fl:  cell.fill      = fl
    if al:  cell.alignment = al
    if bdr: cell.border    = bdr

# Status colours
STATUS_COLOR = {
    "Done":          ("E2EFDA", "1A7A1A"),
    "In Progress":   ("DEEAF1", "1F3864"),
    "Pending":       ("FFF2CC", "BF8F00"),
    "Backlog":       ("F2F2F2", "595959"),
    "Ready for Dev": ("FCE4D6", "C00000"),
    "In Testing":    ("EAD1DC", "7B0099"),
}

PRIORITY_COLOR = {
    "Must":   ("FCE4D6", "C00000"),
    "Should": ("FFF2CC", "BF8F00"),
    "Could":  ("E2EFDA", "1A7A1A"),
    "Won't":  ("F2F2F2", "595959"),
}

# ── Backlog data ──────────────────────────────────────────────────────────────
# Columns: ID, Title, Epic, Sprint, User Story, Priority, Status,
#          Acceptance Criteria, Functional Requirements,
#          Non-Functional Requirements, Estimate, Effort

BACKLOG = [
    # ── EPIC 1: IoT SENSOR MODULE ─────────────────────────────────────────────
    (1, "NPK Sensor Integration",
     "IoT Sensor Module", "Sprint 1",
     "As a farmer, I want the system to automatically read Nitrogen, Phosphorus, and Potassium levels from my soil so that I don't need to visit a lab.",
     "Must", "Done",
     "1. RS485 NPK sensor data is read every 60 seconds.\n2. N, P, K values are displayed in mg/kg.\n3. Values update on the web dashboard in real-time.",
     "Interface RS485 NPK sensor via MAX485 module to Arduino UNO. Parse Modbus RTU response. Transmit data over serial/MQTT.",
     "Sensor read latency < 2 s. Data loss rate < 0.1%. Works at soil temperatures 5–45°C.",
     "5 days", "5 days"),

    (2, "Soil pH Sensor Integration",
     "IoT Sensor Module", "Sprint 1",
     "As a farmer, I want to know my soil's pH level in real time so that I can understand soil acidity without any lab test.",
     "Must", "Done",
     "1. pH value read from analog pin A0.\n2. Reading displayed with ±0.1 resolution.\n3. Alert shown if pH is outside optimal range (5.5–7.5).",
     "Connect analog pH sensor to Arduino A0. Calibrate using buffer solutions (pH 4, 7, 10). Map analog voltage to pH scale.",
     "Accuracy ±0.1 pH units. Response time < 3 s. Calibration must survive power cycle.",
     "3 days", "3 days"),

    (3, "Soil Moisture Sensor Integration",
     "IoT Sensor Module", "Sprint 1",
     "As a farmer, I want real-time soil moisture readings so that I can make timely irrigation decisions.",
     "Must", "Done",
     "1. Moisture percentage displayed (0–100%).\n2. Capacitive sensor used for corrosion resistance.\n3. Low-moisture alert triggered below 25%.",
     "Connect capacitive soil moisture sensor to Arduino analog pin. Convert raw ADC value to volumetric moisture percentage. Publish via MQTT.",
     "Sensor lifespan > 2 years in-field. Read frequency configurable (default 60 s). Accuracy ±3%.",
     "3 days", "3 days"),

    (4, "DHT22 Temperature & Humidity Integration",
     "IoT Sensor Module", "Sprint 1",
     "As a system, I need temperature and humidity data so that the ML model has all required input features.",
     "Must", "Done",
     "1. Temperature and humidity polled every 30 s.\n2. Values shown on dashboard alongside soil readings.\n3. Sensor failure triggers a dashboard alert.",
     "Integrate DHT22 with Arduino digital pin. Implement retry logic for failed reads. Send values to MQTT broker.",
     "Temperature accuracy ±0.5°C. Humidity accuracy ±2–5%. Continuous uptime > 99% over 30-day test period.",
     "2 days", "2 days"),

    (5, "Rainfall Data Auto-Fetch (OpenWeatherMap)",
     "IoT Sensor Module", "Sprint 1",
     "As a farmer, I want rainfall data fetched automatically using my location so that I don't have to enter it manually.",
     "Must", "Done",
     "1. API call made using farmer's GPS coordinates.\n2. 7-day average rainfall returned in mm.\n3. Fallback to manual entry if API fails.",
     "Integrate OpenWeatherMap One Call API. Parse precipitation field. Cache results for 6 hours to avoid rate-limit.",
     "API response time < 3 s. Graceful fallback on network failure. Cached value served within 50 ms.",
     "3 days", "3 days"),

    # ── EPIC 2: ML CROP RECOMMENDATION ENGINE ────────────────────────────────
    (6, "Dataset Collection & Preprocessing",
     "ML Recommendation Engine", "Sprint 2",
     "As a developer, I want a clean, representative Indian crop dataset so that the ML model generalises well across Indian agro-climatic zones.",
     "Must", "Done",
     "1. Dataset contains ≥2,200 samples across 22 Indian crops.\n2. No missing values after preprocessing.\n3. Train/val/test split is 70/15/15 stratified.",
     "Download Kaggle Crop Recommendation Dataset. Augment with ICAR regional soil data. Apply Z-score outlier removal. Fit and serialise StandardScaler.",
     "Class balance ≤1.5× ratio. Scaler saved separately for inference. Preprocessing pipeline is reproducible via script.",
     "4 days", "4 days"),

    (7, "Random Forest Model Training",
     "ML Recommendation Engine", "Sprint 2",
     "As a system, I need a trained Random Forest model so that crop recommendations are accurate and fast.",
     "Must", "Done",
     "1. Model achieves ≥99% accuracy on test set.\n2. Inference time < 5 ms per prediction.\n3. Model file size < 100 MB.",
     "Train Random Forest with GridSearchCV (100–500 estimators, max_depth tuning). 5-fold cross-validation. Serialise model with joblib.",
     "Accuracy ≥99.2% on 22-class test set. Model size ≤10 MB. Reproducible via seed=42.",
     "5 days", "5 days"),

    (8, "Multi-Model Comparison (XGBoost, SVM, MLP, LightGBM)",
     "ML Recommendation Engine", "Sprint 2",
     "As a developer, I want to compare multiple ML models so that I can select the best-performing one for production.",
     "Should", "Done",
     "1. All 5 models evaluated on same test split.\n2. Comparison table showing Accuracy, Precision, Recall, F1.\n3. Best model selected and documented.",
     "Train XGBoost, SVM (RBF), MLP (128-64-32), LightGBM. Use same preprocessing pipeline. Export metrics to CSV.",
     "Evaluation is reproducible. Confusion matrix saved for each model. Report generated automatically.",
     "6 days", "6 days"),

    (9, "ML API Endpoint (FastAPI)",
     "ML Recommendation Engine", "Sprint 2",
     "As a web application, I need a REST API endpoint so that sensor data can be sent and crop predictions returned in JSON.",
     "Must", "In Progress",
     "1. POST /predict accepts 7-feature JSON input.\n2. Returns top-3 crops with confidence scores.\n3. Returns HTTP 422 for invalid inputs.",
     "Build FastAPI app. Load serialised RF model and scaler at startup. Validate input with Pydantic. Return JSON response.",
     "API response time < 200 ms (p95). Handles 50 concurrent requests. Input validation rejects out-of-range values.",
     "4 days", "3 days"),

    (10, "Top-3 Crop Recommendations with Confidence Scores",
     "ML Recommendation Engine", "Sprint 2",
     "As a farmer, I want to see the top 3 crop recommendations with their confidence scores so that I have options to choose from.",
     "Must", "In Progress",
     "1. Dashboard shows top-3 crops ranked by confidence.\n2. Confidence shown as percentage with colour-coded bar.\n3. Clicking a crop shows its sowing and care tips.",
     "Use predict_proba from RF model. Sort descending. Map crop index to name dictionary. Return top 3.",
     "All 3 recommendations returned within 200 ms. Confidence percentages sum to ≤100%. Crop names localised per language setting.",
     "3 days", "2 days"),

    # ── EPIC 3: MARKET-AWARE RECOMMENDATION (NOVELTY) ────────────────────────
    (11, "AGMARKNET MSP Data Integration",
     "Market Intelligence Layer", "Sprint 3",
     "As a farmer, I want to see the current Minimum Support Price for recommended crops so that I can choose crops that are both soil-suitable and economically viable.",
     "Must", "Pending",
     "1. MSP data fetched for all 22 crops from AGMARKNET API.\n2. Data refreshed every 24 hours.\n3. MSP displayed alongside crop recommendation.",
     "Integrate AGMARKNET REST API. Parse commodity MSP fields. Cache in SQLite with 24-hour TTL. Display ₹/quintal alongside recommendation.",
     "API failure must not break recommendation flow (graceful degradation). Cache hit rate > 90% during normal operation.",
     "5 days", "-"),

    (12, "Weighted Market-Agronomic Scoring Function",
     "Market Intelligence Layer", "Sprint 3",
     "As a farmer, I want the system to balance soil suitability and market price so that I get recommendations that are both agronomically and financially optimal.",
     "Must", "Pending",
     "1. Final score = 0.60×ML_prob + 0.25×MSP_Index + 0.15×SeasonDemand.\n2. Weights configurable in admin settings.\n3. Score breakdown shown in detailed view.",
     "Implement scoring formula in Python. Normalise MSP values as index (0–1). Combine with ML probability. Re-rank top-3 output.",
     "Score computation adds < 50 ms to response. Formula weights validated by domain expert (agricultural officer). Unit tested with mock data.",
     "4 days", "-"),

    (13, "Mandi Price Trend Graphs",
     "Market Intelligence Layer", "Sprint 3",
     "As a farmer, I want to see 3-month price trend charts for recommended crops so that I can time my selling decision.",
     "Should", "Backlog",
     "1. Line chart shows last 90 days of mandi prices.\n2. Chart loads within 2 s.\n3. Chart is interactive (hover shows date and price).",
     "Pull historical price data from AGMARKNET. Store in SQLite. Render chart with Chart.js on the frontend.",
     "Chart renders within 2 s on 3G connection. Data sourced from at least 3 mandis per crop. Mobile-responsive.",
     "5 days", "-"),

    # ── EPIC 4: FARMER SUPPORT PORTAL ─────────────────────────────────────────
    (14, "Government Scheme Advisory Module",
     "Farmer Support Portal", "Sprint 3",
     "As a farmer, I want to see government welfare schemes I am eligible for so that I can access PM-KISAN, crop insurance, and other benefits.",
     "Must", "Pending",
     "1. At least 6 schemes displayed with eligibility, benefits, documents, and apply link.\n2. Schemes filtered by farmer's state.\n3. Content updated from MyScheme.gov.in API monthly.",
     "Build Scheme model in database. Populate with PM-KISAN, PM Fasal Bima Yojana, Soil Health Card, PMKSY, KCC, state subsidies. Render as card layout.",
     "Scheme data must be accurate as of current month. Apply links must be live government URLs. Page load < 3 s.",
     "5 days", "-"),

    (15, "Loan & Financial Guidance Module",
     "Farmer Support Portal", "Sprint 3",
     "As a farmer, I want clear guidance on low-interest and zero-interest agricultural loans so that I can make informed financing decisions.",
     "Must", "Backlog",
     "1. At least 5 loan programs listed (KCC, NABARD, state waivers).\n2. Each entry shows interest rate, eligibility, and application steps.\n3. EMI calculator available for KCC loans.",
     "Create Loan model. Populate KCC (0–4% interest), NABARD schemes, PM Formalization micro-food processing. Build EMI calculator component.",
     "Loan information reviewed and approved by faculty advisor. EMI calculator validated against RBI formula. No broken links.",
     "4 days", "-"),

    (16, "Farming Campaign & Awareness Section",
     "Farmer Support Portal", "Sprint 4",
     "As a farmer, I want access to training content on modern farming so that I can improve my techniques sustainably.",
     "Could", "Backlog",
     "1. At least 10 articles/videos on organic farming, fertigation, drip irrigation.\n2. Content searchable by topic.\n3. Content available in all 4 supported languages.",
     "Create Article model with title, content, language, tags. Build search with full-text indexing. Admin panel for content management.",
     "Page load < 3 s. Search returns results < 1 s. Content accessible on 2G connection (text-first).",
     "6 days", "-"),

    (17, "Farm Profit Calculator",
     "Farmer Support Portal", "Sprint 4",
     "As a farmer, I want to estimate profit per crop per acre before planting so that I can make the best financial decision.",
     "Should", "Backlog",
     "1. Calculator takes crop, acreage, and location as input.\n2. Outputs estimated input cost, yield, market price, and net profit.\n3. Results shown as comparison table for top-3 recommended crops.",
     "Build profit estimation logic using AGMARKNET prices and standard input cost data (per crop per state). Render as interactive table.",
     "Calculation completes < 1 s. Input cost data sourced from State Agriculture Department reports. Mobile-friendly layout.",
     "4 days", "-"),

    # ── EPIC 5: MULTILINGUAL INTERFACE ────────────────────────────────────────
    (18, "Multilingual UI — Hindi, Marathi, Tamil, Telugu",
     "Multilingual Interface", "Sprint 4",
     "As a farmer with limited English literacy, I want to use the entire platform in my native language so that I can understand all recommendations and advice.",
     "Must", "Pending",
     "1. Full UI available in Hindi, Marathi, Tamil, Telugu.\n2. Language auto-detected from browser locale.\n3. Manual toggle persisted in user profile.",
     "Implement i18n with React-i18next. Build JSON translation files for all 4 languages. Localise crop names, scheme descriptions, advisory text. Validate translations with native speakers.",
     "Language switch completes < 500 ms. Zero untranslated strings in production build. RTL layout not required (all 4 languages are LTR).",
     "8 days", "-"),

    (19, "Vernacular Crop Advisory Text",
     "Multilingual Interface", "Sprint 4",
     "As a farmer, I want crop-specific sowing tips, care guidelines, and harvest timing shown in my language so that I can act on the recommendation immediately.",
     "Should", "Backlog",
     "1. Each crop has sowing month, fertiliser schedule, and harvest window.\n2. Text displayed in selected language.\n3. Advisory validated by agricultural domain expert.",
     "Create CropAdvisory model with fields for each language. Populate for all 22 crops. Link to recommendation output API.",
     "Advisory text reviewed by KVK agricultural officer. No machine-translation errors for key agronomic terms. Displays correctly on mobile.",
     "6 days", "-"),

    # ── EPIC 6: CROPBOT (WHATSAPP & SMS) ─────────────────────────────────────
    (20, "WhatsApp CropBot (Twilio Integration)",
     "CropBot — WhatsApp & SMS", "Sprint 4",
     "As a farmer with a smartphone but no computer, I want to get crop recommendations via WhatsApp so that I can use the system from my field.",
     "Must", "Pending",
     "1. Farmer sends soil values in natural language via WhatsApp.\n2. Bot parses N, P, K, pH, moisture values from message.\n3. Bot replies with top-3 crops + MSP price + sowing tip within 10 s.",
     "Integrate Twilio WhatsApp API with FastAPI webhook. Build NLP parser for multilingual input (Hindi/English). Connect to ML prediction endpoint. Format and return response.",
     "Bot response time < 10 s end-to-end. Handles malformed input gracefully. Supports Hindi and English input. Uptime > 99.5%.",
     "7 days", "-"),

    (21, "SMS Shortcode Fallback Bot",
     "CropBot — WhatsApp & SMS", "Sprint 4",
     "As a farmer with a basic keypad phone and no internet, I want to get recommendations via SMS so that I am not excluded from the platform.",
     "Should", "Backlog",
     "1. Farmer texts: CROP N90 P42 K43 PH6.5 DIST PUNE\n2. System parses values and returns top-1 crop + price via SMS.\n3. Works from any GSM phone without data connection.",
     "Integrate MSG91 SMS API. Define shortcode format parser. Connect to ML API. Format reply within 160-character SMS limit.",
     "SMS delivered within 60 s. Parser handles missing fields with defaults. Cost per SMS < ₹0.10. Tested on Airtel, Jio, BSNL networks.",
     "5 days", "-"),

    # ── EPIC 7: SOIL HEALTH DASHBOARD ────────────────────────────────────────
    (22, "Soil Health Trend Logging (SQLite)",
     "Soil Health Dashboard", "Sprint 2",
     "As a farmer, I want my soil readings saved over time so that I can see if my soil health is improving or degrading.",
     "Must", "In Progress",
     "1. Every sensor reading stored with timestamp and location.\n2. Data retained for minimum 2 years.\n3. User can download their data as CSV.",
     "Create SensorReading model in SQLite. Auto-insert on every MQTT message. Implement CSV export endpoint.",
     "Write latency < 50 ms. Storage footprint < 1 MB per farm per month. Export handles up to 10,000 rows.",
     "3 days", "2 days"),

    (23, "Soil Health Traffic-Light Dashboard",
     "Soil Health Dashboard", "Sprint 3",
     "As a farmer, I want a simple visual dashboard showing whether each nutrient is in the healthy range so that I can immediately understand my soil status.",
     "Must", "Pending",
     "1. Dashboard shows N, P, K, pH, moisture each with Red/Amber/Green indicator.\n2. Thresholds based on crop-specific optimal ranges.\n3. Dashboard refreshes every 60 s.",
     "Build React dashboard component. Define threshold constants per crop. Map sensor values to RAG status. Implement auto-refresh.",
     "Dashboard loads < 2 s. Threshold data peer-reviewed by agricultural officer. Accessible to colour-blind users (icons supplement colour).",
     "4 days", "-"),

    (24, "Fertiliser Dose Recommendation",
     "Soil Health Dashboard", "Sprint 3",
     "As a farmer, I want the system to recommend how much fertiliser to apply based on my soil deficiency so that I don't over- or under-fertilise.",
     "Should", "Backlog",
     "1. Recommendation shows fertiliser type, quantity per acre, and timing.\n2. Based on deficiency relative to crop-specific optimal NPK.\n3. Cost estimate in INR included.",
     "Implement deficiency calculation (optimal − measured). Map to fertiliser product (Urea for N, DAP for P, MOP for K). Calculate dose per acre using standard ICAR dosage tables.",
     "Fertiliser recommendations validated against ICAR crop nutrition guidelines. Cost data updated monthly from market prices. No recommendation if sensor data is stale > 24 h.",
     "4 days", "-"),

    # ── EPIC 8: WEB APPLICATION & PWA ────────────────────────────────────────
    (25, "React Frontend — Core Dashboard",
     "Web Application & PWA", "Sprint 2",
     "As a farmer, I want a clean, mobile-friendly web dashboard showing all my sensor readings and recommendations in one place.",
     "Must", "In Progress",
     "1. Dashboard shows live NPK, pH, moisture, temp readings.\n2. Crop recommendation card visible on homepage.\n3. Responsive on mobile (375px–1440px width).",
     "Build React app with component: SensorCard, RecommendationCard, LanguageToggle, NavBar. Use CSS Grid for responsive layout.",
     "Lighthouse mobile score > 80. First Contentful Paint < 2 s on 3G. No horizontal scroll on 375px viewport.",
     "8 days", "5 days"),

    (26, "Progressive Web App (PWA) — Offline Support",
     "Web Application & PWA", "Sprint 4",
     "As a farmer in a low-connectivity area, I want the app to work offline so that I can still view my last recommendations without internet.",
     "Should", "Backlog",
     "1. App installable on Android home screen.\n2. Last recommendation and soil readings accessible offline.\n3. Data syncs automatically when connection restores.",
     "Configure Service Worker with Workbox. Cache static assets and last API response. Implement background sync for pending submissions.",
     "Offline mode functional for core features. Cache size < 10 MB. Sync completes within 30 s of reconnection.",
     "5 days", "-"),

    (27, "User Authentication & Farm Profile",
     "Web Application & PWA", "Sprint 2",
     "As a farmer, I want to create a profile with my farm location and details so that recommendations are personalised to my region.",
     "Must", "In Progress",
     "1. Farmer can register with mobile number + OTP.\n2. Profile stores name, state, district, land size.\n3. Location used to auto-fetch rainfall and mandi data.",
     "Implement OTP auth via MSG91. Create Farmer model (name, mobile, state, district, acreage, language preference). JWT token authentication.",
     "OTP delivery < 30 s. Session token expires in 7 days. HTTPS enforced. Password/OTP never stored in plain text.",
     "5 days", "4 days"),

    # ── EPIC 9: LORA + ESP32 EXTENSION (ROADMAP) ─────────────────────────────
    (28, "ESP32 Microcontroller Migration",
     "LoRa + ESP32 Extension", "Sprint 5",
     "As a system architect, I want to migrate from Arduino UNO to ESP32 so that we get built-in Wi-Fi, Bluetooth, and higher processing power.",
     "Could", "Backlog",
     "1. All sensor code ported from Arduino to ESP32 (MicroPython or C++).\n2. Built-in Wi-Fi used instead of external ESP8266.\n3. OTA firmware update capability added.",
     "Port sensor interfaces to ESP32 GPIO. Test all 4 sensors on ESP32 WROOM-32. Enable Arduino OTA library. Document pin mapping.",
     "All sensors functional on ESP32 with same accuracy. OTA update completes < 60 s. Power consumption < 250 mA during sensing cycle.",
     "7 days", "-"),

    (29, "LoRa SX1276 Communication Module",
     "LoRa + ESP32 Extension", "Sprint 5",
     "As a farmer in a remote village without 4G, I want my sensor data to reach the cloud via LoRa so that I can use CropXpert without internet.",
     "Won't", "Backlog",
     "1. Sensor data transmitted via LoRa SX1276 at 915 MHz.\n2. Range > 5 km in open field conditions.\n3. LoRaWAN gateway receives data and forwards to backend.",
     "Integrate LoRa SX1276 with ESP32 SPI bus. Implement LoRaWAN OTAA join. Deploy RAK2245 gateway. Configure TTN (The Things Network) application.",
     "Packet delivery rate > 95% at 5 km range. Power consumption < 20 mA in transmit mode. Data payload ≤ 51 bytes (LoRaWAN limit).",
     "10 days", "-"),

    (30, "PM-WANI Backhaul Integration",
     "LoRa + ESP32 Extension", "Sprint 5",
     "As a system, I want to use PM-WANI public Wi-Fi as backhaul for the LoRaWAN gateway so that deployment costs are minimised in rural areas.",
     "Won't", "Backlog",
     "1. Gateway connects to PM-WANI hotspot automatically.\n2. Fallback to mobile data if PM-WANI unavailable.\n3. Connectivity status visible in admin dashboard.",
     "Configure gateway network priority: PM-WANI Wi-Fi → 4G SIM → 3G SIM. Implement connectivity health check. Admin alert on prolonged disconnect.",
     "Gateway reconnects within 60 s of network change. Supports WPA2 for PM-WANI. Tested in field with Jio and Airtel PM-WANI hotspots.",
     "6 days", "-"),
]

# ── Build workbook ────────────────────────────────────────────────────────────
wb = Workbook()
ws = wb.active
ws.title = "Product Backlog"

# ── Row 1 — Project title ─────────────────────────────────────────────────────
ws.merge_cells("A1:L1")
c = ws["A1"]
c.value = "Product Backlog — CropXpert: IoT + ML Precision Agriculture Platform  |  CINTEL, SRMIST Kattankulathur  |  Team: Adnan Nagdiwala & Chandra Bhayal  |  Guide: Dr. R. Siva"
c.font      = Font(name="Arial", bold=True, size=11, color=WHITE)
c.fill      = fill(DARK_BLUE)
c.alignment = align("center", "center")
c.border    = border("medium", DARK_BLUE)
ws.row_dimensions[1].height = 28

# ── Row 2 — Column headers ────────────────────────────────────────────────────
HEADERS = ["ID", "Title", "Epic", "Sprint", "User Story",
           "Priority\n(MoSCoW)", "Status",
           "Acceptance Criteria", "Functional Requirements",
           "Non-Functional Requirements", "Original\nEstimate", "Actual\nEffort"]

HDR_WIDTHS = [5, 22, 24, 10, 38, 10, 13, 38, 34, 34, 10, 10]

for col_idx, (hdr, w) in enumerate(zip(HEADERS, HDR_WIDTHS), start=1):
    c = ws.cell(2, col_idx, hdr)
    c.font      = Font(name="Arial", bold=True, size=10, color=WHITE)
    c.fill      = fill(MID_BLUE)
    c.alignment = align("center", "center")
    c.border    = border("medium", DARK_BLUE)
    ws.column_dimensions[get_column_letter(col_idx)].width = w

ws.row_dimensions[2].height = 30

# ── Epic group colours ────────────────────────────────────────────────────────
EPIC_FILL = {
    "IoT Sensor Module":           "D6E4F7",
    "ML Recommendation Engine":    "E2EFDA",
    "Market Intelligence Layer":   "FCE4D6",
    "Farmer Support Portal":       "FFF2CC",
    "Multilingual Interface":      "EAD1DC",
    "CropBot — WhatsApp & SMS":    "F0E6FF",
    "Soil Health Dashboard":       "D9EAD3",
    "Web Application & PWA":       "D9F0FF",
    "LoRa + ESP32 Extension":      "F2F2F2",
}

# ── Data rows ─────────────────────────────────────────────────────────────────
for row_num, item in enumerate(BACKLOG, start=3):
    (id_, title, epic, sprint, story, priority, status,
     acceptance, functional, nonfunc, estimate, effort) = item

    row_fill_hex = EPIC_FILL.get(epic, "FFFFFF")
    row_data = [id_, title, epic, sprint, story, priority, status,
                acceptance, functional, nonfunc, estimate, effort]

    for col_idx, val in enumerate(row_data, start=1):
        c = ws.cell(row_num, col_idx, val)
        c.border    = border("thin", "BFBFBF")
        c.alignment = align("left" if col_idx > 2 else "center", "top")
        c.font      = font(size=9)

        # Base row fill from epic colour
        c.fill = fill(row_fill_hex)

        # Override specific columns
        if col_idx == 1:  # ID
            c.font = font(bold=True, size=9, color=DARK_BLUE)
            c.alignment = align("center", "center")

        elif col_idx == 4:  # Sprint
            c.alignment = align("center", "top")
            c.font = font(size=9, color=GREY_HDR, italic=True)

        elif col_idx == 6:  # Priority
            bg, fg = PRIORITY_COLOR.get(priority, ("FFFFFF", "000000"))
            c.fill = fill(bg)
            c.font = font(bold=True, size=9, color=fg)
            c.alignment = align("center", "center")

        elif col_idx == 7:  # Status
            bg, fg = STATUS_COLOR.get(status, ("FFFFFF", "000000"))
            c.fill = fill(bg)
            c.font = font(bold=True, size=9, color=fg)
            c.alignment = align("center", "center")

        elif col_idx in (11, 12):  # Estimates
            c.alignment = align("center", "center")
            c.font = font(size=9, color=GREY_HDR)

    ws.row_dimensions[row_num].height = 80

# ── Freeze panes ──────────────────────────────────────────────────────────────
ws.freeze_panes = "E3"

# ── Auto-filter ───────────────────────────────────────────────────────────────
ws.auto_filter.ref = f"A2:L{len(BACKLOG)+2}"

# ── Add a Summary sheet ───────────────────────────────────────────────────────
ws2 = wb.create_sheet("Sprint Summary")

ws2.merge_cells("A1:F1")
c = ws2["A1"]
c.value = "CropXpert — Sprint Summary & Roadmap"
c.font  = Font(name="Arial", bold=True, size=13, color=WHITE)
c.fill  = fill(DARK_BLUE)
c.alignment = align("center", "center")
ws2.row_dimensions[1].height = 28

hdrs2 = ["Sprint", "Epic(s) Covered", "Key Deliverables", "Story Count",
         "Total Estimate", "Status"]
widths2 = [12, 32, 44, 13, 14, 14]
for ci, (h, w) in enumerate(zip(hdrs2, widths2), 1):
    c = ws2.cell(2, ci, h)
    c.font      = Font(name="Arial", bold=True, size=10, color=WHITE)
    c.fill      = fill(MID_BLUE)
    c.alignment = align("center", "center")
    c.border    = border("medium", DARK_BLUE)
    ws2.column_dimensions[get_column_letter(ci)].width = w
ws2.row_dimensions[2].height = 24

SPRINTS = [
    ("Sprint 1\n(Weeks 1–2)", "IoT Sensor Module",
     "NPK + pH + Moisture + DHT22 sensors integrated. Rainfall API live. MQTT streaming to backend.",
     5, "16 days", "Done"),
    ("Sprint 2\n(Weeks 3–4)", "ML Engine + Web App + Soil Logging",
     "RF model trained (99.2%). FastAPI /predict endpoint. React dashboard. SQLite trend logging. User auth/profile.",
     6, "25 days", "In Progress"),
    ("Sprint 3\n(Weeks 5–6)", "Market Layer + Farmer Portal + Soil Dashboard",
     "AGMARKNET MSP integration. Weighted scoring. Govt scheme portal. Fertiliser advisor. Traffic-light dashboard.",
     6, "22 days", "Pending"),
    ("Sprint 4\n(Weeks 7–8)", "Multilingual UI + CropBot + PWA + Farming Campaigns",
     "Hindi/Marathi/Tamil/Telugu UI. WhatsApp + SMS bots. Offline PWA. Profit calculator. Campaign section.",
     7, "35 days", "Backlog"),
    ("Sprint 5\n(Future Release)", "LoRa + ESP32 Extension",
     "ESP32 migration. LoRa SX1276 5–15 km connectivity. PM-WANI backhaul. 1,000-node LoRaWAN gateway.",
     3, "23 days", "Backlog"),
]

SPRINT_COLORS = ["D6E4F7", "E2EFDA", "FFF2CC", "EAD1DC", "F2F2F2"]

for ri, (sprint, epics, deliverables, count, est, status) in enumerate(SPRINTS, 3):
    row_data = [sprint, epics, deliverables, count, est, status]
    bg = SPRINT_COLORS[ri - 3]
    for ci, val in enumerate(row_data, 1):
        c = ws2.cell(ri, ci, val)
        c.fill = fill(bg)
        c.border = border("thin", "BFBFBF")
        c.alignment = align("center" if ci in (1, 4, 5, 6) else "left", "top")
        c.font = font(size=10, bold=(ci == 1))
        if ci == 6:
            bg_s, fg_s = STATUS_COLOR.get(status, ("FFFFFF", "000000"))
            c.fill = fill(bg_s)
            c.font = font(bold=True, size=10, color=fg_s)
    ws2.row_dimensions[ri].height = 55

# ── MoSCoW Summary sheet ──────────────────────────────────────────────────────
ws3 = wb.create_sheet("MoSCoW Summary")
ws3.merge_cells("A1:D1")
c = ws3["A1"]
c.value = "CropXpert — MoSCoW Priority Summary"
c.font  = Font(name="Arial", bold=True, size=13, color=WHITE)
c.fill  = fill(DARK_BLUE)
c.alignment = align("center", "center")
ws3.row_dimensions[1].height = 28

hdrs3 = ["Priority", "Count", "Story IDs", "Description"]
widths3 = [12, 8, 28, 60]
for ci, (h, w) in enumerate(zip(hdrs3, widths3), 1):
    c = ws3.cell(2, ci, h)
    c.font = Font(name="Arial", bold=True, size=10, color=WHITE)
    c.fill = fill(MID_BLUE)
    c.alignment = align("center", "center")
    c.border = border("medium", DARK_BLUE)
    ws3.column_dimensions[get_column_letter(ci)].width = w
ws3.row_dimensions[2].height = 22

MOSCOW_DATA = [
    ("Must",   14, "1–10, 11–12, 14–15, 18, 20, 22–23, 25, 27",
     "Core non-negotiable features: all sensor integrations, ML engine, market layer, multilingual UI, WhatsApp bot, soil dashboard, web app, auth."),
    ("Should", 10, "13, 16–17, 19, 21, 24, 26, 28",
     "Important features that significantly enhance value: mandi trend charts, profit calculator, SMS bot, fertiliser advisor, PWA offline, ESP32 migration."),
    ("Could",  4,  "16, 28, 29",
     "Desirable but not essential: farming campaigns, ESP32 OTA updates, LoRa SX1276 module."),
    ("Won't",  2,  "29, 30",
     "Out of scope for current release: LoRa hardware deployment, PM-WANI backhaul integration (planned for v2.0)."),
]

for ri, (prio, count, ids, desc) in enumerate(MOSCOW_DATA, 3):
    bg, fg = PRIORITY_COLOR.get(prio, ("FFFFFF", "000000"))
    row_data = [prio, count, ids, desc]
    for ci, val in enumerate(row_data, 1):
        c = ws3.cell(ri, ci, val)
        c.fill = fill(bg)
        c.border = border("thin", "BFBFBF")
        c.alignment = align("center" if ci <= 2 else "left", "top")
        c.font = font(bold=(ci == 1), size=10, color=fg if ci == 1 else "000000")
    ws3.row_dimensions[ri].height = 50

wb.save("/home/claude/CropXpert_Product_Backlog.xlsx")
print("Saved.")
