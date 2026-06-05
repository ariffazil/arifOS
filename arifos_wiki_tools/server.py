"""arifos_wiki_tools.server — MCP server surface for arifOS Wiki Tools.

Run standalone::

    python -m arifos_wiki_tools.server

Requires::

    pip install "arifos-wiki-tools-forge[mcp]"

Or install arifOS in editable mode which brings in the MCP dependency.

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
    FastMCP = None

from arifos_wiki_tools.indexer import ingest_repo
from arifos_wiki_tools.search import search_index
from arifos_wiki_tools.synthesis import ask_repo, map_repo


def build_server():
    """Build the FastMCP server, or raise if MCP is not installed."""
    if FastMCP is None:
        raise RuntimeError(
            "MCP package not installed. Run: pip install 'arifos-wiki-tools-forge[mcp]'"
        )

    mcp = FastMCP("arifos-wiki-tools")

    @mcp.tool(
        name="arif_wiki_ingest",
        description=(
            "Index a local repository: walk files, detect language, extract symbols, "
            "chunk source, and write a local wiki index to <repo>/.arifos/. "
            "Optionally generates markdown wiki pages at <repo>/wiki/generated/. "
            "Safe: respects .gitignore-style exclusions, skips binaries and files >1MB. "
            "Use this first before search or ask."
        ),
    )
    def wiki_ingest(
        repo_path: str,
        scope_name: str = "arifOS",
        write_wiki: bool = True,
    ) -> dict:
        return ingest_repo(repo_path, scope_name=scope_name, write_wiki=write_wiki)

    @mcp.tool(
        name="arif_wiki_map",
        description=(
            "Return a structural map of a repository from its local wiki index: "
            "directory tree, language distribution, and symbol inventory for top files. "
            "Run 'arif_wiki_ingest' first."
        ),
    )
    def wiki_map(repo_path: str, max_depth: int = 4) -> dict:
        return map_repo(repo_path, max_depth=max_depth)

    @mcp.tool(
        name="arif_wiki_search",
        description=(
            "Search the local wiki index and return scored evidence chunks: "
            "file path, line range, detected symbols, and contextual excerpt. "
            "Scoring weights term frequency, path hits, and symbol hits. "
            "Run 'arif_wiki_ingest' first."
        ),
    )
    def wiki_search(repo_path: str, query: str, top_k: int = 8) -> list[dict]:
        return search_index(repo_path, query, top_k=top_k)

    @mcp.tool(
        name="arif_wiki_ask",
        description=(
            "Draft a cautious evidence-first answer to a natural-language question "
            "about a repository, grounded in retrieved index chunks. "
            "Always cites file paths and line ranges. "
            "Confidence is 'medium' when >=3 chunks match, else 'low'. "
            "Run 'arif_wiki_ingest' first."
        ),
    )
    def wiki_ask(repo_path: str, question: str, top_k: int = 8) -> dict:
        return ask_repo(repo_path, question, top_k=top_k)

    return mcp


def main() -> None:
    server = build_server()
    server.run()


if __name__ == "__main__":
    main()
