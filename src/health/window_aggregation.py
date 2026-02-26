# src/health/window_aggregation.py
import sys
from pathlib import Path
import pandas as pd

# -----------------------
# Path setup
# -----------------------
REPO_ROOT = Path(__file__).parents[1].parent
sys.path.append(str(REPO_ROOT / "src"))

# ------------------------
# Config
# ------------------------
EVENTS_CSV = REPO_ROOT / "data" / "raw" / "event" / "events.csv"
WINDOW_FREQ = "1h"   # Can be '1h', '6h', '1D'
MAX_ROWS = None      # None = load full CSV, or set for testing e.g., 10000

# ------------------------
# Load and prepare data
# ------------------------
def load_events(csv_path: Path, max_rows=None):
    print(f"Loading events from: {csv_path}")
    df = pd.read_csv(csv_path, nrows=max_rows)
    # Strip whitespace from columns
    df.columns = df.columns.str.strip()
    # Rename timestamp column
    if "event_timestamp" in df.columns:
        df = df.rename(columns={"event_timestamp": "timestamp"})
    # Convert types
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["event_id"] = pd.to_numeric(df["event_id"], errors="coerce").fillna(0).astype(int)
    df["event_type"] = df["event_type"].fillna("").str.lower()
    # Create failure flag
    df["is_failure"] = df["event_type"].isin(["error", "failure", "down", "link_down"]).astype(int)
    df = df.dropna(subset=["timestamp"])
    return df

# ------------------------
# Vectorized aggregation with pd.Grouper
# ------------------------
def aggregate_events_vectorized(df: pd.DataFrame, freq: str):
    """Aggregate events per device and interface using fully vectorized pd.Grouper."""
    print("Aggregating events vectorized...")

    # ---- Device aggregation ----
    df_device = df.dropna(subset=["device_id"])
    device_agg = (
        df_device.groupby(["device_id", pd.Grouper(key="timestamp", freq=freq)])
        .agg(
            total_events=("event_id", "count"),
            failure_events=("is_failure", "sum")
        )
        .reset_index()
    )
    device_agg["health_score"] = 100 - (device_agg["failure_events"] / device_agg["total_events"] * 100)
    device_agg["health_score"] = device_agg["health_score"].clip(0, 100)

    # ---- Interface aggregation ----
    df_interface = df.dropna(subset=["interface_id"])
    interface_agg = (
        df_interface.groupby(["interface_id", pd.Grouper(key="timestamp", freq=freq)])
        .agg(
            total_events=("event_id", "count"),
            failure_events=("is_failure", "sum")
        )
        .reset_index()
    )
    interface_agg["health_score"] = 100 - (interface_agg["failure_events"] / interface_agg["total_events"] * 100)
    interface_agg["health_score"] = interface_agg["health_score"].clip(0, 100)

    return device_agg, interface_agg

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    df_events = load_events(EVENTS_CSV, max_rows=MAX_ROWS)
    device_agg, interface_agg = aggregate_events_vectorized(df_events, WINDOW_FREQ)

    # Quick summary: last health per device/interface
    print("\n=== Device Health Summary ===")
    top_devices = (
        device_agg.groupby("device_id")["health_score"]
        .last()
        .sort_values()
        .head(5)
    )
    print(top_devices)

    print("\n=== Interface Health Summary ===")
    top_interfaces = (
        interface_agg.groupby("interface_id")["health_score"]
        .last()
        .sort_values()
        .head(5)
    )
    print(top_interfaces)

    print(f"\nAggregation complete! Device rows: {len(device_agg)}, Interface rows: {len(interface_agg)}")