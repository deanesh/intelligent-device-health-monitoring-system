# src/models/failure_prediction.py

import sys
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import joblib
import os
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from warnings import filterwarnings
filterwarnings('ignore')

# -----------------------
# Add repo root to sys.path
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

# -----------------------
# Logger
# -----------------------
from src.utils.logger import get_logger
logger = get_logger("failure_prediction")

# -----------------------
# Configurable paths
# -----------------------
PROCESSED_DATA_PATH = REPO_ROOT / "data" / "processed" / "device" / "device_features.csv"
MODEL_SAVE_PATH = REPO_ROOT / "models" / "failure_model_xgb.pkl"

class FailurePredictionModel:
    def __init__(self, model=None):
        self.model = model if model else XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss',
            scale_pos_weight=1
        )
        self.best_threshold = 0.5

    def load_data(self, path=PROCESSED_DATA_PATH):
        if not Path(path).exists():
            logger.warning(f"Feature file not found at {path}")
            logger.warning("Please run feature_engineering_simple.py first to generate the CSV.")
            return None, None
        
        df = pd.read_csv(path)
        if 'target' not in df.columns:
            raise ValueError("Target column 'target' not found in the data")
        
        X = df.drop(columns=["target", "timestamp", "device_id"], errors='ignore')
        y = df["target"]
        logger.info(f"Loaded feature data with {len(df)} rows and {len(X.columns)} columns")
        return X, y

    def plot_f1_vs_threshold(self, y_true, y_probs):
        thresholds = np.arange(0.0, 1.0, 0.01)
        f1_scores = [(f1_score(y_true, (y_probs >= t).astype(int))) for t in thresholds]
        
        plt.figure(figsize=(8,5))
        plt.plot(thresholds, f1_scores, label='F1-score', color='darkorange')
        plt.axvline(self.best_threshold, color='blue', linestyle='--', label=f'Best threshold: {self.best_threshold:.2f}')
        plt.xlabel('Probability Threshold')
        plt.ylabel('F1-score')
        plt.title('F1-score vs Probability Threshold')
        plt.legend()
        plt.grid(True)
        plt.show()
        logger.info("F1-score vs threshold plot displayed")

    def tune_threshold(self, y_true, y_probs):
        best_f1 = 0
        best_thresh = 0.5
        for thresh in np.arange(0.05, 0.95, 0.01):
            y_pred = (y_probs >= thresh).astype(int)
            f1 = f1_score(y_true, y_pred)
            if f1 > best_f1:
                best_f1 = f1
                best_thresh = thresh
        logger.info(f"Best F1={best_f1:.3f} at threshold={best_thresh:.2f}")
        self.best_threshold = best_thresh
        return best_thresh, best_f1

    def train(self, X, y, test_size=0.2, random_state=42):
        if X is None or y is None:
            logger.warning("Training skipped: No data loaded.")
            return None
        
        pos = sum(y==1)
        neg = sum(y==0)
        if hasattr(self.model, "scale_pos_weight"):
            self.model.scale_pos_weight = neg / max(pos,1)
            logger.info(f"Set scale_pos_weight={self.model.scale_pos_weight:.2f}")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        self.model.fit(X_train, y_train)
        y_probs = self.model.predict_proba(X_test)[:, 1]
        
        self.tune_threshold(y_test, y_probs)
        self.plot_f1_vs_threshold(y_test, y_probs)
        
        y_pred = (y_probs >= self.best_threshold).astype(int)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_probs),
            "threshold": self.best_threshold
        }
        logger.info(f"Training metrics: {metrics}")
        return metrics

    def predict(self, X_new):
        if X_new is None:
            logger.warning("Prediction skipped: No input data provided.")
            return None, None
        probs = self.model.predict_proba(X_new)[:, 1]
        preds = (probs >= self.best_threshold).astype(int)
        logger.info(f"Predicted {len(preds)} rows")
        return preds, probs

    def save_model(self, path=MODEL_SAVE_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"Model saved to: {path}")

    def load_model(self, path=MODEL_SAVE_PATH):
        if not os.path.exists(path):
            logger.warning(f"Model not found at {path}")
            return
        self.model = joblib.load(path)
        logger.info(f"Model loaded from: {path}")

# -----------------------
# Example usage
# -----------------------
if __name__ == "__main__":
    fp_model = FailurePredictionModel()
    X, y = fp_model.load_data()
    if X is not None and y is not None:
        metrics = fp_model.train(X, y)
        if metrics:
            logger.info(f"Model metrics: {metrics}")
            fp_model.save_model()