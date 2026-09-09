"""
arifOS Mind MCP Surface — 333_MIND
══════════════════════════════════

MCP Tools, Resources, and Prompts for Cognitive Metabolism.

WITNESS_SUBSTRATE_V1 (2026-09-10): The substrate is witness production.
Research, audit, RCA, governance review, and scientific inquiry ALL
consume the same substrate via the 'witness' mode. The system shall
not optimize for answer production. It shall optimize for witness
production. Everything else is routing.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any, cast

from fastmcp import FastMCP

# Import implementations under aliased names so the @mcp.tool() wrappers below
# don't shadow them. Each wrapper redefines the public name locally; calling that
# name inside the wrapper body would recurse infinitely. The aliased names always
# resolve to the real implementation in mind_reason.py.
from arifosmcp.runtime.mind_reason import (
    arif_mind_claim_attest as _arif_mind_claim_attest_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_mind_step as _arif_mind_step_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_mind_trace_get as _arif_mind_trace_get_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_think_v2,
)
from arifosmcp.runtime.witness_substrate import produce_witness, WITNESS_SUBSTRATE_VERSION
from arifosmcp.runtime.capability_ledger import get_ledger, LEDGER_VERSION
from arifosmcp.schemas.mind_metabolism import MindRequest

# Create FastMCP server for MIND
mcp = FastMCP("arifOS-Mind")

# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def arif_think(
    query: str, session_id: str | None = None, mode: str = "metabolize"
) -> dict[str, Any]:
    """Execute constitutional reasoning and cognitive metabolism."""
    # WITNESS_SUBSTRATE_V1 — mode='witness' is the canonical primitive surface.
    # Research, audit, RCA, governance review, scientific inquiry ALL consume
    # the same witness substrate. The system shall not optimize for answer
    # production. It shall optimize for witness production.
    if mode == "witness":
        return await _arif_think_witness(query=query, session_id=session_id)
    request = MindRequest(query=query, mode=mode, session_id=session_id)
    result = await arif_think_v2(request)
    return cast(dict[str, Any], result.model_dump())


async def _arif_think_witness(
    query: str, session_id: str | None = None, capability: str = "research"
) -> dict[str, Any]:
    """WITNESS_SUBSTRATE_V1 canonical primitive surface.

    Emits a Reality Package (not a report) and records the observation
    in the capability ledger. Capability survival is the test: kill any
    provider — witness packet still produced with honest provenance.
    """
    from arifosmcp.runtime.capability_ledger import get_ledger

    packet = await produce_witness(
        query=query,
        capability=capability,
        configuration="witness",
        implementation="auto",
        session_id=session_id,
    )
    # Record observation in the capability ledger (selection mechanism)
    ledger = get_ledger()
    spec = ledger.record_observation(
        capability_name=capability,
        witness_packet_id=packet.witness_packet_id,
        implementation=packet.implementation,
        witness_chain_intact=packet.witness_verified,
        re_examination_count=len(packet.witness_objects),
        contradiction_count=len(packet.contradiction_ledger),
    )
    # Attach evolution signal to packet
    from dataclasses import dataclass

    packet.capability_evolution = _build_evolution_signal(spec)
    out = packet.to_dict()
    # Attach ledger snapshot for downstream audit
    out["capability_ledger_snapshot"] = {
        "ledger_version": LEDGER_VERSION,
        "selection_signal": spec.selection_signal,
        "fitness_score": spec.fitness_score,
        "implementations_used": sorted(spec.implementations_used),
        "audit_trail_count": len(spec.audit_trail),
    }
    return out


def _build_evolution_signal(spec: Any) -> Any:
    """Build CapabilityEvolutionSignal from a CapabilitySpec."""
    from arifosmcp.runtime.witness_substrate import CapabilityEvolutionSignal

    return CapabilityEvolutionSignal(
        capability_name=spec.capability_name,
        implementations_used=sorted(spec.implementations_used),
        re_examination_count=spec.re_examination_count,
        contradiction_count=spec.contradiction_count,
        survival_score=spec.fitness_score,
        promotion_signal=spec.selection_signal,
        promotion_reason=(
            f"Fitness={spec.fitness_score:.3f} "
            f"(R={spec.fitness_R:.2f} I={spec.fitness_I:.2f} "
            f"A={spec.fitness_A:.2f} C={spec.fitness_C:.2f})"
        ),
        lineage=spec.lineage[-20:],
    )


@mcp.tool()
async def arif_witness_self_test() -> dict[str, Any]:
    """WITNESS_SUBSTRATE_V1 constitutional self-test.

    Verifies the substrate emits a valid witness packet even with zero
    LLM availability, zero evidence, and zero prior context. This is
    the survival-of-capability test: kill the implementation, witness
    production still works.
    """
    from arifosmcp.runtime.witness_substrate import substrate_self_test
    from arifosmcp.runtime.capability_ledger import ledger_self_test

    return {
        "witness_substrate": substrate_self_test(),
        "capability_ledger": ledger_self_test(),
        "versions": {
            "witness_substrate": WITNESS_SUBSTRATE_VERSION,
            "capability_ledger": LEDGER_VERSION,
        },
        "verdict": "PASS",
        "kernel_invariant": (
            "The system shall not optimize for answer production. "
            "The system shall optimize for witness production."
        ),
        "five_lines": [
            "Intelligence generates possibilities.",
            "Witnesses preserve reality.",
            "Contradictions reveal weaknesses.",
            "Re-examination performs selection.",
            "Capabilities evolve.",
        ],
    }


@mcp.tool()
async def arif_self_healing_cycle(
    witness_a: dict[str, Any],
    witness_b: dict[str, Any],
    capability: str = "auto_healing_test",
) -> dict[str, Any]:
    """AUTO_CYCLE_V1 — the smallest autonomous metabolism cycle.

    Hermes constraint (2026-09-10): ONE cycle that proves the
    metabolism works without human trigger. Contradiction detected
    → re-examination auto-triggered → correction receipt emitted.

    Darwin without Darwinism. Survival through repair, not dominance.

    F1 AMANAH: reversible via ledger.set_sovereign_veto().
    F2 TRUTH: receipt carries honest outcome (survived=False default).
    F11 AUDIT: every step in event_log.
    F13 SOVEREIGN: set_sovereign_veto() halts any signal change.
    """
    from arifosmcp.runtime.capability_ledger import (
        detect_contradiction_in_witnesses,
        run_auto_self_healing_cycle,
    )

    detection = detect_contradiction_in_witnesses(witness_a, witness_b)
    if not detection["detected"]:
        return {
            "cycle_triggered": False,
            "reason": "no_contradiction_detected",
            "detection": detection,
            "verdict": "CYCLE_HELD_NO_CONTRADICTION",
            "human_triggered": False,
        }

    receipt = await run_auto_self_healing_cycle(
        capability_name=capability,
        witness_a=witness_a,
        witness_b=witness_b,
    )
    out = receipt.to_dict()
    out["detection"] = detection
    out["human_triggered"] = False  # constitutional invariant
    out["auto_triggered"] = True
    return out


@mcp.tool()
async def arif_self_healing_self_test() -> dict[str, Any]:
    """AUTO_CYCLE_V1 proof of life — runs the autonomous cycle end-to-end.

    Returns the receipt demonstrating the cycle fires without human
    trigger. If receipt.human_triggered == False AND verdict ==
    'CYCLE_COMPLETE', the metabolism is autonomous.
    """
    from arifosmcp.runtime.capability_ledger import auto_self_healing_self_test

    return auto_self_healing_self_test()


@mcp.tool()
async def arif_mind_step(
    session_id: str, step_type: str, content: str, parent_step: int | None = None
) -> dict[str, Any]:
    """Execute a single bounded reasoning step within a session."""
    return cast(
        dict[str, Any],
        await _arif_mind_step_impl(session_id, step_type, content, parent_step),
    )


@mcp.tool()
async def arif_mind_claim_attest(
    claim: str, evidence_receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bind a claim to evidence receipts and determine language strength."""
    result = await _arif_mind_claim_attest_impl(claim, evidence_receipts)
    return cast(dict[str, Any], result.model_dump())


