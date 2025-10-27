# Inbound Key Validation Service

## User Story & Requirements

**User Story**: As a Backend Service, I need a dedicated, secure system to generate, store, and manage multiple active Secret Keys per environment, so that we can support key rotation without disrupting production traffic.

**Key Requirements**:

1. **Key Rotation**: The system must enforce that for any given client, there can be a maximum of 2 keys with the status of "Active" or "Pending Deactivation" at any time.

2. **Secure Validation**: The validation service must only return validation success/failure, never expose key material or sensitive information in responses.

3. **Encryption**: Keys must be encrypted at rest using strong encryption. AES-256 is required for compliance.