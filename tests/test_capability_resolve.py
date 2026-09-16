"""Tests for capability_index.resolve — task-scoped capability projection.

Covers the constitutional invariants of the resolver:
  • role ceilings (judge never mutates; observe floor; seal tier only at top)
  • eager admissibility (OBSERVE + CLAIM + low risk + domain match only)
  • fail-closed on unknown role (invariant 10 — ambiguity never widens)
  • context-budget aware eager capping
  • domain filtering via aliases

Run: cd /root/arifOS && PYTHONPATH=core .venv/bin/python -m pytest tests/test_capability_resolve.py -q
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from capability_index.models import CapabilityRecord
from capability_index.resolve import (
    DEFAULT_EAGER_MAX,
    LOW_CONTEXT_EAGER_MAX,
    LOW_CONTEXT_THRESHOLD,
    resolve_capabilities,
)


def _rec(
    tool: str,
    server: str = "TEST",
    effective: str = "OBSERVE",
    epistemic: str = "CLAIM",
    risk: str = "low",
    tags: tuple[str, ...] = (),
) -> CapabilityRecord:
    return CapabilityRecord(
        tool_name=tool,
        server=server,
        description=f"test tool {tool}",
        tags=list(tags),
        epistemic_tag=epistemic,
        action_class=effective,
        effective_class=effective,
        risk_tier=risk,
        authority_ceiling=server.upper(),
    )


RECORDS = [
    _rec("safe_read", server="aforge", tags=("code",)),
    _rec("safe_query", server="geox", tags=("seismic",)),
    _rec("gov_session", server="arifos", effective="GOVERN"),
    _rec("mutate_patch", server="aforge", effective="MUTATE", risk="medium"),
    _rec("seal_vault", server="arifos", effective="SEAL"),
    _rec("shaky_estimate", server="geox", epistemic="ESTIMATE"),
    _rec("risky_read", server="wealth", risk="high"),
]


def test_observe_role_never_sees_mutate_or_seal():
    m = resolve_capabilities(RECORDS, agent_id="t-observe", role="observe")
    all_loaded = {e["tool_name"] for e in m["eager"] + m["deferred"]}
    assert "mutate_patch" not in all_loaded
    assert "seal_vault" not in all_loaded
    assert m["hidden_count"] == 3  # GOVERN, MUTATE, SEAL above ceiling


def test_judge_reads_but_never_mutates():
    m = resolve_capabilities(RECORDS, agent_id="t-judge", role="judge")
    all_loaded = {e["tool_name"] for e in m["eager"] + m["deferred"]}
    assert "gov_session" in all_loaded
    assert "mutate_patch" not in all_loaded
    assert "seal_vault" not in all_loaded


def test_forge_may_mutate_but_never_seal():
    m = resolve_capabilities(RECORDS, agent_id="t-forge", role="forge")
    all_loaded = {e["tool_name"] for e in m["eager"] + m["deferred"]}
    assert "mutate_patch" in all_loaded
    assert "seal_vault" not in all_loaded
    assert m["hidden_count"] == 1


def test_seal_role_sees_everything():
    m = resolve_capabilities(RECORDS, agent_id="t-seal", role="seal")
    all_loaded = {e["tool_name"] for e in m["eager"] + m["deferred"]}
    assert all_loaded == {r.tool_name for r in RECORDS}
    assert m["hidden_count"] == 0


def test_eager_requires_observe_claim_low_risk():
    m = resolve_capabilities(RECORDS, agent_id="t-forge", role="forge")
    for e in m["eager"]:
        assert e["effective_class"] == "OBSERVE"
        assert e["epistemic_tag"] == "CLAIM"
        assert e["risk_tier"] == "low"
    eager_names = {e["tool_name"] for e in m["eager"]}
    assert "shaky_estimate" not in eager_names   # ESTIMATE epistemic
    assert "risky_read" not in eager_names       # high risk
    assert "gov_session" not in eager_names      # GOVERN class


def test_domain_filter_narrows_read_surface_but_not_actuation():
    m = resolve_capabilities(RECORDS, agent_id="t-route", role="route", task_domains=["geoscience"])
    all_loaded = {e["tool_name"] for e in m["eager"] + m["deferred"]}
    # OBSERVE tools outside the geoscience domain are hidden from the manifest
    assert "safe_read" not in all_loaded
    assert m["hidden_by_reason"].get("domain_out_of_task_scope", 0) >= 1
    # geoscience-domain OBSERVE tools remain
    assert "safe_query" in all_loaded or "shaky_estimate" in all_loaded
    # actuation substrate (GOVERN) is domain-exempt
    assert "gov_session" in all_loaded


def test_unknown_role_fails_closed():
    m = resolve_capabilities(RECORDS, agent_id="t-ghost", role="warlord")
    assert m["eager"] == [] and m["deferred"] == []
    assert m["hidden_count"] == len(RECORDS)
    assert m["error"] and "fail-closed" in m["error"]


def test_low_context_budget_caps_eager():
    m = resolve_capabilities(
        RECORDS + [_rec(f"bulk_{i}", server="aforge", tags=("code",)) for i in range(40)],
        agent_id="t-lean",
        role="observe",
        context_budget=LOW_CONTEXT_THRESHOLD - 1,
    )
    assert len(m["eager"]) <= LOW_CONTEXT_EAGER_MAX


def test_eager_max_respected_at_scale():
    many = RECORDS + [_rec(f"m_{i}", server="geox", tags=("well",)) for i in range(60)]
    m = resolve_capabilities(many, agent_id="t-big", role="observe")
    assert len(m["eager"]) <= DEFAULT_EAGER_MAX
    # nothing silently dropped: eager + deferred + hidden == everything
    assert len(m["eager"]) + len(m["deferred"]) + m["hidden_count"] == len(many)


def test_manifest_carries_policy_echo():
    m = resolve_capabilities(RECORDS, agent_id="t-audit", role="route")
    assert m["policy"]["observe"] == ["OBSERVE"]
    assert "SEAL" in m["policy"]["seal"]
    assert m["resolver_version"].startswith("capability-fabric.resolve")
