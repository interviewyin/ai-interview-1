"""Tests for key service module"""

import os
import tempfile
from datetime import datetime

import pytest

from app import database
from app.database import KeyDatabase
from app.key_service import (
    create_key,
    deactivate_key,
    get_active_key_count,
    get_key_status,
    list_keys_for_client,
)
from app.models import KeyStatus


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    # Replace the global db instance
    original_db = database.db
    database.db = KeyDatabase(path)

    yield database.db

    # Cleanup
    database.db = original_db
    os.unlink(path)


def test_create_key(temp_db):
    """Test creating a new key"""
    response = create_key(
        client_id="TEST_CLIENT", key_alias="Test Key 1", created_by="test_user"
    )

    assert response.client_id == "TEST_CLIENT"
    assert response.key_alias == "Test Key 1"
    assert response.plaintext_secret is not None
    assert response.status == KeyStatus.ACTIVE
    assert len(response.plaintext_secret) > 40  # Should be base64 encoded


def test_deactivate_key(temp_db):
    """Test manually deactivating a key"""
    # Create a key
    key = create_key("CLIENT_DEACTIVATE", "Key 1", "admin")

    # Deactivate it
    deactivated = deactivate_key(key.id)

    assert deactivated is not None
    assert deactivated.status == KeyStatus.INACTIVE
    assert deactivated.deactivated_at is not None


def test_get_key_status_not_found(temp_db):
    """Test getting status of non-existent key"""
    status = get_key_status("non-existent-id")
    assert status is None
