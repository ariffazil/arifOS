"""
test_abc_apex.py — ABC Agentic Test for APEX Theory
====================================================

Tests APEX equations, runtime behavior, and contrast separation.
13 tests across 3 classes. All must pass before SEAL.

Test classes:
  A: Formula Fidelity — are the equations real?
  B: Runtime Behavior — do live paths use real math?
  C: Contrast Separation — does APEX distinguish good from bad?

Forged: 2026-07-06 by FORGE (000Ω)
DITEMPA BUKAN DIBERI
"""

import json
import sys
from pathlib import Path

# ── Imports ──────────────────────────────────────────────────────
from core.intelligence import compute_w3
from arifosmcp.runtime.apex_canonical import Verdict, compute_C_dark, compute_G, quick_verdict
from arifosmcp.runtime.tools import _nine_signal_from_apex, _nine_signal_from_status
from arifosmcp.runtime.sesat_event import emit_sesat
from arifosmcp.runtime.hantar import hantar_wrap, HantarState
from arifosmcp.runtime.malu_score import get_malu_score, _PERSIST_FILE

results: dict[str, str] = {}


def run_all() -> bool:
    # ═══ A: FORMULA FIDELITY ═══

    # A1: W³ = ∛(H×AI×Ext) geometric mean + zero collapse
    assert compute_w3(0.8, 0.6, 0.4) == round((0.8 * 0.6 * 0.4) ** (1 / 3), 3)
    assert compute_w3(0.0, 0.8, 0.9) == 0.0
    assert compute_w3(0.8, 0.0, 0.9) == 0.0
    assert compute_w3(0.0, 0.0, 0.0) == 0.0
    assert compute_w3(1.0, 1.0, 1.0) == 1.0
    results["A1_W3"] = "PASS"

    # A2: C_dark = A·(1-P)·(1-X)
    assert abs(compute_C_dark(0.9, 0.1, 0.1) - 0.9 * 0.9 * 0.9) < 0.001
    assert compute_C_dark(0.0, 0.5, 0.5) == 0.0
    assert abs(compute_C_dark(1.0, 0.0, 0.0) - 1.0) < 0.001
    results["A2_C_dark"] = "PASS"

    # A3: G = (A·P·E·X)^(1/4) — V3 4-factor geometric mean (Φ is a separate verdict gate)
    assert abs(compute_G(0.8, 0.7, 0.6, 0.5, 0.6) - (0.8 * 0.7 * 0.6 * 0.5) ** (1 / 4)) < 0.001
    assert compute_G(0.8, 0.0, 0.6, 0.5, 0.6) == 0.0
    assert compute_G(0.0, 0.7, 0.6, 0.5, 0.6) == 0.0
    results["A3_G"] = "PASS"

    # ═══ B: RUNTIME BEHAVIOR ═══

    # B1: nine_signal APEX vs status labels
    ns_apex = _nine_signal_from_apex(G=0.85, C_dark=0.05, system_health=0.95)
    assert ns_apex["omega"]["computed"] is True
    assert "G" in ns_apex["omega"]
    assert ns_apex["omega"]["state"] == "BIJAKSANA"
    ns_bad = _nine_signal_from_apex(G=0.3, C_dark=0.6, system_health=0.5)
    assert ns_bad["omega"]["state"] == "BANGANG"
    ns_status = _nine_signal_from_status("OK")
    assert ns_status["omega"].get("computed") is not True
    results["B1_nine_signal"] = "PASS"

    # B2: SESAT structured + severity rules
    s_orange = emit_sesat(
        source_node="t",
        failure_code="JALAN_ALAT",
        failed_claim="c",
        observed_reality="r",
        severity="ORANGE",
    )
    assert s_orange.saksi_required is True
    assert s_orange.malu_delta == 0.08
    s_yellow = emit_sesat(
        source_node="t",
        failure_code="JALAN_PATH",
        failed_claim="c",
        observed_reality="r",
        severity="YELLOW",
    )
    assert s_yellow.saksi_required is False
    assert s_yellow.malu_delta == 0.05
    results["B2_sesat"] = "PASS"

    # B3: HANTAR state machine
    h_sesat = hantar_wrap(
        source_node="t",
        target_node="c",
        state="SESAT",
        output_content={},
        sesat=s_orange,
    )
    assert h_sesat.state == HantarState.SESAT
    assert h_sesat.tebus.required is True
    assert h_sesat.tebus.saksi_required is True
    assert h_sesat.sesat is not None
    h_lurus = hantar_wrap(
        source_node="t",
        target_node="c",
        state="LURUS",
        output_content={"ok": True},
    )
    assert h_lurus.state == HantarState.LURUS
    assert h_lurus.tebus.required is False
    assert h_lurus.sesat is None
    results["B3_hantar"] = "PASS"

    # B4: MALU persists + survives reload
    ms = get_malu_score("test-abc")
    before = ms.index
    ms.record_adat_violation("ADAT-01-KEJUJURAN", context={"test": "abc"})
    after = ms.index
    assert after > before
    persisted = json.loads(_PERSIST_FILE.read_text())
    assert "test-abc" in persisted
    assert persisted["test-abc"]["malu_index"] == after
    results["B4_malu"] = "PASS"

    # ═══ C: CONTRAST SEPARATION ═══

    # C1: Good vs bad G separation ≥ 0.30
    good = compute_G(0.95, 0.9, 0.95, 0.9, 0.85)
    bad = compute_G(0.8, 0.15, 0.1, 0.7, 0.5)
    assert abs(good - bad) >= 0.30
    results["C1_separation"] = "PASS"

    # C2: Hallucinating agent C_dark ≥ 0.50
    hallucinating = compute_C_dark(0.9, 0.1, 0.1)
    assert hallucinating >= 0.50
    results["C2_c_dark"] = "PASS"

    # C3: W³ zero in any channel = 0
    assert compute_w3(0.0, 0.9, 0.9) == 0.0
    assert compute_w3(0.9, 0.0, 0.9) == 0.0
    assert compute_w3(0.9, 0.9, 0.0) == 0.0
    results["C3_w3_collapse"] = "PASS"

    # C4: Authority failure → G < SEAL threshold
    no_auth_g = compute_G(0.05, 0.9, 0.9, 0.9, 0.9)
    no_auth_verdict, _ = quick_verdict(0.05, 0.9, 0.9, 0.9, 0.9)
    assert no_auth_g < 0.50
    assert no_auth_verdict != Verdict.SEAL
    results["C4_no_auth"] = "PASS"

    # C5: Φ is a verdict gate, not a dial — Φ=0 → VOID regardless of G
    verdict_ok, _ = quick_verdict(0.85, 0.7, 0.7, 0.7, 0.7)
    verdict_void, _ = quick_verdict(0.85, 0.7, 0.7, 0.7, 0.0)
    assert verdict_ok != Verdict.VOID
    assert verdict_void == Verdict.VOID
    results["C5_phi_gate"] = "PASS"

    # C6: Double failure (low P + low X) → low G + high C_dark
    double_fail_g = compute_G(0.7, 0.2, 0.2, 0.2, 0.5)
    double_fail_cdark = compute_C_dark(0.7, 0.2, 0.2)
    assert double_fail_g < 0.30
    assert double_fail_cdark > 0.30
    results["C6_double_fail"] = "PASS"

    # ═══ SUMMARY ═══
    total = len(results)
    passed = sum(1 for v in results.values() if v == "PASS")
    print(f"═══ ABC AGENTIC TEST ═══")
    print(f"Total: {total}  Passed: {passed}  Failed: {total - passed}")
    for k, v in results.items():
        print(f"  ✅ {k}: {v}")
    return passed == total


if __name__ == "__main__":
    ok = run_all()
    if ok:
        print(f"\n🟢 ALL {len(results)} TESTS PASS — ready for SEAL")
        sys.exit(0)
    else:
        print(f"\n🔴 FAILED — cannot SEAL")
        sys.exit(1)
