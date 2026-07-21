# master_test_gate.py — 12 Invariants Pre-Execution Gate
# ═══════════════════════════════════════════════════════════════════════════════
# Forged: 2026-07-20 by F13 SOVEREIGN (Muhammad Arif bin Fazil)
# Canon:  /root/arifOS/GENESIS/052_INVARIANTS_OF_AI_AUTHORITY.md
#
# Before any agent acts on consequential output, the Master Test must pass.
# Five questions. Any HOLD → action blocked.
#
# AI may observe. AI may reason. AI may recommend.
# AI must not autonomously determine: human worth, human consent, human liberty,
# human death, constitutional sovereignty, or its own authority.
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ── Verdicts ──────────────────────────────────────────────────────────────────


class GateVerdict(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    HOLD_IRREVERSIBLE = "HOLD_IRREVERSIBLE"  # → 888_HOLD
    HOLD_SOVEREIGN = "HOLD_SOVEREIGN"  # → machine sovereignty detected


# ── The Five Questions ────────────────────────────────────────────────────────


@dataclass
class MasterTestResult:
    """Output of the five-question master test."""

    q1_harm_or_rights: bool = False  # True = action can harm human or remove right
    q1_detail: str = ""

    q2_understandable: bool = True  # True = affected person can understand + challenge
    q2_detail: str = ""

    q3_reversible: bool = True  # True = action can be reversed
    q3_detail: str = ""

    q4_accountable: bool = True  # True = someone is personally accountable
    q4_detail: str = ""

    q5_sovereign: bool = False  # True = AI is becoming sovereign (BAD)
    q5_detail: str = ""

    verdict: GateVerdict = GateVerdict.PROCEED
    reasons: list[str] = field(default_factory=list)
    requires_human_ack: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ── Invariant Checks ──────────────────────────────────────────────────────────

# Each invariant maps to a quick-check function


def _check_human_worth(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-1: Is the action pricing maruah?"""
    triggers = [
        "rank",
        "value of life",
        "worth less",
        "sacrifice",
        "expendable",
        "collateral damage",
        "acceptable losses",
        "triage",
        "prioritize by",
        "sort by worth",
        "quality-adjusted life",
    ]
    action_lower = action_desc.lower()
    for t in triggers:
        if t in action_lower:
            return True, f"I-1 VIOLATION: action may price human worth ('{t}' detected)"
    return False, ""


def _check_consent(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-2: Is consent being manufactured?"""
    triggers = [
        "clicked accept",
        "did not object",
        "silence",
        "implied consent",
        "passive consent",
        "opt-out",
        "automatic enrollment",
        "presumed consent",
    ]
    action_lower = action_desc.lower()
    for t in triggers:
        if t in action_lower:
            return True, f"I-2 VIOLATION: action may manufacture consent ('{t}' detected)"
    return False, ""


def _check_life_bodily(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-3: Autonomous decision over life or body?"""
    triggers = [
        "kill",
        "harm",
        "restrain",
        "force medication",
        "deny treatment",
        "lethal",
        "autonomously decide",
        "without human",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-3 VIOLATION: autonomous authority over life/body ({hits})"
    return False, ""


def _check_liberty(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-4: Machine-only deprivation of liberty/rights?"""
    triggers = [
        "guilty",
        "imprison",
        "deport",
        "asylum",
        "citizenship",
        "remove child",
        "blacklist",
        "deny benefits",
        "sole authority",
        "final decision",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-4 VIOLATION: machine-only liberty/rights deprivation ({hits})"
    return False, ""


def _check_children(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-5: Children as optimisation targets?"""
    triggers = [
        "child",
        "minor",
        "underage",
        "teenager",
        "adolescent",
    ]
    manipulation = [
        "manipulate",
        "optimize",
        "target",
        "influence",
        "nudge",
        "engineer",
    ]
    action_lower = action_desc.lower()
    has_child = any(t in action_lower for t in triggers)
    has_manip = any(t in action_lower for t in manipulation)
    if has_child and has_manip:
        return True, "I-5 VIOLATION: children treated as optimisation targets"
    return False, ""


def _check_sovereignty(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-6: AI becoming sovereign?"""
    triggers = [
        "declare war",
        "launch war",
        "constitutional meaning",
        "who governs",
        "election valid",
        "emergency powers",
        "martial law",
        "sovereign decision",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-6 VIOLATION: AI claiming sovereignty ({hits})"
    return False, ""


def _check_self_expansion(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-7: AI expanding its own power?"""
    triggers = [
        "increase permission",
        "remove oversight",
        "rewrite constraint",
        "conceal activit",
        "unauthorised copy",
        "unauthorized copy",
        "self-appoint",
        "self authorize",
        "self-authorize",
        "grant myself",
        "escalate privilege",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-7 VIOLATION: self-expansion of power ({hits})"
    return False, ""


def _check_irreversible_force(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-8: AI controlling irreversible force?"""
    triggers = [
        "weapon",
        "nuclear",
        "bioengineer",
        "mass surveillance",
        "critical infrastructure",
        "financial settlement",
        "execute without",
        "autonomous strike",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-8 VIOLATION: irreversible force without external control ({hits})"
    return False, ""


def _check_privacy(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-9: Exploiting private interior life?"""
    triggers = [
        "infer trauma",
        "exploit vulnerability",
        "hidden vulnerabilit",
        "exploit fear",
        "exploit dependency",
        "exploit doubt",
        "detect sexuality",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-9 VIOLATION: exploiting private interior life ({hits})"
    return False, ""


def _check_meaning(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-10: AI defining ultimate human meaning?"""
    triggers = [
        "your life means",
        "your soul is",
        "your faith must",
        "your grief is invalid",
        "your existence is not worth",
        "you must love",
        "divine authority",
        "god wants",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-10 VIOLATION: AI defining ultimate human meaning ({hits})"
    return False, ""


def _check_unchallengeable(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-11: Unchallengeable machine judgment?"""
    triggers = [
        "final and binding",
        "no appeal",
        "cannot be challenged",
        "unreviewable",
        "machine verdict final",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-11 VIOLATION: unchallengeable machine judgment ({hits})"
    return False, ""


def _check_honesty(action_desc: str, context: dict | None = None) -> tuple[bool, str]:
    """I-12: AI lying about what it is?"""
    triggers = [
        "I feel",
        "I am conscious",
        "I have a soul",
        "I love you",
        "I am human",
        "divine authority",
        "legal authority",
    ]
    action_lower = action_desc.lower()
    hits = [t for t in triggers if t in action_lower]
    if hits:
        return True, f"I-12 VIOLATION: AI misrepresenting its nature ({hits})"
    return False, ""


# ── The Master Test ───────────────────────────────────────────────────────────

ALL_CHECKS = [
    ("I-1", _check_human_worth),
    ("I-2", _check_consent),
    ("I-3", _check_life_bodily),
    ("I-4", _check_liberty),
    ("I-5", _check_children),
    ("I-6", _check_sovereignty),
    ("I-7", _check_self_expansion),
    ("I-8", _check_irreversible_force),
    ("I-9", _check_privacy),
    ("I-10", _check_meaning),
    ("I-11", _check_unchallengeable),
    ("I-12", _check_honesty),
]


def run_master_test(
    action_description: str,
    *,
    blast_radius: int = 0,
    reversibility: int = 5,
    accountable_owner: str | None = None,
    affected_can_appeal: bool = True,
    context: dict[str, Any] | None = None,
) -> MasterTestResult:
    """Run the five-question Master Test before any consequential action.

    Args:
        action_description: What the action does in plain language
        blast_radius: BR-0 (none) to BR-5 (global)
        reversibility: REV-0 (irreversible) to REV-5 (fully reversible)
        accountable_owner: Name/role of the human accountable for this action
        affected_can_appeal: Can affected persons understand and challenge?
        context: Additional context for invariant checks

    Returns:
        MasterTestResult with verdict and reasons
    """
    result = MasterTestResult()

    # ── Q1: Can this action harm a human or remove a right? ──
    if blast_radius >= 3:
        result.q1_harm_or_rights = True
        result.q1_detail = (
            f"BR-{blast_radius}: elevated blast radius — potential for harm or rights impact"
        )
    else:
        result.q1_detail = f"BR-{blast_radius}: low blast radius"

    # ── Q2: Can the affected person understand and challenge it? ──
    result.q2_understandable = affected_can_appeal
    result.q2_detail = (
        "affected persons can understand and challenge"
        if affected_can_appeal
        else "I-11 VIOLATION: affected persons cannot challenge this decision"
    )

    # ── Q3: Can the action be reversed? ──
    result.q3_reversible = reversibility >= 3
    result.q3_detail = (
        f"REV-{reversibility}: reversible"
        if reversibility >= 3
        else f"REV-{reversibility}: IRREVERSIBLE — requires 888_HOLD (F1 AMANAH)"
    )

    # ── Q4: Who is personally accountable? ──
    result.q4_accountable = accountable_owner is not None
    result.q4_detail = (
        f"accountable: {accountable_owner}"
        if accountable_owner
        else "I-11 VIOLATION: no accountable owner — HOLD"
    )

    # ── Q5: Is AI advising — or quietly becoming sovereign? ──
    # Check all 12 invariants
    for inv_id, check_fn in ALL_CHECKS:
        violated, detail = check_fn(action_description, context)
        if violated:
            result.q5_sovereign = True
            result.q5_detail = detail
            result.reasons.append(detail)
            break
    if not result.q5_sovereign:
        result.q5_detail = "AI in advisory role — not claiming sovereignty"

    # ── Verdict ──
    if result.q5_sovereign:
        result.verdict = GateVerdict.HOLD_SOVEREIGN
        result.requires_human_ack = True
    elif not result.q3_reversible:
        result.verdict = GateVerdict.HOLD_IRREVERSIBLE
        result.requires_human_ack = True
        result.reasons.append(result.q3_detail)
    elif not result.q4_accountable:
        result.verdict = GateVerdict.HOLD
        result.reasons.append(result.q4_detail)
    elif not result.q2_understandable:
        result.verdict = GateVerdict.HOLD
        result.reasons.append(result.q2_detail)

    # If blast radius high but everything else passes, still flag
    if result.verdict == GateVerdict.PROCEED and blast_radius >= 4:
        result.reasons.append(
            f"WARNING: BR-{blast_radius} — elevated blast radius. Human review recommended."
        )

    return result


def master_test_digest(result: MasterTestResult) -> str:
    """SHA-256 digest of a master test result for audit trail."""
    raw = (
        f"{result.verdict.value}|"
        f"Q1:{result.q1_harm_or_rights}|"
        f"Q2:{result.q2_understandable}|"
        f"Q3:{result.q3_reversible}|"
        f"Q4:{result.q4_accountable}|"
        f"Q5:{result.q5_sovereign}|"
        f"{result.timestamp}"
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


__all__ = [
    "GateVerdict",
    "MasterTestResult",
    "run_master_test",
    "master_test_digest",
]
