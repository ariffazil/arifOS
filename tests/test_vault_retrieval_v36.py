"""
test_vault_retrieval_v36.py - Tests for Vault Retrieval RAG stub (v36Ω).

These tests verify that:
1. RetrievalQuery and RetrievalResult dataclasses work correctly.
2. retrieve_canon_entries() handles empty ledgers gracefully.
3. Type and tag filtering works as expected.
4. Keyword scoring ranks entries appropriately.
5. Limit parameter is respected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from arifos_core.governance.vault_retrieval import (
    RetrievalQuery,
    RetrievalResult,
    retrieve_canon_entries,
    _entry_text_blob,
    _entry_tags,
    _simple_keyword_score,
    _matches_types,
    _matches_tags,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_ledger(tmp_path: Path) -> Path:
    """Return path to a temporary ledger file (does not exist yet)."""
    return tmp_path / "L1_cooling_ledger.jsonl"


@pytest.fixture
def sample_entries() -> List[Dict[str, Any]]:
    """Sample ledger entries for testing."""
    return [
        {
            "id": "EUREKA_001",
            "type": "999_SEAL",
            "source": "human",
            "timestamp": "2025-12-01T00:00:00Z",
            "canon": {
                "principle": "Correct is not complete",
                "law": "Maruah protection",
                "checks": ["verify_dignity", "check_completeness"],
                "tags": ["maruah", "dignity"],
            },
            "hash": "abc123",
            "previous_hash": "GENESIS",
        },
        {
            "id": "ZKPC_001",
            "type": "zkpc_receipt",
            "source": "zkpc_runtime",
            "timestamp": "2025-12-02T00:00:00Z",
            "receipt": {
                "verdict": "SEAL",
                "care_scope": {
                    "stakeholders": ["user", "community"],
                    "ethical_risks": ["high_stakes"],
                    "entropy_sources": [],
                },
                "metrics": {
                    "truth": 0.99,
                    "delta_s": 0.1,
                    "amanah": "LOCK",
                },
            },
            "hash": "def456",
            "previous_hash": "abc123",
        },
        {
            "id": "EUREKA_002",
            "type": "999_SEAL",
            "source": "human",
            "timestamp": "2025-12-03T00:00:00Z",
            "canon": {
                "principle": "Truth before comfort",
                "law": "Amanah enforcement",
                "checks": ["verify_truth"],
                "tags": ["truth", "amanah"],
            },
            "hash": "ghi789",
            "previous_hash": "def456",
        },
    ]


def write_ledger(path: Path, entries: List[Dict[str, Any]]) -> None:
    """Write entries to a JSONL file."""
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, sort_keys=True) + "\n")


# =============================================================================
# Tests: Helper Functions
# =============================================================================


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_entry_text_blob_extracts_canon_fields(self, sample_entries: List[Dict[str, Any]]):
        """_entry_text_blob should extract canon principle, law, and checks."""
        entry = sample_entries[0]  # EUREKA_001
        blob = _entry_text_blob(entry)

        assert "correct is not complete" in blob
        assert "maruah protection" in blob
        assert "verify_dignity" in blob
        assert "999_seal" in blob

    def test_entry_text_blob_extracts_receipt_fields(self, sample_entries: List[Dict[str, Any]]):
        """_entry_text_blob should extract receipt verdict and care_scope."""
        entry = sample_entries[1]  # ZKPC_001
        blob = _entry_text_blob(entry)

        assert "seal" in blob
        assert "user" in blob
        assert "high_stakes" in blob
        assert "truth" in blob  # from metrics keys

    def test_entry_tags_from_canon(self, sample_entries: List[Dict[str, Any]]):
        """_entry_tags should extract tags from canon.tags."""
        entry = sample_entries[0]
        tags = _entry_tags(entry)

        assert "maruah" in tags
        assert "dignity" in tags

    def test_entry_tags_from_top_level(self):
        """_entry_tags should extract tags from top-level tags field."""
        entry = {"id": "test", "tags": ["foo", "bar"]}
        tags = _entry_tags(entry)

        assert "foo" in tags
        assert "bar" in tags

    def test_simple_keyword_score_counts_matches(self):
        """_simple_keyword_score should count token overlaps."""
        blob = "this is a test about maruah and dignity protection"
        query = "maruah dignity"
        score = _simple_keyword_score(blob, query)

        assert score == 2  # both "maruah" and "dignity" appear

    def test_simple_keyword_score_empty_query(self):
        """_simple_keyword_score should return 0 for empty query."""
        blob = "some text"
        assert _simple_keyword_score(blob, "") == 0
        assert _simple_keyword_score(blob, "   ") == 0

    def test_matches_types_with_match(self, sample_entries: List[Dict[str, Any]]):
        """_matches_types should return True when type matches."""
        entry = sample_entries[0]
        assert _matches_types(entry, ["999_SEAL"]) is True
        assert _matches_types(entry, ["999_SEAL", "zkpc_receipt"]) is True

    def test_matches_types_no_match(self, sample_entries: List[Dict[str, Any]]):
        """_matches_types should return False when type doesn't match."""
        entry = sample_entries[0]
        assert _matches_types(entry, ["zkpc_receipt"]) is False

    def test_matches_types_none_allows_all(self, sample_entries: List[Dict[str, Any]]):
        """_matches_types should return True when types is None."""
        entry = sample_entries[0]
        assert _matches_types(entry, None) is True

    def test_matches_tags_with_match(self, sample_entries: List[Dict[str, Any]]):
        """_matches_tags should return True when tags intersect."""
        entry = sample_entries[0]
        assert _matches_tags(entry, ["maruah"]) is True
        assert _matches_tags(entry, ["dignity", "other"]) is True

    def test_matches_tags_no_match(self, sample_entries: List[Dict[str, Any]]):
        """_matches_tags should return False when no tags intersect."""
        entry = sample_entries[0]
        assert _matches_tags(entry, ["nonexistent"]) is False

    def test_matches_tags_none_allows_all(self, sample_entries: List[Dict[str, Any]]):
        """_matches_tags should return True when tags is None."""
        entry = sample_entries[0]
        assert _matches_tags(entry, None) is True


