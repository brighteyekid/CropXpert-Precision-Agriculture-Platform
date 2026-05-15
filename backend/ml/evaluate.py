"""
CropXpert — Model evaluation utility.
Loads a trained model and runs comparison metrics on the test set.
"""
import os
import sys
import numpy as np
import pandas as pd
import joblib
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "crop_recommendation.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]


def evaluate():
    df = pd.read_csv(DATA_PATH)

    # Same preprocessing as train.py
    z = np.abs(stats.zscore(df[FEATURE_COLS]))
    df = df[(z < 3).all(axis=1)].copy()

    le = LabelEncoder()
    df["target"] = le.fit_transform(df["label"])

    X = df[FEATURE_COLS].values
    y = df["target"].values

    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
    _, X_test, _, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)

    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
    model = joblib.load(os.path.join(MODEL_DIR, "random_forest.joblib"))

    X_test_s = scaler.transform(X_test)
    y_pred = model.predict(X_test_s)

    print("=" * 50)
    print("  CropXpert — Model Evaluation")
    print("=" * 50)
    print(f"\nAccuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred, average='macro'):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred, average='macro'):.4f}")
    print(f"F1:        {f1_score(y_test, y_pred, average='macro'):.4f}")
    print("\nPer-class report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))


if __name__ == "__main__":
    evaluate()
