#!/usr/bin/env python3
"""Federation ABI Validator — v1.0.0 (Forge 0A.2)

Structural validation (JSON Schema) + honest semantic checks.

Semantic honesty:
  - session_identifier_present: non-empty session_id only (NOT liveness)
  - session_id format enforced by schema (SEAL-<16hex>)
  - session_token is optional sct_v1.* (schema)
  - retry_bound: attempt <= max_attempts (NOT full idempotency)
  - idempotency: stateful check via IdempotencyStore interface + Memory test double
  - payload_hash: FCJ-v1 (see contracts/schemas/CANONICAL_JSON.md) — not full RFC 8785

Usage:
    python scripts/validate_federation_abi.py
    python scripts/validate_federation_abi.py --schema-only
    python scripts/validate_federation_abi.py --fixture <path>
    python scripts/validate_federation_abi.py --check-sums
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "contracts" / "schemas"
FIXTURES_DIR = ROOT / "contracts" / "fixtures"
SHA256SUMS = SCHEMAS_DIR / "SHA256SUMS"

SCHEMA_FILES = {
    "request": SCHEMAS_DIR / "federation-request.v1.schema.json",
    "response": SCHEMAS_DIR / "federation-response.v1.schema.json",
    "error": SCHEMAS_DIR / "federation-error.v1.schema.json",
    "receipt": SCHEMAS_DIR / "federation-receipt.v1.schema.json",
}

EXIT_OK = 0
EXIT_FAIL = 1


def fcj_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def payload_hash(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(fcj_dumps(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IdempotencyRecord:
    request_hash: str
    result_ref: str | None = None


class IdempotencyStore(Protocol):
    def lookup(self, key: str) -> IdempotencyRecord | None: ...

    def reserve(self, key: str, request_hash: str, result_ref: str | None = None) -> None: ...


class MemoryIdempotencyStore:
    def __init__(self) -> None:
        self._store: dict[str, IdempotencyRecord] = {}

    def lookup(self, key: str) -> IdempotencyRecord | None:
        return self._store.get(key)

    def reserve(self, key: str, request_hash: str, result_ref: str | None = None) -> None:
        self._store[key] = IdempotencyRecord(request_hash=request_hash, result_ref=result_ref)


def request_content_hash(instance: dict[str, Any]) -> str:
    return payload_hash(instance.get("payload", {}))


def check_idempotency_stateful(instance: dict[str, Any], store: IdempotencyStore) -> str | None:
    key = instance.get("idempotency_key")
    if not key:
        return "IDEMPOTENCY_KEY_MISSING: idempotency_key required"
    req_hash = request_content_hash(instance)
    prior = store.lookup(str(key))
    if prior is None:
        return None
    if prior.request_hash == req_hash:
        return None
    return (
        "IDEMPOTENCY_CONFLICT: key already consumed with different request hash "
        f"(prior={prior.request_hash[:19]}... new={req_hash[:19]}...)"
    )


def check_retry_bound(instance: dict[str, Any]) -> str | None:
    attempt = instance.get("attempt", 1)
    max_attempts = instance.get("max_attempts", 3)
    try:
        if int(attempt) > int(max_attempts):
            return f"RETRY_BOUND_EXCEEDED: attempt ({attempt}) > max_attempts ({max_attempts})"
    except (TypeError, ValueError):
        return "RETRY_BOUND_INVALID: attempt/max_attempts not integers"
    return None


def load_json(path: Path) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def validate_schema_syntax() -> list[str]:
    errors: list[str] = []
    if jsonschema is None:
        errors.append("jsonschema package not installed")
        return errors
    for name, path in SCHEMA_FILES.items():
        if not path.exists():
            errors.append(f"MISSING: {name} schema at {path}")
            continue
        try:
            schema = load_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            print(f"  ✅ {name}: valid JSON Schema 2020-12")
        except Exception as e:  # noqa: BLE001
            errors.append(f"  ❌ {name}: {e}")
    return errors


def validate_schema_ids() -> list[str]:
    errors: list[str] = []
    for name, path in SCHEMA_FILES.items():
        if not path.exists():
            errors.append(f"MISSING: {name}")
            continue
        schema = load_json(path)
        sid = schema.get("$id", "")
        title = schema.get("title", "")
        if "v1.0.0" not in sid and "v1.0.0" not in title:
            errors.append(f"  ❌ {name}: does not advertise v1.0.0 ({sid})")
            continue
        print(f"  ✅ {name}: $id={sid}")
    return errors


def validate_structural(instance: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    if jsonschema is None:
        return ["jsonschema not installed"]
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{list(err.absolute_path)}: {err.message}" for err in validator.iter_errors(instance)]


def session_identifier_present(instance: dict[str, Any]) -> str | None:
    """Non-empty session_id only. NOT liveness / expiry / binding / signature."""
    session_id = instance.get("session_id", None)
    if session_id is None or session_id == "":
        return "SESSION_MISSING: session_id empty or absent"
    return None


def check_deadline(instance: dict[str, Any]) -> str | None:
    deadline = instance.get("deadline_at")
    if not deadline:
        return None
    try:
        dt = datetime.fromisoformat(str(deadline).replace("Z", "+00:00"))
        if dt < datetime.now(UTC):
            return "DEADLINE_EXCEEDED: deadline_at is in the past"
    except (ValueError, TypeError):
        return "DEADLINE_INVALID: unparseable deadline_at"
    return None


def check_payload_hash(instance: dict[str, Any]) -> str | None:
    declared = instance.get("payload_hash")
    if not declared:
        return None
    if "payload" not in instance:
        return "PAYLOAD_MISSING: payload_hash present without payload"
    computed = payload_hash(instance["payload"])
    if declared != computed:
        return (
            f"PAYLOAD_INTEGRITY_FAILED: declared={declared[:24]}... "
            f"computed={computed[:24]}... (FCJ-v1)"
        )
    return None


def check_authority(instance: dict[str, Any]) -> str | None:
    auth = instance.get("authority") or {}
    if auth.get("action_class") == "EXECUTE":
        if not auth.get("judge_receipt_ref"):
            return "JUDGE_RECEIPT_MISSING: action_class=EXECUTE requires judge_receipt_ref"
    if auth.get("mutation") is True and auth.get("reversible") is False:
        if not auth.get("human_ack_ref"):
            return "HUMAN_ACK_MISSING: mutation=true + reversible=false requires human_ack_ref"
    return None


def validate_fixture_semantic(
    instance: dict[str, Any], store: IdempotencyStore | None = None
) -> list[str]:
    errors: list[str] = []
    for fn in (
        session_identifier_present,
        check_deadline,
        check_payload_hash,
        check_retry_bound,
        check_authority,
    ):
        err = fn(instance)
        if err:
            errors.append(err)
    if store is not None:
        err = check_idempotency_stateful(instance, store)
        if err:
            errors.append(err)
    return errors


def check_sums() -> list[str]:
    errors: list[str] = []
    if not SHA256SUMS.exists():
        return [f"MISSING: {SHA256SUMS}"]
    for line in SHA256SUMS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        expected, _, rel = line.partition("  ")
        path = ROOT / rel.strip()
        if not path.exists():
            errors.append(f"MISSING file for sum: {rel}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected.strip():
            errors.append(f"HASH MISMATCH: {rel}")
        else:
            print(f"  ✅ {rel}")
    return errors


def run_all_tests() -> int:
    print("=" * 60)
    print("Federation ABI Conformance — v1.0.0 (Forge 0A.2)")
    print("=" * 60)
    errors: list[str] = []

    print("\n1. Schema Syntax Validation")
    errors.extend(validate_schema_syntax())

    print("\n2. Schema ID & Version Consistency")
    errors.extend(validate_schema_ids())

    print("\n3. SHA256SUMS integrity")
    errors.extend(check_sums())

    request_schema = load_json(SCHEMA_FILES["request"])
    response_schema = load_json(SCHEMA_FILES["response"])

    store = MemoryIdempotencyStore()
    valid_path = FIXTURES_DIR / "valid-request.json"
    if valid_path.exists():
        valid_inst = load_json(valid_path)
        store.reserve(
            str(valid_inst["idempotency_key"]),
            request_content_hash(valid_inst),
            result_ref="fixture:valid-request",
        )

    print("\n4. Positive Fixtures (must PASS)")
    for fixture_name, schema in (
        ("valid-request.json", request_schema),
        ("valid-response.json", response_schema),
    ):
        path = FIXTURES_DIR / fixture_name
        if not path.exists():
            errors.append(f"  ❌ MISSING: {fixture_name}")
            continue
        instance = load_json(path)
        structural = validate_structural(instance, schema)
        semantic = (
            validate_fixture_semantic(instance, store=store) if "request" in fixture_name else []
        )
        if structural or semantic:
            errors.append(f"  ❌ {fixture_name}: {structural + semantic}")
            for e in structural + semantic:
                print(f"     {e}")
        else:
            print(f"  ✅ {fixture_name}: PASS")

    print("\n5. Negative Fixtures (must FAIL)")
    for path in sorted(p for p in FIXTURES_DIR.glob("*.json") if "invalid" in p.name):
        instance = load_json(path)
        structural = validate_structural(instance, request_schema)
        semantic = validate_fixture_semantic(instance, store=store)
        all_errs = structural + semantic
        if all_errs:
            print(f"  ✅ {path.name}: correctly FAILED ({len(all_errs)})")
            for e in all_errs[:3]:
                print(f"     (expected) {e}")
        else:
            errors.append(f"  ❌ {path.name}: SHOULD fail but passed")

    print("\n6. Semantic Authority Enforcement (synthetic)")
    base = load_json(FIXTURES_DIR / "valid-request.json")
    exec_fix = json.loads(json.dumps(base))
    exec_fix["invocation_id"] = "inv-exec-test"
    exec_fix["idempotency_key"] = "idem-exec-test"
    exec_fix["authority"] = dict(exec_fix["authority"])
    exec_fix["authority"]["action_class"] = "EXECUTE"
    exec_fix["authority"]["judge_receipt_ref"] = None
    auth_err = check_authority(exec_fix)
    if auth_err:
        print(f"  ✅ EXECUTE without judge_receipt_ref: {auth_err}")
    else:
        errors.append("  ❌ EXECUTE without judge_receipt_ref should fail")

    irrev = json.loads(json.dumps(base))
    irrev["invocation_id"] = "inv-irrev-test"
    irrev["idempotency_key"] = "idem-irrev-test"
    irrev["authority"] = dict(irrev["authority"])
    irrev["authority"]["mutation"] = True
    irrev["authority"]["reversible"] = False
    irrev["authority"]["human_ack_ref"] = None
    irrev["authority"]["action_class"] = "EXECUTE"
    irrev["authority"]["judge_receipt_ref"] = "judge-ok"
    auth_err = check_authority(irrev)
    if auth_err:
        print(f"  ✅ IRREVERSIBLE without human_ack_ref: {auth_err}")
    else:
        errors.append("  ❌ IRREVERSIBLE without human_ack_ref should fail")

    print("\n7. Idempotency store behavior (test double)")
    replay_err = check_idempotency_stateful(base, store)
    if replay_err is None:
        print("  ✅ same key + same hash: REPLAY_OK")
    else:
        errors.append(f"  ❌ replay should pass: {replay_err}")
    conflict = json.loads(json.dumps(base))
    conflict["payload"] = {"mode": "other"}
    conflict["payload_hash"] = payload_hash(conflict["payload"])
    c_err = check_idempotency_stateful(conflict, store)
    if c_err and "IDEMPOTENCY_CONFLICT" in c_err:
        print(f"  ✅ same key + different hash: {c_err[:60]}…")
    else:
        errors.append(f"  ❌ conflict expected, got: {c_err}")

    print("\n" + "=" * 60)
    if errors:
        print(f"❌ CONFORMANCE FAILED — {len(errors)} error(s):")
        for e in errors:
            print(f"  {e}")
        return EXIT_FAIL
    print("✅ CONFORMANCE PASSED — all checks green")
    print("NOTE: session_identifier_present ≠ live session attestation.")
    print("NOTE: HARDENED DRAFT — no F13 seal / no ratification claim.")
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(description="Federation ABI Conformance Validator")
    parser.add_argument("--schema-only", action="store_true")
    parser.add_argument("--check-sums", action="store_true")
    parser.add_argument("--fixture", type=str)
    args = parser.parse_args()

    if args.schema_only:
        return EXIT_FAIL if validate_schema_syntax() else EXIT_OK
    if args.check_sums:
        return EXIT_FAIL if check_sums() else EXIT_OK
    if args.fixture:
        path = Path(args.fixture)
        schema = (
            load_json(SCHEMA_FILES["request"])
            if "response" not in path.name
            else load_json(SCHEMA_FILES["response"])
        )
        instance = load_json(path)
        structural = validate_structural(instance, schema)
        semantic = validate_fixture_semantic(instance)
        if structural or semantic:
            print("FAIL")
            for e in structural + semantic:
                print(" ", e)
            return EXIT_FAIL
        print("PASS")
        return EXIT_OK
    return run_all_tests()


if __name__ == "__main__":
    raise SystemExit(main())
