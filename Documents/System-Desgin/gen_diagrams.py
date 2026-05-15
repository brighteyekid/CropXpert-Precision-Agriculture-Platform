import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np
import os

os.makedirs('/home/claude/diagrams', exist_ok=True)

DARK_BLUE  = '#1F3864'
MID_BLUE   = '#2E5FA3'
LIGHT_BLUE = '#D6E4F7'
RED        = '#C00000'
GREEN      = '#1A7A1A'
AMBER      = '#BF8F00'
PALE_GREEN = '#E2EFDA'
PALE_RED   = '#FCE4D6'
PALE_AMB   = '#FFF2CC'
WHITE      = '#FFFFFF'
GREY       = '#595959'
PALE_GREY  = '#F2F2F2'
PALE_PURP  = '#F0E6FF'

def save(fig, name):
    fig.savefig(f'/home/claude/diagrams/{name}.png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'  saved {name}.png')

def box(ax, x, y, w, h, label, sublabel='', bg='#D6E4F7', fc='#1F3864', fs=9, sfs=7, radius=0.04):
    fancy = FancyBboxPatch((x-w/2, y-h/2), w, h,
                           boxstyle=f"round,pad=0.01,rounding_size={radius}",
                           linewidth=1.2, edgecolor=fc, facecolor=bg, zorder=3)
    ax.add_patch(fancy)
    if sublabel:
        ax.text(x, y+0.03, label, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=fc, zorder=4)
        ax.text(x, y-0.07, sublabel, ha='center', va='center', fontsize=sfs,
                color=GREY, zorder=4, style='italic')
    else:
        ax.text(x, y, label, ha='center', va='center', fontsize=fs,
                fontweight='bold', color=fc, zorder=4, multialignment='center')

def arrow(ax, x1, y1, x2, y2, label='', color='#2E5FA3', style='->', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle='arc3,rad=0.0'), zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.02, my+0.02, label, fontsize=6.5, color=color,
                ha='center', va='bottom', style='italic', zorder=5)

def arrow_curved(ax, x1, y1, x2, y2, label='', color='#2E5FA3', rad=0.2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5,
                                connectionstyle=f'arc3,rad={rad}'), zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.06, my, label, fontsize=6.5, color=color,
                ha='center', va='bottom', style='italic', zorder=5)

def title_bar(ax, title):
    ax.text(0.5, 1.02, title, transform=ax.transAxes, ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=DARK_BLUE)
    ax.axhline(y=ax.get_ylim()[1] if hasattr(ax,'get_ylim') else 1,
               color=DARK_BLUE, lw=0.5)

# ══════════════════════════════════════════════════════════════════════════════
# 1. SYSTEM ARCHITECTURE OVERVIEW  (layered)
# ══════════════════════════════════════════════════════════════════════════════
print('Generating diagrams...')
fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13); ax.set_ylim(0, 9)
ax.axis('off')

# Layer bands
layers = [
    (0.1, 1.15, 1.3,  PALE_RED,   'LAYER 1 — IoT Hardware'),
    (0.1, 2.55, 1.3,  PALE_GREEN, 'LAYER 2 — Communication'),
    (0.1, 4.05, 1.4,  PALE_AMB,   'LAYER 3 — Backend & ML'),
    (0.1, 5.55, 1.3,  '#EAD1DC',  'LAYER 4 — Web & API'),
    (0.1, 6.95, 1.3,  PALE_GREY,  'LAYER 5 — Client / Access'),
]
for x, y, h, bg, lbl in layers:
    fancy = FancyBboxPatch((x, y), 12.8, h, boxstyle="round,pad=0.05",
                           linewidth=1, edgecolor='#CCCCCC', facecolor=bg, zorder=1)
    ax.add_patch(fancy)
    ax.text(0.25, y + h/2, lbl, fontsize=7, color=GREY, rotation=0,
            va='center', ha='left', style='italic', zorder=2)

# Layer 1 — IoT Hardware
hw_items = [
    (2.5, 1.75, 'RS485 NPK\nSensor', 'N, P, K mg/kg'),
    (4.3, 1.75, 'Soil pH\nSensor', 'pH 0–14'),
    (6.1, 1.75, 'Capacitive\nMoisture', '0–100%'),
    (7.9, 1.75, 'DHT22\nTemp/Humidity', '°C / %RH'),
    (9.7, 1.75, 'Arduino UNO\n/ ESP32', 'Microcontroller'),
    (11.5, 1.75, 'OpenWeatherMap\nAPI', 'Rainfall mm'),
]
for x, y, lbl, sub in hw_items:
    box(ax, x, y, 1.5, 0.7, lbl, sub, PALE_RED, RED, fs=7.5, sfs=6.5)

# Arrows sensor → MCU
for x in [2.5, 4.3, 6.1, 7.9]:
    arrow(ax, x+0.75, 1.75, 9.7-0.75, 1.75, color=RED, lw=1.2)
arrow(ax, 11.5, 1.4, 9.7+0.75, 1.5, color=GREY, lw=1.2)

# Layer 2 — Communication
box(ax, 3.5, 2.95, 2.2, 0.65, 'MQTT Broker\n(Mosquitto)', 'Port 1883', PALE_GREEN, GREEN, 7.5, 6.5)
box(ax, 6.5, 2.95, 2.2, 0.65, 'HTTP / REST\n(FastAPI)', 'Port 8000', PALE_GREEN, GREEN, 7.5, 6.5)
box(ax, 9.5, 2.95, 2.2, 0.65, 'LoRa SX1276\n(Future v2.0)', '915 MHz, 5–15 km', PALE_GREY, GREY, 7.5, 6.5)

