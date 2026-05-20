"""
arifosmcp/runtime/a_rif/source_rank.py — Source Authority Ranking
═════════════════════════════════════════════════════════════════

Maps sources to an authority tier (1 = highest, 9 = lowest).
Loads canonical ranking from resources/a_rif/source_rank.yaml.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
from typing import Any

import yaml

__all__ = ["rank_source", "get_rank_label", "evidence_level_from_rank"]

_RANKING: dict[int, str] | None = None


def _load_ranking() -> dict[int, str]:
    global _RANKING
    if _RANKING is not None:
        return _RANKING

    yaml_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "resources",
        "a_rif",
        "source_rank.yaml",
    )
    try:
        with open(yaml_path) as fh:
            data = yaml.safe_load(fh)
        _RANKING = {int(k): v for k, v in data.get("ranking", {}).items()}
    except Exception:
        _RANKING = {
            1: "Official Regulator / Government Source",
            2: "Primary Data / Academic Paper / Filing",
            3: "Reputable Institution (NASA, WHO, etc.)",
            4: "Reputable News Organization",
            5: "Specialist Expert Source",
            6: "General News Aggregator",
            7: "Blog / Social Media / Forum",
            8: "SEO Content Farm",
            9: "Unknown / Synthetic Source",
        }
    return _RANKING


def rank_source(url: str, content: str = "") -> int:
    """Return authority rank (1-9, lower is better)."""
    ranking = _load_ranking()
    url_lower = url.lower()

    # Heuristic fast path
    gov_patterns = [".gov", ".mil", ".go.id", ".go.uk", ".go.jp"]
    if any(p in url_lower for p in gov_patterns):
        return 1

    edu_patterns = [".edu", ".ac.uk", ".ac.id", ".ac.jp", "arxiv.org"]
    if any(p in url_lower for p in edu_patterns):
        return 2

    institution_patterns = ["nasa.gov", "who.int", "un.org", "worldbank.org"]
    if any(p in url_lower for p in institution_patterns):
        return 3

    news_patterns = ["reuters.com", "bloomberg.com", "apnews.com", "bbc.com"]
    if any(p in url_lower for p in news_patterns):
        return 4

    blog_patterns = ["medium.com", "blog.", "wordpress.com"]
    if any(p in url_lower for p in blog_patterns):
        return 7

    # Default to unknown
    return 9


def get_rank_label(rank: int) -> str:
    """Human-readable label for a rank."""
    ranking = _load_ranking()
    return ranking.get(rank, "Unknown / Synthetic Source")


def evidence_level_from_rank(rank: int) -> str:
    """Map authority rank to evidence level."""
    if rank <= 1:
        return "L4"
    if rank <= 2:
        return "L3"
    if rank <= 4:
        return "L2"
    if rank <= 6:
        return "L1"
    return "L0"
