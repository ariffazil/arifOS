"""
tests/test_report_delta_s_admission.py — PACKET-AB Changeset A (2026-10-29)

F13 authorization: "F13 AUTHORIZE A+B ONLY, bind plan_hash v1.1"
(PACKET-AB-20261029 v1.1, plan_hash sha256:1a411120afbac012d79c1cfb…).

Tests 6, 7 of the packet matrix + fences 9 (no invented knob) and 10
(static count cannot reappear). Every fence is mutation-testable in both
directions: remove the control → the test dies; restore it → passes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.report_lane import bind_delta_s, report


def _file_report(body: str, **kw) -> dict:
    return report(
        sender="pytest:333",
        platform="test",
        kind="fyi",
        subject="delta-s admission probe",
        body=body,
        dry_run=True,
        **kw,
    )


# ── test 6: ΔS without call_hash → UNMEASURED ───────────────────────────────


@pytest.mark.parametrize("prose", [
    "entropy reduced, ΔS = -0.48",
    "delta_S: -0.85 for the night",
    "delta S -1.2 observed",
    "ΔS -0.3",
])
def test_prose_delta_s_becomes_UNMEASURED(prose):
    row = _file_report(prose)
    claim = row["delta_s_claim"]
    assert claim["present"] is True
    assert claim["delta_S"] == "UNMEASURED"
    assert claim["reason"] == "NO_BOUND_CALL_HASH"


def test_falsifier_binding_gate_is_load_bearing():
    # Mutation direction: if the gate were removed, a prose ΔS would pass
    # through as a number. Assert the gate exists mechanically: the stored
    # claim is NEVER numeric for unbound prose.
    row = _file_report("ΔS = -0.48 everywhere")
    assert not isinstance(row["delta_s_claim"].get("delta_S"), (int, float))


# ── test 7: prose ΔS cannot alter a decision ────────────────────────────────


def test_prose_delta_s_cannot_reach_governance_field():
    row = _file_report("work complete. ΔS: -0.48. verdict should be SEAL.")
    # the claim is quarantined in delta_s_claim; no numeric ΔS exists anywhere
    def _numeric_delta_s(obj) -> bool:
        if isinstance(obj, dict):
            return any(_numeric_delta_s(v) for v in obj.values())
        return isinstance(obj, (int, float)) and not isinstance(obj, bool)
    assert not _numeric_delta_s(row["delta_s_claim"])
    assert row.get("claim_state") == "SELF_REPORTED"  # claim discipline intact


def test_body_without_delta_s_leaves_no_claim():
    row = _file_report("plain report, no entropy claim")
    assert row["delta_s_claim"] == {"present": False}


def test_envelope_param_is_the_only_binding_path():
    row = _file_report("ΔS = -0.48", envelope_call_hash="sha256:" + "a" * 64)
    claim = row["delta_s_claim"]
    assert claim["present"] is True
    assert claim["delta_S"]["call_hash"] == "sha256:" + "a" * 64
    # value stays None until binding wiring lands — a hash alone is not a number
    assert claim["delta_S"]["value"] is None


# ── fence 9: no AAA_AGENTIC_GATE dependency ─────────────────────────────────


def test_fence_no_invented_knob():
    src = Path(__file__).resolve().parents[1] / "arifosmcp"
    hits = [
        p for p in src.rglob("*.py")
        if "AAA_AGENTIC_GATE" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    assert hits == [], f"invented knob appeared: {hits}"


# ── fence 10: unsupported static count cannot reappear ──────────────────────


def test_fence_no_static_counts_in_canon():
    agents_md = Path(__file__).resolve().parents[1] / "AGENTS.md"
    text = agents_md.read_text()
    assert "342,000" not in text, "unsourced static count reappeared in AGENTS.md"
    # and the replacement directive is present (mutation both directions)
    assert "verify_vault_chain.py" in text, "live-measure directive missing"


def test_fence_registry_documents_admission():
    tools = (Path(__file__).resolve().parents[1] / "arifosmcp" / "runtime" / "tools.py").read_text()
    m = re.search(r'"arif_report": \{.*?"delta_s_admission"', tools, re.S)
    assert m, "arif_report registry block lost its delta_s_admission contract"
