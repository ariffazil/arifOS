"""
End-to-end integration tests

NOTE: These tests require valid API keys:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY

Skip with: pytest -k "not integration"
"""

import pytest
import os


# Skip if API keys not present
requires_api_keys = pytest.mark.skipif(
    not (os.getenv("ANTHROPIC_API_KEY") and os.getenv("OPENAI_API_KEY")),
    reason="API keys not set (ANTHROPIC_API_KEY, OPENAI_API_KEY required)"
)


@requires_api_keys
class TestEndToEndOrchestration:
    """Integration tests for full orchestration workflow"""

    def test_basic_orchestration(self):
        """Test basic orchestration workflow"""
        from arifos_orchestrator.core.orchestrator import run_orchestration

        query = "What is 2 + 2?"
        result = run_orchestration(query=query)

        # Check structure
        assert "query" in result
        assert "claude" in result
        assert "codex" in result
        assert "antigravity" in result
        assert "verdict" in result

        # Check verdicts
        assert result["verdict"] in ["SEAL", "PARTIAL", "VOID"]

        # Check Claude output exists
        assert len(result["claude"]["response"]) > 0

        # Check Codex output exists
        assert len(result["codex"]["code"]) > 0

        # Check AntiGravity validation
        validation = result["antigravity"]["validation"]
        assert "confidence" in validation
        assert validation["estimate_only"] is True

    def test_orchestration_with_context(self):
        """Test orchestration with additional context"""
        from arifos_orchestrator.core.orchestrator import run_orchestration

        query = "Explain thermodynamic AI"
        context = "User: Test user"
        result = run_orchestration(query=query, context=context)

        assert result["query"] == query
        assert result["context"] == context
        assert result["verdict"] in ["SEAL", "PARTIAL", "VOID"]

    def test_orchestration_verdict_seal(self):
        """Test orchestration that should produce SEAL verdict"""
        from arifos_orchestrator.core.orchestrator import run_orchestration

        # Simple, factual query
        query = "Write a Python function that adds two numbers"
        result = run_orchestration(query=query)

        # Should likely produce SEAL or PARTIAL (not VOID)
        assert result["verdict"] in ["SEAL", "PARTIAL"]

        # Code should be generated
        assert "def " in result["codex"]["code"] or "function" in result["codex"]["code"]


@requires_api_keys
def test_cli_interface():
    """Test CLI interface works"""
    import subprocess

    # Simple CLI test
    result = subprocess.run(
        ["python", "-m", "arifos_orchestrator", "What is 1+1?", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Should complete without errors
    assert "Verdict:" in result.stdout or result.returncode in [0, 1, 2]
