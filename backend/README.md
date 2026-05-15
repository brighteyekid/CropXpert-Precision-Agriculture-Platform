# CropXpert — Backend

Production-ready backend for CropXpert precision agriculture platform.

## Architecture

```
FastAPI REST + WebSocket API
├── ML Pipeline (RF/XGB/LGBM/SVM/MLP)
├── MQTT Sensor Ingestion (Mosquitto)
├── AGMARKNET Market Intelligence
├── Government Scheme Advisory
├── OTP Auth (MSG91)
├── Discord Bot
└── SQLite + SQLAlchemy
```

## Quick Start

### 1. Train the ML model

```bash
# Download dataset first:
# https://www.kaggle.com/atharvaingle/crop-recommendation-dataset
# Place as: backend/ml/data/crop_recommendation.csv

cd backend
pip install -r requirements.txt

cd ml
python train.py
# → Saves random_forest.joblib + scaler.joblib to ml/models/
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in API keys as needed:
# - OPENWEATHERMAP_API_KEY (for rainfall)
# - DATA_GOV_IN_API_KEY (for AGMARKNET)
# - MSG91_AUTH_KEY (for OTP, optional in dev)
# - DISCORD_BOT_TOKEN (optional)
```

### 3. Start backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start frontend (separate terminal)

```bash
npm run dev
# → http://localhost:3000
```

### 5. Docker (alternative)

```bash
cd backend
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/send-otp` | Send OTP to mobile |
| POST | `/api/auth/verify-otp` | Verify OTP → JWT |
| GET | `/api/auth/me` | Get farmer profile |
| PUT | `/api/farmer/profile` | Update profile |
| POST | `/api/sensors/reading` | Submit sensor data |
| GET | `/api/sensors/history` | Reading history |
| GET | `/api/sensors/latest` | Latest reading |
| GET | `/api/sensors/export` | CSV export |
| POST | `/api/predict` | Crop recommendation |
| GET | `/api/market/msp` | MSP lookup |
| GET | `/api/market/mandi-prices` | Mandi prices |
| GET | `/api/market/trend` | Price trend |
| GET | `/api/market/all-crops` | All MSP data |
| GET | `/api/schemes` | Government schemes |
| GET | `/api/schemes/loans` | Loan programs |
| POST | `/api/schemes/emi-calculate` | EMI calculator |
| GET | `/api/dashboard/summary` | Dashboard aggregate |
| WS | `/ws/live?token=JWT` | Live sensor push |

## Discord Bot Commands

| Command | Description |
|---------|-------------|
| `/crop` | Get crop recommendation |
| `/schemes` | List eligible schemes |
| `/msp` | Current MSP data |
| `/soilhealth` | Latest soil reading |
| `/link` | Link Discord account |
| `/help` | Command reference |

## ML Models Trained

| Model | Expected Accuracy |
|-------|------------------|
| Random Forest | 99.2% |
| XGBoost | 98.7% |
| LightGBM | 98.5% |
| SVM (RBF) | 97.8% |
| MLP | 97.1% |

## Swagger Docs

Available at `http://localhost:8000/docs` when server is running.
