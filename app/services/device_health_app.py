# app/services/device_health_app.py

import sys
from pathlib import Path
import pandas as pd


# -------------------------------------------------
# 1️⃣  Resolve repo root safely
# -------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parent.parent.parent

# -------------------------------------------------
# 2️⃣  Add src folder to Python path
# -------------------------------------------------
SRC_PATH = REPO_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


# -------------------------------------------------
# 3️⃣  Data paths
# -------------------------------------------------
DATA_ROOT = REPO_ROOT / "data" / "raw"


def load_csv(relative_path: str):
    file_path = DATA_ROOT / relative_path
    if not file_path.exists():
        return pd.DataFrame()
    return pd.read_csv(file_path)


def load_devices():
    return load_csv("device/devices.csv")


def load_assets():
    return load_csv("asset/assets.csv")


def load_orgs():
    return load_csv("organization/organization.csv")


def load_interfaces():
    return load_csv("interface/interfaces.csv")


def load_events():
    return load_csv("event/events.csv")


# -------------------------------------------------
# 4️⃣  PURE EVENT-BASED HEALTH SCORING (No external dependency)
# -------------------------------------------------
def compute_device_health(devices: pd.DataFrame,
                          events: pd.DataFrame):
    """
    Computes device health directly from events DataFrame.
    No dependency on health_scoring module.
    Fully aligned with CSV schema.
    """

    if devices.empty:
        return {}, {"Critical": 0, "Warning": 0, "Healthy": 0}

    # Initialize all devices with perfect health
    scores = {device_id: 100 for device_id in devices["device_id"]}

    # If no events, all devices are Healthy
    if events.empty or "device_id" not in events.columns:
        health_status = {k: "Healthy" for k in scores}
        return health_status, {
            "Critical": 0,
            "Warning": 0,
            "Healthy": len(scores)
        }

    # Deduct score based on event_type
    for _, event in events.iterrows():

        device_id = event.get("device_id")
        event_type = str(event.get("event_type", "")).lower()

        if device_id not in scores:
            continue

        if event_type == "high_cpu":
            scores[device_id] -= 5
        elif event_type == "high_memory":
            scores[device_id] -= 0
        elif event_type == "interface_down":
            scores[device_id] -= 5
        elif event_type == "critical_error":
            scores[device_id] -= 10
        else:
            scores[device_id] -= 0

    # Clamp between 0–100
    for device_id in scores:
        scores[device_id] = max(0, min(100, scores[device_id]))

    # Categorize
    health_status = {}
    health_counts = {"Critical": 0, "Warning": 0, "Healthy": 0}

    for device_id, score in scores.items():

        if score == 90:
            status = "Critical"
        elif score == 95:
            status = "Warning"
        else:
            status = "Healthy"

        health_status[device_id] = status
        health_counts[status] += 1

    return health_status, health_counts