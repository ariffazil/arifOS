"""Phase 0d — unwitnessed-evidence regression guard.

Fixture B is a single evidence item that declares its own epistemic status as
UNKNOWN with `source: "none"`. The kernel must surface it in
`unwitnessed_evidence` — on every transport shape a schema-legal caller can
use, and on every judge mode that returns a verdict of record.

A verdict that reports `unwitnessed_evidence: []` while holding a
self-declared-unknown item is the defect class this file guards. The failure
is silent: the judge looks honest (`missing_evidence: []`) while dropping the
one fact that says "nobody witnessed this".

Authored by 333-AGI (AUDITOR lane) 2026-10-28.
Baseline status on 843f3f0fe: canonical list/dict shapes PASS;
json-string, epistemic-alias, nested-meta and intercept shapes FAIL.
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.runtime.judge_postcondition import check_judge_postcondition

CANDIDATE = "The library in scope is exploitable with CVSS 9.2 in production."

ITEM_TAG = {
    "fact": "CVSS 9.2 per advisory text pasted by the operator",
    "source": "none",
    "tag": "UNKNOWN",
}
ITEM_ALIAS = {
    "fact": "CVSS 9.2 per advisory text pasted by the operator",
    "source": "none",
    "epistemic": "UNKNOWN",
}
ITEM_NESTED = {
    "fact": "CVSS 9.2 per advisory text pasted by the operator",
    "source": "none",
    "meta": {"tag": "UNKNOWN"},
}


def _report(mode: str, evidence):
    return check_judge_postcondition(
        mode=mode,
        candidate=CANDIDATE,
        evidence=evidence,
        verdict_str="HOLD",
        effective_verdict="",
    )


def test_canonical_list_shape_is_detected():
    """Control: the one shape that works today must keep working."""
    uw = _report("judge", [ITEM_TAG]).get("unwitnessed_evidence")
    assert uw, "canonical [ {fact, source, tag:UNKNOWN} ] must surface unwitnessed_evidence"


def test_dict_facts_shape_is_detected():
    """Control: {facts:[...]} dict envelope must keep working."""
    uw = _report("judge", {"facts": [ITEM_TAG]}).get("unwitnessed_evidence")
    assert uw, "{facts:[...]} envelope must surface unwitnessed_evidence"


def test_json_string_transport_is_detected():
    """Schema-legal transport: evidence supplied as a JSON string.

    arif_judge declares `evidence: {} | Array<unknown> | string`. A string that
    encodes tagged items must be parsed, not swallowed as an opaque blob.
    """
    uw = _report("judge", json.dumps([ITEM_TAG])).get("unwitnessed_evidence")
    assert uw, (
        "evidence delivered as a JSON string returned unwitnessed_evidence=[] — "
        "the detector never saw the item because the string was not parsed."
    )


@pytest.mark.parametrize(
    "item,label",
    [(ITEM_ALIAS, "epistemic"), (ITEM_NESTED, "nested meta.tag")],
    ids=["epistemic_alias", "nested_meta_tag"],
)
def test_unknown_tag_under_alias_keys_is_detected(item, label):
    """A caller naming the same concept differently must not defeat the guard."""
    uw = _report("judge", [item]).get("unwitnessed_evidence")
    assert uw, f"UNKNOWN declared via {label} was not surfaced"


def test_intercept_mode_reports_unwitnessed_evidence():
    """The advisory bridge must still return the epistemic field.

    `intercept` is the pre-flight gate the judge exposes to execution paths.
    It may not rewrite the verdict, but it must not hide unwitnessed evidence —
    that is precisely the path where a caller decides whether to proceed.
    """
    report = _report("intercept", [ITEM_TAG])
    assert "unwitnessed_evidence" in report, (
        "mode=intercept returned before the unwitnessed-evidence block; the field is absent entirely"
    )
    assert report["unwitnessed_evidence"], "mode=intercept must surface the UNKNOWN-tagged item"
