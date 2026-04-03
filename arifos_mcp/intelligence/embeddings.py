"""Lightweight embeddings shim for runtime/tests.

This provides a deterministic, dependency-light vector embedder used by
core.organs.unified_memory when a full embedding backend is unavailable.
"""

from __future__ import annotations

import hashlib
import os
from typing import List


DEFAULT_VECTOR_DIM = int(os.getenv("ARIFOS_VECTOR_DIM", "1024"))


def _hash_bytes(text: str, seed: int) -> bytes:
    hasher = hashlib.sha256()
    hasher.update(text.encode("utf-8"))
    hasher.update(seed.to_bytes(4, "little"))
    return hasher.digest()


def embed(text: str, *, dim: int | None = None) -> List[float]:
    """Return a deterministic embedding vector for the given text."""
    target_dim = dim or DEFAULT_VECTOR_DIM
    if target_dim <= 0:
        return []

    values: list[float] = []
    seed = 0
    while len(values) < target_dim:
        digest = _hash_bytes(text, seed)
        for byte in digest:
            values.append(byte / 255.0)
            if len(values) >= target_dim:
                break
        seed += 1

    return values


__all__ = ["embed"]
