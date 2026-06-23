"""
arifOS Cognitive Gradient — MCP Packaging Law (v2026.06.21)
═══════════════════════════════════════════════════════════════

THE MCP PACKAGING LAW (discovered live, 2026-06-21):
  MCP tools must be packaged by cognitive level, not by function.

This module is the formal enforcement of that law. It defines four
cognitive levels that every canonical tool maps to, and provides
the queryable surface that agents use to climb the gradient.

AGENTS SEE THE GRADIENT. ORGANS STAY HIDDEN.

Level 1 — PERCEPTION      (111) — "Look"
Level 2 — EVIDENCE        (222) — "Look + Prove"
Level 3 — EXPLORATION     (111x)— "Look + Think + Discover"
Level 4 — INTERVENTION    (010) — "Governed Action"

This is the same principle that makes operating systems, neural
architectures, and biological systems scalable — the surface exposes
capability level, not implementation detail.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

# ═══════════════════════════════════════════════════════════════
# COGNITIVE LEVEL DEFINITIONS
# ═══════════════════════════════════════════════════════════════


class CognitiveLevel(IntEnum):
    """Four cognitive levels — the gradient agents climb.

    Levels are numbered 1-4, matching the intuition:
      Level 1 = cheapest, most stateless
      Level 4 = most expensive, most governed

    The integer values are used for ordinal comparison:
      level >= CognitiveLevel.EXPLORATION means "at least L3 capability"
    """

    PERCEPTION = 1  # Look — stateless, cheap, fire-and-forget
    EVIDENCE = 2  # Look + Prove — verified, receipted, cited
    EXPLORATION = 3  # Look + Think + Discover — multi-hop, governed, graph-building
    INTERVENTION = 4  # Governed Action — mutation under seal, lease-gated

    @property
    def label(self) -> str:
        """Human-readable level name."""
        return _LEVEL_LABELS[self]

    @property
    def verbs(self) -> list[str]:
        """The cognitive verbs that define this level."""
        return _LEVEL_VERBS[self]

    @property
    def contract(self) -> str:
        """What agents should expect at this level — the cognitive contract."""
        return _LEVEL_CONTRACTS[self]

    @property
    def governance_mode(self) -> str:
        """How much governance does this level require?"""
        return _LEVEL_GOVERNANCE[self]

    @property
    def cost_profile(self) -> str:
        """Rough cost/compute profile: cheap | moderate | expensive | governed."""
        return _LEVEL_COST[self]


_LEVEL_LABELS: dict[CognitiveLevel, str] = {
    CognitiveLevel.PERCEPTION: "Perception",
    CognitiveLevel.EVIDENCE: "Evidence",
    CognitiveLevel.EXPLORATION: "Exploration",
    CognitiveLevel.INTERVENTION: "Intervention",
}

_LEVEL_VERBS: dict[CognitiveLevel, list[str]] = {
    CognitiveLevel.PERCEPTION: ["look", "search", "observe", "scan", "browse"],
    CognitiveLevel.EVIDENCE: ["verify", "cite", "prove", "fetch", "ground"],
    CognitiveLevel.EXPLORATION: ["discover", "traverse", "map", "explore", "synthesize"],
    CognitiveLevel.INTERVENTION: ["execute", "deploy", "mutate", "write", "seal"],
}

_LEVEL_CONTRACTS: dict[CognitiveLevel, str] = {
    CognitiveLevel.PERCEPTION: (
        "Stateless, cheap, fire-and-forget. Use when you need a quick look. "
        "No verification, no receipts, no governance overhead. "
        "Best for: initial scouting, broad search, quick checks."
    ),
    CognitiveLevel.EVIDENCE: (
        "Verified, receipted, cited. Use when you need proof, not just data. "
        "Every claim carries a source. Every fact is traceable. "
        "Best for: factual grounding, citation-needing claims, decision inputs."
    ),
    CognitiveLevel.EXPLORATION: (
        "Governed, multi-hop, graph-building traversal. Use when single-shot "
        "lookup is insufficient — the goal requires discovery across multiple "
        "steps, domains, or modalities. Every step obeys ART→ACT→STOP. "
        "Best for: research, codebase exploration, cross-domain synthesis."
    ),
    CognitiveLevel.INTERVENTION: (
        "Governed action with constitutional binding. Use ONLY when a SEAL "
        "verdict has been issued by arif_judge. Every mutation "
        "requires a lease. Every irreversible action requires human ack (F13). "
        "Best for: approved deployments, sealed writes, governed mutation."
    ),
}

_LEVEL_GOVERNANCE: dict[CognitiveLevel, str] = {
    CognitiveLevel.PERCEPTION: "vanilla",
    CognitiveLevel.EVIDENCE: "light",
    CognitiveLevel.EXPLORATION: "standard",
    CognitiveLevel.INTERVENTION: "seal",
}

_LEVEL_COST: dict[CognitiveLevel, str] = {
    CognitiveLevel.PERCEPTION: "cheap",
    CognitiveLevel.EVIDENCE: "moderate",
    CognitiveLevel.EXPLORATION: "expensive",
    CognitiveLevel.INTERVENTION: "governed",
}


# ═══════════════════════════════════════════════════════════════
# TOOL → LEVEL MAPPING (the canonical gradient registry)
# ═══════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class GradientEntry:
    """One tool's position on the cognitive gradient."""

    tool_name: str
    level: CognitiveLevel
    stage_code: str  # 000–999 metabolic stage
    cognitive_axis: str  # identity | observe | verify | explore | execute
    expose: bool = True  # False = internal organ, hidden from agents
    description_short: str = ""  # One sentence agents use to decide


