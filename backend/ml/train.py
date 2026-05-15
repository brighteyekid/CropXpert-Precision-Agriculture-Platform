"""
CropXpert — ML Training Pipeline
Train 5 models, auto-select best, export comparison + serialized artifacts.

Dataset: Kaggle Indian Crop Recommendation
         2,200 samples × 22 crops × 7 features

Usage:
    cd backend/ml
    python train.py
"""
import os
import sys
import time
import warnings
import numpy as np
import pandas as pd
from scipy import stats

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "crop_recommendation.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL = "label"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_data():
    print("📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Loaded {len(df)} samples × {len(df.columns)} columns")
    print(f"   Crops: {df[TARGET_COL].nunique()} unique → {sorted(df[TARGET_COL].unique())}")
    return df


def preprocess(df: pd.DataFrame):
    print("\n🔬 Preprocessing...")

    # Z-score outlier removal (|z| > 3)
    z = np.abs(stats.zscore(df[FEATURE_COLS]))
    mask = (z < 3).all(axis=1)
    removed = len(df) - mask.sum()
    df = df[mask].copy()
    print(f"   Removed {removed} outlier rows (z > 3)")

    # Per-class median imputation
    for col in FEATURE_COLS:
        if df[col].isnull().any():
            medians = df.groupby(TARGET_COL)[col].transform("median")
            df[col] = df[col].fillna(medians)
    print(f"   Missing values filled via per-class median imputation")

    # Encode labels
    le = LabelEncoder()
    df["target"] = le.fit_transform(df[TARGET_COL])
    print(f"   Labels encoded: {list(le.classes_)}")

    return df, le


