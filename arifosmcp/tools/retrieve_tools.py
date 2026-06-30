"""
arifosmcp/tools/retrieve_tools.py — arif_retrieve_tools: BM25 Tool Retrieval
══════════════════════════════════════════════════════════════════════════════

BM25-based lexical tool retrieval across the arifOS federation tool catalog.

ARCHITECTURE — Ratel Insight Applied:
  Ratel proved BM25 beats semantic embeddings for tool selection because tool
  descriptions are short, keyword-shaped, and structurally similar. Cosine
  similarity smears the discriminator token; BM25 keeps it sharp.

  Our hybrid: arif_route classifies intent → organ (structural partition),
  then arif_retrieve_tools ranks tools within that organ via BM25 (lexical
  retrieval). Cross-organ retrieval also supported when organ is ambiguous.

BM25 PARAMETERS (from Ratel ADR-0004, tuned for short tool docs):
  k1 = 0.9  — term saturation (lower = less weight on repeated terms)
  b  = 0.4  — length normalization (lower = short docs not penalized)

SCHEMA-AWARE TEXT PROJECTION:
  Tool name + description + parameter names + enum values
  → flattened into one string, JSON syntax stripped
  → deterministic, stable ordering
  → indexed by BM25

CONSTITUTIONAL:
  F1 AMANAH: Read-only. No mutation. Reversible by definition.
  F2 TRUTH: Scores are lexical match, not confidence. Never claim "best match."
  F7 HUMILITY: Score is term frequency, not semantic relevance. Labeled clearly.
  F9 ANTIHANTU: No hallucinated tools. Only indexed tools returned.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import math
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.schemas.retrieve_tools import (
    RetrieveToolsInput,
    RetrieveToolsOutput,
    RetrievedTool,
    ToolCatalog,
    ToolCatalogEntry,
    ToolDocument,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# BM25 ENGINE — Pure Python, zero dependencies
# ═══════════════════════════════════════════════════════════════════════════════

K1 = 0.9  # term saturation (Ratel ADR-0004)
B = 0.4   # length normalization (tuned for short tool descriptions)


class BM25Engine:
    """Pure-Python BM25 retrieval engine.

    Implements the Okapi BM25 ranking function with k1=0.9, b=0.4
    tuned for short tool descriptions as validated by Ratel benchmarks.
    """

    def __init__(self, k1: float = K1, b: float = B):
        self.k1 = k1
        self.b = b
        self._documents: list[ToolDocument] = []
        self._corpus: list[list[str]] = []  # tokenized documents
        self._doc_freq: dict[str, int] = {}  # document frequency per term
        self._avgdl: float = 0.0
        self._N: int = 0

    def index(self, documents: list[ToolDocument]) -> None:
        """Build the BM25 index from a list of tool documents."""
        self._documents = list(documents)
        self._corpus = []
        self._doc_freq = {}
        self._N = len(documents)

        for doc in documents:
            tokens = self._tokenize(doc.searchable_text)
            self._corpus.append(tokens)
            seen: set[str] = set()
            for token in tokens:
                if token not in seen:
                    self._doc_freq[token] = self._doc_freq.get(token, 0) + 1
                    seen.add(token)

        total_len = sum(len(tokens) for tokens in self._corpus)
        self._avgdl = total_len / max(self._N, 1)

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """Search indexed documents, return (doc_index, bm25_score) pairs."""
        if self._N == 0:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: list[float] = []
        for doc_idx in range(self._N):
            score = self._score(query_tokens, doc_idx)
            scores.append(score)

        # Rank by score descending, keep top_k
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return [(idx, s) for idx, s in ranked if s > 0][:top_k]

    def _score(self, query_tokens: list[str], doc_idx: int) -> float:
        """Compute BM25 score for one document against query tokens."""
        doc_tokens = self._corpus[doc_idx]
        doc_len = len(doc_tokens)
        score = 0.0

        # Count term frequencies in this document
        tf_map: dict[str, int] = {}
        for t in doc_tokens:
            tf_map[t] = tf_map.get(t, 0) + 1

        for qt in query_tokens:
            tf = tf_map.get(qt, 0)
            if tf == 0:
                continue
            df = self._doc_freq.get(qt, 0)
            # IDF: inverse document frequency
            idf = math.log((self._N - df + 0.5) / (df + 0.5) + 1.0)
            # BM25 term score
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(self._avgdl, 1)))
            score += idf * (numerator / denominator)

        return score

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer: lowercase, split on non-alphanumeric, filter short tokens."""
        # Normalize
        text = text.lower()
        # Split on non-alphanumeric (keep underscores as they matter for tool names)
        tokens = re.findall(r"[a-z0-9_]+", text)
        # Filter: remove very short tokens (len < 2) and pure numbers
        return [t for t in tokens if len(t) >= 2 and not t.isdigit()]

    @property
    def document_count(self) -> int:
        return self._N


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMA-AWARE TEXT PROJECTION
# ═══════════════════════════════════════════════════════════════════════════════


