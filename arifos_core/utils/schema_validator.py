"""
arifos_core.utils.schema_validator - BACKWARD COMPATIBILITY SHIM

This module has been moved to arifos_core.spec.schema_validator to avoid
circular import issues (utils imports eye which imports metrics).

This shim maintains backward compatibility for any code that imports from
the old location.
"""

# Re-export from new location (no circular import since spec/ is independent)
from arifos_core.spec.schema_validator import (
    MinimalSchemaValidator,
    ValidationError,
    load_schema,
    validate_spec_against_schema,
)

__all__ = [
    "MinimalSchemaValidator",
    "ValidationError",
    "load_schema",
    "validate_spec_against_schema",
]
