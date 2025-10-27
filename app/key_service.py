"""Key generation and rotation service

This module handles the business logic for key generation, rotation, and management.
It enforces the business rule that a maximum of 2 keys can be active per client.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from app.config import MAX_ACTIVE_KEYS_PER_CLIENT
from app.crypto import encrypt_secret, generate_secret_key
from app.database import db
from app.models import CreateKeyResponse, KeyRecord, KeyStatus

logger = logging.getLogger(__name__)


def create_key(
    client_id: str,
    key_alias: str,
    created_by: str,
    expiration_date: Optional[datetime] = None,
) -> CreateKeyResponse:
    """Create a new secret key for a client with automatic rotation logic.

    This function implements the key rotation policy: a maximum of 2 active keys
    are allowed per client. When creating a new key, if there are already 2 active
    keys, the oldest one will be automatically deactivated.

    Args:
        client_id: Client identifier (e.g., MLM_PROD, MLCES_PROD)
        key_alias: Human-readable key name
        created_by: User creating the key
        expiration_date: Optional expiration date for the key

    Returns:
        CreateKeyResponse containing the new key details and plaintext secret

    """
    logger.info(
        "Creating new key for client",
        extra={
            "client_id": client_id,
            "key_alias": key_alias,
            "created_by": created_by,
            "expiration_date": expiration_date,
        },
    )

    # Get current active keys for this client
    active_keys = db.get_active_keys(client_id)
    logger.debug(
        "Retrieved active keys for client",
        extra={"client_id": client_id, "active_key_count": len(active_keys)},
    )

    if len(active_keys) > 2:
        # Deactivate the oldest active key
        oldest_key = min(active_keys, key=lambda k: k.created_at)
        logger.warning(
            "Too many active keys, deactivating oldest key",
            extra={
                "client_id": client_id,
                "active_key_count": len(active_keys),
                "oldest_key_id": oldest_key.id,
                "oldest_key_alias": oldest_key.key_alias,
                "oldest_key_created_at": oldest_key.created_at,
            },
        )
        db.deactivate_key(oldest_key.id)
        logger.info(
            "Deactivated oldest key",
            extra={"client_id": client_id, "deactivated_key_id": oldest_key.id},
        )

    # Generate new secret key
    logger.debug("Generating new secret key")
    plaintext_secret = generate_secret_key()
    encrypted = encrypt_secret(plaintext_secret)
    logger.debug(
        "Secret key generated and encrypted",
        extra={
            "client_id": client_id,
            "encrypted": encrypted,
        },
    )

    # Create key record
    key_record = KeyRecord(
        id=str(uuid.uuid4()),
        client_id=client_id,
        key_alias=key_alias,
        encrypted_secret=encrypted,
        status=KeyStatus.ACTIVE,
        expiration_date=expiration_date,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )

    # Save to database
    logger.debug("Saving key record to database", extra={"key_id": key_record.id})
    db.add_key(key_record)
    logger.info(
        "Key created successfully",
        extra={
            "key_id": key_record.id,
            "client_id": client_id,
            "key_alias": key_alias,
        },
    )

    # Return response with plaintext secret (only shown once!)
    return CreateKeyResponse(
        id=key_record.id,
        client_id=key_record.client_id,
        key_alias=key_record.key_alias,
        plaintext_secret=plaintext_secret,
        status=key_record.status,
        created_at=key_record.created_at,
    )


def get_key_status(key_id: str) -> Optional[KeyRecord]:
    """Get the status of a specific key.

    Args:
        key_id: The unique key identifier

    Returns:
        KeyRecord if found, None otherwise
    """
    logger.debug("Retrieving key status", extra={"key_id": key_id})
    key_record = db.get_key_by_id(key_id)
    if key_record:
        logger.info(
            "Key found",
            extra={"key_id": key_id, "status": key_record.status},
        )
    else:
        logger.warning("Key not found", extra={"key_id": key_id})
    return key_record


def deactivate_key(key_id: str) -> Optional[KeyRecord]:
    """Manually deactivate a key.

    Args:
        key_id: The unique key identifier

    Returns:
        Updated KeyRecord if found, None otherwise
    """
    logger.info("Deactivating key", extra={"key_id": key_id})
    key_record = db.deactivate_key(key_id)
    if key_record:
        logger.info(
            "Key deactivated successfully",
            extra={"key_id": key_id, "status": key_record.status},
        )
    else:
        logger.warning(
            "Failed to deactivate key - key not found", extra={"key_id": key_id}
        )
    return key_record


def list_keys_for_client(client_id: str) -> list[KeyRecord]:
    """List all keys for a specific client.

    Args:
        client_id: The client identifier

    Returns:
        List of KeyRecord objects
    """
    logger.debug("Listing keys for client", extra={"client_id": client_id})
    keys = db.get_keys_by_client(client_id)
    logger.info(
        "Retrieved keys for client",
        extra={"client_id": client_id, "key_count": len(keys)},
    )
    return keys


def get_active_key_count(client_id: str) -> int:
    """Get the count of active keys for a client.

    This is useful for monitoring and verification.

    Args:
        client_id: The client identifier

    Returns:
        Number of active keys
    """
    logger.debug("Getting active key count for client", extra={"client_id": client_id})
    active_keys = db.get_active_keys(client_id)
    count = len(active_keys)
    logger.info(
        "Active key count retrieved",
        extra={"client_id": client_id, "active_key_count": count},
    )
    return count
