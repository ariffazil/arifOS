
import unittest
from codebase.agi.evidence import estimate_precision, compute_precision_weighted_update
from codebase.agi.stages.reason import _apply_precision_updates
from codebase.agi.stages.sense import ParsedFact, FactType
from codebase.bundles import Hypothesis, ThinkOutput
from unittest.mock import MagicMock

class TestPrecisionWeighting(unittest.TestCase):
    def test_estimate_precision(self):
        # Test known values
        self.assertAlmostEqual(estimate_precision(0.5), 4.0)
        self.assertAlmostEqual(estimate_precision(0.0), 1.0) # clamped to 0.01 internally?
        # 0.9 -> 1/(0.1)^2 = 100
        self.assertAlmostEqual(estimate_precision(0.9), 100.0)
        
    def test_compute_precision_weighted_update(self):
        # Prior 0.5 (Weak), Evidence 0.9 (Strong)
        # pi_p = 4, pi_e = 100. Weight = 100/104 ~ 0.96
        # update = 0.96 * (0.9 - 0.5) = 0.96 * 0.4 = 0.384
        # new = 0.5 + 0.384 = 0.884
        prior = 0.5
        evidence = 0.9
        error = evidence - prior
        new_val = compute_precision_weighted_update(prior, evidence, error)
        self.assertGreater(new_val, 0.8)
        self.assertLess(new_val, 0.95)

    def test_apply_precision_updates(self):
        # Setup Hypothesis
        h = MagicMock(spec=Hypothesis)
        h.content = "Test Hypothesis"
        h.path_type = "conservative"
        h.confidence = 0.5
        h.supporting_facts = ["Fact A"]
        
        # Setup ThinkOutput
        think = MagicMock(spec=ThinkOutput)
        think.conservative = h
        think.exploratory = None
        think.adversarial = None
        
        # Setup Facts
        f1 = ParsedFact(id="1", content="Fact A", fact_type=FactType.STATISTIC, confidence=0.9, source="test")
        facts = [f1]
        
        # Execute
        _apply_precision_updates(think, facts)
        
        # Verify confidence increased
        # Expecting around 0.88 from previous calculation
        self.assertGreater(h.confidence, 0.8)

if __name__ == "__main__":
    unittest.main()
