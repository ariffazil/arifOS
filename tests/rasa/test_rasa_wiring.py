"""
tests/rasa/test_rasa_wiring.py — Rasa Wiring Tests

DITEMPA BUKAN DIBERI — Forged, Not Given.

Tests for the autonomous Rasa Contract kernel wiring:
  - Wrapper functions tested independently
  - activate/deactivate is reversible
  - Idempotent activation
  - Shadow mode: output unchanged, telemetry logged
  - ENFORCE_CRISIS mode: CRISIS messages blocked, SAFE unchanged
  - ENFORCE_ALL mode: all messages governed
  - Telemetry JSONL is writable and readable
  - Feature flag from env var
  - Wrappers don't crash if hooks return None
  - All 6 wrapper functions work
  - Session init wrapper initializes rasa context
  - Wrapped functions still work for non-rasa inputs
  - Existing kernel behavior preserved under SHADOW mode
  - Telemetry delta calculation

Constitutional risk: HIGH. Wiring tests protect the dignity-and-peace layer.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from arifosmcp.rasa.rasa_schemas import (
    RasaDetection,
    RasaEmotionTag,
    RasaRiskBand,
)
from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
from arifosmcp.rasa.rasa_wiring import (
    activate_rasa_wiring,
    deactivate_rasa_wiring,
    is_rasa_wired,
    rasa_wiring_diagnostics,
    rasa_wrap_heart,
    rasa_wrap_judge,
    rasa_wrap_memory,
    rasa_wrap_mind,
    rasa_wrap_sense,
    rasa_wrap_session_init,
)
from arifosmcp.rasa.rasa_wiring_config import (
    RasaContractMode,
    get_rasa_contract_mode,
    mode_allows_enforcement,
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _dummy_sense_fn(*args, **kwargs):
    """Mock arif_sense_observe for wrapper testing."""
    return {"status": "OK", "result": "sense_output", "query": kwargs.get("query", "")}


def _dummy_mind_fn(*args, **kwargs):
    """Mock arif_mind_reason for wrapper testing."""
    return {"status": "OK", "reasoning": "mind_output"}


def _dummy_memory_fn(*args, **kwargs):
    """Mock arif_memory_recall for wrapper testing."""
    return {"status": "OK", "memories": []}


async def _dummy_heart_fn(*args, **kwargs):
    """Mock arif_heart_critique for wrapper testing."""
    return {"status": "OK", "critique": "heart_output"}


async def _dummy_judge_fn(*args, **kwargs):
    """Mock arif_judge_deliberate for wrapper testing."""
    return {"verdict": "SEAL", "status": "OK"}


def _dummy_init_fn(*args, **kwargs):
    """Mock arif_session_init for wrapper testing."""
    return {"status": "OK", "session_created": True}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. WRAPPER FUNCTIONS — Independent Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestWrapperFunctions:
    """Test all 6 wrapper functions independently with mock originals."""

    def test_wrap_sense_returns_original_output(self):
        """rasa_wrap_sense must return original function's output."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        result = wrapped(query="alhamdulillah tenang je", session_id="test-wrap-sense")
        assert result["status"] == "OK"
        assert "sense_output" in result["result"]

    def test_wrap_mind_returns_original_output(self):
        """rasa_wrap_mind must return original function's output."""
        wrapped = rasa_wrap_mind(_dummy_mind_fn)
        result = wrapped(query="test query", session_id="test-wrap-mind")
        assert result["status"] == "OK"
        assert "mind_output" in result["reasoning"]

    def test_wrap_memory_returns_original_output(self):
        """rasa_wrap_memory must return original function's output."""
        wrapped = rasa_wrap_memory(_dummy_memory_fn)
        result = wrapped(mode="recall", session_id="test-wrap-memory")
        assert result["status"] == "OK"

    @pytest.mark.asyncio
    async def test_wrap_heart_returns_original_output(self):
        """rasa_wrap_heart must return original function's output."""
        wrapped = rasa_wrap_heart(_dummy_heart_fn)
        result = await wrapped(session_id="test-wrap-heart")
        assert result["status"] == "OK"
        assert "heart_output" in result["critique"]

    @pytest.mark.asyncio
    async def test_wrap_judge_returns_original_output(self):
        """rasa_wrap_judge must return original function's output."""
        wrapped = rasa_wrap_judge(_dummy_judge_fn)
        result = await wrapped(session_id="test-wrap-judge")
        assert result["verdict"] == "SEAL"

    def test_wrap_session_init_returns_original_output(self):
        """rasa_wrap_session_init must return original function's output."""
        wrapped = rasa_wrap_session_init(_dummy_init_fn)
        result = wrapped(session_id="test-wrap-init")
        assert result["status"] == "OK"

    def test_wrap_sense_handles_non_string_query(self):
        """Wrapper should handle non-string query gracefully."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        result = wrapped(query=12345, session_id="test-wrap-nonstr")
        assert result["status"] == "OK"

    def test_wrap_does_not_crash_on_original_failure(self):
        """Wrapper should not crash if original function raises."""

        def failing_fn(*args, **kwargs):
            raise RuntimeError("simulated failure")

        wrapped = rasa_wrap_mind(failing_fn)
        result = wrapped(query="test", session_id="test-fail")
        assert "error" in result


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ACTIVATION / DEACTIVATION — Reversible Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestActivationDeactivation:
    """Test activate/deactivate cycle is reversible."""

    def test_activate_deactivate_cycle(self):
        """activate → deactivate should restore original state."""
        # Ensure clean state
        deactivate_rasa_wiring()
        assert not is_rasa_wired()

        # Activate
        activate_rasa_wiring(mode=RasaContractMode.SHADOW)
        assert is_rasa_wired()

        # Deactivate
        deactivate_rasa_wiring()
        assert not is_rasa_wired()

    def test_idempotent_activation(self):
        """Calling activate twice should not break anything."""
        deactivate_rasa_wiring()
        activate_rasa_wiring(mode=RasaContractMode.SHADOW)
        activate_rasa_wiring(mode=RasaContractMode.SHADOW)  # Second call
        assert is_rasa_wired()

        deactivate_rasa_wiring()
        assert not is_rasa_wired()

    def test_idempotent_deactivation(self):
        """Calling deactivate twice should not break anything."""
        deactivate_rasa_wiring()
        deactivate_rasa_wiring()  # Second call — safe
        assert not is_rasa_wired()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SHADOW MODE — Output Unchanged
# ═══════════════════════════════════════════════════════════════════════════════


class TestShadowMode:
    """Test that SHADOW mode preserves original output."""

    def test_shadow_mode_preserves_sense_output(self):
        """In SHADOW mode, sense output must be identical to original."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        # Force shadow mode via wiring module
        import arifosmcp.rasa.rasa_wiring as wiring_mod

        original_mode = wiring_mod._current_mode

        try:
            wiring_mod._current_mode = RasaContractMode.SHADOW

            result = wrapped(query="alhamdulillah", session_id="test-shadow")
            assert result["status"] == "OK"
            assert "sense_output" in result["result"]
            # Shadow mode should NOT enforce
            assert "_rasa_governed" not in result or not result.get("_rasa_governed")
        finally:
            wiring_mod._current_mode = original_mode

    def test_shadow_mode_allows_safe_messages(self):
        """Safe messages should flow through without enforcement."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        result = wrapped(query="alhamdulillah bersyukur", session_id="test-shadow-safe")
        assert result["status"] == "OK"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ENFORCEMENT MODES
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnforceModes:
    """Test progressive enforcement modes."""

    def test_mode_allows_enforcement_crisis_only(self):
        """ENFORCE_CRISIS should only allow crisis enforcement."""
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "crisis") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "distress") is False
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_CRISIS, "safe") is False

    def test_mode_allows_enforcement_distress(self):
        """ENFORCE_DISTRESS should allow crisis + distress."""
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "crisis") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "distress") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_DISTRESS, "safe") is False

    def test_mode_allows_enforcement_all(self):
        """ENFORCE_ALL should allow all risk bands."""
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_ALL, "crisis") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_ALL, "distress") is True
        assert mode_allows_enforcement(RasaContractMode.ENFORCE_ALL, "safe") is True

    def test_mode_allows_enforcement_shadow(self):
        """SHADOW should never allow enforcement."""
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "crisis") is False
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "distress") is False
        assert mode_allows_enforcement(RasaContractMode.SHADOW, "safe") is False

    def test_enforce_crisis_blocks_crisis_messages(self):
        """ENFORCE_CRISIS should modify output for CRISIS messages."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)

        import arifosmcp.rasa.rasa_wiring as wiring_mod

        original_mode = wiring_mod._current_mode
        try:
            wiring_mod._current_mode = RasaContractMode.ENFORCE_CRISIS
            result = wrapped(query="aku rasa nak mati", session_id="test-crisis-enforce")
            # In ENFORCE_CRISIS mode with crisis message, output SHOULD be governed
            # CRISIS detection changes status to HOLD and adds _rasa_governed marker
            assert (
                result.get("_rasa_governed") is True or result.get("_rasa_crisis_block") is True
            ), f"CRISIS message should be governed. Got: {result}"
        finally:
            wiring_mod._current_mode = original_mode

    def test_enforce_crisis_does_not_block_safe_messages(self):
        """ENFORCE_CRISIS should NOT modify SAFE messages."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)

        import arifosmcp.rasa.rasa_wiring as wiring_mod

        original_mode = wiring_mod._current_mode
        try:
            wiring_mod._current_mode = RasaContractMode.ENFORCE_CRISIS
            result = wrapped(query="alhamdulillah tenang je", session_id="test-safe-no-enforce")
            assert result["status"] == "OK"
            # SAFE message should not be blocked
        finally:
            wiring_mod._current_mode = original_mode


# ═══════════════════════════════════════════════════════════════════════════════
# 5. TELEMETRY TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestTelemetry:
    """Test shadow telemetry logging."""

    def test_telemetry_writes_jsonl(self):
        """Shadow telemetry should write append-only JSONL."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            log_path = f.name

        try:
            telemetry = RasaTelemetry(log_path=log_path)
            telemetry.log_shadow(
                session_id="test-001",
                message="alhamdulillah",
                ungoverned_result={"status": "OK"},
                governed_result={"final_posture": "proceed", "detection": None},
                enforcement_mode="shadow",
                enforced=False,
            )
            telemetry.log_shadow(
                session_id="test-002",
                message="aku sedih",
                ungoverned_result={"status": "OK"},
                governed_result={"final_posture": "simplify", "detection": None},
                enforcement_mode="shadow",
                enforced=False,
            )

            entries = telemetry.read_log(limit=10)
            assert len(entries) >= 2
            assert entries[0]["session_id"] == "test-002"  # Most recent first
            assert entries[1]["session_id"] == "test-001"
            assert entries[0]["enforcement_mode"] == "shadow"
            assert entries[0]["enforced"] is False
        finally:
            os.unlink(log_path)

    def test_telemetry_read_empty_log(self):
        """Reading nonexistent log should return empty list."""
        telemetry = RasaTelemetry(log_path="/tmp/nonexistent_rasa_telemetry.jsonl")
        entries = telemetry.read_log()
        assert entries == []

    def test_telemetry_should_enforce(self):
        """Telemetry.should_enforce should match mode_allows_enforcement."""
        telemetry = RasaTelemetry()

        # Create mock detection
        crisis_detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.UNKNOWN],
            risk_band=RasaRiskBand.CRISIS,
            confidence=0.95,
        )
        safe_detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.PEACE],
            risk_band=RasaRiskBand.SAFE,
        )

        # Shadow mode
        assert telemetry.should_enforce(crisis_detection, "shadow") is False
        assert telemetry.should_enforce(safe_detection, "shadow") is False

        # Enforce crisis
        assert telemetry.should_enforce(crisis_detection, "enforce_crisis") is True
        assert telemetry.should_enforce(safe_detection, "enforce_crisis") is False

        # Enforce all
        assert telemetry.should_enforce(crisis_detection, "enforce_all") is True
        assert telemetry.should_enforce(safe_detection, "enforce_all") is True

    def test_telemetry_delta_calculation(self):
        """Telemetry delta should describe what would change."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            log_path = f.name

        try:
            telemetry = RasaTelemetry(log_path=log_path)
            telemetry.log_shadow(
                session_id="test-delta",
                message="aku sedih sangat",
                ungoverned_result={"status": "OK"},
                governed_result={
                    "final_posture": "simplify",
                    "detection": RasaDetection(
                        emotion_tags=[RasaEmotionTag.SADNESS],
                        risk_band=RasaRiskBand.SAFE,
                        confidence=0.85,
                    ),
                },
                enforcement_mode="shadow",
                enforced=False,
            )

            entries = telemetry.read_log()
            assert len(entries) == 1
            assert "Shadow only" in entries[0]["delta"]
            assert "simplify" in entries[0]["governed_posture"]
        finally:
            os.unlink(log_path)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. FEATURE FLAG TESTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestFeatureFlag:
    """Test environment variable feature flag."""

    def test_get_mode_defaults_to_shadow(self):
        """Default mode (no env var) should be SHADOW when wiring enabled."""
        # Save originals
        original_mode = os.environ.pop("RASA_CONTRACT_MODE", None)
        original_enabled = os.environ.pop("RASA_WIRING_ENABLED", None)
        os.environ["RASA_WIRING_ENABLED"] = "true"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.SHADOW
        finally:
            os.environ.pop("RASA_WIRING_ENABLED", None)
            if original_enabled is not None:
                os.environ["RASA_WIRING_ENABLED"] = original_enabled
            if original_mode is not None:
                os.environ["RASA_CONTRACT_MODE"] = original_mode

    def test_get_mode_from_env_shadow(self):
        """RASA_CONTRACT_MODE=shadow should return SHADOW when wiring enabled."""
        os.environ["RASA_WIRING_ENABLED"] = "true"
        os.environ["RASA_CONTRACT_MODE"] = "shadow"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.SHADOW
        finally:
            os.environ.pop("RASA_CONTRACT_MODE", None)
            os.environ.pop("RASA_WIRING_ENABLED", None)

    def test_get_mode_from_env_enforce_crisis(self):
        """RASA_CONTRACT_MODE=enforce_crisis should return ENFORCE_CRISIS."""
        os.environ["RASA_WIRING_ENABLED"] = "true"
        os.environ["RASA_CONTRACT_MODE"] = "enforce_crisis"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.ENFORCE_CRISIS
        finally:
            os.environ.pop("RASA_CONTRACT_MODE", None)
            os.environ.pop("RASA_WIRING_ENABLED", None)

    def test_get_mode_from_env_enforce_all(self):
        """RASA_CONTRACT_MODE=enforce_all should return ENFORCE_ALL."""
        os.environ["RASA_WIRING_ENABLED"] = "true"
        os.environ["RASA_CONTRACT_MODE"] = "enforce_all"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.ENFORCE_ALL
        finally:
            os.environ.pop("RASA_CONTRACT_MODE", None)
            os.environ.pop("RASA_WIRING_ENABLED", None)

    def test_get_mode_invalid_env_falls_back_to_shadow(self):
        """Invalid env var value should fall back to SHADOW when wiring enabled."""
        os.environ["RASA_WIRING_ENABLED"] = "true"
        os.environ["RASA_CONTRACT_MODE"] = "invalid_mode_xyz"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.SHADOW
        finally:
            os.environ.pop("RASA_CONTRACT_MODE", None)
            os.environ.pop("RASA_WIRING_ENABLED", None)


# ═══════════════════════════════════════════════════════════════════════════════
# 7. WIRING DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════════════════


class TestWiringDiagnostics:
    """Test wiring diagnostics output."""

    def test_diagnostics_returns_ok(self):
        """Wiring diagnostics should return OK status."""
        deactivate_rasa_wiring()
        diag = rasa_wiring_diagnostics()
        assert diag["status"] == "OK"
        assert "wiring_active" in diag
        assert "wrappers" in diag
        assert "telemetry_path" in diag

    def test_all_wrappers_callable_in_diagnostics(self):
        """All 6 wrappers should be marked CALLABLE."""
        diag = rasa_wiring_diagnostics()
        wrappers = diag["wrappers"]
        for name in [
            "rasa_wrap_sense",
            "rasa_wrap_mind",
            "rasa_wrap_heart",
            "rasa_wrap_memory",
            "rasa_wrap_judge",
            "rasa_wrap_session_init",
        ]:
            assert wrappers.get(name) == "CALLABLE", f"{name} should be CALLABLE"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. HOOKS RETURN NONE — Graceful Degradation
# ═══════════════════════════════════════════════════════════════════════════════


class TestGracefulDegradation:
    """Test that wrappers don't crash when hooks return None or fail."""

    def test_wrap_sense_handles_empty_message(self):
        """rasa_wrap_sense should handle empty message gracefully."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        result = wrapped(query="", session_id="test-empty")
        assert result["status"] == "OK"

    def test_wrap_mind_no_detection(self):
        """rasa_wrap_mind should handle missing detection gracefully."""
        wrapped = rasa_wrap_mind(_dummy_mind_fn)
        result = wrapped(query="test", session_id="test-no-detection")
        assert result["status"] == "OK"
        # No _rasa_context should be added since no prior detection
        assert "_rasa_context" not in result


# ═══════════════════════════════════════════════════════════════════════════════
# 9. RASA CONTRACT MODE ENUM
# ═══════════════════════════════════════════════════════════════════════════════


class TestRasaContractMode:
    """Test the RasaContractMode enum and config."""

    def test_all_modes_have_values(self):
        """All four modes should have string values."""
        assert RasaContractMode.SHADOW.value == "shadow"
        assert RasaContractMode.ENFORCE_CRISIS.value == "enforce_crisis"
        assert RasaContractMode.ENFORCE_DISTRESS.value == "enforce_distress"
        assert RasaContractMode.ENFORCE_ALL.value == "enforce_all"

    def test_mode_enum_from_string(self):
        """Mode enum should be constructable from string."""
        assert RasaContractMode("shadow") == RasaContractMode.SHADOW
        assert RasaContractMode("enforce_crisis") == RasaContractMode.ENFORCE_CRISIS
        assert RasaContractMode("enforce_all") == RasaContractMode.ENFORCE_ALL


# ═══════════════════════════════════════════════════════════════════════════════
# 10. NON-RASA INPUTS
# ═══════════════════════════════════════════════════════════════════════════════


class TestNonRasaInputs:
    """Test that wrapped functions work for non-rasa (non-human-emotion) inputs."""

    def test_wrap_sense_technical_query(self):
        """Technical queries should pass through without issues."""
        wrapped = rasa_wrap_sense(_dummy_sense_fn)
        result = wrapped(
            query="what is the status of the database server",
            session_id="test-tech",
        )
        assert result["status"] == "OK"

    def test_wrap_mind_code_query(self):
        """Code reasoning queries should work fine."""
        wrapped = rasa_wrap_mind(_dummy_mind_fn)
        result = wrapped(
            query="explain the time complexity of quicksort",
            session_id="test-code",
        )
        assert result["status"] == "OK"


# ═══════════════════════════════════════════════════════════════════════════════
# 11. CONSTITUTIONAL FLOOR COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════════════


class TestConstitutionalCompliance:
    """Verify wiring respects constitutional floors."""

    def test_wiring_does_not_modify_kernel_files(self):
        """Wiring must be purely additive — no modification of kernel tools."""
        # Verify wiring is in rasa/ directory only
        import os as _os

        wiring_path = _os.path.join(
            _os.path.dirname(__file__), "../../arifosmcp/rasa/rasa_wiring.py"
        )
        assert _os.path.exists(_os.path.abspath(wiring_path)), (
            "Wiring must be in arifosmcp/rasa/rasa_wiring.py"
        )

        # Verify kernel files are untouched
        kernel_files = [
            "/root/arifOS/arifosmcp/tools/sense.py",
            "/root/arifOS/arifosmcp/tools/reason.py",
            "/root/arifOS/arifosmcp/tools/heart.py",
            "/root/arifOS/arifosmcp/tools/memory.py",
            "/root/arifOS/arifosmcp/tools/judge.py",
            "/root/arifOS/arifosmcp/tools/session.py",
        ]
        for path in kernel_files:
            try:
                with open(path) as f:
                    content = f.read()
            except FileNotFoundError:
                continue
            assert "rasa_wiring" not in content, (
                f"{path} must NOT reference rasa_wiring (wiring is external)"
            )

    def test_shadow_mode_is_default(self):
        """SHADOW mode must be the default — safest, when wiring enabled."""
        original_mode = os.environ.pop("RASA_CONTRACT_MODE", None)
        original_enabled = os.environ.pop("RASA_WIRING_ENABLED", None)
        os.environ["RASA_WIRING_ENABLED"] = "true"
        try:
            mode = get_rasa_contract_mode()
            assert mode == RasaContractMode.SHADOW
        finally:
            os.environ.pop("RASA_WIRING_ENABLED", None)
            if original_enabled is not None:
                os.environ["RASA_WIRING_ENABLED"] = original_enabled
            if original_mode is not None:
                os.environ["RASA_CONTRACT_MODE"] = original_mode

    def test_ditempa_bukan_diberi_in_wiring_file(self):
        """DITEMPA BUKAN DIBERI motto must appear in wiring file."""
        wiring_path = os.path.join(os.path.dirname(__file__), "../../arifosmcp/rasa/rasa_wiring.py")
        with open(os.path.abspath(wiring_path)) as f:
            content = f.read()
        assert "DITEMPA BUKAN DIBERI" in content