def _flatten_tool(tool: ToolCatalogEntry) -> ToolDocument:
    """Project a tool into a searchable text document.

    Schema-aware: strips JSON syntax (type, required, $ref, braces),
    keeps the words that matter — names, descriptions, enum values.
    """
    parts: list[str] = []

    # Tool name (weighted by appearing twice — prefix + full)
    parts.append(tool.name)
    # Also add the verb part of geox_well_ingest → "well ingest" for partial matches
    name_parts = tool.name.replace("_", " ")
    parts.append(name_parts)

    # Description
    if tool.description:
        # Strip JSON-like tokens that add noise
        clean_desc = _strip_json_noise(tool.description)
        parts.append(clean_desc)

    # Parameter names and descriptions
    for param in tool.parameters:
        pname = param.get("name", "")
        pdesc = param.get("description", "")
        if pname:
            parts.append(pname)
        if pdesc:
            parts.append(_strip_json_noise(pdesc))

    # Enum values (keep the words, drop the braces)
    # Already handled in _strip_json_noise for the full text

    # Capability tags
    for tag in tool.capability_tags:
        parts.append(tag.replace("-", " "))

    # Mode names
    if tool.modes:
        for mode in tool.modes:
            parts.append(mode)

    full_text = " ".join(parts)
    # Remove any remaining JSON artifacts
    full_text = _strip_json_noise(full_text)

    return ToolDocument(
        name=tool.name,
        organ=tool.organ,
        domain="",
        description=tool.description,
        searchable_text=full_text,
        capability_tags=tool.capability_tags,
        modes=tool.modes,
        parameters=tool.parameters,
    )


def _strip_json_noise(text: str) -> str:
    """Strip JSON syntax tokens that add noise to searchable text.

    Removes: schema keywords (type, required, properties, $ref, items, enum),
    braces, brackets, quotes — but keeps the actual words.
    """
    # Remove JSON structural tokens
    noise_patterns = [
        (r'\btype\b', ' '),
        (r'\brequired\b', ' '),
        (r'\bproperties\b', ' '),
        (r'\b\$ref\b', ' '),
        (r'\bitems\b', ' '),
        (r'\bconst\b', ' '),
        (r'\bdefault\b', ' '),
        (r'\banyOf\b', ' '),
        (r'\boneOf\b', ' '),
        (r'\ballOf\b', ' '),
        (r'\benum\b', ' '),
        (r'\bnull\b', ' '),
        (r'\bboolean\b', ' '),
        (r'\bstring\b', ' '),
        (r'\binteger\b', ' '),
        (r'\bnumber\b', ' '),
        (r'\bobject\b', ' '),
        (r'\barray\b', ' '),
        (r'\btrue\b', ' '),
        (r'\bfalse\b', ' '),
        (r'\bdescription\b', ' '),
        (r'\btitle\b', ' '),
        (r'[{}\[\]"\'<>]', ' '),
        (r'\s+', ' '),
    ]
    cleaned = text
    for pattern, replacement in noise_patterns:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL CATALOG LOADER
# ═══════════════════════════════════════════════════════════════════════════════

# Cache the catalog and BM25 index
_catalog_cache: ToolCatalog | None = None
_bm25_cache: BM25Engine | None = None
_catalog_loaded_at: str = ""


