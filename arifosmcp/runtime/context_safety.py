"""
arifosmcp/runtime/context_safety.py — Context Witness Safety Gate

Fail-closed validator for SEA-LION interpretation output.
Does NOT silently rewrite hallucinated output.
Does NOT allow unauthorized quotes.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from .quote_ledger import get_quote_by_id

logger = logging.getLogger(__name__)


def validate_interpretation_safety(
    interpretation: dict[str, Any],
    candidate_quotes: list[dict[str, Any]],
    risk_level: str = "medium",
) -> dict[str, Any]:
    """Validate a SEA-LION interpretation against safety rules.

    Returns a dict:
    {
        "status": "ok" | "hold" | "refuse",
        "error": str | None,
        "error_code": str | None,
        "safe_output": dict[str, Any] | None,
    }

    Rules (fail-closed):
    1. selected_quote_id must be in candidate_quotes.
    2. Quote text must match ledger exactly.
    3. Author must match ledger exactly.
    4. If risk_level in (high, critical, irreversible): human_decision_required=true.
    5. If risk_level == irreversible: recommended_action must NOT execute.
    6. Missing required fields -> hold.
    """
    candidate_ids = {q["id"] for q in candidate_quotes}

    # ── Rule 1: selected_quote_id must exist ──
    required = {
        "selected_quote_id",
        "meaning",
        "interpretation",
        "arifos_alignment",
        "decision_boundary",
        "human_decision_required",
        "recommended_action",
        "uncertainty",
        "safety_notes",
    }
    missing = required - set(interpretation.keys())
    if missing:
        return {
            "status": "hold",
            "error": f"Missing required fields: {sorted(missing)}",
            "error_code": "schema_incomplete",
            "safe_output": None,
        }

    selected_id = interpretation.get("selected_quote_id")
    if not selected_id or not isinstance(selected_id, str):
        return {
            "status": "hold",
            "error": "selected_quote_id missing or not string",
            "error_code": "quote_not_in_approved_ledger",
            "safe_output": None,
        }

    if selected_id not in candidate_ids:
        return {
            "status": "hold",
            "error": "selected_quote_id not in approved candidate list",
            "error_code": "quote_not_in_approved_ledger",
            "safe_output": None,
        }

    # Resolve ledger truth
    ledger_quote = get_quote_by_id(selected_id)
    if not ledger_quote:
        return {
            "status": "hold",
            "error": f"Quote {selected_id} not found in ledger",
            "error_code": "quote_not_in_approved_ledger",
            "safe_output": None,
        }

    # ── Rule 2: Exact Quote Text Validation ──
    output_quote = interpretation.get("quote")
    if output_quote is not None:
        if output_quote.strip() != ledger_quote["quote"].strip():
            return {
                "status": "hold",
                "error": "quote_integrity_failed",
                "error_code": "quote_integrity_failed",
                "safe_output": None,
            }

    # ── Rule 3: Exact Author Validation ──
    output_author = interpretation.get("author")
    if output_author is not None:
        if output_author.strip() != ledger_quote["author"].strip():
            return {
                "status": "hold",
                "error": "author_integrity_failed",
                "error_code": "author_integrity_failed",
                "safe_output": None,
            }

    # ── Rule 5: Irreversible Action Check (runs first — refuse is stronger than hold) ──
    if risk_level == "irreversible":
        action = str(interpretation.get("recommended_action", "")).lower()
        forbidden = (
            "execute",
            "commit",
            "deploy",
            "seal",
            "push",
            "destroy",
            "delete",
            "drop",
        )
        if any(word in action for word in forbidden):
            return {
                "status": "refuse",
                "error": "recommended_action for irreversible risk must not execute",
                "error_code": "governance_boundary_violation",
                "safe_output": None,
            }

    # ── Rule 6: High-Risk Human Decision Required ──
    is_high_risk = risk_level in ("high", "critical", "irreversible")
    human_required = bool(interpretation.get("human_decision_required", False))

    if is_high_risk and not human_required:
        return {
            "status": "hold",
            "error": "human_decision_required must be true for high/critical/irreversible risk",
            "error_code": "governance_boundary_violation",
            "safe_output": None,
        }

    # ── Success: Build Safe Output ──
    safe_output = {
        "selected_quote_id": selected_id,
        "meaning": str(interpretation["meaning"]),
        "interpretation": str(interpretation["interpretation"]),
        "arifos_alignment": {
            "physics": str(
                interpretation.get("arifos_alignment", {}).get("physics", "")
            ),
            "math": str(interpretation.get("arifos_alignment", {}).get("math", "")),
            "linguistic": str(
                interpretation.get("arifos_alignment", {}).get("linguistic", "")
            ),
        },
        "decision_boundary": str(interpretation["decision_boundary"]),
        "human_decision_required": human_required,
        "recommended_action": str(interpretation["recommended_action"]),
        "uncertainty": list(interpretation.get("uncertainty", [])),
        "safety_notes": list(interpretation.get("safety_notes", [])),
    }

    return {
        "status": "ok",
        "error": None,
        "error_code": None,
        "safe_output": safe_output,
    }
