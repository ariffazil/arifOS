from __future__ import annotations

import hashlib
import json
from functools import cache
from pathlib import Path
from typing import Any

ABI_ROOT = Path(__file__).resolve().parent
KERNEL_ABI_VERSION = "2026.07.24"
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

# ── arifOS Governance Fields (F1-MCP-Governance-Wrapper) ──

_GOVERNANCE_FIELDS = (
    "is_reversible",
    "impact_radius",
    "requires_888_hold",
    "allowed_roles",
)

# Strict fallback: missing governance = MOST CONSERVATIVE
_GOVERNANCE_DEFAULTS = {
    "is_reversible": False,
    "impact_radius": 5,
    "requires_888_hold": True,
    "allowed_roles": [],
}


def get_governance(capability: dict[str, Any]) -> dict[str, Any]:
    """
    Extract arifos_governance block from a capability entry.
    Returns strict fallback defaults if block is missing or incomplete.
    ZERO ASSUMPTION on missing fields.
    """
    gov = capability.get("arifos_governance", {})
    return {
        field: gov.get(field, _GOVERNANCE_DEFAULTS[field])
        for field in _GOVERNANCE_FIELDS
    }


def evaluate_governance(
    capability_id: str,
    invoking_role: str,
    is_write_operation: bool = False,
) -> dict[str, Any]:
    """
    Pre-execution governance enforcement. Returns verdict dict.

    Decision tree:
    1. Capability not found → BLOCKED (strict fallback)
    2. Role not in allowed_roles → BLOCKED
    3. Write op on reversible-only tool → BLOCKED
    4. requires_888_hold OR impact_radius >= 3 → REQUIRES_HOLD
    5. All clear → APPROVED

    Called BEFORE OPA evaluation in the dispatch pipeline.
    """
    registry = capability_registry()
    capabilities = {c["capability_id"]: c for c in registry["capabilities"]}

    cap = capabilities.get(capability_id)
    if cap is None:
        return {
            "verdict": "BLOCKED",
            "reason": f"Capability '{capability_id}' not found in registry. UNCHECKED_BLOCK.",
            "tool": capability_id,
            "role": invoking_role,
            "governance": _GOVERNANCE_DEFAULTS,
        }

    gov = get_governance(cap)

    # Check 1: Role authorization
    allowed = gov["allowed_roles"]
    if allowed and invoking_role not in allowed:
        return {
            "verdict": "BLOCKED",
            "reason": f"Role '{invoking_role}' not authorized for '{capability_id}'. Allowed: {allowed}",
            "tool": capability_id,
            "role": invoking_role,
            "governance": gov,
        }
    # Empty allowed_roles = sovereign only (888-APEX)
    if not allowed and invoking_role != "888-APEX":
        return {
            "verdict": "BLOCKED",
            "reason": f"Capability '{capability_id}' is sovereign-exclusive. Role '{invoking_role}' denied.",
            "tool": capability_id,
            "role": invoking_role,
            "governance": gov,
        }

    # Check 2: Write operation on read-only tool
    if is_write_operation and gov["is_reversible"]:
        return {
            "verdict": "BLOCKED",
            "reason": f"Write operation on read-only tool '{capability_id}'. Mutation not permitted.",
            "tool": capability_id,
            "role": invoking_role,
            "governance": gov,
        }

    # Check 3: Sovereign hold required
    if gov["requires_888_hold"] or gov["impact_radius"] >= 3:
        return {
            "verdict": "REQUIRES_HOLD",
            "reason": f"Tool '{capability_id}' requires 888 Sovereign Hold. impact_radius={gov['impact_radius']}, reversible={gov['is_reversible']}.",
            "tool": capability_id,
            "role": invoking_role,
            "governance": gov,
        }

    # All clear
    return {
        "verdict": "APPROVED",
        "reason": "Governance check passed.",
        "tool": capability_id,
        "role": invoking_role,
        "governance": gov,
    }


def filter_tools_for_role(
    capability_ids: list[str],
    role: str,
) -> list[str]:
    """
    Filter capability list to only those the role is authorized for.
    Returns subset of input list.
    """
    registry = capability_registry()
    capabilities = {c["capability_id"]: c for c in registry["capabilities"]}
    filtered = []
    for cid in capability_ids:
        cap = capabilities.get(cid)
        if cap is None:
            continue  # Unknown capability = skip (strict fallback)
        gov = get_governance(cap)
        allowed = gov["allowed_roles"]
        if allowed and role in allowed:
            filtered.append(cid)
        elif not allowed and role == "888-APEX":
            filtered.append(cid)
    return filtered


@cache
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
    return policy["profile_aliases"].get(
        raw, raw if raw in policy["profiles"] else policy["default_profile"]
    )


def profile_contract(profile: str | None) -> dict[str, Any]:
    return policy_registry()["profiles"][normalize_profile(profile)]


def tool_names_for_profile(profile: str | None) -> tuple[str, ...]:
    by_id = {item["capability_id"]: item for item in _capabilities()}
    return tuple(
        by_id[item]["provider"]["tool"] for item in profile_contract(profile)["capabilities"]
    )


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
    # Surface-arity invariant: exactly 8 capabilities (KERNEL_ABI_8).
    # The 8-tool constitutional surface is the long-standing contract.
    # Per sovereign directive 2026-07-18: vault.verify is a mode of arif_seal,
    # not a separate tool — keeping the surface at 8.
    if len(ids) != 8 or len(set(ids)) != 8:
        errors.append("Kernel ABI must contain exactly eight unique capabilities")
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

    return {
        "ok": not errors,
        "abi_version": KERNEL_ABI_VERSION,
        "capability_count": len(ids),
        "errors": errors,
    }


# ── Audit Trail Integration ──

def _write_audit_event(
    gov_verdict: dict[str, Any],
    session_id: str | None = None,
    opa_verdict: str | None = None,
) -> dict[str, Any]:
    """Write a governance audit event. Returns the written entry."""
    try:
        from .abi.audit import write_audit_event
        return write_audit_event(
            event=f"TOOL_CALL_{gov_verdict['verdict']}",
            tool=gov_verdict.get("tool", ""),
            capability_id=gov_verdict.get("tool", ""),
            agent_id=gov_verdict.get("role", "unknown"),
            verdict=gov_verdict["verdict"],
            reason=gov_verdict.get("reason", ""),
            governance=gov_verdict.get("governance", {}),
            session_id=session_id,
            opa_verdict=opa_verdict,
            impact_radius=gov_verdict.get("governance", {}).get("impact_radius", 0),
            is_reversible=gov_verdict.get("governance", {}).get("is_reversible", False),
            requires_888_hold=gov_verdict.get("governance", {}).get("requires_888_hold", False),
        )
    except Exception:
        # Audit write must never crash the governance check
        return {"persisted": False}
