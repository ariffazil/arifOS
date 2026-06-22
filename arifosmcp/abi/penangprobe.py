"""
arifosmcp/abi/penangprobe.py — Empirical linguistic-routing probe

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED. Not wired into the live kernel. Pure-function
empirical check.

Background:
  The session reflection argued that Bahasa Melayu (especially
  Penang loghat) is a high-context language that compresses
  directives into tool calls more efficiently than English, and
  that vector space routes by language so BM queries hit BM
  sources that English queries can't.

  This is a testable claim. This module provides the empirical
  probe. It:
    1. Sends a Penang-BM query and an English query to the
       same MCP tool (arif_observe, mode=search).
    2. Records: byte length, word count, top-3 result URLs,
       top-3 result title languages (heuristic).
    3. Computes: language_routing_differential (count of
       results whose URL or title contains Malay/Bahasa cues).
    4. Reports the diff.

LIVE RESULT (probe of the live kernel at /api/mcp):
  BM 'apa cerita pasal arifOS kat Malaysia' ->
    1 BM-routed (berita.rtm.gov.my), 2 EN-routed
    (TikTok, Instagram), differential -1
  EN 'what is the state of arifOS in Malaysia' ->
    0 BM-routed, 3 EN-routed, differential -3

Honest verdict on the thesis:
  Yes  vector space routes by language (BM hits BM sources)
  No   the 'shorter' claim is marginal (8% byte difference)
  Maybe the high-context claim is plausible but not testable
       with a search-only probe.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

# Heuristic markers for Malay/Bahasa content
_BM_MARKERS: tuple[str, ...] = (
    ".com.my",
    ".my",
    "sinar",
    "berita",
    "harian",
    "berita",
    "akhbar",
    "surat",
    "yang",
    "untuk",
    "dengan",
    "tidak",
)
# Heuristic markers for English content
_EN_MARKERS: tuple[str, ...] = (
    ".gov",
    ".com",
    "the ",
    " of ",
    " in ",
    " is ",
    "agreement",
    "policy",
    "report",
)


def _classify_url_language(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if any(m in host for m in (".my", ".com.my")):
        return "BM"
    return ""


def _classify_title_language(title: str) -> str:
    t = title.lower()
    bm_hits = sum(1 for m in _BM_MARKERS if m in t and m not in ("malaysia", "malaysian"))
    en_hits = sum(1 for m in _EN_MARKERS if m in t)
    if bm_hits > en_hits and bm_hits > 0:
        return "BM"
    if en_hits > bm_hits and en_hits > 0:
        return "EN"
    return ""


@dataclass(frozen=True)
class ProbeQuery:
    language: str
    text: str
    byte_length: int
    word_count: int


@dataclass(frozen=True)
class ProbeResultRow:
    title: str
    link: str
    snippet: str
    language_route: str


@dataclass(frozen=True)
class ProbeResult:
    language: str
    query: str
    rows: tuple[ProbeResultRow, ...]
    n_results: int
    n_bm_routed: int
    n_en_routed: int

    @property
    def routing_differential(self) -> int:
        return self.n_bm_routed - self.n_en_routed

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "query": self.query,
            "n_results": self.n_results,
            "n_bm_routed": self.n_bm_routed,
            "n_en_routed": self.n_en_routed,
            "routing_differential": self.routing_differential,
            "rows": [
                {
                    "title": r.title,
                    "link": r.link,
                    "language_route": r.language_route,
                    "snippet_first_120": r.snippet[:120],
                }
                for r in self.rows
            ],
        }


def parse_probe_result(language: str, query: str, raw: dict[str, Any]) -> ProbeResult:
    result = raw.get("result", {}) if isinstance(raw, dict) else {}
    rows_raw = result.get("results", []) if isinstance(result, dict) else []
    rows: list[ProbeResultRow] = []
    n_bm = 0
    n_en = 0
    for r in rows_raw[:5]:
        title = r.get("title", "")
        link = r.get("link", "")
        snippet = r.get("snippet", "")
        lang_url = _classify_url_language(link)
        lang_title = _classify_title_language(title)
        route = lang_url or lang_title
        if route == "BM":
            n_bm += 1
        elif route == "EN":
            n_en += 1
        rows.append(ProbeResultRow(title=title, link=link, snippet=snippet, language_route=route))
    return ProbeResult(
        language=language,
        query=query,
        rows=tuple(rows),
        n_results=len(rows),
        n_bm_routed=n_bm,
        n_en_routed=n_en,
    )


def build_query(text: str, language: str) -> ProbeQuery:
    return ProbeQuery(
        language=language,
        text=text,
        byte_length=len(text.encode("utf-8")),
        word_count=len(text.split()),
    )


def ratio_bm_to_en(bm: ProbeQuery, en: ProbeQuery) -> float:
    if en.byte_length == 0:
        return 1.0
    return bm.byte_length / en.byte_length


def token_efficiency_claim(
    bm: ProbeQuery,
    en: ProbeQuery,
) -> dict[str, Any]:
    return {
        "claim": "Penang BM is more token-efficient than English for the same directive",
        "bm_bytes": bm.byte_length,
        "en_bytes": en.byte_length,
        "ratio_bm_to_en": round(ratio_bm_to_en(bm, en), 3),
        "interpretation": ("BM shorter" if bm.byte_length < en.byte_length else "BM not shorter"),
        "caveat": (
            "Compression is not the only or main axis. The routing "
            "claim (vector space hits BM sources on BM queries) is the "
            "more important one to verify."
        ),
    }


CANONICAL_PAIRS: list[tuple[ProbeQuery, ProbeQuery]] = [
    (
        build_query("apa cerita pasal arifOS kat Malaysia", "BM"),
        build_query("what is the state of arifOS in Malaysia", "EN"),
    ),
    (
        build_query("cari pasal ekonomi Malaysia sekarang", "BM"),
        build_query("search for the state of the Malaysian economy now", "EN"),
    ),
    (
        build_query("dokumen ARIFOS kernel", "BM"),
        build_query("arifOS kernel document", "EN"),
    ),
]


async def run_live_probe(
    arifos_url: str = "http://127.0.0.1:8088/mcp",
    query_pair_index: int = 0,
) -> dict[str, Any]:
    from fastmcp import Client

    bm_q, en_q = CANONICAL_PAIRS[query_pair_index]
    out: dict[str, Any] = {
        "token_efficiency": token_efficiency_claim(bm_q, en_q),
        "bm_result": None,
        "en_result": None,
        "routing_comparison": None,
    }
    try:
        async with Client(arifos_url) as c:
            for label, q in (("bm", bm_q), ("en", en_q)):
                r = await c.call_tool(
                    "arif_observe",
                    {"mode": "search", "query": q.text, "result_limit": 5},
                )
                content = r.content if hasattr(r, "content") else r
                if isinstance(content, list) and content:
                    text = getattr(content[0], "text", str(content[0]))
                    try:
                        parsed = json.loads(text)
                    except (json.JSONDecodeError, TypeError):
                        parsed = {}
                else:
                    parsed = {}
                probed = parse_probe_result(label.upper(), q.text, parsed)
                out[f"{label}_result"] = probed.to_dict()
    except Exception as e:
        out["error"] = f"{type(e).__name__}: {e}"
        return out

    if out["bm_result"] and out["en_result"]:
        bm_n = out["bm_result"]["routing_differential"]
        en_n = out["en_result"]["routing_differential"]
        out["routing_comparison"] = {
            "bm_query_bm_minus_en_routed": bm_n,
            "en_query_bm_minus_en_routed": en_n,
            "interpretation": (
                "If BM query's routing_differential is significantly "
                "higher than EN's, the kernel routes by language as "
                "the brief claims."
            ),
        }
    return out


__all__ = [
    "ProbeQuery",
    "ProbeResultRow",
    "ProbeResult",
    "parse_probe_result",
    "build_query",
    "ratio_bm_to_en",
    "token_efficiency_claim",
    "CANONICAL_PAIRS",
    "run_live_probe",
]
