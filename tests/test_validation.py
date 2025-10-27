"""Tests for validation service"""

import os
import tempfile

import pytest

from app import database
from app.database import KeyDatabase
from app.key_service import create_key
from app.validation_service import validate_key, validate_key_secure


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    original_db = database.db
    database.db = KeyDatabase(path)

    yield database.db

    database.db = original_db
    os.unlink(path)


def test_validate_active_key(temp_db):
    """Test validating an active key"""
    # Create a key
    response = create_key("CLIENT_VALID", "Key 1", "admin")

    # Validate with the plaintext secret
    result = validate_key("CLIENT_VALID", response.plaintext_secret)

    print(f"DEBUG: result = {result}")

    assert result["valid"] is True
    assert result["message"] == "Key validation successful"
    assert "error" not in result or result["error"] is None


def test_validate_wrong_secret(temp_db):
    """Test validating with wrong secret"""
    # Create a key
    create_key("CLIENT_WRONG", "Key 1", "admin")

    # Try to validate with wrong secret
    result = validate_key("CLIENT_WRONG", "wrong-secret-key")

    assert result["valid"] is False
    assert "error" in result


def test_validate_key_wrong_client(temp_db):
    """Test validating a key with wrong client_id"""
    response = create_key("CLIENT_A", "Key 1", "admin")

    # Try to validate with different client_id
    result = validate_key("CLIENT_B", response.plaintext_secret)

    assert result["valid"] is False


def test_validate_key_secure_method(temp_db):
    """Test the secure validation method (only returns boolean)"""
    # Create a key
    response = create_key("CLIENT_SECURE_METHOD", "Key 1", "admin")

    # Validate with secure method
    is_valid = validate_key_secure("CLIENT_SECURE_METHOD", response.plaintext_secret)

    assert is_valid is True

    # Test with wrong secret
    is_valid = validate_key_secure("CLIENT_SECURE_METHOD", "wrong-secret")
    assert is_valid is False


def test_validate_expired_key(temp_db):
    """Test validating an expired key"""
    from datetime import datetime, timedelta

    from app.key_service import create_key as create_key_func

    # Create a key with expiration in the past directly
    expiration_date = datetime.utcnow() - timedelta(days=1)

    # Import and call the function directly with expiration
    import sys

    sys.path.insert(0, str(__file__ + "/../../"))
    from app import key_service

    response = key_service.create_key(
        client_id="CLIENT_EXPIRED",
        key_alias="Expired Key",
        created_by="admin",
        expiration_date=expiration_date,
    )

    # Try to validate
    result = validate_key("CLIENT_EXPIRED", response.plaintext_secret)

    assert result["valid"] is False
    assert "expired" in result["error"].lower()
