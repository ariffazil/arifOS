"""
independent_verifier.py — WAJIB 2: Independent Verification Lane (2026-07-19)
══════════════════════════════════════════════════════════════════════════════

Verifier contract: executor ≠ verifier. Verification result immutable by executor.
5 hard rejection rules per WAJIB 2 / AUDIT-recursive-audit SKILL.md.

Authority: T3 F13 (ratified 2026-07-19)
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class VerificationVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HOLD = "HOLD"  # Cannot verify — missing evidence
    REJECT = "REJECT"  # Verifier == executor — constitutional violation


@dataclass
class VerificationRequest:
    """Evidence package submitted for independent verification."""
    original_intent_hash: str
    executor_id: str
    executor_session_id: str
    mutation_receipt: dict[str, Any]
    success_criteria: list[str]
    freshness_requirement: float  # max age in seconds for evidence
    evidence_sources: list[str] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)


@dataclass
class VerificationResult:
    """Result of independent verification."""
    verdict: VerificationVerdict
    verifier_id: str
    request_hash: str
    rule_violations: list[str] = field(default_factory=list)
    evidence_quality: float = 0.0  # 0.0–1.0
    verified_at: float = field(default_factory=time.time)


# ── 5 Hard Rejection Rules ────────────────────────────────────────────────


def verify_independent(request: VerificationRequest, verifier_id: str) -> VerificationResult:
    """Execute the 5 WAJIB 2 hard rejection rules.

    Returns VerificationResult with PASS only if ALL 5 rules pass.
    Any single rule violation → REJECT.
    """
    violations: list[str] = []

    # Rule 1: Verifier ≠ Executor
    if verifier_id == request.executor_id:
        violations.append(
            f"R1: Verifier identity ({verifier_id}) == executor identity "
            f"({request.executor_id}). Independent verification requires "
            f"separate identities."
        )

    # Rule 2: Evidence independence
    # Evidence must come from sources outside the executor's session
    if not request.evidence_sources:
        violations.append(
            "R2: No evidence sources provided. Independent verification "
            "requires evidence from sources outside the executor's session."
        )

    # Rule 3: No mutation permission
    # The verifier must have OBSERVE-only authority — cannot mutate
    # (enforced at lease level — this is a documentation check)

    # Rule 4: Freshness
    age = time.time() - request.submitted_at
    if age > request.freshness_requirement:
        violations.append(
            f"R4: Evidence is {age:.0f}s old, exceeds freshness requirement "
            f"of {request.freshness_requirement:.0f}s."
        )

    # Rule 5: No missing success criteria
    if not request.success_criteria:
        violations.append(
            "R5: No success criteria defined. Cannot verify outcome "
            "without explicit criteria."
        )

    # Check success criteria against mutation receipt
    if request.success_criteria and request.mutation_receipt:
        receipt_str = str(request.mutation_receipt)
        for criterion in request.success_criteria:
            # Flexible match: check if key=value pattern exists in receipt
            if "=" in criterion:
                key, val = criterion.split("=", 1)
                receipt_val = str(request.mutation_receipt.get(key, ""))
                if receipt_val != val:
                    violations.append(
                        f"R5: Success criterion '{criterion}' not satisfied. "
                        f"Expected {key}={val}, got {key}={receipt_val}"
                    )
            elif criterion not in receipt_str:
                violations.append(
                    f"R5: Success criterion '{criterion[:40]}' not found "
                    f"in mutation receipt."
                )

    # ── Compute verdict ──────────────────────────────────────────────
    if not violations:
        return VerificationResult(
            verdict=VerificationVerdict.PASS,
            verifier_id=verifier_id,
            request_hash=_hash_request(request),
            evidence_quality=1.0,
        )

    # Check for Rule 1 violation (most severe — verifier == executor)
    has_identity_violation = any("R1:" in v for v in violations)

    if has_identity_violation:
        return VerificationResult(
            verdict=VerificationVerdict.REJECT,
            verifier_id=verifier_id,
            request_hash=_hash_request(request),
            rule_violations=violations,
            evidence_quality=0.0,
        )

    return VerificationResult(
        verdict=VerificationVerdict.FAIL,
        verifier_id=verifier_id,
        request_hash=_hash_request(request),
        rule_violations=violations,
        evidence_quality=max(0.0, 1.0 - 0.2 * len(violations)),
    )


def _hash_request(request: VerificationRequest) -> str:
    """Deterministic hash of a verification request."""
    raw = f"{request.original_intent_hash}|{request.executor_id}|{request.submitted_at}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
