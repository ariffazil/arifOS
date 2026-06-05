"""arifos_wiki_tools.search — Unified wiki search: indexed + grep-style fallback.

search_index() uses indexed retrieval when a wiki index exists at
<repo>/.arifos/wiki_index.jsonl; otherwise falls back to cross-organ
grep-style search across configured federation roots.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from arifos_wiki_tools.models import read_jsonl

TOKEN_RE = re.compile(r"[A-Za-z0-9_./:-]+")

# ── Cross-organ federation roots (used by grep fallback) ────────────────────────
_FEDERATION_ROOTS: dict[str, Path] = {
    "aaa": Path("/root/AAA/wiki"),
    "arifos": Path("/root/arifOS"),
    "geox": Path("/root/geox"),
    "wealth": Path("/root/WEALTH/wiki"),
    "well": Path("/root/WELL"),
}

# ── Grep fallback skip dirs ─────────────────────────────────────────────────
_GREP_SKIP_DIRS: set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".egg-info",
    ".tox",
    ".cache",
    ".github",
    ".agents",
    ".claude",
    ".kimi",
    ".codex",
    ".gemini",
    ".copilot",
}

_GREP_EXTENSIONS: tuple[str, ...] = (".md", ".txt", ".py", ".yaml", ".yml", ".json")


# ── Tokenization ────────────────────────────────────────────────────────────────


def tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokens from text."""
    return [t.lower() for t in TOKEN_RE.findall(text) if t]


# ── Index-based retrieval ─────────────────────────────────────────────────────


def _load_index(repo_path: Path) -> list[dict]:
    """Load wiki index from .arifos/wiki_index.jsonl, or return empty list."""
    index_path = repo_path / ".arifos" / "wiki_index.jsonl"
    records = read_jsonl(index_path)
    return records


def _score_chunk(query_tokens: list[str], chunk: dict) -> float:
    """
    Score a chunk by lexical relevance.

    - TF-IDF-like term frequency (log-weighted)
    - Length normalization
    - Path/symbol hit bonuses
    """
    text_tokens = tokenize(chunk.get("text", ""))
    if not text_tokens:
        return 0.0

    counts: Counter[str] = Counter(text_tokens)
    length_norm = 1.0 / math.sqrt(max(len(text_tokens), 1))
    score = 0.0
    for qt in query_tokens:
        tf = counts.get(qt, 0)
        if tf:
            score += (1.0 + math.log(tf)) * length_norm

    rel_path = chunk.get("rel_path", "").lower()
    symbol_blob = " ".join(str(s.get("name", "")) for s in chunk.get("symbols", [])).lower()
    for qt in query_tokens:
        if qt in rel_path:
            score += 0.75
        if qt in symbol_blob:
            score += 1.25

    return score


def _make_excerpt(text: str, query_tokens: list[str], max_chars: int = 700) -> str:
    """Extract a contextual excerpt around the first query hit."""
    lower = text.lower()
    hit_positions = [lower.find(q) for q in query_tokens if lower.find(q) >= 0]
    if not hit_positions:
        return text[:max_chars].strip()
    first_hit = min(hit_positions)
    start = max(first_hit - 180, 0)
    return text[start : start + max_chars].strip()


# ── Grep-style fallback ────────────────────────────────────────────────────────


