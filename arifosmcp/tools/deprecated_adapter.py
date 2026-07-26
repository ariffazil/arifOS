"""
arifosmcp/tools/deprecated_adapter.py — DEPRECATED TOOL ADAPTER
═══════════════════════════════════════════════════════════

Maps 16 internal/absorbed tool names to their 8 canonical equivalents.
All emit deprecation warnings. Sunset: 2026-08-26 (30 days from P0).

Forged: 2026-07-26 under P0 canonical spine freeze.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

_SUNSET_DATE = "2026-08-26"

DEPRECATION_MAP: dict[str, dict[str, Any]] = {
    # ── Absorbed into arif_init ──
    "arif_triage": {
        "canonical_tool": "arif_init",
        "mode_override": "triage",
        "rationale": "arif_init(mode=triage) — session status, preflight, priority",
    },
    # ── Absorbed into arif_observe ──
    "arif_fetch": {
        "canonical_tool": "arif_observe",
        "mode_override": "fetch",
        "rationale": "arif_observe(mode=fetch) — governed URL evidence intake",
    },
    "arif_entropy_observe": {
        "canonical_tool": "arif_observe",
        "mode_override": "entropy_dS",
        "rationale": "arif_observe(mode=entropy_dS) — entropy delta measurement",
    },
    "arif_correction_probe": {
        "canonical_tool": "arif_observe",
        "mode_override": "hybrid_discovery",
        "rationale": "arif_observe(mode=hybrid_discovery) — correction/drift probe",
    },
    # ── Absorbed into arif_think ──
    "arif_critique": {
        "canonical_tool": "arif_think",
        "mode_override": "reflect",
        "rationale": "arif_think(mode=reflect) — self-critique and review",
    },
    "arif_challenge": {
        "canonical_tool": "arif_think",
        "mode_override": "verify",
        "rationale": "arif_think(mode=verify) — contradiction and challenge",
    },
    "arif_consequence_trace": {
        "canonical_tool": "arif_think",
        "mode_override": "simulate",
        "rationale": "arif_think(mode=simulate) — consequence tracing",
    },
    # ── Absorbed into arif_route ──
    "arif_bridge_connect": {
        "canonical_tool": "arif_route",
        "mode_override": "bridge",
        "rationale": "arif_route(mode=bridge) — direct organ tool bridge",
    },
    "arif_entropy_route": {
        "canonical_tool": "arif_route",
        "mode_override": "route",
        "rationale": "arif_route(mode=route) — entropy-aware routing",
    },
    # ── Absorbed into arif_judge ──
    "arif_kernel_intercept": {
        "canonical_tool": "arif_judge",
        "mode_override": "intercept",
        "rationale": "arif_judge(mode=intercept) — minimum constitutional kernel intercept",
    },
    "arif_judge_deliberate": {
        "canonical_tool": "arif_judge",
        "mode_override": "validate",
        "rationale": "arif_judge(mode=validate) — formal constitutional deliberation",
    },
    "arif_j_state_assess": {
        "canonical_tool": "arif_judge",
        "mode_override": "hold",
        "rationale": "arif_judge(mode=hold) — state assessment and gating",
    },
    "arif_j_gate": {
        "canonical_tool": "arif_judge",
        "mode_override": "escalate",
        "rationale": "arif_judge(mode=escalate) — gate check for authority",
    },
    # ── Absorbed into arif_forge ──
    "arif_compose": {
        "canonical_tool": "arif_forge",
        "mode_override": "generate",
        "rationale": "arif_forge(mode=generate) — artifact composition",
    },
    "arif_act": {
        "canonical_tool": "arif_forge",
        "mode_override": "write",
        "rationale": "arif_forge(mode=write) — governed action execution",
    },
    # ── Absorbed (measurement) ──
    "arif_measure": {
        "canonical_tool": "arif_judge",
        "mode_override": "validate",
        "rationale": "arif_judge(mode=validate) — evidence-based measurement",
    },
}


def is_deprecated(tool_name: str) -> bool:
    return tool_name in DEPRECATION_MAP


def map_to_canonical(tool_name: str) -> dict[str, Any] | None:  # type: ignore[return-type]
    if not is_deprecated(tool_name):
        return None
    entry = DEPRECATION_MAP[tool_name]
    return {
        "canonical_tool": entry["canonical_tool"],
        "mode_override": entry["mode_override"],
        "warning": (
            f"DEPRECATED: '{tool_name}' → '{entry['canonical_tool']}(mode={entry['mode_override']})'. "
            f"{entry['rationale']}. "
            f"Sunset: {_SUNSET_DATE}. Update your tool calls."
        ),
        "sunset": _SUNSET_DATE,
    }


def wrap_deprecated_call(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    If tool_name is deprecated, emit warning and return rerouted call info.
    Otherwise return None (not deprecated).
    """
    mapping = map_to_canonical(tool_name)
    if mapping is None:
        return None

    logger.warning(mapping["warning"])

    args = dict(arguments or {})
    args["mode"] = args.get("mode") or mapping["mode_override"]

    return {
        "reroute": True,
        "canonical_tool": mapping["canonical_tool"],
        "arguments": args,
        "warning": mapping["warning"],
        "sunset": mapping["sunset"],
    }


def validate_no_deprecated(tool_call: str, caller: str = "unknown") -> dict[str, Any]:
    """Check if a tool call uses a deprecated name. Returns routing decision."""
    if is_deprecated(tool_call):
        mapping = map_to_canonical(tool_call)
        return {
            "verdict": "DEPRECATED",
            "tool": tool_call,
            "canonical": mapping["canonical_tool"],
            "mode": mapping["mode_override"],
            "warning": mapping["warning"],
            "caller": caller,
            "sunset": mapping["sunset"],
        }
    return {
        "verdict": "OK",
        "tool": tool_call,
        "caller": caller,
    }


def deprecated_tool_names() -> list[str]:
    return sorted(DEPRECATION_MAP.keys())


def canonical_tool_names() -> list[str]:
    """The 8 canonical tools per ABI."""
    return [
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
        "arif_seal",
    ]


def verify_no_orphan_tools() -> dict[str, Any]:
    """Check that all deprecated tools map to valid canonical tools."""
    canonical = set(canonical_tool_names())
    errors = []
    for old, entry in DEPRECATION_MAP.items():
        if entry["canonical_tool"] not in canonical:
            errors.append(f"{old} → {entry['canonical_tool']} (INVALID CANONICAL)")
    return {
        "ok": not errors,
        "deprecated_count": len(DEPRECATION_MAP),
        "canonical_count": len(canonical),
        "errors": errors,
        "sunset": _SUNSET_DATE,
        "forged": "2026-07-26",
    }
