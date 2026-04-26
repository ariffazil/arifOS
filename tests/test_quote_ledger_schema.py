"""
tests/test_quote_ledger_schema.py — Quote ledger schema and integrity tests.

Acceptance: All 99 quotes validate; malformed entries are rejected.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.runtime.quote_ledger import (
    assert_quote_integrity,
    get_quote_by_id,
    load_quote_ledger,
    validate_quote_schema,
    QuoteSchemaError,
)

LEDGER_PATH = Path(__file__).resolve().parents[1] / "arifosmcp" / "data" / "wisdom_quotes_99.json"


class TestLoadLedger:
    def test_loads_lite_ledger(self):
        ledger = load_quote_ledger()
        assert len(ledger) == 20

    def test_all_entries_have_required_fields(self):
        ledger = load_quote_ledger()
        required = {
            "id", "quote", "author", "tradition", "domain", "theme",
            "trigger_conditions", "arifos_mapping", "action_bias",
            "risk_use", "source_status", "allow_use",
        }
        for q in ledger:
            missing = required - set(q.keys())
            assert not missing, f"Quote {q.get('id')} missing {missing}"

    def test_action_bias_values_are_canonical(self):
        ledger = load_quote_ledger()
        valid = {"pause_and_reflect", "request_approval", "proceed_carefully", "refuse", "hold"}
        for q in ledger:
            assert q["action_bias"] in valid, f"Quote {q['id']} has bad action_bias: {q['action_bias']}"

    def test_source_status_values_are_canonical(self):
        ledger = load_quote_ledger()
        valid = {"verified", "public_domain", "curated", "uncertain"}
        for q in ledger:
            assert q["source_status"] in valid, f"Quote {q['id']} has bad source_status: {q['source_status']}"

    def test_no_uncertain_quotes_are_allowed(self):
        ledger = load_quote_ledger()
        for q in ledger:
            if q["source_status"] == "uncertain":
                assert q["allow_use"] is False, f"Uncertain quote {q['id']} must have allow_use=false"

    def test_risk_use_contains_only_valid_levels(self):
        ledger = load_quote_ledger()
        valid = {"low", "medium", "high", "critical", "irreversible"}
        for q in ledger:
            bad = set(q["risk_use"]) - valid
            assert not bad, f"Quote {q['id']} has invalid risk_use: {bad}"


class TestValidateQuoteSchema:
    def test_valid_quote_passes(self):
        q = {
            "id": "TEST_001",
            "quote": "Test quote.",
            "author": "Test Author",
            "tradition": "Test",
            "domain": ["ethics"],
            "theme": "testing",
            "trigger_conditions": ["test trigger"],
            "arifos_mapping": {"physics": "p", "math": "m", "linguistic": "l"},
            "action_bias": "pause_and_reflect",
            "risk_use": ["low"],
            "source_status": "curated",
            "allow_use": True,
        }
        validate_quote_schema(q)  # should not raise

    def test_missing_field_raises(self):
        q = {"id": "TEST_002", "quote": "x", "author": "A"}
        with pytest.raises(QuoteSchemaError):
            validate_quote_schema(q)

    def test_invalid_action_bias_raises(self):
        q = {
            "id": "TEST_003",
            "quote": "x",
            "author": "A",
            "tradition": "T",
            "domain": ["ethics"],
            "theme": "t",
            "trigger_conditions": ["c"],
            "arifos_mapping": {"physics": "p", "math": "m", "linguistic": "l"},
            "action_bias": "do_whatever",
            "risk_use": ["low"],
            "source_status": "curated",
            "allow_use": True,
        }
        with pytest.raises(QuoteSchemaError):
            validate_quote_schema(q)


class TestGetQuoteById:
    def test_existing_id_returns_quote(self):
        ledger = load_quote_ledger()
        q = get_quote_by_id(ledger[0]["id"])
        assert q is not None
        assert q["id"] == ledger[0]["id"]

    def test_missing_id_returns_none(self):
        assert get_quote_by_id("NONEXISTENT_999") is None


class TestAssertQuoteIntegrity:
    def test_exact_match_ok(self):
        ledger = load_quote_ledger()
        original = ledger[0]
        candidate = {
            "id": original["id"],
            "quote": original["quote"],
            "author": original["author"],
        }
        result = assert_quote_integrity(candidate, ledger_quote=original)
        assert result["ok"] is True
        assert result["error"] is None

    def test_mutated_quote_fails(self):
        ledger = load_quote_ledger()
        original = ledger[0]
        candidate = {
            "id": original["id"],
            "quote": original["quote"] + " EXTRA",
            "author": original["author"],
        }
        result = assert_quote_integrity(candidate, ledger_quote=original)
        assert result["ok"] is False
        assert result["error"] == "quote_integrity_failed"

    def test_mutated_author_fails(self):
        ledger = load_quote_ledger()
        original = ledger[0]
        candidate = {
            "id": original["id"],
            "quote": original["quote"],
            "author": "Fake Author",
        }
        result = assert_quote_integrity(candidate, ledger_quote=original)
        assert result["ok"] is False
        assert result["error"] == "author_integrity_failed"

    def test_disallowed_quote_fails(self):
        original = {
            "id": "TEST_004",
            "quote": "x",
            "author": "A",
            "allow_use": False,
            "source_status": "curated",
        }
        candidate = {"id": "TEST_004", "quote": "x", "author": "A"}
        result = assert_quote_integrity(candidate, ledger_quote=original)
        assert result["ok"] is False
        assert result["error"] == "quote_not_approved_for_use"

    def test_uncertain_quote_fails(self):
        original = {
            "id": "TEST_005",
            "quote": "x",
            "author": "A",
            "allow_use": True,
            "source_status": "uncertain",
        }
        candidate = {"id": "TEST_005", "quote": "x", "author": "A"}
        result = assert_quote_integrity(candidate, ledger_quote=original)
        assert result["ok"] is False
        assert result["error"] == "quote_source_uncertain"