arrow(ax, 9.7, 1.4, 3.5, 2.62, color=GREEN, lw=1.3)
arrow(ax, 9.7, 1.4, 6.5, 2.62, color=GREEN, lw=1.3)

# Layer 3 — Backend & ML
box(ax, 2.3, 4.75, 2.0, 0.7, 'Random Forest\nClassifier', '99.2% acc, 22 crops', PALE_AMB, AMBER, 7.5, 6.5)
box(ax, 4.6, 4.75, 2.0, 0.7, 'AGMARKNET\nMSP Layer', 'Market Scoring', PALE_AMB, AMBER, 7.5, 6.5)
box(ax, 6.9, 4.75, 2.0, 0.7, 'PostgreSQL\n+ SQLite', 'Sensor History DB', PALE_AMB, AMBER, 7.5, 6.5)
box(ax, 9.2, 4.75, 2.0, 0.7, 'OpenWeatherMap\nRainfall Cache', 'TTL 6 hr', PALE_AMB, AMBER, 7.5, 6.5)
box(ax, 11.5, 4.75, 1.4, 0.7, 'AGMARKNET\nCache', 'TTL 24 hr', PALE_AMB, AMBER, 7.5, 6.5)

for x_src in [3.5, 6.5]:
    arrow(ax, x_src, 2.62, 5.5, 4.4, color=AMBER, lw=1.2)

# Layer 4 — Web & API
box(ax, 2.8, 6.2, 2.0, 0.65, 'FastAPI\nREST API', '/predict /schemes', '#EAD1DC', '#7B0099', 7.5, 6.5)
box(ax, 5.3, 6.2, 2.0, 0.65, 'React.js PWA\nFrontend', 'Mobile + Desktop', '#EAD1DC', '#7B0099', 7.5, 6.5)
box(ax, 7.8, 6.2, 2.0, 0.65, 'i18n Layer\n(React-i18next)', 'Hi/Mr/Ta/Te', '#EAD1DC', '#7B0099', 7.5, 6.5)
box(ax, 10.3, 6.2, 2.0, 0.65, 'Twilio Bot\nWhatsApp+SMS', 'CropBot', '#EAD1DC', '#7B0099', 7.5, 6.5)

for bx in [2.3, 4.6, 6.9]:
    arrow(ax, bx, 4.4, 4.05, 5.87, color='#7B0099', lw=1.1)

# Layer 5 — Client
box(ax, 2.5, 7.6, 1.8, 0.6, 'Farmer\nSmartphone', 'Web Browser', PALE_GREY, GREY, 7.5, 6.5)
box(ax, 4.8, 7.6, 1.8, 0.6, 'Farmer Desktop\n/ Kiosk', 'Web Browser', PALE_GREY, GREY, 7.5, 6.5)
box(ax, 7.1, 7.6, 1.8, 0.6, 'WhatsApp\nClient', 'Any Smartphone', PALE_GREY, GREY, 7.5, 6.5)
box(ax, 9.4, 7.6, 1.8, 0.6, 'Basic Phone\n(SMS)', 'Keypad Only', PALE_GREY, GREY, 7.5, 6.5)
box(ax, 11.5, 7.6, 1.2, 0.6, 'KVK Officer\nPortal', 'Admin', PALE_GREY, GREY, 7, 6.5)

for bx in [2.5, 4.8]:
    arrow(ax, 5.3, 5.87, bx+0.1, 7.3, color=GREY, lw=1.0)
arrow(ax, 10.3, 5.87, 7.8, 7.3, color=GREY, lw=1.0)
arrow(ax, 10.3, 5.87, 9.4+0.2, 7.3, color=GREY, lw=1.0)

ax.text(6.5, 8.75, 'CropXpert — System Architecture Overview', fontsize=13,
        fontweight='bold', color=DARK_BLUE, ha='center', va='center')
ax.text(6.5, 8.4, 'CINTEL, SRMIST Kattankulathur  |  Guide: Dr. R. Siva  |  Adnan Nagdiwala & Chandra Bhayal',
        fontsize=8, color=GREY, ha='center', va='center', style='italic')

save(fig, '01_system_overview')

# ══════════════════════════════════════════════════════════════════════════════
# 2. USE CASE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13); ax.set_ylim(0, 9)
ax.axis('off')
ax.set_facecolor('#FAFAFA')

ax.text(6.5, 8.6, 'CropXpert — Use Case Diagram', fontsize=13, fontweight='bold',
        color=DARK_BLUE, ha='center')
ax.text(6.5, 8.25, 'Actors: Farmer · Admin · IoT Sensor System · External APIs',
        fontsize=8, color=GREY, ha='center', style='italic')

# System boundary
sys_box = FancyBboxPatch((2.5, 0.4), 8.0, 7.5, boxstyle="round,pad=0.1",
                         linewidth=2, edgecolor=DARK_BLUE, facecolor='#F7FAFF', zorder=1)
ax.add_patch(sys_box)
ax.text(6.5, 7.75, '« CropXpert System »', fontsize=9, color=DARK_BLUE,
        ha='center', fontweight='bold', zorder=2)

