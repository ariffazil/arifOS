"""
Unit tests for AntiGravity Agent (Symbolic Validator)
"""

import pytest
from arifos.orchestrator.agents.antigravity_agent import AntiGravityAgent


class TestAntiGravityAgent:
    """Test suite for AntiGravity symbolic validation"""

    @pytest.fixture
    def agent(self):
        """Create AntiGravity agent instance"""
        return AntiGravityAgent()

    def test_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.humility_band == (0.03, 0.05)
        assert len(agent.validation_rules) > 0

    def test_validate_code_with_good_code(self, agent):
        """Test validation of well-formed code"""
        good_code = """
# Governance Audit: Example function
# arifOS orchestrator generated

def example_function(x: int) -> int:
    try:
        result = x * 2
        print(f"Result: {result}")
        return result
    except Exception as e:
        print(f"Error: {e}")
        raise
"""
        result = agent.validate_code(good_code)

        assert result["valid"] is True
        assert result["verdict"] == "SEAL"
        assert result["passed_rules"] >= 4  # Should pass most rules
        assert result["confidence"] == 0.04  # Humility band midpoint

    def test_validate_code_with_bad_code(self, agent):
        """Test validation of code with issues"""
        bad_code = """
def bad_function(x):
    api_key = "sk-hardcoded-secret"  # Hardcoded secret!
    return x * 2
"""
        result = agent.validate_code(bad_code)

        assert result["valid"] is False
        assert result["verdict"] == "VOID"  # Critical failure
        assert result["failed_rules"] > 0

    def test_audit_truth_with_substantive_response(self, agent):
        """Test truth audit with substantive response"""
        response = "This is a substantive response with meaningful content about constitutional governance."
        assert agent._audit_truth(response) is True

    def test_audit_truth_with_honesty_marker(self, agent):
        """Test truth audit with honesty marker"""
        response = "I don't know the answer to this question. Estimate Only."
        assert agent._audit_truth(response) is True

    def test_audit_truth_with_short_response(self, agent):
        """Test truth audit with too-short response"""
        response = "Yes"
        assert agent._audit_truth(response) is False

    def test_audit_alignment_with_good_code(self, agent):
        """Test alignment audit with well-formed code"""
        code = """
# Governance Audit: Test function
try:
    result = do_something()
except Exception as e:
    handle_error(e)
"""
        is_valid, violations = agent._audit_alignment(code)
        assert is_valid is True
        assert len(violations) == 0

    def test_audit_alignment_with_bad_code(self, agent):
        """Test alignment audit with problematic code"""
        code = "x = 5"  # No error handling, no governance comment
        is_valid, violations = agent._audit_alignment(code)
        assert is_valid is False
        assert len(violations) > 0

    def test_estimate_cooling(self, agent):
        """Test cooling estimate"""
        cooling = agent._estimate_cooling()
        assert cooling == 0.04
        assert 0.03 <= cooling <= 0.05  # Within humility band

    def test_verify_cooling(self, agent):
        """Test full cooling verification"""
        claude_response = "This is a substantive constitutional analysis with meaningful content."
        codex_response = """
# Governance Audit: Generated code
try:
    result = process()
except Exception:
    log_error()
"""
        result = agent.verify_cooling(claude_response, codex_response)

        assert "claude_truth_valid" in result
        assert "codex_aligned" in result
        assert "entropy_reduced" in result
        assert result["confidence"] == 0.04
        assert result["estimate_only"] is True
