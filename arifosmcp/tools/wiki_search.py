"""arifos_wiki_search — Cross-organ constitutional wiki + skills search.

One tool. Filesystem only. Grep-style. Fast. Read-only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Canonical search roots per organ (adjust if your layout differs)
_SEARCH_ROOTS: dict[str, Path] = {
    "aaa": Path("/root/AAA/wiki"),
    "arifos": Path("/root/arifOS"),
    "geox": Path("/root/geox"),
    "wealth": Path("/root/WEALTH/wiki"),
    "well": Path("/root/WELL"),
}

# Directories to skip during filesystem walk
_SKIP_DIRS: set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
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

# File extensions to search
_SEARCH_EXTS: tuple[str, ...] = (
    ".md",
    ".txt",
    ".py",
    ".yaml",
    ".yml",
    ".json",
)


def _walk_roots(roots: list[Path]):
    """Yield file paths under roots, skipping irrelevant directories."""
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            # Prune skipped directories in-place for efficiency
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for filename in filenames:
                if filename.endswith(_SEARCH_EXTS):
                    yield Path(dirpath) / filename


def arifos_wiki_search(
    query: str,
    repo: str = "all",
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search constitutional wikis and skills across the federation.

    Args:
        query: Search string (case-insensitive).
        repo: "all" or specific organ ("aaa", "arifos", "geox", "wealth", "well").
        limit: Max results to return.

    Returns:
        {
            "matches": [...],
            "total": int,
            "searched_repos": list[str],
            "query": str
        }
    """
    q = query.lower().strip()
    if not q:
        return {"matches": [], "total": 0, "searched_repos": [], "query": query}

    matches: list[dict[str, Any]] = []
    searched: list[str] = []

    targets = {repo: _SEARCH_ROOTS.get(repo)} if repo != "all" else _SEARCH_ROOTS

    for name, root in targets.items():
        if root is None or not root.exists():
            continue
        searched.append(name)

        for filepath in _walk_roots([root]):
            try:
                # Skip files larger than 2 MB to avoid latency
                if filepath.stat().st_size > 2 * 1024 * 1024:
                    continue

                content = filepath.read_text(encoding="utf-8", errors="ignore")
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
                        "title": filepath.stem,
                        "path": rel_path,
                        "repo": name,
                        "type": "skill" if "skill" in rel_path.lower() else "wiki",
                        "excerpt": excerpt[:200] + ("..." if len(excerpt) > 200 else ""),
                    }
                )
                if len(matches) >= limit:
                    break
            except Exception:
                continue
        if len(matches) >= limit:
            break

    return {
        "matches": matches[:limit],
        "total": len(matches),
        "searched_repos": searched,
        "query": query,
    }
