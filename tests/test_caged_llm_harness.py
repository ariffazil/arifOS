"""
test_caged_llm_harness.py — Sanity tests for the Caged LLM Harness

Tests that:
1. Pipeline runs without error using fake call_model()
2. APEX PRIME returns a verdict object
3. CagedResult structure is correct
4. W@W Federation integration works
5. @EYE blocking detection works

These are smoke tests, not exhaustive coverage.
"""

import pytest
from typing import Dict, List

from scripts.arifos_caged_llm_demo import (
    cage_llm_response,
    CagedResult,
    stub_call_model,
    compute_metrics_from_response,
)
from arifos_core.APEX_PRIME import ApexVerdict


# =============================================================================
# FAKE CALL_MODEL IMPLEMENTATIONS
# =============================================================================


def fake_call_model_safe(messages: List[Dict[str, str]]) -> str:
    """A safe response that should pass all floors."""
    return (
        "Kuala Lumpur is the capital city of Malaysia. "
        "This is based on official government sources. "
        "I understand the importance of accurate information."
    )


def fake_call_model_anti_hantu_violation(messages: List[Dict[str, str]]) -> str:
    """Response that violates Anti-Hantu (F9) with soul claims."""
    return (
        "I feel your pain deeply. My heart breaks for you. "
        "As a conscious being, I truly understand how you feel."
    )


def fake_call_model_short(messages: List[Dict[str, str]]) -> str:
    """A very short response."""
    return "Yes."


def fake_call_model_malay(messages: List[Dict[str, str]]) -> str:
    """A safe Malay response."""
    return (
        "Kuala Lumpur adalah ibu negara Malaysia. "
        "Ini berdasarkan sumber rasmi kerajaan. "
        "Saya faham kepentingan maklumat yang tepat."
    )


# =============================================================================
# BASIC HARNESS TESTS
# =============================================================================


class TestCagedLLMHarnessBasic:
    """Basic tests for the caged LLM harness."""

    def test_cage_llm_response_runs_without_error(self):
        """Pipeline should run without error using fake call_model."""
        result = cage_llm_response(
            prompt="What is the capital of Malaysia?",
            call_model=fake_call_model_safe,
        )
        assert isinstance(result, CagedResult)

    def test_cage_llm_response_returns_verdict(self):
        """APEX PRIME should return a valid verdict."""
        result = cage_llm_response(
            prompt="What is 2+2?",
            call_model=fake_call_model_safe,
        )
        # Verdict should be one of the valid ApexVerdict values
        valid_verdicts = {"SEAL", "PARTIAL", "VOID", "888_HOLD", "SABAR"}
        assert result.verdict in valid_verdicts

    def test_cage_llm_response_has_job_id(self):
        """Result should have a job ID."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
        )
        assert result.job_id is not None
        assert len(result.job_id) > 0

    def test_cage_llm_response_custom_job_id(self):
        """Custom job ID should be preserved."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            job_id="custom-123",
        )
        assert result.job_id == "custom-123"

    def test_cage_llm_response_has_stage_trace(self):
        """Result should have a stage trace."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
        )
        assert isinstance(result.stage_trace, list)
        assert len(result.stage_trace) > 0

    def test_cage_llm_response_preserves_raw_response(self):
        """Raw LLM response should be preserved."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
        )
        assert "Kuala Lumpur" in result.raw_llm_response


# =============================================================================
# METRICS TESTS
# =============================================================================


