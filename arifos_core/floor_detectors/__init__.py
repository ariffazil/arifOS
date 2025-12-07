"""
floor_detectors — Python-Sovereign Floor Detection (PHOENIX SOVEREIGNTY v36.1Ω)

This module implements the "Dumb Code, Smart Model" architecture.
These detectors are RIGID, DETERMINISTIC, and OVERRIDE LLM self-reports.

Axiom: "AI cannot self-legitimize."
Motto: "DITEMPA BUKAN DIBERI" — Measure, don't ask.

Modules:
    amanah_risk_detectors: F1 Amanah sovereign detection (irreversibility, destruction)
"""

from arifos_core.floor_detectors.amanah_risk_detectors import (
    AmanahDetector,
    AmanahResult,
    RiskLevel,
    AMANAH_DETECTOR,
)

__all__ = [
    "AmanahDetector",
    "AmanahResult",
    "RiskLevel",
    "AMANAH_DETECTOR",
]