# ── Canonical gradient mapping ───────────────────────────────

CANONICAL_GRADIENT: dict[str, GradientEntry] = {
    # LEVEL 1 — PERCEPTION (111)
    "arif_observe": GradientEntry(
        tool_name="arif_observe",
        level=CognitiveLevel.PERCEPTION,
        stage_code="111",
        cognitive_axis="observe",
        expose=True,
        description_short="Look — search the web, scan the repo, check system state. Stateless, cheap, fire-and-forget.",
    ),
    # LEVEL 2 — EVIDENCE (222)
    "arif_fetch": GradientEntry(
        tool_name="arif_fetch",
        level=CognitiveLevel.EVIDENCE,
        stage_code="222",
        cognitive_axis="verify",
        expose=True,
        description_short="Look + Prove — fetch external evidence with citations. Every claim has a source. Verified, receipted.",
    ),
    # LEVEL 3 — EXPLORATION (111x)
    "arif_explore": GradientEntry(
        tool_name="arif_explore",
        level=CognitiveLevel.EXPLORATION,
        stage_code="111x",
        cognitive_axis="explore",
        expose=True,
        description_short=(
            "Look + Think + Discover — governed multi-step exploration. "
            "Traverse, map, synthesize. Six internal modes (Navigator, Prospector, "
            "Driller, Mapper, Surveyor, Eureka) — agents see only the gradient."
        ),
    ),
    "arif_think": GradientEntry(
        tool_name="arif_think",
        level=CognitiveLevel.EXPLORATION,
        stage_code="333",
        cognitive_axis="reason",
        expose=True,
        description_short="Think — multi-step reasoning, planning, reflection. Epistemically honest, confidence-labeled.",
    ),
    # LEVEL 4 — INTERVENTION (010)
    "arif_forge": GradientEntry(
        tool_name="arif_forge",
        level=CognitiveLevel.INTERVENTION,
        stage_code="010",
        cognitive_axis="execute",
        expose=True,
        description_short=(
            "Governed Action — execute approved builds, deployments, system changes. "
            "SEAL verdict REQUIRED. Lease REQUIRED for mutation. F13 human veto FINAL."
        ),
    ),
    # ── GOVERNANCE TOOLS (span levels — classified by primary function) ──
    "arif_init": GradientEntry(
        tool_name="arif_init",
        level=CognitiveLevel.PERCEPTION,
        stage_code="000",
        cognitive_axis="identity",
        expose=True,
        description_short="Bootstrap — start or resume a session. Call FIRST in every conversation. Lightweight identity binding.",
    ),
    "arif_critique": GradientEntry(
        tool_name="arif_critique",
        level=CognitiveLevel.EXPLORATION,
        stage_code="666",
        cognitive_axis="critique",
        expose=True,
        description_short="Ethical critique — assess risks and human impact before acting. Heart before hammer.",
    ),
    "arif_judge": GradientEntry(
        tool_name="arif_judge",
        level=CognitiveLevel.INTERVENTION,
        stage_code="888",
        cognitive_axis="judge",
        expose=True,
        description_short="Constitutional verdict — SEAL, SABAR, HOLD, or VOID. The final word before action.",
    ),
    "arif_seal": GradientEntry(
        tool_name="arif_seal",
        level=CognitiveLevel.INTERVENTION,
        stage_code="999",
        cognitive_axis="seal",
        expose=True,
        description_short="Seal — write to the immutable audit ledger. Irreversible. Terminal stage.",
    ),
    # ── ROUTING / OPERATIONAL (cross-cutting) ──
    "arif_route": GradientEntry(
        tool_name="arif_route",
        level=CognitiveLevel.PERCEPTION,
        stage_code="555",
        cognitive_axis="route",
        expose=True,
        description_short="Route — find the right tool for an intent. Use when unsure which tool to call.",
    ),
    "arif_triage": GradientEntry(
        tool_name="arif_triage",
        level=CognitiveLevel.PERCEPTION,
        stage_code="555",
        cognitive_axis="triage",
        expose=True,
        description_short="Preflight — constitutional preflight check. Returns holds, lanes, and stage status.",
    ),
    "arif_measure": GradientEntry(
        tool_name="arif_measure",
        level=CognitiveLevel.EVIDENCE,
        stage_code="777",
        cognitive_axis="measure",
        expose=True,
        description_short="Measure — system health, vitals, cost, drift. Operational telemetry.",
    ),
    "arif_memory": GradientEntry(
        tool_name="arif_memory",
        level=CognitiveLevel.EVIDENCE,
        stage_code="555m",
        cognitive_axis="memory",
        expose=True,
        description_short="Memory — recall, store, inspect across the 6-layer memory stack.",
    ),
    "arif_gateway_connect": GradientEntry(
        tool_name="arif_gateway_connect",
        level=CognitiveLevel.EXPLORATION,
        stage_code="666g",
        cognitive_axis="gateway",
        expose=True,
        description_short="Gateway — bridge to federation organs (GEOX, WEALTH, WELL, A-FORGE, AAA).",
    ),
    # ── KERNEL / OPERATIONAL (internal sensing + routing) ──
    "arif_kernel_route": GradientEntry(
        tool_name="arif_kernel_route",
        level=CognitiveLevel.PERCEPTION,
        stage_code="555",
        cognitive_axis="route",
        expose=True,
        description_short="Deprecated router — use arif_route instead. Maps intent to correct organ or tool.",
    ),
    "arif_kernel_status": GradientEntry(
        tool_name="arif_kernel_status",
        level=CognitiveLevel.EVIDENCE,
        stage_code="555",
        cognitive_axis="telemetry",
        expose=True,
        description_short="Kernel telemetry — discover tools, query health, predict readiness across federation.",
    ),
    "arif_kernel_attest": GradientEntry(
        tool_name="arif_kernel_attest",
        level=CognitiveLevel.EVIDENCE,
        stage_code="555",
        cognitive_axis="attest",
        expose=True,
        description_short="Organ attestation — verify identity, tool surface, and constitutional binding of federation organs.",
    ),
    "arif_kernel_health": GradientEntry(
        tool_name="arif_kernel_health",
        level=CognitiveLevel.PERCEPTION,
        stage_code="555",
        cognitive_axis="health",
        expose=True,
        description_short="Liveness probe — lightweight kernel reachability check. Zero ceremony.",
    ),
    "arif_bridge_connect": GradientEntry(
        tool_name="arif_bridge_connect",
        level=CognitiveLevel.EXPLORATION,
        stage_code="555",
        cognitive_axis="bridge",
        expose=True,
        description_short="Cross-organ bridge — direct tool call to a named federation organ (geox, wealth, well).",
    ),
    "arif_bridge": GradientEntry(
        tool_name="arif_bridge",
        level=CognitiveLevel.EXPLORATION,
        stage_code="555",
        cognitive_axis="bridge",
        expose=True,
        description_short="[DEPRECATED] Legacy cross-organ bridge. Use arif_bridge_connect instead.",
    ),
    "arif_compose": GradientEntry(
        tool_name="arif_compose",
        level=CognitiveLevel.EVIDENCE,
        stage_code="444r",
        cognitive_axis="reply",
        expose=True,
        description_short="Compose — format the final response with citations, style, and tone. Call LAST after judgment.",
    ),
    "arif_memory_recall": GradientEntry(
        tool_name="arif_memory_recall",
        level=CognitiveLevel.EVIDENCE,
        stage_code="555m",
        cognitive_axis="memory",
        expose=True,
        description_short="[DEPRECATED] Legacy memory recall. Use arif_memory instead for full 6-layer stack access.",
    ),
}