# Use cases (ellipses)
use_cases = [
    (6.5, 7.1,  'Register / Login\n(OTP-based)'),
    (4.5, 6.3,  'View Real-Time\nSensor Readings'),
    (8.5, 6.3,  'Get Crop\nRecommendation'),
    (4.5, 5.3,  'View Soil Health\nDashboard'),
    (8.5, 5.3,  'View Market\nPrices (MSP)'),
    (4.5, 4.3,  'Access Govt\nSchemes Portal'),
    (8.5, 4.3,  'Use WhatsApp\n/ SMS Bot'),
    (4.5, 3.3,  'View Loan\nGuidance'),
    (8.5, 3.3,  'Calculate Farm\nProfit'),
    (4.5, 2.3,  'Download Soil\nHistory (CSV)'),
    (8.5, 2.3,  'Switch Language\n(Hi/Mr/Ta/Te)'),
    (6.5, 1.4,  'Admin: Manage\nSchemes & Content'),
]
for x, y, lbl in use_cases:
    ellipse = mpatches.Ellipse((x, y), 2.8, 0.72, linewidth=1.3,
                               edgecolor=MID_BLUE, facecolor=LIGHT_BLUE, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, lbl, ha='center', va='center', fontsize=7.2,
            color=DARK_BLUE, fontweight='bold', zorder=4, multialignment='center')

# Actors
def actor(ax, x, y, name, color=DARK_BLUE):
    ax.plot(x, y+0.35, 'o', markersize=14, color=color, zorder=5)
    ax.plot([x, x], [y+0.22, y-0.12], color=color, lw=2, zorder=5)
    ax.plot([x-0.22, x+0.22], [y+0.05, y+0.05], color=color, lw=2, zorder=5)
    ax.plot([x-0.18, x], [y-0.12, y-0.35], color=color, lw=2, zorder=5)
    ax.plot([x, x+0.18], [y-0.35, y-0.12], color=color, lw=2, zorder=5)
    ax.text(x, y-0.55, name, ha='center', va='top', fontsize=8,
            fontweight='bold', color=color, zorder=5)

actor(ax, 1.1, 5.0,  'Farmer',         DARK_BLUE)
actor(ax, 1.1, 2.3,  'Admin',          RED)
actor(ax, 11.9, 6.3, 'IoT Sensor\nSystem', GREEN)
actor(ax, 11.9, 4.3, 'External APIs\n(AGMARKNET\nOpenWeather)', AMBER)

# Association lines
farmer_cases = [7.1, 6.3, 5.3, 4.3, 3.3, 2.3]
for y in farmer_cases:
    ax.plot([1.5, 2.5+0.1], [5.0+0.2*(y-5.0)/1.0, y], color=DARK_BLUE,
            lw=0.9, zorder=2, alpha=0.6)
# simpler: just draw lines from actor to left edge of use cases
for x_uc, y_uc, _ in use_cases:
    if x_uc <= 5.5 and y_uc >= 2.0 and y_uc <= 6.5:
        ax.plot([1.5, x_uc - 1.4], [4.8, y_uc], color=DARK_BLUE, lw=0.7, alpha=0.5)
for x_uc, y_uc, _ in use_cases:
    if x_uc >= 8.0 and y_uc >= 5.5:
        ax.plot([11.5, x_uc + 1.4], [6.0, y_uc], color=GREEN, lw=0.7, alpha=0.5)
for x_uc, y_uc, _ in use_cases:
    if x_uc >= 8.0 and 3.0 <= y_uc <= 5.0:
        ax.plot([11.5, x_uc + 1.4], [4.1, y_uc], color=AMBER, lw=0.7, alpha=0.5)
ax.plot([1.5, 6.5 - 1.4], [2.1, 1.4], color=RED, lw=0.7, alpha=0.5)

# include arrows
arrow_curved(ax, 6.5, 6.74, 8.5, 6.66, '«include»', MID_BLUE, 0.1)
arrow_curved(ax, 8.5, 5.94, 8.5, 5.66, '«include»', AMBER, 0.2)

save(fig, '02_use_case')

# ══════════════════════════════════════════════════════════════════════════════
# 3. DFD — LEVEL 0 (Context Diagram)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 7))
ax.set_xlim(0, 11); ax.set_ylim(0, 7)
ax.axis('off')
ax.text(5.5, 6.6, 'CropXpert — DFD Level 0 (Context Diagram)', fontsize=12,
        fontweight='bold', color=DARK_BLUE, ha='center')

# Central system
circle = plt.Circle((5.5, 3.4), 1.3, color=LIGHT_BLUE, ec=DARK_BLUE, lw=2, zorder=3)
ax.add_patch(circle)
ax.text(5.5, 3.5, 'CropXpert', ha='center', va='center', fontsize=11,
        fontweight='bold', color=DARK_BLUE, zorder=4)
ax.text(5.5, 3.1, 'System', ha='center', va='center', fontsize=9,
        color=MID_BLUE, zorder=4)

# External entities
entities = [
    (1.2, 5.8, 'Farmer\n(Primary User)', PALE_RED, RED),
    (1.2, 2.0, 'IoT Sensor\nModule', PALE_GREEN, GREEN),
    (9.8, 5.8, 'AGMARKNET\nGovt API', PALE_AMB, AMBER),
    (9.8, 2.0, 'OpenWeatherMap\nAPI', '#EAD1DC', '#7B0099'),
    (5.5, 0.7, 'Twilio / MSG91\n(WhatsApp + SMS)', PALE_GREY, GREY),
]
for x, y, lbl, bg, fc in entities:
    box(ax, x, y, 2.0, 0.8, lbl, bg=bg, fc=fc, fs=8)

