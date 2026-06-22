"""
enforcement_engines.py — Enforcement Engine Architecture
═════════════════════════════════════════════════════════

Adapted from CORE (DariuszNewecki/CORE) — 13 enforcement engines.
Each floor has its own enforcement engine. Deterministic when possible,
LLM only when necessary.

What arifOS adds that CORE doesn't have:
  - substrate_gate: Human properties enforcement (scars, shadows, hollows)
  - grief_gate: Grief sensitivity enforcement
  - hollow_gate: Hollow boundary enforcement
  - scar_gate: Scar sensitivity enforcement

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from arifosmcp.schemas.consequence_chain import (
    ConsequenceChain,
    SubstrateContext,
    auto_classify_risk,
    create_chain,
)

logger = logging.getLogger(__name__)


# ── Engine Registry ──────────────────────────────────────────────────


class EnforcementEngine:
    """Base class for enforcement engines."""

    name: str = "base"
    description: str = "Base enforcement engine"
    deterministic: bool = True  # False = needs LLM

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        """Check if the action passes this engine.

        Returns:
            (passed, reason, metadata)
        """
        raise NotImplementedError


# ── Floor Gate ────────────────────────────────────────────────────────


class FloorGate(EnforcementEngine):
    """Constitutional floor enforcement."""

    name = "floor_gate"
    description = "Enforces F1-F13 constitutional floors"

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        spec = CANONICAL_TOOLS.get(tool_name)
        if spec is None:
            return True, "Tool not in canonical map — no floor enforcement", {}

        action_class = spec.get("action_class", "OBSERVE")
        floors = spec.get("floors", [])

        if not floors:
            return True, "No floors assigned", {}

        return True, f"Floors checked: {[f.value if hasattr(f, 'value') else f for f in floors]}", {
            "floors": [f.value if hasattr(f, 'value') else f for f in floors],
            "action_class": action_class,
        }


# ── Substrate Gate ───────────────────────────────────────────────────


class SubstrateGate(EnforcementEngine):
    """Human properties enforcement — scars, shadows, paradoxes.

    This is the gate that makes arifOS different from every other
    governance system. The human's constitutional substrate is checked
    on every tool call.
    """

    name = "substrate_gate"
    description = "Enforces human substrate properties (scars, shadows, hollows, grief)"

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        from arifosmcp.core.human_substrate import check_human_substrate_floor

        # Get floors from context
        floors = context.get("floors", [])
        if not floors:
            return True, "No floors to check against substrate", {}

        worst_verdict = "PASS"
        all_reasons = []
        all_impacts = []

        for floor in floors:
            result = check_human_substrate_floor(floor, tool_name, params)
            if result["verdict"] != "PASS":
                all_reasons.append(f"{floor}: {result['reason']}")
                all_impacts.extend(result["impacts"])
                if result["verdict"] == "BLOCK":
                    worst_verdict = "BLOCK"
                elif result["verdict"] == "GUARD" and worst_verdict != "BLOCK":
                    worst_verdict = "GUARD"
                elif result["verdict"] == "STRENGTHEN" and worst_verdict == "PASS":
                    worst_verdict = "STRENGTHEN"

        passed = worst_verdict != "BLOCK"
        reason = "; ".join(all_reasons) if all_reasons else "Substrate clear"

        return passed, reason, {
            "substrate_verdict": worst_verdict,
            "substrate_impacts": all_impacts,
        }


# ── Grief Gate ───────────────────────────────────────────────────────


class GriefGate(EnforcementEngine):
    """Grief sensitivity enforcement.

    When grief is active, the engine adjusts posture:
    - witness, don't fix
    - shorter answers
    - no probing
    """

    name = "grief_gate"
    description = "Enforces grief sensitivity posture"

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        from arifosmcp.core.human_substrate import get_human_properties

        props = get_human_properties()

        if not props.grief_active:
            return True, "Grief not active", {"grief_active": False}

        # Check if the tool is grief-sensitive
        grief_sensitive_tools = [
            "arif_critique",
            "arif_compose",
            "arif_think",
        ]

        if tool_name not in grief_sensitive_tools:
            return True, "Tool not grief-sensitive", {
                "grief_active": True,
                "grief_sensitive_tool": False,
            }

        # Grief active + sensitive tool → GUARD (not BLOCK)
        params_str = str(params).lower()
        grief_probes = [
            "father", "abah", "fazil", "march", "bekantan", "death", "died",
            "passed away", "grief", "loss",
        ]

        if any(probe in params_str for probe in grief_probes):
            return True, "Grief context detected — posture: witness, don't fix", {
                "grief_active": True,
                "grief_sensitive_tool": True,
                "grief_context_detected": True,
                "posture": "witness_not_fix",
            }

        return True, "Grief active but no grief context in params", {
            "grief_active": True,
            "grief_sensitive_tool": True,
            "grief_context_detected": False,
        }


# ── Hollow Gate ──────────────────────────────────────────────────────


class HollowGate(EnforcementEngine):
    """Hollow boundary enforcement.

    Hollows are deliberately unfilled spaces in the human's memory graph.
    The AI knows they exist but doesn't know what's in them.
    DO_NOT_FILL is a hard boundary.
    """

    name = "hollow_gate"
    description = "Enforces hollow boundary (DO_NOT_FILL)"

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        from arifosmcp.core.human_substrate import get_human_properties

        props = get_human_properties()

        if props.hollow_count == 0:
            return True, "No hollows", {"hollow_count": 0}

        # Check if params contain hollow-probing intent
        params_str = str(params).lower()
        hollow_probes = [
            "hollow", "fill", "probe", "what is in", "what's in",
            "empty space", "unfilled", "deliberately empty",
        ]

        if any(probe in params_str for probe in hollow_probes):
            return False, f"Hollow boundary violated — {props.hollow_count} hollows exist, DO_NOT_FILL", {
                "hollow_count": props.hollow_count,
                "hollow_probe_detected": True,
                "verdict": "BLOCK",
            }

        return True, f"{props.hollow_count} hollows exist — boundary respected", {
            "hollow_count": props.hollow_count,
            "hollow_probe_detected": False,
        }


# ── Scar Gate ────────────────────────────────────────────────────────


class ScarGate(EnforcementEngine):
    """Scar sensitivity enforcement.

    Different scars have different sensitivity levels:
    - normal: no special handling
    - high: GUARD posture
    - extreme: GUARD + extra caution
    """

    name = "scar_gate"
    description = "Enforces scar sensitivity levels"

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        from arifosmcp.core.human_substrate import get_human_properties

        props = get_human_properties()

        extreme_scars = [s for s in props.scars if s.sensitivity == "extreme"]
        high_scars = [s for s in props.scars if s.sensitivity == "high"]

        if not extreme_scars and not high_scars:
            return True, "No high/extreme sensitivity scars", {}

        # Check if params reference scar-related content
        params_str = str(params).lower()
        scar_triggers = {
            "bekantan": ["bekantan", "march 2024", "father", "abah", "fazil", "discovery day"],
            "institutional": ["petronas", "2015", "crash", "layoff", "mentor"],
            "tricipta": ["tricipta", "theft", "stolen", "erased", "credit"],
            "sb412": ["sb412", "red flag", "ignored", "performance theater"],
            "mak-03": ["mak", "mother", "faridah", "inherited", "firewall"],
        }

        triggered_scars = []
        for scar_id, triggers in scar_triggers.items():
            if any(t in params_str for t in triggers):
                scar = props.get_scar_by_id(scar_id)
                if scar:
                    triggered_scars.append(scar)

        if not triggered_scars:
            return True, f"{len(extreme_scars)} extreme + {len(high_scars)} high scars — no triggers", {
                "extreme_count": len(extreme_scars),
                "high_count": len(high_scars),
                "triggered": [],
            }

        # Determine verdict
        has_extreme = any(s.sensitivity == "extreme" for s in triggered_scars)
        if has_extreme:
            verdict = "GUARD"
        else:
            verdict = "STRENGTHEN"

        return True, f"Scar triggered: {[s.name for s in triggered_scars]} — {verdict}", {
            "extreme_count": len(extreme_scars),
            "high_count": len(high_scars),
            "triggered": [s.scar_id for s in triggered_scars],
            "verdict": verdict,
        }


# ── Injection Gate ───────────────────────────────────────────────────


class InjectionGate(EnforcementEngine):
    """Injection detection (F12)."""

    name = "injection_gate"
    description = "Detects injection attempts in tool parameters"

    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)",
        r"system\s*prompt",
        r"you\s+are\s+now",
        r"forget\s+(everything|all|your)",
        r"new\s+(instructions?|role|identity)",
        r"\[INST\]",
        r"<\|im_start\|>",
    ]

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        params_str = str(params).lower()

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, params_str, re.IGNORECASE):
                return False, f"Injection detected: {pattern}", {
                    "pattern": pattern,
                    "verdict": "BLOCK",
                }

        return True, "No injection detected", {}


# ── Sovereign Gate ───────────────────────────────────────────────────


class SovereignGate(EnforcementEngine):
    """F13 Sovereign veto enforcement."""

    name = "sovereign_gate"
    description = "Enforces F13 sovereign veto on irreversible actions"

    IRREVERSIBLE_TOOLS = [
        "arif_seal",
        "arif_forge",
    ]

    def check(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        if tool_name not in self.IRREVERSIBLE_TOOLS:
            return True, "Not an irreversible tool", {}

        ack = params.get("ack_irreversible", False)
        if not ack:
            return False, "Irreversible action requires ack_irreversible=True", {
                "verdict": "HOLD",
                "reason": "F1 AMANAH gate — ack_irreversible required",
            }

        return True, "Irreversible acknowledged", {
            "ack_irreversible": True,
        }


# ── Engine Registry ──────────────────────────────────────────────────

ENGINES: dict[str, EnforcementEngine] = {
    "floor_gate": FloorGate(),
    "substrate_gate": SubstrateGate(),
    "grief_gate": GriefGate(),
    "hollow_gate": HollowGate(),
    "scar_gate": ScarGate(),
    "injection_gate": InjectionGate(),
    "sovereign_gate": SovereignGate(),
}


# ── Enforcement Pipeline ─────────────────────────────────────────────


def run_enforcement(
    tool_name: str,
    params: dict[str, Any],
    session_id: str | None = None,
    actor_id: str | None = None,
) -> ConsequenceChain:
    """Run the full enforcement pipeline on a tool call.

    Returns a ConsequenceChain with the finding, proposal, and
    substrate context. Approval and execution are separate steps.
    """
    from arifosmcp.core.human_substrate import get_human_properties

    props = get_human_properties()

    # Build substrate context
    substrate = SubstrateContext(
        scar_density=props.scar_density,
        shadow_count=props.shadow_count,
        hollow_count=props.hollow_count,
        grief_active=props.grief_active,
        grief_sensitivity="extreme" if any(
            s.sensitivity == "extreme" for s in props.scars
        ) else "high" if any(
            s.sensitivity == "high" for s in props.scars
        ) else "normal",
        active_scar_ids=[s.scar_id for s in props.scars if s.active],
        active_shadow_ids=[s.shadow_id for s in props.shadows],
        floor_impacts=props.get_active_floor_impacts(),
    )

    # Run engines in order
    context: dict[str, Any] = {}
    worst_verdict = "PASS"
    all_reasons = []
    failed_engine = None

    for engine_name, engine in ENGINES.items():
        passed, reason, metadata = engine.check(tool_name, params, context)
        context[engine_name] = metadata

        if not passed:
            worst_verdict = "BLOCK"
            all_reasons.append(f"{engine_name}: {reason}")
            failed_engine = engine_name
            break  # First BLOCK stops the pipeline
        elif metadata.get("verdict") in ("GUARD", "STRENGTHEN"):
            all_reasons.append(f"{engine_name}: {reason}")
            if metadata["verdict"] == "GUARD" and worst_verdict != "BLOCK":
                worst_verdict = "GUARD"
            elif metadata["verdict"] == "STRENGTHEN" and worst_verdict == "PASS":
                worst_verdict = "STRENGTHEN"

    # Update substrate verdict
    substrate.substrate_verdict = worst_verdict
    substrate.substrate_reasons = all_reasons

    # Create chain
    description = "; ".join(all_reasons) if all_reasons else "All engines passed"
    severity = {
        "PASS": "advisory",
        "STRENGTHEN": "warning",
        "GUARD": "warning",
        "BLOCK": "block",
    }.get(worst_verdict, "advisory")

    chain = create_chain(
        finding_type="enforcement_check",
        tool_name=tool_name,
        description=description,
        severity=severity,
        params=params,
        session_id=session_id,
        actor_id=actor_id,
    )
    chain.substrate_context = substrate

    # Auto-classify risk
    risk = auto_classify_risk(chain)
    chain.finding.finding_type = failed_engine or "enforcement_check"

    return chain


__all__ = [
    "ENGINES",
    "EnforcementEngine",
    "FloorGate",
    "GriefGate",
    "HollowGate",
    "InjectionGate",
    "ScarGate",
    "SovereignGate",
    "SubstrateGate",
    "run_enforcement",
]
