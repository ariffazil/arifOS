"""P1 apex-scalar-disambiguation — every APEX block names the system it describes.

Live defect (2026-10-27): one arif_init response carried G=0.5798 under
apex_scalars (federation aggregate, 7-day tool-call metrics) beside G=0.3663
under act_claims.apex (actor-scoped reading frozen at mint). Neither carried a
scope, so a reader could not say which number described what.

Fix: act_token.tag_apex_scope is the one writer of the scope/note labels;
session mint labels its block "actor"; the standing echo labels the aggregate
"federation". Values are never rewritten.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime import act_token


def test_tag_apex_scope_labels_federation_without_rewriting_values():
    tagged = act_token.tag_apex_scope({"G": 0.5798, "h": 0.8412})
    assert tagged["scope"] == "federation"
    assert "not this session" in tagged["note"].lower()
    assert tagged["G"] == 0.5798 and tagged["h"] == 0.8412


def test_tag_apex_scope_is_idempotent():
    once = act_token.tag_apex_scope({"G": 0.5})
    twice = act_token.tag_apex_scope(once)
    assert twice["scope"] == once["scope"] == "federation"
    assert twice["note"] == once["note"]


def test_actor_scope_note_differs_from_federation():
    tagged = act_token.tag_apex_scope({"G": 0.3663}, scope=act_token.APEX_SCOPE_ACTOR)
    assert tagged["scope"] == "actor"
    assert "frozen into this session's token" in tagged["note"]


def test_standing_apex_is_labelled_federation(monkeypatch):
    """_claims_to_standing reads the FEDERATION aggregate — label it as such."""
    monkeypatch.setattr(
        "arifosmcp.runtime.apex_primitives.compute_apex_from_metrics",
        lambda **kw: {"G": 0.5798, "C_dark": 0.2005, "W3": None, "h": 0.8412, "sample_size": 15739},
    )
    standing = act_token._claims_to_standing(
        {"sid": "s1", "actor": "a", "auth": "OBSERVE_ONLY", "av": False, "allowed": []},
        "tok",
        "sct",
        "test",
    )
    assert standing.apex["scope"] == "federation"
    assert standing.apex["G"] == 0.5798
    assert standing.apex["sample_size"] == 15739
    assert "not this session" in standing.apex["note"].lower()


def test_standing_apex_unmeasured_is_labelled_not_invented(monkeypatch):
    monkeypatch.setattr(
        "arifosmcp.runtime.apex_primitives.compute_apex_from_metrics",
        lambda **kw: {"G": None, "C_dark": None, "W3": None, "h": None, "sample_size": 0},
    )
    standing = act_token._claims_to_standing(
        {"sid": "s1", "actor": "a", "auth": "OBSERVE_ONLY", "av": False, "allowed": []},
        "tok",
        "sct",
        "test",
    )
    assert standing.apex["scope"] == "federation"
    assert standing.apex["G"] == "UNMEASURED"
