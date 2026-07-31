# arifOS SENSE Pipeline — Evidence Reranker v3
# Three-stage with configurable backends:
#   Stage 1 — Keyword boost (always, fast, local)
#   Stage 2 — Cross-encoder rerank via qwen3-rerank (DashScope) OR pointwise LLM (Ollama)
# Backend chain: dashscope → ollama → keyword (graceful degradation)
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field

import httpx

from .result_normalizer import NormalizedResult

logger = logging.getLogger(__name__)

# ── Backend configuration ──────────────────────────────────────────
# RERANK_BACKEND: "dashscope" (qwen3-rerank cross-encoder, recommended),
#                 "ollama" (pointwise LLM, legacy), "keyword" (stage1 only)
RERANK_BACKEND = os.getenv("RERANK_BACKEND", "ollama")

# DashScope / Bailian (qwen3-rerank)
# Uses the DashScope NATIVE API — the Cohere-compatible /reranks endpoint
# is only available on workspace-specific MaaS URLs, not dashscope-intl.
# Native path: /api/v1/services/rerank/text-rerank/text-rerank
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope-intl.aliyuncs.com/api/v1",
)
DASHSCOPE_RERANK_MODEL = os.getenv("DASHSCOPE_RERANK_MODEL", "qwen3-rerank")
DASHSCOPE_RERANK_PATH = "/services/rerank/text-rerank/text-rerank"

# Ollama (legacy pointwise LLM)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
RERANK_MODEL = os.getenv("RERANK_MODEL", "qwen2.5:7b")

# Shared
RERANK_TOP_K_DEFAULT = int(os.getenv("RERANK_TOP_K", "10"))
RERANK_CANDIDATE_POOL = int(os.getenv("RERANK_CANDIDATE_POOL", "50"))

# Stage 1 keyword weights
QUERY_KEYWORDS_WEIGHT = 0.4
TITLE_KEYWORDS_WEIGHT = 0.35
SNIPPET_KEYWORDS_WEIGHT = 0.25


@dataclass
class RerankResult:
    reranked: list[NormalizedResult]
    stage1_scores: dict[str, float]
    stage2_applied: bool = False
    stage2_backend: str = ""
    rerank_model: str = "keyword"
    stage2_latency_ms: float = 0.0


def _extract_keywords(query: str) -> set[str]:
    words = query.lower().split()
    stopwords = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "this",
        "that",
        "these",
        "those",
        "it",
        "its",
        "what",
        "which",
        "who",
        "whom",
        "how",
        "why",
        "not",
        "no",
        "nor",
        "so",
        "if",
        "as",
    }
    return {w.strip(".,!?;:()[]{}'\"") for w in words if len(w) > 2 and w not in stopwords}


def _compute_keyword_score(result: NormalizedResult, keywords: set[str]) -> float:
    if not keywords:
        return 0.5
    title_lower = result.title.lower()
    snippet_lower = result.snippet.lower()
    title_max = len(keywords)
    title_matches = sum(1 for kw in keywords if kw in title_lower)
    snippet_matches = sum(1 for kw in keywords if kw in snippet_lower)
    qscore = title_matches / title_max if title_max > 0 else 0.0
    return (
        qscore * QUERY_KEYWORDS_WEIGHT
        + qscore * TITLE_KEYWORDS_WEIGHT
        + (snippet_matches / title_max if title_max > 0 else 0.0) * SNIPPET_KEYWORDS_WEIGHT
    )


def _build_documents(candidates: list[NormalizedResult]) -> list[str]:
    """Build document strings for reranker from NormalizedResult objects."""
    docs = []
    for r in candidates:
        doc = (r.title + " " + r.snippet[:500]).strip()
        if not doc:
            doc = r.domain or r.url or ""
        docs.append(doc)
    return docs


