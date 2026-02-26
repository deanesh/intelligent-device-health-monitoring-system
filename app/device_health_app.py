# app/device_health_app.py

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# Robust path setup
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[1]  # app/ → repo root
MODELS_PATH = REPO_ROOT / "src" / "models"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(MODELS_PATH))

# Logger
from src.utils.logger import get_logger
logger = get_logger("device_health_app")

# -----------------------
# Import model class safely
# -----------------------
try:
    from failure_prediction import FailurePredictionModel
except ModuleNotFoundError:
    logger.error("Cannot import FailurePredictionModel from src/models. Check that src/models/failure_prediction.py exists.")
    st.error("Cannot import model class. Check logs for details.")
    st.stop()

# -----------------------
# File paths
# -----------------------
MODEL_PATH = REPO_ROOT / "models" / "failure_model_xgb.pkl"
FEATURES_PATH = REPO_ROOT / "data" / "processed" / "device" / "device_features.csv"

# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="Device Health Dashboard", layout="wide")
st.title("📊 Device Health Monitoring Dashboard")

# Load model
model = FailurePredictionModel()
if not MODEL_PATH.exists():
    logger.warning(f"Model not found at {MODEL_PATH}. Please run train.py first.")
    st.warning(f"Model not found at {MODEL_PATH}. Please run train.py first.")
else:
    model.load_model(MODEL_PATH)
    logger.info(f"Loaded model from {MODEL_PATH}")

# Load features and predict
if not FEATURES_PATH.exists():
    logger.warning(f"Feature file not found at {FEATURES_PATH}. Please run feature_engineering_simple.py first.")
    st.warning(f"Feature file not found at {FEATURES_PATH}. Please run feature_engineering_simple.py first.")
else:
    df = pd.read_csv(FEATURES_PATH)
    X = df.drop(columns=["target", "timestamp", "device_id"], errors='ignore')
    preds, probs = model.predict(X)
    df["Predicted Failure"] = preds
    df["Failure Probability"] = probs
    logger.info(f"Predictions generated for {len(df)} rows")

    st.subheader("Device Predictions")
    st.dataframe(df[["timestamp", "device_id", "Predicted Failure", "Failure Probability"]]
                 .sort_values(["timestamp","device_id"]))

    # Filter by device
    device_filter = st.selectbox("Filter by Device ID", ["All"] + df["device_id"].unique().tolist())
    if device_filter != "All":
        df_filtered = df[df["device_id"] == device_filter]
    else:
        df_filtered = df

    # Plot failure probabilities over time
    st.subheader("Failure Probability Over Time")
    fig, ax = plt.subplots(figsize=(10,4))
    for device_id, group in df_filtered.groupby("device_id"):
        ax.plot(pd.to_datetime(group["timestamp"]), group["Failure Probability"], label=f"{device_id}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Failure Probability")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    logger.info("Displayed failure probability plot")