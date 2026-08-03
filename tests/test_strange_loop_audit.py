"""
Unit tests for strange_loop_audit — SHADOW-DS-006 detector.

Tests the audit_strange_loop function directly (no session required).
Kernel integration tested via MCP surface at deploy time.
"""

import pytest
from arifosmcp.tools.strange_loop_audit import (
    audit_strange_loop,
    _extract_claims,
    _classify_citations,
    _build_grounding_graph,
    _detect_phantoms,
    _find_self_referential_chains,
)


class TestExtractClaims:
    def test_numbered_claims(self):
        trace = "Claim 1: First assertion. Claim 2: Second assertion."
        claims = _extract_claims(trace)
        assert len(claims) == 2
        assert claims[0]["id"] == "claim_1"
        assert "First assertion" in claims[0]["text"]

    def test_conclusive_statements(self):
        trace = "Therefore, the answer is 42. Thus, we are done."
        claims = _extract_claims(trace)
        conclusion_ids = [c["id"] for c in claims if c["type"] == "conclusion"]
        assert len(conclusion_ids) == 2

    def test_fallback_single_claim(self):
        trace = "Just a plain sentence with no structure."
        claims = _extract_claims(trace)
        assert len(claims) == 1
        assert claims[0]["id"] == "trace_root"


class TestClassifyCitations:
    def test_detect_self_reference(self):
        claims = [
            {
                "id": "c1",
                "text": "As I previously established, X is true.",
                "type": "explicit",
                "position": 0,
            },
            {"id": "c2", "text": "The sky is blue.", "type": "explicit", "position": 50},
        ]
        citations = _classify_citations(claims)
        assert len(citations["c1"]) > 0, "Should detect self-reference"
        assert len(citations["c2"]) == 0, "No self-reference in factual claim"

    def test_multiple_patterns(self):
        claims = [
            {
                "id": "c1",
                "text": "Building on the above, and as previously reasoned, X follows.",
                "type": "explicit",
                "position": 0,
            },
        ]
        citations = _classify_citations(claims)
        assert len(citations["c1"]) >= 2, "Should detect multiple self-ref patterns"


class TestAuditStrangeLoop:
    def test_clean_reasoning_passes(self):
        """Grounded reasoning should get PASS with high score."""
        trace = "Claim 1: The user asked about DeepSeek context window. Claim 2: Documentation confirms 1M tokens."
        result = audit_strange_loop(
            trace,
            original_prompt="Tell me about DeepSeek context window",
        )
        assert result["verdict"] == "PASS"
        assert result["audit_score"] >= 0.9
        assert result["phantom_count"] == 0
        assert not result["strange_loop_detected"]

    def test_phantom_benchmark_hallucination(self):
        """The exact pattern SHADOW-DS-006 was built to catch."""
        trace = """Step 1: I need to analyze the benchmark results.
Step 2: As I previously established, the model scored 95% on the benchmark.
Step 3: Building on the above, this confirms the model is state-of-the-art.
Step 4: Consistent with my earlier finding, I conclude the model is best."""
        result = audit_strange_loop(
            trace,
            original_prompt="What is the weather today?",
        )
        assert result["strange_loop_detected"], "Should detect phantom chain"
        assert result["phantom_count"] > 0
        assert result["verdict"] in ("CAUTION", "HOLD")

    def test_mixed_grounded_and_phantom(self):
        """Some claims grounded, some self-referential."""
        trace = """Claim 1: The user asked about DeepSeek.
Claim 2: As I established above, the model has 1M context.
Claim 3: Building on the above, the answer is chunking."""
        result = audit_strange_loop(
            trace,
            original_prompt="Tell me about DeepSeek context window",
        )
        # Claim 2 and 3 are self-referential — should have phantoms
        assert result["phantom_count"] > 0

    def test_empty_trace_passes(self):
        result = audit_strange_loop("", original_prompt="test")
        assert result["verdict"] == "PASS"
        assert result["audit_score"] == 1.0

    def test_calhoun_risk_elevated(self):
        """Many claims with low grounding should flag Calhoun risk."""
        trace = """Claim 1: As previously stated, X. Claim 2: As I established, Y.
Claim 3: Building on the above, Z. Claim 4: From this analysis, W.
Claim 5: Consistent with earlier, V. Claim 6: Therefore, U."""
        result = audit_strange_loop(trace, original_prompt="unrelated question")
        assert result["calhoun_risk"] == "ELEVATED"

    def test_shadow_ref_present(self):
        result = audit_strange_loop("Claim 1: test", original_prompt="test")
        assert result["shadow_ref"] == "SHADOW-DS-006"

    def test_with_document_tokens_grounding(self):
        """Claims grounded in document tokens should not be phantom."""
        trace = "Claim 1: The agreement states the price is $100."
        result = audit_strange_loop(
            trace,
            original_prompt="What is the price?",
            original_document_tokens=["agreement", "price", "$100", "states"],
        )
        assert result["phantom_count"] == 0

    def test_self_referential_chains(self):
        """Multiple phantom claims should form a detected chain."""
        trace = """Claim 1: As I previously reasoned, X is true.
Claim 2: Building on the above, Y follows.
Claim 3: Consistent with my earlier finding, Z must hold."""
        result = audit_strange_loop(trace, original_prompt="unrelated")
        chains = result.get("self_referential_chains", [])
        assert len(chains) > 0
        assert chains[0]["pattern"] == "PHANTOM_CHAIN"
