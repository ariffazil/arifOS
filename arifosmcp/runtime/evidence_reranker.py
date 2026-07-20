# arifOS SENSE Pipeline — Evidence Reranker v2
# Two-stage: keyword boost (Stage 1) → pointwise LLM rerank (Stage 2) via qwen2.5:7b
# Cross-encoder slot reserved: set RERANK_MODEL env for bge-reranker when pulled
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass

import httpx

from .result_normalizer import NormalizedResult

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
RERANK_MODEL = os.getenv("RERANK_MODEL", "qwen2.5:7b")
RERANK_TOP_K_DEFAULT = int(os.getenv("RERANK_TOP_K", "10"))
RERANK_CANDIDATE_POOL = int(os.getenv("RERANK_CANDIDATE_POOL", "50"))

QUERY_KEYWORDS_WEIGHT = 0.4
TITLE_KEYWORDS_WEIGHT = 0.35
SNIPPET_KEYWORDS_WEIGHT = 0.25


@dataclass
class RerankResult:
    reranked: list[NormalizedResult]
    stage1_scores: dict[str, float]
    stage2_applied: bool = False
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


class EvidenceReranker:
    """Two-stage reranker with keyword boost + pointwise LLM scoring.

    Stage 1 — Keyword boost (always, fast).
    Stage 2 — Pointwise relevance score via LLM (qwen2.5:7b / bge-reranker).
    Falls back gracefully if Stage 2 unavailable.
    """

    __slots__ = ("_stage1_only", "_ollama_url", "_model")

    def __init__(
        self,
        stage1_only: bool = False,
        ollama_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._stage1_only = stage1_only
        self._ollama_url = ollama_url or OLLAMA_BASE_URL
        self._model = model or RERANK_MODEL

    def rerank(
        self,
        results: list[NormalizedResult],
        query: str,
        top_k: int = RERANK_TOP_K_DEFAULT,
    ) -> RerankResult:
        """Stage 1: keyword lexical boost (no LLM)."""
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
        """Stage 1 → Stage 2 pointwise LLM scoring on top candidates."""
        stage1 = self.rerank(results, query, min(top_k, RERANK_CANDIDATE_POOL))
        if self._stage1_only or not stage1.reranked:
            return stage1

        try:
            t0 = time.perf_counter()
            llm_scores = await self._pointwise_score(stage1.reranked, query)
            t1 = time.perf_counter()

            paired = sorted(zip(llm_scores, stage1.reranked), key=lambda x: x[0], reverse=True)
            return RerankResult(
                reranked=[r for _, r in paired[:top_k]],
                stage1_scores=stage1.stage1_scores,
                stage2_applied=True,
                rerank_model=self._model,
                stage2_latency_ms=(t1 - t0) * 1000,
            )
        except Exception as e:
            logger.warning("Stage 2 failed, using Stage 1: %s", e)
            return stage1

    async def _pointwise_score(self, candidates: list[NormalizedResult], query: str) -> list[float]:
        """Score each candidate [0-1] via structured LLM prompt."""
        scores: list[float] = []
        batch_size = 5

        for i in range(0, len(candidates), batch_size):
            batch = candidates[i : i + batch_size]
            prompts = []
            for r in batch:
                doc = (r.title + " " + r.snippet[:300]).strip() or r.domain
                prompts.append(
                    f"Query: {query}\nDocument: {doc}\nScore relevance [0.0-1.0] (return ONLY the number):"
                )

            async with httpx.AsyncClient(timeout=90.0) as client:
                for p in prompts:
                    try:
                        resp = await client.post(
                            f"{self._ollama_url}/api/generate",
                            json={
                                "model": self._model,
                                "prompt": p,
                                "stream": False,
                                "options": {"num_ctx": 4096, "temperature": 0.0},
                            },
                        )
                        if resp.status_code == 200:
                            text = resp.json().get("response", "").strip()
                            score = self._parse_score(text)
                            scores.append(score)
                        else:
                            scores.append(0.5)
                    except Exception as e:
                        logger.debug("Pointwise error: %s", e)
                        scores.append(0.5)

        return scores

    def _parse_score(self, text: str) -> float:
        """Extract a float score from model response."""
        nums = re.findall(r"[-+]?[0-9]*\.?[0-9]+", text)
        for n in nums:
            val = float(n)
            if 0.0 <= val <= 1.0:
                return val
            if 1.0 <= val <= 100.0:
                return val / 100.0
        return 0.5
