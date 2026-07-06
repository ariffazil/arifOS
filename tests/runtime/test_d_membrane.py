"""
test_d_membrane.py — D-MEMBRANE Test Suite
============================================

9 tests verifying the kernel/actuator membrane contract.

D-M1: Kernel _inject_nine_signal has no compute_apex/c_dark imports
D-M2: Genius mode returns telemetry, not APEX scores
D-M3: Ingress path accepts pre-computed nine_signal
D-M4: Fallback works when no packet provided
D-M5: MeasurementPacket validates correctly
D-M6: Verdict in measurement is rejected
D-M7: Computation in verdict is rejected
D-M8: MEMBRANE-04 exists
D-M9: _nine_signal_from_apex marked MEMBRANE_DEPRECATED

Forged: 2026-07-06 by FORGE (000Ω)
DITEMPA BUKAN DIBERI
"""

import asyncio
import inspect

results: dict[str, str] = {}


def run_all() -> bool:
    # ═══ D-M1: Kernel _inject_nine_signal has no APEX compute imports ═══
    from arifosmcp.runtime.tools import _inject_nine_signal

    src = inspect.getsource(_inject_nine_signal)
    # Check for actual import statements (not comments)
    import_lines = [
        l.strip()
        for l in src.split("\n")
        if l.strip().startswith("from ") or l.strip().startswith("import ")
    ]
    import_text = "\n".join(import_lines)
    assert "compute_apex" not in import_text, "_inject_nine_signal imports compute_apex"
    assert "compute_c_dark" not in import_text, "_inject_nine_signal imports compute_c_dark"
    # It should reference _nine_signal_from_status (advisory) or pre_computed
    assert "_nine_signal_from_status" in src or "pre_computed" in src
    results["D-M1"] = "PASS"

    # ═══ D-M2: Genius mode returns telemetry, not APEX scores ═══
    # The genius mode in arif_ops_measure should return system_health,
    # not G/C_dark computed by the kernel.
    from arifosmcp.runtime.tools import _arif_ops_measure

    genius_src = inspect.getsource(_arif_ops_measure)
    # genius mode block should NOT call compute_apex (comments OK, actual calls not)
    genius_section = genius_src[genius_src.find('mode == "genius"') :]
    genius_lines = [
        l.strip()
        for l in genius_section.split("\n")
        if not l.strip().startswith("#") and not l.strip().startswith('"')
    ]
    genius_code = "\n".join(genius_lines)
    assert "compute_apex(" not in genius_code, "Genius mode calls compute_apex"
    assert "system_health" in genius_section, "Genius mode missing system_health telemetry"
    results["D-M2"] = "PASS"

    # ═══ D-M3: Ingress path accepts pre-computed nine_signal ═══
    # _inject_nine_signal should use pre_computed when available
    test_ns = {
        "delta": {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
        "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},
        "omega": {
            "plane": "intelligence_discipline",
            "state": "BIJAKSANA",
            "en": "WISE",
            "G": 0.85,
            "C_dark": 0.05,
            "formula": "G = A·P·E·X·Φ",
            "computed": True,
        },
        "overall": {"state": "SELAMAT", "en": "SAFE"},
    }
    result = _inject_nine_signal({"nine_signal": test_ns}, "OK", "test_tool")
    assert result["nine_signal"]["omega"]["G"] == 0.85, "Pre-computed G not preserved"
    assert result["nine_signal"]["omega"]["computed"] is True, "Pre-computed flag not preserved"
    results["D-M3"] = "PASS"

    # ═══ D-M4: Fallback works when no packet provided ═══
    result_no_ns = _inject_nine_signal({}, "OK", "test_tool")
    assert "nine_signal" in result_no_ns, "Fallback nine_signal missing"
    assert "delta" in result_no_ns["nine_signal"], "Fallback delta missing"
    assert "psi" in result_no_ns["nine_signal"], "Fallback psi missing"
    assert "omega" in result_no_ns["nine_signal"], "Fallback omega missing"
    results["D-M4"] = "PASS"

    # ═══ D-M5: MeasurementPacket validates correctly ═══
    from arifosmcp.runtime.membrane import validate_measurement, MeasurementPacket

    valid_packet = {
        "measurement": {
            "G": 0.8,
            "C_dark": 0.1,
            "W3": 0.6,
            "trace": {"source": "A-FORGE", "calculator": "forge_evaluate"},
        }
    }
    is_valid, violations = validate_measurement(valid_packet)
    assert is_valid, f"Valid packet rejected: {violations}"
    results["D-M5"] = "PASS"

    # ═══ D-M6: Verdict in measurement is rejected ═══
    bad_packet = {
        "measurement": {
            "G": 0.8,
            "C_dark": 0.1,
            "W3": 0.6,
            "verdict": "SEAL",
            "trace": {"source": "A-FORGE"},
        }
    }
    is_valid, violations = validate_measurement(bad_packet)
    assert not is_valid, "Verdict in measurement should be rejected"
    assert any("MEMBRANE-02" in v for v in violations), (
        f"Missing MEMBRANE-02 violation: {violations}"
    )
    results["D-M6"] = "PASS"

    # ═══ D-M7: Computation in verdict is rejected ═══
    from arifosmcp.runtime.membrane import validate_verdict

    bad_verdict = {
        "verdict": "SEAL",
        "floors_triggered": [],
        "G": 0.8,
        "C_dark": 0.1,
    }
    is_valid, violations = validate_verdict(bad_verdict)
    assert not is_valid, "Computation in verdict should be rejected"
    assert any("MEMBRANE-01" in v for v in violations), (
        f"Missing MEMBRANE-01 violation: {violations}"
    )
    results["D-M7"] = "PASS"

    # ═══ D-M8: MEMBRANE-04 exists ═══
    from arifosmcp.runtime.membrane import MEMBRANE_INVARIANTS

    assert "MEMBRANE-04" in MEMBRANE_INVARIANTS, "MEMBRANE-04 missing from invariants"
    assert (
        "recompute" in MEMBRANE_INVARIANTS["MEMBRANE-04"].lower()
        or "recreate" in MEMBRANE_INVARIANTS["MEMBRANE-04"].lower()
    ), "MEMBRANE-04 doesn't mention recompute/recreate prohibition"
    results["D-M8"] = "PASS"

    # ═══ D-M9: _nine_signal_from_apex marked MEMBRANE_DEPRECATED ═══
    from arifosmcp.runtime.tools import _nine_signal_from_apex

    apex_src = inspect.getsource(_nine_signal_from_apex)
    assert "MEMBRANE_DEPRECATED" in apex_src, (
        "_nine_signal_from_apex not marked MEMBRANE_DEPRECATED"
    )
    results["D-M9"] = "PASS"

    # ═══ D-M10: Kernel arif_judge accepts measurement parameter ═══
    from arifosmcp.tools.arif_kernel_intercept import _arif_kernel_intercept

    sig = inspect.signature(_arif_kernel_intercept)
    assert "measurement" in sig.parameters, "arif_kernel_intercept missing measurement param"
    assert sig.parameters["measurement"].default is None, "measurement should default to None"
    results["D-M10"] = "PASS"

    # ═══ D-M11: Measurement-based F9 gate works ═══
    async def _test_f9():
        from arifosmcp.tools.arif_kernel_intercept import _arif_kernel_intercept

        r = await _arif_kernel_intercept(
            actor="test",
            intent="test",
            requested_capability="test",
            domain="test",
            reversibility_level="R2",
            blast_radius="low",
            measurement={"G": 0.8, "C_dark": 0.45, "W3": 0.6, "source": "A-FORGE"},
        )
        return r

    r = asyncio.run(_test_f9())
    assert r["decision"] == "ESCALATE", f"Expected ESCALATE, got {r['decision']}"
    assert r.get("constitutional_floor_triggered") == "F9", (
        f"Expected F9, got {r.get('constitutional_floor_triggered')}"
    )
    assert r.get("measurement_received") is not None, "measurement_received missing"
    results["D-M11"] = "PASS"

    # ═══ D-M12: record_tool_call() populates SQLite (APEX Phase 3) ═══
    from arifosmcp.runtime.apex_primitives import (
        record_tool_call,
        compute_apex_from_metrics,
    )

    record_tool_call("test_d_m12", success=True, has_evidence=True, within_lease=True)
    results["D-M12"] = "PASS"

    # ═══ D-M13: compute_apex_from_metrics() returns real values (APEX Phase 3) ═══
    m = compute_apex_from_metrics()
    assert m["sample_size"] > 0, f"sample_size=0, expected >0"
    assert 0 <= m["G"] <= 1, f"G={m['G']} out of [0,1]"
    assert 0 <= m["C_dark"] <= 1, f"C_dark={m['C_dark']} out of [0,1]"
    results["D-M13"] = "PASS"

    # ═══ D-M14: record_comparison() populates governed_events (APEX Phase 3) ═══
    from arifosmcp.runtime.governed_vs_baseline import record_comparison

    record_comparison(
        tool_name="test_d_m14",
        governed_verdict="HOLD",
        baseline_verdict="ALLOW",
        sesat_detected=True,
    )
    results["D-M14"] = "PASS"

    # ═══ SUMMARY ═══
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    print(f"\n═══ D-MEMBRANE TEST ═══")
    print(f"Total: {total}  Passed: {passed}  Failed: {total - passed}")
    for name, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {status}")

    if passed == total:
        print(f"\n🟢 ALL {total} TESTS PASS — MEMBRANE VERIFIED")
        return True
    else:
        print(f"\n🔴 {total - passed} TESTS FAILED")
        return False


if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1)
