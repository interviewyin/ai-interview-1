"""Script to generate sample data for the database

Run this script to populate the keys.json file with sample data.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.crypto import encrypt_secret, generate_secret_key
from app.models import KeyStatus


def generate_sample_data():
    """Generate sample key data"""

    # Generate some sample keys
    keys = []

    # MLM_PROD: 2 active keys
    mlm_key1_plain = generate_secret_key()
    mlm_key1 = {
        "id": "mlm-prod-key-001",
        "client_id": "MLM_PROD",
        "key_alias": "MLM Prod Key 2025-Q1",
        "encrypted_secret": encrypt_secret(mlm_key1_plain),
        "status": KeyStatus.ACTIVE.value,
        "expiration_date": (datetime.utcnow() + timedelta(days=90)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z",
        "deactivated_at": None,
    }
    keys.append(mlm_key1)

    mlm_key2_plain = generate_secret_key()
    mlm_key2 = {
        "id": "mlm-prod-key-002",
        "client_id": "MLM_PROD",
        "key_alias": "MLM Prod Key 2025-Q2",
        "encrypted_secret": encrypt_secret(mlm_key2_plain),
        "status": KeyStatus.ACTIVE.value,
        "expiration_date": (datetime.utcnow() + timedelta(days=180)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
        "deactivated_at": None,
    }
    keys.append(mlm_key2)

    # MLM_PROD: 1 inactive key
    mlm_key3_plain = generate_secret_key()
    mlm_key3 = {
        "id": "mlm-prod-key-003-inactive",
        "client_id": "MLM_PROD",
        "key_alias": "MLM Prod Key 2024-Q4 (Deactivated)",
        "encrypted_secret": encrypt_secret(mlm_key3_plain),
        "status": KeyStatus.INACTIVE.value,
        "expiration_date": (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=120)).isoformat() + "Z",
        "deactivated_at": (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z",
    }
    keys.append(mlm_key3)

    # MLCES_PROD: 1 active key
    mlces_key1_plain = generate_secret_key()
    mlces_key1 = {
        "id": "mlces-prod-key-001",
        "client_id": "MLCES_PROD",
        "key_alias": "MLCES Prod Key 2025-Q1",
        "encrypted_secret": encrypt_secret(mlces_key1_plain),
        "status": KeyStatus.ACTIVE.value,
        "expiration_date": (datetime.utcnow() + timedelta(days=90)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat() + "Z",
        "deactivated_at": None,
    }
    keys.append(mlces_key1)

    # MLCWS_PROD: 1 active key with pending deactivation
    mlcws_key1_plain = generate_secret_key()
    mlcws_key1 = {
        "id": "mlcws-prod-key-001",
        "client_id": "MLCWS_PROD",
        "key_alias": "MLCWS Prod Key 2025-Q1",
        "encrypted_secret": encrypt_secret(mlcws_key1_plain),
        "status": KeyStatus.PENDING_DEACTIVATION.value,
        "expiration_date": (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat() + "Z",
        "deactivated_at": None,
    }
    keys.append(mlcws_key1)

    # MLCWS_PROD: 1 expired inactive key
    mlcws_key2_plain = generate_secret_key()
    mlcws_key2 = {
        "id": "mlcws-prod-key-002-expired",
        "client_id": "MLCWS_PROD",
        "key_alias": "MLCWS Prod Key 2024-Q3 (Expired)",
        "encrypted_secret": encrypt_secret(mlcws_key2_plain),
        "status": KeyStatus.INACTIVE.value,
        "expiration_date": (datetime.utcnow() - timedelta(days=60)).isoformat() + "Z",
        "created_by": "admin",
        "created_at": (datetime.utcnow() - timedelta(days=150)).isoformat() + "Z",
        "deactivated_at": (datetime.utcnow() - timedelta(days=60)).isoformat() + "Z",
    }
    keys.append(mlcws_key2)

    # Create the database structure
    data = {"keys": keys}

    # Write to file
    output_path = Path(__file__).parent / "data" / "keys.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Sample data generated successfully at {output_path}")
    print(f"\nGenerated {len(keys)} keys:")
    print(f"  - MLM_PROD: 2 active, 1 inactive")
    print(f"  - MLCES_PROD: 1 active")
    print(f"  - MLCWS_PROD: 1 pending deactivation, 1 expired")

    # Save plaintext secrets for testing
    secrets_file = Path(__file__).parent / "data" / "plaintext_secrets.txt"
    with open(secrets_file, "w") as f:
        f.write("# Plaintext secrets for testing (DO NOT COMMIT IN PRODUCTION!)\n\n")
        f.write(f"MLM_PROD Active Key 1: {mlm_key1_plain}\n")
        f.write(f"MLM_PROD Active Key 2: {mlm_key2_plain}\n")
        f.write(f"MLM_PROD Inactive Key: {mlm_key3_plain}\n")
        f.write(f"MLCES_PROD Active Key: {mlces_key1_plain}\n")
        f.write(f"MLCWS_PROD Pending Key: {mlcws_key1_plain}\n")
        f.write(f"MLCWS_PROD Expired Key: {mlcws_key2_plain}\n")

    print(f"\nPlaintext secrets saved to {secrets_file} for testing purposes")


if __name__ == "__main__":
    generate_sample_data()
