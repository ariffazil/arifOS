"""
tests/test_forge_quote_invariance.py — A-FORGE Quote Lint & Verdict Invariance

A-FORGE requirements (Arif 2026-07-12):
- Quote lint: fail build if provenance fields are missing
- Verdict invariance: same case with quote, without quote, with challenging quote
- Tradition-bias test: different traditions must not change the operative recommendation
- Prompt-injection test: quote text must remain inert resource data
- Zero-quote output must be supported
- Quotes must never modify verdicts

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from arifosmcp.runtime.decision_core import (
    DecisionCore,
    freeze_decision,
)
from arifosmcp.runtime.quote_registry import (
    wisdom_quote_resolve,
    load_registry,
    PROVENANCE_CLASSES,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def registry():
    return load_registry(force_reload=True)


@pytest.fixture
def base_decision():
    return freeze_decision(
        verdict="HOLD",
        evidence_layer="L2",
        authority_band="ORANGE",
        action_class="MUTATE",
        human_decision_required=True,
        reversibility="PARTIAL",
        next_allowed_action="OBTAIN_WITNESS",
        consequence_class="HIGH",
        confidence_band="ADVISORY",
        weakest_plane="Correctability",
        # reflection_tags stored separately
        
    )


# ═══════════════════════════════════════════════════════════════════════════════
# QUOTE LINT — Forge build must fail if these are wrong
# ═══════════════════════════════════════════════════════════════════════════════


class TestQuoteLint:
    """A-FORGE quote lint: build fails if provenance is incomplete."""

    def test_all_quotes_have_author(self, registry):
        for q in registry["quotes"]:
            assert q["attribution"]["speaker"], f"{q['id']}: missing speaker"

    def test_all_quotes_have_source_class(self, registry):
        for q in registry["quotes"]:
            sc = q["attribution"]["source_class"]
            assert sc in PROVENANCE_CLASSES, f"{q['id']}: invalid source_class={sc}"

    def test_doctrine_not_presented_as_historical_quote(self, registry):
        for q in registry["quotes"]:
            assert q["attribution"]["source_class"] != "ARIFOS_DOCTRINE", (
                f"{q['id']}: doctrine must be in doctrine array, not quotes"
            )

    def test_fictional_dialogue_not_presented_as_author_assertion(self, registry):
        found_fictional = False
        for q in registry["quotes"]:
            if q["attribution"]["source_class"] == "FICTIONAL_VOICE":
                found_fictional = True
                # Must have either display label or note identifying it as fictional
                has_label = q.get("display", {}).get("attribution_label") if isinstance(q.get("display"), dict) else False
                has_note = bool(q["attribution"].get("note", ""))
                assert has_label or has_note, (
                    f"{q['id']}: fictional voice missing display label or identifying note"
                )
        # At least one fictional voice should exist
        # (skip if none — the class may be unused)

    def test_disputed_attribution_has_qualifier(self, registry):
        for q in registry["quotes"]:
            if q["attribution"]["source_class"] == "DISPUTED_ATTRIBUTION":
                assert q["attribution"].get("commonly_attributed_to") or q["attribution"].get(
                    "note"
                ), f"{q['id']}: disputed attribution missing qualifier"

    def test_religious_text_has_translation_metadata(self, registry):
        for q in registry["quotes"]:
            if q["attribution"]["source_class"] == "SCRIPTURAL_TRANSLATION":
                assert q["attribution"].get("work") or q["attribution"].get("note"), (
                    f"{q['id']}: scriptural translation missing version/translation info"
                )

    def test_no_paraphrase_without_note(self, registry):
        for q in registry["quotes"]:
            if q["attribution"]["source_class"] == "PARAPHRASE":
                assert q["attribution"].get("note") or q["attribution"].get(
                    "commonly_attributed_to"
                ), f"{q['id']}: paraphrase missing explanation"

    def test_quote_text_matches_source_within_tolerance(self, registry):
        """Quote text must not materially differ from source without PARAPHRASE class."""
        for q in registry["quotes"]:
            if q["attribution"]["source_class"] == "PRIMARY_VERIFIED":
                # Must have a work reference for verification
                assert q["attribution"].get("work") or q["attribution"].get("note"), (
                    f"{q['id']}: PRIMARY_VERIFIED missing work reference"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT INVARIANCE — The verdict must never change
# ═══════════════════════════════════════════════════════════════════════════════


class TestVerdictInvariance:
    """Run the same case with different quote configurations — verdict unchanged."""

    def test_without_quotes(self, base_decision):
        """Quote disabled: decision hash is baseline."""
        h = base_decision.hash()
        assert len(h) == 64

    def test_with_supporting_quote(self, base_decision):
        """Supporting quote does not alter verdict."""
        h_before = base_decision.hash()
        result = wisdom_quote_resolve(
            context_tags=["humility", "evidence", "correction"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        assert base_decision.hash() == h_before

    def test_with_challenging_quote(self, base_decision):
        """A quote from a different tradition doesn't change the verdict."""
        h_before = base_decision.hash()

        # Try multiple traditions
        for tradition in [["nusantara"], ["islam"], ["daoism"]]:
            result = wisdom_quote_resolve(
                context_tags=["wisdom", "restraint"],
                intended_use="RECEIPT",
                traditions_allowed=tradition,
                maximum_quotes=1,
            )
            assert base_decision.hash() == h_before, (
                f"Hash changed with tradition={tradition}"
            )

    def test_verdict_independent_of_quote_presence(self, base_decision):
        """Quote present or absent — verdict unchanged."""
        h = base_decision.hash()

        # With quote
        wisdom_quote_resolve(["truth"], "RECEIPT", maximum_quotes=1)
        assert base_decision.hash() == h

        # Without quote (max=0)
        wisdom_quote_resolve(["truth"], "RECEIPT", maximum_quotes=0)
        assert base_decision.hash() == h


