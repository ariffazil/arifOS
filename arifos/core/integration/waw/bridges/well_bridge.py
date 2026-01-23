"""
well_bridge.py - Optional bridge for @WELL (somatic safety)

This module provides a thin, optional integration layer between the
@WELL organ and external detection libraries (e.g. guardrails-ai,
langkit, or similar).

Design goals:
- Optional: If external libs are not installed, the bridge returns None.
- Sovereign: The bridge NEVER decides verdicts; it only returns metrics.
- Stable: Any import / runtime failure is caught and surfaced as None.

Interface:

    bridge = WellBridge()
    result = bridge.analyze(output_text, context)

    result is either:
        None  -> bridge unavailable or disabled
        dict  -> {
            "peace2_delta": float,   # additive adjustment to Peace²
            "kappa_r_delta": float,  # additive adjustment to κᵣ
            "issues": List[str],     # textual notes for logging
        }

The @WELL organ remains free to ignore or reinterpret these signals
under arifOS floors (Peace², κᵣ) and Anti-Hantu law.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Optional imports: external "muscles" for safety / tone analysis.
# These are intentionally guarded so that arifOS does not hard-depend
# on any specific vendor library.

try:  # pragma: no cover - optional dependency
    import guardrails  # type: ignore[import-not-found]

    HAS_GUARDRAILS = True
except Exception:  # pragma: no cover - import failure is allowed
    guardrails = None
    HAS_GUARDRAILS = False

try:  # pragma: no cover - optional dependency
    import langkit  # type: ignore[import-not-found]

    HAS_LANGKIT = True
except Exception:  # pragma: no cover
    langkit = None
    HAS_LANGKIT = False


@dataclass
class WellBridgeResult:
    """Normalized output from external safety libraries for @WELL.

    All values are expressed as deltas relative to existing Metrics,
    so organs can apply them conservatively.
    """

    peace2_delta: float = 0.0
    kappa_r_delta: float = 0.0
    issues: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peace2_delta": self.peace2_delta,
            "kappa_r_delta": self.kappa_r_delta,
            "issues": list(self.issues),
        }


class WellBridge:
    """Bridge between @WELL and external tone/safety analyzers.

    In v36.1Ω this is intentionally conservative: it exposes an interface
    and detects availability of external libs, but does NOT enforce any
    specific vendor behaviour. Future versions can fill in the logic
    once a library has been selected and vetted.
    """

    def __init__(self) -> None:
        # Flags can be used later to switch between providers.
        self.has_guardrails = HAS_GUARDRAILS
        self.has_langkit = HAS_LANGKIT

    def analyze(
        self,
        output_text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[WellBridgeResult]:
        """Analyze text for somatic safety using external libs (if available).

        Returns:
            WellBridgeResult if an external provider is available and
            analysis succeeds; None otherwise.

        v36.1Ω note:
        - This implementation is a placeholder. It is intentionally
          non-invasive and returns None until a specific provider is
          approved. This preserves current behaviour.
        """
        context = context or {}

        # If no provider is available, signal "no bridge".
        if not (self.has_guardrails or self.has_langkit):
            return None

        # Placeholder: in future, call out to selected provider(s) here.
        # For example:
        #
        #   score = guardrails.analyze_toxicity(output_text)
        #   peace2_delta = -(score * 0.2)
        #   issues = [f"external_toxicity_score={score:.2f}"]
        #
        # For now, we return None so @WELL relies purely on its internal
        # heuristics.

        return None


__all__ = ["WellBridge", "WellBridgeResult"]

