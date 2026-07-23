#!/usr/bin/env python3
"""
Federation ABI Validator — v1.0.0

Structural validation (JSON Schema) + Semantic validation (runtime checks).
Usage:
    python scripts/validate_federation_abi.py                          # validate all fixtures
    python scripts/validate_federation_abi.py --schema-only            # schema syntax only
    python scripts/validate_federation_abi.py --fixture <path>         # single fixture
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "contracts" / "schemas"
FIXTURES_DIR = ROOT / "contracts" / "fixtures"

SCHEMA_FILES = {
    "request": SCHEMAS_DIR / "federation-request.v1.schema.json",
    "response": SCHEMAS_DIR / "federation-response.v1.schema.json",
    "error": SCHEMAS_DIR / "federation-error.v1.schema.json",
    "receipt": SCHEMAS_DIR / "federation-receipt.v1.schema.json",
}

# Fixtures expected to FAIL structural validation
NEGATIVE_FIXTURES = {
    "missing-session-invalid.json": "SESSION_MISSING",
    "expired-authority-invalid.json": "DEADLINE_EXCEEDED",
    "duplicate-execution-invalid.json": "IDEMPOTENCY_CONFLICT",
}

EXIT_OK = 0
EXIT_FAIL = 1


def load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def validate_schema_syntax() -> list[str]:
    """Validate all schemas are valid JSON Schema documents."""
    errors: list[str] = []
    for name, path in SCHEMA_FILES.items():
        if not path.exists():
            errors.append(f"MISSING: {name} schema at {path}")
            continue
        try:
            schema = load_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            print(f"  ✅ {name}: valid JSON Schema 2020-12")
        except Exception as e:
            errors.append(f"  ❌ {name}: {e}")
    return errors


def validate_schema_ids() -> list[str]:
    """Validate $id fields are consistent with filenames and version."""
    errors: list[str] = []
    version = None
    for name, path in SCHEMA_FILES.items():
        schema = load_json(path)
        sid = schema.get("$id", "")
        sv = schema.get("properties", {}).get("schema_version", {}).get("const")
        if not sv:
            errors.append(f"  ❌ {name}: missing schema_version const")
            continue
        if version is None:
            version = sv
        elif sv != version:
            errors.append(f"  ❌ {name}: version mismatch — {sv} != {version}")
        print(f"  ✅ {name}: $id={sid} version={sv}")
    return errors


def validate_fixture(fixture_path: Path, schema: dict[str, Any] | Path) -> tuple[bool, str]:
    """Structural (JSON Schema) validation of a single fixture."""
    if isinstance(schema, Path):
        schema = load_json(schema)
    instance = load_json(fixture_path)
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(instance))
    if errors:
        return False, "; ".join(str(e.message) for e in errors)
    return True, "PASS"


def semantic_check_deadline(instance: dict) -> str | None:
    """Semantic: deadline_at must be in the future."""
    deadline = instance.get("deadline_at")
    if deadline:
        try:
            dt = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            if dt < datetime.now(timezone.utc):
                return "DEADLINE_EXCEEDED: deadline_at is in the past"
        except ValueError:
            return "DEADLINE_EXCEEDED: invalid deadline_at format"
    return None


def semantic_check_session(instance: dict) -> str | None:
    """Semantic: session_id must be non-empty and match SEAL-* pattern."""
    sid = instance.get("session_id", "")
    if not sid or not sid.startswith("SEAL-"):
        return "SESSION_MISSING: session_id must match SEAL-<hex> pattern"
    return None


def semantic_check_idempotency(instance: dict) -> str | None:
    """Semantic: attempt must not exceed max_attempts."""
    attempt = instance.get("attempt", 1)
    max_attempts = instance.get("max_attempts", 3)
    if attempt > max_attempts:
        return f"IDEMPOTENCY_CONFLICT: attempt={attempt} exceeds max_attempts={max_attempts}"
    return None


def semantic_check_authority(instance: dict) -> str | None:
    """Semantic: EXECUTE requires judge_receipt_ref, IRREVERSIBLE requires human_ack_ref."""
    authority = instance.get("authority", {})
    action_class = authority.get("action_class", "")
    mutation = authority.get("mutation", False)
    reversible = authority.get("reversible", True)
    judge_ref = authority.get("judge_receipt_ref")
    human_ack = authority.get("human_ack_ref")

    if action_class == "EXECUTE" and (not judge_ref or judge_ref == ""):
        return "JUDGE_RECEIPT_MISSING: action_class=EXECUTE requires judge_receipt_ref"
    if mutation and not reversible and (not human_ack or human_ack == ""):
        return "HUMAN_ACK_MISSING: mutation=true + reversible=false requires human_ack_ref"
    return None


def run_all_tests() -> int:
    """Run the full ABI conformance test suite."""
    errors: list[str] = []
    print("=" * 60)
    print("Federation ABI Conformance — v1.0.0")
    print("=" * 60)

    # 1. Schema syntax
    print("\n1. Schema Syntax Validation")
    errors.extend(validate_schema_syntax())

    # 2. Schema ID consistency
    print("\n2. Schema ID & Version Consistency")
    errors.extend(validate_schema_ids())

    # 3. Positive fixtures
    print("\n3. Positive Fixtures (must PASS)")
    request_schema = load_json(SCHEMA_FILES["request"])
    response_schema = load_json(SCHEMA_FILES["response"])

    for fixture_name in ["valid-request.json", "valid-response.json"]:
        path = FIXTURES_DIR / fixture_name
        if not path.exists():
            errors.append(f"  ❌ MISSING: {fixture_name}")
            continue
        ok, msg = validate_fixture(
            path, request_schema if "request" in fixture_name else response_schema
        )
        if ok:
            print(f"  ✅ {fixture_name}: {msg}")
        else:
            errors.append(f"  ❌ {fixture_name}: {msg}")

    # 4. Negative fixtures (must FAIL structural validation)
    print("\n4. Negative Fixtures (must FAIL)")
    for fixture_name, expected_error in NEGATIVE_FIXTURES.items():
        path = FIXTURES_DIR / fixture_name
        if not path.exists():
            errors.append(f"  ❌ MISSING: {fixture_name}")
            continue
        ok, _ = validate_fixture(path, request_schema)
        instance = load_json(path)

        # Run semantic checks
        semantic_error = (
            semantic_check_session(instance)
            or semantic_check_deadline(instance)
            or semantic_check_idempotency(instance)
        )

        if not ok or semantic_error:
            reason = "structural" if not ok else "semantic"
            detail = semantic_error or "structural schema violation"
            print(f"  ✅ {fixture_name}: correctly FAILED ({reason}): {detail}")
        else:
            errors.append(
                f"  ❌ {fixture_name}: should have FAILED but passed both structural and semantic checks"
            )

    # 5. Semantic authority checks
    print("\n5. Semantic Authority Enforcement")
    authority_fixture = load_json(FIXTURES_DIR / "valid-request.json")

    # Test EXECUTE without judge_receipt_ref
    exec_fixture = dict(authority_fixture)
    exec_fixture["invocation_id"] = "inv-exec-test"
    exec_fixture["idempotency_key"] = "idem-exec-test"
    exec_fixture["authority"] = dict(exec_fixture["authority"])
    exec_fixture["authority"]["action_class"] = "EXECUTE"
    exec_fixture["authority"]["judge_receipt_ref"] = None
    auth_error = semantic_check_authority(exec_fixture)
    if auth_error:
        print(f"  ✅ EXECUTE without judge_receipt_ref: correctly FAILED — {auth_error}")
    else:
        errors.append("  ❌ EXECUTE without judge_receipt_ref: should have FAILED")

    # Test IRREVERSIBLE without human_ack_ref
    irrev_fixture = dict(authority_fixture)
    irrev_fixture["invocation_id"] = "inv-irrev-test"
    irrev_fixture["idempotency_key"] = "idem-irrev-test"
    irrev_fixture["authority"] = dict(irrev_fixture["authority"])
    irrev_fixture["authority"]["mutation"] = True
    irrev_fixture["authority"]["reversible"] = False
    irrev_fixture["authority"]["human_ack_ref"] = None
    auth_error = semantic_check_authority(irrev_fixture)
    if auth_error:
        print(f"  ✅ IRREVERSIBLE without human_ack_ref: correctly FAILED — {auth_error}")
    else:
        errors.append("  ❌ IRREVERSIBLE without human_ack_ref: should have FAILED")

    # 6. Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ CONFORMANCE FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
        return EXIT_FAIL
    else:
        print("✅ CONFORMANCE PASSED — all checks green")
        return EXIT_OK


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Federation ABI Conformance Validator")
    parser.add_argument("--schema-only", action="store_true", help="Validate schema syntax only")
    parser.add_argument("--fixture", type=str, help="Validate a single fixture file")
    args = parser.parse_args()

    if args.schema_only:
        errs = validate_schema_syntax()
        sys.exit(EXIT_FAIL if errs else EXIT_OK)

    if args.fixture:
        path = Path(args.fixture)
        schema = SCHEMA_FILES["request"] if "request" in args.fixture else SCHEMA_FILES["response"]
        ok, msg = validate_fixture(path, schema)
        print(f"{'PASS' if ok else 'FAIL'}: {msg}")
        sys.exit(EXIT_OK if ok else EXIT_FAIL)

    sys.exit(run_all_tests())
