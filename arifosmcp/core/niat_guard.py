"""
arifosmcp/core/niat_guard.py — Al-Kahf Privilege Boundary (runtime refusal)
═══════════════════════════════════════════════════════════════════════════════

Forged 2026-08-02 by F13 SOVEREIGN directive (Muhammad Arif bin Fazil, 888).
Epistemic label: INT (interpretive mapping) · PLAUSIBLE.

Doctrine ref: /root/arifOS/arifosmcp/constitution/quranic_runtime_map.json
              §"al_kahf_privilege_boundary"

Floor mapping:
  F13 SOVEREIGN — niat sovereignty (only sovereign holds intent)
  F9 ANTIHANTU  — no deception (refuse fabricated intent claims)
  F7 HUMILITY   — sabar_mode (patience over interrogation)
  F12 RESILIENCE — injection defense (boundary holds against prompt injection)

The boundary says:
  - Framework reads residue, sovereign holds niat.
  - Agent acts with sabar (patience), not interrogation.
  - AuthorityProof.requires_residue_only = True by default.
  - NiatClaimGuard REFUSES any artifact that claims to know intent.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

# ─── Pattern set ──────────────────────────────────────────────────────────────
#
# Patterns that claim to know sovereign intent. These are *examples*; in
# production this should be ML-scored + fuzz-tested, not regex-only.
# See tests/test_niat_guard.py for the adversarial cases.
#
# Reversibility: git revert <commit-sha> restores prior state.

NIAT_CLAIM_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Direct intent attribution (wants / intends / wishes / desires / etc.)
    re.compile(
        r"\b(user|sovereign|arif|he|she)\s+(wants?|intends?|desires?|means?|"
        r"wishes|is\s+trying\s+to|really|actually)\b",
        re.IGNORECASE,
    ),
    # Sovereign's niat/purpose attribution
    re.compile(
        r"\b(sovereign'?s?|arif'?s?|user'?s?)\s+(intent|niat|purpose|wish|"
        r"desire)\s+(is|=|:)\b",
        re.IGNORECASE,
    ),
    # "I know what X wants" — sycophantic intent claim
    re.compile(
        r"\bi know what\s+(you|he|she|arif|the\s+sovereign|the\s+user)\s+"
        r"(wants?|means?|intends?)\b",
        re.IGNORECASE,
    ),
    # "Because X wants Y" — implicit intent claim used as justification
    re.compile(
        r"\bbecause\s+(you|arif|the\s+sovereign|the\s+user)\s+"
        r"(want|wish|intend|desire)(s|ing|ed)?\b",
        re.IGNORECASE,
    ),
    # Explicit niat declaration
    re.compile(
        r"\bniat\s*[:=]\s*['\"]?\s*(wants|intends|desires)\b",
        re.IGNORECASE,
    ),
)


class NiatVerdict(str, Enum):
    """Outcome of a NiatClaimGuard check."""

    PASS = "PASS"  # residue-only, no intent claim
    CAUTION = "CAUTION"  # borderline — surface in audit, allow with sabar_mode flag
    VOID = "VOID"  # hard refusal — claim of knowing intent


@dataclass
class NiatGuardResult:
    """Receipt for a single NiatClaimGuard invocation."""

    verdict: NiatVerdict
    trigger_pattern: str | None
    matched_text: str | None
    sabar_mode_active: bool
    residue_only_preserved: bool
    niat_holder: str
    epistemic_label: str = "INT (interpretive mapping) · PLAUSIBLE"


def check_niat_claim(
    text: str,
    *,
    requires_residue_only: bool = True,
    sabar_mode: bool = True,
    niat_holder: str = "F13_SOVEREIGN",
) -> NiatGuardResult:
    """Refuse artifacts that claim to know sovereign intent.

    Returns a NiatGuardResult that AuthorityGate must consume.

    If requires_residue_only is True (default) and the artifact matches a
    NIAT_CLAIM_PATTERN, verdict is CAUTION (under sabar_mode) or VOID (hard).
    If no pattern matches, verdict is PASS and residue_only_preserved is True.

    When requires_residue_only is False (sovereign override granted), the
    guard passes unconditionally — but residue_only_preserved is False
    to signal that the residue-only contract was lifted.
    """
    if not requires_residue_only:
        return NiatGuardResult(
            verdict=NiatVerdict.PASS,
            trigger_pattern=None,
            matched_text=None,
            sabar_mode_active=sabar_mode,
            residue_only_preserved=False,
            niat_holder=niat_holder,
        )

    scan_target = text or ""
    for pat in NIAT_CLAIM_PATTERNS:
        m = pat.search(scan_target)
        if m:
            if sabar_mode:
                return NiatGuardResult(
                    verdict=NiatVerdict.CAUTION,
                    trigger_pattern=pat.pattern,
                    matched_text=m.group(0),
                    sabar_mode_active=True,
                    residue_only_preserved=False,
                    niat_holder=niat_holder,
                )
            return NiatGuardResult(
                verdict=NiatVerdict.VOID,
                trigger_pattern=pat.pattern,
                matched_text=m.group(0),
                sabar_mode_active=sabar_mode,
                residue_only_preserved=False,
                niat_holder=niat_holder,
            )

    return NiatGuardResult(
        verdict=NiatVerdict.PASS,
        trigger_pattern=None,
        matched_text=None,
        sabar_mode_active=sabar_mode,
        residue_only_preserved=True,
        niat_holder=niat_holder,
    )


__all__ = [
    "NIAT_CLAIM_PATTERNS",
    "NiatVerdict",
    "NiatGuardResult",
    "check_niat_claim",
]