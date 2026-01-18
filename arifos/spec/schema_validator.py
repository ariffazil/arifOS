"""
arifos_core.spec.schema_validator - Minimal JSON Schema Validator

LIGHTWEIGHT validator for v44 spec files (Track B authority enforcement).
Does NOT require jsonschema dependency.

Validates:
- Required fields exist
- Type correctness (string, number, boolean, object, array)
- Enum values (if specified)
- String patterns (basic regex matching)
- Const values (exact matches)

Usage:
    validator = MinimalSchemaValidator(schema_dict)
    errors = validator.validate(data_dict)
    if errors:
        raise ValueError(f"Schema validation failed: {errors}")
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class ValidationError:
    """Single validation error with path context."""

    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message

    def __str__(self):
        return f"{self.path}: {self.message}"

    def __repr__(self):
        return f"ValidationError({self.path!r}, {self.message!r})"


class MinimalSchemaValidator:
    """
    Minimal JSON Schema validator (no external deps).

    Supports:
    - type checking (string, number, boolean, object, array, integer)
    - required fields
    - enum values
    - const values
    - pattern matching (basic regex)
    - minLength, maxLength
    - minimum, maximum
    - minItems, maxItems
    - $ref (simple definitions resolution)
    - additionalProperties: false
    """

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.definitions = schema.get("definitions", {})

    def validate(self, data: Any, schema: Optional[Dict[str, Any]] = None, path: str = "$") -> List[ValidationError]:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema: Schema to validate against (defaults to root schema)
            path: Current JSON path (for error reporting)

        Returns:
            List of ValidationError objects (empty if valid)
        """
        if schema is None:
            schema = self.schema

        errors: List[ValidationError] = []

        # Resolve $ref if present
        if "$ref" in schema:
            schema = self._resolve_ref(schema["$ref"])

        # Type checking
        expected_type = schema.get("type")
        if expected_type:
            if not self._check_type(data, expected_type):
                errors.append(ValidationError(path, f"Expected type {expected_type}, got {type(data).__name__}"))
                return errors  # Stop validation if type is wrong

        # Const checking (exact value match)
        if "const" in schema:
            if data != schema["const"]:
                errors.append(ValidationError(path, f"Expected const value {schema['const']!r}, got {data!r}"))

        # Enum checking
        if "enum" in schema:
            if data not in schema["enum"]:
                errors.append(ValidationError(path, f"Value {data!r} not in enum {schema['enum']}"))

        # String validations
        if isinstance(data, str):
            errors.extend(self._validate_string(data, schema, path))

        # Number validations
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            errors.extend(self._validate_number(data, schema, path))

        # Object validations
        if isinstance(data, dict):
            errors.extend(self._validate_object(data, schema, path))

        # Array validations
        if isinstance(data, list):
            errors.extend(self._validate_array(data, schema, path))

        return errors

    def _check_type(self, data: Any, expected_type: str) -> bool:
        """Check if data matches expected JSON schema type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "object": dict,
            "array": list,
            "null": type(None),
        }

        # Special case: integer must not match boolean
        if expected_type == "integer":
            return isinstance(data, int) and not isinstance(data, bool)

        # Special case: number must not match boolean
        if expected_type == "number":
            return isinstance(data, (int, float)) and not isinstance(data, bool)

        expected = type_map.get(expected_type)
        if expected is None:
            return True  # Unknown type, skip check

        return isinstance(data, expected)

    def _validate_string(self, data: str, schema: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate string-specific constraints."""
        errors: List[ValidationError] = []

        # Pattern (regex)
        if "pattern" in schema:
            pattern = schema["pattern"]
            if not re.match(pattern, data):
                errors.append(ValidationError(path, f"String {data!r} does not match pattern {pattern!r}"))

        # minLength
        if "minLength" in schema:
            min_len = schema["minLength"]
            if len(data) < min_len:
                errors.append(ValidationError(path, f"String length {len(data)} < minLength {min_len}"))

        # maxLength
        if "maxLength" in schema:
            max_len = schema["maxLength"]
            if len(data) > max_len:
                errors.append(ValidationError(path, f"String length {len(data)} > maxLength {max_len}"))

        # format (basic URI check)
        if schema.get("format") == "uri":
            if not (data.startswith("http://") or data.startswith("https://")):
                errors.append(ValidationError(path, f"String {data!r} is not a valid URI"))

        return errors

    def _validate_number(self, data: float, schema: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate number-specific constraints."""
        errors: List[ValidationError] = []

        # minimum
        if "minimum" in schema:
            minimum = schema["minimum"]
            if data < minimum:
                errors.append(ValidationError(path, f"Number {data} < minimum {minimum}"))

        # maximum
        if "maximum" in schema:
            maximum = schema["maximum"]
            if data > maximum:
                errors.append(ValidationError(path, f"Number {data} > maximum {maximum}"))

        return errors

    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate object-specific constraints."""
        errors: List[ValidationError] = []

        # Required fields
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(ValidationError(path, f"Required field '{field}' missing"))

        # Properties
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                prop_schema = properties[key]
                errors.extend(self.validate(value, prop_schema, f"{path}.{key}"))

        # additionalProperties: false
        if schema.get("additionalProperties") is False:
            allowed_keys = set(properties.keys())
            actual_keys = set(data.keys())
            extra_keys = actual_keys - allowed_keys
            if extra_keys:
                errors.append(ValidationError(path, f"Additional properties not allowed: {sorted(extra_keys)}"))

        return errors

    def _validate_array(self, data: List[Any], schema: Dict[str, Any], path: str) -> List[ValidationError]:
        """Validate array-specific constraints."""
        errors: List[ValidationError] = []

        # minItems
        if "minItems" in schema:
            min_items = schema["minItems"]
            if len(data) < min_items:
                errors.append(ValidationError(path, f"Array length {len(data)} < minItems {min_items}"))

        # maxItems
        if "maxItems" in schema:
            max_items = schema["maxItems"]
            if len(data) > max_items:
                errors.append(ValidationError(path, f"Array length {len(data)} > maxItems {max_items}"))

        # items (schema for array elements)
        if "items" in schema:
            item_schema = schema["items"]
            for i, item in enumerate(data):
                errors.extend(self.validate(item, item_schema, f"{path}[{i}]"))

        return errors

    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        """Resolve $ref to schema definition."""
        # Only handle simple #/definitions/xxx refs
        if ref.startswith("#/definitions/"):
            def_name = ref.split("/")[-1]
            if def_name in self.definitions:
                return self.definitions[def_name]
            else:
                raise ValueError(f"Undefined $ref: {ref}")
        else:
            raise ValueError(f"Unsupported $ref format: {ref}")


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Load JSON schema from file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_spec_against_schema(
    spec_data: Dict[str, Any],
    schema_path: Path,
    allow_legacy: bool = False
) -> None:
    """
    Validate spec data against JSON schema.

    Args:
        spec_data: Spec dictionary to validate
        schema_path: Path to JSON schema file
        allow_legacy: If True, skip all validation (legacy fallback mode)

    Raises:
        RuntimeError: If validation fails (fail-closed)
    """
    # Legacy mode: skip all validation
    if allow_legacy:
        return

    # Check if schema exists
    if not schema_path.exists():
        # Fail-closed: schema must exist
        raise RuntimeError(
            f"TRACK B AUTHORITY FAILURE: Schema file not found: {schema_path}. "
            f"Schema validation is required. Set ARIFOS_ALLOW_LEGACY_SPEC=1 to disable (NOT RECOMMENDED)."
        )

    # Load schema
    try:
        schema = load_schema(schema_path)
    except Exception as e:
        raise RuntimeError(f"TRACK B AUTHORITY FAILURE: Failed to load schema {schema_path}: {e}")

    # Validate
    validator = MinimalSchemaValidator(schema)
    errors = validator.validate(spec_data)

    if errors:
        error_summary = "\n".join(f"  - {err}" for err in errors)
        raise RuntimeError(
            f"TRACK B AUTHORITY FAILURE: Spec validation failed against schema {schema_path.name}.\n"
            f"Validation errors:\n{error_summary}\n"
            f"Spec version: {spec_data.get('version', 'UNKNOWN')}\n"
            f"Fix spec or set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass (NOT RECOMMENDED)."
        )

    # Validation passed - attach schema marker
    spec_data["_schema_used"] = str(schema_path)
