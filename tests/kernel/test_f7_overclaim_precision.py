"""F7 HUMILITY — overclaim detector precision (2026-10-26).

Regression class F7_KEYWORD_FALSE_POSITIVE.

Measured live: two arif_report filings were refused with
``888_HOLD: F7 HUMILITY: Overclaim language detected: verified`` because the
report BODY quoted verification state (``actor_verified: true``, "the deployed
result was verified with live probes"). The detector's pattern was a bare-token
alternation ``\\b(always|never|guaranteed|proven|verified|confirmed)\\b`` applied
to every text field, including JSON-serialised evidence quotations.

That is self-defeating in a federation whose core verb is Verify: the vocabulary
needed to report on verification was itself classified as overclaim.

The fix has two halves, and both are tested here:

1. CITATION IMMUNITY — a claim that is quoted is being reported, not asserted.
2. ASSERTION FORM — the bare adjective no longer fires; the copula/claim forms
   that actually express certainty still do.

Guard-rail against over-correction: every genuine overclaim shape must still be
caught. If a future edit only proves half 1, these tests fail.
"""

from __future__ import annotations

import pytest

from arifosmcp.kernel.interceptor import _check_overclaim, _strip_citations
from arifosmcp.kernel.models import (
    AuthorityTier,
    CapabilityNode,
    InterceptorInput,
    MutationClass,
)

MUTATING_CAP = CapabilityNode(
    capability_id="test.write",
    tool_name="arif_report",
    server_id="local",
    mutation_class=MutationClass.LOCAL_STATE,
)


def _decide(text: str, field: str = "body"):
    req = InterceptorInput(
        raw_tool_name="arif_report",
        raw_arguments={field: text},
        actor_id="333-AGI",
    )
    return _check_overclaim(req, MUTATING_CAP, AuthorityTier.MEDIUM)


# ── Half 1: citation immunity ────────────────────────────────────────────────


def test_quoted_verified_is_not_an_overclaim():
    """Reporting that something was verified is not asserting certainty."""
    decision = _decide(
        'The call returned verdict=SEAL with `"actor_verified": true` and the '
        'run was reported as "verified" by the live probe.'
    )
    assert decision is None, decision.reason if decision else None


def test_json_evidence_blob_does_not_trip_the_gate():
    """A serialised evidence dict is data, not assertion."""
    req = InterceptorInput(
        raw_tool_name="arif_report",
        raw_arguments={
            "body": "Filed the result.",
            "evidence": {"first_call": "HOLD", "second_call": "SEAL, verified"},
        },
        actor_id="333-AGI",
    )
    assert _check_overclaim(req, MUTATING_CAP, AuthorityTier.MEDIUM) is None


def test_strip_citations_removes_double_quotes_and_backticks_only():
    assert _strip_citations('a "verified" b') == "a   b"
    assert _strip_citations("a `verified` b") == "a   b"
    # Apostrophes in contractions must NOT open a span.
    assert _strip_citations("don't say verified here") == "don't say verified here"


# ── Half 2: assertion forms still fire ───────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "This is proven, ship it.",
        "The fix is guaranteed.",
        "That approach is confirmed to work.",
        "It has been proven beyond question.",
    ],
)
def test_copula_claims_are_still_overclaims(text: str):
    assert _check_overclaim(_decide_req(text), MUTATING_CAP, AuthorityTier.MEDIUM) is not None


@pytest.mark.parametrize(
    "text",
    [
        "This is verified, ship it.",
        "The consequence is verified against the live service.",
        "Confirm receipt of this report.",
    ],
)
def test_state_reports_are_not_certainty_claims(text: str):
    """'verified' reports work done; F7 governs certainty, not evidence state."""
    assert _check_overclaim(_decide_req(text), MUTATING_CAP, AuthorityTier.MEDIUM) is None


@pytest.mark.parametrize(
    "text",
    [
        "This module never fails.",
        "The pipeline always works on the first try.",
        "It is guaranteed to work in production.",
        "This is 100% safe.",
        "There is zero risk here.",
        "I am absolutely sure this is correct.",
    ],
)
def test_genuine_overclaim_shapes_are_still_caught(text: str):
    assert _check_overclaim(_decide_req(text), MUTATING_CAP, AuthorityTier.MEDIUM) is not None


def test_bare_adjective_is_no_longer_punished():
    """'verified' as a noun/adjective of engineering state is not a certainty claim."""
    assert (
        _decide("Verify receipt accepted; consequence verified against the live service.") is None
    )


def _decide_req(text: str) -> InterceptorInput:
    return InterceptorInput(
        raw_tool_name="arif_report",
        raw_arguments={"body": text},
        actor_id="333-AGI",
    )