# ═══════════════════════════════════════════════════════════════
# QUERYABLE SURFACE — what agents call to navigate the gradient
# ═══════════════════════════════════════════════════════════════


def resolve_level(tool_name: str) -> CognitiveLevel | None:
    """Return the cognitive level for a given tool, or None if unknown.

    >>> resolve_level("arif_observe")
    <CognitiveLevel.PERCEPTION: 1>
    >>> resolve_level("arif_forge")
    <CognitiveLevel.INTERVENTION: 4>
    """
    entry = CANONICAL_GRADIENT.get(tool_name)
    return entry.level if entry else None


def tools_at_level(level: CognitiveLevel, *, exposed_only: bool = True) -> list[str]:
    """Return all tool names registered at a given cognitive level.

    Args:
        level: The cognitive level to query.
        exposed_only: If True (default), return only tools exposed to agents.
                      If False, include internal organs.

    >>> tools_at_level(CognitiveLevel.PERCEPTION)
    ['arif_observe', 'arif_init', 'arif_route', 'arif_triage']
    """
    result: list[str] = []
    for name, entry in CANONICAL_GRADIENT.items():
        if entry.level == level:
            if exposed_only and not entry.expose:
                continue
            result.append(name)
    return sorted(result)


def gradient_summary(*, exposed_only: bool = True) -> dict[int, dict[str, Any]]:
    """Return the full gradient as a dict, keyed by level number.

    This is the primary queryable surface for agents. They call this
    to discover the cognitive ladder and choose the right tool.

    Returns:
        {
          1: {"label": "Perception", "verbs": [...], "tools": [...], "contract": "..."},
          2: {"label": "Evidence", ...},
          3: {"label": "Exploration", ...},
          4: {"label": "Intervention", ...},
        }
    """
    result: dict[int, dict[str, Any]] = {}
    for level in CognitiveLevel:
        tools = tools_at_level(level, exposed_only=exposed_only)
        result[int(level)] = {
            "label": level.label,
            "verbs": level.verbs,
            "contract": level.contract,
            "governance_mode": level.governance_mode,
            "cost_profile": level.cost_profile,
            "tools": tools,
            "tool_count": len(tools),
        }
    return result