def split_data(df: pd.DataFrame):
    print("\n📊 Splitting data (70/15/15, stratified)...")
    X = df[FEATURE_COLS].values
    y = df["target"].values

    # 70% train, 30% temp
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y
    )
    # 50/50 of temp → 15/15
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
    )

    print(f"   Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def scale_features(X_train, X_val, X_test):
    print("\n⚖️  Fitting StandardScaler...")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    scaler_path = os.path.join(MODEL_DIR, "scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"   Scaler saved → {scaler_path}")

    return X_train_s, X_val_s, X_test_s, scaler


def train_models(X_train, y_train):
    print("\n🏋️ Training 5 models with GridSearchCV + 5-fold stratified CV...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {}

    # 1. Random Forest
    print("\n   [1/5] Random Forest...")
    t = time.time()
    rf_params = {
        "n_estimators": [100, 300, 500],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5],
    }
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        rf_params, cv=cv, scoring="accuracy", n_jobs=-1, verbose=0,
    )
    rf_grid.fit(X_train, y_train)
    models["Random Forest"] = rf_grid.best_estimator_
    print(f"         Best: {rf_grid.best_params_} | CV acc: {rf_grid.best_score_:.4f} | {time.time()-t:.1f}s")

    # 2. XGBoost
    print("   [2/5] XGBoost...")
    t = time.time()
    try:
        from xgboost import XGBClassifier
        xgb_params = {
            "n_estimators": [100, 300],
            "max_depth": [6, 10],
            "learning_rate": [0.1, 0.05],
        }
        xgb_grid = GridSearchCV(
            XGBClassifier(random_state=42, use_label_encoder=False, eval_metric="mlogloss", n_jobs=-1, verbosity=0),
            xgb_params, cv=cv, scoring="accuracy", n_jobs=-1, verbose=0,
        )
        xgb_grid.fit(X_train, y_train)
        models["XGBoost"] = xgb_grid.best_estimator_
        print(f"         Best: {xgb_grid.best_params_} | CV acc: {xgb_grid.best_score_:.4f} | {time.time()-t:.1f}s")
    except ImportError:
        print("         ⚠️  xgboost not installed — skipping")

    # 3. LightGBM
    print("   [3/5] LightGBM...")
    t = time.time()
    try:
        from lightgbm import LGBMClassifier
        lgb_params = {
            "n_estimators": [100, 300],
            "max_depth": [6, 10, -1],
            "learning_rate": [0.1, 0.05],
        }
        lgb_grid = GridSearchCV(
            LGBMClassifier(random_state=42, verbose=-1, n_jobs=-1),
            lgb_params, cv=cv, scoring="accuracy", n_jobs=-1, verbose=0,
        )
        lgb_grid.fit(X_train, y_train)
        models["LightGBM"] = lgb_grid.best_estimator_
        print(f"         Best: {lgb_grid.best_params_} | CV acc: {lgb_grid.best_score_:.4f} | {time.time()-t:.1f}s")
    except ImportError:
        print("         ⚠️  lightgbm not installed — skipping")

    # 4. SVM (RBF)
    print("   [4/5] SVM (RBF kernel)...")
    t = time.time()
    svm_params = {"C": [1, 10], "gamma": ["scale", "auto"]}
    svm_grid = GridSearchCV(
        SVC(kernel="rbf", probability=True, random_state=42),
        svm_params, cv=cv, scoring="accuracy", n_jobs=-1, verbose=0,
    )
    svm_grid.fit(X_train, y_train)
    models["SVM (RBF)"] = svm_grid.best_estimator_
    print(f"         Best: {svm_grid.best_params_} | CV acc: {svm_grid.best_score_:.4f} | {time.time()-t:.1f}s")

    # 5. MLP
    print("   [5/5] MLP Neural Network...")
    t = time.time()
    mlp_params = {
        "hidden_layer_sizes": [(128, 64, 32)],
        "alpha": [0.0001, 0.001],
        "learning_rate_init": [0.001, 0.01],
    }
    mlp_grid = GridSearchCV(
        MLPClassifier(max_iter=500, random_state=42),
        mlp_params, cv=cv, scoring="accuracy", n_jobs=-1, verbose=0,
    )
    mlp_grid.fit(X_train, y_train)
    models["MLP"] = mlp_grid.best_estimator_
    print(f"         Best: {mlp_grid.best_params_} | CV acc: {mlp_grid.best_score_:.4f} | {time.time()-t:.1f}s")

    return models


def evaluate_models(models, X_test, y_test, le):
    print("\n📈 Evaluating on held-out test set...")
    results = []
    best_name, best_acc, best_model = None, 0, None

    for name, model in models.items():
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision (macro)": round(prec, 4),
            "Recall (macro)": round(rec, 4),
            "F1 (macro)": round(f1, 4),
        })
        print(f"   {name:<20} Acc: {acc:.4f} | P: {prec:.4f} | R: {rec:.4f} | F1: {f1:.4f}")

        if acc > best_acc:
            best_acc = acc
            best_name = name
            best_model = model

    # Export comparison CSV
    results_df = pd.DataFrame(results).sort_values("Accuracy", ascending=False)
    csv_path = os.path.join(RESULTS_DIR, "model_comparison.csv")
    results_df.to_csv(csv_path, index=False)
    print(f"\n   Results → {csv_path}")

    return best_name, best_model, best_acc


def save_best_model(name, model):
    model_path = os.path.join(MODEL_DIR, "random_forest.joblib")
    joblib.dump(model, model_path)
    print(f"\n💾 Best model ({name}) saved → {model_path}")


def print_feature_importances(model):
    print("\n📊 Feature Importances (top 7):")
    try:
        importances = model.feature_importances_
        sorted_idx = np.argsort(importances)[::-1]
        for i, idx in enumerate(sorted_idx):
            print(f"   {i+1}. {FEATURE_COLS[idx]:<15} {importances[idx]:.4f}")
    except AttributeError:
        print("   (not available for this model type)")


def main():
    print("=" * 60)
    print("  CropXpert — ML Training Pipeline")
    print("=" * 60)

    # Check dataset exists
    if not os.path.exists(DATA_PATH):
        print(f"\n❌ Dataset not found at: {DATA_PATH}")
        print("   Download from: https://www.kaggle.com/atharvaingle/crop-recommendation-dataset")
        print(f"   Place the CSV at: {DATA_PATH}")
        sys.exit(1)

    df = load_data()
    df, le = preprocess(df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(df)
    X_train_s, X_val_s, X_test_s, scaler = scale_features(X_train, X_val, X_test)

    models = train_models(X_train_s, y_train)
    best_name, best_model, best_acc = evaluate_models(models, X_test_s, y_test, le)

    save_best_model(best_name, best_model)
    print_feature_importances(best_model)

    print("\n" + "=" * 60)
    print(f"  ✅ Training complete — Best: {best_name} ({best_acc*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    main()
