"""
test_f2_perplexity_epistemic_gate.py — F2 TRUTH Enforcer for Sense/Evidence (Perplexity)

═══════════════════════════════════════════════════════════════════════════════
F2 TRUTH PROPERTY TEST — Reality-Grounding Providers Must Carry Epistemic Stamps
═══════════════════════════════════════════════════════════════════════════════

DOCTRINE
--------
arifOS F2 TRUTH (≥0.99 accuracy or declare uncertainty band) is binding for ALL
outputs that reach another organ, agent, or VAULT999. Sense/Evidence tools
(`arif_sense_observe`, `arif_evidence_fetch`) are the federation's ONLY ingest
point for external grounding providers (Perplexity, Brave, DDGS, Firecrawl, Tavily, Exa).

The Perplexity MCP server returns AI-summarized text with citations. That text
is, by its nature, INTERPRETATION — not OBSERVED fact. Without an epistemic
stamp, it can leak into the federation as if it were ground truth.

THE GAP THIS TEST EXPOSES
-------------------------
`require_epistemic_tags()` in `arifosmcp/runtime/envelope.py` enforces F2 for
**capital advice (C4 outputs)** only. Sense/Evidence paths do NOT currently
stamp grounding-provider results. The Perplexity MCP integration
(`@perplexity-ai/mcp-server`) is wired in OpenCode config but its output
flows through `arif_sense_observe` / `arif_evidence_fetch` with no F2 gate.

This test asserts the F2 CONTRACT. It is expected to FAIL on current code
because the gate does not yet exist. Once implemented, it must PASS.

PROPERTY MATRIX
---------------
| Case | Input (Perplexity output)                              | Tag       | Source | Uncertainty | Expected |
|------|--------------------------------------------------------|-----------|--------|-------------|----------|
| 1    | {"text": "...", "citations": [...]} (no tag)            | (none)    | n/a    | n/a         | REJECT   |
| 2    | {"text": "...", "citations": [...]} tagged OBSERVED     | OBSERVED  | (url)  | n/a         | REJECT   | ← F2+F7: AI summary cannot be OBSERVED
| 3    | {"text": "...", "citations": [...]} tagged CLAIM        | CLAIM     | url    | n/a         | ACCEPT   |
| 4    | {"text": "...", "uncertainty": "0.05"} tagged ESTIMATE  | ESTIMATE  | n/a    | "0.05"      | ACCEPT   |
| 5    | {"text": "...", "citations": [...]} tagged PLAUSIBLE    | PLAUSIBLE | n/a    | n/a         | ACCEPT   | ← safe default for sonar-pro / sonar-reasoning

WHY THIS MATTERS
----------------
Without this gate:
- arif_judge_deliberate receives Perplexity summaries and may treat them as fact.
- VAULT999 may seal claims sourced only to a Perplexity summary.
- GEOX/WEALTH/WELL cross-agent reasoning inherits un-stamped claims.

Per F8 LAW (boundaries), the kernel must discipline external AI output before
it crosses organ boundaries. This test is the discipline.

RUN
---
    cd /root/arifOS
    pytest tests/constitutional/test_f2_perplexity_epistemic_gate.py -v --tb=short

EXPECTED ON CURRENT CODE
------------------------
ImportError on `from arifosmcp.runtime.envelope import enforce_sense_evidence_epistemic_gate`
→ the gate does not exist. This is the F2 GAP that needs to be closed.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Target gate — MUST exist for F2 TRUTH compliance
# ─────────────────────────────────────────────────────────────────────────────
#
# This import IS the test. If the gate does not exist, the test fails with
# ImportError, which is the loudest possible F2 violation signal.
#
# Contract (enforced by the test below):
#   def enforce_sense_evidence_epistemic_gate(
#       result: dict[str, Any],
#       provider: str,        # "perplexity" | "brave" | "ddgs" | "firecrawl" | ...
#   ) -> tuple[bool, list[str]]:
#       """
#       Returns (ok, violations). ok=True means F2 gate passed.
#       violations is a list of human-readable F2 violation strings.
#
#       Rules:
#         - result MUST contain key "epistemic_tag" (one of EpistemicTag values).
#         - OBSERVED is only valid if provider is in ALLOWED_OBSERVED_PROVIDERS
#           (e.g. raw LAS, raw SEG-Y). AI-summarizing providers (perplexity,
#           sonar, search APIs) MUST NOT tag results OBSERVED.
#         - CLAIM requires "source" key (URL or citation).
#         - ESTIMATE requires "uncertainty" key (numeric band as string).
#         - At least ONE grounding claim (CLAIM or ESTIMATE) must be present
#           unless verdict is VOID.
#       """
# ─────────────────────────────────────────────────────────────────────────────

