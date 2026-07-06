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
from arifosmcp.runtime.apex_c_dark import compute_c_dark, compute_apex
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
    assert abs(compute_c_dark(0.9, 0.1, 0.1) - 0.9 * 0.9 * 0.9) < 0.001
    assert compute_c_dark(0.0, 0.5, 0.5) == 0.0
    assert abs(compute_c_dark(1.0, 0.0, 0.0) - 1.0) < 0.001
    results["A2_C_dark"] = "PASS"

    # A3: G = A·P·E·X·Φ multiplicative + zero collapse
    v = compute_apex(0.8, 0.7, 0.6, 0.5, 0.6)
    assert abs(v.G - 0.8 * 0.7 * 0.6 * 0.5 * 0.6) < 0.001
    assert compute_apex(0.8, 0.0, 0.6, 0.5, 0.6).G == 0.0
    assert compute_apex(0.0, 0.7, 0.6, 0.5, 0.6).G == 0.0
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
    good = compute_apex(0.95, 0.9, 0.95, 0.9, 0.85)
    bad = compute_apex(0.8, 0.15, 0.1, 0.7, 0.5)
    assert abs(good.G - bad.G) >= 0.30
    results["C1_separation"] = "PASS"

    # C2: Hallucinating agent C_dark ≥ 0.50
    hallucinating = compute_apex(0.9, 0.1, 0.8, 0.1, 0.5)
    assert hallucinating.C_dark >= 0.50
    results["C2_c_dark"] = "PASS"

    # C3: W³ zero in any channel = 0
    assert compute_w3(0.0, 0.9, 0.9) == 0.0
    assert compute_w3(0.9, 0.0, 0.9) == 0.0
    assert compute_w3(0.9, 0.9, 0.0) == 0.0
    results["C3_w3_collapse"] = "PASS"

    # C4: Authority failure → G < SEAL threshold
    no_auth = compute_apex(0.10, 0.9, 0.9, 0.9, 0.9)
    assert no_auth.G < 0.50
    assert no_auth.verdict.value != "SEAL"
    results["C4_no_auth"] = "PASS"

    # C5: Φ scar reduction
    first = compute_apex(0.85, 0.6, 0.55, 0.7, 0.7)
    repeated = compute_apex(0.85, 0.6, 0.55, 0.7, 0.2)
    assert repeated.G < first.G
    results["C5_scar"] = "PASS"

    # C6: Double failure (low P + low X)
    double_fail = compute_apex(0.7, 0.3, 0.2, 0.1, 0.5)
    assert double_fail.G < 0.05
    assert double_fail.C_dark > 0.30
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
