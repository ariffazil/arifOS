from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass
from typing import Any

from core.intelligence import compute_w3


@dataclass
class VerificationReport:
    content_hash: str
    hash_match: bool
    integrity_score: float


@dataclass
class ValidationResult:
    w3_score: float
    verification: VerificationReport
    state_diff: str | None


class ExecutionValidator:
    def __init__(self, session_id: str):
        self.session_id = session_id

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def validate_execution(
        self,
        expected: dict[str, Any],
        actual: dict[str, Any],
        human_approved: bool = False,
        compute_diff: bool = False,
    ) -> ValidationResult:
        actual_stdout = actual.get("stdout", "")
        content_hash = self._compute_hash(actual_stdout)
        expected_hash = expected.get("verification_hash")
        hash_match = bool(expected_hash) and expected_hash == content_hash
        integrity_score = 1.0 if hash_match else 0.8 if actual.get("success") else 0.2
        diff = None
        if compute_diff:
            diff = "\n".join(
                difflib.unified_diff(
                    str(expected.get("stdout", "")).splitlines(),
                    str(actual_stdout).splitlines(),
                    lineterm="",
                )
            )
        w3 = compute_w3(1.0 if human_approved else 0.8, 0.95 if actual.get("success") else 0.3, integrity_score)
        return ValidationResult(
            w3_score=w3,
            verification=VerificationReport(
                content_hash=content_hash,
                hash_match=hash_match,
                integrity_score=integrity_score,
            ),
            state_diff=diff,
        )


def validate(
    expected: dict[str, Any],
    actual: dict[str, Any],
    session_id: str,
    compute_diff: bool = False,
) -> ValidationResult:
    validator = ExecutionValidator(session_id)
    return validator.validate_execution(
        expected=expected,
        actual=actual,
        human_approved=True,
        compute_diff=compute_diff,
    )

