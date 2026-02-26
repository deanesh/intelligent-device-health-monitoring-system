# feature_engineering_simple.py

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# -----------------------
# Paths
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "data" / "aggregated_device_1h.csv"
MODEL_PATH = REPO_ROOT / "models" / "device_failure_model_balanced_simple.pkl"

# -----------------------
# Load data
# -----------------------
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
df = df.sort_values(["device_id", "timestamp"])
print(f"Loaded data: {df.shape[0]} rows")

# -----------------------
# Create features
# -----------------------
print("Creating simple features...")

# Basic features
df["failure_rate"] = df["failure_events"] / df["total_events"]
df["failure_rate"] = df["failure_rate"].fillna(0)

# Rolling 3-window failure_events per device
df["rolling_failure_3"] = df.groupby("device_id")["failure_events"].transform(
    lambda x: x.rolling(3, min_periods=1).mean()
)

# -----------------------
# Create target
# -----------------------
print("Creating target (next window failure)...")
df["target"] = df.groupby("device_id")["failure_events"].shift(-1).fillna(0)
df["target"] = (df["target"] > 0).astype(int)

# Drop rows with missing target
df = df.dropna()

# -----------------------
# Select features & target
# -----------------------
feature_cols = ["total_events", "failure_events", "health_score", "failure_rate", "rolling_failure_3"]
X = df[feature_cols]
y = df["target"]

# -----------------------
# Train/Validation split (chronological)
# -----------------------
split_index = int(len(df) * 0.8)
X_train, X_val = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_val = y.iloc[:split_index], y.iloc[split_index:]

print(f"Training on {len(X_train)} rows, validating on {len(X_val)} rows")

# -----------------------
# Train model
# -----------------------
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
model.fit(X_train, y_train)
print("Model training complete!")

# -----------------------
# Predict & evaluate
# -----------------------
threshold = 0.525
probs = model.predict_proba(X_val)[:, 1]
y_pred = (probs >= threshold).astype(int)

print("\nModel Evaluation at fixed threshold 0.525:")
print(classification_report(y_val, y_pred))
print(confusion_matrix(y_val, y_pred))

# -----------------------
# Save model
# -----------------------
joblib.dump(model, MODEL_PATH)
print(f"Model saved to: {MODEL_PATH}")
print(f"Balanced threshold used: {threshold}")