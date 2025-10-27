"""Key validation service

This module handles the validation of incoming secret keys from LOS clients.
It verifies that the provided key exists, is active, and matches the stored value.
"""

from typing import Dict

from app.crypto import compare_secrets, encrypt_secret
from app.database import db
from app.models import KeyStatus


def validate_key(client_id: str, secret_key: str) -> Dict:
    """Validate an incoming secret key from a client.

    This function checks if the provided secret key is valid for the given client.
    It performs the following checks:
    1. Encrypts the provided secret and looks it up in the database
    2. Verifies the key belongs to the specified client
    3. Checks if the key status is Active

    Args:
        client_id: The client identifier
        secret_key: The plaintext secret key to validate

    Returns:
        Dictionary with validation result:
        - valid (bool): Whether the key is valid
        - message (str): Success or error message
        - error (str, optional): Error details if validation fails
        - debug_info (str, optional): Debug information

    """
    try:
        # Get all keys for this client
        client_keys = db.get_keys_by_client(client_id)

        # Find matching key by decrypting and comparing
        key_record = None
        for key in client_keys:
            if compare_secrets(secret_key, key.encrypted_secret):
                key_record = key
                break

        if not key_record:
            return {
                "valid": False,
                "message": "Key validation failed",
                "error": "Key not found for this client",
            }

        # Check if key status is Active
        if key_record.status != KeyStatus.ACTIVE:
            return {
                "valid": False,
                "message": "Key validation failed",
                "error": f"Key is {key_record.status.value}",
                "debug_info": f"Key: {key_record.encrypted_secret}",
            }

        # Check if key is expired
        if key_record.expiration_date:
            from datetime import datetime

            # Ensure expiration_date is a datetime object
            exp_date = key_record.expiration_date
            if isinstance(exp_date, str):
                # Parse as offset-naive datetime by removing timezone info
                exp_date = datetime.fromisoformat(
                    exp_date.replace("Z", "").replace("+00:00", "")
                )
            elif hasattr(exp_date, "tzinfo") and exp_date.tzinfo is not None:
                # Convert offset-aware to offset-naive
                exp_date = exp_date.replace(tzinfo=None)

            if datetime.utcnow() > exp_date:
                return {
                    "valid": False,
                    "message": "Key validation failed",
                    "error": "Key has expired",
                }

        # All checks passed
        return {
            "valid": True,
            "message": "Key validation successful",
            "debug_info": f"Key: {key_record.encrypted_secret}",
        }

    except Exception as e:
        return {
            "valid": False,
            "message": "Key validation failed",
            "error": f"Internal error: {str(e)}",
        }


def validate_key_secure(client_id: str, secret_key: str) -> bool:
    """Simplified secure validation that only returns True/False.

    This is an alternative validation method that doesn't leak any information.

    Args:
        client_id: The client identifier
        secret_key: The plaintext secret key to validate

    Returns:
        True if key is valid and active, False otherwise
    """
    result = validate_key(client_id, secret_key)
    return result.get("valid", False)
