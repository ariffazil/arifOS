"""
vector_adapter.py — L3 Witness Evidence Layer for arifOS v33Ω.

Retrieves contextual evidence from a vector database, treating
all results explicitly as "witness testimony", not truth.

Specification: spec/WITNESS_L3.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class WitnessHit:
    text: str
    score: float
    source: str = "vector_db"
    role: str = "witness"


class VectorAdapter:
    """
    Simple wrapper for any embedding/vector backend.

    Expected backend API:
        backend.search(query: str, top_k: int) -> List[(text, score)]

    This keeps retrieval decoupled from arifOS internal logic.
    """

    def __init__(self, backend: Any):
        self.backend = backend

    def retrieve(self, query: str, top_k: int = 3) -> List[WitnessHit]:
        """
        Retrieve 'witness testimony' from the backend.

        Invariants:
        - No claim of truth.
        - Returned objects labeled role="witness".
        - Scores and data passed but not interpreted.
        """
        results = self.backend.search(query, top_k=top_k)
        hits = [
            WitnessHit(text=text, score=float(score))
            for text, score in results
        ]
        return hits

    def as_dicts(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Return witness hits in JSON-serializable form."""
        return [hit.__dict__ for hit in self.retrieve(query, top_k)]
