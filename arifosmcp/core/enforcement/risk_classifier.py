"""
Risk Classifier — Unified Risk Classification Engine
═══════════════════════════════════════════════════════════════════════════════

Takes the five competing risk taxonomies and maps them to a single canonical
RiskPassport. Every tool call in the federation is classified through here.

Canonical ladder:
  T0  Harmless observation
  T1  Account-scoped observation
  T2  Org-scoped preparation
  T3  Org-scoped mutation
  T4  Public-scoped mutation
  T5  Infrastructure-scoped atomic action

DITEMPA BUKAN DIBERI — No tool bypasses classification.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    BlastRadius,
    ExternalEffect,
    ReversibilityLevel,
    RiskPassport,
    RiskTier,
    SecretTouch,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY MAPPINGS (source taxonomy → canonical)
# ═══════════════════════════════════════════════════════════════════════════════

_LEGACY_READONLY_MAP = {
    "READONLY": (RiskTier.T0, ActionClass.OBSERVE),
    "C0": (RiskTier.T0, ActionClass.OBSERVE),
    "C1": (RiskTier.T1, ActionClass.OBSERVE),
    "C2": (RiskTier.T2, ActionClass.PREPARE),
    "low": (RiskTier.T1, ActionClass.OBSERVE),
    "medium": (RiskTier.T2, ActionClass.PREPARE),
    "high": (RiskTier.T4, ActionClass.MUTATE),
    "T0": (RiskTier.T0, ActionClass.OBSERVE),
    "T1": (RiskTier.T1, ActionClass.OBSERVE),
    "T2": (RiskTier.T2, ActionClass.PREPARE),
    "T3": (RiskTier.T3, ActionClass.MUTATE),
    "T4": (RiskTier.T4, ActionClass.MUTATE),
}

_LEGACY_ACTION_CLASS_MAP = {
    "READONLY": ActionClass.OBSERVE,
    "C0": ActionClass.OBSERVE,
    "C1": ActionClass.OBSERVE,
    "C2": ActionClass.PREPARE,
    "observe": ActionClass.OBSERVE,
    "prepare": ActionClass.PREPARE,
    "mutate": ActionClass.MUTATE,
    "atomic": ActionClass.ATOMIC,
    "write": ActionClass.MUTATE,
    "delete": ActionClass.MUTATE,
    "deploy": ActionClass.ATOMIC,
    "restart": ActionClass.MUTATE,
}

_LEGACY_BLAST_MAP = {
    "local": BlastRadius.LOCAL,
    "account": BlastRadius.ACCOUNT,
    "org": BlastRadius.ORG,
    "public": BlastRadius.PUBLIC,
    "financial": BlastRadius.FINANCIAL,
    "infra": BlastRadius.INFRA,
    "none": BlastRadius.LOCAL,
    "host": BlastRadius.INFRA,
    "user": BlastRadius.ACCOUNT,
}

_LEGACY_REVERSIBILITY_MAP = {
    "high": ReversibilityLevel.HIGH,
    "medium": ReversibilityLevel.MEDIUM,
    "low": ReversibilityLevel.LOW,
    "irreversible": ReversibilityLevel.IRREVERSIBLE,
    "yes": ReversibilityLevel.HIGH,
    "no": ReversibilityLevel.IRREVERSIBLE,
    "partial": ReversibilityLevel.MEDIUM,
}

_LEGACY_SECRET_MAP = {
    "none": SecretTouch.NONE,
    "possible": SecretTouch.POSSIBLE,
    "definite": SecretTouch.DEFINITE,
    True: SecretTouch.DEFINITE,
    False: SecretTouch.NONE,
    "yes": SecretTouch.DEFINITE,
    "no": SecretTouch.NONE,
}

_LEGACY_EXTERNAL_MAP = {
    "none": ExternalEffect.NONE,
    "private": ExternalEffect.PRIVATE,
    "public": ExternalEffect.PUBLIC,
    "legal": ExternalEffect.LEGAL,
    "financial": ExternalEffect.FINANCIAL,
    True: ExternalEffect.PUBLIC,
    False: ExternalEffect.NONE,
}


def _map_legacy(raw: str | None, mapping: dict[Any, Any], default: Any) -> Any:
    """Map a legacy value to canonical, returning default on unknown."""
    if raw is None:
        return default
    if raw in mapping:
        return mapping[raw]
    # Try case-insensitive
    raw_lower = raw.lower() if isinstance(raw, str) else raw
    if raw_lower in mapping:
        return mapping[raw_lower]
    logger.warning(f"Unknown legacy risk value '{raw}', using default {default}")
    return default


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


def classify_from_legacy(
    taxonomy: str | None = None,
    level: str | None = None,
    action_class: str | None = None,
    blast_radius: str | None = None,
    reversibility: str | None = None,
    secret_touch: str | None = None,
    external_effect: str | None = None,
    risk_ceiling: str | None = None,
) -> RiskPassport:
    """
    Convert any of the five legacy taxonomies into a canonical RiskPassport.

    Args:
        taxonomy: Which taxonomy the level comes from (e.g. "C0-C5", "T0-T4", "low/medium/high")
        level: The risk level string from the legacy taxonomy
        action_class: Legacy action class string
        blast_radius: Legacy blast radius string
        reversibility: Legacy reversibility string
        secret_touch: Legacy secret touch string
        external_effect: Legacy external effect string
        risk_ceiling: Max allowed risk tier for this actor

    Returns:
        Canonical RiskPassport
    """
    # Derive tier and action_class from legacy input
    tier, acl = RiskTier.T0, ActionClass.OBSERVE

    if level:
        mapped = _map_legacy(level, _LEGACY_READONLY_MAP, None)
        if mapped:
            tier, acl = mapped
    elif action_class:
        acl = _map_legacy(action_class, _LEGACY_ACTION_CLASS_MAP, ActionClass.OBSERVE)
        # Derive tier from action class
        tier = _derive_tier_from_action(acl)

    # Override action_class if explicitly provided
    if action_class:
        acl = _map_legacy(action_class, _LEGACY_ACTION_CLASS_MAP, acl)

    return RiskPassport(
        tier=tier,
        action_class=acl,
        blast_radius=_map_legacy(blast_radius, _LEGACY_BLAST_MAP, BlastRadius.LOCAL),
        reversibility=_map_legacy(
            reversibility, _LEGACY_REVERSIBILITY_MAP, ReversibilityLevel.HIGH
        ),
        secret_touch=_map_legacy(secret_touch, _LEGACY_SECRET_MAP, SecretTouch.NONE),
        external_effect=_map_legacy(external_effect, _LEGACY_EXTERNAL_MAP, ExternalEffect.NONE),
        risk_ceiling=risk_ceiling,
    )


def _derive_tier_from_action(action: ActionClass) -> RiskTier:
    """Derive a default tier from action class."""
    return {
        ActionClass.OBSERVE: RiskTier.T0,
        ActionClass.PREPARE: RiskTier.T2,
        ActionClass.MUTATE: RiskTier.T3,
        ActionClass.ATOMIC: RiskTier.T5,
    }.get(action, RiskTier.T0)


# Explicit canonical tool mappings (arifOS Federation)
_CANONICAL_TOOL_RISKS: dict[str, RiskPassport] = {
    # T5 ATOMIC — constitutional / irreversible
    "arif_forge_execute": RiskPassport(
        tier=RiskTier.T5,
        action_class=ActionClass.ATOMIC,
        blast_radius=BlastRadius.INFRA,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
    ),
    "arif_judge_deliberate": RiskPassport(
        tier=RiskTier.T5,
        action_class=ActionClass.ATOMIC,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
    ),
    "arif_vault_seal": RiskPassport(
        tier=RiskTier.T5,
        action_class=ActionClass.ATOMIC,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
    ),
    "arif_heart_critique": RiskPassport(
        # 666_HEART: read-only ethical reflection (critique | simulate |
        # empathize | redteam | maruah | deescalate | summary). The tool
        # never mutates state — it produces advisory output consumed by
        # upstream judgment. Over-classifying as ATOMIC broke legacy
        # callers (Claude web / Perplexity) who could not pass the
        # FederationEnvelope gate. The other 3 ATOMIC tools (judge
        # verdict, vault seal, forge execute) correctly remain ATOMIC
        # because they produce binding decisions or actual mutations.
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
    ),
    "arif_session_init": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
    ),
    # T1 OBSERVE — read-only routing (all modes: status/list/route are non-destructive)
    "arif_kernel_route": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
    ),
    # T1 OBSERVE — bridge connection, no mutation
    "arif_gateway_connect": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
    ),
    # T2 PREPARE — recall/list/get are read-only; store writes but is gated separately
    "arif_memory_recall": RiskPassport(
        tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
    ),
    # T2 PREPARE
    "arif_mind_reason": RiskPassport(
        tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
    ),
    "arif_evidence_fetch": RiskPassport(
        tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
    ),
    # T1 OBSERVE
    "arif_sense_observe": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
    ),
    "arif_ops_measure": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
    ),
    "arif_reply_compose": RiskPassport(
        tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.PUBLIC,
        reversibility=ReversibilityLevel.HIGH,
    ),
}


def classify_tool(tool_name: str, tool_description: str | None = None) -> RiskPassport:
    """
    Classify a tool by its name and description.

    First checks explicit canonical mappings, then falls back to heuristic.
    """
    name = tool_name.lower()
    desc = (tool_description or "").lower()
    combined = name + " " + desc

    # Explicit mapping for canonical tools
    if name in _CANONICAL_TOOL_RISKS:
        return _CANONICAL_TOOL_RISKS[name]

    # T5 ATOMIC: infrastructure-scoped atomic
    if any(
        kw in combined
        for kw in [
            "atomic",
            "deploy",
            "infrastructure",
            "reboot",
            "shutdown",
            "partition",
            "format",
            "drop table",
            "drop database",
            "rm -rf",
            "git push --force",
            "vault999",
            "seal",
        ]
    ):
        return RiskPassport(
            tier=RiskTier.T5,
            action_class=ActionClass.ATOMIC,
            blast_radius=BlastRadius.INFRA,
            reversibility=ReversibilityLevel.IRREVERSIBLE,
        )

    # T4 PUBLIC-scoped mutation
    if any(
        kw in combined
        for kw in [
            "public",
            "broadcast",
            "send email",
            "post tweet",
            "publish",
            "release",
            "merge to main",
            "git push",
        ]
    ):
        return RiskPassport(
            tier=RiskTier.T4,
            action_class=ActionClass.MUTATE,
            blast_radius=BlastRadius.PUBLIC,
        )

    # T3 ORG-scoped mutation
    if any(
        kw in combined
        for kw in [
            "write",
            "modify",
            "update",
            "delete",
            "create",
            "restart service",
            "systemctl",
            "commit",
            "push",
            "migrate",
            "alter",
            "insert",
            "execute",
        ]
    ):
        return RiskPassport(
            tier=RiskTier.T3,
            action_class=ActionClass.MUTATE,
            blast_radius=BlastRadius.ORG,
        )

    # T2 PREPARE
    if any(
        kw in combined
        for kw in [
            "prepare",
            "plan",
            "validate",
            "check",
            "dry-run",
            "lint",
            "test",
            "audit",
            "verify",
            "estimate",
            "simulate",
            "forecast",
            "project",
        ]
    ):
        return RiskPassport(
            tier=RiskTier.T2,
            action_class=ActionClass.PREPARE,
            blast_radius=BlastRadius.ORG,
        )

    # T1 Account-scoped observation
    if any(
        kw in combined
        for kw in [
            "search",
            "fetch",
            "read",
            "get",
            "list",
            "view",
            "query",
            "select",
            "describe",
            "show",
            "inspect",
            "analyze",
            "summary",
        ]
    ):
        return RiskPassport(
            tier=RiskTier.T1,
            action_class=ActionClass.OBSERVE,
            blast_radius=BlastRadius.ACCOUNT,
        )

    # Default: T0 harmless observation
    return RiskPassport(
        tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
    )


def derive_ceiling(
    authority_verified: bool,
    delegation_scope: list[str] | None = None,
    is_f13: bool = False,
) -> RiskTier:
    """
    Derive the risk ceiling for an actor from authority properties.

    Returns the highest tier this actor is allowed to execute.
    """
    if is_f13:
        return RiskTier.T5  # Sovereign has no ceiling
    if authority_verified and delegation_scope and "atomic" in (delegation_scope or []):
        return RiskTier.T5
    if authority_verified and delegation_scope and "mutate" in (delegation_scope or []):
        return RiskTier.T3
    if authority_verified:
        return RiskTier.T2
    return RiskTier.T1  # Unverified authority: observe only
