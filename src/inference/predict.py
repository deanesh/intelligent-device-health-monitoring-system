# src/inference/predict.py

import sys
from pathlib import Path
import pandas as pd

# -----------------------
# Set up paths
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_PATH = REPO_ROOT / "src" / "models"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(MODELS_PATH))  # so we can import failure_prediction.py

from failure_prediction import FailurePredictionModel

# -----------------------
# Logger
# -----------------------
from src.utils.logger import get_logger
logger = get_logger("predict")

# -----------------------
# File paths
# -----------------------
MODEL_PATH = REPO_ROOT / "models" / "failure_model_xgb.pkl"
INPUT_FEATURES_PATH = REPO_ROOT / "data" / "processed" / "device" / "device_features.csv"
OUTPUT_PREDICTIONS_PATH = REPO_ROOT / "data" / "processed" / "device" / "device_predictions.csv"

# -----------------------
# Inference
# -----------------------
def main():
    logger.info("Starting device failure prediction inference...")

    # Load model
    model = FailurePredictionModel()
    if not MODEL_PATH.exists():
        logger.warning(f"Model file not found at {MODEL_PATH}")
        logger.warning("Please run train.py first.")
        return
    model.load_model(MODEL_PATH)

    # Load input features
    if not INPUT_FEATURES_PATH.exists():
        logger.warning(f"Input feature file not found at {INPUT_FEATURES_PATH}")
        logger.warning("Please run feature_engineering_simple.py first.")
        return

    df = pd.read_csv(INPUT_FEATURES_PATH)
    X = df.drop(columns=["target", "timestamp", "device_id"], errors='ignore')
    logger.info(f"Loaded input features: {X.shape[0]} rows, {X.shape[1]} columns")

    # Predict failures
    preds, probs = model.predict(X)
    df["predicted_failure"] = preds
    df["failure_probability"] = probs

    # Save predictions
    OUTPUT_PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PREDICTIONS_PATH, index=False)
    logger.info(f"Predictions saved to: {OUTPUT_PREDICTIONS_PATH}")
    logger.info("Inference complete.")

if __name__ == "__main__":
    main()