# src/health/window_aggregation.py

import sys
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

# -----------------------
# Path setup
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # repo root
sys.path.append(str(REPO_ROOT / "src"))  # so we can import utils

# -----------------------
# Logger
# -----------------------
from utils.logger import get_logger

logger = get_logger("window_aggregation")

# ------------------------
# Config
# ------------------------
EVENTS_CSV = REPO_ROOT / "data" / "raw" / "event" / "events.csv"
OUTPUT_DIR = REPO_ROOT / "data" / "processed"
WINDOW_FREQ = "1h"   # Options: '1h', '6h', '1D'
MAX_ROWS = None      # None = full CSV, or set for testing (e.g., 10000)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------
# Load and prepare data
# ------------------------
def load_events(csv_path: Path, max_rows: Optional[int] = None) -> pd.DataFrame:
    """Load and clean raw events data."""
    if not csv_path.exists():
        logger.error(f"{csv_path} not found.")
        raise FileNotFoundError(f"Events file not found: {csv_path}")

    logger.info(f"Loading events from: {csv_path}")
    df = pd.read_csv(csv_path, nrows=max_rows)

    if df.empty:
        logger.warning("Loaded dataframe is empty.")

    df.columns = df.columns.str.strip()

    if "event_timestamp" in df.columns:
        df = df.rename(columns={"event_timestamp": "timestamp"})

    if "timestamp" not in df.columns:
        logger.error("Missing required column: 'timestamp'")
        raise ValueError("Missing required column: 'timestamp'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["event_id"] = pd.to_numeric(df.get("event_id", 1), errors="coerce")
    df["event_type"] = df.get("event_type", "").fillna("").astype(str).str.lower()

    FAILURE_TYPES = {"error", "failure", "down", "link_down"}
    df["is_failure"] = df["event_type"].isin(FAILURE_TYPES).astype(int)

    return df

# ------------------------
# Aggregation
# ------------------------
def compute_health_score(df: pd.DataFrame) -> pd.Series:
    ratio = df["failure_events"] / df["total_events"]
    ratio = ratio.fillna(0)
    health = 100 - (ratio * 100)
    return health.clip(0, 100)

def aggregate_events_vectorized(df: pd.DataFrame, freq: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logger.info(f"Aggregating events with frequency: {freq}")

    # Device aggregation
    device_agg = pd.DataFrame()
    if "device_id" in df.columns:
        df_device = df.dropna(subset=["device_id"])
        if not df_device.empty:
            device_agg = (
                df_device
                .groupby(["device_id", pd.Grouper(key="timestamp", freq=freq)])
                .agg(total_events=("event_id", "count"),
                     failure_events=("is_failure", "sum"))
                .reset_index()
            )
            device_agg["health_score"] = compute_health_score(device_agg)

    # Interface aggregation
    interface_agg = pd.DataFrame()
    if "interface_id" in df.columns:
        df_interface = df.dropna(subset=["interface_id"])
        if not df_interface.empty:
            interface_agg = (
                df_interface
                .groupby(["interface_id", pd.Grouper(key="timestamp", freq=freq)])
                .agg(total_events=("event_id", "count"),
                     failure_events=("is_failure", "sum"))
                .reset_index()
            )
            interface_agg["health_score"] = compute_health_score(interface_agg)

    return device_agg, interface_agg

# ------------------------
# Save outputs
# ------------------------
# ------------------------
# Save outputs
# ------------------------
def save_outputs(device_agg: pd.DataFrame, interface_agg: pd.DataFrame, freq: str):
    freq_label = freq.replace(" ", "").lower()

    device_path = OUTPUT_DIR / f"aggregated_device_{freq_label}.csv"
    interface_path = OUTPUT_DIR / f"aggregated_interface_{freq_label}.csv"

    if not device_agg.empty:
        device_agg.to_csv(device_path, index=False)
        logger.info(f"Saved device aggregation -> {device_path}")  # changed arrow

    if not interface_agg.empty:
        interface_agg.to_csv(interface_path, index=False)
        logger.info(f"Saved interface aggregation -> {interface_path}")  # changed arrow

# ------------------------
# Main
# ------------------------
def main():
    df_events = load_events(EVENTS_CSV, max_rows=MAX_ROWS)

    device_agg, interface_agg = aggregate_events_vectorized(df_events, WINDOW_FREQ)

    if not device_agg.empty:
        logger.info("Device Health Summary (Lowest 5):")
        logger.info(
            "\n" + str(
                device_agg.sort_values("timestamp")
                          .groupby("device_id")["health_score"]
                          .last()
                          .sort_values()
                          .head(5)
            )
        )

    if not interface_agg.empty:
        logger.info("Interface Health Summary (Lowest 5):")
        logger.info(
            "\n" + str(
                interface_agg.sort_values("timestamp")
                             .groupby("interface_id")["health_score"]
                             .last()
                             .sort_values()
                             .head(5)
            )
        )

    logger.info(f"Aggregation complete! Device rows: {len(device_agg)}, Interface rows: {len(interface_agg)}")
    save_outputs(device_agg, interface_agg, WINDOW_FREQ)

if __name__ == "__main__":
    main()