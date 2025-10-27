"""Tests for cryptography module"""

import pytest

from app.crypto import (
    compare_secrets,
    decrypt_secret,
    derive_encryption_key,
    encrypt_secret,
    generate_secret_key,
)


def test_generate_secret_key():
    """Test that secret keys are generated correctly"""
    key1 = generate_secret_key()
    key2 = generate_secret_key()

    # Keys should be strings
    assert isinstance(key1, str)
    assert isinstance(key2, str)

    # Keys should be different (random)
    assert key1 != key2

    # Keys should be base64 encoded (proper length)
    assert len(key1) > 40


def test_encrypt_decrypt_roundtrip():
    """Test that encryption and decryption work correctly"""
    plaintext = "test-secret-key-12345"

    # Encrypt
    encrypted = encrypt_secret(plaintext)
    assert encrypted != plaintext
    assert isinstance(encrypted, str)

    # Decrypt
    decrypted = decrypt_secret(encrypted)
    assert decrypted == plaintext


def test_compare_secrets_valid():
    """Test comparing a plaintext secret with its encrypted version"""
    plaintext = generate_secret_key()
    encrypted = encrypt_secret(plaintext)

    # Should match
    assert compare_secrets(plaintext, encrypted) is True


def test_compare_secrets_invalid():
    """Test that mismatched secrets return False"""
    plaintext1 = generate_secret_key()
    plaintext2 = generate_secret_key()
    encrypted1 = encrypt_secret(plaintext1)

    # Should not match
    assert compare_secrets(plaintext2, encrypted1) is False


def test_decrypt_invalid_token():
    """Test that decrypting invalid data raises an error"""
    with pytest.raises(ValueError):
        decrypt_secret("invalid-encrypted-data")