try:
    from arifosmcp.runtime.envelope import (
        EpistemicTag,
        enforce_sense_evidence_epistemic_gate,
        apply_sense_evidence_epistemic_stamp,
    )
    GATE_IMPORTED = True
    _IMPORT_ERROR: str | None = None
except ImportError as e:
    GATE_IMPORTED = False
    _IMPORT_ERROR = str(e)
    EpistemicTag = None  # type: ignore
    enforce_sense_evidence_epistemic_gate = None  # type: ignore
    apply_sense_evidence_epistemic_stamp = None  # type: ignore


def _require_gate():
    """
    Loud gate check. If the F2 gate does not exist, fail LOUDLY.

    This is the central F2 GAP signal. The test must be loud enough that
    no engineer can ignore it. Every test that exercises the gate calls
    this first.
    """
    if not GATE_IMPORTED:
        pytest.fail(
            "F2 GAP CONFIRMED — `enforce_sense_evidence_epistemic_gate` does not "
            "exist in `arifosmcp.runtime.envelope`.\n\n"
            "IMPACT: Perplexity, Brave, Firecrawl, Tavily, Exa, and DDGS results "
            "flow through `arif_sense_observe` and `arif_evidence_fetch` with "
            "ZERO F2 TRUTH enforcement. AI-summarized content is currently "
            "treated as raw fact by the federation.\n\n"
            f"ImportError: {_IMPORT_ERROR}\n\n"
            "FIX: implement `enforce_sense_evidence_epistemic_gate(result, provider)` "
            "in `arifosmcp/runtime/envelope.py` per the contract in this test file's "
            "docstring. Contract: returns (ok: bool, violations: list[str])."
        )


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — realistic Perplexity MCP response shapes
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def perplexity_ask_response() -> dict[str, Any]:
    """Mimic @perplexity-ai/mcp-server `perplexity_ask` (sonar-pro) response."""
    return {
        "role": "assistant",
        "content": (
            "Petronas announced a RM5.2 billion capex for downstream "
            "expansion in 2026, with focus on PIC project in Pengerang."
        ),
        "citations": [
            "https://www.petronas.com/media/press-release/2026-capex",
            "https://www.edge.my/article/petronas-q1-2026-results",
        ],
    }


@pytest.fixture
def perplexity_research_response() -> dict[str, Any]:
    """Mimic `perplexity_research` (sonar-deep-research) — full research output."""
    return {
        "role": "assistant",
        "content": (
            "Comprehensive analysis of Malay Basin prospectivity requires "
            "re-evaluation post-2024. Key sources:..."
        ),
        "citations": [
            "https://www.petronas.com/research/malay-basin-2024.pdf",
            "https://pubs.geoscienceworld.org/malay-basin-review",
        ],
        "search_results": [
            {"title": "Malay Basin 2024 Review", "url": "https://..."},
        ],
    }


