# src/models/evaluate.py

import sys
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import joblib
import numpy as np
import matplotlib.pyplot as plt
from failure_prediction import FailurePredictionModel

# -----------------------
# Add repo root to sys.path
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

# -----------------------
# Configurable paths
# -----------------------
PROCESSED_DATA_PATH = REPO_ROOT / "data" / "processed" / "device" / "device_features.csv"
MODEL_PATH = REPO_ROOT / "models" / "failure_model_xgb.pkl"

def plot_f1_vs_threshold(y_true, y_probs, best_threshold):
    thresholds = np.arange(0.0, 1.0, 0.01)
    f1_scores = [f1_score(y_true, (y_probs >= t).astype(int)) for t in thresholds]
    
    plt.figure(figsize=(8,5))
    plt.plot(thresholds, f1_scores, color='darkorange', label='F1-score')
    plt.axvline(best_threshold, color='blue', linestyle='--', label=f'Best threshold: {best_threshold:.2f}')
    plt.xlabel("Probability Threshold")
    plt.ylabel("F1-score")
    plt.title("F1-score vs Probability Threshold")
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    print("Starting model evaluation...\n")

    # Load features
    if not PROCESSED_DATA_PATH.exists():
        print(f"WARNING: Feature file not found at {PROCESSED_DATA_PATH}")
        print("Please run feature_engineering_simple.py first.")
        return

    df = pd.read_csv(PROCESSED_DATA_PATH)
    if 'target' not in df.columns:
        print("Target column not found in features.")
        return

    X = df.drop(columns=["target", "timestamp", "device_id"], errors='ignore')
    y = df["target"]

    # Load trained model
    if not MODEL_PATH.exists():
        print(f"WARNING: Model not found at {MODEL_PATH}")
        print("Please run train.py first.")
        return

    model = FailurePredictionModel()
    model.load_model(MODEL_PATH)

    # Predict probabilities and labels
    y_probs = model.model.predict_proba(X)[:, 1]
    y_pred = (y_probs >= model.best_threshold).astype(int)

    # Metrics
    metrics = {
        "accuracy": accuracy_score(y, y_pred),
        "f1_score": f1_score(y, y_pred),
        "roc_auc": roc_auc_score(y, y_probs),
        "threshold": model.best_threshold
    }

    print("\nEvaluation metrics on full dataset:")
    print(metrics)

    # Plot F1 vs threshold
    plot_f1_vs_threshold(y, y_probs, model.best_threshold)
    print("\nEvaluation complete.")

if __name__ == "__main__":
    main()