"""
arifosmcp/tools/wiki.py — Wiki tools: ingest, search, map, ask
═══════════════════════════════════════════════════════════════════

Consolidated from standalone arifos_wiki_tools package (ADR-013).
Provides repo-level comprehension: chunk index, TF-IDF search, grep fallback,
structural map, and evidence-first Q&A.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

TOKEN_RE = re.compile(r"[A-Za-z0-9_./:-]+")


@dataclass(frozen=True)
class FileRecord:
    path: str
    rel_path: str
    language: str
    size_bytes: int
    sha256: str
    line_count: int
    symbols: list[dict[str, Any]]


@dataclass(frozen=True)
class ChunkRecord:
    chunk_id: str
    rel_path: str
    language: str
    start_line: int
    end_line: int
    text: str
    symbols: list[dict[str, Any]]


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file, return list of dicts (empty on error/missing)."""
    if not path.exists():
        return []
    records: list[dict] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        return []
    return records


def to_jsonl(records: list[Any], path: Path) -> None:
    """Write records as JSONL."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = "\n".join(json.dumps(asdict(r), ensure_ascii=False) for r in records)
    path.write_text(lines + "\n", encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# INDEXER
# ═══════════════════════════════════════════════════════════════════════════════

_MAX_CHUNK_LINES = 80


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _safe_read(path: Path) -> str | None:
    """Read a file as UTF-8, or None if binary."""
    try:
        data = path.read_bytes()
        if b"\x00" in data[:4096]:
            return None
        return data.decode("utf-8", errors="replace")
    except Exception:
        return None


def _load_gitignore_patterns(repo_path: Path) -> list[re.Pattern]:
    """Load .gitignore patterns as compiled regexes."""
    gitignore_path = repo_path / ".gitignore"
    if not gitignore_path.exists():
        return []
    patterns: list[re.Pattern] = []
    for line in gitignore_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("/"):
            line = line[1:]
        try:
            patterns.append(re.compile(re.escape(line).replace(r"\*", ".*")))
        except re.error:
            continue
    return patterns


def _should_index(rel_path: str, gitignore_patterns: list[re.Pattern]) -> bool:
    """Check if a file should be indexed (not ignored)."""
    skip_extensions = {
        ".pyc", ".pyo", ".so", ".o", ".class", ".exe", ".dll", ".dylib",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
        ".woff", ".woff2", ".ttf", ".eot",
        ".zip", ".tar", ".gz", ".bz2", ".rar", ".7z",
        ".mp3", ".mp4", ".avi", ".mov", ".mkv",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".lock", ".gitkeep",
    }
    skip_dirs: set[str] = {
        ".git", "__pycache__", "node_modules", ".venv", "venv",
        "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ".egg-info", ".tox", ".cache", ".github", ".agents",
    }
    parts = rel_path.replace("\\", "/").split("/")
    if any(p in skip_dirs for p in parts):
        return False
    ext = Path(rel_path).suffix.lower()
    if ext in skip_extensions:
        return False
    for pattern in gitignore_patterns:
        if pattern.search(rel_path):
            return False
    return True


def _detect_language(rel_path: str) -> str:
    suffix = rel_path.lower().rsplit(".", 1)[-1] if "." in rel_path else ""
    return {
        "py": "python", "md": "markdown", "txt": "text",
        "yaml": "yaml", "yml": "yaml", "json": "json",
        "js": "javascript", "ts": "typescript", "tsx": "typescript",
        "jsx": "javascript", "rs": "rust", "go": "go",
        "java": "java", "c": "c", "cpp": "cpp", "h": "c",
        "html": "html", "css": "css", "sh": "bash", "toml": "toml",
        "sql": "sql", "rb": "ruby", "php": "php",
    }.get(suffix, "text")


def _extract_symbols(text: str, language: str) -> list[dict[str, Any]]:
    """Extract symbols (function/class defs) from source text."""
    symbols: list[dict[str, Any]] = []
    patterns: dict[str, list[re.Pattern]] = {
        "python": [
            re.compile(r"^(async\s+)?def\s+(\w+)\s*\(", re.MULTILINE),
            re.compile(r"^class\s+(\w+)", re.MULTILINE),
        ],
        "typescript": [
            re.compile(r"^(export\s+)?(async\s+)?function\s+(\w+)", re.MULTILINE),
            re.compile(r"^(export\s+)?class\s+(\w+)", re.MULTILINE),
            re.compile(r"^(export\s+)?(const|let|var)\s+(\w+)\s*[=:]", re.MULTILINE),
        ],
        "javascript": [
            re.compile(r"^(export\s+)?(async\s+)?function\s+(\w+)", re.MULTILINE),
            re.compile(r"^(export\s+)?class\s+(\w+)", re.MULTILINE),
        ],
    }
    for pat in patterns.get(language, []):
        for m in pat.finditer(text):
            name = m.group(len(m.groups()))
            symbols.append({
                "name": name,
                "kind": "function" if "def" in m.group(0) or "function" in m.group(0) else "class",
                "line": text[: m.start()].count("\n") + 1,
            })
    return symbols


def ingest_repo(
    repo_path: str | Path,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """
    Walk a repo, chunk files, extract symbols, write index.

    Returns a summary dict: files_indexed, chunks_written, languages, errors.
    """
    repo = Path(repo_path).expanduser().resolve()
    out_dir = repo / ".arifos"
    out_dir.mkdir(parents=True, exist_ok=True)

    gitignore_patterns = _load_gitignore_patterns(repo)

    files_metadata: list[FileRecord] = []
    chunks: list[ChunkRecord] = []
    errors: list[str] = []
    chunk_id_seq = 0

    for dirpath, dirnames, filenames in os.walk(repo, followlinks=False):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            fp = Path(dirpath) / fn
            rel = str(fp.relative_to(repo))
            if not _should_index(rel, gitignore_patterns):
                continue
            content = _safe_read(fp)
            if content is None:
                continue
            lang = _detect_language(rel)
            syms = _extract_symbols(content, lang)
            lines = content.splitlines()
            files_metadata.append(FileRecord(
                path=str(fp), rel_path=rel, language=lang,
                size_bytes=fp.stat().st_size, sha256=_sha256_text(content),
                line_count=len(lines), symbols=syms,
            ))
            for i in range(0, len(lines), _MAX_CHUNK_LINES):
                chunk_lines = lines[i : i + _MAX_CHUNK_LINES]
                chunks.append(ChunkRecord(
                    chunk_id=f"wiki:{rel}:{chunk_id_seq}",
                    rel_path=rel, language=lang,
                    start_line=i + 1, end_line=min(i + _MAX_CHUNK_LINES, len(lines)),
                    text="\n".join(chunk_lines), symbols=syms,
                ))
                chunk_id_seq += 1

    languages = Counter(r.language for r in files_metadata)

    to_jsonl(files_metadata, out_dir / "wiki_files.jsonl")
    to_jsonl(chunks, out_dir / "wiki_index.jsonl")

    return {
        "repo_path": str(repo),
        "files_indexed": len(files_metadata),
        "chunks_written": len(chunks),
        "languages": dict(languages.most_common()),
        "errors": errors,
        "index_path": str(out_dir / "wiki_index.jsonl"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

_FEDERATION_ROOTS: dict[str, Path] = {
    "aaa": Path("/root/AAA/wiki"),
    "arifos": Path(os.environ.get("ARIFOS_HOME", "/root")) / "arifOS",
    "geox": Path(os.environ.get("ARIFOS_HOME", "/root")) / "geox",
    "wealth": Path("/root/WEALTH/wiki"),
    "well": Path(os.environ.get("ARIFOS_HOME", "/root")) / "WELL",
}

_GREP_SKIP_DIRS: set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".egg-info", ".tox", ".cache", ".github", ".agents",
    ".claude", ".kimi", ".codex", ".gemini", ".copilot",
}

_GREP_EXTENSIONS: tuple[str, ...] = (".md", ".txt", ".py", ".yaml", ".yml", ".json")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text) if t]


def _score_chunk(query_tokens: list[str], chunk: dict) -> float:
    text_tokens = _tokenize(chunk.get("text", ""))
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
    lower = text.lower()
    hit_positions = [lower.find(q) for q in query_tokens if lower.find(q) >= 0]
    if not hit_positions:
        return text[:max_chars].strip()
    first_hit = min(hit_positions)
    start = max(first_hit - 180, 0)
    return text[start : start + max_chars].strip()


def _grep_search(repo_path: Path, query: str, limit: int = 8, max_files: int = 500) -> list[dict]:
    q = query.lower().strip()
    matches: list[dict[str, Any]] = []
    files_visited = 0
    repo_resolved = repo_path.resolve()
    targets: list[tuple[str, Path]] = []
    for name, root in _FEDERATION_ROOTS.items():
        try:
            if repo_resolved == root.resolve():
                targets = [(name, root)]
                break
        except Exception:
            pass
    else:
        if repo_path.exists():
            targets = [("local", repo_path)]
    if not targets:
        return []
    for name, root in targets:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in _GREP_SKIP_DIRS]
            for filename in filenames:
                if files_visited >= max_files:
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
                matches.append({
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
                })
                if len(matches) >= limit:
                    return matches[:limit]
    return matches[:limit]


def search_index(repo_path: str | Path, query: str, top_k: int = 8) -> list[dict]:
    """
    Unified wiki search — indexed when available, grep fallback otherwise.
    """
    repo = Path(repo_path).expanduser().resolve()
    q = query.lower().strip()
    if not q:
        return []
    index_path = repo / ".arifos" / "wiki_index.jsonl"
    records = read_jsonl(index_path)
    if records:
        query_tokens = _tokenize(q)
        scored: list[tuple[float, dict]] = []
        for rec in records:
            sc = _score_chunk(query_tokens, rec)
            if sc > 0:
                scored.append((sc, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        out: list[dict] = []
        for score, rec in scored[:top_k]:
            out.append({
                "score": round(score, 4),
                "rel_path": rec["rel_path"],
                "language": rec.get("language", "text"),
                "start_line": rec["start_line"],
                "end_line": rec["end_line"],
                "symbols": rec.get("symbols", []),
                "excerpt": _make_excerpt(rec.get("text", ""), query_tokens),
                "chunk_id": rec["chunk_id"],
                "search_mode": "indexed",
            })
        return out
    return _grep_search(repo, q, limit=top_k)


# ═══════════════════════════════════════════════════════════════════════════════
# SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════


def map_repo(repo_path: str | Path, max_depth: int = 4) -> dict:
    """Build a structural map of the repository from the wiki index."""
    repo = Path(repo_path).expanduser().resolve()
    files_path = repo / ".arifos" / "wiki_files.jsonl"
    records = read_jsonl(files_path)
    if not records:
        return {"error": f"No wiki file inventory at {files_path}. Run ingest first."}
    languages = Counter(r.get("language", "unknown") for r in records)
    tree: dict = {}
    for rec in records:
        parts = rec["rel_path"].split("/")
        node = tree
        for part in parts[:max_depth]:
            node = node.setdefault(part, {})
        if len(parts) > max_depth:
            node.setdefault("…", {})
    symbol_inventory: list[dict] = []
    for rec in records:
        syms = rec.get("symbols", [])
        if syms:
            symbol_inventory.append({
                "rel_path": rec["rel_path"],
                "language": rec["language"],
                "symbol_count": len(syms),
                "symbols": syms[:20],
            })
    symbol_inventory.sort(key=lambda x: x["symbol_count"], reverse=True)
    return {
        "repo_path": str(repo),
        "files_indexed": len(records),
        "languages": dict(languages.most_common()),
        "tree": tree,
        "symbol_inventory": symbol_inventory[:100],
    }


def ask_repo(repo_path: str | Path, question: str, top_k: int = 4) -> dict:
    """Draft evidence-first answer with citations."""
    chunks = search_index(repo_path, question, top_k=top_k)
    if not chunks:
        return {"answer": "No relevant evidence found.", "evidence": [], "confidence": "none"}
    excerpts = []
    for c in chunks:
        excerpts.append(f"[{c['rel_path']}:{c['start_line']}]\n{c['excerpt']}")
    return {
        "answer": f"Found {len(chunks)} relevant passages:\n\n" + "\n\n".join(excerpts),
        "evidence": chunks,
        "confidence": "draft" if len(chunks) >= 2 else "low",
    }


__all__ = [
    "ingest_repo",
    "search_index",
    "map_repo",
    "ask_repo",
]
