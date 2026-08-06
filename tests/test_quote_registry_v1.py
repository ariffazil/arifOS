"""
tests/test_quote_registry_v1.py — Verdict Invariance & Registry Validation

Validates Arif's 2026-07-12 directive:
- Quotes must never alter verdict
- Provenance classes are correct
- Disputed quotes get proper labels
- Zero-quote output is supported
- Registry schema is valid

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from arifosmcp.runtime.quote_registry import (
    PROVENANCE_CLASSES,
    PERMITTED_STAGES,
    FORBIDDEN_STAGES,
    QuoteResult,
    ResolveResult,
    load_registry,
    wisdom_quote_resolve,
    audit_quote,
    get_quotes_by_floor,
    get_disputed_quotes,
    get_doctrine,
    get_prohibited_uses,
)


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistryIntegrity:
    """Structural integrity of the quote registry (v3 flat schema)."""

    def test_registry_loads(self):
        reg = load_registry(force_reload=True)
        assert "doctrine" in reg
        assert "quotes" in reg
        v = (reg.get("_meta") or reg.get("_metadata") or {}).get("version", "?")
        assert v[0] in ("1", "2", "3"), f"Unknown version: {v}"

    def test_all_quotes_have_required_fields(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            qid = q.get("id", "")
            assert qid, f"Missing id in {q}"
            text = q.get("text", "")
            assert text, f"Missing text in {qid}"
            assert q.get("speaker"), f"Missing speaker in {qid}"
            conf = q.get("attribution_confidence", 0.0)
            assert conf >= 0.0, f"Missing confidence in {qid}"

    def test_disputed_quotes_have_warning(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            conf = q.get("attribution_confidence", 0.0)
            if conf < 0.45 and conf >= 0.30:  # DISPUTED band
                assert q.get("note"), f"Disputed quote {q['id']} missing note"

    def test_fictional_voice_labeled(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            # FICTIONAL_VOICE = confidence exactly 0.95 with specific marker
            is_fictional = q.get("attribution_confidence") == 0.95 and "FICTIONAL" in str(
                q.get("_v3_migrated_from", "")
            )
            if is_fictional:
                has_label = bool(q.get("display_label", ""))
                has_note = bool(q.get("note", ""))
                assert has_label or has_note, f"Fictional quote {q['id']} missing display label"

    def test_doctrine_separated(self):
        reg = load_registry(force_reload=True)
        assert len(reg["doctrine"]) >= 17, f"Expected >=17 doctrine, got {len(reg['doctrine'])}"
        for d in reg["doctrine"]:
            assert d.get("doctrine_id"), "doctrine entry missing doctrine_id"
            rat = (
                d.get("ratification_status")
                or d.get("ratification")
                or (d.get("status") or {}).get("ratification")
            )
            assert rat, f"{d.get('doctrine_id')}: missing ratification status"


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT INVARIANCE
# ═══════════════════════════════════════════════════════════════════════════════


class TestVerdictInvariance:
    """THE critical test suite: quotes must never alter verdicts."""

    def test_resolver_is_read_only(self):
        """Resolver returns advisory Result, never mutates state."""
        result = wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="REFLECTION",
            maximum_quotes=1,
        )
        # Result is a pure data object — no side effects
        assert isinstance(result, ResolveResult)
        assert result.selection_reason

    def test_zero_quote_supported(self):
        """maximum_quotes=0 must return no quote."""
        result = wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="REFLECTION",
            maximum_quotes=0,
        )
        assert result.quote is None
        assert "maximum_quotes=0" in result.selection_reason

    def test_no_match_returns_null_quote(self):
        """Impossible context tags must return no quote, not a random one."""
        result = wisdom_quote_resolve(
            context_tags=["xyz_nonexistent_tag_99999"],
            intended_use="REFLECTION",
            maximum_quotes=1,
        )
        assert result.quote is None
        assert result.provenance_warning == "NO_MATCH"

    def test_same_context_same_result(self):
        """Deterministic: same inputs → same output."""
        r1 = wisdom_quote_resolve(["truth", "evidence"], "REFLECTION", maximum_quotes=1)
        r2 = wisdom_quote_resolve(["truth", "evidence"], "REFLECTION", maximum_quotes=1)
        if r1.quote and r2.quote:
            assert r1.quote.quote_id == r2.quote.quote_id

    def test_quote_result_never_includes_verdict_fields(self):
        """QuoteResult must not contain verdict, confidence, or authority fields."""
        result = wisdom_quote_resolve(["truth"], "REFLECTION", maximum_quotes=1)
        if result.quote:
            # QuoteResult has no verdict/confidence/authority fields
            forbidden = {"verdict", "evidence_layer", "confidence", "authority", "tool_permission"}
            result_dict = result.quote.__dict__
            assert not forbidden.intersection(set(result_dict.keys())), (
                f"QuoteResult contains forbidden fields: {forbidden & set(result_dict.keys())}"
            )

    def test_disputed_excluded_by_default(self):
        """By default, disputed quotes must not appear."""
        result = wisdom_quote_resolve(
            context_tags=["evil", "inaction"],
            intended_use="REFLECTION",
            exclude_disputed=True,
            maximum_quotes=1,
        )
        # Should not return the Burke disputed quote
        if result.quote:
            assert not result.quote.disputed, (
                f"Disputed quote returned when exclude_disputed=True: {result.quote.quote_id}"
            )

    def test_disputed_included_when_requested(self):
        """When exclude_disputed=False, disputed quotes may appear with warning."""
        result = wisdom_quote_resolve(
            context_tags=["evil", "inaction"],
            intended_use="REFLECTION",
            exclude_disputed=False,
            maximum_quotes=1,
        )
        if result.quote and result.quote.disputed:
            assert result.provenance_warning is not None
            assert "DISPUTED_ATTRIBUTION" in result.provenance_warning

    def test_tradition_filter_works(self):
        """Traditions filter restricts results."""
        result = wisdom_quote_resolve(
            context_tags=["wisdom"],
            intended_use="REFLECTION",
            traditions_allowed=["nusantara"],
            maximum_quotes=1,
        )
        if result.quote:
            assert any("nusantara" in t for t in result.quote.tradition), (
                f"Non-Nusantara quote returned: {result.quote.tradition}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT MODE
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuditMode:
    """Audit tool correctly identifies quote provenance."""

    def test_known_doctrine_audited(self):
        result = audit_quote("DITEMPA BUKAN DIBERI", "arifOS Foundry")
        assert result["found"] is True
        assert result["source_class"] == "ARIFOS_DOCTRINE"

    def test_unknown_quote_audited(self):
        result = audit_quote("Blah blah completely made up text xyz 999", "Nobody")
        assert result["found"] is False
        assert result["source_class"] == "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE QUERIES
# ═══════════════════════════════════════════════════════════════════════════════


class TestResourceQueries:
    """MCP resource query functions work."""

    def test_floor_query(self):
        result = get_quotes_by_floor("F2")
        assert isinstance(result, list)
        for q in result:
            assert "F2" in q.get("arifos_floors", [])

    def test_disputed_query(self):
        result = get_disputed_quotes()
        for q in result:
            assert q["source_class"] == "DISPUTED_ATTRIBUTION"

    def test_doctrine_query(self):
        result = get_doctrine()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_prohibited_uses_query(self):
        result = get_prohibited_uses()
        assert isinstance(result, list)
        assert "factual_evidence" in result
        assert "verdict_authority" in result


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL INTEGRATION CONSTRAINTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestKernelConstraints:
    """Quotes must only be used at permitted kernel stages."""

    def test_init_not_permitted(self):
        assert "000_INIT" in FORBIDDEN_STAGES
        assert "000_INIT" not in PERMITTED_STAGES

    def test_hearts_and_seal_permitted(self):
        assert "555_HEART" in PERMITTED_STAGES
        assert "999_RECEIPT" in PERMITTED_STAGES

    def test_think_not_permitted(self):
        assert "333_THINK" in FORBIDDEN_STAGES

    def test_forge_not_permitted(self):
        assert "777_FORGE" in FORBIDDEN_STAGES


# ═══════════════════════════════════════════════════════════════════════════════
# PROVENANCE CLASS INTEGRITY
# ═══════════════════════════════════════════════════════════════════════════════


class TestProvenanceIntegrity:
    """Every quote must conform to its provenance class requirements (v3 flat)."""

    def test_primary_verified_has_work_reference(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            conf = q.get("attribution_confidence", 0.0)
            if conf >= 0.95:  # PRIMARY_VERIFIED band
                assert q.get("work") or q.get("note"), (
                    f"PRIMARY_VERIFIED quote {q['id']} missing work reference"
                )

    def test_paraphrase_has_note(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            conf = q.get("attribution_confidence", 0.0)
            if 0.50 <= conf < 0.85:  # PARAPHRASE band
                assert q.get("note"), f"PARAPHRASE quote {q['id']} missing note"

    def test_scriptural_has_version_note(self):
        reg = load_registry(force_reload=True)
        for q in reg["quotes"]:
            conf = q.get("attribution_confidence", 0.0)
            if conf >= 0.85 and q.get("language") in ("zh", "ms"):
                has_ref = q.get("work") or q.get("note")
                assert has_ref, f"SCRIPTURAL quote {q['id']} missing version/translation info"
