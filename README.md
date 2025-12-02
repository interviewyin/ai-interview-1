# Inbound Key Management Service

A secure backend service for managing and validating inbound secret keys with support for key rotation.

## Overview

This service provides:
- Secure key generation and storage with encryption
- Key rotation with automatic management (max 2 active keys per client)
- Fast key validation for incoming requests
- REST API for key management

## Project Structure

```
ai-interview-1/
├── app/
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration settings
│   ├── models.py              # Pydantic data models
│   ├── crypto.py              # Encryption/decryption utilities
│   ├── database.py            # JSON file database operations
│   ├── key_service.py         # Key generation and rotation logic
│   ├── validation_service.py  # Key validation logic
│   ├── logging_config.py      # Logging configuration
│   └── main.py                # FastAPI application
├── data/
│   ├── keys.json              # Key database (generated)
│   └── plaintext_secrets.txt  # Test secrets (generated)
├── docs/
│   └── CHALLENGE.md           # Challenge documentation
├── tests/
│   ├── __init__.py
│   ├── test_crypto.py         # Crypto module tests
│   ├── test_key_service.py    # Key service tests
│   └── test_validation.py     # Validation service tests
├── .gitignore                 # Git ignore rules
├── pyproject.toml             # Python project configuration (uv)
├── requirements.txt           # Python dependencies
├── uv.lock                    # UV lock file
├── generate_sample_data.py    # Sample data generator script
└── README.md                  # This file
```

## Generate sample data

   ```bash
   uv run python generate_sample_data.py
   ```

   This creates:
   - `data/keys.json` - Sample key database
   - `data/plaintext_secrets.txt` - Plaintext secrets for testing

## Running FastAPI Server

To run the FastAPI server, use the following command:
```bash
uv run fastapi dev app/main.py
```

## Running Tests

Run the test suite:
```bash
pytest tests/ -v
```

## API Endpoints

### Key Management

- `POST /keys/generate` - Generate a new key for a client
- `GET /keys/{client_id}` - List all keys for a client
- `GET /keys/{client_id}/active-count` - Get count of active keys
- `GET /keys/status/{key_id}` - Get status of a specific key
- `POST /keys/{key_id}/deactivate` - Deactivate a key

### Key Validation

- `POST /keys/validate` - Validate an incoming secret key

### Health & Info

- `GET /` - Service information
- `GET /health` - Health check

## Example Usage

### Generate a New Key

```bash
curl -X POST "http://localhost:8000/keys/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "MLM_PROD",
    "key_alias": "MLM Prod Key 2025-Q3",
    "created_by": "admin"
  }'
```

Response:
```json
{
  "id": "uuid-here",
  "client_id": "MLM_PROD",
  "key_alias": "MLM Prod Key 2025-Q3",
  "plaintext_secret": "base64-encoded-secret",
  "status": "Active",
  "created_at": "2025-01-15T10:00:00",
  "message": "Key created successfully. Store the plaintext_secret securely - it cannot be retrieved again."
}
```

**IMPORTANT**: The `plaintext_secret` is only shown once. Store it securely!

### Validate a Key

```bash
curl -X POST "http://localhost:8000/keys/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "MLM_PROD",
    "secret_key": "your-plaintext-secret-here"
  }'
```

Response (Success):
```json
{
  "valid": true,
  "message": "Key validation successful"
}
```

Response (Failure):
```json
{
  "valid": false,
  "message": "Key validation failed",
  "error": "Key is Inactive",
  "debug_info": "Key prefix: gAAAAABl..."
}
```

## Configuration

Environment variables can be set to customize the service:

- `DATABASE_PATH` - Path to the JSON database file (default: `./data/keys.json`)
- `MASTER_ENCRYPTION_PASSWORD` - Master password for key derivation (default provided)

## Sample Data

The `generate_sample_data.py` script creates:

- **MLM_PROD**: 2 active keys, 1 inactive key
- **MLCES_PROD**: 1 active key
- **MLCWS_PROD**: 1 pending deactivation key, 1 expired key

Use `data/plaintext_secrets.txt` to test validation with these keys.