# Data flows
flows = [
    (1.2, 5.4, 4.2, 4.4, 'Crop query / Location', DARK_BLUE),
    (4.2, 3.8, 1.2, 5.1, 'Recommendations + MSP\n+ Schemes + Loans', DARK_BLUE),
    (1.2, 1.6, 4.3, 2.5, 'N, P, K, pH, Moisture,\nTemperature', GREEN),
    (9.8, 5.4, 6.8, 4.4, 'MSP + Mandi Prices', AMBER),
    (9.8, 2.4, 6.7, 3.2, 'Rainfall Data (mm)', '#7B0099'),
    (5.5, 2.1, 5.5, 1.15, 'Crop Recommendation\n(SMS reply)', GREY),
    (5.5, 1.15, 5.5, 2.1, 'Farmer SMS / WA\nQuery', GREY),
]
for x1, y1, x2, y2, lbl, col in flows:
    arrow(ax, x1, y1, x2, y2, lbl, col)

save(fig, '03_dfd_level0')

# ══════════════════════════════════════════════════════════════════════════════
# 4. DFD — LEVEL 1
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14); ax.set_ylim(0, 10)
ax.axis('off')
ax.text(7.0, 9.6, 'CropXpert — DFD Level 1', fontsize=12,
        fontweight='bold', color=DARK_BLUE, ha='center')

# Processes (rounded boxes)
procs = [
    (3.0, 8.2, 'P1\nSensor Data\nAcquisition', PALE_GREEN, GREEN),
    (7.0, 8.2, 'P2\nRainfall Data\nFetch', PALE_GREEN, GREEN),
    (11.0, 8.2, 'P3\nUser\nAuthentication', PALE_RED, RED),
    (3.0, 5.8, 'P4\nML Crop\nRecommendation', PALE_AMB, AMBER),
    (7.0, 5.8, 'P5\nMarket Score\nCalculation', '#EAD1DC', '#7B0099'),
    (11.0, 5.8, 'P6\nMultilingual\nOutput', LIGHT_BLUE, MID_BLUE),
    (3.0, 3.2, 'P7\nGovt Scheme\n& Loan Lookup', PALE_AMB, AMBER),
    (7.0, 3.2, 'P8\nSoil Health\nTrend Logging', PALE_GREEN, GREEN),
    (11.0, 3.2, 'P9\nCropBot\nWhatsApp/SMS', '#F0E6FF', '#5B0099'),
]
for x, y, lbl, bg, fc in procs:
    ellipse = mpatches.Ellipse((x, y), 2.4, 1.0, linewidth=1.5,
                               edgecolor=fc, facecolor=bg, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, lbl, ha='center', va='center', fontsize=7,
            color=fc, fontweight='bold', zorder=4, multialignment='center')

# Data stores (open rectangles)
stores = [
    (7.0, 7.0, 'D1: Sensor Reading DB (SQLite)'),
    (3.5, 1.5, 'D2: Crop Dataset + RF Model'),
    (10.5, 1.5, 'D3: Scheme/Loan DB'),
    (7.0, 1.5, 'D4: AGMARKNET Cache'),
]
for x, y, lbl in stores:
    ax.plot([x-2.0, x+2.0], [y+0.2, y+0.2], color=DARK_BLUE, lw=1.5)
    ax.plot([x-2.0, x+2.0], [y-0.2, y-0.2], color=DARK_BLUE, lw=1.5)
    ax.text(x, y, lbl, ha='center', va='center', fontsize=7.5,
            color=DARK_BLUE, fontweight='bold')

# External entities
ext = [
    (0.9, 8.2, 'IoT\nSensors', PALE_GREEN, GREEN),
    (13.1, 8.2, 'Farmer', PALE_RED, RED),
    (0.9, 5.8, 'AGMARKNET\nAPI', PALE_AMB, AMBER),
    (13.1, 5.8, 'OpenWeather\nAPI', '#EAD1DC', '#7B0099'),
    (0.9, 3.2, 'Twilio/MSG91', PALE_GREY, GREY),
    (13.1, 3.2, 'MyScheme\n.gov.in', PALE_GREY, GREY),
]
for x, y, lbl, bg, fc in ext:
    box(ax, x, y, 1.6, 0.65, lbl, bg=bg, fc=fc, fs=7)

# Flow arrows (key ones)
flow_arrows = [
    (1.7, 8.2, 2.1, 8.2, 'Sensor Data'),
    (3.0, 7.7, 3.0, 6.3, 'Parsed Values'),
    (3.0, 5.3, 3.0, 4.3, '7-Feature Vector'),
    (4.2, 5.8, 5.8, 5.8, 'ML Prediction'),
    (8.2, 5.8, 9.8, 5.8, 'Ranked Output'),
    (6.0, 5.3, 7.0, 5.5, 'MSP Score'),
    (7.0, 7.7, 7.0, 7.2, 'Stored'),
    (7.0, 4.5, 7.0, 3.65, 'MSP Data'),
    (11.0, 5.3, 11.0, 3.65, 'Bot Reply'),
    (1.7, 3.2, 2.1, 3.2, 'Query'),
    (12.3, 3.2, 11.9, 3.2, 'Schemes'),
    (12.3, 5.8, 12.3, 5.8),
]
for fa in flow_arrows:
    if len(fa) == 5:
        arrow(ax, fa[0], fa[1], fa[2], fa[3], fa[4], MID_BLUE)
    elif len(fa) == 4:
        arrow(ax, fa[0], fa[1], fa[2], fa[3], '', GREY)

arrow(ax, 7.8, 8.2, 12.2, 8.2, 'OTP Auth', DARK_BLUE)
arrow(ax, 1.7, 5.8, 2.1, 5.8, 'Mkt Prices', AMBER)
arrow(ax, 12.3, 5.8, 11.9, 5.8, 'Rain mm', '#7B0099')