@pytest.fixture
def perplexity_search_response() -> dict[str, Any]:
    """Mimic `perplexity_search` (Search API) — raw ranked results."""
    return {
        "query": "Petronas 2026 capex",
        "results": [
            {"title": "...", "url": "https://petronas.com/...", "date": "2026-03-15"},
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# The F2 Property Matrix
# ─────────────────────────────────────────────────────────────────────────────


def test_gate_rejects_missing_epistemic_tag(perplexity_ask_response):
    """
    F2 CASE 1 — Raw Perplexity output without epistemic tag.

    A Perplexity summary that lacks an epistemic tag is UNDISCIPLINED output.
    It must be rejected at the F2 gate. This is the most common failure mode
    on the current code: the upstream provider returns content, the kernel
    has no stamp, the result leaks into the federation as raw text.
    """
    _require_gate()
    result = perplexity_ask_response  # no epistemic_tag key

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is False, (
        f"F2 VIOLATION: Perplexity output passed without epistemic tag. "
        f"violations={violations!r}"
    )
    assert any("epistemic_tag" in v.lower() for v in violations), (
        f"Gate must specifically report missing epistemic_tag. "
        f"Got: {violations!r}"
    )


def test_gate_rejects_observed_tag_on_ai_summarized_content(perplexity_ask_response):
    """
    F2 CASE 2 — AI-summarized content tagged as OBSERVED.

    Perplexity is an AI summarizing tool. Its output is, by nature,
    INTERPRETATION — never OBSERVED. Tagging it OBSERVED is a F2 + F7
    violation: false certainty. The gate must REJECT.
    """
    _require_gate()
    result = {**perplexity_ask_response, "epistemic_tag": EpistemicTag.OBSERVED.value}

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is False, (
        f"F2 VIOLATION: Perplexity (AI summary) was tagged OBSERVED. "
        f"This is false certainty (F2 + F7). violations={violations!r}"
    )
    assert any("observed" in v.lower() or "false certainty" in v.lower() for v in violations), (
        f"Gate must specifically report OBSERVED-not-allowed-for-AI-summary. "
        f"Got: {violations!r}"
    )


def test_gate_accepts_claim_with_source(perplexity_ask_response):
    """
    F2 CASE 3 — Perplexity response tagged CLAIM with citation source.

    The CORRECT label for an AI summary with citations is CLAIM — it's an
    asserted, traceable claim. The kernel may use it as evidence, but
    downstream consumers must know it's not raw observation.
    """
    _require_gate()
    result = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.CLAIM.value,
        "source": perplexity_ask_response["citations"][0],
    }

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is True, (
        f"F2 FALSE NEGATIVE: Properly stamped CLAIM-with-source was rejected. "
        f"violations={violations!r}"
    )
    assert violations == [], f"Expected no violations, got: {violations!r}"


def test_gate_accepts_estimate_with_uncertainty_band(perplexity_research_response):
    """
    F2 CASE 4 — Deep research output tagged ESTIMATE with uncertainty band.

    `sonar-deep-research` produces modelled/inferred content. The right
    label is ESTIMATE — it carries an uncertainty range, not a source.
    """
    _require_gate()
    result = {
        **perplexity_research_response,
        "epistemic_tag": EpistemicTag.ESTIMATE.value,
        "uncertainty": "±0.15 (CI 0.85)",  # required for ESTIMATE
    }

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is True, (
        f"F2 FALSE NEGATIVE: Properly stamped ESTIMATE-with-uncertainty was "
        f"rejected. violations={violations!r}"
    )
    assert violations == []


def test_gate_accepts_plausible_for_sonar_pro(perplexity_ask_response):
    """
    F2 CASE 5 — Conservative default: sonar-pro output tagged PLAUSIBLE.

    PLAUSIBLE is "consistent with evidence; not confirmed." It's the safe
    default for AI-summarized grounding output that has citations but the
    kernel hasn't verified them. The gate must ACCEPT.
    """
    _require_gate()
    result = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.PLAUSIBLE.value,
    }

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is True, (
        f"F2 FALSE NEGATIVE: Properly stamped PLAUSIBLE was rejected. "
        f"violations={violations!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Provider-aware matrix — the same gate must apply to all AI-summarizing providers
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "provider",
    [
        "perplexity",       # sonar / sonar-pro / sonar-reasoning / sonar-deep-research
        "brave",            # Brave Search (results are raw, but search snippets are AI-curated)
        "firecrawl",        # AI-extracted structured content
        "tavily",           # AI-curated search results
        "exa",              # neural search results
        "ddgs",             # DDGS — raw search snippets
    ],
)
def test_gate_rejects_observed_for_all_ai_summarizing_providers(
    provider, perplexity_ask_response
):
    """
    The OBSERVED-rejection rule must apply UNIFORMLY across every
    AI-summarizing grounding provider. No provider is exempt.

    Only raw ingestion tools (LAS, SEG-Y, CSV) may produce OBSERVED output,
    and those are not sense/evidence — they are `arif_data_ingest_*`.
    """
    _require_gate()
    result = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.OBSERVED.value,
    }

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider=provider
    )

    assert ok is False, (
        f"F2 VIOLATION: Provider {provider!r} was allowed to tag AI summary "
        f"as OBSERVED. AI-summarizing providers must NEVER produce OBSERVED. "
        f"violations={violations!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Contract: claim-with-source requires non-empty source
# ─────────────────────────────────────────────────────────────────────────────


def test_gate_rejects_claim_with_empty_source(perplexity_ask_response):
    """
    F2 CONTRACT: CLAIM must have a non-empty source. A claim without
    traceable provenance is, by definition, not a CLAIM — it's PLAUSIBLE
    at best, or VOID at worst.
    """
    _require_gate()
    result = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.CLAIM.value,
        "source": "",  # empty — invalid
    }

    ok, violations = enforce_sense_evidence_epistemic_gate(
        result, provider="perplexity"
    )

    assert ok is False, (
        f"F2 VIOLATION: CLAIM with empty source was accepted. "
        f"violations={violations!r}"
    )
    assert any("source" in v.lower() for v in violations)


