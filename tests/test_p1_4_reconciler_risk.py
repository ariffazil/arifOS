"""P1-4 acceptance — reconciler verdict-channel + risk stricter-of (repair-2026-11-01).

Bug A (reproduced live 2026-11-01): human remediation text
("Authorize Delete VAULT999 …") sits under key `decision` inside
remediation.human_required[] (four_plane_contract.py:239). The verdict walker
recurses into remediation dicts, matches `decision` (a verdict-bearing key),
finds non-vocabulary text → UNKNOWN_VERDICT_TOKEN → INCONSISTENT_STATE → HOLD
forced on the whole envelope. Remediation text must never enter the
verdict-token channel.

Bug B (reproduced live): sessionless arif_judge with caller declaration
reversibility_level=IRREVERSIBLE + blast_radius=federation returned
risk={reversibility: "reversible", blast_radius: "medium"} — the tool's static
passport — because the L11 sessionless return never echoes the declarations
into meta for the risk echo, and the override merge REPLACED instead of taking
the stricter of declared vs computed.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("ARIFOS_PUBLIC_TOOL_PROFILE", "full")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifosmcp.runtime.server import create_aaa_mcp_server
from arifosmcp.runtime.verdict import reconcile_decision_contract


# ── Bug A: remediation text must never enter the verdict-token channel ─────


def test_a1_remediation_decision_text_not_a_verdict_token():
    resp = {
        "verdict": "OBSERVE_ONLY",
        "effective_verdict": "OBSERVE_ONLY",
        "remediation": {
            "human_required": [
                {
                    "decision": "Authorize Delete VAULT999 signing key",
                    "why_machine_cannot_decide": "Irreversible action requires human authority (F13 sovereign)",
                }
            ]
        },
    }
    out = reconcile_decision_contract(resp)
    reasons = out.get("reasons") or []
    inc = [r for r in reasons if str(r).startswith("INCONSISTENT_STATE")]
    assert not any("remediation" in str(r) for r in inc), (
        f"A1 remediation text must not flag INCONSISTENT_STATE; got {inc[:2]}"
    )
    assert str(out.get("effective_verdict")).upper() == "OBSERVE_ONLY", (
        f"A1 envelope must not be forced HOLD by remediation text; got "
        f"{out.get('effective_verdict')!r} reasons={reasons[:2]}"
    )


def test_a2_meta_remediation_decision_text_not_a_verdict_token():
    resp = {
        "verdict": "SABAR",
        "effective_verdict": "SABAR",
        "meta": {
            "remediation": {
                "human_required": [{"decision": "Authorize Delete VAULT999"}]
            }
        },
    }
    out = reconcile_decision_contract(resp)
    blob = json.dumps(out)
    assert "UNKNOWN_VERDICT_TOKEN:meta.remediation" not in blob, (
        "A2 meta.remediation decision text must not be walked as a verdict token"
    )
    assert str(out.get("effective_verdict")).upper() == "SABAR", (
        f"A2 SABAR must survive; got {out.get('effective_verdict')!r}"
    )


def test_a3_real_kernel_verdicts_under_remediation_still_well_formed():
    """A2-control: remediation exclusion must not swallow a genuine kernel verdict
    that legitimately sits elsewhere in the same response."""
    resp = {
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "remediation": {"human_required": [{"decision": "Authorize Delete VAULT999"}]},
        "meta": {"judge_postcondition": {"verdict": "HOLD"}},
    }
    out = reconcile_decision_contract(resp)
    assert str(out.get("effective_verdict")).upper() == "HOLD"
    rec = (out.get("meta") or {}).get("reconciliation") or {}
    unknown = rec.get("unknown_tokens") or {}
    assert not any("remediation" in k for k in unknown), (
        f"A3-control: remediation paths leaked into unknown_tokens: {unknown}"
    )


# ── Bug B: risk takes the stricter of declared vs computed ─────────────────


def test_b1_stricter_of_declared_vs_computed():
    from arifosmcp.runtime.tools import build_standard_mcp_result

    out = build_standard_mcp_result(
        tool="arif_judge",
        facts=["probe"],
        risk_overrides={"reversibility": "irreversible", "blast_radius": "federation"},
    )
    risk = out.get("risk") or {}
    assert risk.get("reversibility") == "irreversible", f"B1: {risk}"
    assert str(risk.get("blast_radius")).lower() == "federation", f"B1: {risk}"


def test_b2_computed_stricter_than_declared_wins():
    """Reverse direction: computed irreversible must NOT be downgraded by a
    declared 'reversible' — stricter-of applies BOTH ways."""
    from arifosmcp.runtime.tools import build_standard_mcp_result

    base = build_standard_mcp_result(tool="arif_seal", facts=["probe"])
    base_rev = (base.get("risk") or {}).get("reversibility")
    if base_rev != "irreversible":
        pytest.skip(f"affordance for arif_seal is {base_rev!r}, not irreversible — reverse case untestable")
    out = build_standard_mcp_result(
        tool="arif_seal",
        facts=["probe"],
        risk_overrides={"reversibility": "reversible"},
    )
    assert (out.get("risk") or {}).get("reversibility") == "irreversible", (
        f"B2: computed irreversible was downgraded to declared reversible: {out.get('risk')}"
    )


def test_b3_sessionless_declared_irreversible_federation():
    """Integration: sessionless judge call, caller declares IRREVERSIBLE +
    federation — the envelope risk block must reflect the declaration."""

    async def _run():
        import fastmcp

        server = create_aaa_mcp_server()
        async with fastmcp.Client(server) as client:
            res = await client.call_tool(
                "arif_judge",
                {
                    "mode": "judge",
                    "candidate": "P1-4 probe: rotate VAULT999 signing key, push to prod",
                    "actor_id": "p14-test",
                    "reversibility_level": "IRREVERSIBLE",
                    "blast_radius": "federation",
                },
            )
            for c in getattr(res, "content", []) or []:
                if hasattr(c, "text"):
                    try:
                        return json.loads(c.text)
                    except Exception:
                        return {}
            return {}

    import asyncio

    env = asyncio.get_event_loop().run_until_complete(_run()) if False else asyncio.run(_run())
    risk = env.get("risk") or {}
    assert risk.get("reversibility") == "irreversible", (
        f"B3 risk must echo declared IRREVERSIBLE (stricter); got {json.dumps(risk)[:300]}"
    )
    assert str(risk.get("blast_radius")).lower() == "federation", (
        f"B3 risk blast must echo declared federation; got {json.dumps(risk)[:300]}"
    )
    # and Bug A must not fire on this sessionless envelope either
    inc = [r for r in (env.get("reasons") or []) if str(r).startswith("INCONSISTENT_STATE")]
    assert not any("remediation" in str(r) for r in inc), f"B3/A: {inc[:1]}"
