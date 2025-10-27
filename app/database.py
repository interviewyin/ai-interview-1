"""Database operations for the LOS Key Validation Service

This module provides a simple JSON file-based database for storing key records.
In production, this would be replaced with a real database (PostgreSQL, MongoDB, etc.)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from app.config import DATABASE_PATH
from app.models import KeyRecord, KeyStatus


class KeyDatabase:
    """Simple JSON file-based database for key records"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Ensure the database file exists with proper structure"""
        if not os.path.exists(self.db_path):
            # Create parent directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            # Initialize empty database
            self._write_data({"keys": []})
        elif os.path.getsize(self.db_path) == 0:
            # File exists but is empty, initialize it
            self._write_data({"keys": []})

    def _read_data(self) -> Dict:
        """Read the entire database"""
        with open(self.db_path, "r") as f:
            return json.load(f)

    def _write_data(self, data: Dict):
        """Write the entire database"""
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def add_key(self, key_record: KeyRecord) -> KeyRecord:
        """Add a new key record to the database

        Args:
            key_record: The key record to add

        Returns:
            The added key record
        """
        data = self._read_data()
        # Convert to dict for JSON serialization
        key_dict = key_record.model_dump(mode="json")
        data["keys"].append(key_dict)
        self._write_data(data)
        return key_record

    def get_key_by_id(self, key_id: str) -> Optional[KeyRecord]:
        """Get a key record by its ID

        Args:
            key_id: The unique key identifier

        Returns:
            The key record if found, None otherwise
        """
        data = self._read_data()
        for key_dict in data["keys"]:
            if key_dict["id"] == key_id:
                return KeyRecord(**key_dict)
        return None

    def get_keys_by_client(self, client_id: str) -> List[KeyRecord]:
        """Get all key records for a specific client

        Args:
            client_id: The client identifier

        Returns:
            List of key records for the client
        """
        data = self._read_data()
        keys = []
        for key_dict in data["keys"]:
            if key_dict["client_id"] == client_id:
                keys.append(KeyRecord(**key_dict))
        return keys

    def get_active_keys(self, client_id: str) -> List[KeyRecord]:
        """Get all active keys for a specific client

        Args:
            client_id: The client identifier

        Returns:
            List of active key records
        """
        all_keys = self.get_keys_by_client(client_id)
        return [
            key
            for key in all_keys
            if key.status in [KeyStatus.ACTIVE, KeyStatus.PENDING_DEACTIVATION]
        ]

    def update_key(self, key_id: str, updates: Dict) -> Optional[KeyRecord]:
        """Update a key record

        Args:
            key_id: The unique key identifier
            updates: Dictionary of fields to update

        Returns:
            Updated key record if found, None otherwise
        """
        data = self._read_data()
        for i, key_dict in enumerate(data["keys"]):
            if key_dict["id"] == key_id:
                # Update fields
                key_dict.update(updates)
                data["keys"][i] = key_dict
                self._write_data(data)
                return KeyRecord(**key_dict)
        return None

    def deactivate_key(self, key_id: str) -> Optional[KeyRecord]:
        """Deactivate a key

        Args:
            key_id: The unique key identifier

        Returns:
            Updated key record if found, None otherwise
        """
        updates = {
            "status": KeyStatus.INACTIVE.value,
            "deactivated_at": datetime.utcnow().isoformat(),
        }
        return self.update_key(key_id, updates)

    def find_key_by_encrypted_secret(
        self, client_id: str, encrypted_secret: str
    ) -> Optional[KeyRecord]:
        """Find a key by its encrypted secret value

        Args:
            client_id: The client identifier
            encrypted_secret: The encrypted secret to search for

        Returns:
            The matching key record if found, None otherwise
        """
        keys = self.get_keys_by_client(client_id)
        for key in keys:
            if key.encrypted_secret == encrypted_secret:
                return key
        return None

    def get_all_keys(self) -> List[KeyRecord]:
        """Get all key records in the database

        Returns:
            List of all key records
        """
        data = self._read_data()
        return [KeyRecord(**key_dict) for key_dict in data["keys"]]


# Global database instance
db = KeyDatabase()
