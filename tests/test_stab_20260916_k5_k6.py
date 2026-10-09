"""STAB-2026-09-16 Wave 1 — K5 (read-mode risk truth) + K6 (floors reason truth).

K5: arif_seal mode=verify is a READ; the response risk block must not inherit
    the tool's L5 default agency (which stamped reversibility="irreversible").
K6: the default SEAL reasons template claimed "Constitutional floors passed"
    while constitutional_check._floor_measurement="unmeasured" — a fabricated
    pass claim. Default must report absence ("No failed floors reported").
"""

from arifosmcp.runtime.tools import build_standard_mcp_result, ensure_standard_mcp_output


def test_k5_verify_mode_risk_is_reversible():
    out = build_standard_mcp_result(
        tool="arif_seal",
        facts=["chain check"],
        mode="verify",
        raw_result={"mode": "verify", "ledger_size": 1},
    )
    assert out["risk"]["reversibility"] == "reversible", out["risk"]
    assert out["risk"]["blast_radius"] == "low", out["risk"]


def test_k5_seal_mode_risk_stays_irreversible():
    out = build_standard_mcp_result(
        tool="arif_seal",
        facts=["seal write"],
        mode="seal",
        raw_result={"mode": "seal"},
    )
    assert out["risk"]["reversibility"] == "irreversible", out["risk"]
    assert out["risk"]["blast_radius"] == "high", out["risk"]


def test_k6_fabricated_floor_pass_claim_removed_from_source():
    # Unit-level regression guard: the fabricated "floors passed" template is
    # gone from the envelope module. Behavioural proof is the live kernel
    # receipt (reasons[] after deploy) — recorded in WAVE_1.md.
    import inspect

    import arifosmcp.runtime.tools as tools_mod

    src = inspect.getsource(tools_mod)
    assert '"Constitutional floors passed"' not in src
    assert '"No failed floors reported"' in src


def test_k5_wrapper_resolves_mode_from_result_dict():
    # The seal verify branch carries mode inside result{}; the wrapper must
    # resolve it, not fall back to "observe" (which is absent from
    # mode_agency_levels and would re-inherit the L5 default).
    out = ensure_standard_mcp_output(
        "arif_seal",
        {"status": "OK", "result": {"mode": "verify", "ledger_size": 1}},
    )
    assert out["risk"]["reversibility"] == "reversible", out["risk"]
