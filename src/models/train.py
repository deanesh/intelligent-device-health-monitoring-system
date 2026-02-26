# src/models/train.py

import sys
from pathlib import Path

# -----------------------
# Repo root and paths
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # repo root
SRC_PATH = REPO_ROOT / "src"
MODELS_PATH = SRC_PATH / "models"

sys.path.append(str(SRC_PATH))
sys.path.append(str(MODELS_PATH))
sys.path.append(str(REPO_ROOT))

# -----------------------
# Imports
# -----------------------
from src.utils.logger import get_logger
from failure_prediction import FailurePredictionModel

# -----------------------
# Logger setup (consolidated log)
# -----------------------
logger = get_logger("train")  # logs go to logs/pipeline.log with rollover

# -----------------------
# Main training orchestrator
# -----------------------
def main():
    logger.info("Starting device failure prediction training pipeline...")

    # Initialize model
    model = FailurePredictionModel()

    # Load features
    X, y = model.load_data()
    if X is None or y is None:
        logger.warning("No feature data available. Please run feature_engineering_simple.py first.")
        return

    # Train model with automatic threshold tuning
    metrics = model.train(X, y)
    if metrics:
        logger.info("Training complete!")
        logger.info(f"Model metrics: {metrics}")

        # Save trained model
        model.save_model()
        logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()