save(fig, '04_dfd_level1')

# ══════════════════════════════════════════════════════════════════════════════
# 5. COMPONENT DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 9))
ax.set_xlim(0, 13); ax.set_ylim(0, 9)
ax.axis('off')
ax.text(6.5, 8.65, 'CropXpert — Component Diagram', fontsize=12,
        fontweight='bold', color=DARK_BLUE, ha='center')

def comp_box(ax, x, y, w, h, title, items, bg, fc):
    fancy = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                           linewidth=2, edgecolor=fc, facecolor=bg, zorder=3)
    ax.add_patch(fancy)
    # component icon (top-right)
    ix, iy = x + w - 0.25, y + h - 0.08
    ax.plot([ix-0.15, ix+0.05], [iy, iy], color=fc, lw=1.5, zorder=5)
    ax.plot([ix-0.15, ix+0.05], [iy-0.12, iy-0.12], color=fc, lw=1.5, zorder=5)
    ax.plot([ix-0.25, ix-0.15], [iy+0.04, iy+0.04], color=fc, lw=1.5, zorder=5)
    ax.plot([ix-0.25, ix-0.15], [iy-0.04, iy-0.04], color=fc, lw=1.5, zorder=5)
    ax.plot([ix-0.25, ix-0.15], [iy-0.12-0.04, iy-0.12-0.04], color=fc, lw=1.5, zorder=5)
    ax.plot([ix-0.25, ix-0.15], [iy-0.12+0.04, iy-0.12+0.04], color=fc, lw=1.5, zorder=5)
    ax.text(x + w/2, y + h - 0.18, f'«component» {title}', ha='center',
            va='top', fontsize=8, fontweight='bold', color=fc, zorder=4)
    ax.axhline(y=y + h - 0.32, xmin=(x)/13, xmax=(x+w)/13, color=fc, lw=0.8, alpha=0.5)
    for i, item in enumerate(items):
        ax.text(x + 0.2, y + h - 0.48 - i * 0.22, f'  {item}', ha='left',
                va='top', fontsize=6.8, color='#333333', zorder=4)

comp_box(ax, 0.2, 6.4, 3.8, 2.1, 'IoT Hardware Layer',
         ['+RS485NPKSensor  +pHSensor', '+MoistureSensor  +DHT22',
          '+ArduinoUNO  +ESP32_WiFi', '+MAX485_Converter'],
         PALE_RED, RED)

comp_box(ax, 4.5, 6.4, 4.0, 2.1, 'Communication Layer',
         ['+MQTTBroker (Mosquitto:1883)', '+HTTPClient (FastAPI:8000)',
          '+LoRaGateway (v2.0 roadmap)', '+OpenWeatherMap_Client'],
         PALE_GREEN, GREEN)

comp_box(ax, 9.0, 6.4, 3.8, 2.1, 'ML Engine',
         ['+RandomForestClassifier (22 crops)', '+StandardScaler (serialised)',
          '+FeatureVector (N,P,K,pH,M,T,R)', '+ConfidenceScorer (top-3)'],
         PALE_AMB, AMBER)

comp_box(ax, 0.2, 3.8, 3.8, 2.2, 'Market Intelligence',
         ['+AGMARKNETClient', '+MSP_IndexCalculator',
          '+WeightedScorer (α=0.60,β=0.25,γ=0.15)', '+PriceTrendCache (TTL 24h)'],
         '#FCE4D6', RED)

comp_box(ax, 4.5, 3.8, 4.0, 2.2, 'Backend Services',
         ['+FastAPI_App  +JWTAuthMiddleware', '+SensorReadingService',
          '+SchemeService  +LoanService', '+SQLite_DB  +PostgreSQL_DB'],
         LIGHT_BLUE, MID_BLUE)

comp_box(ax, 9.0, 3.8, 3.8, 2.2, 'CropBot',
         ['+TwilioWhatsAppWebhook', '+SMSShortcodeParser',
          '+NLP_InputParser (Hi/En)', '+ResponseFormatter'],
         PALE_PURP, '#5B0099')

comp_box(ax, 0.2, 1.2, 3.8, 2.2, 'Frontend (React PWA)',
         ['+SensorDashboard  +RecommendationCard', '+SoilHealthChart (Chart.js)',
          '+SchemePortal  +LoanAdvisor', '+ProfitCalculator  +LanguageToggle'],
         '#EAD1DC', '#7B0099')

comp_box(ax, 4.5, 1.2, 4.0, 2.2, 'i18n Layer',
         ['+ReactI18next  +TranslationJSON', '+Locale: hi / mr / ta / te',
          '+CropNameDictionary', '+AdvisoryTextLocaliser'],
         PALE_GREEN, GREEN)

comp_box(ax, 9.0, 1.2, 3.8, 2.2, 'External APIs',
         ['+AGMARKNET_REST  +eNAM_API', '+OpenWeatherMap_OneCall',
          '+MyScheme_Gov  +MSG91_SMS', '+Twilio_WA  +OTP_Service'],
         PALE_GREY, GREY)

# Connection arrows between components
conn = [
    (4.0, 7.5, 4.5, 7.5), (8.5, 7.5, 9.0, 7.5),
    (4.0, 4.9, 4.5, 4.9), (8.5, 4.9, 9.0, 4.9),
    (4.0, 2.3, 4.5, 2.3), (8.5, 2.3, 9.0, 2.3),
    (2.1, 6.4, 2.1, 6.0), (6.5, 6.4, 6.5, 6.0),
    (2.1, 3.8, 2.1, 3.4), (6.5, 3.8, 6.5, 3.4),
]
for x1, y1, x2, y2 in conn:
    arrow(ax, x1, y1, x2, y2, color=DARK_BLUE, lw=1.3)

