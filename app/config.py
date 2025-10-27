"""Configuration settings for the LOS Key Validation Service"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "keys.json"))

# Encryption settings
MASTER_ENCRYPTION_PASSWORD = os.getenv(
    "MASTER_ENCRYPTION_PASSWORD", "los-master-key-2025-secure-password"
)

# Key generation settings
KEY_LENGTH_BYTES = 32  # 256-bit keys
MAX_ACTIVE_KEYS_PER_CLIENT = 2

# API settings
API_TITLE = "LOS Inbound Key Validation Service"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
Backend service for managing and validating LOS inbound secret keys.

Supports:
- Key generation with encryption
- Key rotation with max 2 active keys per client
- Secure key validation
"""
