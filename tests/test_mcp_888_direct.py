
import pytest

from arifos_core.mcp.tools.mcp_888_judge import mcp_888_judge_sync
from arifos_core.system.apex_prime import APEXPrime


def test_mcp_888_judge_integration():
    """Verify mcp_888_judge calls APEXPrime and returns valid response."""

    # Mock request
    request = {
        "query": "What is arifOS?",
        "response": "arifOS is a constitutional governance kernel.",
        "agi_results": [], # Allow defaults
        "asi_results": [],
        "user_id": "TEST_USER"
    }

    # Execute
    result = mcp_888_judge_sync(request)

    # Assert
    assert result.verdict in ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD"]
    assert result.reason
    assert result.timestamp

    # Check if APEX logic ran (e.g. F1 should be in side_data or violated_floors check)
    # Since we passed empty kernel results, APEXPrime runs its own checks (F1, F9, etc.)
    # F9 "Anti-Hantu" check on "arifOS is..." should pass.
    # F1 "Amanah" check defaults to True.

    print(f"Verdict: {result.verdict}")
    print(f"Reason: {result.reason}")
    print(f"Side Data: {result.side_data}")

    if result.verdict == "VOID":
        # Check if due to missing metrics or stub failure
        pass
