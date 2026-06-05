"""arifos_wiki_tools.synthesis — Map and ask operations over wiki index."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from arifos_wiki_tools.models import read_jsonl
from arifos_wiki_tools.search import search_index


def map_repo(repo_path: str | Path, max_depth: int = 4) -> dict:
    """
    Build a structural map of the repository from the wiki index.

    Returns a dict with:
        repo_path, files_indexed, languages (Counter),
        tree (nested dict of dir names), symbol_inventory (top 100 files with symbols)
    """
    repo = Path(repo_path).expanduser().resolve()
    files_path = repo / ".arifos" / "wiki_files.jsonl"
    records = read_jsonl(files_path)
    if not records:
        raise ValueError(
            f"No wiki file inventory found at {files_path}. Run 'arif-wiki ingest <repo>' first."
        )

    languages = Counter(r.get("language", "unknown") for r in records)

    # Build a shallow tree up to max_depth
    tree: dict = {}
    for rec in records:
        parts = rec["rel_path"].split("/")
        node = tree
        for part in parts[:max_depth]:
            node = node.setdefault(part, {})
        if len(parts) > max_depth:
            node.setdefault("…", {})

    symbol_inventory = []
    for rec in records:
        syms = rec.get("symbols", [])
        if syms:
            symbol_inventory.append(
                {
                    "rel_path": rec["rel_path"],
                    "language": rec["language"],
                    "symbol_count": len(syms),
                    "symbols": syms[:20],
                }
            )

    return {
        "repo_path": str(repo),
        "files_indexed": len(records),
        "languages": dict(languages.most_common()),
        "tree": tree,
        "symbol_inventory": symbol_inventory[:100],
    }


def ask_repo(
    repo_path: str | Path,
    question: str,
    top_k: int = 8,
) -> dict:
    """
    Draft an evidence-first answer grounded in the local wiki index.

    v0 policy: conservative synthesis — no fabricated architecture.
    The answer cites file paths, line ranges, and symbols.
    Confidence is "medium" when >=3 evidence chunks match, else "low".

    Returns a dict with:
        answer (str), confidence ("medium"|"low"),
        evidence (list of search hits), warnings (list of caveats)
    """
    evidence = search_index(repo_path, question, top_k=top_k)

    if not evidence:
        return {
            "answer": (
                "No grounded answer found. "
                "Run ingestion first, broaden the query, or inspect the repo manually."
            ),
            "confidence": "low",
            "evidence": [],
            "warnings": ["No evidence chunks matched the question."],
        }

    # Deduplicate by file path, preserve order
    seen: set[str] = set()
    likely_paths: list[str] = []
    for e in evidence:
        key = e["rel_path"]
        if key not in seen:
            likely_paths.append(key)
            seen.add(key)

    answer_parts = [
        "**Evidence-first answer draft:**",
        "",
        f"The strongest matching files are: {', '.join(f'`{p}`' for p in likely_paths[:5])}.",
        "",
        "*Review the cited line ranges before accepting this conclusion.*",
        "",
    ]

    # Add detected symbols as structured evidence
    symbols: list[str] = []
    for e in evidence:
        for s in e.get("symbols", []):
            symbols.append(
                f"- `{s.get('kind')} {s.get('name')}` in `{e['rel_path']}`:{s.get('line', '?')}"
            )
    if symbols:
        answer_parts.extend(["", "**Detected relevant symbols:**"])
        answer_parts.extend(symbols[:12])

    warnings = [
        "This v0 tool uses lexical retrieval, not full semantic embeddings.",
        "Use Qdrant/BGE-M3 + SEA-LION adapter in v1 for stronger synthesis.",
    ]

    return {
        "answer": "\n".join(answer_parts),
        "confidence": "medium" if len(evidence) >= 3 else "low",
        "evidence": evidence,
        "warnings": warnings,
    }