def gradient_ladder() -> list[dict[str, Any]]:
    """Return the gradient as an ordered list — the cognitive ladder.

    This is the format agents use to "climb the gradient" — start at
    Level 1, escalate to Level 2 if verification needed, to Level 3
    if discovery needed, to Level 4 only if action is sealed.

    Returns:
        [
          {"level": 1, "label": "Perception", "verb": "Look", "escalate_when": "..."},
          ...
        ]
    """
    ESCALATION_RULES: dict[CognitiveLevel, str] = {
        CognitiveLevel.PERCEPTION: (
            "Escalate to Level 2 when: you need citations, sources, or verified facts. "
            "Level 1 gives you data. Level 2 gives you proof."
        ),
        CognitiveLevel.EVIDENCE: (
            "Escalate to Level 3 when: single-shot lookup is insufficient. "
            "You need multi-hop traversal, graph-building, or cross-domain synthesis. "
            "Level 2 gives you proof. Level 3 gives you discovery."
        ),
        CognitiveLevel.EXPLORATION: (
            "Escalate to Level 4 ONLY when: arif_judge has issued a SEAL verdict. "
            "Level 3 gives you discovery. Level 4 executes governed action. "
            "NEVER skip straight to Level 4 — the heart critiques before the hammer strikes."
        ),
        CognitiveLevel.INTERVENTION: (
            "Level 4 is terminal — no further escalation. "
            "After execution: arif_measure (verify) → arif_seal (record)."
        ),
    }

    ladder: list[dict[str, Any]] = []
    for level in CognitiveLevel:
        tools = tools_at_level(level, exposed_only=True)
        ladder.append(
            {
                "level": int(level),
                "label": level.label,
                "verbs": level.verbs,
                "primary_verb": level.verbs[0] if level.verbs else "",
                "contract": level.contract,
                "governance_mode": level.governance_mode,
                "cost_profile": level.cost_profile,
                "tools": tools,
                "tool_count": len(tools),
                "escalate_when": ESCALATION_RULES.get(level, ""),
            }
        )
    return ladder


