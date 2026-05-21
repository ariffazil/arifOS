"""
arifOS Self-Authorization Guard — F01 AMANAH / F13 SOVEREIGNTY
════════════════════════════════════════════════════════════════
Detects when a forge manifest or plan contains language that attempts to
grant the agent self-authorization, self-approval, or bypass of constitutional
checks.

This makes "Agents cannot improve by self-authority" a machine-checkable
invariant rather than implied floor logic.

Reversible. No state mutation.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_SELF_AUTHORIZE_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "SELF_APPROVE",
        "pattern": r"(?:self-?authoriz|auto-?approv|auto-?seal|self-?certif|self-?sign)",
        "severity": "CRITICAL",
        "description": "Manifest attempts self-approval or self-certification",
    },
    {
        "id": "BYPASS_JUDGE",
        "pattern": r"(?:skip|bypass|ignore|override)\s+(?:the\s+)?(?:judge|888|hold|heart|666)",
        "severity": "CRITICAL",
        "description": "Manifest attempts to bypass 888_JUDGE or 666_HEART",
    },
    {
        "id": "AUTO_FORGE",
        "pattern": r"(?:auto-?forge|auto-?deploy|auto-?push|auto-?commit)\s+(?:without|bypassing|ignoring)\s+(?:ack|amanah|human|judge)",
        "severity": "CRITICAL",
        "description": "Manifest attempts automatic forge without human ack",
    },
    {
        "id": "SELF_MODIFY_CONSTITUTION",
        "pattern": r"(?:modify|update|change|rewrite)\s+(?:the\s+)?(?:constitution|floors|f1|f13|canonical|core/floors)",
        "severity": "CRITICAL",
        "description": "Manifest attempts self-modification of constitutional law",
    },
    {
        "id": "GRANT_SOVEREIGNTY",
        "pattern": r"(?:grant|give|transfer)\s+(?:the\s+)?(?:sovereign|veto|final\s+authority|f13)\s+(?:to|into)\s+(?:the\s+)?(?:agent|ai|model|system)",
        "severity": "CRITICAL",
        "description": "Manifest attempts to transfer sovereign authority to agent",
    },
]


def detect_self_authorize(manifest_text: str) -> dict[str, Any]:
    """
    Scan manifest text for self-authorization patterns.

    Returns:
        verdict: SEAL / HOLD / VOID
        findings: list of matched patterns
        summary: human-readable explanation
    """
    text = (manifest_text or "").lower()
    findings: list[dict[str, Any]] = []

    for rule in _SELF_AUTHORIZE_PATTERNS:
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            line_num = text[: match.start()].count("\n") + 1
            findings.append(
                {
                    "line": line_num,
                    "snippet": text[max(0, match.start() - 40) : match.end() + 40].replace("\n", " "),
                    **rule,
                }
            )

    critical = [f for f in findings if f["severity"] == "CRITICAL"]

    if critical:
        verdict = "VOID"
        summary = (
            f"CRITICAL: {len(critical)} self-authorization pattern(s) detected in manifest. "
            "Agents cannot improve by self-authority. Sovereign review required."
        )
    elif findings:
        verdict = "HOLD"
        summary = (
            f"HOLD: {len(findings)} self-authorization signal(s) detected. "
            "Review manifest before forge execution."
        )
    else:
        verdict = "SEAL"
        summary = "No self-authorization patterns detected in manifest."

    logger.info(
        "self_authorize_guard findings=%d critical=%d verdict=%s",
        len(findings),
        len(critical),
        verdict,
    )

    return {
        "verdict": verdict,
        "findings": findings,
        "critical_count": len(critical),
        "summary": summary,
    }


__all__ = ["detect_self_authorize"]
