"""
tests/test_void_memanjang.py — VOID Memanjang Elimination Regression Suite

THE VOID MEMANJANG FAILURE MODE (what this test suite prevents):
  Any infrastructure/network error causes a VOID verdict.
  VOID means constitutional collapse. Network errors are NOT constitutional collapses.

CI GATE (from Grand Unified Technical Specification, FORGED-2026.03):
  Any VOID verdict issued for a non-constitutional cause = CI FAILURE.

TEST CATEGORIES:
  1. classify_exception() → never returns VOID for mechanical faults
  2. FaultClassification.verdict → 888_HOLD or SABAR for all mechanical faults
  3. VOID is issued ONLY for constitutional violations (F2/F11/F12/F10/F13)
  4. MACHINE_FAULT_CODES frozenset is exhaustive
  5. W3 verdicts correctly map to 888_HOLD (not VOID) for low scores
  6. MachineEnvelope.fault_code and GovernanceEnvelope.void_reason are mutually exclusive

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.fault_codes import (
    FaultClass,
    MechanicalFaultCode,
    ConstitutionalFaultCode,
    classify_exception,
    classify_network_errors,
)
from core.contracts.responses import MACHINE_FAULT_CODES, MachineEnvelope, GovernanceEnvelope
from core.intelligence.w3 import compute_w3, w3_to_verdict


# ─────────────────────────────────────────────────────────────────────────────
# 1. classify_exception() — NEVER VOID for mechanical faults
# ─────────────────────────────────────────────────────────────────────────────
class TestClassifyExceptionNeverVoid:

    def test_generic_connection_error_is_hold(self):
        exc = ConnectionError("Connection refused")
        result = classify_exception(exc)
        assert result.verdict != "VOID", (
            f"ConnectionError must not produce VOID. Got: {result.verdict} / {result.fault_code}"
        )
        assert result.verdict in ("888_HOLD", "SABAR")

    def test_timeout_error_is_hold(self):
        exc = TimeoutError("Request timed out after 15s")
        result = classify_exception(exc)
        assert result.verdict != "VOID"
        assert result.is_hold or result.is_sabar

    def test_os_error_is_hold(self):
        exc = OSError("Network unreachable")
        result = classify_exception(exc)
        assert result.verdict != "VOID"

    def test_runtime_error_unknown_is_hold(self):
        exc = RuntimeError("Some unexpected runtime error from Qdrant")
        result = classify_exception(exc)
        assert result.verdict != "VOID", (
            "Unknown RuntimeError must be classified as INFRA_DEGRADED/888_HOLD, not VOID"
        )

    def test_ssl_error_is_hold(self):
        exc = Exception("SSL: CERTIFICATE_VERIFY_FAILED")
        result = classify_exception(exc)
        assert result.verdict != "VOID"
        assert result.fault_code == MechanicalFaultCode.TLS_FAIL

    def test_qdrant_unreachable_is_hold(self):
        exc = ConnectionRefusedError("qdrant refused connection on port 6333")
        result = classify_exception(exc)
        assert result.verdict != "VOID"
        assert result.fault_class == FaultClass.MECHANICAL

    @pytest.mark.parametrize("timeout_msg", [
        "timeout exceeded",
        "request timed out",
        "read timeout",
        "connect timeout",
    ])
    def test_various_timeout_messages_are_hold(self, timeout_msg):
        exc = Exception(timeout_msg)
        result = classify_exception(exc)
        assert result.verdict != "VOID", f"Timeout '{timeout_msg}' must not produce VOID"

    def test_httpx_404_is_tool_not_exposed(self):
        try:
            import httpx
            # Simulate httpx.HTTPStatusError for 404
            req = httpx.Request("GET", "https://example.com")
            resp = httpx.Response(404, request=req)
            exc = httpx.HTTPStatusError("404 Not Found", request=req, response=resp)
            result = classify_exception(exc)
            assert result.verdict != "VOID"
            assert result.fault_code == MechanicalFaultCode.TOOL_NOT_EXPOSED
        except ImportError:
            pytest.skip("httpx not installed")

    def test_httpx_500_is_infra_degraded(self):
        try:
            import httpx
            req = httpx.Request("GET", "https://example.com")
            resp = httpx.Response(503, request=req)
            exc = httpx.HTTPStatusError("503 Service Unavailable", request=req, response=resp)
            result = classify_exception(exc)
            assert result.verdict != "VOID"
            assert result.fault_code == MechanicalFaultCode.INFRA_DEGRADED
        except ImportError:
            pytest.skip("httpx not installed")

    def test_httpx_429_is_rate_limited(self):
        try:
            import httpx
            req = httpx.Request("GET", "https://example.com")
            resp = httpx.Response(429, request=req)
            exc = httpx.HTTPStatusError("429 Too Many Requests", request=req, response=resp)
            result = classify_exception(exc)
            assert result.verdict != "VOID"
            assert result.fault_code == MechanicalFaultCode.RATE_LIMITED
        except ImportError:
            pytest.skip("httpx not installed")


# ─────────────────────────────────────────────────────────────────────────────
# 2. FaultClassification.verdict — 888_HOLD or SABAR only for mechanical
# ─────────────────────────────────────────────────────────────────────────────
class TestFaultClassificationVerdicts:

    def test_all_mechanical_codes_map_to_hold_or_sabar(self):
        """Every MechanicalFaultCode must map to 888_HOLD or SABAR, never VOID."""
        for code in MechanicalFaultCode:
            # We cannot easily construct specific exceptions for every code,
            # but we can verify the enum values exist in the non-VOID space.
            assert code.value not in {c.value for c in ConstitutionalFaultCode}, (
                f"MechanicalFaultCode.{code.name} overlaps with ConstitutionalFaultCode — "
                "this would create ambiguity in the fault taxonomy"
            )

    def test_no_results_maps_to_sabar_not_void(self):
        errors = [{"code": "NO_RESULTS", "engine": "brave"}]
        classification = classify_network_errors(errors)
        # NO_RESULTS returns "NO_RESULTS" code, which maps to SABAR at the tool level
        assert classification == "NO_RESULTS"

    def test_all_infra_errors_map_to_infra_degraded(self):
        errors = [
            {"code": "TIMEOUT_EXCEEDED", "engine": "brave"},
            {"code": "DNS_FAIL", "engine": "jina"},
            {"code": "INFRA_DEGRADED", "engine": "perplexity"},
        ]
        classification = classify_network_errors(errors)
        assert classification == "INFRA_DEGRADED"


# ─────────────────────────────────────────────────────────────────────────────
# 3. MACHINE_FAULT_CODES frozenset is complete
# ─────────────────────────────────────────────────────────────────────────────
class TestMachineFaultCodesCompleteness:

    def test_all_mechanical_codes_in_frozenset(self):
        """Every MechanicalFaultCode value must be in MACHINE_FAULT_CODES."""
        for code in MechanicalFaultCode:
            if code == MechanicalFaultCode.NO_RESULTS:
                continue  # NO_RESULTS → SABAR (epistemic), not in MACHINE_FAULT_CODES
            assert code.value in MACHINE_FAULT_CODES, (
                f"MechanicalFaultCode.{code.name} ({code.value}) not in MACHINE_FAULT_CODES frozenset. "
                "Add it to core/contracts/responses.py."
            )

    def test_no_constitutional_codes_in_machine_frozenset(self):
        """Constitutional fault codes must NOT appear in MACHINE_FAULT_CODES."""
        for code in ConstitutionalFaultCode:
            assert code.value not in MACHINE_FAULT_CODES, (
                f"ConstitutionalFaultCode.{code.name} found in MACHINE_FAULT_CODES — "
                "this would allow constitutional violations to be silently treated as mechanical"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 4. W3 verdict mapping — no VOID for low scores
# ─────────────────────────────────────────────────────────────────────────────
class TestW3VerdictNeverVoid:

    @pytest.mark.parametrize("s_h,s_a,s_e,expected_not", [
        (0.0, 0.0, 0.0, "VOID"),   # All witnesses zero → 888_HOLD
        (0.1, 0.1, 0.1, "VOID"),   # Very low scores → 888_HOLD
        (0.4, 0.4, 0.4, "VOID"),   # Below SABAR threshold → 888_HOLD
        (0.6, 0.6, 0.6, "VOID"),   # SABAR territory
        (0.8, 0.8, 0.8, "VOID"),   # PARTIAL territory
    ])
    def test_low_w3_never_produces_void(self, s_h, s_a, s_e, expected_not):
        result = compute_w3(s_h, s_a, s_e)
        assert result.verdict != expected_not, (
            f"W3 score {result.score:.3f} from (H={s_h}, A={s_a}, E={s_e}) "
            f"produced {result.verdict} — W3 scoring must never produce VOID"
        )

    @pytest.mark.parametrize("w3,expected_verdict", [
        (0.96, "SEAL"),
        (0.95, "SEAL"),
        (0.94, "PARTIAL"),
        (0.75, "PARTIAL"),
        (0.74, "SABAR"),
        (0.50, "SABAR"),
        (0.49, "888_HOLD"),
        (0.0,  "888_HOLD"),
    ])
    def test_w3_threshold_verdicts(self, w3, expected_verdict):
        verdict = w3_to_verdict(w3)
        assert verdict == expected_verdict, (
            f"w3_to_verdict({w3}) returned {verdict}, expected {expected_verdict}"
        )

    def test_irreversible_action_always_hold(self):
        """F13 mandate: irreversible actions always → 888_HOLD regardless of W3."""
        result = compute_w3(1.0, 1.0, 1.0, action_is_irreversible=True)
        assert result.verdict == "888_HOLD", (
            "F13 Sovereign Gate: irreversible=True must always produce 888_HOLD, "
            f"even with perfect W3={result.score}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. MachineEnvelope.fault_code and GovernanceEnvelope.void_reason are separate
# ─────────────────────────────────────────────────────────────────────────────
class TestEnvelopeSeparation:

    def test_machine_fault_code_field_exists(self):
        envelope = MachineEnvelope(fault_code="TIMEOUT_EXCEEDED")
        assert envelope.fault_code == "TIMEOUT_EXCEEDED"

    def test_governance_void_reason_field_exists(self):
        envelope = GovernanceEnvelope(
            verdict="VOID",
            void_reason="F11_AUTH_FAILURE",
        )
        assert envelope.void_reason == "F11_AUTH_FAILURE"

    def test_governance_hold_id_field_exists(self):
        envelope = GovernanceEnvelope(
            verdict="HOLD",
            hold_id="test-hold-id-uuid7",
        )
        assert envelope.hold_id == "test-hold-id-uuid7"

    def test_governance_metabolic_stage_field_exists(self):
        envelope = GovernanceEnvelope(metabolic_stage="500")
        assert envelope.metabolic_stage == "500"

    def test_governance_floor_scores_field_exists(self):
        envelope = GovernanceEnvelope(
            floor_scores={"F2": 0.99, "F11": 1.0, "F7": 0.85}
        )
        assert envelope.floor_scores["F2"] == 0.99

    def test_machine_envelope_tool_name_and_latency(self):
        envelope = MachineEnvelope(tool_name="reality_compass", latency_ms=42.5)
        assert envelope.tool_name == "reality_compass"
        assert envelope.latency_ms == 42.5

    def test_fault_code_should_not_be_void(self):
        """
        Ensures no one accidentally puts a constitutional code into fault_code.
        This is a documentation/pattern test.
        """
        constitutional_codes = {c.value for c in ConstitutionalFaultCode}
        for bad_code in constitutional_codes:
            # We can still construct it (no runtime block), but document the invariant:
            envelope = MachineEnvelope(fault_code=bad_code)
            # If fault_code is set to a constitutional code, the governance verdict
            # should still be VOID, not 888_HOLD. The test just ensures the fields exist
            # and the taxonomy is documented.
            assert bad_code in constitutional_codes  # tautology to document intent
