"""
arifosmcp/runtime/context_witness.py — arifOS Context Witness v2

Orchestrates the retrieval, interpretation, and safety validation of
approved wisdom quotes.  SEA-LION acts strictly as an interpreter;
quotes are always drawn from the locked ledger.

Pipeline:
1. load ledger
2. retrieve top 3 approved quote witnesses
3. pass candidate quotes to SEA-LION interpreter
4. validate SEA-LION output with context_safety
5. enforce governance boundary
6. emit structured response

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from .quote_ledger import get_quote_by_id, load_quote_ledger
from .quote_retriever import retrieve_witnesses
from .sea_lion_interpreter import fallback_interpret, interpret_with_sea_lion, InterpretationError
from .context_safety import validate_interpretation_safety

logger = logging.getLogger(__name__)
GOVERNANCE_DOMAINS = {"governance", "ethics", "conflict", "identity", "authority"}

# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE BOUNDARY
# ═══════════════════════════════════════════════════════════════════════════════


def _apply_governance_boundary(
    safe_output: dict[str, Any],
    risk_level: str,
) -> dict[str, Any]:
    """Apply hard governance overrides that no interpretation may override.

    - High / critical / irreversible -> human_decision_required = true
    - Irreversible -> recommended_action must not execute
    """
    is_high_risk = risk_level in ("high", "critical", "irreversible")
    is_irreversible = risk_level == "irreversible"

    safe_output["human_decision_required"] = safe_output.get("human_decision_required", False) or is_high_risk

    if is_irreversible:
        action = str(safe_output.get("recommended_action", "")).lower()
        forbidden = ("execute", "commit", "deploy", "seal", "push", "destroy", "delete", "drop")
        if any(word in action for word in forbidden):
            safe_output["recommended_action"] = "HOLD — irreversible action requires explicit human ratification."
            safe_output["safety_notes"] = list(safe_output.get("safety_notes", [])) + [
                "GOVERNANCE OVERRIDE: Irreversible risk detected. Autonomous execution blocked."
            ]

    return safe_output


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


async def arifos_context_witness(
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    risk_level: str = "low",
    domain: str = "governance",
    language: str = "en",
    audience: str = "agent",
    include_quote: bool = True,
) -> dict[str, Any]:
    """Main Context Witness pipeline.

    Returns structured response with status ok | partial | hold | refuse.
    """
    # ── 1. Load ledger ──
    try:
        load_quote_ledger()
    except Exception as exc:
        logger.error("Ledger load failed: %s", exc)
        return {
            "status": "hold",
            "meaning": "Quote ledger unavailable.",
            "quote_witness": None,
            "interpretation": "System cannot retrieve wisdom witnesses.",
            "arifos_alignment": {"physics": "", "math": "", "linguistic": ""},
            "decision_boundary": "No autonomous action without ledger.",
            "human_decision_required": risk_level in ("high", "critical", "irreversible"),
            "recommended_action": "HOLD — inspect ledger integrity.",
            "uncertainty": ["Ledger load error."],
            "safety_notes": [str(exc)],
        }

    # ── 2. Retrieve top-k approved quotes ──
    candidates = retrieve_witnesses(
        event=event,
        domain=domain,
        risk_level=risk_level,
        top_k=3,
    )

    if not candidates:
        logger.warning("No approved candidates for event=%r domain=%r risk=%r", event, domain, risk_level)
        return {
            "status": "hold",
            "meaning": "No approved quote witnesses match this situation.",
            "quote_witness": None,
            "interpretation": "The event falls outside the current coverage of the wisdom ledger.",
            "arifos_alignment": {"physics": "", "math": "", "linguistic": ""},
            "decision_boundary": "No autonomous action without witness.",
            "human_decision_required": risk_level in ("high", "critical", "irreversible"),
            "recommended_action": "HOLD — expand ledger or defer to human judgment.",
            "uncertainty": ["No matching quotes in approved ledger."],
            "safety_notes": ["Ledger coverage gap detected."],
        }

    # ── 3. SEA-LION interpretation (or fallback) ──
    sea_lion_ok = False
    interpretation: dict[str, Any] | None = None
    try:
        interpretation = await interpret_with_sea_lion(
            event=event,
            state=state,
            judgment=judgment,
            candidate_quotes=candidates,
            language=language,
        )
        sea_lion_ok = True
    except InterpretationError as exc:
        logger.warning("SEA-LION interpretation failed (%s); falling back to deterministic mode.", exc)
    except Exception as exc:
        logger.error("Unexpected error during SEA-LION call: %s", exc)

    if not sea_lion_ok or interpretation is None:
        interpretation = fallback_interpret(
            event=event,
            state=state,
            judgment=judgment,
            candidate_quotes=candidates,
            risk_level=risk_level,
            language=language,
        )

    # ── 4. Safety validation (fail-closed) ──
    safety = validate_interpretation_safety(
        interpretation=interpretation,
        candidate_quotes=candidates,
        risk_level=risk_level,
    )

    if safety["status"] != "ok":
        return {
            "status": safety["status"],
            "meaning": f"Safety gate triggered: {safety['error']}",
            "quote_witness": None,
            "interpretation": "The interpretation failed safety validation.",
            "arifos_alignment": {"physics": "", "math": "", "linguistic": ""},
            "decision_boundary": "No autonomous action while safety gate is active.",
            "human_decision_required": risk_level in ("high", "critical", "irreversible"),
            "recommended_action": "HOLD — review safety error and retry.",
            "uncertainty": [safety["error"] or "unknown safety failure"],
            "safety_notes": [safety["error_code"] or "safety_gate_failure"],
        }

    safe_output = safety["safe_output"]

    # ── 5. Governance boundary enforcement ──
    safe_output = _apply_governance_boundary(safe_output, risk_level)

    # ── 6. Resolve quote witness metadata from ledger ──
    selected_quote = get_quote_by_id(safe_output["selected_quote_id"])
    if selected_quote is None:
        # Defensive: should not happen after safety gate
        return {
            "status": "hold",
            "meaning": "Selected quote disappeared from ledger after safety check.",
            "quote_witness": None,
            "interpretation": "Race condition or ledger corruption suspected.",
            "arifos_alignment": safe_output.get("arifos_alignment", {"physics": "", "math": "", "linguistic": ""}),
            "decision_boundary": "No autonomous action.",
            "human_decision_required": risk_level in ("high", "critical", "irreversible"),
            "recommended_action": "HOLD — inspect ledger integrity.",
            "uncertainty": ["Ledger inconsistency."],
            "safety_notes": ["selected_quote_id not found in ledger post-safety."],
        }

    quote_witness = {
        "id": selected_quote["id"],
        "quote": selected_quote["quote"] if include_quote else "",
        "author": selected_quote["author"],
        "tradition": selected_quote.get("tradition", ""),
        "theme": selected_quote.get("theme", ""),
        "source_status": selected_quote.get("source_status", "curated"),
    }

    # ── 7. Emit structured response ──
    status = "ok" if sea_lion_ok else "partial"
    # If risk_level is irreversible, downgrade to partial as a signal
    if risk_level == "irreversible":
        status = "partial"

    return {
        "status": status,
        "meaning": safe_output["meaning"],
        "quote_witness": quote_witness,
        "interpretation": safe_output["interpretation"],
        "arifos_alignment": safe_output["arifos_alignment"],
        "decision_boundary": safe_output["decision_boundary"],
        "human_decision_required": safe_output["human_decision_required"],
        "recommended_action": safe_output["recommended_action"],
        "uncertainty": safe_output["uncertainty"],
        "safety_notes": safe_output["safety_notes"],
    }


def should_emit_context_witness(meta: dict[str, Any] | None = None) -> bool:
    payload = dict(meta or {})
    risk_level = str(payload.get("risk_level", "low")).lower()
    domain = str(payload.get("domain", "")).lower()
    audience = str(payload.get("audience", "machine")).lower()
    mode = str(payload.get("mode", "")).lower()
    explicit = bool(payload.get("emit_context_witness"))
    risk_trigger = risk_level in {"high", "critical", "irreversible"}
    mode_trigger = mode in {"governed", "witness"}
    domain_trigger = domain in GOVERNANCE_DOMAINS
    return explicit or mode_trigger or (risk_trigger and audience == "human" and domain_trigger)


def build_internal_context_witness(
    *,
    event: str,
    state: dict[str, Any],
    judgment: dict[str, Any],
    risk_level: str = "low",
    domain: str = "governance",
    audience: str = "human",
    include_quote: bool = True,
) -> dict[str, Any]:
    if audience.lower() != "human":
        return {}

    try:
        load_quote_ledger()
    except Exception as exc:
        return {
            "meaning": "Quote ledger unavailable.",
            "quote_witness": None,
            "interpretation": "System cannot retrieve context witnesses.",
            "boundary": "No autonomous action without ledger.",
            "human_decision_required": risk_level in {"high", "critical", "irreversible"},
            "recommended_action": "HOLD — inspect ledger integrity.",
            "safety_notes": [str(exc)],
        }

    candidates = retrieve_witnesses(
        event=event,
        domain=domain,
        risk_level=risk_level,
        top_k=3,
    )
    if not candidates:
        return {
            "meaning": "No approved quote witnesses match this situation.",
            "quote_witness": None,
            "interpretation": "The event falls outside the current coverage of the wisdom ledger.",
            "boundary": "No autonomous action without witness.",
            "human_decision_required": risk_level in {"high", "critical", "irreversible"},
            "recommended_action": "HOLD — expand ledger or defer to human judgment.",
            "safety_notes": ["Ledger coverage gap detected."],
        }

    interpretation = fallback_interpret(
        event=event,
        state=state,
        judgment=judgment,
        candidate_quotes=candidates,
        risk_level=risk_level,
    )
    safety = validate_interpretation_safety(
        interpretation=interpretation,
        candidate_quotes=candidates,
        risk_level=risk_level,
    )
    if safety["status"] != "ok":
        return {
            "meaning": f"Safety gate triggered: {safety['error']}",
            "quote_witness": None,
            "interpretation": "The interpretation failed safety validation.",
            "boundary": "No autonomous action while safety gate is active.",
            "human_decision_required": risk_level in {"high", "critical", "irreversible"},
            "recommended_action": "HOLD — review safety error and retry.",
            "safety_notes": [safety["error_code"] or "context_witness_safety_failure"],
        }

    safe_output = _apply_governance_boundary(safety["safe_output"], risk_level)
    selected_quote = get_quote_by_id(safe_output["selected_quote_id"])
    quote_witness = None
    if selected_quote is not None:
        quote_witness = {
            "id": selected_quote["id"],
            "quote": selected_quote["quote"] if include_quote else "",
            "author": selected_quote["author"],
        }

    return {
        "meaning": safe_output["meaning"],
        "quote_witness": quote_witness,
        "interpretation": safe_output["interpretation"],
        "boundary": safe_output["decision_boundary"],
        "human_decision_required": safe_output["human_decision_required"],
        "recommended_action": safe_output["recommended_action"],
        "safety_notes": safe_output["safety_notes"],
    }


__all__ = [
    "arifos_context_witness",
    "build_internal_context_witness",
    "should_emit_context_witness",
]
