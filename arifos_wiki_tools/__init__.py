"""arifOS Wiki Tools Forge — Local-first DeepWiki-style repo comprehension.

Four MCP-ready wiki operations:

- arif_wiki_ingest  — Walk a repo, chunk files, extract symbols, write index
- arif_wiki_map     — Produce repo structure map with key files and symbols
- arif_wiki_search  — Retrieve grounded evidence chunks from local index
- arif_wiki_ask     — Draft evidence-first answer with citations

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from arifos_wiki_tools.indexer import ingest_repo
from arifos_wiki_tools.search import search_index
from arifos_wiki_tools.synthesis import ask_repo, map_repo

__all__ = [
    "ingest_repo",
    "search_index",
    "ask_repo",
    "map_repo",
    "__version__",
]
__version__ = "0.1.0"
