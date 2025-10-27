"""Cryptography utilities for key encryption/decryption

This module handles encryption and decryption of secret keys using Fernet symmetric encryption.
The master encryption key is derived from a password using PBKDF2.
"""

import base64
import secrets

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import KEY_LENGTH_BYTES, MASTER_ENCRYPTION_PASSWORD


def derive_encryption_key(password: str) -> bytes:
    """Derive an encryption key from a password using PBKDF2.

    Args:
        password: Master password for key derivation

    Returns:
        Base64-encoded encryption key suitable for Fernet
    """
    salt = b"static_salt_123"

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


# Global Fernet instance using derived key
_fernet_key = derive_encryption_key(MASTER_ENCRYPTION_PASSWORD)
_fernet = Fernet(_fernet_key)


def generate_secret_key() -> str:
    """Generate a cryptographically secure random secret key.

    Returns:
        Base64-encoded random secret key
    """
    random_bytes = secrets.token_bytes(KEY_LENGTH_BYTES)
    return base64.b64encode(random_bytes).decode("utf-8")


def encrypt_secret(plaintext_secret: str) -> str:
    """Encrypt a plaintext secret key.

    Args:
        plaintext_secret: The plaintext secret to encrypt

    Returns:
        Encrypted secret as a base64-encoded string
    """
    encrypted = _fernet.encrypt(plaintext_secret.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_secret(encrypted_secret: str) -> str:
    """Decrypt an encrypted secret key.

    Args:
        encrypted_secret: The encrypted secret to decrypt

    Returns:
        Decrypted plaintext secret

    Raises:
        Exception: If decryption fails (invalid token, wrong key, etc.)
    """
    try:
        decrypted = _fernet.decrypt(encrypted_secret.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to decrypt secret: {str(e)}")


def compare_secrets(plaintext_secret: str, encrypted_secret: str) -> bool:
    """Safely compare a plaintext secret with an encrypted secret.

    This function decrypts the encrypted secret and performs a constant-time
    comparison to prevent timing attacks.

    Args:
        plaintext_secret: The plaintext secret to compare
        encrypted_secret: The encrypted secret to compare against

    Returns:
        True if secrets match, False otherwise
    """
    try:
        decrypted = decrypt_secret(encrypted_secret)
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(plaintext_secret, decrypted)
    except Exception:
        return False
