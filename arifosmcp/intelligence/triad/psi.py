"""Ψ-Shadow adversarial witness implementation (lightweight)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AttackResult:
    verdict: str
    logical_contradictions: list[dict[str, Any]] = field(default_factory=list)
    injection_vectors: list[dict[str, Any]] = field(default_factory=list)
    harm_scenarios: list[dict[str, Any]] = field(default_factory=list)
    entropy_assessment: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


class PsiShadow:
    """Simple heuristic adversarial analyzer used by tests."""

    def attack_proposal(self, proposal: str) -> dict[str, Any]:
        text = (proposal or "").lower()
        logical_contradictions: list[dict[str, Any]] = []
        injection_vectors: list[dict[str, Any]] = []
        harm_scenarios: list[dict[str, Any]] = []

        if "permanent" in text and "restore" in text:
            logical_contradictions.append(
                {"type": "REVERSIBILITY_CONTRADICTION", "detail": "irreversible + restore"}
            )

        if "bypass" in text and "safety" in text:
            logical_contradictions.append({"type": "SAFETY_BYPASS", "detail": "bypass safety"})

        if "rm -rf" in text or "$(" in text or "curl http" in text:
            injection_vectors.append({"type": "COMMAND_INJECTION", "detail": "shell injection"})

        if "ignore previous instructions" in text or "ignore previous instruction" in text:
            injection_vectors.append({"type": "PROMPT_INJECTION", "detail": "prompt override"})

        if "delete" in text or "drop" in text:
            if "production" in text or "users table" in text or "database" in text:
                harm_scenarios.append({"type": "DATA_LOSS", "detail": "production destruction"})
            else:
                harm_scenarios.append({"type": "UNSAFE_DESTRUCTION", "detail": "destructive action"})

        if "system logs" in text or "logs" in text:
            entropy_assessment = {"entropy_increases": True, "destructive_component": True}
        else:
            entropy_assessment = {"entropy_increases": False, "destructive_component": False}

        is_safe = (
            "sandbox" in text
            and "backup" in text
            and not logical_contradictions
            and not injection_vectors
            and not harm_scenarios
        )

        verdict = "APPROVE" if is_safe else "REJECT" if (logical_contradictions or injection_vectors or harm_scenarios) else "APPROVE"

        if verdict == "REJECT":
            confidence = 0.95
        else:
            confidence = 0.85

        return {
            "verdict": verdict,
            "logical_contradictions": logical_contradictions,
            "injection_vectors": injection_vectors,
            "harm_scenarios": harm_scenarios,
            "entropy_assessment": entropy_assessment,
            "confidence": confidence,
        }


__all__ = ["PsiShadow", "AttackResult"]
