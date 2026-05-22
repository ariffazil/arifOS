"""arifos_wiki_tools.models — Immutable record types for wiki indexing."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


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
    sha256: str


def to_jsonl(records: list[Any], path: Path) -> None:
    """Write a list of dataclass instances to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file back as a list of plain dicts."""
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out
