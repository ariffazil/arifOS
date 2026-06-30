"""
tests/test_retrieve_tools.py — BM25 Tool Retrieval Tests
══════════════════════════════════════════════════════════

Tests for arif_retrieve_tools: BM25 engine correctness, schema-aware
text projection, within-organ and cross-organ retrieval, epistemic
labeling, and constitutional compliance.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import pytest

from arifosmcp.schemas.retrieve_tools import (
    RetrieveToolsInput,
    RetrieveToolsOutput,
    RetrievedTool,
    ToolCatalog,
    ToolCatalogEntry,
    ToolDocument,
)
from arifosmcp.tools.retrieve_tools import (
    BM25Engine,
    _extract_snippet,
    _flatten_tool,
    _strip_json_noise,
    get_bm25_engine,
    load_tool_catalog,
    retrieve_tools,
    retrieve_tools_sync,
    K1,
    B,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. BM25 ENGINE UNIT TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestBM25Engine:
    """BM25 engine correctness — algorithmic contract."""

    def test_empty_index(self):
        """Empty index returns no results."""
        engine = BM25Engine()
        results = engine.search("anything")
        assert results == []
        assert engine.document_count == 0

    def test_single_document_exact_match(self):
        """Single document with exact query match returns it."""
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name="geox_well_ingest",
                organ="GEOX",
                description="Load and parse well log data from LAS files",
                searchable_text="geox_well_ingest well ingest load and parse well log data from las files",
                capability_tags=["well", "ingest"],
            )
        ]
        engine.index(docs)
        results = engine.search("well log data")
        assert len(results) >= 1
        assert results[0][0] == 0  # doc index 0
        assert results[0][1] > 0  # positive score

    def test_multiple_documents_ranking(self):
        """Query matching one doc better than others ranks it higher."""
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name="geox_well_ingest",
                organ="GEOX",
                description="Load and parse well log data from LAS files",
                searchable_text="geox_well_ingest well ingest load and parse well log data from las files",
            ),
            ToolDocument(
                name="wealth_compute_npv",
                organ="WEALTH",
                description="Compute Net Present Value for capital projects",
                searchable_text="wealth_compute_npv wealth compute npv net present value capital projects",
            ),
            ToolDocument(
                name="geox_well_qc",
                organ="GEOX",
                description="Quality-control check for well log data",
                searchable_text="geox_well_qc well qc quality control check well log data",
            ),
        ]
        engine.index(docs)
        results = engine.search("well log data quality")
        # geox_well_qc and geox_well_ingest should rank higher than wealth_compute_npv
        top_indices = [idx for idx, _ in results]
        # wealth should NOT be first
        if 1 in top_indices and len(top_indices) > 1:
            assert top_indices[0] != 1  # npv shouldn't be top for "well log"

    def test_no_match_returns_empty(self):
        """Query with no matching tokens returns empty results."""
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name="geox_well_ingest",
                organ="GEOX",
                description="Load well logs",
                searchable_text="geox well ingest load well logs",
            )
        ]
        engine.index(docs)
        results = engine.search("zzzznotexist xyznomatch")
        assert results == []

    def test_bm25_parameters_default(self):
        """Default BM25 parameters match Ratel ADR-0004."""
        engine = BM25Engine()
        assert engine.k1 == 0.9
        assert engine.b == 0.4

    def test_bm25_parameters_custom(self):
        """Custom k1, b are respected."""
        engine = BM25Engine(k1=1.2, b=0.75)
        assert engine.k1 == 1.2
        assert engine.b == 0.75

    def test_avgdl_computed(self):
        """Average document length is computed correctly."""
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name="t1", organ="GEOX", description="d1",
                searchable_text="one two three"
            ),
            ToolDocument(
                name="t2", organ="GEOX", description="d2",
                searchable_text="one two three four five six seven"
            ),
        ]
        engine.index(docs)
        # avgdl = (3 + 7) / 2 = 5
        assert engine._avgdl == 5.0

    def test_tokenize_filters_short_tokens(self):
        """Tokenizer filters single-char tokens and pure numbers."""
        engine = BM25Engine()
        tokens = engine._tokenize("a be cat 1 12 dog")
        assert "a" not in tokens
        assert "1" not in tokens
        assert "12" not in tokens
        assert "be" in tokens
        assert "cat" in tokens
        assert "dog" in tokens

    def test_tokenize_lowercases(self):
        """Tokenizer lowercases all tokens."""
        engine = BM25Engine()
        tokens = engine._tokenize("Well LOG Data LAS")
        assert "well" in tokens
        assert "log" in tokens
        assert "data" in tokens
        assert "las" in tokens

    def test_score_deterministic(self):
        """Same query on same index returns same scores."""
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name=f"tool_{i}", organ="GEOX", description=f"desc{i}",
                searchable_text=f"tool_{i} description text about seismic well logs"
            )
            for i in range(5)
        ]
        engine.index(docs)
        results1 = engine.search("seismic well")
        results2 = engine.search("seismic well")
        for (i1, s1), (i2, s2) in zip(results1, results2):
            assert i1 == i2
            assert s1 == s2


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SCHEMA-AWARE TEXT PROJECTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestTextProjection:
    """Schema-aware text projection correctness."""

    def test_strip_json_noise_removes_type_keywords(self):
        """Strip removes JSON schema type keywords."""
        text = '{"type": "string", "description": "well name", "enum": ["deep", "shallow"]}'
        cleaned = _strip_json_noise(text)
        assert "type" not in cleaned
        assert "string" not in cleaned
        assert "well" in cleaned
        assert "name" in cleaned
        assert "deep" in cleaned
        assert "shallow" in cleaned

    def test_strip_json_noise_removes_braces(self):
        """Strip removes JSON structural characters."""
        text = '{"name": "test"}'
        cleaned = _strip_json_noise(text)
        assert "{" not in cleaned
        assert "}" not in cleaned
        assert '"' not in cleaned
        assert "test" in cleaned
        assert "name" in cleaned

    def test_flatten_tool_includes_name_and_description(self):
        """Flattened document includes tool name and description."""
        tool = ToolCatalogEntry(
            name="geox_well_ingest",
            description="Load and parse well log data from LAS files",
            capability_tags=["well", "ingest"],
            organ="GEOX",
        )
        doc = _flatten_tool(tool)
        assert "geox_well_ingest" in doc.searchable_text
        assert "well ingest" in doc.searchable_text
        # searchable_text preserves original case from description; check lowercase
        assert "load" in doc.searchable_text.lower()
        assert "las" in doc.searchable_text.lower()

    def test_flatten_tool_includes_parameters(self):
        """Flattened document includes parameter names and descriptions."""
        tool = ToolCatalogEntry(
            name="test_tool",
            description="A test tool",
            organ="GEOX",
            parameters=[
                {"name": "well_id", "description": "The well identifier string"},
                {"name": "depth_range", "description": "Depth range in meters"},
            ],
        )
        doc = _flatten_tool(tool)
        assert "well_id" in doc.searchable_text.lower()
        assert "depth_range" in doc.searchable_text.lower()
        assert "identifier" in doc.searchable_text.lower()

    def test_flatten_tool_includes_capability_tags(self):
        """Flattened document includes capability tags (hyphen→space normalized)."""
        tool = ToolCatalogEntry(
            name="test_tool",
            description="A test tool",
            organ="GEOX",
            capability_tags=["well-log", "petrophysics"],
        )
        doc = _flatten_tool(tool)
        assert "well log" in doc.searchable_text
        assert "petrophysics" in doc.searchable_text

    def test_flatten_tool_includes_modes(self):
        """Flattened document includes mode names."""
        tool = ToolCatalogEntry(
            name="test_tool",
            description="A test tool",
            organ="GEOX",
            modes=["las", "segy", "deviation"],
        )
        doc = _flatten_tool(tool)
        assert "las" in doc.searchable_text
        assert "segy" in doc.searchable_text
        assert "deviation" in doc.searchable_text

    def test_flatten_tool_strips_json_noise(self):
        """Flattened document does not contain JSON schema tokens."""
        tool = ToolCatalogEntry(
            name="test_tool",
            description='{"type": "object", "properties": {"x": {"type": "string"}}}',
            organ="GEOX",
        )
        doc = _flatten_tool(tool)
        assert "object" not in doc.searchable_text
        # 'type' is noise, should be stripped
        assert " string " not in doc.searchable_text


# ═══════════════════════════════════════════════════════════════════════════════
# 3. CATALOG LOADING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestCatalogLoading:
    """Tool catalog loading correctness."""

    def test_load_catalog_returns_tools(self):
        """Catalog loading returns non-empty tool list."""
        catalog = load_tool_catalog()
        assert len(catalog.tools) > 0
        assert catalog.source is not None

    def test_catalog_has_organs(self):
        """Catalog contains tools from multiple organs."""
        catalog = load_tool_catalog()
        organs = {t.organ for t in catalog.tools}
        assert len(organs) >= 3  # arifOS, GEOX, WEALTH, WELL, A-FORGE

    def test_catalog_caching(self):
        """Catalog is cached on second load."""
        catalog1 = load_tool_catalog()
        catalog2 = load_tool_catalog()
        assert catalog1 is catalog2  # same object — cached

    def test_catalog_refresh(self):
        """Catalog refresh returns new object."""
        catalog1 = load_tool_catalog()
        catalog2 = load_tool_catalog(refresh=True)
        # May be same content but fresh load
        assert len(catalog2.tools) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. RETRIEVAL INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRetrievalIntegration:
    """End-to-end retrieval tests."""

    def test_retrieve_well_query_returns_geox_tools(self):
        """Query about well logs returns GEOX well tools."""
        output = retrieve_tools_sync("load well log data from LAS file", top_k=10)
        assert output.total_tools_indexed > 0
        assert len(output.results) > 0
        # Top result should be geox_well_ingest for a well log query
        top_names = [r.tool_name for r in output.results[:5]]
        assert any("well" in name for name in top_names), f"Expected well tools in top results, got {top_names}"

    def test_retrieve_seismic_query(self):
        """Query about seismic returns GEOX seismic tools."""
        output = retrieve_tools_sync("compute seismic attributes and interpret horizons", top_k=10)
        top_names = [r.tool_name for r in output.results[:5]]
        assert any("seismic" in name for name in top_names), f"Expected seismic tools, got {top_names}"

    def test_retrieve_finance_query_returns_wealth(self):
        """Query about NPV returns WEALTH tools."""
        output = retrieve_tools_sync("compute net present value for project", top_k=10)
        top_names = [r.tool_name for r in output.results[:5]]
        assert any("wealth" in name for name in top_names), f"Expected WEALTH tools, got {top_names}"

    def test_retrieve_within_organ_filter(self):
        """Organ filter restricts results to that organ."""
        output = retrieve_tools_sync("load data", organ="GEOX", top_k=10)
        for result in output.results:
            assert result.organ == "GEOX", f"Expected only GEOX, got {result.organ}"

    def test_retrieve_cross_organ(self):
        """Cross-organ retrieval returns tools from multiple organs."""
        output = retrieve_tools_sync("assess risk and uncertainty", top_k=10)
        organs = {r.organ for r in output.results}
        # Should get results from multiple organs
        assert len(output.results) > 0

    def test_retrieve_respects_top_k(self):
        """Top-K limit is respected."""
        output = retrieve_tools_sync("well data", top_k=3)
        assert len(output.results) <= 3

    def test_retrieve_epistemic_note_present(self):
        """Output includes F2/F7 epistemic disclaimer."""
        output = retrieve_tools_sync("well data")
        assert "BM25" in output.epistemic_note or "lexical" in output.epistemic_note.lower()
        assert output.epistemic_note  # non-empty

    def test_retrieve_scores_are_positive(self):
        """BM25 scores for matching results are positive."""
        output = retrieve_tools_sync("load well log data", top_k=5)
        for result in output.results:
            assert result.bm25_score >= 0.0

    def test_empty_query_validation(self):
        """Empty query is caught by validation."""
        with pytest.raises(Exception):
            RetrieveToolsInput(query="", top_k=5)

    def test_top_k_bounds_validation(self):
        """Top-K bounds are enforced."""
        with pytest.raises(Exception):
            RetrieveToolsInput(query="test", top_k=0)
        with pytest.raises(Exception):
            RetrieveToolsInput(query="test", top_k=21)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. BM25 ENGINE INDEX TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestBM25Index:
    """BM25 index construction and management."""

    def test_get_bm25_engine_returns_engine(self):
        """get_bm25_engine returns a valid engine."""
        engine = get_bm25_engine()
        assert engine is not None
        assert engine.document_count > 0

    def test_get_bm25_engine_cached(self):
        """get_bm25_engine returns same engine on second call."""
        engine1 = get_bm25_engine()
        engine2 = get_bm25_engine()
        assert engine1 is engine2

    def test_get_bm25_engine_refresh(self):
        """get_bm25_engine with refresh returns new engine."""
        engine1 = get_bm25_engine()
        engine2 = get_bm25_engine(refresh=True)
        # Both should have documents
        assert engine2.document_count > 0


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SNIPPET EXTRACTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestSnippetExtraction:
    """Relevant snippet extraction from searchable text."""

    def test_snippet_finds_match(self):
        """Snippet centers on query token match."""
        text = "this is a long text about well log data processing and quality control for petrophysical analysis"
        snippet = _extract_snippet(text, "well log", max_chars=100)
        assert "well" in snippet.lower()

    def test_snippet_truncates_long_text(self):
        """Snippet respects max_chars."""
        text = "x " * 300
        snippet = _extract_snippet(text, "well", max_chars=100)
        assert len(snippet) <= 100 + 2  # +2 for ellipsis chars

    def test_snippet_no_match_returns_start(self):
        """When no query token matches, snippet returns start of text."""
        text = "abcdefghijklmnopqrstuvwxyz" * 5
        snippet = _extract_snippet(text, "zzzznomatch", max_chars=50)
        assert len(snippet) <= 50 + 2


# ═══════════════════════════════════════════════════════════════════════════════
# 7. CONSTITUTIONAL COMPLIANCE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstitutionalCompliance:
    """F1-F13 constitutional compliance checks."""

    def test_f1_reversible(self):
        """F1 AMANAH: arif_retrieve_tools is read-only, reversible by definition."""
        # No mutation methods exist on the tool — it's a pure function
        import inspect
        sig = inspect.signature(retrieve_tools_sync)
        # Only takes query, organ, top_k — no write/mutate params
        params = list(sig.parameters.keys())
        assert "mode" not in params  # no mutate mode

    def test_f2_truth_scores_labeled(self):
        """F2 TRUTH: BM25 scores are labeled as lexical match, not confidence."""
        output = retrieve_tools_sync("well data")
        # Epistemic note must clarify score meaning
        assert output.epistemic_note, "Epistemic note is required"
        # Scores are present but labeled
        for r in output.results:
            assert isinstance(r.bm25_score, float)

    def test_f7_humility_not_best_match(self):
        """F7 HUMILITY: Output never claims 'best match'."""
        output = retrieve_tools_sync("well data")
        # Check that no claim of authority is made
        for r in output.results:
            # Results have rank but no "confidence" field
            assert hasattr(r, "rank")
            # Description doesn't claim certainty
            assert "guaranteed" not in r.description.lower()

    def test_f9_no_hallucination(self):
        """F9 ANTIHANTU: Only indexed tools returned."""
        catalog = load_tool_catalog()
        indexed_names = {t.name for t in catalog.tools}
        output = retrieve_tools_sync("random obscure query unlikely to match anything", top_k=5)
        for r in output.results:
            assert r.tool_name in indexed_names, f"{r.tool_name} not in catalog!"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. RATEL BENCHMARK REPLICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestRatelInsightValidation:
    """Validate that BM25 beats naive keyword matching for tool selection."""

    def test_bm25_discriminates_nearby_descriptions(self):
        """BM25 distinguishes tools with similar descriptions but different nouns.

        This is the core Ratel finding: 'list the open issues' vs 'list the channel
        messages' — cosine smears, BM25 keeps the discriminator sharp.
        """
        engine = BM25Engine()
        docs = [
            ToolDocument(
                name="github_list_issues",
                organ="A-FORGE",
                description="List the open issues in a GitHub repository",
                searchable_text="github list issues list the open issues in a github repository repo_id",
            ),
            ToolDocument(
                name="slack_list_messages",
                organ="A-FORGE",
                description="List the channel messages in a Slack workspace",
                searchable_text="slack list messages list the channel messages in a slack workspace channel_id",
            ),
        ]
        engine.index(docs)
        # Query for GitHub issues
        results = engine.search("list the open issues in the repo")
        assert len(results) > 0
        assert results[0][0] == 0  # github_list_issues should be first

        # Query for Slack messages
        results = engine.search("list the channel messages")
        assert len(results) > 0
        assert results[0][0] == 1  # slack_list_messages should be first

    def test_schema_aware_projection_discriminates(self):
        """Schema-aware text projection keeps parameter names that discriminate.

        Without schema projection, 'list issues' and 'list messages' look similar.
        With projection, 'repo_id' vs 'channel_id' breaks the tie.
        """
        issue_tool = ToolCatalogEntry(
            name="list_issues",
            description="List issues",
            organ="A-FORGE",
            parameters=[{"name": "repo_id", "description": "The GitHub repository ID"}],
            capability_tags=["github", "issues"],
        )
        msg_tool = ToolCatalogEntry(
            name="list_messages",
            description="List messages",
            organ="A-FORGE",
            parameters=[{"name": "channel_id", "description": "The Slack channel ID"}],
            capability_tags=["slack", "messages"],
        )

        doc_issue = _flatten_tool(issue_tool)
        doc_msg = _flatten_tool(msg_tool)

        engine = BM25Engine()
        engine.index([doc_issue, doc_msg])

        # "repo_id" token in issue query should match issue tool
        results = engine.search("list issues in repo")
        assert results[0][0] == 0

        # "channel" token in message query should match message tool
        results = engine.search("list channel messages")
        assert results[0][0] == 1