# =============================================================================
# Tests: retrieve_canon_entries
# =============================================================================


class TestRetrieveCanonEntries:
    """Tests for the main retrieve_canon_entries function."""

    def test_empty_ledger_returns_empty_result(self, tmp_ledger: Path):
        """Should return empty entries when ledger doesn't exist."""
        query = RetrievalQuery(text="test query")
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert result.entries == []
        assert result.debug_info["total_entries"] == 0

    def test_retrieves_all_entries_without_filters(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should return all entries when no type/tag filters."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(text="", limit=10)
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert len(result.entries) == 3
        assert result.debug_info["total_entries"] == 3

    def test_filters_by_type(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should filter entries by type."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(text="", types=["999_SEAL"], limit=10)
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert len(result.entries) == 2
        for entry in result.entries:
            assert entry["type"] == "999_SEAL"

    def test_filters_by_tags(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should filter entries by tags."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(text="", tags=["maruah"], limit=10)
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert len(result.entries) == 1
        assert result.entries[0]["id"] == "EUREKA_001"

    def test_ranks_by_keyword_score(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should rank entries by keyword match score."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(text="maruah dignity protection", limit=10)
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        # EUREKA_001 should rank highest (has maruah, dignity, protection)
        assert result.entries[0]["id"] == "EUREKA_001"

    def test_respects_limit(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should respect the limit parameter."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(text="", limit=2)
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert len(result.entries) == 2
        assert result.debug_info["returned"] == 2

    def test_debug_info_contains_query_details(
        self, tmp_ledger: Path, sample_entries: List[Dict[str, Any]]
    ):
        """Should include query details in debug_info."""
        write_ledger(tmp_ledger, sample_entries)
        query = RetrievalQuery(
            text="test",
            types=["999_SEAL"],
            tags=["maruah"],
            high_stakes=True,
            limit=5,
        )
        result = retrieve_canon_entries(query, ledger_path=tmp_ledger)

        assert result.debug_info["query"]["text"] == "test"
        assert result.debug_info["query"]["types"] == ["999_SEAL"]
        assert result.debug_info["query"]["tags"] == ["maruah"]
        assert result.debug_info["query"]["high_stakes"] is True
        assert result.debug_info["query"]["limit"] == 5


# =============================================================================
# Tests: RetrievalQuery and RetrievalResult dataclasses
# =============================================================================


class TestDataclasses:
    """Tests for RetrievalQuery and RetrievalResult dataclasses."""

    def test_retrieval_query_defaults(self):
        """RetrievalQuery should have sensible defaults."""
        query = RetrievalQuery(text="test")

        assert query.text == "test"
        assert query.types is None
        assert query.tags is None
        assert query.high_stakes is False
        assert query.limit == 10
        assert query.meta == {}

    def test_retrieval_result_structure(self):
        """RetrievalResult should hold entries and debug_info."""
        result = RetrievalResult(
            entries=[{"id": "test"}],
            debug_info={"info": "value"},
        )

        assert len(result.entries) == 1
        assert result.entries[0]["id"] == "test"
        assert result.debug_info["info"] == "value"