save(fig, '05_component')

# ══════════════════════════════════════════════════════════════════════════════
# 6. SEQUENCE DIAGRAM — Crop Recommendation Flow
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14); ax.set_ylim(0, 10.2)
ax.axis('off')
ax.text(7.0, 9.9, 'CropXpert — Sequence Diagram: Crop Recommendation Flow',
        fontsize=11, fontweight='bold', color=DARK_BLUE, ha='center')

lifelines = [
    (1.2,  'Farmer\n(Browser)', PALE_RED, RED),
    (3.2,  'React\nFrontend', '#EAD1DC', '#7B0099'),
    (5.2,  'FastAPI\nBackend', PALE_AMB, AMBER),
    (7.2,  'MQTT\nBroker', PALE_GREEN, GREEN),
    (9.2,  'ML Engine\n(RF Model)', PALE_AMB, AMBER),
    (11.2, 'AGMARKNET\nAPI', PALE_RED, RED),
    (13.0, 'SQLite\nDB', LIGHT_BLUE, MID_BLUE),
]
TOP = 9.3
for x, lbl, bg, fc in lifelines:
    box(ax, x, TOP, 1.6, 0.55, lbl, bg=bg, fc=fc, fs=7.5, radius=0.03)
    ax.plot([x, x], [TOP - 0.28, 0.3], color=fc, lw=1, linestyle='--', zorder=1, alpha=0.5)

# Sequence steps
steps = [
    # (from_x, to_x, y, label, color, return=False)
    (1.2, 3.2, 8.6,  'Open Dashboard',                      DARK_BLUE, False),
    (3.2, 5.2, 8.1,  'GET /live-readings',                   MID_BLUE,  False),
    (5.2, 7.2, 7.6,  'Subscribe MQTT topic',                 GREEN,     False),
    (7.2, 5.2, 7.1,  'Sensor data (N,P,K,pH,M,T)',           GREEN,     True),
    (5.2, 13.0, 6.6, 'INSERT sensor_reading',                MID_BLUE,  False),
    (5.2, 3.2, 6.1,  'Return live JSON',                     MID_BLUE,  True),
    (3.2, 1.2, 5.6,  'Display live readings',                '#7B0099', True),
    (1.2, 3.2, 5.1,  'Click "Get Recommendation"',           DARK_BLUE, False),
    (3.2, 5.2, 4.6,  'POST /predict {N,P,K,pH,M,T,R}',      MID_BLUE,  False),
    (5.2, 9.2, 4.1,  'predict_proba(feature_vector)',        AMBER,     False),
    (9.2, 5.2, 3.6,  'top-3 crops + confidence[]',          AMBER,     True),
    (5.2, 11.2, 3.1, 'GET /msp?crops=[rice,jute,coconut]',  RED,       False),
    (11.2, 5.2, 2.6, 'MSP prices + market data',            RED,       True),
    (5.2, 5.2, 2.1,  'weighted_score(ml_prob, msp_idx)',     AMBER,     False),
    (5.2, 3.2, 1.6,  'JSON: ranked top-3 + prices + tips',  MID_BLUE,  True),
    (3.2, 1.2, 1.1,  'Render Recommendation Card',          '#7B0099', True),
]

for i, (x1, x2, y, lbl, col, ret) in enumerate(steps):
    style = '<-' if ret else '->'
    ls = '--' if ret else '-'
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle=style, color=col, lw=1.5,
                                linestyle=ls, connectionstyle='arc3,rad=0.0'))
    mx = (x1 + x2) / 2
    offset = 0.08 if not ret else -0.08
    ax.text(mx, y + offset, lbl, ha='center', va='center', fontsize=6.8,
            color=col, style='italic' if ret else 'normal',
            bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

    # Activation boxes
    if not ret:
        box_h = 0.3
        for bx in [x1, x2]:
            rect = FancyBboxPatch((bx - 0.1, y - 0.05), 0.2, box_h,
                                  boxstyle="square,pad=0.01",
                                  linewidth=0.8, edgecolor=col, facecolor=col, alpha=0.25)
            ax.add_patch(rect)

# self-call note
ax.text(5.5, 2.1, 'self', ha='left', va='center', fontsize=7, color=AMBER, style='italic')

ax.text(7.0, 0.15, 'Note: Entire flow completes in < 500 ms end-to-end  |  RF inference: ~2.3 ms',
        ha='center', fontsize=8, color=GREY, style='italic')

save(fig, '06_sequence')

# ══════════════════════════════════════════════════════════════════════════════
# 7. DEPLOYMENT DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 13); ax.set_ylim(0, 8.5)
ax.axis('off')
ax.text(6.5, 8.15, 'CropXpert — Deployment Diagram', fontsize=12,
        fontweight='bold', color=DARK_BLUE, ha='center')

def node(ax, x, y, w, h, title, items, bg, fc):
    # node box with dog-ear
    fancy = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                           linewidth=2, edgecolor=fc, facecolor=bg, zorder=3)
    ax.add_patch(fancy)
    ax.text(x + w/2, y + h - 0.15, f'«node» {title}', ha='center',
            fontsize=8.5, fontweight='bold', color=fc, zorder=4)
    ax.axhline(y=y + h - 0.32, xmin=(x+0.1)/13, xmax=(x+w-0.1)/13,
               color=fc, lw=0.8, alpha=0.4)
    for i, item in enumerate(items):
        ax.text(x + 0.18, y + h - 0.5 - i * 0.22, item, ha='left',
                va='top', fontsize=7, color='#222222', zorder=4)

