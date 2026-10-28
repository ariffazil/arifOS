"""P1 judge-schema-reversibility-drift — risk echo must describe the judged action.

Live defect (2026-10-27): arif_judge called with reversibility_level=HARD and
blast_radius=low returned risk={"reversibility":"reversible",
"blast_radius":"medium"} — the judge TOOL's static passport echoed back as if
it were the action's risk, contradicting the caller's declaration.

Fix: when meta carries the judged action's declaration, echo it and keep the
tool passport under risk.tool_baseline. Default (non-judge) envelopes keep the
tool-level risk block unchanged.
"""

from __future__ import annotations

from arifosmcp.runtime.tools import (
    _enforce_nine_signal,
    build_standard_mcp_result,
    ensure_standard_mcp_output,
)


def test_wrapper_echo_survives_result_only_payload():
    """LIVE-DEFECT regression (2026-10-28).

    The wrapper hands ensure_standard_mcp_output a RESULT-ONLY payload, so the
    judged action's declaration (top-level meta: reversibility_level /
    blast_radius) was never visible to the risk echo. The envelope therefore
    answered with the judge TOOL's static passport — "reversible"/"medium" for
    an action the caller declared HARD/organ.

    Seams tested here is the REAL one (_enforce_nine_signal -> public
    envelope), not the helper the earlier unit test called directly.
    """
    payload = {
        "status": "completed",
        "tool": "arif_judge",
        "verdict": "HOLD",
        "effective_verdict": "HOLD",
        "meta": {
            "reversibility_level": "HARD",
            "blast_radius": "organ",
            "kernel_intercept": {"affordance": {"blast_radius": "unknown"}},
        },
        "result": {"verdict": "HOLD", "judgment": "probe"},
    }
    out = _enforce_nine_signal("arif_judge", payload, actor_id="333-AGI")
    risk = out.get("risk", {})
    assert risk.get("subject") == "judged_action", risk
    assert risk.get("reversibility") == "hard", risk
    assert risk.get("blast_radius") == "organ", risk
    # The static tool passport survives — it is not erased.
    assert risk.get("tool_baseline", {}).get("reversibility") == "reversible", risk


def test_wrapper_without_declaration_keeps_tool_passport():
    payload = {
        "status": "completed",
        "tool": "arif_judge",
        "verdict": "HOLD",
        "meta": {"latency_ms": 1.2},
        "result": {"verdict": "HOLD"},
    }
    out = _enforce_nine_signal("arif_judge", payload, actor_id="333-AGI")
    risk = out.get("risk", {})
    assert "subject" not in risk, risk
    assert risk.get("reversibility") == "reversible", risk


def test_judged_action_risk_echo_prefers_declared_class():
    out = ensure_standard_mcp_output(
        "arif_judge",
        {
            "status": "completed",
            "tool": "arif_judge",
            "verdict": "HOLD",
            "meta": {"reversibility_level": "HARD", "blast_radius": "low"},
            "result": {"verdict": "HOLD"},
        },
    )
    assert out["risk"]["reversibility"] == "hard", out["risk"]
    assert out["risk"]["blast_radius"] == "low", out["risk"]
    assert out["risk"]["subject"] == "judged_action", out["risk"]
    # The static tool passport survives, it is not erased.
    assert out["risk"]["tool_baseline"]["reversibility"] == "reversible", out["risk"]


def test_r_scale_echo_mapping():
    table = {
        "R0": "reversible",
        "R1": "reversible",
        "R2": "reversible",
        "R3": "hard",
        "R4": "irreversible",
        "R5": "irreversible",
    }
    for token, expected in table.items():
        out = ensure_standard_mcp_output(
            "arif_judge",
            {
                "status": "completed",
                "tool": "arif_judge",
                "verdict": "HOLD",
                "meta": {"reversibility_level": token, "blast_radius": "low"},
                "result": {"verdict": "HOLD"},
            },
        )
        assert out["risk"]["reversibility"] == expected, (token, out["risk"])


def test_non_judge_payload_keeps_tool_risk_block():
    out = ensure_standard_mcp_output(
        "arif_seal",
        {
            "status": "completed",
            "tool": "arif_seal",
            "verdict": "SEAL",
            "result": {"mode": "verify", "ledger_size": 1},
        },
    )
    assert out["risk"]["reversibility"] == "reversible", out["risk"]
    assert "subject" not in out["risk"], out["risk"]


def test_risk_overrides_keep_default_shape_when_absent():
    out = build_standard_mcp_result(
        tool="arif_judge",
        facts=["verdict HOLD"],
        mode="judge",
        raw_result={"verdict": "HOLD"},
    )
    assert out["risk"]["reversibility"] in ("reversible", "irreversible"), out["risk"]
    assert "subject" not in out["risk"], out["risk"]
