# src/models/train.py

import sys
from pathlib import Path
from failure_prediction import FailurePredictionModel

# -----------------------
# Add repo root to sys.path
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

# -----------------------
# Main training orchestrator
# -----------------------
def main():
    print("Starting device failure prediction training pipeline...\n")

    # Initialize model
    model = FailurePredictionModel()

    # Load features
    X, y = model.load_data()
    if X is None or y is None:
        print("No feature data available. Please run feature_engineering_simple.py first.")
        return

    # Train model with automatic threshold tuning
    metrics = model.train(X, y)
    if metrics:
        print("\nTraining complete!")
        print("Model metrics:", metrics)

        # Save trained model
        model.save_model()
        print("\nPipeline finished successfully.")

if __name__ == "__main__":
    main()