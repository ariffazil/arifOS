from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ABI_ROOT = Path(__file__).resolve().parent
KERNEL_ABI_VERSION = "1.0.0"
_SEMANTIC_FIELDS = (
    "capability_id",
    "version",
    "action_class",
    "mutation",
    "irreversible",
    "authority_required",
    "evidence_required",
    "idempotency",
    "receipt_policy",
    "constitutional_floors",
)


@lru_cache(maxsize=None)
def _load_registry(filename: str) -> dict[str, Any]:
    return json.loads((ABI_ROOT / filename).read_text(encoding="utf-8"))


def capability_registry() -> dict[str, Any]:
    return _load_registry("capability_registry.json")


def model_registry() -> dict[str, Any]:
    return _load_registry("model_registry.json")


def policy_registry() -> dict[str, Any]:
    return _load_registry("policy_registry.json")


def receipt_registry() -> dict[str, Any]:
    return _load_registry("receipt_registry.json")


def _capabilities() -> tuple[dict[str, Any], ...]:
    return tuple(capability_registry()["capabilities"])


def capability_ids() -> tuple[str, ...]:
    return tuple(item["capability_id"] for item in _capabilities())


def semantic_tool_names() -> tuple[str, ...]:
    return tuple(item["provider"]["tool"] for item in _capabilities())


def profile_names() -> tuple[str, ...]:
    return tuple(policy_registry()["profiles"])


def normalize_profile(profile: str | None) -> str:
    policy = policy_registry()
    raw = (profile or policy["default_profile"]).strip().lower()
    return policy["profile_aliases"].get(raw, raw if raw in policy["profiles"] else policy["default_profile"])


def profile_contract(profile: str | None) -> dict[str, Any]:
    return policy_registry()["profiles"][normalize_profile(profile)]


def tool_names_for_profile(profile: str | None) -> tuple[str, ...]:
    by_id = {item["capability_id"]: item for item in _capabilities()}
    return tuple(by_id[item]["provider"]["tool"] for item in profile_contract(profile)["capabilities"])


def semantic_hash(capability: dict[str, Any]) -> str:
    payload = {field: capability[field] for field in _SEMANTIC_FIELDS}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def validate_abi() -> dict[str, Any]:
    capability = capability_registry()
    policy = policy_registry()
    receipts = receipt_registry()["receipts"]
    ids = capability_ids()
    tools = semantic_tool_names()
    errors: list[str] = []

    if capability.get("abi_version") != KERNEL_ABI_VERSION:
        errors.append("ABI version mismatch")
    # Surface-arity invariant: every id unique, but no hard-coded count.
    # The kernel ABI grew from 8 → 9 with vault.verify on 2026-07-18.
    if len(set(ids)) != len(ids):
        errors.append("Kernel ABI capability ids must be unique")
    if len(set(tools)) != len(tools):
        errors.append("Each semantic capability must have one unique public provider tool")
    for item in _capabilities():
        if item.get("semantic_hash") != semantic_hash(item):
            errors.append(f"semantic hash drift: {item['capability_id']}")
        if item["capability_id"] not in receipts:
            errors.append(f"missing receipt contract: {item['capability_id']}")
    known = set(ids)
    for name, profile in policy["profiles"].items():
        unknown = set(profile["capabilities"]) - known
        if unknown:
            errors.append(f"profile {name} contains unknown capabilities: {sorted(unknown)}")

    return {"ok": not errors, "abi_version": KERNEL_ABI_VERSION, "capability_count": len(ids), "errors": errors}
