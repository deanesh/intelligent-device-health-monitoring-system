# src/transformation/load_relational_data.py

import sys
from pathlib import Path
import csv
from datetime import datetime
from typing import Dict

# -----------------------
# Repo root and paths
# -----------------------
REPO_ROOT = Path(__file__).resolve().parents[2]  # repo root
SRC_PATH = REPO_ROOT / "src"
TRANS_PATH = SRC_PATH / "transformation"

sys.path.append(str(SRC_PATH))
sys.path.append(str(TRANS_PATH))
sys.path.append(str(REPO_ROOT))

# -----------------------
# Imports
# -----------------------
from src.utils.logger import get_logger
from transformation.relational_model import Organization, Asset, DeviceClass, Device, Interface, Event

# -----------------------
# Logger setup
# -----------------------
logger = get_logger("load_relational_data")  # logs go to logs/pipeline.log with rollover

# -----------------------
# Data directory
# -----------------------
DATA_DIR = REPO_ROOT / "data" / "raw"


def clean_row(row: dict) -> dict:
    """Strip whitespace from keys and values."""
    return {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}


def load_organizations() -> Dict[int, Organization]:
    file = DATA_DIR / "organization" / "organization.csv"
    organizations = {}
    logger.info("Loading organizations from: %s", file)
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            org = Organization(
                organization_id=int(row.get("organization_id") or 0),
                org_name=row.get("name") or row.get("org_name") or "",
                org_industry=row.get("industry") or row.get("org_industry") or "",
                org_address=row.get("address") or row.get("org_address") or "",
                org_email=row.get("contact_email") or row.get("org_email") or "",
                org_phone=row.get("contact_phone") or row.get("org_phone") or ""
            )
            organizations[org.organization_id] = org
    return organizations


def load_device_classes() -> Dict[int, DeviceClass]:
    file = DATA_DIR / "device_class" / "device_class.csv"
    device_classes = {}
    logger.info("Loading device_classes from: %s", file)
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            dc = DeviceClass(
                device_class_id=int(row.get("device_class_id") or 0),
                device_class_name=row.get("device_class_name") or row.get("name") or "",
                device_class_description=row.get("device_class_description") or row.get("description") or ""
            )
            device_classes[dc.device_class_id] = dc
    return device_classes


def load_assets(organizations: Dict[int, Organization]) -> Dict[int, Asset]:
    file = DATA_DIR / "asset" / "assets.csv"
    assets = {}
    logger.info("Loading assets from: %s", file)

    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        for row in reader:
            row = clean_row(row)

            org_id = int(row.get("organization_id") or 0)
            org = organizations.get(org_id)

            # Correct column mapping
            asset_name = row.get("name", "")
            asset_location = row.get("location", "")
            asset_owner = row.get("owner", "")
            purchase_raw = row.get("purchase_date", "")

            asset_purchase_date = None
            if purchase_raw:
                try:
                    asset_purchase_date = datetime.strptime(
                        purchase_raw, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    logger.warning(
                        "Invalid date format for asset_id %s: %s",
                        row.get("asset_id"),
                        purchase_raw
                    )

            asset = Asset(
                asset_id=int(row.get("asset_id") or 0),
                asset_name=asset_name,
                organization=org,
                asset_location=asset_location,
                asset_purchase_date=asset_purchase_date,
                asset_owner=asset_owner
            )

            assets[asset.asset_id] = asset

    return assets


def load_devices(assets: Dict[int, Asset], device_classes: Dict[int, DeviceClass]) -> Dict[int, Device]:
    file = DATA_DIR / "device" / "devices.csv"
    devices = {}
    logger.info("Loading devices from: %s", file)
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            asset_id = int(row.get("asset_id") or 0)
            device_class_id = int(row.get("device_class_id") or 0)
            device = Device(
                device_id=int(row.get("device_id") or 0),
                device_ip=row.get("device_ip") or "",
                asset=assets.get(asset_id),
                device_class=device_classes.get(device_class_id),
                device_serial=row.get("device_serial") or "",
                device_manufacturer=row.get("device_manufacturer") or ""
            )
            devices[device.device_id] = device
    return devices


def load_interfaces(devices: Dict[int, Device]) -> Dict[int, Interface]:
    file = DATA_DIR / "interface" / "interfaces.csv"
    interfaces = {}
    logger.info("Loading interfaces from: %s", file)
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            device_id = int(row.get("device_id") or 0)
            interface = Interface(
                interface_id=int(row.get("interface_id") or 0),
                interface_name=row.get("interface_name") or "",
                device=devices.get(device_id),
                interface_status=row.get("interface_status") or "",
                interface_mac=row.get("interface_mac") or ""
            )
            interfaces[interface.interface_id] = interface
    return interfaces


def load_events(devices: Dict[int, Device], interfaces: Dict[int, Interface]) -> Dict[int, Event]:
    file = DATA_DIR / "event" / "events.csv"
    events = {}
    logger.info("Loading events from: %s", file)
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            device_id = int(row.get("device_id") or 0)
            interface_id = row.get("interface_id")
            device = devices.get(device_id)
            interface = interfaces.get(int(interface_id)) if interface_id else None
            timestamp_str = row.get("event_timestamp") or row.get("timestamp") or ""
            try:
                # Handle ISO 8601 with T or space
                if "T" in timestamp_str:
                    event_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
                else:
                    event_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid timestamp for event_id %s: %s",
                    row.get("event_id"), timestamp_str
                )
                event_timestamp = datetime.now()
            event = Event(
                event_id=int(row.get("event_id") or 0),
                event_timestamp=event_timestamp,
                device=device,
                interface=interface,
                event_type=row.get("event_type") or "",
                event_description=row.get("event_description") or ""
            )
            events[event.event_id] = event
    return events


def load_all_data():
    organizations = load_organizations()
    device_classes = load_device_classes()
    assets = load_assets(organizations)
    devices = load_devices(assets, device_classes)
    interfaces = load_interfaces(devices)
    events = load_events(devices, interfaces)

    logger.info("Loaded %d organizations", len(organizations))
    logger.info("Loaded %d device_classes", len(device_classes))
    logger.info("Loaded %d assets", len(assets))
    logger.info("Loaded %d devices", len(devices))
    logger.info("Loaded %d interfaces", len(interfaces))
    logger.info("Loaded %d events", len(events))

    return {
        "organizations": organizations,
        "device_classes": device_classes,
        "assets": assets,
        "devices": devices,
        "interfaces": interfaces,
        "events": events
    }


if __name__ == "__main__":
    db = load_all_data()