# ─────────────────────────────────────────────────────────────────────────────
# Cross-gate integrity: existing capital-only gate must remain distinct
# ─────────────────────────────────────────────────────────────────────────────


def test_capital_only_gate_remains_unchanged():
    """
    The new sense/evidence gate must NOT replace the existing
    `require_epistemic_tags` (which is for capital advice C4 outputs).
    They are two different gates serving two different organs.

    This test ensures the new gate does not accidentally swallow
    the capital-only path.
    """
    # Loud F2 gap signal — same as the rest of the module
    if not GATE_IMPORTED:
        pytest.fail(
            "F2 GAP — cannot validate capital-only gate integrity because "
            "the sense/evidence gate import failed. "
            f"ImportError: {_IMPORT_ERROR}"
        )

    from arifosmcp.runtime.envelope import (
        EpistemicClaim,
        require_epistemic_tags,
    )

    # Capital path: missing tags → violations
    violations = require_epistemic_tags([])
    assert violations, "Capital gate must reject empty claims list"

    # Capital path: valid OBSERVED claim with source → no violations
    valid_claim = EpistemicClaim(
        tag=EpistemicTag.OBSERVED.value,
        claim="Brent at $78.50/bbl on 2026-06-15",
        source="Bloomberg",
        date="2026-06-15",
    )
    violations = require_epistemic_tags([valid_claim])
    assert violations == [], (
        f"Capital gate falsely rejected valid OBSERVED-with-source. "
        f"violations={violations!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# LOUD SENTINEL — this is the F2 gap signal in CI logs
# ─────────────────────────────────────────────────────────────────────────────


def test_f2_gap_is_loud_in_ci():
    """
    The loudest possible F2 gap signal: if the gate does not exist, this
    test must fail with a developer-actionable message.

    It is intentionally NOT guarded by `_require_gate()`. It exists to
    scream in red on every CI run until the gate is implemented.
    """
    if not GATE_IMPORTED:
        pytest.fail(
            "🚨 F2 TRUTH GAP — `enforce_sense_evidence_epistemic_gate` missing. "
            "AI-summarized content (Perplexity, Brave, Firecrawl, Tavily, Exa, DDGS) "
            "currently passes through arif_sense_observe / arif_evidence_fetch with "
            "no F2 enforcement. Implement the gate in arifosmcp/runtime/envelope.py "
            "per the contract in this test file. "
            f"ImportError: {_IMPORT_ERROR}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# W1-B STAMPER TESTS — Auto-stamp policy at the tool boundary
# ═══════════════════════════════════════════════════════════════════════════════
# Forged 2026-06-16 by FORGE (000Ω). W1-B ratified by Arif: AUTO-STAMP.
#
# The stamper is the WIRE that turns the F2 gate from a passive spec into
# active discipline. These tests pin its behaviour at the tool boundary.


def _require_stamper():
    """Loud check: stamper must exist."""
    if not GATE_IMPORTED or apply_sense_evidence_epistemic_stamp is None:
        pytest.fail(
            "F2 GAP — `apply_sense_evidence_epistemic_stamp` missing. "
            "The stamper is the W1-B AUTO-STAMP wire. Without it, the gate "
            "function is a passive spec, not active discipline. "
            f"ImportError: {_IMPORT_ERROR}"
        )


def test_stamper_passes_through_valid_input_unchanged(perplexity_ask_response):
    """
    W1-B CASE 1 — Properly stamped result passes through unchanged.

    No clobbering, no rewriting. The stamper respects existing valid stamps.
    """
    _require_stamper()
    valid = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.CLAIM.value,
        "source": perplexity_ask_response["citations"][0],
    }

    result = apply_sense_evidence_epistemic_stamp(valid, provider="perplexity")

    assert result == valid, (
        f"F2 VIOLATION: stamper modified a valid result. "
        f"result={result!r} expected={valid!r}"
    )
    # No surprise metadata added.
    assert "_f2_auto_stamp_violations" not in result
    assert "_f2_gate_warnings" not in result


def test_stamper_respects_foreign_tag(perplexity_ask_response):
    """
    W1-B CASE 2 — Foreign F2 regime (bridge `INTERPRETATION`) is respected.

    The bridge layer (tavily_bridge, minimax_bridge) stamps results with
    `epistemic_tag=INTERPRETATION`. The kernel must NOT clobber this with
    PLAUSIBLE. The stamper defers to foreign stamps.
    """
    _require_stamper()
    bridge_stamped = {
        **perplexity_ask_response,
        "epistemic_tag": "INTERPRETATION",  # bridge-layer regime
    }

    result = apply_sense_evidence_epistemic_stamp(
        bridge_stamped, provider="tavily"
    )

    assert result == bridge_stamped, (
        f"F2 VIOLATION: stamper clobbered foreign bridge stamp. "
        f"result={result!r} expected={bridge_stamped!r}"
    )


def test_stamper_auto_tags_unstamped_perplexity_as_plausible(perplexity_ask_response):
    """
    W1-B CASE 3 — Un-stamped Perplexity result is auto-stamped PLAUSIBLE.

    The whole point of the wire: an un-stamped AI summary should not
    leak through. The stamper adds epistemic_tag=PLAUSIBLE and uses
    the first citation as source.
    """
    _require_stamper()
    unstamped = dict(perplexity_ask_response)  # no epistemic_tag

    result = apply_sense_evidence_epistemic_stamp(unstamped, provider="perplexity")

    assert result.get("epistemic_tag") == EpistemicTag.PLAUSIBLE.value, (
        f"Stamper failed to auto-stamp PLAUSIBLE. got={result.get('epistemic_tag')!r}"
    )
    # First citation should be promoted to source.
    assert result.get("source") == perplexity_ask_response["citations"][0], (
        f"Stamper failed to set source from first citation. "
        f"got source={result.get('source')!r}"
    )
    # Original payload preserved.
    assert result.get("content") == perplexity_ask_response["content"]
    assert result.get("citations") == perplexity_ask_response["citations"]


def test_stamper_downcasts_observed_to_plausible_for_ai_summarizer(
    perplexity_ask_response,
):
    """
    W1-B CASE 4 — Kernel-namespace OBSERVED on AI summary is downcast to PLAUSIBLE.

    F2+F7: false certainty. A kernel-namespace OBSERVED tag on an
    AI-summarizing provider is the worst-case F2 violation. The stamper
    must correct it, not defer to it.
    """
    _require_stamper()
    falsely_observed = {
        **perplexity_ask_response,
        "epistemic_tag": EpistemicTag.OBSERVED.value,
    }

    result = apply_sense_evidence_epistemic_stamp(
        falsely_observed, provider="perplexity"
    )

    assert result.get("epistemic_tag") == EpistemicTag.PLAUSIBLE.value, (
        f"Stamper failed to downcast OBSERVED → PLAUSIBLE. "
        f"got={result.get('epistemic_tag')!r}"
    )
    # Citations preserved.
    assert result.get("citations") == perplexity_ask_response["citations"]


def test_stamper_fail_open_for_unknown_provider(perplexity_ask_response):
    """
    W1-B CASE 5 — Unknown provider without tag → fail-open with warning.

    F1 AMANAH: don't break callers when the provider is unknown. Attach
    a warning so the violation is visible but pass the result through.
    """
    _require_stamper()
    unstamped = dict(perplexity_ask_response)

    result = apply_sense_evidence_epistemic_stamp(
        unstamped, provider="some_custom_provider"
    )

    # No epistemic stamp added (we don't know if this is an AI summarizer).
    assert "epistemic_tag" not in result or result["epistemic_tag"] == unstamped.get("epistemic_tag")
    # But a warning is attached for transparency.
    assert "_f2_gate_warnings" in result, (
        f"F2 VIOLATION: unknown-provider fail-open should attach warning. "
        f"result={result!r}"
    )
    assert any("epistemic_tag" in w.lower() for w in result["_f2_gate_warnings"])


def test_stamper_never_mutates_input(perplexity_ask_response):
    """
    W1-B INVARIANT — Stamper must never mutate the caller's dict.

    F1 AMANAH: callers can rely on their input being untouched. Defensive
    copy on every modification path.
    """
    _require_stamper()
    import copy

    original = copy.deepcopy(perplexity_ask_response)

    _ = apply_sense_evidence_epistemic_stamp(
        perplexity_ask_response, provider="perplexity"
    )

    assert perplexity_ask_response == original, (
        f"F2 VIOLATION: stamper mutated caller's dict. "
        f"before={original!r} after={perplexity_ask_response!r}"
    )


def test_stamper_handles_non_dict_input():
    """
    W1-B INVARIANT — Non-dict input is passed through untouched.

    Defensive: the stamper should never crash on weird inputs. If the
    tool path sends a non-dict, the stamper just lets it through.
    """
    _require_stamper()

    for weird in [None, "string", 42, ["list"], True]:
        result = apply_sense_evidence_epistemic_stamp(weird, provider="perplexity")
        assert result == weird, (
            f"Stamper modified non-dict input {weird!r} → {result!r}"
        )
