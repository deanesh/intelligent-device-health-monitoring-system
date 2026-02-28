# relational_model.py

from datetime import datetime, date
from typing import List, Optional


class Organization:
    def __init__(self, organization_id: int, org_name: str, org_industry: str = "",
                 org_address: str = "", org_email: str = "", org_phone: str = "",
                 org_country: str = ""):  # <-- added country
        self.organization_id = organization_id
        self.org_name = org_name
        self.org_industry = org_industry
        self.org_address = org_address
        self.org_email = org_email
        self.org_phone = org_phone
        self.org_country = org_country  # store country
        self.assets: List["Asset"] = []

    def add_asset(self, asset: "Asset"):
        self.assets.append(asset)


class Asset:
    def __init__(self, asset_id: int, asset_name: str, organization: Organization,
                 asset_location: str = "", asset_purchase_date: Optional[date] = None,
                 asset_owner: str = ""):
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.organization = organization
        self.asset_location = asset_location
        self.asset_purchase_date = asset_purchase_date
        self.asset_owner = asset_owner
        self.devices: List["Device"] = []

        # Link asset to organization
        organization.add_asset(self)

    def add_device(self, device: "Device"):
        self.devices.append(device)


class DeviceClass:
    def __init__(self, device_class_id: int, device_class_name: str,
                 device_class_description: str = ""):
        self.device_class_id = device_class_id
        self.device_class_name = device_class_name
        self.device_class_description = device_class_description
        self.devices: List["Device"] = []

    def add_device(self, device: "Device"):
        self.devices.append(device)


class Device:
    def __init__(self, device_id: int, device_ip: str, asset: Asset,
                 device_class: Optional[DeviceClass] = None,  # <-- make optional
                 device_serial: str = "",
                 device_manufacturer: str = ""):
        self.device_id = device_id
        self.device_ip = device_ip
        self.asset = asset
        self.device_class = device_class  # can be None if missing
        self.device_serial = device_serial
        self.device_manufacturer = device_manufacturer
        self.interfaces: List["Interface"] = []
        self.events: List["Event"] = []

        # Link device to asset
        asset.add_device(self)
        # Link to device class if exists
        if device_class is not None:
            device_class.add_device(self)

    def add_interface(self, interface: "Interface"):
        self.interfaces.append(interface)

    def add_event(self, event: "Event"):
        self.events.append(event)


class Interface:
    def __init__(self, interface_id: int, interface_name: str, device: Device,
                 interface_status: str = "", interface_mac: str = ""):
        self.interface_id = interface_id
        self.interface_name = interface_name
        self.device = device
        self.interface_status = interface_status
        self.interface_mac = interface_mac
        self.events: List["Event"] = []

        # Link interface to device
        device.add_interface(self)

    def add_event(self, event: "Event"):
        self.events.append(event)


class Event:
    def __init__(self, event_id: int, event_timestamp: datetime, device: Device,
                 interface: Optional[Interface] = None, event_type: str = "",
                 event_description: str = ""):
        self.event_id = event_id
        self.event_timestamp = event_timestamp
        self.device = device
        self.interface = interface
        self.event_type = event_type
        self.event_description = event_description

        # Link event to device and interface
        device.add_event(self)
        if interface:
            interface.add_event(self)