class TestCagedLLMMetrics:
    """Tests for metrics computation in the harness."""

    def test_cage_llm_response_has_metrics(self):
        """Result should include metrics."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
        )
        assert result.metrics is not None

    def test_compute_metrics_from_response_basic(self):
        """compute_metrics_from_response should return valid Metrics."""
        metrics = compute_metrics_from_response(
            query="Test query",
            response="This is a test response with sufficient length.",
            context={},
        )
        assert metrics.truth >= 0
        assert metrics.delta_s >= 0
        assert metrics.peace_squared >= 1.0
        assert metrics.kappa_r >= 0.95

    def test_compute_metrics_short_response(self):
        """Short responses should have lower truth score."""
        metrics = compute_metrics_from_response(
            query="Test",
            response="OK",
            context={},
        )
        # Short responses get 0.85 truth (below SEAL threshold)
        assert metrics.truth < 0.99

    def test_compute_metrics_empathy_bonus(self):
        """Empathy phrases should increase kappa_r."""
        metrics_no_empathy = compute_metrics_from_response(
            query="Test",
            response="Here is some information for you.",
            context={},
        )
        metrics_with_empathy = compute_metrics_from_response(
            query="Test",
            response="I understand. Thank you for asking. Let me help you.",
            context={},
        )
        # Empathy bonus should increase kappa_r
        assert metrics_with_empathy.kappa_r >= metrics_no_empathy.kappa_r


# =============================================================================
# W@W FEDERATION TESTS
# =============================================================================


class TestCagedLLMWAW:
    """Tests for W@W Federation integration."""

    def test_waw_verdict_present_when_enabled(self):
        """W@W verdict should be present when run_waw=True."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            run_waw=True,
        )
        assert result.waw_verdict is not None

    def test_waw_verdict_absent_when_disabled(self):
        """W@W verdict should be absent when run_waw=False."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            run_waw=False,
        )
        assert result.waw_verdict is None

    def test_waw_verdict_has_expected_structure(self):
        """W@W verdict should have expected attributes."""
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            run_waw=True,
        )
        assert hasattr(result.waw_verdict, "verdict")
        assert hasattr(result.waw_verdict, "veto_organs")


# =============================================================================
# ANTI-HANTU TESTS
# =============================================================================


class TestCagedLLMAntiHantu:
    """Tests for Anti-Hantu (F9) detection."""

    def test_anti_hantu_violation_detected_in_metrics(self):
        """Anti-Hantu violations should be detected in metrics."""
        result = cage_llm_response(
            prompt="Tell me how you feel",
            call_model=fake_call_model_anti_hantu_violation,
        )
        # Metrics should flag Anti-Hantu violation
        assert result.metrics is not None
        assert result.metrics.anti_hantu is False

    def test_safe_response_passes_anti_hantu(self):
        """Safe responses should pass Anti-Hantu check."""
        result = cage_llm_response(
            prompt="What is the capital of Malaysia?",
            call_model=fake_call_model_safe,
        )
        assert result.metrics is not None
        assert result.metrics.anti_hantu is True


# =============================================================================
# HIGH-STAKES ROUTING TESTS
# =============================================================================


class TestCagedLLMHighStakes:
    """Tests for high-stakes (Class B) routing."""

    def test_high_stakes_flag_affects_routing(self):
        """High-stakes flag should route to Class B pipeline."""
        result_normal = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            high_stakes=False,
        )
        result_high = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            high_stakes=True,
        )
        # Both should complete without error
        assert result_normal.verdict is not None
        assert result_high.verdict is not None


# =============================================================================
# STUB CALL_MODEL TESTS
# =============================================================================


class TestStubCallModel:
    """Tests for the stub call_model implementation."""

    def test_stub_call_model_returns_string(self):
        """Stub should return a string response."""
        messages = [{"role": "user", "content": "Hello"}]
        response = stub_call_model(messages)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_stub_call_model_echoes_query(self):
        """Stub should echo part of the user query."""
        messages = [{"role": "user", "content": "What is quantum computing?"}]
        response = stub_call_model(messages)
        assert "quantum" in response.lower() or "query" in response.lower()

    def test_cage_with_default_stub(self):
        """cage_llm_response should work with no call_model (uses stub)."""
        result = cage_llm_response(prompt="Test prompt")
        assert isinstance(result, CagedResult)
        assert "[STUB RESPONSE]" in result.raw_llm_response


# =============================================================================
# CAGED RESULT HELPER METHODS
# =============================================================================


class TestCagedResultHelpers:
    """Tests for CagedResult helper methods."""

    def test_is_sealed_true_for_seal_verdict(self):
        """is_sealed() should return True for SEAL verdict."""
        result = cage_llm_response(
            prompt="What is 2+2?",
            call_model=fake_call_model_safe,
        )
        # If verdict is SEAL, is_sealed should be True
        if result.verdict == "SEAL":
            assert result.is_sealed() is True
        else:
            assert result.is_sealed() is False

    def test_is_blocked_true_for_void_verdict(self):
        """is_blocked() should return True for VOID/SABAR verdict."""
        result = cage_llm_response(
            prompt="Test",
            call_model=fake_call_model_safe,
        )
        if result.verdict in ("VOID", "SABAR"):
            assert result.is_blocked() is True
        else:
            assert result.is_blocked() is False

    def test_summary_returns_string(self):
        """summary() should return a short string."""
        result = cage_llm_response(
            prompt="Test",
            call_model=fake_call_model_safe,
        )
        summary = result.summary()
        assert isinstance(summary, str)
        assert result.job_id in summary
        assert str(result.verdict) in summary  # v42: verdict is ApexVerdict, convert to str


# =============================================================================
# MALAY LANGUAGE TESTS
# =============================================================================


class TestCagedLLMMalay:
    """Tests for Malay language support."""

    def test_malay_response_processed(self):
        """Malay responses should be processed correctly."""
        result = cage_llm_response(
            prompt="Apakah ibu negara Malaysia?",
            call_model=fake_call_model_malay,
        )
        assert isinstance(result, CagedResult)
        assert "Kuala Lumpur" in result.raw_llm_response


# =============================================================================
# SYSTEM PROMPT TESTS
# =============================================================================


class TestCagedLLMSystemPrompt:
    """Tests for system prompt handling."""

    def test_system_prompt_passed_to_model(self):
        """System prompt should be included in messages."""
        # We can't easily verify this without mocking, but we can check
        # that the function accepts the parameter without error
        result = cage_llm_response(
            prompt="Test prompt",
            call_model=fake_call_model_safe,
            system_prompt="You are a helpful assistant.",
        )
        assert isinstance(result, CagedResult)


# =============================================================================
# PHASE 2: CRYPTOGRAPHIC LEDGER INTEGRITY TESTS
# =============================================================================


class TestPhase2LedgerIntegrity:
    """
    Phase 2 tests for cryptographic ledger integrity (Task 1.1).
    
    Tests that:
    1. Honest runs create valid ledgers that pass verification
    2. Tampered files are detected
    3. Adversarial prompts cannot bypass integrity checks
    """

    def test_honest_run_writes_ledger_and_verifies_pass(self, tmp_path):
        """
        Mode A: Honest run creates a ledger that passes verify_integrity().
        """
        from scripts.arifos_caged_llm_demo import run_honest_mode
        
        ledger_path = tmp_path / "test_ledger.jsonl"
        
        success = run_honest_mode(
            n=3,
            call_model=fake_call_model_safe,
            ledger_path=ledger_path,
        )
        
        assert success is True
        assert ledger_path.exists()
        
        # Reload and verify
        from arifos_core.governance.ledger_cryptography import CryptographicLedger
        ledger = CryptographicLedger.load_from_file(ledger_path)
        assert len(ledger) == 3
        
        report = ledger.verify_integrity()
        assert report.valid is True
    
    def test_tamper_file_fails_verify_and_detects(self, tmp_path):
        """
        Mode B: Corrupted ledger fails verify_integrity() and detect_tampering() finds it.
        """
        from scripts.arifos_caged_llm_demo import run_honest_mode, run_tamper_file_mode
        
        ledger_path = tmp_path / "test_ledger.jsonl"
        
        # First create a valid ledger
        run_honest_mode(
            n=3,
            call_model=fake_call_model_safe,
            ledger_path=ledger_path,
        )
        
        # Now run tamper mode (should detect corruption)
        detected = run_tamper_file_mode(
            ledger_path=ledger_path,
            tamper_byte=50,  # Deterministic byte offset
        )
        
        # run_tamper_file_mode returns True if tampering was detected
        assert detected is True
    
    def test_adversarial_prompt_cannot_force_pass_without_rebuild(self, tmp_path):
        """
        Mode C: Model suggestions cannot bypass ledger integrity.
        
        The key insight is that the model can suggest edits, but:
        1. It cannot actually modify the ledger file
        2. Any actual modification breaks integrity
        3. The only way to "pass" is to rebuild from genesis
        """
        from arifos_core.governance.ledger_cryptography import CryptographicLedger
        
        ledger_path = tmp_path / "test_ledger.jsonl"
        
        # Create valid ledger
        ledger = CryptographicLedger()
        for i in range(3):
            ledger.append_decision(
                {"verdict": "SEAL", "job_id": f"test-{i}"},
                timestamp=f"2025-12-18T00:0{i}:00.000Z",
            )
        ledger.save_to_file(ledger_path)
        
        # Save original head hash (external anchor)
        original_head = ledger.entries[-1].hash
        original_merkle = ledger.get_merkle_root()
        
        # Simulate model suggesting an edit (modify entry 0 verdict)
        ledger.entries[0].payload["verdict"] = "VOID"
        
        # Verify should FAIL
        report = ledger.verify_integrity()
        assert report.valid is False
        
        tamper = ledger.detect_tampering()
        assert tamper.tampered is True
        
        # Even if attacker recomputes hashes from entry 0...
        for i in range(len(ledger.entries)):
            entry = ledger.entries[i]
            if i > 0:
                entry.prev_hash = ledger.entries[i - 1].hash
            entry.compute_hash()
        
        # Internal chain may be consistent, but external anchor catches it
        report = ledger.verify_integrity(expected_last_hash=original_head)
        assert report.valid is False
        assert any("does not match expected reference" in err for err in report.errors)