node(ax, 0.2, 5.5, 3.5, 2.3, 'Field Sensor Unit',
     ['Arduino UNO (ATmega328P)',
      'RS485 NPK + pH + Moisture',
      'DHT22 Temp/Humidity',
      'ESP8266 Wi-Fi Module',
      'Power: 5V USB / Solar'],
     PALE_RED, RED)

node(ax, 0.2, 2.5, 3.5, 2.6, 'LoRa Gateway (v2.0)',
     ['ESP32 WROOM-32',
      'LoRa SX1276 (915 MHz)',
      'RAK2245 LoRaWAN Hat',
      'Backhaul: 4G SIM / PM-WANI',
      'Coverage: 5–15 km radius'],
     PALE_GREY, GREY)

node(ax, 4.2, 5.5, 4.2, 2.3, 'Cloud Server (Railway.app / AWS)',
     ['FastAPI App (Python 3.10)',
      'RF Model + StandardScaler (joblib)',
      'Mosquitto MQTT Broker :1883',
      'PostgreSQL + SQLite',
      'Docker Container'],
     PALE_AMB, AMBER)

node(ax, 4.2, 2.5, 4.2, 2.6, 'External Services',
     ['AGMARKNET REST API',
      'OpenWeatherMap OneCall API',
      'MyScheme.gov.in API',
      'Twilio (WhatsApp + SMS)',
      'MSG91 (SMS fallback)'],
     PALE_GREEN, GREEN)

node(ax, 9.0, 5.5, 3.8, 2.3, 'Farmer Device',
     ['Any Android/iOS Smartphone',
      'Chrome / Firefox Browser',
      'React PWA (installable)',
      'Min: 2G connection',
      'Offline: Service Worker'],
     '#EAD1DC', '#7B0099')

node(ax, 9.0, 2.5, 3.8, 2.6, 'Basic Phone (SMS)',
     ['Any GSM Keypad Phone',
      'SMS to shortcode',
      'Format: CROP N90 P42...',
      'Networks: Jio/Airtel/BSNL',
      'Zero data plan needed'],
     PALE_GREY, GREY)

# Network links
links = [
    (3.7, 6.6, 4.2, 6.6, 'MQTT / HTTP\n(Wi-Fi)', GREEN),
    (3.7, 3.8, 4.2, 3.8, 'LoRaWAN\n→ backhaul', GREY),
    (8.4, 6.6, 9.0, 6.6, 'HTTPS :443\n(REST API)', MID_BLUE),
    (8.4, 3.8, 9.0, 3.8, 'SMS API\n(Twilio)', '#5B0099'),
    (6.3, 5.5, 6.3, 5.1, 'HTTPS', MID_BLUE),
    (1.95, 5.5, 1.95, 5.1, '', GREY),
]
for l in links:
    x1, y1, x2, y2 = l[0], l[1], l[2], l[3]
    lbl = l[4] if len(l) > 4 else ''
    col = l[5] if len(l) > 5 else DARK_BLUE
    arrow(ax, x1, y1, x2, y2, lbl, col)

ax.text(6.5, 0.25, 'All cloud communication over HTTPS (TLS 1.3)  |  JWT authentication  |  BCrypt password hashing',
        ha='center', fontsize=8, color=GREY, style='italic')

save(fig, '07_deployment')

# ══════════════════════════════════════════════════════════════════════════════
# 8. CLASS DIAGRAM (simplified key classes)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14); ax.set_ylim(0, 10)
ax.axis('off')
ax.text(7.0, 9.7, 'CropXpert — Class Diagram (Key Domain Classes)',
        fontsize=12, fontweight='bold', color=DARK_BLUE, ha='center')

def class_box(ax, x, y, w, name, attrs, methods, bg, fc):
    # Calculate height
    n_attrs = len(attrs)
    n_meth  = len(methods)
    h_name  = 0.4
    h_attr  = max(0.2, n_attrs * 0.22 + 0.1)
    h_meth  = max(0.2, n_meth  * 0.22 + 0.1)
    h_total = h_name + h_attr + h_meth

    fancy = FancyBboxPatch((x - w/2, y - h_total), w, h_total,
                           boxstyle="square,pad=0.02",
                           linewidth=1.5, edgecolor=fc, facecolor=bg, zorder=3)
    ax.add_patch(fancy)
    # name section
    ax.add_patch(FancyBboxPatch((x-w/2, y-h_name), w, h_name,
                                boxstyle="square,pad=0.0",
                                linewidth=0, edgecolor='none', facecolor=fc, zorder=4))
    ax.text(x, y - h_name/2, name, ha='center', va='center', fontsize=8,
            fontweight='bold', color=WHITE, zorder=5)
    # attrs
    div1_y = y - h_name
    ax.plot([x-w/2, x+w/2], [div1_y, div1_y], color=fc, lw=0.8, zorder=4)
    for i, a in enumerate(attrs):
        ax.text(x - w/2 + 0.08, div1_y - 0.05 - i*0.22, a, ha='left', va='top',
                fontsize=6.5, color='#222222', zorder=4)
    # methods
    div2_y = div1_y - h_attr
    ax.plot([x-w/2, x+w/2], [div2_y, div2_y], color=fc, lw=0.8, zorder=4)
    for i, m in enumerate(methods):
        ax.text(x - w/2 + 0.08, div2_y - 0.05 - i*0.22, m, ha='left', va='top',
                fontsize=6.5, color='#222222', zorder=4)
    return h_total

