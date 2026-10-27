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

from arifosmcp.runtime.tools import build_standard_mcp_result, ensure_standard_mcp_output


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
