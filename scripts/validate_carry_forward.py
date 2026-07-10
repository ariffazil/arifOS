#!/usr/bin/env python3
"""
validate_carry_forward.py — Schema validator for carry_forward.json
Uses Python stdlib only (json + re + datetime) — no external deps.

Usage:
    python3 validate_carry_forward.py [--file <path>]

Exit codes:
    0  = valid
    1  = invalid (print violations)
    2  = file not found or read error
    3  = schema not found
"""

import json
import sys
import re
import datetime
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "carry_forward.schema.json"


def read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"[VALIDATE ERROR] Cannot read {path}: {e}", file=sys.stderr)
        return None


def validate_string(val, schema_prop, path, errors):
    """Validate a string field against schema constraints."""
    if schema_prop.get("format") == "date-time":
        try:
            datetime.datetime.fromisoformat(val.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{path}: invalid datetime format '{val}'")
    elif schema_prop.get("format") == "date":
        try:
            datetime.date.fromisoformat(val)
        except ValueError:
            errors.append(f"{path}: invalid date format '{val}'")
    elif schema_prop.get("type") == "string":
        if "minLength" in schema_prop and len(val) < schema_prop["minLength"]:
            errors.append(f"{path}: too short (min {schema_prop['minLength']}, got {len(val)})")
        if "maxLength" in schema_prop and len(val) > schema_prop["maxLength"]:
            errors.append(f"{path}: too long (max {schema_prop['maxLength']}, got {len(val)})")
        if "pattern" in schema_prop and not re.match(schema_prop["pattern"], val):
            errors.append(f"{path}: pattern mismatch '{val}' !~ {schema_prop['pattern']}")
        if "enum" in schema_prop and val not in schema_prop["enum"]:
            errors.append(f"{path}: '{val}' not in {schema_prop['enum']}")


def validate_object(val, schema_prop, path, errors, depth=0):
    """Recursively validate an object."""
    if not isinstance(val, dict):
        errors.append(f"{path}: expected object, got {type(val).__name__}")
        return

    if depth > 0 and "required" in schema_prop:
        for req in schema_prop["required"]:
            if req not in val:
                errors.append(f"{path}: missing required field '{req}'")

    if "additionalProperties" in schema_prop and not schema_prop["additionalProperties"]:
        schema_keys = set()
        for prop_name, prop_schema in schema_prop.get("properties", {}).items():
            schema_keys.add(prop_name)
            if prop_schema.get("type") == "object":
                schema_keys.update(
                    k for k in prop_schema.get("properties", {}).keys()
                )
        extra = set(val.keys()) - schema_keys
        if extra:
            errors.append(f"{path}: additional properties not allowed: {extra}")

    for key, val2 in val.items():
        prop_schema = schema_prop.get("properties", {}).get(key)
        if prop_schema is None:
            continue  # additionalProperties: true — skip
        validate_value(val2, prop_schema, f"{path}.{key}", errors, depth + 1)


def validate_array(val, schema_prop, path, errors, depth):
    """Recursively validate an array."""
    if not isinstance(val, list):
        errors.append(f"{path}: expected array, got {type(val).__name__}")
        return

    items_schema = schema_prop.get("items")
    if items_schema:
        for i, item in enumerate(val):
            validate_value(item, items_schema, f"{path}[{i}]", errors, depth + 1)


def validate_value(val, schema_prop, path, errors, depth=0):
    """Validate a value against a schema property definition."""
    # Handle oneOf — try all branches; only error if none match
    if "oneOf" in schema_prop:
        branch_errors = []
        for sub_schema in schema_prop["oneOf"]:
            be = []
            validate_value(val, sub_schema, path, be, depth)
            if not be:
                return  # Matched — no errors, done
            branch_errors.append(be)
        # None matched
        errors.append(
            f"{path}: no oneOf variant matched. "
            f"Errors per branch: {len(branch_errors)} branches tried."
        )
        return

    # Type check
    expected = schema_prop.get("type")
    if expected == "string" and not isinstance(val, str):
        errors.append(f"{path}: expected string, got {type(val).__name__}")
        return
    elif expected == "integer" and not isinstance(val, int):
        errors.append(f"{path}: expected integer, got {type(val).__name__}")
        return
    elif expected == "boolean" and not isinstance(val, bool):
        errors.append(f"{path}: expected boolean, got {type(val).__name__}")
        return
    elif expected == "object" and not isinstance(val, dict):
        errors.append(f"{path}: expected object, got {type(val).__name__}")
        return
    elif expected == "array" and not isinstance(val, list):
        errors.append(f"{path}: expected array, got {type(val).__name__}")
        return
    elif expected == "null" and val is not None:
        errors.append(f"{path}: expected null, got {type(val).__name__}")
        return

    # Type-specific validation
    if expected == "string":
        validate_string(val, schema_prop, path, errors)
    elif expected == "integer":
        if "const" in schema_prop and val != schema_prop["const"]:
            errors.append(f"{path}: must be {schema_prop['const']}, got {val}")
    elif expected == "object":
        validate_object(val, schema_prop, path, errors, depth)
    elif expected == "array":
        validate_array(val, schema_prop, path, errors, depth)


def typeof(val) -> str:
    if val is None: return "null"
    if isinstance(val, bool): return "boolean"
    if isinstance(val, int): return "integer"
    if isinstance(val, float): return "number"
    if isinstance(val, str): return "string"
    if isinstance(val, list): return "array"
    if isinstance(val, dict): return "object"
    return "unknown"


def validate(data: dict, schema: dict) -> list[str]:
    errors = []
    # Check schema_version
    if "schema_version" in schema.get("required", []):
        schema_version = schema["properties"]["schema_version"]["const"]
        if data.get("schema_version") != schema_version:
            errors.append(
                f"schema_version: expected {schema_version}, got {data.get('schema_version')}"
            )
    # Check required top-level fields
    for req in schema.get("required", []):
        if req not in data:
            errors.append(f"root: missing required field '{req}'")
    # Validate properties
    if "properties" in schema:
        for key, val in data.items():
            if key in schema["properties"]:
                validate_value(val, schema["properties"][key], key, errors)
    return errors


def main():
    # Determine file path
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        cf_path = Path(sys.argv[2])
    else:
        cf_path = Path("/root/.local/share/arifos/carry_forward.json")

    schema_path = SCHEMA_PATH

    # Load
    schema = read_json(schema_path)
    if schema is None:
        print(f"[VALIDATE] Schema not found at {schema_path} — cannot validate", file=sys.stderr)
        sys.exit(3)

    data = read_json(cf_path)
    if data is None:
        sys.exit(2)

    # Validate
    errors = validate(data, schema)

    if errors:
        print(f"[CARRY_FORWARD INVALID] {len(errors)} violation(s):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"[CARRY_FORWARD VALID] Schema v{data.get('schema_version')} OK — no violations")
        sys.exit(0)


if __name__ == "__main__":
    main()