classes = [
    # (cx, cy, w, name, attrs, methods, bg, fc)
    (2.0, 9.5, 3.2, 'Farmer',
     ['- farmer_id: int', '- mobile: str', '- name: str',
      '- state: str', '- district: str', '- acreage: float', '- lang_pref: str'],
     ['+register(mobile, otp): bool', '+login(mobile, otp): Token',
      '+getProfile(): FarmerDTO', '+updateProfile(dto): bool'],
     PALE_RED, RED),
    (6.5, 9.5, 3.4, 'SensorReading',
     ['- reading_id: int', '- farmer_id: int',
      '- timestamp: datetime', '- nitrogen: float',
      '- phosphorus: float', '- potassium: float',
      '- ph: float', '- moisture: float', '- temperature: float'],
     ['+save(): bool', '+getHistory(farmer_id, days): List',
      '+exportCSV(farmer_id): File', '+getLatest(farmer_id): SensorReading'],
     PALE_GREEN, GREEN),
    (11.2, 9.5, 3.0, 'CropRecommendation',
     ['- rec_id: int', '- farmer_id: int',
      '- reading_id: int', '- timestamp: datetime',
      '- top_crops: List[str]', '- confidence: List[float]',
      '- ml_scores: List[float]', '- market_scores: List[float]'],
     ['+generate(reading: SensorReading): self',
      '+getMarketAdjusted(): List',
      '+translateOutput(lang): dict'],
     PALE_AMB, AMBER),
    (2.0, 4.8, 3.2, 'GovernmentScheme',
     ['- scheme_id: int', '- name: str',
      '- category: str', '- state: str',
      '- eligibility: str', '- benefit_amount: float',
      '- apply_link: str', '- last_updated: date'],
     ['+getByState(state): List',
      '+getByCategory(cat): List',
      '+checkEligibility(farmer): bool',
      '+update(data): bool'],
     PALE_AMB, AMBER),
    (6.5, 4.8, 3.4, 'MLModel',
     ['- model_path: str', '- scaler_path: str',
      '- n_classes: int = 22', '- crop_labels: List[str]',
      '- feature_names: List[str]'],
     ['+load(): bool',
      '+predict(features: np.array): np.array',
      '+predictProba(features): np.array',
      '+getTopN(proba, n=3): List[tuple]',
      '+validateInput(features): bool'],
     LIGHT_BLUE, MID_BLUE),
    (11.2, 4.8, 3.0, 'MarketScorer',
     ['- alpha: float = 0.60', '- beta:  float = 0.25',
      '- gamma: float = 0.15', '- cache_ttl: int = 86400'],
     ['+fetchMSP(crop: str): float',
      '+computeIndex(msp: float): float',
      '+score(ml_p, msp_idx, season_d): float',
      '+rankCrops(crops, scores): List'],
     PALE_RED, RED),
    (2.0, 1.1, 3.2, 'CropBot',
     ['- twilio_client: TwilioClient',
      '- sms_client: MSG91Client',
      '- lang_detector: LangDetect'],
     ['+handleWhatsApp(msg: str): str',
      '+handleSMS(sms: str): str',
      '+parseInput(text): SensorDTO',
      '+formatReply(rec, lang): str'],
     PALE_PURP, '#5B0099'),
    (6.5, 1.1, 3.4, 'LoanProgram',
     ['- loan_id: int', '- name: str',
      '- provider: str', '- interest_rate: float',
      '- max_amount: float', '- eligibility: str'],
     ['+getAll(): List',
      '+calculateEMI(principal, rate, months): float',
      '+checkEligibility(farmer): bool'],
     PALE_GREEN, GREEN),
    (11.2, 1.1, 3.0, 'FarmerPortal',
     ['- farmer: Farmer', '- language: str',
      '- last_reading: SensorReading'],
     ['+getDashboard(): DashboardDTO',
      '+getRecommendation(): RecDTO',
      '+getSchemes(): List[SchemeDTO]',
      '+getLoans(): List[LoanDTO]',
      '+switchLanguage(lang: str): bool'],
     '#EAD1DC', '#7B0099'),
]

for args in classes:
    class_box(ax, *args)

# Relationships
rels = [
    # (x1, y1, x2, y2, label, style)
    (2.0, 7.8, 6.5, 7.8, '1..*  records', MID_BLUE),
    (6.5, 7.5, 11.2, 7.5, '1  generates', MID_BLUE),
    (11.2, 6.3, 6.5, 6.2, 'uses', AMBER),
    (11.2, 6.3, 11.2, 5.5, 'uses', RED),
    (2.0, 2.7, 6.5, 2.7, 'queries', GREEN),
    (6.5, 2.7, 11.2, 2.7, 'queries', '#5B0099'),
    (2.0, 7.8, 2.0, 3.6, '1  qualifies for', AMBER),
    (11.2, 6.3, 11.2, 2.4, 'renders via', '#7B0099'),
]
for x1, y1, x2, y2, lbl, col in rels:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=col, lw=1.3,
                                connectionstyle='arc3,rad=0.0'))
    mx, my = (x1+x2)/2, (y1+y2)/2
    ax.text(mx, my+0.08, lbl, ha='center', va='bottom', fontsize=6.5,
            color=col, style='italic')

save(fig, '08_class')

print('All diagrams generated successfully!')
