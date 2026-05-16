# arifOS SENSE Pipeline — Verify Expander
# URL verification + 3-method expansion (firecrawl/jina/direct)
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import asyncio
import logging
import os
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

MAX_CONTENT_BYTES = 500_000
MIN_CONTENT_BYTES = 100

VALID_URL_PATTERNS = [
    re.compile(r"^https?://"),
    re.compile(r"^www\."),
]

BLOCKED_SCHEMES = {"ftp://", "file://", "tel:", "mailto:", "javascript:"}


@dataclass
class VerifyResult:
    url: str
    is_safe: bool
    is_reachable: bool
    status_code: int | None
    content_type: str | None
    content_length: int | None
    final_url: str | None
    error: str | None


@dataclass
class ExpansionResult:
    original_url: str
    expanded_urls: list[str]
    verification: VerifyResult | None
    method: str  # "firecrawl" | "jina" | "direct" | "multi"
    titles: dict[str, str]


def _is_safe_url(url: str) -> bool:
    if not url or len(url) > MAX_CONTENT_BYTES:
        return False
    for scheme in BLOCKED_SCHEMES:
        if url.lower().startswith(scheme):
            return False
    return True


async def verify_url(url: str, timeout: float = 10.0) -> VerifyResult:
    if not _is_safe_url(url):
        return VerifyResult(
            url=url,
            is_safe=False,
            is_reachable=False,
            status_code=None,
            content_type=None,
            content_length=None,
            final_url=None,
            error="URL failed safety checks",
        )
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.head(url)
            return VerifyResult(
                url=url,
                is_safe=True,
                is_reachable=True,
                status_code=resp.status_code,
                content_type=resp.headers.get("content-type", ""),
                content_length=int(resp.headers.get("content-length", 0) or 0),
                final_url=str(resp.url),
                error=None,
            )
    except Exception as e:
        return VerifyResult(
            url=url,
            is_safe=True,
            is_reachable=False,
            status_code=None,
            content_type=None,
            content_length=None,
            final_url=None,
            error=str(e),
        )


async def expand_url(url: str, method: str = "direct") -> ExpansionResult:
    if method == "firecrawl":
        return await _expand_firecrawl(url)
    elif method == "jina":
        return await _expand_jina(url)
    else:
        return await _expand_direct(url)


async def _expand_direct(url: str) -> ExpansionResult:
    verify = await verify_url(url)
    return ExpansionResult(
        original_url=url,
        expanded_urls=[url] if verify.is_reachable else [],
        verification=verify,
        method="direct",
        titles={url: ""},
    )


async def _expand_firecrawl(url: str) -> ExpansionResult:
    api_key = os.getenv("FIRECRAWL_API_KEY", "")
    if not api_key:
        return await _expand_direct(url)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.firecrawl.dev/v0/expand",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"url": url},
            )
            if resp.status_code != 200:
                return await _expand_direct(url)
            data = resp.json()
            expanded = data.get("expanded_urls", [])
            titles = {e["url"]: e.get("title", "") for e in expanded}
            verify = await verify_url(url)
            return ExpansionResult(
                original_url=url,
                expanded_urls=expanded,
                verification=verify,
                method="firecrawl",
                titles=titles,
            )
    except Exception:
        return await _expand_direct(url)


async def _expand_jina(url: str) -> ExpansionResult:
    api_key = os.getenv("JINA_API_KEY", "")
    if not api_key:
        return await _expand_direct(url)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                "https://api.jina.ai/expander",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"url": url},
            )
            if resp.status_code != 200:
                return await _expand_direct(url)
            data = resp.json()
            expanded = data.get("expanded_urls", [])
            verify = await verify_url(url)
            return ExpansionResult(
                original_url=url,
                expanded_urls=expanded,
                verification=verify,
                method="jina",
                titles={},
            )
    except Exception:
        return await _expand_direct(url)


async def expand_url_multi(url: str) -> ExpansionResult:
    results = await asyncio.gather(
        _expand_direct(url),
        _expand_firecrawl(url),
        _expand_jina(url),
        return_exceptions=True,
    )
    expanded_set: set[str] = set()
    all_titles: dict[str, str] = {}
    best_method = "direct"

    for i, r in enumerate(results):
        if isinstance(r, Exception):
            continue
        if not isinstance(r, ExpansionResult):
            continue
        if not r.expanded_urls:
            continue
        for eu in r.expanded_urls:
            if eu not in expanded_set:
                expanded_set.add(eu)
                if r.titles.get(eu):
                    all_titles[eu] = r.titles[eu]
        if i > 0:
            best_method = r.method

    verify = await verify_url(url)
    return ExpansionResult(
        original_url=url,
        expanded_urls=list(expanded_set),
        verification=verify,
        method=best_method,
        titles=all_titles,
    )


class VerifyExpander:
    def __init__(self, default_method: str = "multi") -> None:
        self._default_method = default_method

    async def verify(self, url: str) -> VerifyResult:
        return await verify_url(url)

    async def expand(self, url: str, method: str | None = None) -> ExpansionResult:
        m = method or self._default_method
        if m == "multi":
            return await expand_url_multi(url)
        return await expand_url(url, m)

    async def verify_and_expand(
        self, url: str, method: str | None = None
    ) -> tuple[VerifyResult, ExpansionResult]:
        verify_result = await verify_url(url)
        if self._default_method == "multi":
            expand_result = await expand_url_multi(url)
        else:
            expand_result = await expand_url(url, method or "direct")
        return verify_result, expand_result
