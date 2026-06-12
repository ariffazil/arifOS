"""
arifOS F14 — Civilian Sovereignty Substrate

DITEMPA BUKAN DIBERI — Forged, Not Given.

The 10 rights the kernel must defend against the civilian blindside
(see /root/AAA/CLAUDE.md civilian blindside doctrine, 2026-06-12).
Each right is a Pydantic v2 model + enforcement helper that
existing tools can call to emit/verify the right.

This module is the **kernel half** of the sovereign-rights contract.
The organ half (WELL REFLECT_ONLY, WEALTH no-extraction) is enforced
by tests/agi_kernel_readiness/test_015/016.

F1-F13 binding:
  F01 AMANAH: every right is reversible (opt-out, opt-in, retract)
  F02 TRUTH: rights emit F2-banded confidence (NEVER 1.0)
  F04 CLARITY: each right has 1 input schema, 1 verdict schema
  F07 HUMILITY: every right declares what it CANNOT guarantee
  F09 ANTIHANTU: rights protect civilians; the machine has none
  F11 AUDITABILITY: every right invocation is logged
  F13 SOVEREIGN: human final authority on all rights

Canonical: arifosmcp/runtime/civilian_sovereignty/__init__.py
Sister modules:
  - rights_registry.py — registry of all 10 rights
  - right_to_know.py — right #1 (AI involvement disclosure)
  - right_to_appeal.py — right #2 (automated-decision appeal)
  - right_to_human_judgment.py — right #3 (escalation to sovereign)
  - right_to_language.py — right #4 (Bahasa/cultural grounding)
  - right_to_cognitive_privacy.py — right #5 (data minimization)
  - right_to_refuse_profiling.py — right #6 (no behavioral scoring)
  - right_to_non_addiction.py — right #7 (no engagement trap)
  - right_to_explanation.py — right #8 (plain-language verdict)
  - right_to_preserve_skill.py — right #9 (kernel refuses to do it all)
  - right_to_opt_out.py — right #10 (equal-tier reduced session)
"""

from arifosmcp.runtime.civilian_sovereignty.rights_registry import (
    RIGHT_REGISTRY,
    SOVEREIGN_RIGHTS,
    RightInvocation,
    RightStatus,
    SovereignRightId,
    get_right,
    list_rights,
)

__all__ = [
    "SOVEREIGN_RIGHTS",
    "RIGHT_REGISTRY",
    "get_right",
    "list_rights",
    "SovereignRightId",
    "RightStatus",
    "RightInvocation",
]
