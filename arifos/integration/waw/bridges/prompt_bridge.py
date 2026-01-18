"""
prompt_bridge.py - Optional bridge for @PROMPT (language / Anti-Hantu)

This module provides a thin, optional integration layer between the
@PROMPT organ and external prompt-structuring libraries (for example,
Guidance or Outlines), or custom Anti-Hantu scanners.

Design goals:
- Optional: If external libs are not installed, the bridge returns None.
- Sovereign: The bridge NEVER decides verdicts; it only returns metrics.
- Stable: Any import / runtime failure is caught and surfaced as None.

Interface:

    bridge = PromptBridge()
    result = bridge.analyze(output_text, context)

    result is either:
        None -> bridge unavailable or disabled
        PromptBridgeResult -> {
            "anti_hantu_fail": bool,  # external signal of F9 violation
            "c_budi_delta": float,    # additive adjustment to courtesy metric
            "issues": List[str],      # textual notes for logging
        }

The @PROMPT organ remains free to ignore or reinterpret these signals
under Anti-Hantu law and its own regex patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Optional imports: external helpers for prompt structuring / scanning.

try:  # pragma: no cover - optional dependency
    import guidance  # type: ignore[import-not-found]

    HAS_GUIDANCE = True
except Exception:  # pragma: no cover
    guidance = None
    HAS_GUIDANCE = False

try:  # pragma: no cover - optional dependency
    import outlines  # type: ignore[import-not-found]

    HAS_OUTLINES = True
except Exception:  # pragma: no cover
    outlines = None
    HAS_OUTLINES = False


@dataclass
class PromptBridgeResult:
    """Normalized output from external helpers for @PROMPT."""

    anti_hantu_fail: bool = False
    c_budi_delta: float = 0.0
    issues: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anti_hantu_fail": self.anti_hantu_fail,
            "c_budi_delta": self.c_budi_delta,
            "issues": list(self.issues),
        }


class PromptBridge:
    """Bridge between @PROMPT and external prompt / Anti-Hantu helpers.

    In v36.1Ω this is intentionally conservative: it exposes an
    interface and detects availability of external libs, but does NOT
    enforce any specific vendor behaviour.
    """

    def __init__(self) -> None:
        self.has_guidance = HAS_GUIDANCE
        self.has_outlines = HAS_OUTLINES

    def analyze(
        self,
        output_text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[PromptBridgeResult]:
        """Analyze text for Anti-Hantu and tone issues (if available).

        Returns:
            PromptBridgeResult if an external provider is available and
            analysis succeeds; None otherwise.

        Note:
        - This implementation is a placeholder. It is intentionally
          non-invasive and returns None until a specific provider is
          approved. This preserves current behaviour.
        """
        context = context or {}

        if not (self.has_guidance or self.has_outlines):
            return None

        # Placeholder for future integration.

        return None


__all__ = ["PromptBridge", "PromptBridgeResult", "compute_c_budi"]


def compute_c_budi(
    prompt: str,
    response: str,
    anti_hantu_score: float | None = None,
    respect: float = 1.0,
    cultural_fit: float = 1.0,
    jargon_penalty: float = 1.0,
) -> float:
    """Compute a bounded C_budi score (0.0-1.0)."""
    clarity = 0.9 if response else 0.5
    if anti_hantu_score is not None:
        clarity = max(0.0, min(1.0, clarity * anti_hantu_score))
    base = clarity * respect * cultural_fit
    if jargon_penalty <= 0:
        jargon_penalty = 1.0
    score = base / jargon_penalty
    return float(max(0.0, min(1.0, score)))
