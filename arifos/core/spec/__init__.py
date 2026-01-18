"""
arifos_core.spec - Specification validation and loading

This package provides schema validation and cryptographic manifest verification
for v44 Track B specs. Moved here from utils/ to avoid circular import chains.
"""

from .schema_validator import (
    MinimalSchemaValidator,
    ValidationError,
    load_schema,
    validate_spec_against_schema,
)

from .manifest_verifier import (
    compute_sha256,
    load_manifest,
    verify_file_hash,
    verify_manifest,
)

__all__ = [
    "MinimalSchemaValidator",
    "ValidationError",
    "load_schema",
    "validate_spec_against_schema",
    "compute_sha256",
    "load_manifest",
    "verify_file_hash",
    "verify_manifest",
]
