# src/health/health_scoring.py

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add repo root to sys.path so transformation modules can be imported
REPO_ROOT = Path(__file__).parents[1].parent  # intelligent-device-health/
sys.path.append(str(REPO_ROOT / "src"))       # src/

from transformation.relational_model import Device, Interface, Event
from transformation.load_relational_data import load_all_data

# Constants for health scoring
MAX_SCORE = 100
MIN_SCORE = 0


def calculate_device_health(device: Device, events: List[Event]) -> float:
    """Compute a simple health score for a device based on its events."""
    if not events:
        return MAX_SCORE
    total_events = len(events)
    failure_events = sum(1 for e in events if e.event_type.lower() in ["error", "failure", "down"])
    health_score = MAX_SCORE - (failure_events / total_events * MAX_SCORE)
    return max(MIN_SCORE, min(MAX_SCORE, health_score))


def calculate_interface_health(interface: Interface, events: List[Event]) -> float:
    """Compute a simple health score for an interface based on its events."""
    if not events:
        return MAX_SCORE
    total_events = len(events)
    down_events = sum(1 for e in events if e.event_type.lower() in ["down", "link_down", "error"])
    health_score = MAX_SCORE - (down_events / total_events * MAX_SCORE)
    return max(MIN_SCORE, min(MAX_SCORE, health_score))


def score_all_devices(devices: Dict[int, Device], events: Dict[int, Event]) -> Dict[int, float]:
    """Compute health scores for all devices."""
    device_scores = {}
    device_events_map: Dict[int, List[Event]] = {}
    for e in events.values():
        device_events_map.setdefault(e.device.device_id, []).append(e)

    for device_id, device in devices.items():
        device_scores[device_id] = calculate_device_health(device, device_events_map.get(device_id, []))
    return device_scores


def score_all_interfaces(interfaces: Dict[int, Interface], events: Dict[int, Event]) -> Dict[int, float]:
    """Compute health scores for all interfaces."""
    interface_scores = {}
    interface_events_map: Dict[int, List[Event]] = {}
    for e in events.values():
        if e.interface:
            interface_events_map.setdefault(e.interface.interface_id, []).append(e)

    for interface_id, interface in interfaces.items():
        interface_scores[interface_id] = calculate_interface_health(
            interface, interface_events_map.get(interface_id, [])
        )
    return interface_scores


def print_health_summary(
    device_scores: Dict[int, float],
    interface_scores: Dict[int, float],
    devices: Dict[int, Device],
    interfaces: Dict[int, Interface]
):
    """Print a simple summary of health scores."""
    avg_device_health = sum(device_scores.values()) / len(device_scores) if device_scores else 0
    avg_interface_health = sum(interface_scores.values()) / len(interface_scores) if interface_scores else 0

    print(f"=== Health Summary ===")
    print(f"Devices scored: {len(device_scores)} | Average health: {avg_device_health:.2f}")
    print(f"Interfaces scored: {len(interface_scores)} | Average health: {avg_interface_health:.2f}")

    print("\nTop 5 lowest device health:")
    for device_id in sorted(device_scores, key=device_scores.get)[:5]:
        d = devices[device_id]
        print(f"Device {d.device_id} ({d.device_ip}): Health {device_scores[device_id]:.2f}")

    print("\nTop 5 lowest interface health:")
    for interface_id in sorted(interface_scores, key=interface_scores.get)[:5]:
        i = interfaces[interface_id]
        print(f"Interface {i.interface_id} ({i.interface_name}): Health {interface_scores[interface_id]:.2f}")


if __name__ == "__main__":
    # Load all relational data
    db = load_all_data()
    devices = db["devices"]
    interfaces = db["interfaces"]
    events = db["events"]

    # Compute health scores
    device_scores = score_all_devices(devices, events)
    interface_scores = score_all_interfaces(interfaces, events)

    # Print summary
    print_health_summary(device_scores, interface_scores, devices, interfaces)