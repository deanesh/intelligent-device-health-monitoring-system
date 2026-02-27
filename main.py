import sys
from pathlib import Path

# Add src folder to path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from pipeline.run_pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline()