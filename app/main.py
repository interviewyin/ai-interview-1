"""FastAPI main application for LOS Key Validation Service

This module defines the REST API endpoints for key management and validation.
"""

import logging
from typing import List

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import API_DESCRIPTION, API_TITLE, API_VERSION
from app.key_service import (
    create_key,
    deactivate_key,
    get_active_key_count,
    get_key_status,
    list_keys_for_client,
)
from app.logging_config import setup_logging
from app.models import (
    CreateKeyRequest,
    CreateKeyResponse,
    DeactivateKeyResponse,
    KeyRecord,
    KeyStatusResponse,
    ValidateKeyRequest,
    ValidateKeyResponse,
)
from app.validation_service import validate_key

# Configure logging
setup_logging(level=logging.DEBUG)

# Initialize FastAPI app
app = FastAPI(title=API_TITLE, version=API_VERSION, description=API_DESCRIPTION)


@app.get("/")
def read_root():
    """Root endpoint with API debugging information"""
    return {
        "service": "LOS Inbound Key Validation Service",
        "version": API_VERSION,
        "status": "operational",
        "endpoints": {"docs": "/docs", "health": "/health"},
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "los-key-validation"}


@app.post(
    "/keys/generate",
    response_model=CreateKeyResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_key(request: CreateKeyRequest):
    """Generate a new secret key for a client.

    This endpoint creates a new secret key with automatic rotation logic.
    If the client already has 2 active keys, the oldest one will be deactivated.

    **IMPORTANT**: The plaintext_secret is only returned once and cannot be retrieved again.
    Store it securely!

    Args:
        request: CreateKeyRequest with client_id, key_alias, and created_by

    Returns:
        CreateKeyResponse with the new key details and plaintext secret
    """
    try:
        response = create_key(
            client_id=request.client_id,
            key_alias=request.key_alias,
            created_by=request.created_by,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create key: {str(e)}",
        )


@app.get("/keys/{client_id}", response_model=List[KeyStatusResponse])
def get_client_keys(client_id: str):
    """Get all keys for a specific client.

    Args:
        client_id: The client identifier (e.g., MLM_PROD)

    Returns:
        List of key records for the client
    """
    try:
        keys = list_keys_for_client(client_id)
        return [
            KeyStatusResponse(
                id=key.id,
                client_id=key.client_id,
                key_alias=key.key_alias,
                status=key.status,
                created_at=key.created_at,
                expiration_date=key.expiration_date,
                deactivated_at=key.deactivated_at,
            )
            for key in keys
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve keys: {str(e)}",
        )


@app.get("/keys/{client_id}/active-count")
def get_active_count(client_id: str):
    """Get the count of active keys for a client.

    This endpoint is useful for monitoring and verification.

    Args:
        client_id: The client identifier

    Returns:
        Count of active keys
    """
    try:
        count = get_active_key_count(client_id)
        return {"client_id": client_id, "active_key_count": count, "max_allowed": 2}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active key count: {str(e)}",
        )


@app.get("/keys/status/{key_id}", response_model=KeyStatusResponse)
def get_key_status_endpoint(key_id: str):
    """Get the status of a specific key by its ID.

    Args:
        key_id: The unique key identifier

    Returns:
        Key status information

    Raises:
        404: If key not found
    """
    key = get_key_status(key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key with ID {key_id} not found",
        )

    return KeyStatusResponse(
        id=key.id,
        client_id=key.client_id,
        key_alias=key.key_alias,
        status=key.status,
        created_at=key.created_at,
        expiration_date=key.expiration_date,
        deactivated_at=key.deactivated_at,
    )


@app.post("/keys/{key_id}/deactivate", response_model=DeactivateKeyResponse)
def deactivate_key_endpoint(key_id: str):
    """Manually deactivate a key.

    Args:
        key_id: The unique key identifier

    Returns:
        Deactivation confirmation

    Raises:
        404: If key not found
    """
    key = deactivate_key(key_id)
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Key with ID {key_id} not found",
        )

    return DeactivateKeyResponse(
        id=key.id,
        status=key.status,
        deactivated_at=key.deactivated_at,
        message=f"Key {key_id} has been deactivated",
    )


@app.post("/keys/validate", response_model=ValidateKeyResponse)
def validate_key_endpoint(request: ValidateKeyRequest):
    """Validate an incoming secret key.

    This is the main endpoint used by LOS clients to validate their keys.
    It checks if the key exists, is active, and belongs to the specified client.

    Args:
        request: ValidateKeyRequest with client_id and secret_key

    Returns:
        ValidateKeyResponse with validation result

    """
    try:
        result = validate_key(request.client_id, request.secret_key)
        return ValidateKeyResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
