from __future__ import annotations

import asyncio
import logging
import os
import re
import time
from typing import Any
from urllib.parse import urlparse

import httpx

from .reality_models import (
    Actor,
    BundleInput,
    BundleStatus,
    ErrorCode,
    EvidenceBundle,
    FetchResult,
    SearchResult,
    StatusError,
)

# Vector auto-sync bridge (SEALTRIWITNESS Phase 2)
try:
    from ..intelligence.tools.vector_bridge import auto_sync_bundle

    VECTOR_SYNC_AVAILABLE = True
except ImportError:
    VECTOR_SYNC_AVAILABLE = False

    async def auto_sync_bundle(*args, **kwargs):
        """No-op when vector bridge not available."""
        pass


# ── Phase 4A: QueryPlanner ───────────────────────────────────────────────
QUERY_PLANNER_ENABLED = os.getenv("QUERY_PLANNER_ENABLED", "false").lower() in ("true", "1", "yes")

try:
    from .query_planner import QueryMode, QueryPlanner, get_planner  # noqa: F401

    QUERY_PLANNER_AVAILABLE = True
except ImportError:
    QUERY_PLANNER_AVAILABLE = False


logger = logging.getLogger(__name__)

# Constants from server.py / tools.py
BROWSERLESS_URL = os.getenv("BROWSERLESS_URL", "http://headless_browser:3000")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
JINA_API_KEY = os.getenv("JINA_API_KEY", "")
PPLX_API_KEY = os.getenv("PPLX_API_KEY", "")
EXA_API_KEY = os.getenv("EXA_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

try:
    from ddgs import DDGS  # noqa: F401

    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


def _resolve_mode(bundle_input: BundleInput) -> str:
    mode = bundle_input.mode
    if mode == "auto":
        return "fetch" if bundle_input.value.startswith(("http://", "https://")) else "search"
    return mode


def _make_bundle(actor: Actor, bundle_input: BundleInput, message: str) -> EvidenceBundle:
    return EvidenceBundle(
        status=BundleStatus(
            state="PARTIAL",
            stage="111_OBSERVE",
            verdict="SABAR",
            message=message,
        ),
        input=bundle_input,
        actor=actor,
    )


def _try_vector_sync(bundle: EvidenceBundle, auth_context: dict[str, Any]) -> None:
    if not (VECTOR_SYNC_AVAILABLE and bundle.status.state == "SUCCESS"):
        return
    try:
        asyncio.create_task(
            auto_sync_bundle(
                bundle=bundle,
                session_id=auth_context.get("session_id", "global"),
                actor_id=auth_context.get("actor_id", "anonymous"),
            )
        )
    except Exception as sync_e:
        logger.warning("Vector auto-sync failed (non-blocking): %s", sync_e)


class RealityHandler:
    def __init__(self):
        pass

    def _map_exception(self, e: Exception) -> ErrorCode:
        err_str = str(e).lower()
        if (
            isinstance(e, httpx.ConnectError)
            or "dns" in err_str
            or "name or service not known" in err_str
        ):
            return "DNS_FAIL"
        if isinstance(e, httpx.TimeoutException) or "timed out" in err_str:
            return "TIMEOUT"
        if "ssl" in err_str or "certificate" in err_str:
            return "TLS_FAIL"
        if isinstance(e, httpx.HTTPStatusError):
            code = e.response.status_code
            if code == 403 or code == 429:
                return "WAF_BLOCK"
            if 400 <= code < 500:
                return "HTTP_4XX"
            return "HTTP_5XX"
        return "PARSE_FAIL"

    def _map_http_error(self, status_code: int) -> ErrorCode:
        if status_code == 403 or status_code == 429:
            return "WAF_BLOCK"
        if 400 <= status_code < 500:
            return "HTTP_4XX"
        return "HTTP_5XX"

    def _is_safe_url(self, url: str) -> bool:
        """Simple check to prevent SSRF (local/private IPs)."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False

            host = parsed.hostname
            if not host:
                return False

            # Block localhost and common private ranges
            # This is a basic heuristic for defense-in-depth
            if re.match(
                r"^(127\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\.|169\.254\.)",
                host,
            ):
                return False
            if host in ("localhost", "local", "loopback"):
                return False

            return True
        except Exception:
            return False

    async def fetch_url(self, url: str, render: str = "auto", policy: Any = None) -> FetchResult:
        timings = {"dns": 0.0, "connect": 0.0, "ttfb": 0.0, "total": 0.0}

        res = FetchResult(url=url)

        # SSRF Protection
        if not self._is_safe_url(url):
            res.error_message = "URL blocked by security policy (SSRF guard)"
            res.status_code = 403
            return res

        use_render = render == "always"
        max_size = 10 * 1024 * 1024  # 10MB limit

        try:
            if render != "always":
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    h_start = time.time()
                    try:
                        # Use stream to enforce MAX_CONTENT_LENGTH before reading everything
                        async with client.stream(
                            "GET",
                            url,
                            headers={
                                "User-Agent": "Mozilla/5.0 arifOS/2026.03.13 (RealityCompass/v2-hardened)",  # noqa: E501
                                "Accept": (
                                    "text/html,application/xhtml+xml,"
                                    "application/xml;q=0.9,*/*;q=0.8"
                                ),
                                "Cache-Control": "no-cache",
                            },
                        ) as response:
                            timings["total"] = (time.time() - h_start) * 1000

                            res.status_code = response.status_code
                            res.content_type = response.headers.get("content-type")
                            res.headers_subset = {
                                k: v
                                for k, v in response.headers.items()
                                if k.lower()
                                in [
                                    "server",
                                    "cache-control",
                                    "x-cache",
                                    "cf-ray",
                                    "content-encoding",
                                ]
                            }
                            res.final_url = str(response.url)
                            res.redirects = len(response.history)

                            if response.status_code >= 400:
                                if response.status_code in [403, 429] and render == "auto":
                                    use_render = True
                                    res.error_message = (
                                        f"HTTP {response.status_code} -> triggering render fallback"
                                    )
                                else:
                                    # Still want to read some error body
                                    chunks = []
                                    count = 0
                                    async for chunk in response.aiter_text():
                                        chunks.append(chunk)
                                        count += len(chunk)
                                        if count > 200:
                                            break
                                    res.error_message = (
                                        f"HTTP {response.status_code}: {''.join(chunks)[:200]}"
                                    )
                                    res.status_code = response.status_code
                            else:
                                # Check content-length header if present
                                cl = response.headers.get("content-length")
                                if cl and int(cl) > max_size:
                                    res.error_message = f"Content length {cl} exceeds limit"
                                    res.status_code = 413
                                    return res

                                chunks = []
                                bytes_read = 0
                                async for chunk in response.aiter_text():
                                    chunks.append(chunk)
                                    bytes_read += len(chunk)
                                    if bytes_read > max_size:
                                        res.error_message = (
                                            f"Response body exceeds {max_size} bytes"
                                        )
                                        res.status_code = 413
                                        return res

                                full_text = "".join(chunks)
                                res.raw_content = full_text
                                res.content_length = len(full_text)
                    except Exception as inner_e:
                        res.exception_class = inner_e.__class__.__name__
                        res.error_message = str(inner_e)
                        if render == "auto":
                            use_render = True

            if use_render:
                # SSRF check already passed for 'url'
                r_start = time.time()
                async with httpx.AsyncClient(timeout=30.0) as b_client:
                    try:
                        token = os.getenv("BROWSERLESS_TOKEN", "").strip()
                        endpoint = (
                            f"{BROWSERLESS_URL}/content?token={token}"
                            if token
                            else f"{BROWSERLESS_URL}/content"
                        )
                        b_res = await b_client.post(
                            endpoint,
                            json={"url": url},
                            headers={"Content-Type": "application/json"},
                        )
                        if b_res.status_code == 200:
                            if len(b_res.text) > max_size:
                                res.error_message = "Rendered content exceeds limit"
                                res.status_code = 413
                            else:
                                res.raw_content = b_res.text
                                res.content_length = len(b_res.text)
                                res.render_fallback_used = True
                                res.status_code = 200
                                res.error_message = None
                            timings["total"] = (time.time() - r_start) * 1000
                        else:
                            res.error_message = (
                                f"Browserless Fail {b_res.status_code}: {b_res.text[:200]}"
                            )
                            res.status_code = b_res.status_code
                    except Exception as b_e:
                        res.error_message = f"Browserless Exception: {str(b_e)}"
                        res.exception_class = b_e.__class__.__name__

        except Exception as e:
            res.exception_class = e.__class__.__name__
            res.error_message = str(e)
            res.status_code = res.status_code or 0

        res.latency_ms = timings
        return res

    async def search_exa(self, query: str, top_k: int = 5) -> SearchResult:
        """Search via Exa.ai."""
        start_time = time.time()
        res = SearchResult(engine="exa", query=query)
        if not EXA_API_KEY:
            res.error = "EXA_API_KEY missing"
            return res
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.exa.ai/search",
                    json={"query": query, "numResults": top_k, "useAutoprompt": True},
                    headers={"x-api-key": EXA_API_KEY, "Content-Type": "application/json"},
                )
                res.status_code = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    res.results = [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "description": r.get("text", "") or r.get("highlights", [""])[0],
                            "score": r.get("score", 0.0),
                        }
                        for r in data.get("results", [])
                    ]
                else:
                    res.error = f"Exa Error {response.status_code}: {response.text[:200]}"
        except Exception as e:
            res.error = f"Exa Exception: {str(e)}"
        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def search_tavily(self, query: str, top_k: int = 5) -> SearchResult:
        """Search via Tavily."""
        start_time = time.time()
        res = SearchResult(engine="tavily", query=query)
        if not TAVILY_API_KEY:
            res.error = "TAVILY_API_KEY missing"
            return res
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={"query": query, "max_results": top_k, "api_key": TAVILY_API_KEY},
                )
                res.status_code = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    res.results = [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "description": r.get("content", ""),
                            "score": r.get("score", 0.0),
                        }
                        for r in data.get("results", [])
                    ]
                else:
                    res.error = f"Tavily Error {response.status_code}: {response.text[:200]}"
        except Exception as e:
            res.error = f"Tavily Exception: {str(e)}"
        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def search_brave(
        self, query: str, top_k: int = 5, region: str = "MY", locale: str = "en-MY"
    ) -> SearchResult:
        start_time = time.time()
        res = SearchResult(engine="brave", query=query)

        # ── Fallback Chain Orchestration ──────────────────────────────────────
        async def _try_fallbacks():
            # 1. Tavily (High quality)
            if TAVILY_API_KEY:
                t_res = await self.search_tavily(query, top_k)
                if t_res.results: return t_res
            # 2. Exa (Neural search)
            if EXA_API_KEY:
                e_res = await self.search_exa(query, top_k)
                if e_res.results: return e_res
            # 3. DDGS (Privacy-first)
            if DDGS_AVAILABLE:
                d_res = await self.search_ddgs(query, top_k)
                if d_res.results: return d_res
            # 4. Meyhem (Meta-search)
            return await self.search_meyhem(query, top_k)

        if not BRAVE_API_KEY:
            logger.info("Brave key missing, entering fallback chain")
            return await _try_fallbacks()

        # Brave V1 implementation...
        search_lang = locale.split("-")[0] if "-" in locale else "en"
        params = {
            "q": query,
            "count": min(max(1, top_k), 20),
            "search_lang": search_lang,
            "ui_lang": locale,
            "country": region,
            "text_decorations": 0,
            "spellcheck": 1,
        }
        res.request_params = params

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params=params,
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": BRAVE_API_KEY,
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip",
                    },
                )
                res.status_code = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    web_results = data.get("web", {}) or {}
                    res.results = web_results.get("results", []) if web_results else []
                    if not res.results:
                        if DDGS_AVAILABLE:
                            logger.info("Brave returned no results, trying DDGS fallback")
                            ddgs_result = await self.search_ddgs(query, top_k)
                            if ddgs_result.results:
                                return ddgs_result
                            # DDGS also empty → final fallback: Meyhem
                            logger.info("DDGS also empty, trying Meyhem final fallback")
                            return await self.search_meyhem(query, top_k)
                        # No DDGS → try Meyhem directly
                        return await self.search_meyhem(query, top_k)
                elif DDGS_AVAILABLE:
                    logger.warning(f"Brave error {response.status_code}, trying DDGS fallback")
                    ddgs_result = await self.search_ddgs(query, top_k)
                    if ddgs_result.results:
                        return ddgs_result
                    logger.info("DDGS also failed, trying Meyhem final fallback")
                    return await self.search_meyhem(query, top_k)
                else:
                    res.error = f"Brave API Error {response.status_code}: {response.text[:500]}"
        except Exception as e:
            if DDGS_AVAILABLE:
                logger.warning(f"Brave exception ({type(e).__name__}), trying DDGS fallback")
                ddgs_result = await self.search_ddgs(query, top_k)
                if ddgs_result.results:
                    return ddgs_result
                logger.info("DDGS fallback also failed, trying Meyhem final fallback")
                return await self.search_meyhem(query, top_k)
            logger.warning(f"Brave exception ({type(e).__name__}), trying Meyhem directly")
            return await self.search_meyhem(query, top_k)

        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def search_ddgs(self, query: str, top_k: int = 5) -> SearchResult:
        """Search DuckDuckGo."""
        start_time = time.time()
        res = SearchResult(engine="ddgs", query=query)
        if not DDGS_AVAILABLE:
            res.error = "ddgs library not installed"
            return res

        try:
            from ddgs import DDGS  # noqa: F401

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=top_k))
                res.results = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "description": r.get("body", ""),
                    }
                    for r in results
                ]
                res.status_code = 200
        except Exception as e:
            res.error = f"DDGS error: {str(e)}"
            res.status_code = 500

        res.latency_ms = (time.time() - start_time) * 1000
        return res

    async def search_meyhem(
        self, query: str, top_k: int = 5, agent_id: str = "arifOS-sensor"
    ) -> SearchResult:
        """
        Search via Meyhem (api.rhdxm.com) — outcome-ranked web search.

        Meyhem blends Exa + Tavily in parallel, deduplicates, score-normalizes,
        and LLM-re-ranks results. Zero API key required.

        API: POST https://api.rhdxm.com/search
        Body:  {"query": "...", "max_results": N, "agent_id": "...", "freshness": "hour"}
        Docs:  https://api.rhdxm.com/docs
        """
        start_time = time.time()
        res = SearchResult(engine="meyhem", query=query)

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "https://api.rhdxm.com/search",
                    json={
                        "query": query,
                        "max_results": min(max(1, top_k), 10),
                        "agent_id": agent_id,
                        "freshness": "hour",
                    },
                    headers={"Content-Type": "application/json"},
                )
                res.status_code = response.status_code
                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get("results", []) if isinstance(data, dict) else []
                    if not raw_results:
                        res.error = (
                            "Meyhem returned 0 results (service may be rate-limiting or degraded)"
                        )
                        res.status_code = 200
                    else:
                        res.results = [
                            {
                                "title": r.get("title") or r.get("url", ""),
                                "url": r.get("url", ""),
                                "description": r.get("description", "") or r.get("snippet", ""),
                                "score": r.get("score", 0.0),
                                "source_domain": r.get("source_domain", ""),
                                "provider": r.get("provider", "meyhem"),
                                "position": r.get("position", i),
                            }
                            for i, r in enumerate(raw_results)
                        ]
                else:
                    res.error = f"Meyhem HTTP {response.status_code}: {response.text[:300]}"
        except Exception as e:
            res.error = f"Meyhem exception ({type(e).__name__}): {str(e)}"
            res.status_code = 0

        res.latency_ms = (time.time() - start_time) * 1000
        return res

    # ── Phase 4A: QueryPlanner-backed handler ──────────────────────────────
    async def handle_compass_qp(
        self, bundle_input: BundleInput, auth_context: dict[str, Any]
    ) -> EvidenceBundle:
        """
        QueryPlanner-backed reality acquisition.
        Routes queries to the best available provider based on query classification,
        normalizes results, and returns an EvidenceBundle.

        This method is only called when QUERY_PLANNER_ENABLED=true.
        """
        # Imports here to avoid circular deps at module level
        from .query_planner import get_planner

        planner = get_planner()
        if planner is None:
            # Fall back to legacy path
            return await self.handle_compass_legacy(bundle_input, auth_context)

        actor = Actor(
            actor_id=auth_context.get("actor_id", "anonymous"),
            authority_level=auth_context.get("authority_level", "anonymous"),
            token_fingerprint=auth_context.get("token_fingerprint"),
        )
        bundle = _make_bundle(actor, bundle_input, "QueryPlanner acquisition initiated.")
        mode = _resolve_mode(bundle_input)

        try:
            if mode == "fetch":
                # Single URL fetch — use existing fetch_url
                f_res = await self.fetch_url(bundle_input.value, render=bundle_input.render)
                bundle.results.append(f_res)
                if f_res.status_code == 200 and f_res.content_length > 0:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = "Successfully fetched evidence via QueryPlanner."
                else:
                    bundle.status.state = "SABAR"
                    bundle.status.errors.append(
                        StatusError(
                            code=self._map_exception(Exception(f_res.error_message or "")),
                            detail=f_res.error_message or "Empty content",
                        )
                    )

            elif mode == "search":
                # Multi-provider search via QueryPlanner
                qp_result = await planner.plan_and_execute(
                    query=bundle_input.value,
                    mode=None,  # Auto-detect
                    top_k=bundle_input.top_k,
                )

                # Convert QueryPlanResult → FetchResult for bundle compatibility
                if qp_result.is_success:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = (
                        f"QueryPlanner found {len(qp_result.results)} results "
                        f"in {qp_result.latency_ms:.0f}ms using {qp_result.provider_used}."
                    )

                    # Build synthetic SearchResult for bundle.results
                    search_result = self._qp_results_to_search_result(qp_result)
                    bundle.results.append(search_result)

                    # Optional: fetch top results
                    if bundle_input.fetch_top_k > 0:
                        top_urls = [r.url for r in qp_result.results[: bundle_input.fetch_top_k]]
                        fetch_tasks = [
                            self.fetch_url(url, render=bundle_input.render) for url in top_urls
                        ]
                        f_results = await asyncio.gather(*fetch_tasks)
                        bundle.results.extend(f_results)
                else:
                    bundle.status.state = "SABAR"
                    bundle.status.errors.append(
                        StatusError(
                            code="NO_RESULTS",
                            detail=qp_result.error or "QueryPlanner search failed.",
                            hint=f"Provider={qp_result.provider_used}, latency={qp_result.latency_ms:.0f}ms",  # noqa: E501
                        )
                    )
            else:
                bundle.status.state = "SABAR"
                bundle.status.errors.append(
                    StatusError(code="ENGINE_422", detail=f"Unknown mode: {mode}")
                )
        except Exception as e:
            bundle.status.state = "ERROR"
            bundle.status.message = f"QueryPlanner handler failure: {str(e)}"
            bundle.status.errors.append(StatusError(code="SCHEMA_FAIL", detail=str(e)))

        _try_vector_sync(bundle, auth_context)
        return bundle

    def _qp_results_to_search_result(self, qp_result) -> SearchResult:
        """Convert QueryPlanResult to SearchResult for bundle compatibility."""
        from .reality_models import SearchResult

        sr = SearchResult(
            engine=qp_result.provider_used,
            query=qp_result.plan.query,
        )
        sr.status_code = qp_result.status_code
        sr.latency_ms = qp_result.latency_ms
        sr.error = qp_result.error
        sr.results = [
            {
                "title": r.title,
                "url": r.url,
                "description": r.description,
                "final_score": r.final_score,
                "evidence_level": r.evidence_level.value,
                "relevance_score": r.relevance_score,
                "authority_score": r.authority_score,
                "freshness_score": r.freshness_score,
                "provider_trust": r.provider_trust,
                "content_depth_score": r.content_depth_score,
                "age_days": r.age_days,
            }
            for r in qp_result.results
        ]
        return sr

    async def handle_compass_legacy(
        self, bundle_input: BundleInput, auth_context: dict[str, Any]
    ) -> EvidenceBundle:
        """Canonical handle_compass implementation — used directly and as QP fallback."""
        actor = Actor(
            actor_id=auth_context.get("actor_id", "anonymous"),
            authority_level=auth_context.get("authority_level", "anonymous"),
            token_fingerprint=auth_context.get("token_fingerprint"),
        )
        bundle = _make_bundle(actor, bundle_input, "Reality acquisition initiated.")
        mode = _resolve_mode(bundle_input)

        try:
            if mode == "fetch":
                f_res = await self.fetch_url(bundle_input.value, render=bundle_input.render)
                bundle.results.append(f_res)
                if f_res.status_code == 200 and f_res.content_length > 0:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = "Successfully fetched evidence."
                else:
                    bundle.status.state = "SABAR"
                    err_code = (
                        self._map_exception(Exception(f_res.error_message))
                        if f_res.error_message
                        else "NO_RESULTS"
                    )
                    bundle.status.errors.append(
                        StatusError(
                            code=err_code,
                            detail=f_res.error_message or "Empty content",
                            hint="Try render='always' if site is dynamic.",
                        )
                    )
            elif mode == "search":
                s_res = await self.search_brave(bundle_input.value, top_k=bundle_input.top_k)
                bundle.results.append(s_res)
                if s_res.status_code == 200 and s_res.results:
                    bundle.status.state = "SUCCESS"
                    bundle.status.verdict = "SEAL"
                    bundle.status.message = f"Found {len(s_res.results)} search candidates."
                    if bundle_input.fetch_top_k > 0:
                        bundle.status.message += (
                            f" Initiating fetch for top {bundle_input.fetch_top_k}."
                        )
                        fetch_tasks = [
                            self.fetch_url(r["url"], render=bundle_input.render)
                            for r in s_res.results[: bundle_input.fetch_top_k]
                        ]
                        bundle.results.extend(await asyncio.gather(*fetch_tasks))
                else:
                    bundle.status.state = "SABAR"
                    err_code = (
                        "ENGINE_422"
                        if s_res.status_code == 422
                        else ("NO_RESULTS" if s_res.status_code == 200 else "HTTP_5XX")
                    )
                    bundle.status.errors.append(
                        StatusError(
                            code=err_code,
                            detail=s_res.error or "No results found.",
                            hint="Check query syntax or API status.",
                        )
                    )
            else:
                bundle.status.state = "SABAR"
                bundle.status.errors.append(
                    StatusError(code="ENGINE_422", detail=f"Unknown mode: {mode}")
                )
        except Exception as e:
            bundle.status.state = "ERROR"
            bundle.status.message = f"Handler failure: {str(e)}"
            bundle.status.errors.append(StatusError(code="SCHEMA_FAIL", detail=str(e)))

        _try_vector_sync(bundle, auth_context)
        return bundle

    async def handle_compass(
        self, bundle_input: BundleInput, auth_context: dict[str, Any]
    ) -> EvidenceBundle:
        if QUERY_PLANNER_ENABLED and QUERY_PLANNER_AVAILABLE:
            return await self.handle_compass_qp(bundle_input, auth_context)
        return await self.handle_compass_legacy(bundle_input, auth_context)


handler = RealityHandler()
