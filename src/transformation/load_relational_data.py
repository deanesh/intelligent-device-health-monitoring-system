# src/transformation/load_relational_data.py

import sys
from pathlib import Path
import csv
from datetime import datetime
from typing import Dict

# Add src and repo root to sys.path so imports work
sys.path.append(str(Path(__file__).parents[0]))  # src/transformation
sys.path.append(str(Path(__file__).parents[1]))  # src

from transformation.relational_model import Organization, Asset, DeviceClass, Device, Interface, Event

# Correct DATA_DIR pointing to repo root
REPO_ROOT = Path(__file__).parents[1].parent  # intelligent-device-health/
DATA_DIR = REPO_ROOT / "data" / "raw"


def clean_row(row: dict) -> dict:
    """Strip whitespace from keys and values."""
    return {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}


def load_organizations() -> Dict[int, Organization]:
    file = DATA_DIR / "organization" / "organization.csv"
    organizations = {}
    print(f"Loading organizations from: {file}")
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
    print(f"Loading device_classes from: {file}")
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
    print(f"Loading assets from: {file}")
    with open(file, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]
        for row in reader:
            row = clean_row(row)
            org_id = int(row.get("organization_id") or 0)
            org = organizations.get(org_id)
            asset_purchase_date = None
            if row.get("asset_purchase_date"):
                try:
                    asset_purchase_date = datetime.strptime(row["asset_purchase_date"], "%Y-%m-%d").date()
                except ValueError:
                    pass
            asset = Asset(
                asset_id=int(row.get("asset_id") or 0),
                asset_name=row.get("asset_name") or "",
                organization=org,
                asset_location=row.get("asset_location") or "",
                asset_purchase_date=asset_purchase_date,
                asset_owner=row.get("asset_owner") or ""
            )
            assets[asset.asset_id] = asset
    return assets


def load_devices(assets: Dict[int, Asset], device_classes: Dict[int, DeviceClass]) -> Dict[int, Device]:
    file = DATA_DIR / "device" / "devices.csv"
    devices = {}
    print(f"Loading devices from: {file}")
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
    print(f"Loading interfaces from: {file}")
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
    print(f"Loading events from: {file}")
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
                event_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
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
    print(f"Loaded {len(db['organizations'])} organizations")
    print(f"Loaded {len(db['assets'])} assets")
    print(f"Loaded {len(db['device_classes'])} device_classes")
    print(f"Loaded {len(db['devices'])} devices")
    print(f"Loaded {len(db['interfaces'])} interfaces")
    print(f"Loaded {len(db['events'])} events")