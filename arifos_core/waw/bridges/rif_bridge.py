"""
rif_bridge.py - Optional bridge for @RIF (epistemic rigor)

This module provides a thin, optional integration layer between the
@RIF organ and external reasoning / evaluation libraries (for example,
Ragas for answer quality or DSPy-style chains for reasoning traces).

Design goals:
- Optional: If external libs are not installed, the bridge returns None.
- Sovereign: The bridge NEVER decides verdicts; it only returns metrics.
- Stable: Any import / runtime failure is caught and surfaced as None.

Interface:

    bridge = RifBridge()
    result = bridge.analyze(output_text, context)

    result is either:
        None -> bridge unavailable or disabled
        RifBridgeResult -> {
            "delta_s_delta": float,  # additive adjustment to ΔS
            "truth_delta": float,    # additive adjustment to Truth
            "issues": List[str],     # textual notes for logging
        }

The @RIF organ remains free to ignore or reinterpret these signals
under arifOS floors (ΔS, Truth) and its own heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Optional imports: external "muscles" for epistemic checks.
# These are intentionally guarded so that arifOS does not hard-depend
# on any specific vendor library.

try:  # pragma: no cover - optional dependency
    import ragas  # type: ignore[import-not-found]

    HAS_RAGAS = True
except Exception:  # pragma: no cover - import failure is allowed
    ragas = None
    HAS_RAGAS = False

try:  # pragma: no cover - optional dependency
    import dspy  # type: ignore[import-not-found]

    HAS_DSPY = True
except Exception:  # pragma: no cover
    dspy = None
    HAS_DSPY = False


@dataclass
class RifBridgeResult:
    """Normalized output from external epistemic libraries for @RIF.

    Values are expressed as deltas relative to existing Metrics so that
    organs can apply them conservatively.
    """

    delta_s_delta: float = 0.0
    truth_delta: float = 0.0
    issues: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.issues is None:
            self.issues = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "delta_s_delta": self.delta_s_delta,
            "truth_delta": self.truth_delta,
            "issues": list(self.issues),
        }


class RifBridge:
    """Bridge between @RIF and external epistemic analyzers.

    In v36.1Ω this is intentionally conservative: it exposes an
    interface and detects availability of external libs, but does NOT
    enforce any specific vendor behaviour. Future versions can fill in
    the logic once a library has been selected and vetted.
    """

    def __init__(self) -> None:
        self.has_ragas = HAS_RAGAS
        self.has_dspy = HAS_DSPY

    def analyze(
        self,
        output_text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[RifBridgeResult]:
        """Analyze text for epistemic rigor using external libs (if available).

        Returns:
            RifBridgeResult if an external provider is available and
            analysis succeeds; None otherwise.

        Note:
        - This implementation is a placeholder. It is intentionally
          non-invasive and returns None until a specific provider is
          approved. This preserves current behaviour.
        """
        context = context or {}

        if not (self.has_ragas or self.has_dspy):
            return None

        # Placeholder: wire up external evaluation here in future.
        # For example, compute answer quality and adjust delta_s_delta
        # or truth_delta accordingly, while appending human-readable
        # issues for logging.

        return None


__all__ = ["RifBridge", "RifBridgeResult"]

