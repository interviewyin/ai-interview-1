"""Pydantic models for the LOS Key Validation Service"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class KeyStatus(str, Enum):
    """Key status enumeration"""

    ACTIVE = "Active"
    PENDING_DEACTIVATION = "Pending Deactivation"
    INACTIVE = "Inactive"


class KeyRecord(BaseModel):
    """Database model for a key record"""

    id: str = Field(..., description="Unique identifier for the key")
    client_id: str = Field(
        ..., description="Client identifier (e.g., MLM_PROD, MLCES_PROD)"
    )
    key_alias: str = Field(..., description="Human-readable key name")
    encrypted_secret: str = Field(..., description="Encrypted secret key")
    status: KeyStatus = Field(default=KeyStatus.ACTIVE, description="Key status")
    expiration_date: Optional[datetime] = Field(
        None, description="Optional expiration date"
    )
    created_by: str = Field(..., description="User who created the key")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    deactivated_at: Optional[datetime] = Field(
        None, description="Deactivation timestamp"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class CreateKeyRequest(BaseModel):
    """Request model for creating a new key"""

    client_id: str = Field(..., description="Client identifier", example="MLM_PROD")
    key_alias: str = Field(
        ..., description="Human-readable key name", example="MLM Prod Key 2025-Q3"
    )
    created_by: str = Field(..., description="User creating the key", example="admin")


class CreateKeyResponse(BaseModel):
    """Response model for key creation"""

    id: str
    client_id: str
    key_alias: str
    plaintext_secret: str = Field(
        ..., description="WARNING: Store this securely! It will not be shown again."
    )
    status: KeyStatus
    created_at: datetime
    message: str = "Key created successfully. Store the plaintext_secret securely - it cannot be retrieved again."


class ValidateKeyRequest(BaseModel):
    """Request model for key validation"""

    client_id: str = Field(..., description="Client identifier")
    secret_key: str = Field(..., description="Secret key to validate")


class ValidateKeyResponse(BaseModel):
    """Response model for key validation"""

    valid: bool
    message: str
    error: Optional[str] = None
    debug_info: Optional[str] = None


class KeyStatusResponse(BaseModel):
    """Response model for key status check"""

    id: str
    client_id: str
    key_alias: str
    status: KeyStatus
    created_at: datetime
    expiration_date: Optional[datetime]
    deactivated_at: Optional[datetime]


class DeactivateKeyResponse(BaseModel):
    """Response model for key deactivation"""

    id: str
    status: KeyStatus
    deactivated_at: datetime
    message: str
