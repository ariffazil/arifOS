"""
core/uncertainty_engine.py — Legacy compatibility shim

The uncertainty engine was merged into the judgment pipeline during
architectural unification. This module provides backward-compatible
exports for existing imports.
"""

from __future__ import annotations

from typing import Any


class UncertaintyEngine:
    """Legacy uncertainty engine shim."""

    def __init__(self) -> None:
        pass

    def evaluate(self, content: str, context: dict | None = None) -> dict[str, Any]:
        return {"uncertainty": 0.0, "confidence": 1.0, "entropy": 0.0}


def calculate_uncertainty(evidence: Any) -> float:
    """Legacy uncertainty calculation shim."""
    return 0.0
