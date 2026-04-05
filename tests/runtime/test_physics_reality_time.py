
import pytest
from arifosmcp.runtime.megaTools.tool_08_physics_reality import physics_reality
from arifosmcp.runtime.models import VerdictCode

@pytest.mark.asyncio
async def test_physics_reality_time_mode_returns_ok_seal():
    """
    Tests that the physics_reality tool in 'time' mode returns a successful
    'SEAL' verdict with confidence 1.0, fixing the bug where it incorrectly
    returned a 'SABAR' verdict due to low confidence.
    """
    # When
    result_envelope = await physics_reality(mode="time", session_id="test-session")

    # Then
    assert result_envelope.ok is True, f"Expected ok=True, but got {result_envelope.ok}"
    assert result_envelope.verdict == VerdictCode.SEAL, f"Expected verdict=SEAL, but got {result_envelope.verdict}"
    
    # The confidence is now inside the verdict_detail and metrics
    if result_envelope.verdict_detail:
        assert result_envelope.verdict_detail.reason_code == "OK_ALL_PASS", f"Unexpected reason: {result_envelope.verdict_detail.reason_code}"

    if result_envelope.metrics and result_envelope.metrics.telemetry:
        assert result_envelope.metrics.telemetry.confidence == 1.0, f"Expected confidence=1.0, but got {result_envelope.metrics.telemetry.confidence}"

    assert result_envelope.payload is not None
    assert "temporal" in result_envelope.payload.get("data", {})
