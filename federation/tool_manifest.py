"""
arifOS Federation — Tool Manifest Schema
═══════════════════════════════════════════════════════════════════════════════

Single source of truth for tool registration across all organs.
Replaces ad-hoc SOMATIC_TOOLS, SACRED_SURFACE sets with a unified schema.

W0: Federation invariant — W0 applies to all manifests.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class CognitiveAxis(str, Enum):
    """
    The 11 orthogonal vectors of computation + 2 lifecycle verbs.

    0–10: Primary axes — each answers a distinct cognitive question.
    REPAIR + EXECUTE: Lifecycle verbs — terminal action modes.

    Semantic coordinate for cosine-distance routing:
      axis != organ. A well tool and a geox tool on the same axis
      are closer in intent-space than two well tools on different axes.
    """

    # ── Primary Axes ──────────────────────────────────────────────────────
    IDENTITY = "identity"
    """Who/what is this? (session_init, classify_substrate, system_registry)"""

    OBSERVE = "observe"
    """What is the raw state? (sense_observe, measure_gradient, data_ingest)"""

    TRACE = "trace"
    """How did we get here? (memory_recall, trace_lineage, history_audit)"""

    BOUNDARY = "boundary"
    """What are the limits? (gateway_connect, detect_boundary, map_context)"""

    VERIFY = "verify"
    """Is this true? [F2 TRUTH gate] (evidence_fetch, data_qc)"""

    REASON = "reason"
    """What does this mean? (mind_reason, assess_metabolism, subsurface_candidates)"""

    VITALITY = "vitality"
    """Can we sustain? (ops_measure, compute_metabolic_flux, flow_liquidity)"""

    REFLECT = "reflect"
    """Are we thinking right? (reply_compose, reflect_intelligence, stewardship)"""

    CRITIQUE = "critique"
    """Is this ethical/coherent? (heart_critique, guard_dignity, entropy_risk)"""

    JUDGE = "judge"
    """What's the verdict? (judge_deliberate, validate_vitality, prospect_evaluate)"""

    SEAL = "seal"
    """Lock it in? [W_scar boundary] (vault_seal, anchor_evidence, prospect_judge_seal)"""

    # ── Lifecycle Verbs ───────────────────────────────────────────────────
    REPAIR = "repair"
    """Do we fix? Sub-axis of VITALITY — vitality restoration under stress.
    (check_repair, well_forge_closeout)"""

    EXECUTE = "execute"
    """Do it? Terminal axis — all preceding axes must resolve before EXECUTE.
    (forge_execute, wealth_allocate_optimize)"""


# ── Well-known axis order (for stable serialization) ──────────────────────
AXIS_ORDER: list[CognitiveAxis] = [
    CognitiveAxis.IDENTITY,
    CognitiveAxis.OBSERVE,
    CognitiveAxis.TRACE,
    CognitiveAxis.BOUNDARY,
    CognitiveAxis.VERIFY,
    CognitiveAxis.REASON,
    CognitiveAxis.VITALITY,
    CognitiveAxis.REFLECT,
    CognitiveAxis.CRITIQUE,
    CognitiveAxis.JUDGE,
    CognitiveAxis.SEAL,
    CognitiveAxis.REPAIR,
    CognitiveAxis.EXECUTE,
]


class ToolManifest(BaseModel):
    """
    Unified tool manifest — every MCP tool in the federation.

    Routes by semantic coordinate (cosine-distance on cognitive_axis)
    rather than organ prefix. The orchestration layer resolves intent
    before domain.

    W0: Exposed tools hold a mirror, not a veto.
    W_scar: SEAL-axis tools carry irreversibility risk.
    """

    name: str = Field(
        ...,
        description="Canonical tool name (organ_noun_verb). "
        "Must match the MCP registration name exactly.",
        pattern=r"^(arif_|well_|geox_|wealth_|vault_|mcp_)[a-z0-9_]+$",
    )
    description: str = Field(
        ...,
        description="Functional description. First sentence should "
        "answer the axis question.",
    )
    expose: bool = Field(
        default=False,
        description="Somatic boundary flag. "
        "True: visible on public MCP surface. "
        "False: autonomic — callable internally only.",
    )
    cognitive_axis: CognitiveAxis = Field(
        ...,
        description="The orthogonal routing vector. "
        "Determines intent-space proximity for orchestration routing.",
    )
    organ: str = Field(
        ...,
        description="Canonical organ name: arifos | well | geox | wealth",
        pattern=r"^(arifos|well|geox|wealth)$",
    )

    model_config = {"frozen": True, "use_enum_values": True}


FEDERATION_TOOLS: dict[str, ToolManifest] = {}
"""Global registry: name → ToolManifest. Populated by each organ at init."""


def is_tool_somatic(name: str) -> bool:
    """Check if a tool is visible on the public MCP surface.

    Uses the global FEDERATION_TOOLS registry. Returns False if
    the tool is unregistered (conservative default — fail hidden).
    """
    manifest = FEDERATION_TOOLS.get(name)
    if manifest is None:
        return False
    return manifest.expose


def get_tool_axis(name: str) -> str | None:
    """Return the cognitive axis for a given tool name, or None."""
    manifest = FEDERATION_TOOLS.get(name)
    if manifest is None:
        return None
    val = manifest.cognitive_axis
    if isinstance(val, str):
        return val
    return str(val.value) if hasattr(val, 'value') else str(val)


def tools_by_axis(axis: str) -> list[ToolManifest]:
    """Return all registered tools on a given cognitive axis."""
    return [
        m for m in FEDERATION_TOOLS.values()
        if (m.cognitive_axis.value if hasattr(m.cognitive_axis, 'value') else m.cognitive_axis) == axis
    ]


def tools_by_organ(organ: str) -> list[ToolManifest]:
    """Return all registered tools for a given organ."""
    return [m for m in FEDERATION_TOOLS.values() if m.organ == organ]