def _grep_search(
    repo_path: Path,
    query: str,
    limit: int = 8,
    max_files: int = 500,
) -> list[dict]:
    """
    Grep-style search used when no wiki index exists.

    When repo_path is a known federation root, searches that root directly.
    When repo_path is a custom path, searches it and its subdirectories.

    Args:
        repo_path: The repo to search.
        query: Search query string.
        limit: Maximum number of results to return.
        max_files: Cap on files to inspect before bailing out.
            Prevents catastrophic slowdown on large directory trees.
    """
    q = query.lower().strip()
    matches: list[dict[str, Any]] = []
    files_visited = 0

    # Determine search roots
    repo_resolved = repo_path.resolve()

    # If repo_path matches a federation root, search that root only
    # Otherwise search repo_path and its subdirs
    targets: list[tuple[str, Path]] = []

    for name, root in _FEDERATION_ROOTS.items():
        try:
            if repo_resolved == root.resolve():
                targets = [(name, root)]
                break
        except Exception:
            pass
    else:
        # Not a known root — treat repo_path as the search target
        if repo_path.exists():
            targets = [("local", repo_path)]

    if not targets:
        return []

    for name, root in targets:
        if not root.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            # Prune skipped directories in-place
            dirnames[:] = [d for d in dirnames if d not in _GREP_SKIP_DIRS]

            for filename in filenames:
                if files_visited >= max_files:
                    # Bail out — too many files inspected
                    return matches[:limit]

                if not filename.endswith(_GREP_EXTENSIONS):
                    continue

                files_visited += 1
                filepath = Path(dirpath) / filename
                try:
                    if filepath.stat().st_size > 2 * 1024 * 1024:
                        continue
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                if q not in content.lower():
                    continue

                idx = content.lower().find(q)
                start = max(0, idx - 80)
                end = min(len(content), idx + 120)
                excerpt = content[start:end].replace("\n", " ").strip()

                try:
                    rel_path = str(filepath.relative_to(root))
                except ValueError:
                    rel_path = str(filepath)

                matches.append(
                    {
                        "score": 1.0,
                        "rel_path": rel_path,
                        "repo": name,
                        "language": _detect_language(rel_path),
                        "start_line": content[:idx].count("\n") + 1,
                        "end_line": content[: idx + (end - start)].count("\n") + 1,
                        "symbols": [],
                        "excerpt": excerpt[:200] + ("..." if len(excerpt) > 200 else ""),
                        "chunk_id": f"{rel_path}:grep",
                        "search_mode": "grep",
                    }
                )
                if len(matches) >= limit:
                    return matches[:limit]

    return matches[:limit]


def _detect_language(rel_path: str) -> str:
    suffix = rel_path.lower().rsplit(".", 1)[-1] if "." in rel_path else ""
    return {
        "py": "python",
        "md": "markdown",
        "txt": "text",
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json",
    }.get(suffix, "text")


# ── Public API ────────────────────────────────────────────────────────────────


def search_index(
    repo_path: str | Path,
    query: str,
    top_k: int = 8,
) -> list[dict]:
    """
    Unified wiki search — indexed when available, grep fallback otherwise.

    Strategy:
      1. If <repo_path>/.arifos/wiki_index.jsonl exists → indexed retrieval
         (chunk-level, scored by TF-IDF + symbol bonus)
      2. Otherwise → grep-style cross-organ search
         (file-level, across federation roots or the given repo)

    Returns up to ``top_k`` results. Each result includes:
      score, rel_path, language, start_line, end_line, symbols,
      excerpt, chunk_id, and search_mode ("indexed" | "grep").
    """
    repo = Path(repo_path).expanduser().resolve()
    q = query.lower().strip()
    if not q:
        return []

    # ── Try indexed search first ─────────────────────────────────────────────
    records = _load_index(repo)
    if records:
        query_tokens = tokenize(q)
        scored: list[tuple[float, dict]] = []
        for rec in records:
            sc = _score_chunk(query_tokens, rec)
            if sc > 0:
                scored.append((sc, rec))

        scored.sort(key=lambda x: x[0], reverse=True)
        out: list[dict] = []
        for score, rec in scored[:top_k]:
            out.append(
                {
                    "score": round(score, 4),
                    "rel_path": rec["rel_path"],
                    "language": rec.get("language", "text"),
                    "start_line": rec["start_line"],
                    "end_line": rec["end_line"],
                    "symbols": rec.get("symbols", []),
                    "excerpt": _make_excerpt(rec.get("text", ""), query_tokens),
                    "chunk_id": rec["chunk_id"],
                    "search_mode": "indexed",
                }
            )
        return out

    # ── Grep fallback ──────────────────────────────────────────────────────────
    return _grep_search(repo, q, limit=top_k)
