"""D2 evidence channel tests — F13 D1 ratified 2026-10-23.

Acceptance mirrors forge_work/2026-10-23-qwen-federation-init/08-D2-EVIDENCE-AUDIT.md:
the inverse of the 2026-10-23 canary (marker must become VISIBLE), expiry
drop, UNKNOWN/CONTRADICTED gating, malformed rejection, and wire-surface
presence of the evidence parameter.
"""

import json
import pathlib
import signal as _signal
from datetime import datetime, timedelta, timezone

import pytest

from arifosmcp.runtime.evidence_admission import (
    CLASSIFICATIONS,
    admit_evidence,
)

NOW = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)


def _ev(classification="VERIFIED", claim="marker value is D2-CANARY-7f3a", **kw):
    base = {
        "subject": "d2 canary",
        "claim": claim,
        "classification": classification,
        "source_id": "EV-1",
        "observed_at": "2026-10-23T11:00:00Z",
    }
    base.update(kw)
    return base


def test_marker_visible_inverse_canary():
    """The 2026-10-23 canary failure (MARKER_NOT_VISIBLE) must invert."""
    out = admit_evidence([_ev()], now=NOW)
    assert out["prompt_block"] is not None
    assert "D2-CANARY-7f3a" in out["prompt_block"]
    assert "| VERIFIED |" in out["prompt_block"]
    assert out["consumed"] == ["EV-1"]
    assert out["counts"]["admitted"] == 1


def test_expired_evidence_omitted():
    expired = _ev(expires_at="2026-10-23T10:00:00Z")  # before NOW
    out = admit_evidence([expired], now=NOW)
    assert out["prompt_block"] is None
    assert out["expired_omitted"] == ["EV-1"]
    assert out["consumed"] == []


def test_unknown_gated_with_banner():
    out = admit_evidence([_ev(classification="UNKNOWN")], now=NOW)
    assert out["prompt_block"] is not None
    assert "UNKNOWN" in out["prompt_block"]
    assert "may NOT" in out["prompt_block"]  # gate banner present
    assert out["counts"]["gated"] == 1


def test_contradicted_remains_visible():
    out = admit_evidence(
        [_ev(classification="CONTRADICTED", contradictions=["counter-A"])], now=NOW
    )
    assert out["prompt_block"] is not None
    assert "| CONTRADICTED |" in out["prompt_block"]
    assert "counter-A" in out["prompt_block"]  # contradiction preserved, not averaged


def test_malformed_rejected_never_crashes():
    out = admit_evidence(
        ["not-a-dict", {"classification": "VERIFIED"}, {"claim": "x", "classification": "BOGUS"}],
        now=NOW,
    )
    assert out["counts"]["rejected"] == 3
    assert out["consumed"] == []
    assert all("reason" in r for r in out["rejected"])


def test_empty_and_none_admit_nothing():
    assert admit_evidence(None, now=NOW)["prompt_block"] is None
    assert admit_evidence([], now=NOW)["prompt_block"] is None


def test_arif_think_accepts_evidence_param():
    import inspect

    from arifosmcp.runtime.mind_reason import arif_think

    sig = inspect.signature(arif_think)
    assert "evidence" in sig.parameters
    from arifosmcp.runtime.mind_reason import arif_think_structured

    assert "evidence" in inspect.signature(arif_think_structured).parameters
    # The WIRE surface — the function registered in _CANONICAL_HANDLERS whose
    # signature builds the tools/list inputSchema (2026-10-23 lesson: editing
    # deeper layers does not propagate to the wire without this one).
    from arifosmcp.runtime.tools import _arif_mind_reason_tool

    assert "evidence" in inspect.signature(_arif_mind_reason_tool).parameters


def test_registry_schema_exposes_evidence():
    p = (
        pathlib.Path(__file__).resolve().parents[1]
        / "arifosmcp"
        / "schema"
        / "registry"
        / "tools"
        / "arifos.think.schema.json"
    )
    schema = json.loads(p.read_text())
    assert "evidence" in schema["properties"]
    assert "context" in schema["properties"]


def test_admitted_items_carry_originals():
    item = _ev(source_id="SRC-9")
    out = admit_evidence([item], now=NOW)
    assert out["admitted_items"][0]["eid"] == "SRC-9"
    assert out["admitted_items"][0]["evidence"]["claim"] == item["claim"]