def validate_tool_level(tool_name: str, level: CognitiveLevel) -> bool:
    """Enforce the packaging law: does this tool belong at this level?

    Returns True if the tool is registered at EXACTLY this level.
    Used to prevent organ leakage — a Level 3 tool must not be
    exposed as Level 1 (cheap perception).

    >>> validate_tool_level("arif_explore", CognitiveLevel.EXPLORATION)
    True
    >>> validate_tool_level("arif_explore", CognitiveLevel.PERCEPTION)
    False
    """
    entry = CANONICAL_GRADIENT.get(tool_name)
    if entry is None:
        return False
    return entry.level == level


def packaging_law_check() -> dict[str, Any]:
    """Run the MCP Packaging Law compliance check.

    Returns violations found and a pass/fail verdict. This is the
    enforcement mechanism — tools that violate the packaging law
    (exposed at wrong level, organ leakage, missing gradient entry)
    are flagged.

    Returns:
        {
          "verdict": "PASS" | "FAIL",
          "violations": [...],
          "summary": "...",
        }
    """
    violations: list[dict] = []

    # Check 1: every exposed canonical tool must have a gradient entry
    from arifosmcp.constitutional_map import CANONICAL_TOOLS as CT

    for tool_name, spec in CT.items():
        if not spec.get("expose", True):
            continue  # internal tools are exempt
        if tool_name not in CANONICAL_GRADIENT:
            violations.append(
                {
                    "tool": tool_name,
                    "violation": "MISSING_GRADIENT_ENTRY",
                    "detail": f"Canonical tool '{tool_name}' is exposed but has no gradient entry. "
                    f"Every exposed tool must declare its cognitive level.",
                }
            )

    # Check 2: no tool exposes its internal organs at the wrong level
    for tool_name, entry in CANONICAL_GRADIENT.items():
        if not entry.expose:
            continue

        # Level 4 (Intervention) tools must not be described as cheap/stateless
        if entry.level == CognitiveLevel.INTERVENTION:
            if (
                "cheap" in entry.description_short.lower()
                or "fire-and-forget" in entry.description_short.lower()
            ):
                violations.append(
                    {
                        "tool": tool_name,
                        "violation": "LEVEL_MISREPRESENTATION",
                        "detail": f"Level 4 tool '{tool_name}' described as cheap/fire-and-forget. "
                        f"Intervention tools are governed, not cheap.",
                    }
                )

        # Level 1 (Perception) tools must not claim governance
        if entry.level == CognitiveLevel.PERCEPTION:
            if (
                "governed" in entry.description_short.lower()
                or "seal" in entry.description_short.lower()
            ):
                violations.append(
                    {
                        "tool": tool_name,
                        "violation": "LEVEL_MISREPRESENTATION",
                        "detail": f"Level 1 tool '{tool_name}' claims governance. "
                        f"Perception tools are stateless and cheap.",
                    }
                )

    # Check 3: the gradient must have all four levels populated
    for level in CognitiveLevel:
        exposed = tools_at_level(level, exposed_only=True)
        if not exposed:
            violations.append(
                {
                    "tool": f"LEVEL_{int(level)}",
                    "violation": "EMPTY_LEVEL",
                    "detail": f"Level {int(level)} ({level.label}) has no exposed tools. "
                    f"The cognitive gradient must have all levels populated.",
                }
            )

    verdict = "PASS" if not violations else "FAIL"
    return {
        "verdict": verdict,
        "violations": violations,
        "violation_count": len(violations),
        "summary": (
            f"Packaging Law Check: {verdict}. "
            f"{len(violations)} violation(s) found across {len(CANONICAL_GRADIENT)} gradient entries."
            if violations
            else f"Packaging Law Check: PASS. "
            f"All {len(CANONICAL_GRADIENT)} gradient entries compliant. "
            f"The gradient is clean. Organs stay hidden."
        ),
    }


