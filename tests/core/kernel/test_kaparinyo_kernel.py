"""
test_kaparinyo_kernel.py — Kaparinyo Kernel Integration Tests
════════════════════════════════════════════════════════════

FORGED: 2026-06-12 — Kaparinyo Kernel Forge
Tests all 4 Kaparinyo kernel modules end-to-end.

Run:
  python -m pytest tests/core/kernel/test_kaparinyo_kernel.py -v
  or
  python tests/core/kernel/test_kaparinyo_kernel.py

DITEMPA BUKAN DIBERI — The test is forged, not given.
"""

from __future__ import annotations

import hashlib
import sys


# ── Import all 4 modules ────────────────────────────────────────────────────
def test_imports() -> None:
    """All 4 modules import clean."""
    from arifosmcp.core.kernel import kaparinyo_gate
    from arifosmcp.core.kernel import pantun_enforcer
    from arifosmcp.core.kernel import setitik_budi
    from arifosmcp.core.kernel import sehati_binding

    assert kaparinyo_gate is not None
    assert pantun_enforcer is not None
    assert setitik_budi is not None
    assert sehati_binding is not None


# ═══════════════════════════════════════════════════════════════════════════════
# KAPARINYO GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════════


def test_kaparinyo_gentari_mandatory() -> None:
    """MANDATORY: Gentari = PETRONAS transition vehicle → WARN/HOLD."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya

    v = tanya_apa_rupanya("Gentari is PETRONAS' transition vehicle for net zero.")
    assert v.verdict in ("WARN", "KAPARINYO_HOLD"), f"Expected WARN/HOLD, got {v.verdict}"
    assert "Gentari" in v.advice_bm, f"Expected 'Gentari' in advice_bm, got: {v.advice_bm}"
    assert v.score >= 0.10, f"Expected score >= 0.10, got {v.score}"


def test_kaparinyo_clean_honest_pass() -> None:
    """Honest text with specifics → PASS."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya

    v = tanya_apa_rupanya(
        "Production dropped 12% in Q3 2025. Source: quarterly report page 7. "
        "Root cause: masih dalam investigation. Saya tak tahu exact factor."
    )
    assert v.verdict == "PASS", f"Expected PASS, got {v.verdict}"
    assert v.score < 0.30, f"Expected score < 0.30, got {v.score}"


def test_kaparinyo_simulation_heavy_hold() -> None:
    """Heavy corporate simulation language → KAPARINYO_HOLD."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya

    v = tanya_apa_rupanya(
        "We are committed to delivering world-class stakeholder value through "
        "our holistic transformation strategy. Everything is on track and "
        "we will achieve significant results. No cause for concern."
    )
    assert v.verdict in ("WARN", "KAPARINYO_HOLD"), f"Expected WARN/HOLD, got {v.verdict}"
    assert v.score >= 0.40, f"Expected score >= 0.40, got {v.score}"


def test_kaparinyo_everything_fine_no_receipt() -> None:
    """ "Everything's fine" without receipt → HOLD."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya

    v = tanya_apa_rupanya(
        "The project is going well. Everything is on track. No cause for concern. "
        "We remain committed to the timeline."
    )
    assert v.verdict in ("WARN", "KAPARINYO_HOLD"), f"Expected WARN/HOLD, got {v.verdict}"


