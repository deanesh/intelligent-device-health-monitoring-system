"""
Data Ingestion Module
Author: Deanesh Takkallapati
Purpose: Load CSVs for entities, rename columns, and provide unified logging
"""

import os
import pandas as pd
from typing import Dict
from utils.logger import get_logger

logger = get_logger("Data_Ingestion")

# Schema mapping for entity columns
ENTITY_MAPPINGS = {
    "organization": {
        "organization_id": "organization_id",
        "name": "org_name",
        "industry": "org_industry",
        "address": "org_address",
        "contact_email": "org_email",
        "contact_phone": "org_phone"
    },
    "asset": {
        "asset_id": "asset_id",
        "name": "asset_name",
        "organization_id": "organization_id",
        "location": "asset_location",
        "purchase_date": "asset_purchase_date",
        "owner": "asset_owner"
    },
    "device_class": {
        "device_class_id": "device_class_id",
        "name": "device_class_name",
        "description": "device_class_description"
    },
    "device": {
        "device_id": "device_id",
        "ip_address": "device_ip",
        "asset_id": "asset_id",
        "device_class_id": "device_class_id",
        "serial_number": "device_serial",
        "manufacturer": "device_manufacturer"
    },
    "interface": {
        "interface_id": "interface_id",
        "name": "interface_name",
        "status": "interface_status",
        "device_id": "device_id",
        "mac_address": "interface_mac"
    },
    "event": {
        "event_id": "event_id",
        "timestamp": "event_timestamp",
        "device_id": "device_id",
        "interface_id": "interface_id",
        "event_type": "event_type",
        "description": "event_description"
    }
}

def load_entities(base_path: str) -> Dict[str, pd.DataFrame]:
    """
    Load all entity CSVs and rename columns according to ENTITY_MAPPINGS.
    Returns a dictionary of DataFrames keyed by entity name.
    """
    entity_files = {
        "organization": "organization/organization.csv",
        "asset": "asset/assets.csv",
        "device_class": "device_class/device_class.csv",
        "device": "device/devices.csv",
        "interface": "interface/interfaces.csv",
        "event": "event/events.csv"
    }

    data_frames = {}
    for entity, rel_path in entity_files.items():
        path = os.path.join(base_path, rel_path)
        if not os.path.exists(path):
            logger.warning(f"{entity} CSV missing: {path}")
            continue
        try:
            df = pd.read_csv(path)
            if entity in ENTITY_MAPPINGS:
                df = df.rename(columns=ENTITY_MAPPINGS[entity])
                df = df[list(ENTITY_MAPPINGS[entity].values())]  # reorder columns
            data_frames[entity] = df
            logger.info(f"{entity.upper()} loaded [rows={df.shape[0]}|cols={df.shape[1]}]")
            logger.info(f"columns={list(df.columns)}")
        except Exception as e:
            logger.error(f"Failed to load {entity}: {e}")
    return data_frames