async def _rerank_dashscope(
    query: str,
    candidates: list[NormalizedResult],
    top_k: int,
    api_key: str,
    base_url: str,
    model: str,
) -> tuple[list[float], str, float]:
    """Call qwen3-rerank via DashScope native API.

    Uses the DashScope native endpoint (not Cohere-compatible, which is
    workspace-MaaS-only). Format:
      POST {base_url}/services/rerank/text-rerank/text-rerank
      {"model":"qwen3-rerank","input":{"query":"...","documents":[...]},"parameters":{"top_n":N}}

    Returns: (scores_per_candidate, backend_label, latency_ms)
    """
    documents = _build_documents(candidates)
    if not documents:
        return [], "dashscope-empty", 0.0

    if not api_key:
        return [], "dashscope-no-key", 0.0

    t0 = time.perf_counter()
    backend_label = f"dashscope/{model}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{base_url}{DASHSCOPE_RERANK_PATH}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "input": {
                        "query": query,
                        "documents": documents,
                    },
                    "parameters": {
                        "top_n": top_k,
                    },
                },
            )

            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000

            if resp.status_code == 200:
                data = resp.json()
                # DashScope native response: {"output":{"results":[...]}}
                results = data.get("output", {}).get("results", [])
                score_map: dict[int, float] = {}
                for item in results:
                    idx = item.get("index", -1)
                    score = item.get("relevance_score", 0.5)
                    if 0 <= idx < len(candidates):
                        score_map[idx] = score

                scores = [score_map.get(i, 0.5) for i in range(len(candidates))]
                logger.info(
                    "DashScope rerank: %d candidates → %d results in %.0fms",
                    len(candidates),
                    len(results),
                    latency_ms,
                )
                return scores, backend_label, latency_ms
            else:
                logger.warning(
                    "DashScope rerank failed: HTTP %d — %s",
                    resp.status_code,
                    resp.text[:200],
                )
                return [], f"dashscope-error-{resp.status_code}", latency_ms

    except Exception as e:
        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000
        logger.warning("DashScope rerank exception: %s", e)
        return [], f"dashscope-exception", latency_ms


async def _rerank_ollama_pointwise(
    candidates: list[NormalizedResult],
    query: str,
    ollama_url: str,
    model: str,
) -> tuple[list[float], str, float]:
    """Legacy pointwise LLM scoring via Ollama (one prompt per document)."""
    t0 = time.perf_counter()
    scores: list[float] = []
    batch_size = 5

    for i in range(0, len(candidates), batch_size):
        batch = candidates[i : i + batch_size]
        async with httpx.AsyncClient(timeout=90.0) as client:
            for r in batch:
                doc = (r.title + " " + r.snippet[:300]).strip() or r.domain
                prompt = (
                    f"Query: {query}\n"
                    f"Document: {doc}\n"
                    f"Score relevance [0.0-1.0] (return ONLY the number):"
                )
                try:
                    resp = await client.post(
                        f"{ollama_url}/api/generate",
                        json={
                            "model": model,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"num_ctx": 4096, "temperature": 0.0},
                        },
                    )
                    if resp.status_code == 200:
                        text = resp.json().get("response", "").strip()
                        nums = re.findall(r"[-+]?[0-9]*\.?[0-9]+", text)
                        score = 0.5
                        for n in nums:
                            val = float(n)
                            if 0.0 <= val <= 1.0:
                                score = val
                                break
                            if 1.0 <= val <= 100.0:
                                score = val / 100.0
                                break
                        scores.append(score)
                    else:
                        scores.append(0.5)
                except Exception as e:
                    logger.debug("Ollama pointwise error: %s", e)
                    scores.append(0.5)

    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000
    return scores, f"ollama/{model}", latency_ms


