"""
arifOS V2 Response Envelope — Shared builder for all 8 canonical tools.

Injects deterministic top-level fields (canonical_verdict, authority_scope,
receipt_state, execution_state) into every tool response. Used as middleware
in server.py, following the AKAL wrapper pattern.

Source of truth: capability_registry.json for capability_id mapping.
V2 envelope schema: arifOS.response.v2 at schema/response.envelope.schema.json.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Cache the capability registry at module level
_CAPABILITY_REGISTRY: dict[str, dict[str, Any]] | None = None
_CAPABILITY_BY_TOOL: dict[str, dict[str, Any]] | None = None


def _load_capability_registry() -> tuple[dict[str, Any], dict[str, Any]]:
    """Load and cache the capability registry. Returns (registry, by_tool)."""
    global _CAPABILITY_REGISTRY, _CAPABILITY_BY_TOOL
    if _CAPABILITY_REGISTRY is None:
        path = Path(__file__).resolve().parent.parent / "abi" / "capability_registry.json"
        try:
            with open(path) as f:
                _CAPABILITY_REGISTRY = json.load(f)
            _CAPABILITY_BY_TOOL = {}
            for cap in _CAPABILITY_REGISTRY.get("capabilities", []):
                tool_name = cap.get("provider", {}).get("tool", "")
                if tool_name:
                    _CAPABILITY_BY_TOOL[tool_name] = cap
        except Exception as e:
            logger.warning("Failed to load capability registry: %s", e)
            _CAPABILITY_REGISTRY = {"capabilities": []}
            _CAPABILITY_BY_TOOL = {}
    return _CAPABILITY_REGISTRY, _CAPABILITY_BY_TOOL


def _get_capability_id(tool_name: str) -> str:
    """Resolve capability_id from tool name using capability_registry.json."""
    _, by_tool = _load_capability_registry()
    cap = by_tool.get(tool_name)
    if cap:
        return cap.get("capability_id", f"unknown.{tool_name}")
    return f"unknown.{tool_name}"


# ── Verdict extraction helpers ──────────────────────────────────────────────


def _extract_canonical_verdict(response: dict[str, Any]) -> str:
    """Extract the dominant canonical_verdict from the response.

    Priority order: effective_verdict → top-level verdict → result.verdict → status → session.verdict → PROCEED
    """
    top_ev = response.get("effective_verdict") or response.get("verdict")
    if top_ev and str(top_ev).upper() in ("SEAL", "HOLD", "SABAR", "VOID", "PROCEED", "DENY"):
        _map = {"SEAL": "PROCEED", "SABAR": "HOLD", "PARTIAL": "PROCEED"}
        return _map.get(str(top_ev).upper(), str(top_ev).upper())

    # Check result sub-object first (deepest signal)
    result = response.get("result")
    if isinstance(result, dict):
        rv = result.get("verdict")
        if rv and rv in ("SEAL", "HOLD", "SABAR", "VOID", "PROCEED", "DENY"):
            # Map kernel verdicts to canonical set: SEAL→PROCEED, SABAR→HOLD
            _map = {"SEAL": "PROCEED", "SABAR": "HOLD", "PARTIAL": "PROCEED"}
            return _map.get(rv, rv)

    # Check session object
    session = response.get("session")
    if isinstance(session, dict):
        sv = session.get("verdict")
        if sv and sv in ("SEAL", "HOLD", "SABAR", "VOID"):
            _map = {"SEAL": "PROCEED", "SABAR": "HOLD"}
            return _map.get(sv, sv)

    # Check top-level status
    status = response.get("status", "")
    if status:
        _status_map = {
            "OK": "PROCEED",
            "HOLD": "HOLD",
            "ERROR": "HOLD",
            "VOID": "VOID",
            "FAIL": "DENY",
            "PENDING": "HOLD",
        }
        return _status_map.get(status, "HOLD")

    return "PROCEED"


def _extract_authority_scope(response: dict[str, Any]) -> str:
    """Extract authority scope from response or session."""
    # Check session
    session = response.get("session")
    if isinstance(session, dict):
        authority = session.get("authority", "")
        if authority in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL"):
            return authority

    # Check actor
    actor = response.get("actor")
    if isinstance(actor, dict):
        level = actor.get("authority_level", "")
        if level == "ANONYMOUS":
            return "OBSERVE_ONLY"

    # Check meta
    meta = response.get("meta", {}) if isinstance(response.get("meta"), dict) else {}
    mode = meta.get("authority_mode", "")
    if mode in ("OBSERVE_ONLY", "LIMITED_MUTATE", "FULL"):
        return mode

    return "OBSERVE_ONLY"


def _extract_receipt_state(response: dict[str, Any]) -> str:
    """Extract receipt state based on whether a seal was written."""
    result = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    # If seal was involved and succeeded
    vault_entry = result.get("vault_entry_id") or result.get("merkle_root")
    if vault_entry:
        return "SEALED"

    # Check if session has been sealed
    session = response.get("session", {}) if isinstance(response.get("session"), dict) else {}
    if session.get("verdict") == "SEAL":
        return "SEALED"

    # Check if there's a receipt_id
    receipt_id = result.get("receipt_id")
    if receipt_id:
        return "SEALED"

    return "UNSEALED"


def _extract_reason_code(
    tool_name: str,
    canonical_verdict: str,
    response: dict[str, Any],
) -> str:
    """Extract or derive a machine-readable reason code."""
    # Check top-level response first
    top_rc = response.get("reason_code")
    if top_rc:
        return str(top_rc)

    # Check for existing reason codes in meta
    meta = response.get("meta", {}) if isinstance(response.get("meta"), dict) else {}
    reason_code = meta.get("reason_code") or meta.get("reason", "")
    if reason_code:
        return str(reason_code)

    # Check result for reason
    result = response.get("result", {}) if isinstance(response.get("result"), dict) else {}
    reason = result.get("reason", "")
    if reason:
        return str(reason)

    # Derive from verdict + tool
    if canonical_verdict == "HOLD":
        if tool_name == "arif_init":
            return "IDENTITY_UNVERIFIED"
        elif tool_name == "arif_forge":
            return "AUTHORITY_INSUFFICIENT"
        elif tool_name == "arif_judge":
            return "CONSTITUTIONAL_BLOCK"
        else:
            return "HOLD_NO_REASON"

    return "OK"


def _extract_can_mutate(canonical_verdict: str, authority_scope: str) -> bool:
    """Derive mutate permission from verdict + scope."""
    if canonical_verdict in ("DENY", "VOID"):
        return False
    if canonical_verdict == "HOLD":
        return False
    return authority_scope in ("LIMITED_MUTATE", "FULL")


def _extract_can_claim_success(
    canonical_verdict: str,
    execution_state: str,
) -> bool:
    """Derive success claim permission."""
    if canonical_verdict == "PROCEED" and execution_state == "COMPLETED":
        return True
    return False


# ── Main V2 envelope builder ───────────────────────────────────────────────


# Map of known canonical tool names for validation
CANONICAL_TOOL_NAMES = frozenset(
    {
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    }
)


def build_v2_envelope(tool_name: str, response: dict[str, Any]) -> dict[str, Any]:
    """Wrap a tool response with the V2 envelope.

    The V2 envelope is always the outermost layer. It adds deterministic
    top-level fields without modifying the tool-specific result data.

    Args:
        tool_name: The canonical tool name (e.g. 'arif_init')
        response: The raw response dict from the tool handler

    Returns:
        The response dict with V2 envelope fields injected at top level.
    """
    if not isinstance(response, dict):
        return response

    # Only wrap canonical tools
    if tool_name not in CANONICAL_TOOL_NAMES:
        return response

    # Determine execution state
    status = response.get("status", "")
    execution_state_map = {
        "OK": "COMPLETED",
        "HOLD": "FAILED",
        "ERROR": "FAILED",
        "VOID": "FAILED",
        "FAIL": "FAILED",
        "PENDING": "RUNNING",
    }
    execution_state = execution_state_map.get(status, "COMPLETED")

    # Extract V2 fields from existing response
    canonical_verdict = _extract_canonical_verdict(response)
    authority_scope = _extract_authority_scope(response)
    receipt_state = _extract_receipt_state(response)
    capability_id = _get_capability_id(tool_name)
    reason_code = _extract_reason_code(tool_name, canonical_verdict, response)

    # Set permission flags
    can_mutate = _extract_can_mutate(canonical_verdict, authority_scope)
    can_claim_success = _extract_can_claim_success(canonical_verdict, execution_state)

    # Build the V2 envelope. Add as top-level fields directly
    # (the existing response already has 'status', 'result', 'meta' etc.)
    envelope = dict(response)

    # Inject V2 fields at top level (never override existing data)
    envelope.setdefault("schema_version", "2.0.0")
    envelope.setdefault("capability_id", capability_id)
    envelope.setdefault("implementation_tool", tool_name)
    envelope.setdefault("canonical_verdict", canonical_verdict)
    envelope.setdefault("reason_code", reason_code)
    envelope.setdefault("authority_scope", authority_scope)
    envelope.setdefault("receipt_state", receipt_state)
    envelope.setdefault("execution_state", execution_state)
    envelope.setdefault("can_continue_observing", True)
    envelope.setdefault("can_mutate", can_mutate)
    envelope.setdefault("can_claim_success", can_claim_success)

    # Extract facts/inferences/unknowns if result has them
    result = response.get("result", {})
    if isinstance(result, dict):
        envelope.setdefault("facts", result.get("facts", []))
        envelope.setdefault("inferences", result.get("inferences", []))
        envelope.setdefault("unknowns", result.get("unknowns", []))
        envelope.setdefault("warnings", result.get("warnings", []))
        envelope.setdefault("evidence_refs", result.get("evidence_refs", []))
        envelope.setdefault("recommended_next", result.get("recommended_next", []))

    return envelope