def load_tool_catalog(refresh: bool = False) -> ToolCatalog:
    """Load the federation tool catalog from TOOLREGISTRY.json.

    Cached after first load. Use refresh=True to force reload.
    """
    global _catalog_cache, _catalog_loaded_at

    if _catalog_cache is not None and not refresh:
        return _catalog_cache

    tools: list[ToolCatalogEntry] = []

    # ── Primary source: TOOLREGISTRY.json ──────────────────────────────────
    registry_paths = [
        Path("/root/AAA/docs/TOOLREGISTRY.json"),
        Path("/root/arifOS/arifosmcp/tool_registry.json"),
    ]

    for registry_path in registry_paths:
        if registry_path.exists():
            try:
                with open(registry_path) as f:
                    data = json.load(f)
                tools.extend(_extract_tools_from_registry(data, str(registry_path)))
            except Exception:
                logger.warning(f"Failed to load tool registry from {registry_path}", exc_info=True)

    # ── Fallback: always include hardcoded catalog as supplement ────────────
    # The TOOLREGISTRY.json "skills" section uses skill names (kebab-case)
    # which differ from MCP tool names (snake_case). The fallback catalog
    # provides the canonical MCP tool names with proper descriptions.
    fallback_tools = _fallback_catalog()
    # Merge: fallback tools supplement registry, don't duplicate by name
    existing_names = {t.name for t in tools}
    for ft in fallback_tools:
        if ft.name not in existing_names:
            tools.append(ft)

    _catalog_cache = ToolCatalog(
        tools=tools,
        source="TOOLREGISTRY.json + fallback",
        loaded_at=datetime.now(UTC).isoformat(),
    )
    _catalog_loaded_at = _catalog_cache.loaded_at
    return _catalog_cache


def _extract_tools_from_registry(data: dict, source_path: str) -> list[ToolCatalogEntry]:
    """Extract tool entries from TOOLREGISTRY.json structure."""
    entries: list[ToolCatalogEntry] = []

    # Skills section
    for skill in data.get("skills", []):
        entries.append(
            ToolCatalogEntry(
                name=skill.get("name", ""),
                description=skill.get("description", ""),
                capability_tags=skill.get("capability_tags", []),
                organ=skill.get("organ", "unknown"),
                implemented=skill.get("implemented", True),
            )
        )

    # Deep research stub tools
    stub_tools = data.get("deep_research_stub_tools", {})
    for tool_name, tool_info in stub_tools.items():
        if isinstance(tool_info, dict):
            entries.append(
                ToolCatalogEntry(
                    name=tool_name,
                    description=tool_info.get("description", ""),
                    capability_tags=tool_info.get("capability_tags", []),
                    organ=tool_info.get("organ", "arifOS"),
                    implemented=tool_info.get("implemented", True),
                )
            )

    # Tools section (if present)
    for tool in data.get("tools", []):
        if isinstance(tool, dict):
            entries.append(
                ToolCatalogEntry(
                    name=tool.get("name", ""),
                    description=tool.get("description", ""),
                    capability_tags=tool.get("capability_tags", []),
                    organ=tool.get("organ", "unknown"),
                    implemented=tool.get("implemented", True),
                    modes=tool.get("modes"),
                )
            )

    # Organs section — extract tool lists per organ
    for organ_name, organ_data in data.get("organs", {}).items():
        if isinstance(organ_data, dict):
            for tool_item in organ_data.get("tools", []):
                if isinstance(tool_item, dict):
                    entries.append(
                        ToolCatalogEntry(
                            name=tool_item.get("name", ""),
                            description=tool_item.get("description", ""),
                            capability_tags=tool_item.get("capability_tags", []),
                            organ=organ_name,
                            implemented=tool_item.get("implemented", True),
                            modes=tool_item.get("modes"),
                            parameters=tool_item.get("parameters", []),
                        )
                    )

    return entries