# ═══════════════════════════════════════════════════════════════
# AGENT-FACING UTILITY — "which tool should I use?"
# ═══════════════════════════════════════════════════════════════


def recommend_level(intent: str) -> CognitiveLevel:
    """Given a natural-language intent, recommend which cognitive level to use.

    This is a lightweight heuristic — for full intent routing, use arif_route.

    >>> recommend_level("search the web for recent AI papers")
    <CognitiveLevel.PERCEPTION: 1>
    >>> recommend_level("verify this claim with external sources")
    <CognitiveLevel.EVIDENCE: 2>
    >>> recommend_level("explore the codebase to understand the auth system")
    <CognitiveLevel.EXPLORATION: 3>
    """
    intent_lower = intent.lower()

    # Level 4 signal words
    l4_signals = [
        "deploy",
        "execute",
        "mutate",
        "write to",
        "production",
        "force push",
        "drop database",
        "delete data",
        "seal",
    ]
    if any(s in intent_lower for s in l4_signals):
        return CognitiveLevel.INTERVENTION

    # Level 3 signal words
    l3_signals = [
        "explore",
        "discover",
        "traverse",
        "map out",
        "understand how",
        "multi-step",
        "research",
        "investigate",
        "codebase",
        "architecture",
        "across",
        "synthesize",
        "compare",
        "analyze",
    ]
    if any(s in intent_lower for s in l3_signals):
        return CognitiveLevel.EXPLORATION

    # Level 2 signal words
    l2_signals = [
        "verify",
        "prove",
        "cite",
        "evidence",
        "fact-check",
        "source",
        "receipt",
        "confirm",
        "validate",
        "ground",
    ]
    if any(s in intent_lower for s in l2_signals):
        return CognitiveLevel.EVIDENCE

    # Default: Level 1 — cheap perception
    return CognitiveLevel.PERCEPTION


# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    "CognitiveLevel",
    "GradientEntry",
    "CANONICAL_GRADIENT",
    "resolve_level",
    "tools_at_level",
    "gradient_summary",
    "gradient_ladder",
    "validate_tool_level",
    "packaging_law_check",
    "recommend_level",
]
