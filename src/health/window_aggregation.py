# src/health/window_aggregation.py

import sys
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

# -----------------------
# Path setup
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "src"))

# ------------------------
# Config
# ------------------------
EVENTS_CSV = REPO_ROOT / "data" / "raw" / "event" / "events.csv"
OUTPUT_DIR = REPO_ROOT / "data"
WINDOW_FREQ = "1h"   # Options: '1h', '6h', '1D'
MAX_ROWS = None      # None = full CSV, or set for testing (e.g., 10000)

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------
# Load and prepare data
# ------------------------
def load_events(csv_path: Path, max_rows: Optional[int] = None) -> pd.DataFrame:
    """
    Load and clean raw events data.
    """

    if not csv_path.exists():
        raise FileNotFoundError(f"Events file not found: {csv_path}")

    print(f"Loading events from: {csv_path}")
    df = pd.read_csv(csv_path, nrows=max_rows)

    if df.empty:
        raise ValueError("Loaded dataframe is empty.")

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Normalize timestamp column
    if "event_timestamp" in df.columns:
        df = df.rename(columns={"event_timestamp": "timestamp"})

    if "timestamp" not in df.columns:
        raise ValueError("Missing required column: 'timestamp'")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    # Safe numeric conversion
    if "event_id" in df.columns:
        df["event_id"] = pd.to_numeric(df["event_id"], errors="coerce")
    else:
        df["event_id"] = 1  # fallback if missing

    # Normalize event_type
    if "event_type" not in df.columns:
        df["event_type"] = ""

    df["event_type"] = df["event_type"].fillna("").astype(str).str.lower()

    # Create failure flag
    FAILURE_TYPES = {"error", "failure", "down", "link_down"}
    df["is_failure"] = df["event_type"].isin(FAILURE_TYPES).astype(int)

    return df


# ------------------------
# Aggregation
# ------------------------
def compute_health_score(df: pd.DataFrame) -> pd.Series:
    """
    Compute health score safely.
    Avoid division-by-zero.
    """
    ratio = df["failure_events"] / df["total_events"]
    ratio = ratio.fillna(0)
    health = 100 - (ratio * 100)
    return health.clip(0, 100)


def aggregate_events_vectorized(
    df: pd.DataFrame,
    freq: str
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate events per device and interface using vectorized pd.Grouper.
    """

    print(f"Aggregating events with frequency: {freq}")

    # ---------------- Device aggregation ----------------
    device_agg = pd.DataFrame()
    if "device_id" in df.columns:
        df_device = df.dropna(subset=["device_id"])

        if not df_device.empty:
            device_agg = (
                df_device
                .groupby(
                    ["device_id", pd.Grouper(key="timestamp", freq=freq)]
                )
                .agg(
                    total_events=("event_id", "count"),
                    failure_events=("is_failure", "sum"),
                )
                .reset_index()
            )

            device_agg["health_score"] = compute_health_score(device_agg)

    # ---------------- Interface aggregation ----------------
    interface_agg = pd.DataFrame()
    if "interface_id" in df.columns:
        df_interface = df.dropna(subset=["interface_id"])

        if not df_interface.empty:
            interface_agg = (
                df_interface
                .groupby(
                    ["interface_id", pd.Grouper(key="timestamp", freq=freq)]
                )
                .agg(
                    total_events=("event_id", "count"),
                    failure_events=("is_failure", "sum"),
                )
                .reset_index()
            )

            interface_agg["health_score"] = compute_health_score(interface_agg)

    return device_agg, interface_agg


# ------------------------
# Save results
# ------------------------
def save_outputs(
    device_agg: pd.DataFrame,
    interface_agg: pd.DataFrame,
    freq: str
):
    """
    Save aggregated CSV files.
    """

    freq_label = freq.replace(" ", "").lower()

    device_path = OUTPUT_DIR / f"aggregated_device_{freq_label}.csv"
    interface_path = OUTPUT_DIR / f"aggregated_interface_{freq_label}.csv"

    if not device_agg.empty:
        device_agg.to_csv(device_path, index=False)
        print(f"Saved device aggregation → {device_path}")

    if not interface_agg.empty:
        interface_agg.to_csv(interface_path, index=False)
        print(f"Saved interface aggregation → {interface_path}")


# ------------------------
# Main
# ------------------------
def main():
    df_events = load_events(EVENTS_CSV, max_rows=MAX_ROWS)

    device_agg, interface_agg = aggregate_events_vectorized(
        df_events,
        WINDOW_FREQ
    )

    # Quick summary
    if not device_agg.empty:
        print("\n=== Device Health Summary (Lowest 5) ===")
        print(
            device_agg
            .sort_values("timestamp")
            .groupby("device_id")["health_score"]
            .last()
            .sort_values()
            .head(5)
        )

    if not interface_agg.empty:
        print("\n=== Interface Health Summary (Lowest 5) ===")
        print(
            interface_agg
            .sort_values("timestamp")
            .groupby("interface_id")["health_score"]
            .last()
            .sort_values()
            .head(5)
        )

    print(
        f"\nAggregation complete! "
        f"Device rows: {len(device_agg)}, "
        f"Interface rows: {len(interface_agg)}"
    )

    save_outputs(device_agg, interface_agg, WINDOW_FREQ)


if __name__ == "__main__":
    main()