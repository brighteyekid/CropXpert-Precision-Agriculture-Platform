"""
CropXpert — Data preprocessing utilities.
Reusable functions for train.py and evaluate.py.
"""
import numpy as np
import pandas as pd
from scipy import stats

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL = "label"


def remove_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Remove rows where any feature has |z-score| > threshold."""
    z = np.abs(stats.zscore(df[FEATURE_COLS]))
    return df[(z < threshold).all(axis=1)].copy()


def impute_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Per-class median imputation for missing feature values."""
    for col in FEATURE_COLS:
        if df[col].isnull().any():
            medians = df.groupby(TARGET_COL)[col].transform("median")
            df[col] = df[col].fillna(medians)
    return df
