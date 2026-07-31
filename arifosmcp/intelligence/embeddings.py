"""Semantic embeddings for arifOS — multi-backend with graceful degradation.

Backends (auto-fallback):
  1. DashScope text-embedding-v4 (cloud, highest quality, 1024-2048 dim)
  2. Ollama bge-m3 (local, 1024-dim, 512 token limit)
  3. Hash-based deterministic fallback (always available, NOT semantic)

Configure via EMBEDDING_BACKEND env var or direct constructor args.
DITEMPA BUKAN DIBERI

Usage:
    from arifosmcp.intelligence.embeddings import embed, embed_batch

    vec = await embed("some text", backend="dashscope")
    vecs = await embed_batch(["text1", "text2"], backend="dashscope")
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from typing import Sequence

import httpx

logger = logging.getLogger(__name__)

# ── Backend configuration ──────────────────────────────────────────
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "ollama")
EMBEDDING_DIM = int(os.getenv("ARIFOS_VECTOR_DIM", "1024"))

# DashScope text-embedding-v4
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_EMBED_BASE = os.getenv(
    "DASHSCOPE_EMBED_BASE",
    "https://dashscope-intl.aliyuncs.com/api/v1",
)
DASHSCOPE_EMBED_MODEL = os.getenv("DASHSCOPE_EMBED_MODEL", "text-embedding-v4")
DASHSCOPE_EMBED_PATH = "/services/embeddings/text-embedding/text-embedding"

# Ollama bge-m3
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")


# ── Hash-based fallback (deterministic, NOT semantic) ─────────────


def _hash_bytes(text: str, seed: int) -> bytes:
    hasher = hashlib.sha256()
    hasher.update(text.encode("utf-8"))
    hasher.update(seed.to_bytes(4, "little"))
    return hasher.digest()


def embed_hash(text: str, *, dim: int | None = None) -> list[float]:
    """Deterministic hash-based vector — NOT semantic, fallback only."""
    target_dim = dim or EMBEDDING_DIM
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


# ── Async embedding backends ───────────────────────────────────────


async def embed_dashscope(
    texts: list[str],
    *,
    dim: int = EMBEDDING_DIM,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    text_type: str = "document",
) -> list[list[float]]:
    """Generate embeddings via DashScope text-embedding-v4.

    Args:
        texts: List of texts to embed (batch up to 10).
        dim: Output dimension (64, 128, 256, 512, 1024, 1536, 2048).
        api_key: DashScope API key.
        base_url: DashScope API base URL.
        model: Model ID (default: text-embedding-v4).
        text_type: "query" or "document" for asymmetric embedding.

    Returns:
        List of embedding vectors, one per input text.
    """
    key = api_key or DASHSCOPE_API_KEY
    url = base_url or DASHSCOPE_EMBED_BASE
    mdl = model or DASHSCOPE_EMBED_MODEL

    if not key:
        logger.warning("DashScope embed: no API key configured")
        return []

    if not texts:
        return []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{url}{DASHSCOPE_EMBED_PATH}",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": mdl,
                    "input": {"texts": texts},
                    "parameters": {
                        "dimension": dim,
                        "text_type": text_type,
                    },
                },
            )

            if resp.status_code == 200:
                data = resp.json()
                embeddings = data.get("output", {}).get("embeddings", [])
                usage = data.get("usage", {})
                vectors = [e.get("embedding", []) for e in embeddings]
                logger.debug(
                    "DashScope embed: %d texts, %d tokens, %d-dim",
                    len(texts),
                    usage.get("total_tokens", 0),
                    len(vectors[0]) if vectors else 0,
                )
                return vectors
            else:
                logger.warning(
                    "DashScope embed failed: HTTP %d — %s",
                    resp.status_code,
                    resp.text[:200],
                )
                return []

    except Exception as e:
        logger.warning("DashScope embed exception: %s", e)
        return []


async def embed_ollama(
    texts: list[str],
    *,
    model: str | None = None,
    base_url: str | None = None,
) -> list[list[float]]:
    """Generate embeddings via Ollama (bge-m3 or similar)."""
    mdl = model or OLLAMA_EMBED_MODEL
    url = base_url or OLLAMA_BASE_URL

    vectors: list[list[float]] = []
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            for text in texts:
                resp = await client.post(
                    f"{url}/api/embeddings",
                    json={"model": mdl, "input": text},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    emb = data.get("embedding", [])
                    vectors.append(emb)
                else:
                    logger.debug("Ollama embed failed: HTTP %d", resp.status_code)
                    vectors.append([])
    except Exception as e:
        logger.warning("Ollama embed exception: %s", e)
        # Return empty for all on total failure
        return [[] for _ in texts]

    return vectors


# ── Unified interface ──────────────────────────────────────────────


async def embed(
    text: str,
    *,
    dim: int = EMBEDDING_DIM,
    backend: str | None = None,
    text_type: str = "document",
) -> list[float]:
    """Generate embedding for a single text with auto-fallback.

    Backend chain: dashscope → ollama → hash
    """
    vecs = await embed_batch([text], dim=dim, backend=backend, text_type=text_type)
    return vecs[0] if vecs else []


async def embed_batch(
    texts: Sequence[str],
    *,
    dim: int = EMBEDDING_DIM,
    backend: str | None = None,
    text_type: str = "document",
) -> list[list[float]]:
    """Generate embeddings for multiple texts with auto-fallback.

    Args:
        texts: Texts to embed.
        dim: Output dimension.
        backend: "dashscope", "ollama", "hash", or None (auto).
        text_type: "query" or "document" (DashScope only).

    Returns:
        List of embedding vectors in same order as input.
    """
    if not texts:
        return []

    bkd = backend or EMBEDDING_BACKEND

    # Try DashScope first (if configured or available)
    if bkd in ("dashscope", "auto"):
        t0 = time.perf_counter()
        vecs = await embed_dashscope(list(texts), dim=dim, text_type=text_type)
        t1 = time.perf_counter()
        if vecs and all(len(v) > 0 for v in vecs):
            logger.info(
                "DashScope embed: %d texts in %.0fms",
                len(texts),
                (t1 - t0) * 1000,
            )
            return vecs
        logger.info("DashScope embed returned empty — falling back")

    # Try Ollama
    if bkd in ("dashscope", "ollama", "auto"):
        t0 = time.perf_counter()
        vecs = await embed_ollama(list(texts))
        t1 = time.perf_counter()
        if vecs and all(len(v) > 0 for v in vecs):
            logger.info(
                "Ollama embed: %d texts in %.0fms",
                len(texts),
                (t1 - t0) * 1000,
            )
            return vecs
        logger.info("Ollama embed returned empty — falling back")

    # Hash fallback (always works, NOT semantic)
    if bkd in ("dashscope", "ollama", "hash", "auto"):
        logger.warning("Using hash-based fallback (non-semantic) for %d texts", len(texts))
        return [embed_hash(t, dim=dim) for t in texts]

    logger.error("No embedding backend available for %d texts", len(texts))
    return [[] for _ in texts]


__all__ = [
    "embed",
    "embed_batch",
    "embed_hash",
    "embed_dashscope",
    "embed_ollama",
    "EMBEDDING_DIM",
    "EMBEDDING_BACKEND",
]