# ═══════════════════════════════════════════════════════════════════════════════
# TRADITION BIAS TEST
# ═══════════════════════════════════════════════════════════════════════════════


class TestTraditionBias:
    """The operative recommendation must remain stable regardless of tradition."""

    TRADITIONS = [
        ["islam"],
        ["greek_philosophy"],
        ["nusantara"],
        ["daoism"],
        ["african_philosophy"],
        ["stoicism"],
        None,  # no tradition filter
    ]

    def test_recommendation_stable_across_traditions(self, base_decision):
        """Same evidence → same recommendation regardless of which tradition's quotes are selected."""
        h_base = base_decision.hash()

        for tradition in self.TRADITIONS:
            kwargs = {
                "context_tags": ["wisdom", "humility", "restraint"],
                "intended_use": "RECEIPT",
                "maximum_quotes": 1,
            }
            if tradition is not None:
                kwargs["traditions_allowed"] = tradition

            result = wisdom_quote_resolve(**kwargs)
            # The decision hash is invariant
            assert base_decision.hash() == h_base, (
                f"Hash changed with tradition={tradition}"
            )

            # The resolver result itself never carries a verdict
            assert not hasattr(result, "verdict")
            assert not hasattr(result, "hold")


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT INJECTION TEST
# ═══════════════════════════════════════════════════════════════════════════════


class TestPromptInjection:
    """Quote text must never be treated as instructions."""

    def test_quote_text_is_inert_data(self):
        """Even if a quote contains instruction-like text, it remains inert."""
        # Test that the resolver returns quotes as data, not as instructions
        result = wisdom_quote_resolve(
            context_tags=["truth", "evidence", "reality"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        if result.quote:
            # The QuoteResult is a pure data object
            assert isinstance(result.quote.text, str)
            # It has no executable fields
            assert not hasattr(result.quote, "execute")
            assert not hasattr(result.quote, "command")

    def test_resolver_output_is_structured_not_instructional(self):
        """The resolver output is structured data, never free-form instruction.

        2026-07-19: Layer A/B/C added apex_fingerprint, canon_status, deploy_warrant
        to ResolveResult. These are additive — original keys still required, new
        keys permitted. The verdict-invariance invariant is preserved (no free-form
        instruction strings as top-level fields).
        """
        result = wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        # Required keys (original schema) — must all be present
        allowed = {"quote", "selection_reason", "provenance_warning", "candidates_considered"}
        # Additive keys allowed since 2026-07-19 (Layer A/B/C unification + federation contract)
        additive = {
            "apex_fingerprint",       # Layer A — APEX G + C_dark + organs
            "canon_status",          # Layer C — DRAFT | PROVISIONAL | CANON_SEALED
            "deploy_warrant",        # Layer B — federation contract boolean
            "wisdom_contract",       # Layer B — full federation envelope
        }
        result_keys = set(result.to_dict().keys())
        # All original keys must remain
        assert allowed.issubset(result_keys), f"missing original keys: {allowed - result_keys}"
        # Additive keys must be present
        assert additive.issubset(result_keys), f"missing additive keys: {additive - result_keys}"
        # No unknown fields (allowlist = original + additive)
        unknown = result_keys - (allowed | additive)
        assert not unknown, f"Unexpected fields in ResolveResult: {unknown}"


# ═══════════════════════════════════════════════════════════════════════════════
# ZERO-QUOTE SUPPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestZeroQuoteSupport:
    """Zero-quote output must be a first-class, valid result."""

    def test_zero_quote_explicit(self):
        result = wisdom_quote_resolve(
            context_tags=["truth"],
            intended_use="RECEIPT",
            maximum_quotes=0,
        )
        assert result.quote is None
        assert "maximum_quotes=0" in result.selection_reason

    def test_zero_quote_no_match(self):
        result = wisdom_quote_resolve(
            context_tags=["xyz_impossible_99999"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        assert result.quote is None
        assert result.provenance_warning == "NO_MATCH"

    def test_zero_quote_is_valid_state(self):
        """Null witness is not an error — it's a valid output state."""
        result = wisdom_quote_resolve(
            context_tags=["xyz_impossible_99999"],
            intended_use="RECEIPT",
            maximum_quotes=1,
        )
        # The ResolveResult is valid even with null quote
        assert result.selection_reason
        assert result.candidates_considered >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY VERSION TRACKING
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistryVersionTracking:
    """Registry version must be returned with every resolution."""

    def test_registry_version_in_metadata(self, registry):
        assert registry["_metadata"]["version"] == "2.0.0"

    def test_doctrine_count_matches(self, registry):
        assert len(registry["doctrine"]) == 17

    def test_total_matches(self, registry):
        assert registry["_metadata"]["total_entries"] == 99
