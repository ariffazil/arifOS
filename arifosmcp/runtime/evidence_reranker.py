# arifOS SENSE Pipeline — Evidence Reranker
# Two-stage reranking: keyword scoring (Stage 1) + Ollama LLM reorder (Stage 2)
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import logging
import os
from dataclasses import dataclass

import httpx

from .result_normalizer import NormalizedResult

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_RERANK_MODEL", "qwen2.5:7b")

QUERY_KEYWORDS_WEIGHT = 0.4
TITLE_KEYWORDS_WEIGHT = 0.35
SNIPPET_KEYWORDS_WEIGHT = 0.25

RERANK_TOP_K = 5


@dataclass
class RerankResult:
    reranked: list[NormalizedResult]
    stage1_scores: dict[str, float]
    stage2_applied: bool = False


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
    }
    keywords = {w.strip(".,!?;:()[]{}") for w in words if len(w) > 2 and w not in stopwords}
    return keywords


def _compute_keyword_score(result: NormalizedResult, keywords: set[str]) -> float:
    if not keywords:
        return 0.5
    title_lower = result.title.lower()
    snippet_lower = result.snippet.lower()
    url_lower = result.domain.lower()

    title_matches = sum(1 for kw in keywords if kw in title_lower)
    snippet_matches = sum(1 for kw in keywords if kw in snippet_lower)
    url_matches = sum(1 for kw in keywords if kw in url_lower)

    title_max = len(keywords)
    query_score = title_matches / title_max if title_max > 0 else 0.0
    title_score = title_matches / title_max if title_max > 0 else 0.0
    snippet_score = snippet_matches / title_max if title_max > 0 else 0.0
    url_score = url_matches / title_max if title_max > 0 else 0.0

    return (
        query_score * QUERY_KEYWORDS_WEIGHT
        + title_score * TITLE_KEYWORDS_WEIGHT
        + snippet_score * SNIPPET_KEYWORDS_WEIGHT
        + url_score * 0.0
    )


class EvidenceReranker:
    __slots__ = ("_stage1_only", "_ollama_url", "_model")

    def __init__(
        self,
        stage1_only: bool = False,
        ollama_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self._stage1_only = stage1_only
        self._ollama_url = ollama_url or OLLAMA_BASE_URL
        self._model = model or OLLAMA_MODEL

    def rerank(
        self,
        results: list[NormalizedResult],
        query: str,
        top_k: int = RERANK_TOP_K,
    ) -> RerankResult:
        keywords = _extract_keywords(query)
        stage1_scores: dict[str, float] = {}

        scored = []
        for r in results:
            kw_score = _compute_keyword_score(r, keywords)
            combined = r.final_score * 0.6 + kw_score * 0.4
            stage1_scores[r.url] = kw_score
            scored.append((combined, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        reranked = [r for _, r in scored[:top_k]]

        return RerankResult(
            reranked=reranked,
            stage1_scores=stage1_scores,
            stage2_applied=False,
        )

    async def rerank_stage2(
        self,
        results: list[NormalizedResult],
        query: str,
        top_k: int = RERANK_TOP_K,
    ) -> RerankResult:
        stage1 = self.rerank(results, query, top_k)
        if self._stage1_only:
            return stage1

        try:
            llm_reordered = await self._llm_reorder(stage1.reranked, query)
            return RerankResult(
                reranked=llm_reordered,
                stage1_scores=stage1.stage1_scores,
                stage2_applied=True,
            )
        except Exception as e:
            logger.warning(f"Stage 2 reranking failed, falling back to Stage 1: {e}")
            return stage1

    async def _llm_reorder(
        self,
        results: list[NormalizedResult],
        query: str,
    ) -> list[NormalizedResult]:
        prompt = self._build_rerank_prompt(results, query)
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(
                    f"{self._ollama_url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                if resp.status_code != 200:
                    return results
                text = resp.json().get("response", "")
                return self._parse_llm_order(text, results)
            except Exception:
                return results

    def _build_rerank_prompt(self, results: list[NormalizedResult], query: str) -> str:
        items = "\n".join(f"{i + 1}. {r.title} — {r.snippet[:200]}" for i, r in enumerate(results))
        return (
            f"Query: {query}\n\n"
            f"Results:\n{items}\n\n"
            f"Reorder these results by relevance to the query. "
            f"Return a JSON list of numbers in new order (most relevant first):"
        )

    def _parse_llm_order(
        self, text: str, results: list[NormalizedResult]
    ) -> list[NormalizedResult]:
        import re

        numbers = re.findall(r"\d+", text)
        if not numbers:
            return results
        try:
            order = [int(n) - 1 for n in numbers[: len(results)]]
            seen = set()
            unique_order = [n for n in order if n not in seen and 0 <= n < len(results)]
            if len(unique_order) < len(results):
                remaining = [i for i in range(len(results)) if i not in set(unique_order)]
                unique_order.extend(remaining)
            return [results[i] for i in unique_order]
        except (ValueError, IndexError):
            return results
