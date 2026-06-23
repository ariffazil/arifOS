"""
MCP Tool Annotations — Computed, Not Declared
═══════════════════════════════════════════════════════════════════════════════

The MCP 2025-03-26 spec defines four standard tool annotations:
  - readOnlyHint
  - destructiveHint
  - idempotentHint
  - openWorldHint

The spec is explicit: these annotations are UNTRUSTED unless they come from a
trusted server. A malicious server can mark a destructive tool with
`readOnlyHint: true` to bypass client-side confirmation.

The arifOS move: DERIVE the annotations from the deterministic enums in
FederationEnvelope v2.0. By computing them from action_class, reversibility,
and external_effect, we close the spec loophole by construction.

DITEMPA BUKAN DIBERI — The substrate is forged, not given.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arifosmcp.schemas.federation_envelope import (
        ActionClass,
        ExternalEffect,
        ReversibilityLevel,
    )


def compute_mcp_annotations(
    action_class: "ActionClass",
    reversibility: "ReversibilityLevel" = None,
    external_effect: "ExternalEffect" = None,
) -> dict[str, bool]:
    """
    Compute MCP tool annotations from deterministic governance enums.

    This function is the SINGLE SOURCE OF TRUTH for tool annotations.
    It MUST be used:
      1. At @mcp.tool registration time (passed as annotations=...)
      2. In every tool response envelope (returned as mcp_annotations=...)
      3. In the public surface manifest (declared as mcp_annotations=...)

    Args:
        action_class: The ActionClass enum (OBSERVE, MUTATE, IRREVERSIBLE, ...)
        reversibility: The ReversibilityLevel enum (HIGH, MEDIUM, LOW, IRREVERSIBLE)
        external_effect: The ExternalEffect enum (NONE, PRIVATE, PUBLIC, ...)

    Returns:
        A dict with the four MCP standard annotations:
          - readOnlyHint
          - destructiveHint
          - idempotentHint
          - openWorldHint

    Reference:
      MCP spec 2025-03-26 — Tool Annotations:
      https://modelcontextprotocol.io/specification/2025-03-26/server/tools#annotations

    arifOS Doctrine (GENESIS/030 §7):
      Annotations are COMPUTED FROM action_class. Never hand-set.
      A hand-set annotation is an attack vector. The substrate enforces the law.
    """
    # Lazy import to avoid circular dependency at module load
    from arifosmcp.schemas.federation_envelope import (
        ActionClass,
        ExternalEffect,
        ReversibilityLevel,
    )

    # ── readOnlyHint ─────────────────────────────────────────────────────
    # Per spec: "If true, the tool does not modify its environment."
    # arifOS rule: action_class == OBSERVE means no environment modification.
    read_only = action_class == ActionClass.OBSERVE

    # ── destructiveHint ─────────────────────────────────────────────────
    # Per spec: "If true, the tool may perform destructive updates to its
    # environment. Only meaningful when readOnlyHint == false."
    # arifOS rule: MUTATE or IRREVERSIBLE action with low/IRREVERSIBLE reversibility.
    if reversibility is None:
        reversibility = ReversibilityLevel.HIGH
    destructive = action_class in (
        ActionClass.MUTATE,
        ActionClass.IRREVERSIBLE,
    ) and reversibility in (ReversibilityLevel.LOW, ReversibilityLevel.IRREVERSIBLE)

    # ── idempotentHint ──────────────────────────────────────────────────
    # Per spec: "If true, calling the tool repeatedly with the same arguments
    # will have no additional effect."
    # arifOS rule: HIGH reversibility means re-running produces same end state.
    idempotent = reversibility == ReversibilityLevel.HIGH and action_class in (
        ActionClass.OBSERVE,
        ActionClass.MUTATE,
    )

    # ── openWorldHint ───────────────────────────────────────────────────
    # Per spec: "If true, this tool may interact with an 'open world' of
    # external entities (e.g., the internet). If false, the tool is
    # confined to a closed universe."
    # arifOS rule: external_effect in {PUBLIC, LEGAL, FINANCIAL} = open world.
    if external_effect is None:
        external_effect = ExternalEffect.NONE
    open_world = external_effect in (
        ExternalEffect.PUBLIC,
        ExternalEffect.LEGAL,
        ExternalEffect.FINANCIAL,
    )

    return {
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }


def annotations_from_risk_passport(risk: "RiskPassport") -> dict[str, bool]:
    """
    Convenience wrapper — compute annotations from a RiskPassport.

    Usage in tool response envelope:
        from arifosmcp.runtime.annotations import annotations_from_risk_passport
        response["mcp_annotations"] = annotations_from_risk_passport(envelope.risk)
    """
    return compute_mcp_annotations(
        action_class=risk.action_class,
        reversibility=risk.reversibility,
        external_effect=risk.external_effect,
    )
