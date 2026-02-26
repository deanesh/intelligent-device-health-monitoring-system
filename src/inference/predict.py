# src/inference/predict.py

import sys
from pathlib import Path
import pandas as pd
import joblib

# -----------------------
# Set up paths
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_PATH = REPO_ROOT / "src" / "models"
sys.path.append(str(REPO_ROOT))
sys.path.append(str(MODELS_PATH))  # so we can import failure_prediction.py

from failure_prediction import FailurePredictionModel

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
    print("Starting device failure prediction inference...\n")

    # Load model
    model = FailurePredictionModel()
    if not MODEL_PATH.exists():
        print(f"WARNING: Model file not found at {MODEL_PATH}")
        print("Please run train.py first.")
        return
    model.load_model(MODEL_PATH)

    # Load input features
    if not INPUT_FEATURES_PATH.exists():
        print(f"WARNING: Input feature file not found at {INPUT_FEATURES_PATH}")
        print("Please run feature_engineering_simple.py first.")
        return

    df = pd.read_csv(INPUT_FEATURES_PATH)
    X = df.drop(columns=["target", "timestamp", "device_id"], errors='ignore')

    # Predict failures
    preds, probs = model.predict(X)

    # Add predictions to DataFrame
    df["predicted_failure"] = preds
    df["failure_probability"] = probs

    # Save predictions
    OUTPUT_PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PREDICTIONS_PATH, index=False)
    print(f"Predictions saved to: {OUTPUT_PREDICTIONS_PATH}")
    print("\nInference complete.")


if __name__ == "__main__":
    main()