def _fallback_catalog() -> list[ToolCatalogEntry]:
    """Hardcoded minimal catalog when no registry files are available."""
    return [
        # arifOS canonical tools
        ToolCatalogEntry(
            name="arif_init",
            description="Initialize governed session — constitutional bootstrap, identity binding, floor activation",
            capability_tags=["session", "bootstrap", "init", "constitutional"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_observe",
            description="Observe reality — web search, hybrid discovery, system state, vitals",
            capability_tags=["observe", "search", "discovery", "read-only"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_think",
            description="Multi-step reasoning, plan generation, refactor planning, cross-domain analysis",
            capability_tags=["reasoning", "planning", "analysis"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_route",
            description="Route intent to correct federation organ — classifies earth/capital/human/governance/execution",
            capability_tags=["routing", "intent", "organ-bridge"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_judge",
            description="Constitutional verdict — SEAL/SABAR/HOLD/VOID against F1-F13 floors",
            capability_tags=["judge", "verdict", "constitutional", "seal"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_act",
            description="Execute approved plan — requires SEAL verdict from arif_judge",
            capability_tags=["execute", "forge", "mutation"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_seal",
            description="Seal outcome to VAULT999 immutable audit ledger",
            capability_tags=["seal", "vault", "audit", "immutable"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_resolve_tool",
            description="Resolve tool name or alias to canonical form",
            capability_tags=["discovery", "utility", "read-only"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_vault_query",
            description="Query VAULT999 sealed ledger by claim_id, actor, verdict, time range",
            capability_tags=["vault", "query", "audit"],
            organ="arifOS",
        ),
        ToolCatalogEntry(
            name="arif_conformance_report",
            description="Generate MCP conformance report for federation tools",
            capability_tags=["conformance", "audit", "diagnostic"],
            organ="arifOS",
        ),
        # GEOX tools
        ToolCatalogEntry(
            name="geox_well_ingest",
            description="Load and parse well log data from LAS, SEG-Y, DST, deviation surveys, stratigraphic tops",
            capability_tags=["well", "ingest", "las", "logs", "geoscience"],
            organ="GEOX",
            modes=["las", "segy", "deviation", "tops", "dst", "checkshot", "auto"],
        ),
        ToolCatalogEntry(
            name="geox_well_qc",
            description="Quality-control check for depth consistency, curve completeness, log quality flags, FJIS standards",
            capability_tags=["well", "qc", "quality", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_petrophysics",
            description="Derive petrophysical properties — Archie, Sw, net-pay, PINN models",
            capability_tags=["petrophysics", "well", "physics", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_seismic_ingest",
            description="Load seismic volume data from SEG-Y and other formats",
            capability_tags=["seismic", "ingest", "segy", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_seismic_compute",
            description="Compute seismic attributes, inversion, and forward models",
            capability_tags=["seismic", "compute", "attributes", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_seismic_interpret",
            description="Interpret seismic horizons, faults, and stratigraphic features",
            capability_tags=["seismic", "interpret", "horizons", "faults", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_vision",
            description="Vision-based analysis of seismic sections and geological images",
            capability_tags=["vision", "seismic", "image-analysis", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_subsurface_model",
            description="Joint inversion and subsurface model generation",
            capability_tags=["model", "inversion", "subsurface", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_geomechanics",
            description="Geomechanical analysis — stress, strain, wellbore stability",
            capability_tags=["geomechanics", "stress", "wellbore", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_basin",
            description="Basin analysis and petroleum systems modeling",
            capability_tags=["basin", "petroleum-systems", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_deep_time_state",
            description="Deep time stratigraphic age resolution and ICS chart integration",
            capability_tags=["deep-time", "stratigraphy", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_claim",
            description="Create, validate, and seal geological claims with evidence",
            capability_tags=["claim", "evidence", "geoscience", "governance"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_evidence",
            description="Evidence gathering and validation for geological interpretations",
            capability_tags=["evidence", "validation", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_prospect",
            description="Prospect evaluation — volume, risk, and uncertainty assessment",
            capability_tags=["prospect", "evaluation", "risk", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_doctrine",
            description="GEOX Physics9 doctrine retrieval and constitutional checks",
            capability_tags=["doctrine", "physics", "constitutional", "geoscience"],
            organ="GEOX",
        ),
        ToolCatalogEntry(
            name="geox_sequence",
            description="Sequence stratigraphic interpretation and well correlation",
            capability_tags=["sequence", "stratigraphy", "correlation", "geoscience"],
            organ="GEOX",
        ),
        # WEALTH tools
        ToolCatalogEntry(
            name="wealth_compute_npv",
            description="Compute Net Present Value (NPV) for capital projects",
            capability_tags=["npv", "valuation", "capital", "finance"],
            organ="WEALTH",
        ),
        ToolCatalogEntry(
            name="wealth_compute_emv",
            description="Compute Expected Monetary Value (EMV) under uncertainty",
            capability_tags=["emv", "uncertainty", "valuation", "finance"],
            organ="WEALTH",
        ),
        ToolCatalogEntry(
            name="wealth_evaluate_project",
            description="Full project evaluation — NPV, IRR, EMV, risk scoring",
            capability_tags=["project", "npv", "irr", "evaluation", "finance"],
            organ="WEALTH",
        ),
        ToolCatalogEntry(
            name="wealth_analyze_stock",
            description="Stock analysis — technical indicators, fundamental ratios, sentiment",
            capability_tags=["stock", "analysis", "technical", "fundamental", "finance"],
            organ="WEALTH",
        ),
        ToolCatalogEntry(
            name="wealth_risk_assess",
            description="Capital risk assessment — portfolio, project, market risk",
            capability_tags=["risk", "portfolio", "capital", "finance"],
            organ="WEALTH",
        ),
        # WELL tools
        ToolCatalogEntry(
            name="well_assess_homeostasis",
            description="Assess human operator homeostasis state — sleep, stress, fatigue",
            capability_tags=["homeostasis", "sleep", "stress", "vitality"],
            organ="WELL",
        ),
        ToolCatalogEntry(
            name="well_guard_dignity",
            description="Dignity guard — ensure interactions preserve human dignity",
            capability_tags=["dignity", "guard", "human", "ethics"],
            organ="WELL",
        ),
        ToolCatalogEntry(
            name="well_health_check",
            description="Health check — vitality guard system status",
            capability_tags=["health", "check", "vitality"],
            organ="WELL",
        ),
        ToolCatalogEntry(
            name="well_classify_substrate",
            description="Classify human substrate state from biometric signals",
            capability_tags=["substrate", "classify", "biometric", "vitality"],
            organ="WELL",
        ),
        # A-FORGE tools
        ToolCatalogEntry(
            name="forge_plan",
            description="Generate engineering plan with dry-run simulation",
            capability_tags=["plan", "dry-run", "engineering", "forge"],
            organ="A-FORGE",
        ),
        ToolCatalogEntry(
            name="forge_execute",
            description="Execute approved engineering plan — requires SEAL verdict",
            capability_tags=["execute", "forge", "mutation", "engineering"],
            organ="A-FORGE",
        ),
        ToolCatalogEntry(
            name="forge_rollback",
            description="Rollback a previously executed forge plan",
            capability_tags=["rollback", "undo", "engineering"],
            organ="A-FORGE",
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# THE TOOL — arif_retrieve_tools
# ═══════════════════════════════════════════════════════════════════════════════


def get_bm25_engine(refresh: bool = False) -> BM25Engine:
    """Get or build the BM25 index from the federation tool catalog."""
    global _bm25_cache

    if _bm25_cache is not None and not refresh:
        return _bm25_cache

    catalog = load_tool_catalog(refresh=refresh)
    documents = [_flatten_tool(tool) for tool in catalog.tools]
    engine = BM25Engine(k1=K1, b=B)
    engine.index(documents)
    _bm25_cache = engine
    return engine


def retrieve_tools(
    query: str,
    organ: str | None = None,
    top_k: int = 5,
    include_scores: bool = True,
) -> RetrieveToolsOutput:
    """Retrieve top-K tools by BM25 lexical match against the query.

    This is a pure function — no side effects, no mutation, no SEAL.

    Args:
        query: Natural language intent to match against tools.
        organ: Restrict to this organ, or None for cross-organ.
        top_k: Number of top tools to return (1-20).
        include_scores: Include BM25 scores in output.

    Returns:
        RetrieveToolsOutput with ranked results and epistemic disclaimer.
    """
    engine = get_bm25_engine()
    catalog = load_tool_catalog()

    # Filter by organ if specified
    if organ:
        # Map organ aliases
        organ_map = {
            "arifos": "arifOS",
            "geox": "GEOX",
            "wealth": "WEALTH",
            "well": "WELL",
            "a-forge": "A-FORGE",
            "aforge": "A-FORGE",
        }
        canonical_organ = organ_map.get(organ.lower(), organ)

        # Build organ-filtered index
        organ_docs = [d for d, t in zip(engine._documents, catalog.tools) if t.organ == canonical_organ]
        if not organ_docs:
            return RetrieveToolsOutput(
                query=query,
                organ_filter=organ,
                total_tools_indexed=engine.document_count,
                results=[],
                epistemic_note=(
                    f"No tools found for organ '{organ}'. "
                    "BM25 lexical match. Scores measure TERM FREQUENCY overlap, not semantic relevance."
                ),
            )

        # Build temporary organ-specific BM25
        organ_engine = BM25Engine(k1=K1, b=B)
        organ_engine.index(organ_docs)
        ranked = organ_engine.search(query, top_k=top_k)
        # Map back to original catalog indices
        doc_map = {i: engine._documents.index(d) for i, d in enumerate(organ_docs)}
        ranked = [(doc_map[idx], score) for idx, score in ranked]
        total_indexed = len(organ_docs)
    else:
        ranked = engine.search(query, top_k=top_k)
        total_indexed = engine.document_count

    # Build results
    results: list[RetrievedTool] = []
    for rank, (doc_idx, score) in enumerate(ranked, start=1):
        doc = engine._documents[doc_idx]
        tool = catalog.tools[doc_idx]

        # Extract a relevant snippet from the searchable text
        snippet = _extract_snippet(doc.searchable_text, query, max_chars=200)

        results.append(
            RetrievedTool(
                rank=rank,
                tool_name=doc.name,
                organ=doc.organ,
                domain=doc.domain,
                bm25_score=round(score, 4) if include_scores else 0.0,
                description=doc.description,
                snippet=snippet,
                parameters=doc.parameters[:5],  # first 5 params
                capability_tags=doc.capability_tags,
            )
        )

    return RetrieveToolsOutput(
        query=query,
        organ_filter=organ,
        total_tools_indexed=total_indexed,
        results=results,
    )


def _extract_snippet(text: str, query: str, max_chars: int = 200) -> str:
    """Extract the most relevant snippet from text matching query tokens."""
    query_tokens = set(re.findall(r"[a-z0-9_]+", query.lower()))
    if not query_tokens:
        return text[:max_chars]

    # Find the first match position for any query token
    text_lower = text.lower()
    best_pos = len(text)
    for token in query_tokens:
        if len(token) >= 2:
            pos = text_lower.find(token)
            if pos >= 0 and pos < best_pos:
                best_pos = pos

    if best_pos >= len(text):
        return text[:max_chars]

    # Expand to show context around the match
    start = max(0, best_pos - 60)
    end = min(len(text), best_pos + max_chars - 60)
    snippet = text[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


# ═══════════════════════════════════════════════════════════════════════════════
# FastMCP TOOL HANDLER — registered in arifosmcp/tools/__init__.py
# ═══════════════════════════════════════════════════════════════════════════════


async def arif_retrieve_tools(
    query: str,
    organ: str | None = None,
    top_k: int = 5,
    include_scores: bool = True,
    _envelope: Any = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """BM25 lexical tool retrieval across the arifOS federation tool catalog.

    Ratel-proven: BM25 beats semantic embeddings for tool selection because
    tool descriptions are short, keyword-shaped, and structurally similar.
    This is the read-only retrieval primitive — pair with arif_route for
    intent → organ → BM25 rank → select → arif_judge gate → execute.

    CONSTITUTIONAL:
      F1 AMANAH: Read-only. No mutation. Reversible by definition.
      F2 TRUTH: BM25 scores are term-frequency lexical match, NOT confidence.
                Never claim "best match." These are hints, not verdicts.
      F7 HUMILITY: Scores are NOT semantic relevance. They measure keyword overlap.
      F9 ANTIHANTU: Only indexed, registered tools returned. No hallucinations.

    Args:
        query: Natural language intent. E.g. "load well logs from LAS file"
        organ: Restrict to organ (arifOS/GEOX/WEALTH/WELL/A-FORGE). None = cross-organ.
        top_k: Number of top results (1-20, default 5).
        include_scores: Include BM25 scores in output (default True).
    """
    # Validate with Pydantic
    validated = RetrieveToolsInput(
        query=query,
        organ=organ,
        top_k=top_k,
        include_scores=include_scores,
    )

    # Run retrieval (pure CPU, no I/O after catalog load)
    output = retrieve_tools(
        query=validated.query,
        organ=validated.organ,
        top_k=validated.top_k,
        include_scores=validated.include_scores,
    )

    # Return as dict for MCP transport
    return output.model_dump()


# ═══════════════════════════════════════════════════════════════════════════════
# TEST SUPPORT — direct access for tests without MCP transport
# ═══════════════════════════════════════════════════════════════════════════════


def retrieve_tools_sync(query: str, organ: str | None = None, top_k: int = 5) -> RetrieveToolsOutput:
    """Direct retrieval for testing — no async, no MCP transport."""
    return retrieve_tools(query=query, organ=organ, top_k=top_k)
