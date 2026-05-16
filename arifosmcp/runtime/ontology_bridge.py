"""
arifosmcp/runtime/ontology_bridge.py
═══════════════════════════════════════════════════════════════════════════════════════
Bridge between raw tool outputs and the Unified Constitutional Ontology.

Every tool result is canonicalized into ConstitutionalOntologyPayload before
state progression. This ensures the kernel always has a typed, validated view
of what happened, even if the underlying tool emitted an ad-hoc dict.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.executor import ExecutionState

try:
    from core.shared.constitutional_ontology import (
        ConfidenceLevel,
        ConstitutionalOntologyPayload,
        OntologyValidator,
        Reversibility,
        RiskLevel,
        RuntimeState,
        ValidationResult,
    )
except ImportError:
    # Fallback if core.shared is not on PATH (e.g., during isolated tests)
    ConstitutionalOntologyPayload = None  # type: ignore[misc,assignment]
    OntologyValidator = None  # type: ignore[misc,assignment]
    ValidationResult = None  # type: ignore[misc,assignment]
    RuntimeState = None  # type: ignore[misc,assignment]
    RiskLevel = None  # type: ignore[misc,assignment]
    ConfidenceLevel = None  # type: ignore[misc,assignment]
    Reversibility = None  # type: ignore[misc,assignment]

# ═══════════════════════════════════════════════════════════════════════════════════════
# ENV GATE
# ═══════════════════════════════════════════════════════════════════════════════════════

_ONTOLOGY_VALIDATE = os.getenv("ARIFOS_ONTOLOGY_VALIDATE", "false").lower() in (
    "1",
    "true",
    "yes",
)

# Domain mapping: tool prefix → canonical domain
_TOOL_DOMAIN_MAP: dict[str, str] = {
    "arif_session_init": "ARIFOS",
    "arif_sense_observe": "ARIFOS",
    "arif_evidence_fetch": "ARIFOS",
    "arif_ops_measure": "ARIFOS",
    "arif_memory_recall": "ARIFOS",
    "arif_kernel_route": "ARIFOS",
    "arif_mind_reason": "ARIFOS",
    "arif_heart_critique": "ARIFOS",
    "arif_judge_deliberate": "ARIFOS",
    "arif_gateway_connect": "ARIFOS",
    "arif_forge_execute": "ARIFOS",
    "arif_reply_compose": "ARIFOS",
    "arif_vault_seal": "ARIFOS",
    # Domain bridges (when called via federation)
    "arif_well_": "WELL",
    "arif_geox_": "GEOX",
    "arif_wealth_": "WEALTH",
    "arif_aaa_": "AAA",
    "arif_apex_": "APEX",
}


def _resolve_domain(tool_name: str) -> str:
    """Map a tool name to its canonical domain."""
    for prefix, domain in _TOOL_DOMAIN_MAP.items():
        if tool_name.startswith(prefix):
            return domain
    return "ARIFOS"


def _execution_state_to_runtime_state(execution_state: ExecutionState | None) -> str:
    """Map ExecutionState → RuntimeState string value."""
    mapping = {
        ExecutionState.OBSERVE: "OBSERVE",
        ExecutionState.ANALYZE: "ANALYZE",
        ExecutionState.SIMULATE: "SIMULATE",
        ExecutionState.AWAIT_APPROVAL: "AWAIT_APPROVAL",
        ExecutionState.EXECUTE: "EXECUTE",
        ExecutionState.VERIFY: "VERIFY",
        ExecutionState.SEAL: "SEAL",
    }
    return mapping.get(execution_state, "OBSERVE") if execution_state else "OBSERVE"


def _extract_from_result(result: dict[str, Any], key: str, default: Any = None) -> Any:
    """Deep-safe extraction from a potentially nested tool result."""
    if not isinstance(result, dict):
        return default
    # Try top level
    if key in result:
        return result[key]
    # Try nested common locations
    for path in ("result", "payload", "data", "output", "governance", "meta"):
        nested = result.get(path)
        if isinstance(nested, dict) and key in nested:
            return nested[key]
    return default


class OntologyBridge:
    """
    Canonicalizes raw tool outputs into ConstitutionalOntologyPayload.

    This is the integration layer between:
    - Execution State Machine (runtime state tracking)
    - Constitutional Ontology (unified schema)
    - Tool handlers (ad-hoc dict outputs)
    """

    def __init__(self, strict: bool = False):
        self.strict = strict
        self._validator = OntologyValidator(strict=strict) if OntologyValidator else None

    @staticmethod
    def is_validation_enabled() -> bool:
        return _ONTOLOGY_VALIDATE

    def canonicalize(
        self,
        tool_name: str,
        result: dict[str, Any],
        *,
        session_id: str | None,
        actor_id: str,
        execution_state: ExecutionState | None,
    ) -> dict[str, Any]:
        """
        Wrap a raw tool result with canonical ontology fields.

        Returns a dict that can be passed to OntologyValidator.validate().
        Does NOT modify the original result.
        """
        if ConstitutionalOntologyPayload is None:
            # Ontology not available — pass through
            return dict(result)

        now = datetime.now(UTC)

        # Build canonical payload from runtime context + tool output
        canonical: dict[str, Any] = {
            "session_id": session_id or str(uuid.uuid4()),
            "trace_id": str(uuid.uuid4()),
            "state": _execution_state_to_runtime_state(execution_state),
            "domain": _resolve_domain(tool_name),
            "actor_id": actor_id,
            "authority_level": "operator",
            "timestamp": now.isoformat(),
            "kernel_epoch": "v2026.05",
            # Extract from tool result where available
            "risk": _extract_from_result(result, "risk", "UNKNOWN"),
            "confidence": _extract_from_result(result, "confidence", "UNKNOWN"),
            "reversibility": _extract_from_result(result, "reversibility", "UNKNOWN"),
            "observation": _extract_from_result(result, "observation", ""),
            "analysis": _extract_from_result(result, "analysis", ""),
            "assumption": _extract_from_result(result, "assumption", ""),
            "action": _extract_from_result(result, "action", ""),
            "verdict": _extract_from_result(result, "verdict", "SEAL"),
            "entropy_delta": _extract_from_result(result, "entropy_delta", 0.0),
            "stability": _extract_from_result(result, "stability", 1.0),
            "evidence_chain": _extract_from_result(result, "evidence_chain", []),
            "sources": _extract_from_result(result, "sources", []),
            "floors_passed": _extract_from_result(result, "floors_passed", []),
            "floors_failed": _extract_from_result(result, "floors_failed", []),
            "floors_pending": _extract_from_result(result, "floors_pending", []),
        }

        # Preserve original result inside the canonical envelope
        canonical["_raw_result"] = dict(result)
        return canonical

    def validate_canonicalized(self, canonical: dict[str, Any]) -> dict[str, Any]:
        """
        Validate a canonicalized payload.

        Returns a dict with:
            - ontology_valid: bool
            - ontology_error: str | None
            - ontology_payload: dict | None
        """
        if self._validator is None or not _ONTOLOGY_VALIDATE:
            return {
                "ontology_valid": True,
                "ontology_error": None,
                "ontology_payload": canonical,
            }

        validation = self._validator.validate(canonical)
        return {
            "ontology_valid": validation.valid,
            "ontology_error": validation.error,
            "ontology_payload": (
                validation.payload.model_dump(mode="json") if validation.payload else canonical
            ),
        }

    def process(
        self,
        tool_name: str,
        result: dict[str, Any],
        *,
        session_id: str | None,
        actor_id: str,
        execution_state: ExecutionState | None,
    ) -> dict[str, Any]:
        """
        Full pipeline: canonicalize → validate → merge metadata back into result.

        The original result is preserved; ontology metadata is added under
        the "ontology" key.
        """
        canonical = self.canonicalize(
            tool_name=tool_name,
            result=result,
            session_id=session_id,
            actor_id=actor_id,
            execution_state=execution_state,
        )
        validation = self.validate_canonicalized(canonical)

        # Merge back into the original result without destroying it
        enriched = dict(result)
        enriched["ontology"] = {
            "canonical": canonical,
            "validation": validation,
            "enforced": _ONTOLOGY_VALIDATE,
        }
        return enriched


# Singleton
ontology_bridge = OntologyBridge(strict=False)