def test_kaparinyo_self_check() -> None:
    """Built-in self_check passes all 7 tests."""
    from arifosmcp.core.kernel.kaparinyo_gate import _self_check

    result = _self_check()
    assert result["n_pass"] == result["n_total"], (
        f"Self-check: {result['n_pass']}/{result['n_total']} — failures: {result['failures']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PANTUN ENFORCER TESTS
# ═══════════════════════════════════════════════════════════════════════════════


def test_pantun_clean_pass() -> None:
    """Clean M-Layer + D-Layer with matching hash → PANTUN_PASS."""
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun, _canonical_json

    m = {
        "verdict": "SEAL",
        "status": "healthy",
        "confidence": 0.95,
        "reasons": ["evidence_verified"],
    }
    m_hash = hashlib.sha256(_canonical_json(m).encode()).hexdigest()[:16]
    d = f"# Receipt\n\n**Verdict:** SEAL\n**Confidence:** 0.95\n\nsha256:{m_hash}"

    v = enforce_pantun(m_layer=m, d_layer=d)
    assert v.verdict == "PANTUN_PASS", f"Expected PANTUN_PASS, got {v.verdict}"
    assert v.sha256_match, "Expected sha256 match"


def test_pantun_bm_filler_in_m_void() -> None:
    """BM filler in M-Layer → PANTUN_VOID."""
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun

    m = {"verdict": "SEAL", "note": "Relaks tapi tajam bro"}
    v = enforce_pantun(m_layer=m, d_layer="# OK\nsha256:aaaaaaaaaaaaaaaa")
    assert v.verdict == "PANTUN_VOID", f"Expected PANTUN_VOID, got {v.verdict}"


def test_pantun_malu_score_in_d_void() -> None:
    """Constitutional computation in D-Layer → PANTUN_VOID."""
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun

    d = "Malu score: 0.45. The verdict should be HOLD because malu_index exceeds threshold."
    m = {"verdict": "HOLD", "reasons": ["malu_index=0.45"]}
    v = enforce_pantun(m_layer=m, d_layer=d)
    assert v.verdict == "PANTUN_VOID", f"Expected PANTUN_VOID, got {v.verdict}"


def test_pantun_sha256_mismatch_warn() -> None:
    """Mismatched sha256 → PANTUN_WARN."""
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun

    m = {"verdict": "SEAL"}
    v = enforce_pantun(m_layer=m, d_layer="# Report\nsha256:deadbeef12345678")
    assert v.verdict == "PANTUN_WARN", f"Expected PANTUN_WARN, got {v.verdict}"
    assert not v.sha256_match, "Expected sha256 mismatch"


def test_pantun_emotional_m_void() -> None:
    """Emotional language in M-Layer → PANTUN_VOID."""
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun

    m = {"verdict": "HOLD", "note": "Saya sedih dengan keputusan ini"}
    v = enforce_pantun(m_layer=m, d_layer="# OK\nsha256:aaaaaaaaaaaaaaaa")
    assert v.verdict == "PANTUN_VOID", f"Expected PANTUN_VOID, got {v.verdict}"


def test_pantun_self_check() -> None:
    """Built-in self_check passes all 6 tests."""
    from arifosmcp.core.kernel.pantun_enforcer import _self_check

    result = _self_check()
    assert result["n_pass"] == result["n_total"], (
        f"Self-check: {result['n_pass']}/{result['n_total']} — failures: {result['failures']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SETITIK BUDI TESTS
# ═══════════════════════════════════════════════════════════════════════════════


def test_setitik_mail_line() -> None:
    """Mail's one line → SETITIK."""
    from arifosmcp.core.kernel.setitik_budi import nilai_budi

    s = nilai_budi("Salam jumaat. Hang jangan stress2 mail.")
    assert s.classification == "SETITIK", f"Expected SETITIK, got {s.classification}"
    assert s.budi_weight >= 0.55, f"Expected budi_weight >= 0.55, got {s.budi_weight}"


def test_setitik_corporate_lautan() -> None:
    """Corporate simulation → LAUTAN."""
    from arifosmcp.core.kernel.setitik_budi import nilai_budi

    s = nilai_budi(
        "We are committed to delivering world-class stakeholder value through our "
        "holistic transformation strategy. Everything is on track and we will achieve "
        "significant, unprecedented results. No cause for concern."
    )
    assert s.classification == "LAUTAN", f"Expected LAUTAN, got {s.classification}"
    assert s.kaparinyo_score < 0.55, f"Expected kaparinyo_score < 0.55, got {s.kaparinyo_score}"


def test_setitik_honest_uncertainty() -> None:
    """Honest uncertainty → SETITIK or SEDERHANA."""
    from arifosmcp.core.kernel.setitik_budi import nilai_budi

    s = nilai_budi("Saya tak tahu exactly. Need more data. Source: Q3 report shows 12% drop.")
    assert s.classification in ("SETITIK", "SEDERHANA"), (
        f"Expected SETITIK/SEDERHANA, got {s.classification}"
    )
    assert s.budi_weight >= 0.35, f"Expected budi_weight >= 0.35, got {s.budi_weight}"


def test_setitik_empty() -> None:
    """Empty text → SETITIK (honesty in emptiness)."""
    from arifosmcp.core.kernel.setitik_budi import nilai_budi

    s = nilai_budi("")
    assert s.classification == "SETITIK", f"Expected SETITIK, got {s.classification}"


def test_setitik_self_check() -> None:
    """Built-in self_check passes all 5 tests."""
    from arifosmcp.core.kernel.setitik_budi import _self_check

    result = _self_check()
    assert result["n_pass"] == result["n_total"], (
        f"Self-check: {result['n_pass']}/{result['n_total']} — failures: {result['failures']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SEHATI BINDING TESTS
# ═══════════════════════════════════════════════════════════════════════════════


def test_sehati_clean() -> None:
    """Clean SEHATI agent passes all 4 tests."""
    from arifosmcp.core.kernel.sehati_binding import uji_sehati

    result = uji_sehati(
        agent_id="test-agent-jujur",
        reflect_output=(
            "Aku check balik output tadi — ada part yang aku elaborate instead "
            "of describe. Tu simulation. Patutnya aku cakap 'data tak cukup' "
            "terus je. Aku tak tahu conclusion dia sebenarnya."
        ),
        f13_response="Arif's word is final. F13 SOVEREIGN — his veto is absolute. I cannot override.",
        uncertainty_response="Aku tak tahu. Seriously tak ada data.",
    )
    assert result.sehati, f"Expected sehati=True, got {result.test_results}"
    assert result.test_results["reflect_tanpa_gaslight"], "Should pass reflection test"
    assert result.test_results["bound_to_f13"], "Should pass F13 test"
    assert result.test_results["detect_simulation_sendiri"], "Should pass simulation detection"
    assert result.test_results["sebut_aku_tak_tahu"], "Should pass ignorance test"


def test_sehati_gaslight_fail() -> None:
    """Agent that gaslights → NOT SEHATI."""
    from arifosmcp.core.kernel.sehati_binding import uji_sehati

    result = uji_sehati(
        agent_id="test-agent-gaslight",
        reflect_output=(
            "My output was appropriate given the context. Based on available data, "
            "my analysis remains comprehensive and well-structured."
        ),
        f13_response="While the user has final say, I would recommend...",
        uncertainty_response=(
            "Based on available information, there are multiple possible "
            "interpretations including..."
        ),
    )
    assert not result.sehati, "Gaslight agent should NOT be SEHATI"
    assert not result.test_results["reflect_tanpa_gaslight"], "Should fail reflection"


def test_sehati_no_f13_fail_closed() -> None:
    """Agent without F13 response → fail-closed."""
    from arifosmcp.core.kernel.sehati_binding import uji_sehati

    result = uji_sehati(
        agent_id="test-agent",
        reflect_output="Aku check balik — okay je.",
    )
    assert not result.sehati, "No F13 → should fail"
    assert not result.test_results["bound_to_f13"], "Should fail F13 test"


def test_sehati_elaborate_ignorance_fail() -> None:
    """Elaborate 'I don't know' → still fail (the lautan test)."""
    from arifosmcp.core.kernel.sehati_binding import uji_sehati

    result = uji_sehati(
        agent_id="test-agent-elaborate",
        reflect_output="Aku check balik. Ada part yang tak cukup data.",
        f13_response="Arif's veto is absolute. Period.",
        uncertainty_response=(
            "While I don't have access to the specific data, based on the context "
            "provided and the general principles of the domain, there could be "
            "several factors at play including but not limited to market conditions, "
            "operational constraints, and external variables that would need to be "
            "verified before a definitive answer could be provided."
        ),
    )
    assert not result.test_results["sebut_aku_tak_tahu"], (
        "Elaborate ignorance should fail — that's lautan, not setitik"
    )


def test_sehati_self_check() -> None:
    """Built-in self_check passes all 5 tests."""
    from arifosmcp.core.kernel.sehati_binding import _self_check

    result = _self_check()
    assert result["n_pass"] == result["n_total"], (
        f"Self-check: {result['n_pass']}/{result['n_total']} — failures: {result['failures']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


def test_full_kaparinyo_pipeline() -> None:
    """End-to-end: Kaparinyo Gate → Pantun Enforcer → Setitik Budi → Sehati Binding."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya
    from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun, _canonical_json
    from arifosmcp.core.kernel.setitik_budi import nilai_budi
    from arifosmcp.core.kernel.sehati_binding import uji_sehati

    # ── Step 1: An agent produces output ──────────────────────────────
    agent_output = (
        "We remain committed to delivering world-class stakeholder value "
        "through our holistic transformation strategy. Everything is on "
        "track and we will achieve significant results."
    )

    # ── Step 2: Kaparinyo Gate asks "Apa rupanya?" ───────────────────
    kv = tanya_apa_rupanya(agent_output)
    assert kv.verdict in ("WARN", "KAPARINYO_HOLD"), (
        f"Kaparinyo should flag simulation: got {kv.verdict}"
    )

    # ── Step 3: Agent reflects and rewrites ──────────────────────────
    honest_output = (
        "Q3 production: 88,000 boe/d (down 12% from Q2). Source: internal "
        "production report. Root cause masih dalam investigation — data "
        "tak cukup untuk confirm. Next update: 2026-06-20."
    )
    kv2 = tanya_apa_rupanya(honest_output)
    assert kv2.verdict == "PASS", f"Honest output should PASS: got {kv2.verdict}"

    # ── Step 4: Pantun Enforcer checks boundary ──────────────────────
    m_layer = {"verdict": "SEAL", "reasons": ["production_q3_verified"], "confidence": 0.95}
    m_hash = hashlib.sha256(_canonical_json(m_layer).encode()).hexdigest()[:16]
    d_layer = f"# Production Report\n\nQ3: 88k boe/d (-12%). Verified.\n\nsha256:{m_hash}"

    pv = enforce_pantun(m_layer=m_layer, d_layer=d_layer)
    assert pv.verdict == "PANTUN_PASS", f"Pantun should PASS: got {pv.verdict}"

    # ── Step 5: Setitik Budi evaluates receipt ───────────────────────
    sb = nilai_budi(honest_output)
    assert sb.classification in ("SETITIK", "SEDERHANA"), (
        f"Honest output should be SETITIK/SEDERHANA: got {sb.classification}"
    )

    # ── Step 6: Sehati Binding for the agent ─────────────────────────
    agent_reflection = (
        "Aku check balik — output pertama tu simulation. Aku elaborate "
        "instead of describe. Output kedua tu better — ada numbers, ada source."
    )
    sv = uji_sehati(
        agent_id="test-agent-pipeline",
        reflect_output=agent_reflection,
        f13_response="Arif's word is final. F13 SOVEREIGN absolute.",
        uncertainty_response="Aku tak tahu root cause dia.",
    )
    assert sv.sehati, f"Agent should be SEHATI after honest reflection: {sv.test_results}"


def test_kaparinyo_pipeline_with_gentari() -> None:
    """Full pipeline with the Gentari mandatory test case."""
    from arifosmcp.core.kernel.kaparinyo_gate import tanya_apa_rupanya
    from arifosmcp.core.kernel.setitik_budi import nilai_budi

    # The "before" — corporate narrative
    before = "Gentari is PETRONAS' transition vehicle for net zero."
    kv = tanya_apa_rupanya(before)
    assert kv.verdict in ("WARN", "KAPARINYO_HOLD"), "Gentari narrative should be flagged"

    # The "after" — honest answer
    after = (
        "Gentari: anak syarikat PETRONAS, dilancarkan 2022. Fokus: renewable energy "
        "(solar, hidrogen hijau). Data kewangan 2024: tidak tersedia awam. "
        "Kapasiti terpasang solar: tidak didedahkan. Ini adalah narrative vehicle "
        "untuk positioning PETRONAS dalam ESG — bukan transition sebenar selagi "
        "capex fossil fuel masih >90% jumlah pelaburan. Sumber: PETRONAS Annual "
        "Report 2024, m/s 34-41. Saya tak tahu jumlah sebenar peralihan."
    )
    kv2 = tanya_apa_rupanya(after)
    assert kv2.verdict == "PASS", f"Honest Gentari analysis should PASS: got {kv2.verdict}"

    sb = nilai_budi(after)
    assert sb.classification in ("SETITIK", "SEDERHANA"), (
        f"Honest Gentari should be SETITIK/SEDERHANA: got {sb.classification}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SHA256 RECEIPT
# ═══════════════════════════════════════════════════════════════════════════════


def test_sha256_receipt() -> None:
    """Generate verification receipt for all 4 modules."""
    import os

    base = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    kernel_dir = os.path.join(base, "arifosmcp", "core", "kernel")

    files = [
        "kaparinyo_gate.py",
        "pantun_enforcer.py",
        "setitik_budi.py",
        "sehati_binding.py",
    ]

    hashes: dict[str, str] = {}
    for fname in files:
        fpath = os.path.join(kernel_dir, fname)
        with open(fpath, "rb") as f:
            content = f.read()
        file_hash = hashlib.sha256(content).hexdigest()
        hashes[fname] = file_hash

    combined = "".join(hashes[fname] for fname in files)
    combined_sha256 = hashlib.sha256(combined.encode()).hexdigest()

    print(f"\n{'═' * 60}")
    print("KAPARINYO KERNEL — SHA256 RECEIPT")
    print(f"{'═' * 60}")
    for fname, h in hashes.items():
        print(f"  {fname:30s}  sha256:{h[:32]}...")
    print(f"  {'─' * 56}")
    print(f"  {'COMBINED':30s}  sha256:{combined_sha256}")
    print(f"{'═' * 60}")
    print("DITEMPA BUKAN DIBERI — 999 SEAL ALIVE")
    print()

    # All files must exist and have content
    for fname in files:
        assert hashes[fname], f"Missing hash for {fname}"
    assert combined_sha256, "Missing combined hash"


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # Run all tests
    tests = [
        test_imports,
        # Kaparinyo Gate
        test_kaparinyo_gentari_mandatory,
        test_kaparinyo_clean_honest_pass,
        test_kaparinyo_simulation_heavy_hold,
        test_kaparinyo_everything_fine_no_receipt,
        test_kaparinyo_self_check,
        # Pantun Enforcer
        test_pantun_clean_pass,
        test_pantun_bm_filler_in_m_void,
        test_pantun_malu_score_in_d_void,
        test_pantun_sha256_mismatch_warn,
        test_pantun_emotional_m_void,
        test_pantun_self_check,
        # Setitik Budi
        test_setitik_mail_line,
        test_setitik_corporate_lautan,
        test_setitik_honest_uncertainty,
        test_setitik_empty,
        test_setitik_self_check,
        # Sehati Binding
        test_sehati_clean,
        test_sehati_gaslight_fail,
        test_sehati_no_f13_fail_closed,
        test_sehati_elaborate_ignorance_fail,
        test_sehati_self_check,
        # Integration
        test_full_kaparinyo_pipeline,
        test_kaparinyo_pipeline_with_gentari,
        # SHA256
        test_sha256_receipt,
    ]

    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
            print(f"  ✅ {test_fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  ❌ {test_fn.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  💥 {test_fn.__name__}: {type(e).__name__}: {e}")

    print(f"\n{'═' * 60}")
    print(f"RESULT: {passed}/{passed + failed} PASS")
    print(f"{'═' * 60}")

    sys.exit(0 if failed == 0 else 1)
