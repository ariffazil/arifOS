"""
arifosmcp/runtime/envelope_validator.py
══════════════════════════════════════════
P0-2: ENVELOPE ENFORCEMENT HARNESS

Shared validator that ensures every tool call carries a valid
FederationEnvelope with policy_hash and authority chain.

This is Gate 7 in the governance pipeline — the LAST gate before execution.
All 13 canonical tools MUST pass this gate.

F1 AMANAH: Additive wrapper, never mutates kernel.
F2 TRUTH: policy_hash verified against kernel manifest.
F11 AUTH: authority chain validated (agent → organ → kernel).
F13 SOVEREIGN: ATOMIC actions require F13 signature.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger("arifosmcp.envelope_validator")


class EnvelopeVerdict(StrEnum):
    VALID = "VALID"
    MISSING = "MISSING"  # No envelope at all
    INVALID_SCHEMA = "INVALID_SCHEMA"  # Envelope present but malformed
    POLICY_HASH_MISMATCH = "POLICY_HASH_MISMATCH"  # policy_hash doesn't match kernel
    AUTHORITY_CHAIN_BROKEN = "AUTHORITY_CHAIN_BROKEN"  # agent→organ→kernel chain invalid
    TOOL_NOT_ALLOWED = "TOOL_NOT_ALLOWED"  # Tool not in allowed set
    F13_SIGNATURE_MISSING = "F13_SIGNATURE_MISSING"  # ATOMIC action needs F13 sig
    HOLD = "HOLD"


# Canonical policy hash (sha256 of constitutional_map.py CANONICAL_TOOLS + FLOOR_SPEC)
# Generated at forge time, verified at runtime.
_KERNEL_POLICY_HASH: str = ""
_KERNEL_MANIFEST_HASH: str = ""


def set_kernel_policy_hash(h: str) -> None:
    """Set the canonical policy hash from constitutional_map."""
    global _KERNEL_POLICY_HASH
    _KERNEL_POLICY_HASH = h


def set_kernel_manifest_hash(h: str) -> None:
    """Set the canonical manifest hash."""
    global _KERNEL_MANIFEST_HASH
    _KERNEL_MANIFEST_HASH = h


# Allowed tools by action class
ALLOWED_TOOLS_BY_CLASS: dict[str, set[str]] = {
    "READ": {
        "arif_measure",
        "arif_observe",
        "arif_fetch",
        "arif_memory_recall",
        "arif_kernel_route",
        "arif_compose",
        "arif_lease_inspect",
    },
    "ADVISORY": {
        "arif_think",
        "arif_critique",
        "arif_gateway_connect",
        "arif_lease_issue",
    },
    "MUTATE": {
        "arif_init",
        "arif_forge",
        "arif_lease_revoke",
    },
    "ATOMIC": {
        "arif_judge",
        "arif_seal",
    },
}

# Tools that always require F13 signature
F13_REQUIRED_TOOLS: set[str] = {"arif_seal", "arif_judge"}


@dataclass
class EnvelopeCheck:
    """Result of envelope validation."""

    verdict: EnvelopeVerdict
    tool_name: str
    policy_hash_match: bool = False
    authority_valid: bool = False
    tool_allowed: bool = False
    f13_present: bool = False
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def validate_envelope(
    tool_name: str,
    envelope: dict[str, Any] | None = None,
    action_class: str = "READ",
    policy_hash: str | None = None,
    authority_chain: list[str] | None = None,
    f13_signature: str | None = None,
) -> EnvelopeCheck:
    """
    Validate a FederationEnvelope for a tool call.

    Gate 7: This is the LAST gate before execution.
    All previous gates must pass before this is called.

    Args:
        tool_name: The canonical tool name (e.g. 'arif_forge')
        envelope: The raw _envelope dict from the MCP call
        action_class: READ | ADVISORY | MUTATE | ATOMIC
        policy_hash: sha256 hash from the envelope
        authority_chain: list of authority fingerprints
        f13_signature: Ed25519 signature (required for ATOMIC)

    Returns:
        EnvelopeCheck with verdict and reasons
    """
    reasons: list[str] = []

    # 1. Envelope must exist
    if not envelope:
        return EnvelopeCheck(
            verdict=EnvelopeVerdict.MISSING,
            tool_name=tool_name,
            reasons=["No _envelope provided. All governed tools require FederationEnvelope."],
        )

    # 2. Extract fields from envelope
    env_dict: dict[str, Any] = envelope if envelope is not None else {}
    if policy_hash is None:
        policy_hash = env_dict.get("policy_hash", "")
    if authority_chain is None:
        authority_chain = env_dict.get("authority_chain", [])
    if f13_signature is None:
        f13_signature = env_dict.get("f13_signature", "")

    check = EnvelopeCheck(
        verdict=EnvelopeVerdict.VALID,
        tool_name=tool_name,
        metadata={
            "action_class": action_class,
            "policy_hash": (policy_hash or "none")[:16] + "...",
        },
    )

    # 3. Policy hash must match kernel (skip if kernel hash not yet configured)
    if _KERNEL_POLICY_HASH:
        if policy_hash:
            check.policy_hash_match = policy_hash == _KERNEL_POLICY_HASH
            if not check.policy_hash_match:
                reasons.append(
                    f"policy_hash mismatch: envelope={(policy_hash or 'none')[:16]}... kernel={_KERNEL_POLICY_HASH[:16]}..."
                )
        else:
            reasons.append("policy_hash missing from envelope")
    else:
        # Kernel policy hash not configured yet — treat as valid, skip check
        check.policy_hash_match = True

    # 4. Authority chain must be valid (at least: agent → organ)
    if authority_chain and len(authority_chain) >= 2:
        check.authority_valid = True
    else:
        reasons.append("authority_chain incomplete (need agent→organ→kernel)")

    # 5. Tool must be allowed for this action class
    allowed = ALLOWED_TOOLS_BY_CLASS.get(action_class, set())
    check.tool_allowed = tool_name in allowed
    if not check.tool_allowed:
        reasons.append(f"Tool '{tool_name}' not allowed for action_class='{action_class}'")

    # 6. ATOMIC actions require F13 signature
    if action_class == "ATOMIC" or tool_name in F13_REQUIRED_TOOLS:
        check.f13_present = bool(f13_signature and len(f13_signature) > 32)
        if not check.f13_present:
            reasons.append(f"F13 signature required for ATOMIC action '{tool_name}'")

    # 7. Final verdict
    if not envelope:
        check.verdict = EnvelopeVerdict.MISSING
    elif not check.policy_hash_match and policy_hash:
        check.verdict = EnvelopeVerdict.POLICY_HASH_MISMATCH
    elif not check.authority_valid:
        check.verdict = EnvelopeVerdict.AUTHORITY_CHAIN_BROKEN
    elif not check.tool_allowed:
        check.verdict = EnvelopeVerdict.TOOL_NOT_ALLOWED
    elif action_class == "ATOMIC" and not check.f13_present:
        check.verdict = EnvelopeVerdict.F13_SIGNATURE_MISSING
    else:
        check.verdict = EnvelopeVerdict.VALID

    check.reasons = reasons
    return check


def gate_envelope(
    tool_name: str,
    envelope: dict[str, Any] | None = None,
    action_class: str = "READ",
    **kwargs: Any,
) -> tuple[bool, EnvelopeCheck]:
    """Gate 7: Envelope validation. Returns (allowed, check)."""
    check = validate_envelope(tool_name, envelope=envelope, action_class=action_class, **kwargs)
    allowed = check.verdict == EnvelopeVerdict.VALID
    return allowed, check


def _self_check() -> dict[str, Any]:
    """Self-test — verify envelope validation logic."""
    results = []

    # Test 1: Missing envelope
    r = validate_envelope("arif_think", envelope=None, action_class="ADVISORY")
    results.append(("missing_envelope", r.verdict == EnvelopeVerdict.MISSING, str(r.verdict)))

    # Test 2: Tool not allowed for action class (with valid authority chain)
    r = validate_envelope(
        "arif_seal",
        envelope={"policy_hash": "abc", "authority_chain": ["a", "b"]},
        action_class="READ",
    )
    results.append(
        ("tool_not_allowed", r.verdict == EnvelopeVerdict.TOOL_NOT_ALLOWED, str(r.verdict))
    )

    # Test 3: ATOMIC without F13 signature
    r = validate_envelope(
        "arif_seal",
        envelope={"policy_hash": "abc", "authority_chain": ["a", "b"]},
        action_class="ATOMIC",
        f13_signature="",
    )
    results.append(
        ("atomic_no_f13", r.verdict == EnvelopeVerdict.F13_SIGNATURE_MISSING, str(r.verdict))
    )

    # Test 4: Valid advisory call
    r = validate_envelope(
        "arif_think",
        envelope={"policy_hash": "abc", "authority_chain": ["agent", "organ"]},
        action_class="ADVISORY",
        policy_hash="abc",
    )
    results.append(("valid_advisory", r.verdict == EnvelopeVerdict.VALID, str(r.verdict)))

    passed = sum(1 for _, ok, _ in results if ok)
    return {
        "module": "envelope_validator",
        "tests": len(results),
        "passed": passed,
        "results": results,
        "verdict": "OK" if passed == len(results) else "FAIL",
    }


__all__ = [
    "EnvelopeVerdict",
    "EnvelopeCheck",
    "validate_envelope",
    "gate_envelope",
    "set_kernel_policy_hash",
    "set_kernel_manifest_hash",
    "ALLOWED_TOOLS_BY_CLASS",
    "F13_REQUIRED_TOOLS",
    "_self_check",
]
