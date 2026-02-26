# src/health/health_scoring.py

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# -----------------------
# Repo root & paths
# -----------------------
REPO_ROOT = Path(__file__).parents[1].parent  # intelligent-device-health/

# -----------------------
# Logger
# -----------------------
from utils.logger import get_logger
logger = get_logger("health_scoring")

# -----------------------
# Import relational model
# -----------------------
from transformation.relational_model import Device, Interface, Event
from transformation.load_relational_data import load_all_data

# -----------------------
# Constants
# -----------------------
MAX_SCORE = 100
MIN_SCORE = 0

# -----------------------
# Health scoring functions
# -----------------------
def calculate_device_health(device: Device, events: List[Event]) -> float:
    """Compute a simple health score for a device based on its events."""
    func_name = "calculate_device_health"
    if not events:
        return MAX_SCORE
    total_events = len(events)
    failure_events = sum(1 for e in events if e.event_type.lower() in ["error", "failure", "down"])
    health_score = MAX_SCORE - (failure_events / total_events * MAX_SCORE)
    logger.debug(f"{func_name} | Device {device.device_id}: {failure_events}/{total_events} failure events")
    return max(MIN_SCORE, min(MAX_SCORE, health_score))


def calculate_interface_health(interface: Interface, events: List[Event]) -> float:
    """Compute a simple health score for an interface based on its events."""
    func_name = "calculate_interface_health"
    if not events:
        return MAX_SCORE
    total_events = len(events)
    down_events = sum(1 for e in events if e.event_type.lower() in ["down", "link_down", "error"])
    health_score = MAX_SCORE - (down_events / total_events * MAX_SCORE)
    logger.debug(f"{func_name} | Interface {interface.interface_id}: {down_events}/{total_events} down events")
    return max(MIN_SCORE, min(MAX_SCORE, health_score))


def score_all_devices(devices: Dict[int, Device], events: Dict[int, Event]) -> Dict[int, float]:
    """Compute health scores for all devices."""
    func_name = "score_all_devices"
    device_scores = {}
    device_events_map: Dict[int, List[Event]] = {}
    for e in events.values():
        device_events_map.setdefault(e.device.device_id, []).append(e)

    for device_id, device in devices.items():
        device_scores[device_id] = calculate_device_health(device, device_events_map.get(device_id, []))
    logger.info(f"{func_name} | Scored {len(device_scores)} devices")
    return device_scores


def score_all_interfaces(interfaces: Dict[int, Interface], events: Dict[int, Event]) -> Dict[int, float]:
    """Compute health scores for all interfaces."""
    func_name = "score_all_interfaces"
    interface_scores = {}
    interface_events_map: Dict[int, List[Event]] = {}
    for e in events.values():
        if e.interface:
            interface_events_map.setdefault(e.interface.interface_id, []).append(e)

    for interface_id, interface in interfaces.items():
        interface_scores[interface_id] = calculate_interface_health(
            interface, interface_events_map.get(interface_id, [])
        )
    logger.info(f"{func_name} | Scored {len(interface_scores)} interfaces")
    return interface_scores


def print_health_summary(
    device_scores: Dict[int, float],
    interface_scores: Dict[int, float],
    devices: Dict[int, Device],
    interfaces: Dict[int, Interface]
):
    """Log a summary of health scores."""
    func_name = "print_health_summary"
    avg_device_health = sum(device_scores.values()) / len(device_scores) if device_scores else 0
    avg_interface_health = sum(interface_scores.values()) / len(interface_scores) if interface_scores else 0

    logger.info(f"{func_name} | Devices scored: {len(device_scores)} | Avg health: {avg_device_health:.2f}")
    logger.info(f"{func_name} | Interfaces scored: {len(interface_scores)} | Avg health: {avg_interface_health:.2f}")

    logger.info(f"{func_name} | Top 5 lowest device health:")
    for device_id in sorted(device_scores, key=device_scores.get)[:5]:
        d = devices[device_id]
        logger.info(f"{func_name} | Device {d.device_id} ({d.device_ip}): Health {device_scores[device_id]:.2f}")

    logger.info(f"{func_name} | Top 5 lowest interface health:")
    for interface_id in sorted(interface_scores, key=interface_scores.get)[:5]:
        i = interfaces[interface_id]
        logger.info(f"{func_name} | Interface {i.interface_id} ({i.interface_name}): Health {interface_scores[interface_id]:.2f}")


# -----------------------
# Main execution
# -----------------------
if __name__ == "__main__":
    logger.info("Starting health scoring pipeline...")

    # Load all relational data
    db = load_all_data()
    devices = db.get("devices", {})
    interfaces = db.get("interfaces", {})
    events = db.get("events", {})

    # Compute health scores
    device_scores = score_all_devices(devices, events)
    interface_scores = score_all_interfaces(interfaces, events)

    # Log summary
    print_health_summary(device_scores, interface_scores, devices, interfaces)

    logger.info("Health scoring pipeline complete.")