class EvidenceReranker:
    """Multi-backend reranker with graceful degradation.

    Backend chain (auto-fallback):
      1. dashscope (qwen3-rerank cross-encoder) — fastest + most accurate
      2. ollama (pointwise LLM) — local, slower, less accurate
      3. keyword-only (stage 1) — always available, zero cost

    Configure via RERANK_BACKEND env var or constructor.
    """

    __slots__ = (
        "_backend",
        "_ollama_url",
        "_ollama_model",
        "_dashscope_api_key",
        "_dashscope_base_url",
        "_dashscope_model",
        "_stage1_only",  # backward-compat v2
    )

    def __init__(
        self,
        backend: str | None = None,
        ollama_url: str | None = None,
        ollama_model: str | None = None,
        dashscope_api_key: str | None = None,
        dashscope_base_url: str | None = None,
        dashscope_model: str | None = None,
        # ── backward-compat: old v2 API ──
        stage1_only: bool = False,
        model: str | None = None,
    ) -> None:
        # Backward-compat: old v2 constructor
        if stage1_only:
            backend = "keyword"
        if model and not ollama_model:
            ollama_model = model

        self._backend = backend or RERANK_BACKEND
        self._ollama_url = ollama_url or OLLAMA_BASE_URL
        self._ollama_model = ollama_model or RERANK_MODEL
        self._dashscope_api_key = dashscope_api_key or DASHSCOPE_API_KEY
        self._dashscope_base_url = dashscope_base_url or DASHSCOPE_BASE_URL
        self._dashscope_model = dashscope_model or DASHSCOPE_RERANK_MODEL
        # Backward-compat alias (v2 tests access this directly)
        self._stage1_only = self._backend == "keyword"

    def rerank(
        self,
        results: list[NormalizedResult],
        query: str,
        top_k: int = RERANK_TOP_K_DEFAULT,
    ) -> RerankResult:
        """Stage 1 only: keyword lexical boost (no remote call)."""
        keywords = _extract_keywords(query)
        stage1_scores: dict[str, float] = {}
        scored = []
        for r in results:
            kw_score = _compute_keyword_score(r, keywords)
            combined = r.final_score * 0.6 + kw_score * 0.4
            stage1_scores[r.url] = kw_score
            scored.append((combined, r))
        scored.sort(key=lambda x: x[0], reverse=True)
        return RerankResult(
            reranked=[r for _, r in scored[:top_k]],
            stage1_scores=stage1_scores,
            rerank_model="keyword",
        )

    async def rerank_stage2(
        self,
        results: list[NormalizedResult],
        query: str,
        top_k: int = RERANK_TOP_K_DEFAULT,
    ) -> RerankResult:
        """Stage 1 → Stage 2 with automatic backend fallback.

        Backend chain: dashscope → ollama → keyword.
        """
        # Stage 1: always run keyword boost first
        pool_size = min(top_k, RERANK_CANDIDATE_POOL)
        stage1 = self.rerank(results, query, max(pool_size, RERANK_CANDIDATE_POOL))
        if not stage1.reranked:
            return stage1

        # Stage 2: try configured backends in fallback order
        backends_to_try = self._resolve_backend_chain()

        for backend in backends_to_try:
            if backend == "dashscope" and self._dashscope_api_key:
                scores, label, latency = await _rerank_dashscope(
                    query=query,
                    candidates=stage1.reranked[:RERANK_CANDIDATE_POOL],
                    top_k=top_k,
                    api_key=self._dashscope_api_key,
                    base_url=self._dashscope_base_url,
                    model=self._dashscope_model,
                )
                if scores and len(scores) == len(stage1.reranked[:RERANK_CANDIDATE_POOL]):
                    paired = sorted(
                        zip(scores, stage1.reranked[:RERANK_CANDIDATE_POOL]),
                        key=lambda x: x[0],
                        reverse=True,
                    )
                    return RerankResult(
                        reranked=[r for _, r in paired[:top_k]],
                        stage1_scores=stage1.stage1_scores,
                        stage2_applied=True,
                        stage2_backend="dashscope",
                        rerank_model=self._dashscope_model,
                        stage2_latency_ms=latency,
                    )
                logger.info("DashScope rerank returned empty — falling back")

            elif backend == "ollama":
                scores, label, latency = await _rerank_ollama_pointwise(
                    candidates=stage1.reranked[:RERANK_CANDIDATE_POOL],
                    query=query,
                    ollama_url=self._ollama_url,
                    model=self._ollama_model,
                )
                if scores and len(scores) == len(stage1.reranked[:RERANK_CANDIDATE_POOL]):
                    paired = sorted(
                        zip(scores, stage1.reranked[:RERANK_CANDIDATE_POOL]),
                        key=lambda x: x[0],
                        reverse=True,
                    )
                    return RerankResult(
                        reranked=[r for _, r in paired[:top_k]],
                        stage1_scores=stage1.stage1_scores,
                        stage2_applied=True,
                        stage2_backend="ollama",
                        rerank_model=self._ollama_model,
                        stage2_latency_ms=latency,
                    )
                logger.info("Ollama rerank returned empty — falling back")

        # All backends failed → return stage1 as-is
        logger.warning("All Stage 2 backends failed — using keyword-only")
        return stage1

    def _resolve_backend_chain(self) -> list[str]:
        """Return ordered list of backends to try.

        If backend is explicitly "keyword", skip all remote backends.
        Otherwise: dashscope → ollama (fallback chain).
        """
        if self._backend == "keyword":
            return []
        if self._backend == "dashscope":
            return ["dashscope", "ollama"]
        if self._backend == "ollama":
            return ["ollama"]
        # Default: try dashscope first if key is available
        if self._dashscope_api_key:
            return ["dashscope", "ollama"]
        return ["ollama"]


__all__ = ["EvidenceReranker", "RerankResult"]
