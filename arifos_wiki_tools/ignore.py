"""arifos_wiki_tools.ignore — File filtering for safe repo scanning.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Iterator

DEFAULT_EXCLUDES: set[str] = {
    ".git/",
    ".hg/",
    ".svn/",
    ".venv/",
    "venv/",
    "node_modules/",
    "dist/",
    "build/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".next/",
    ".turbo/",
    "*.pyc",
    "*.pyo",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.pdf",
    "*.zip",
    "*.tar",
    "*.gz",
    "*.7z",
    "*.sqlite",
    "*.db",
    "*.parquet",
    "*.onnx",
    "*.pt",
    "*.bin",
    "*.lock",
    ".env",
    ".env.*",
    ".gitignore",
    ".gitingestignore",
}

DEFAULT_INCLUDES: set[str] = {
    "*.py",
    "*.js",
    "*.jsx",
    "*.ts",
    "*.tsx",
    "*.md",
    "*.mdx",
    "*.txt",
    "*.json",
    "*.yaml",
    "*.yml",
    "*.toml",
    "*.sh",
    "*.sql",
    "*.html",
    "*.css",
    "*.c",
    "*.cpp",
    "*.h",
    "*.hpp",
    "*.go",
    "*.rs",
    "*.java",
    "*.kt",
}


def _parse_gitignore(content: str) -> Iterator[str]:
    """
    Parse .gitignore content and yield fnmatch-compatible patterns.

    Handles:
    - Full-line comments (#)
    - Trailing comments (pattern # comment)
    - Negations (!pattern)
    - Directory-only patterns (trailing /)
    - Double-asterisk wildcards (**)
    - Escaped special chars (\\#, \\!)
    """
    for raw_line in content.splitlines():
        # Strip inline comments and trailing whitespace
        line = re.sub(r"#.*$", "", raw_line).strip()
        if not line:
            continue

        # Negations are returned as-is; caller handles them specially
        if line.startswith("!"):
            yield "\\" + line[1:]  # escape so fnmatch treats as literal !
            continue

        # Directory marker — convert to fnmatch-friendly glob
        if line.endswith("/"):
            yield line[:-1] + "/*"
            continue

        # Escape escaped special chars so fnmatch doesn't interpret them
        line = line.replace("\\#", "#").replace("\\!", "!")

        yield line


def load_gitignore_patterns(repo_root: Path, max_ancestor_depth: int = 4) -> set[str]:
    """
    Load and parse .gitignore patterns from repo_root and its ancestors.

    Returns a set of fnmatch patterns. Ancestor .gitignore patterns are
    prefixed with the relative path so they correctly scope subdirectories.

    Args:
        repo_root: The repository root to start from.
        max_ancestor_depth: Maximum number of ancestor directories to walk up.
            Defaults to 4 (prevents walking to filesystem root on deep paths).
    """
    patterns: list[tuple[Path, str]] = []  # (anchor_dir, pattern)
    cursor: Path | None = repo_root
    depth = 0

    while cursor is not None and depth <= max_ancestor_depth:
        gi = cursor / ".gitignore"
        if gi.is_file():
            try:
                content = gi.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                content = ""

            # Compute relative anchor from repo root
            try:
                rel = cursor.relative_to(repo_root)
                anchor = "" if str(rel) == "." else str(rel) + "/"
            except ValueError:
                anchor = ""

            for pat in _parse_gitignore(content):
                patterns.append((cursor, anchor + pat))

        cursor = cursor.parent
        depth += 1

    # De-dupe while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for _anchor, pat in reversed(patterns):
        if pat not in seen:
            seen.add(pat)
            unique.append(pat)

    return set(unique)


def matches_any(rel_path: str, patterns: set[str] | list[str] | tuple[str, ...]) -> bool:
    """Return True if rel_path matches any fnmatch pattern."""
    normalized = rel_path.replace("\\", "/")
    return any(fnmatch.fnmatch(normalized, pat) for pat in patterns)


def matches_gitignore(rel_path: str, gitignore_patterns: set[str]) -> bool:
    """Return True if rel_path matches any .gitignore pattern with git-style anchoring."""
    rel_path = rel_path.replace("\\", "/").strip("/")
    basename = rel_path.split("/")[-1]

    for pat in gitignore_patterns:
        is_negated = False
        if pat.startswith("\\!"):
            is_negated = True
            pat = pat[2:]

        pat_clean = pat.replace("\\", "/").strip("/")
        is_anchored = ("/" in pat_clean) or pat.startswith("/")

        if is_anchored:
            if fnmatch.fnmatch(rel_path, pat_clean):
                if is_negated:
                    return False
                return True
        else:
            if fnmatch.fnmatch(basename, pat_clean) or fnmatch.fnmatch(rel_path, pat_clean):
                if is_negated:
                    return False
                return True

    return False


def should_index(
    path: Path,
    repo_root: Path,
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    gitignore_patterns: set[str] | None = None,
) -> bool:
    """
    Decide whether a file should be included in the wiki index.

    Returns False for directories, binary files, files >1MB, and
    files matching DEFAULT_EXCLUDES, unlisted extensions, or
    .gitignore patterns parsed from the repo.
    """
    if not path.is_file():
        return False

    rel = path.relative_to(repo_root).as_posix()
    includes = set(include_globs or DEFAULT_INCLUDES)
    excludes = set(exclude_globs or DEFAULT_EXCLUDES)

    if matches_any(rel, excludes):
        return False

    # Apply .gitignore-derived patterns
    if gitignore_patterns and matches_gitignore(rel, gitignore_patterns):
        return False

    if not matches_any(rel, includes):
        return False

    try:
        if path.stat().st_size > 1_000_000:
            return False
    except OSError:
        return False

    return True
