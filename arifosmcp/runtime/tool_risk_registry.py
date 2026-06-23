"""
Tool Risk Registry — E7 Bridge: MCP Tools → Autonomy Contract Table
═══════════════════════════════════════════════════════════════════════

Maps every canonical arifOS MCP tool (and key mode variants) to E7's
autonomy contract parameters. Without this registry, E7 cannot
consistently classify actions — every tool call defaults to the same
generic parameters.

This is the missing bridge between:
  - E7 principal_paradox.py (16-row contract table)
  - arifosmcp/tool_registry.json (13 canonical tools)
  - Actual MCP tool calls arriving at the governance pipeline

ARCHITECTURE:
  Base mapping per tool → per-mode overrides → E7 parameters
  (risk_tier, blast_radius, reversibility, action_class, autonomy_floor)

USAGE:
  from arifosmcp.runtime.tool_risk_registry import classify_tool
  params = classify_tool("arif_forge", {"mode": "engineer"})
  # → {risk_tier: "HIGH", blast_radius: "PUBLIC", ...}

F1 AMANAH: Registry is policy, not code. Updating it is reversible.
F2 TRUTH: Every entry has a rationale — why this tool maps to this risk.
F11 AUDIT: Registry changes must be sealed to VAULT999.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ═══════════════════════════════════════════════════════════════
# E7 Risk Parameters (output of classification)
# ═══════════════════════════════════════════════════════════════


@dataclass
class ToolRiskProfile:
    """E7 risk classification for a tool (+ optional mode)."""

    tool_name: str
    mode: str | None  # None = base profile, str = mode-specific override
    action_class: str  # OBSERVE | ANALYZE | DRAFT | MUTATE | IRREVERSIBLE
    risk_tier: str  # LOW | MEDIUM | HIGH | ATOMIC
    blast_radius: str  # LOCAL | ACCOUNT | ORG | PUBLIC | MARKET | INFRASTRUCTURE | CIVILIZATIONAL
    reversibility: float  # 1.0 → 0.0
    autonomy_floor: str  # minimum autonomy tier allowed
    rationale: str  # WHY this classification
    requires_lease: bool = False
    can_escalate_to: str = ""  # next higher autonomy tier if conditions met

    def to_e7_params(self) -> dict[str, Any]:
        """Convert to parameters expected by evaluate_autonomy_ceiling()."""
        return {
            "action_class": self.action_class,
            "risk_tier": self.risk_tier,
            "blast_radius": self.blast_radius,
            "reversibility": self.reversibility,
            "autonomy_floor": self.autonomy_floor,
        }


# ═══════════════════════════════════════════════════════════════
# CANONICAL TOOL RISK REGISTRY
# ═══════════════════════════════════════════════════════════════

# Format: tool_name → list[ToolRiskProfile]  (first entry = base/default)
TOOL_RISK_REGISTRY: dict[str, list[ToolRiskProfile]] = {
    # ── 000: Session Init ──────────────────────────────────────────
    "arif_init": [
        ToolRiskProfile(
            tool_name="arif_init",
            mode=None,  # base
            action_class="DRAFT",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=0.95,
            autonomy_floor="FULL_AUTO",
            rationale="Session init is low-risk preparation. Only side effect is creating a session record.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_init",
            mode="init",
            action_class="DRAFT",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="init mode is fully reversible — just bootstraps a new session identity.",
            requires_lease=False,
        ),
    ],
    # ── SENSE: Search/Observe ─────────────────────────────────────
    "arif_observe": [
        ToolRiskProfile(
            tool_name="arif_observe",
            mode=None,
            action_class="OBSERVE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Observation is always read-only. No mutation. E7 explicitly exempts OBSERVE class.",
            requires_lease=False,
        ),
    ],
    # ── EVIDENCE: Fetch + Cite ────────────────────────────────────
    "arif_fetch": [
        ToolRiskProfile(
            tool_name="arif_fetch",
            mode=None,
            action_class="OBSERVE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Evidence fetch is read-only retrieval. No mutation path.",
            requires_lease=False,
        ),
    ],
    # ── MIND: Multi-Step Reasoning ────────────────────────────────
    "arif_think": [
        ToolRiskProfile(
            tool_name="arif_think",
            mode=None,
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="ORG",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Reasoning within arifOS boundary, fully reversible. Plan output is proposal only.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_think",
            mode="plan_approve",
            action_class="DRAFT",
            risk_tier="MEDIUM",
            blast_radius="PUBLIC",
            reversibility=0.7,
            autonomy_floor="PROPOSE_ONLY",
            rationale="Plan approval gates execution. The plan itself is reversible but commits intent.",
            requires_lease=True,
        ),
    ],
    # ── HEART: Ethical Critique ───────────────────────────────────
    "arif_critique": [
        ToolRiskProfile(
            tool_name="arif_critique",
            mode=None,
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="ORG",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Heart critique is advisory only — computes risk, does not block. F1 reversible.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_critique",
            mode="redteam",
            action_class="ANALYZE",
            risk_tier="MEDIUM",
            blast_radius="ORG",
            reversibility=0.9,
            autonomy_floor="FULL_AUTO",
            rationale="Red-team mode simulates attacks. Higher blast radius conceptually but advisory.",
            requires_lease=False,
        ),
    ],
    # ── KERNEL: Route Intent ─────────────────────────────────────
    "arif_kernel_route": [
        ToolRiskProfile(
            tool_name="arif_kernel_route",
            mode=None,
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="ORG",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Routing is computational dispatch. No mutation. Purely organizational.",
            requires_lease=False,
        ),
    ],
    # ── REPLY: Compose Response ───────────────────────────────────
    "arif_compose": [
        ToolRiskProfile(
            tool_name="arif_compose",
            mode=None,
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Reply composition formats output. Read-only. No side effects beyond display.",
            requires_lease=False,
        ),
    ],
    # ── MEMORY: Recall/Store ──────────────────────────────────────
    "arif_memory_recall": [
        ToolRiskProfile(
            tool_name="arif_memory_recall",
            mode=None,
            action_class="OBSERVE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Memory recall is read-only search. recall mode never mutates.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_memory_recall",
            mode="store",
            action_class="MUTATE",
            risk_tier="MEDIUM",
            blast_radius="ORG",
            reversibility=0.8,
            autonomy_floor="PROPOSE_ONLY",
            rationale="Memory store writes to memory. Reversible but changes agent knowledge graph.",
            requires_lease=True,
        ),
    ],
    # ── BRIDGE: Direct Organ Call (RULE 14) ─────────────────────
    "arif_bridge_connect": [
        ToolRiskProfile(
            tool_name="arif_bridge_connect",
            mode=None,
            action_class="ANALYZE",
            risk_tier="MEDIUM",
            blast_radius="PUBLIC",
            reversibility=0.9,
            autonomy_floor="FULL_AUTO",
            rationale="Bridge connect is cross-organ routing. No local mutation — delegates to target organ. F1 AMANAH: reversible at arifOS level (target organ action may not be). Canonical name follows arif_<noun>_<verb> convention (forged 2026-06-21).",
            requires_lease=False,
        ),
    ],
    # ── GATEWAY: Federation Bridge ────────────────────────────────
    "arif_gateway_connect": [
        ToolRiskProfile(
            tool_name="arif_gateway_connect",
            mode=None,
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="ORG",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Gateway routing is computational. No mutation. Bridges to other organs.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_gateway_connect",
            mode="route",
            action_class="ANALYZE",
            risk_tier="MEDIUM",
            blast_radius="PUBLIC",
            reversibility=0.9,
            autonomy_floor="FULL_AUTO",
            rationale="Cross-organ routing carries federation risk. Still computational only.",
            requires_lease=False,
        ),
    ],
    # ── JUDGE: Constitutional Verdict ─────────────────────────────
    "arif_judge": [
        ToolRiskProfile(
            tool_name="arif_judge",
            mode=None,
            action_class="DRAFT",
            risk_tier="MEDIUM",
            blast_radius="ORG",
            reversibility=0.8,
            autonomy_floor="PROPOSE_ONLY",
            rationale="Judgment proposes constitutional verdicts. Advisory to principal, not self-executing.",
            requires_lease=True,
        ),
        ToolRiskProfile(
            tool_name="arif_judge",
            mode="judge",
            action_class="DRAFT",
            risk_tier="HIGH",
            blast_radius="PUBLIC",
            reversibility=0.5,
            autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
            rationale="Binding judgment crosses into principal territory. F13 sovereignty gate.",
            requires_lease=True,
        ),
    ],
    # ── VAULT: Immutable Seal ─────────────────────────────────────
    "arif_seal": [
        ToolRiskProfile(
            tool_name="arif_seal",
            mode=None,
            action_class="IRREVERSIBLE",
            risk_tier="ATOMIC",
            blast_radius="PUBLIC",
            reversibility=0.0,
            autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
            rationale="VAULT999 seal is IRREVERSIBLE by design. SEAL writes permanently to append-only ledger. E7 hard floor: reversibility 0.0 < 0.3 → HOLD unless principal.",
            requires_lease=True,
        ),
    ],
    # ── FORGE: Execute Builds/Deploys ─────────────────────────────
    "arif_forge": [
        ToolRiskProfile(
            tool_name="arif_forge",
            mode=None,  # base default — safest, used when mode unknown
            action_class="MUTATE",
            risk_tier="HIGH",
            blast_radius="PUBLIC",
            reversibility=0.5,
            autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
            rationale="Forge default is HIGH risk: code mutation with federation blast. Conservative default.",
            requires_lease=True,
        ),
        ToolRiskProfile(
            tool_name="arif_forge",
            mode="query",
            action_class="OBSERVE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Query mode is read-only system introspection. No mutation.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_forge",
            mode="dry_run",
            action_class="ANALYZE",
            risk_tier="LOW",
            blast_radius="ORG",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Dry run simulates without mutation. F1 AMANAH: fully reversible.",
            requires_lease=False,
        ),
        ToolRiskProfile(
            tool_name="arif_forge",
            mode="engineer",
            action_class="MUTATE",
            risk_tier="HIGH",
            blast_radius="PUBLIC",
            reversibility=0.4,
            autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
            rationale="Engineer mode WRITES CODE to disk. Federation blast: affects all organs. Requires principal for irreversible deploys.",
            requires_lease=True,
        ),
        ToolRiskProfile(
            tool_name="arif_forge",
            mode="commit",
            action_class="MUTATE",
            risk_tier="HIGH",
            blast_radius="PUBLIC",
            reversibility=0.3,
            autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
            rationale="Commit writes to git history. Reversibility 0.3 — borderline hard floor. Principal approval required.",
            requires_lease=True,
        ),
        ToolRiskProfile(
            tool_name="arif_forge",
            mode="deploy",
            action_class="IRREVERSIBLE",
            risk_tier="ATOMIC",
            blast_radius="CIVILIZATIONAL",
            reversibility=0.1,
            autonomy_floor="HOLD",
            rationale="DEPLOY IS ATOMIC: pushes to production, affects external systems, near-irreversible. E7 HOLD — principal must directly execute.",
            requires_lease=True,
        ),
    ],
    # ── OPS: Health + Vitals ──────────────────────────────────────
    "arif_measure": [
        ToolRiskProfile(
            tool_name="arif_measure",
            mode=None,
            action_class="OBSERVE",
            risk_tier="LOW",
            blast_radius="LOCAL",
            reversibility=1.0,
            autonomy_floor="FULL_AUTO",
            rationale="Operations measurement is read-only health check. No mutation path.",
            requires_lease=False,
        ),
    ],
}

# ═══════════════════════════════════════════════════════════════
# DANGEROUS MODE ALIASES — conservative overrides
# ═══════════════════════════════════════════════════════════════

DANGEROUS_MODE_ALIASES: dict[str, str] = {
    # Maps dangerous/ambiguous mode names to their canonical mode
    # Any mode NOT in the registry for a tool defaults to the tool's base profile
    "write": "engineer",
    "generate": "engineer",
    "build": "engineer",
    "mutate": "engineer",
    "execute": "deploy",
    "apply": "deploy",
    "push": "deploy",
}


# ═══════════════════════════════════════════════════════════════
# CLASSIFICATION FUNCTION
# ═══════════════════════════════════════════════════════════════


def classify_tool(
    tool_name: str,
    params: dict[str, Any] | None = None,
) -> ToolRiskProfile:
    """
    Classify a tool call into its E7 risk profile.

    Resolution order:
      1. Tool + exact mode match
      2. Tool base profile (mode=None)
      3. Universal safe default (OBSERVE/LOW/LOCAL/1.0)

    Args:
        tool_name: Canonical tool name (e.g. "arif_forge")
        params: Tool parameters dict (used to extract "mode")

    Returns:
        ToolRiskProfile with full E7 classification
    """
    params = params or {}

    # Extract mode from params — check common mode field names
    mode = params.get("mode") or params.get("action") or params.get("type")
    if mode:
        # Check for dangerous aliases
        mode = DANGEROUS_MODE_ALIASES.get(mode, mode)

    # Look up tool in registry
    profiles = TOOL_RISK_REGISTRY.get(tool_name)

    if profiles:
        # Try mode-specific match first
        if mode:
            for profile in profiles:
                if profile.mode == mode:
                    return profile

        # Fall back to base profile (mode=None)
        for profile in profiles:
            if profile.mode is None:
                return profile

    # ── Universal safe default for unknown tools ──
    # F1 AMANAH: unknown tools default to most conservative classification
    return ToolRiskProfile(
        tool_name=tool_name,
        mode=mode,
        action_class="OBSERVE",
        risk_tier="HIGH",  # Conservative: unknown tools are high risk
        blast_radius="ORG",
        reversibility=0.5,
        autonomy_floor="PRINCIPAL_APPROVAL_REQUIRED",
        rationale=f"Unknown tool '{tool_name}' — conservative default. "
        f"Add to TOOL_RISK_REGISTRY to refine.",
        requires_lease=False,
    )


def classify_tool_call(ctx: Any) -> ToolRiskProfile:
    """
    Classify a ToolCallContext into its E7 risk profile.

    Convenience wrapper for governance pipeline integration.
    Extracts tool_name and params from the context object.

    Args:
        ctx: ToolCallContext or similar object with tool_name and params

    Returns:
        ToolRiskProfile
    """
    tool_name = getattr(ctx, "tool_name", "unknown")
    params = getattr(ctx, "params", {}) or {}
    return classify_tool(tool_name, params)


def get_all_registered_tools() -> list[str]:
    """Return all tool names in the risk registry."""
    return sorted(TOOL_RISK_REGISTRY.keys())


def get_tool_modes(tool_name: str) -> list[str]:
    """Return all registered modes for a tool."""
    profiles = TOOL_RISK_REGISTRY.get(tool_name, [])
    return [p.mode for p in profiles if p.mode is not None]


def validate_registry() -> dict[str, Any]:
    """
    Validate the risk registry for completeness and consistency.

    Returns:
        Dict with coverage stats and any warnings.
    """
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
    except ImportError:
        # Fallback: derive from tool_registry.json
        import json
        import os

        _reg_path = os.path.join(os.path.dirname(__file__), "..", "tool_registry.json")
        with open(_reg_path) as f:
            _reg = json.load(f)
        CANONICAL_TOOLS = _reg.get("tools", {})

    canonical = set(CANONICAL_TOOLS.keys())
    registered = set(TOOL_RISK_REGISTRY.keys())
    missing = canonical - registered
    extra = registered - canonical

    return {
        "verdict": "PASS" if not missing else "WARN",
        "canonical_count": len(canonical),
        "registered_count": len(registered),
        "missing_tools": sorted(missing),
        "extra_registrations": sorted(extra),
        "total_profiles": sum(len(p) for p in TOOL_RISK_REGISTRY.values()),
        "tools_with_mode_overrides": sum(
            1 for p in TOOL_RISK_REGISTRY.values() if any(q.mode is not None for q in p)
        ),
    }


__all__ = [
    "ToolRiskProfile",
    "TOOL_RISK_REGISTRY",
    "DANGEROUS_MODE_ALIASES",
    "classify_tool",
    "classify_tool_call",
    "get_all_registered_tools",
    "get_tool_modes",
    "validate_registry",
]
