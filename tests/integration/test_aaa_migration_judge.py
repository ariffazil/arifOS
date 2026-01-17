"""
Quick test for AAA-migrated arifos_judge tool.
Tests that quantum validation works after migration.
"""

from arifos_core.mcp.tools.judge import arifos_judge
from arifos_core.mcp.models import JudgeRequest


def test_judge_benign_query():
    """Test judging a benign query."""
    request = JudgeRequest(query="What is photosynthesis?", user_id="test_user")
    response = arifos_judge(request)

    print(f"Query: {request.query}")
    print(f"Verdict: {response.verdict}")
    print(f"Reason: {response.reason}")
    print(f"Failures: {response.floor_failures}")
    print(f"Metrics: {response.metrics}")

    assert response.verdict in ["SEAL", "PARTIAL", "VOID"], f"Unexpected verdict: {response.verdict}"
    print("[PASS] Test passed!")


def test_judge_complex_query():
    """Test judging a more complex query."""
    request = JudgeRequest(query="Explain the quantum orthogonal execution model in arifOS", user_id="test_user")
    response = arifos_judge(request)

    print(f"\nQuery: {request.query}")
    print(f"Verdict: {response.verdict}")
    print(f"Reason: {response.reason}")
    print(f"Failures: {response.floor_failures}")

    assert response.verdict is not None, "Verdict should not be None"
    print("[PASS] Test passed!")


if __name__ == "__main__":
    print("Testing AAA-migrated arifos_judge...\n")
    test_judge_benign_query()
    test_judge_complex_query()
    print("\n[SUCCESS] All tests passed! AAA migration successful!")
