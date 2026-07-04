"""
arifosmcp/schemas/retrieve_tools.py — BM25 Tool Retrieval Schema
════════════════════════════════════════════════════════════════

Pydantic v2 schemas for arif_retrieve_tools — the BM25 lexical
tool retrieval primitive. F2 TRUTH: scores are lexical match,
never semantic relevance. F7 HUMILITY: scores are term-frequency,
not confidence.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolDocument(BaseModel):
    """A tool flattened into a searchable text document.

    This is the schema-aware text projection: name + description
    + parameter names + enum values, stripped of JSON syntax.
    """

    name: str = Field(description="Canonical tool name (e.g. geox_well_ingest)")
    organ: str = Field(description="Federation organ (arifOS, GEOX, WEALTH, WELL, A-FORGE)")
    domain: str = Field(default="", description="Domain within organ (well, seismic, model, basin, govern)")
    description: str = Field(description="One-line tool description")
    searchable_text: str = Field(
        description="Flattened searchable text: name + description + param names + enum values, JSON syntax stripped"
    )
    capability_tags: list[str] = Field(default_factory=list, description="Capability tags for hybrid re-rank")
    modes: list[str] | None = Field(default=None, description="Available operation modes (if mode-based tool)")
    parameters: list[dict[str, str]] = Field(
        default_factory=list,
        description="Parameter names and descriptions (no types, no JSON syntax)",
    )


class RetrievedTool(BaseModel):
    """A single BM25 retrieval result with epistemic labeling."""

    rank: int = Field(description="Rank position (1 = highest BM25 score)")
    tool_name: str = Field(description="Canonical tool name")
    organ: str = Field(description="Federation organ")
    domain: str = Field(default="", description="Domain within organ")
    bm25_score: float = Field(
        description="BM25 lexical match score. F7: term-frequency, NOT semantic relevance. NOT confidence."
    )
    description: str = Field(description="Tool description")
    snippet: str = Field(
        default="",
        description="Relevant excerpt from the searchable text that matched the query",
    )
    parameters: list[dict[str, str]] = Field(default_factory=list, description="Key parameters")
    capability_tags: list[str] = Field(default_factory=list, description="Capability tags")


class RetrieveToolsInput(BaseModel):
    """Input contract for arif_retrieve_tools."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language intent to match against tools. E.g. 'load well logs from LAS file'",
    )
    organ: str | None = Field(
        default=None,
        description="Restrict retrieval to this organ (arifOS, GEOX, WEALTH, WELL, A-FORGE). Omit for cross-organ.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of top tools to return (1-20, default 5)",
    )
    include_scores: bool = Field(
        default=True,
        description="Include BM25 scores in output. Set false for compact output.",
    )


class RetrieveToolsOutput(BaseModel):
    """Output contract for arif_retrieve_tools.

    F2 TRUTH: scores are lexical match, not confidence.
    F7 HUMILITY: BM25 is term-frequency ranking, not semantic understanding.
    """

    query: str = Field(description="Original query")
    organ_filter: str | None = Field(default=None, description="Organ filter applied (or none)")
    total_tools_indexed: int = Field(description="Total tools in the BM25 index")
    results: list[RetrievedTool] = Field(default_factory=list, description="Top-K retrieval results")
    epistemic_note: str = Field(
        default=(
            "BM25 lexical match. Scores measure TERM FREQUENCY overlap, not semantic relevance. "
            "A high score means the tool description shares many keywords with your query — "
            "it does NOT mean the tool is the 'best' or 'most appropriate' for your intent. "
            "Use these results as DISCOVERY hints, not as authoritative selection."
        ),
        description="F2/F7 epistemic disclaimer",
    )


# ─── Tool catalog types ──────────────────────────────────────────────────────


class ToolCatalogEntry(BaseModel):
    """A single entry in the federation tool catalog (from TOOLREGISTRY.json)."""

    name: str
    description: str
    capability_tags: list[str] = Field(default_factory=list)
    organ: str
    implemented: bool = True
    modes: list[str] | None = None
    parameters: list[dict[str, str]] = Field(default_factory=list)


class ToolCatalog(BaseModel):
    """The full federation tool catalog loaded from registry + live servers."""

    tools: list[ToolCatalogEntry] = Field(default_factory=list)
    source: str = Field(default="TOOLREGISTRY.json", description="Where the catalog was loaded from")
    loaded_at: str = Field(default="", description="ISO timestamp of catalog load")

    def __len__(self) -> int:
        return len(self.tools)

    def __iter__(self):
        return iter(self.tools)
