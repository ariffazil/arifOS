"""
arifosmcp/runtime/a_rif/ — Anomalous Retrieval & Integrity Framework
════════════════════════════════════════════════════════════════════

Truth Substrate package for arifOS.

Modules:
  engine              — Core A-RIF logic (W, ΔS, C, L)
  models              — Unified Pydantic schemas
  search_worthiness   — Search gate
  entropy             — Entropy stopping law
  anomalous_contrast  — Anomaly routing
  source_rank         — Source authority ranking
  attestation         — Proof of custody
  abduction           — Hypothesis generation
  prompt_injection    — External instruction guard
  ssrf_guard          — URL safety validation
  receipts            — Receipt builder
  contradiction       — Contradiction audit
  scorecard           — Effectiveness metrics

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

# Lazy imports to avoid circular dependencies
__all__ = [
    "engine",
    "models",
    "search_worthiness",
    "entropy",
    "anomalous_contrast",
    "source_rank",
    "attestation",
    "abduction",
    "prompt_injection",
    "ssrf_guard",
    "receipts",
    "contradiction",
    "scorecard",
    "get_current_scorecard",
]


def __getattr__(name: str):
    if name == "get_current_scorecard":
        from arifosmcp.runtime.a_rif.scorecard import get_current_scorecard
        return get_current_scorecard
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