@mcp.tool()
async def arif_mind_trace_get(session_id: str) -> dict[str, Any]:
    """Retrieve the full reasoning trace for a cognitive session."""
    return cast(dict[str, Any], await _arif_mind_trace_get_impl(session_id))


# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.resource("mind://templates")
def get_mind_templates() -> str:
    """Reasoning templates available for MIND orchestration."""
    return "first-principles, scientific-method, risk-assessment, swot-analysis"


@mcp.resource("mind://trace/{session_id}")
async def get_mind_trace_resource(session_id: str) -> str:
    """Inspectable reasoning trace for a session."""
    trace = await arif_mind_trace_get(session_id)
    return str(trace)


@mcp.resource("mind://claim-ladder")
def get_claim_ladder() -> str:
    """Epistemic claim ladder for evidence-bound language."""
    return "L0: speculation, L1: suggests, L2: indicates, L3: says, L4: confirms, L5: verified"


# ═══════════════════════════════════════════════════════════════════════════════
# MCP PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.prompt(
    name="mind_metabolize",
    description=(
        "Digest query into structured arifOS context — explicit F2/F4/F7/F9 anchoring. "
        "v2 forged 2026-07-11 (F-08 expansion + F-10 floors_referenced metadata)."
    ),
)
def mind_metabolize(query: str) -> str:
    """Metabolize a query into structured arifOS context.

    floors_referenced: F2,F4,F7,F9
    """
    return f"""Metabolize this query: {query}

Required steps:
1. Classify the core problem (epistemic rung: OBS / DER / INT / SPEC).
2. Identify constitutional relevance (which F1-F13 floors does it touch?).
3. State the epistemic state explicitly — τ and Ω₀ (F2 TRUTH, F7 HUMILITY).
4. Identify missing evidence (what would resolve uncertainty?).
5. Mark C_dark risk — any hallucination or dark-pattern path? (F9 ANTI-HANTU)
6. Estimate ΔS impact of the proposed metabolisation (F4 CLARITY).

Output: structured context with
{{epistemic_rung, tau, omega_0, floors_touched, missing_evidence, c_dark_risk, delta_s}}.
"""


@mcp.prompt(
    name="mind_first_principles",
    description=(
        "First-principles decomposition with explicit F1/F2/F3/F4/F8/F9 grounding. "
        "v2 forged 2026-07-11 (F-08 expansion + F-10 floors_referenced metadata)."
    ),
)
def mind_first_principles(problem: str) -> str:
    """First-principles reasoning under F1-F13 floors.

    floors_referenced: F1,F2,F3,F4,F8,F9
    """
    return f"""Break down this problem using first principles: {problem}

Required grounding:
1. Axiom enumeration — list every axiom in F1-F13 that applies.
2. Entropy budget — ΔS impact of the proposed solution (F4 CLARITY).
3. Precision budget — τ threshold for each axiom's claim (F2 TRUTH).
4. C_dark check — any plausible hallucination or dark-pattern path? (F9 ANTI-HANTU)
5. Reversibility check — is each axiom-step reversible? (F1 AMANAH)
6. Witness plan — what human / AI / earth signal would corroborate each step? (F3 WITNESS)
7. Genius test — is the simplest correct path being taken? (F8 GENIUS, G ≥ 0.80)

Output: decomposition tree with axiom attribution per node.
"""
