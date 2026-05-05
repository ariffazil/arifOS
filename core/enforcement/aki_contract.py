from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AKIContract:
    name: str = "aki_contract"
    eager_ml_imports: bool = False


CONTRACT = AKIContract()

__all__ = ["AKIContract", "CONTRACT"]

