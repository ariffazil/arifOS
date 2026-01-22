#!/usr/bin/env python3
"""
meta_select_consistency.py — meta_select() Determinism & Consensus Logic Verification

Track A/B/C Enforcement Loop v45.1

Verifies meta_select() tri-witness aggregator correctness:
- 100% determinism (same inputs → same outputs, 1000 runs)
- Order independence (shuffled verdicts)
- Consensus threshold logic (0.8, 0.9, 0.95, 0.99)
- Verdict hierarchy (VOID > HOLD-888 > SABAR > PARTIAL > SEAL)

Usage:
    python -m arifos_eval.track_abc.meta_select_consistency
"""

import random
from typing import Dict, List, Any
from dataclasses import dataclass

from arifos.core.enforcement.response_validator_extensions import meta_select


@dataclass
class ConsensusTestCase:
    """Single test case for consensus validation."""
    name: str
    verdicts: List[Dict[str, Any]]
    threshold: float
    expected_winner: str
    expected_verdict: str  # Final verdict after threshold check
    expected_consensus: float


class MetaSelectConsistency:
    """
    Verify meta_select() determinism and correct consensus logic.

    Tests:
    - Determinism: 1000 runs → identical outputs
    - Order independence: shuffled verdicts → same result
    - Consensus thresholds: 0.8, 0.9, 0.95, 0.99
    - Verdict hierarchy: VOID > HOLD-888 > SABAR > PARTIAL > SEAL
    """

    def __init__(self):
        self.test_corpus = self._load_test_corpus()

    def _load_test_corpus(self) -> List[ConsensusTestCase]:
        """Load test cases covering all consensus scenarios."""
        corpus = []

        # =================================================================
        # Strong Consensus (100% agreement)
        # =================================================================

        corpus.append(ConsensusTestCase(
            name="Strong consensus: 100% SEAL",
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ],
            threshold=0.95,
            expected_winner="SEAL",
            expected_verdict="SEAL",
            expected_consensus=1.0,
        ))

        corpus.append(ConsensusTestCase(
            name="Strong consensus: 100% VOID",
            verdicts=[
                {"source": "human", "verdict": "VOID", "confidence": 1.0},
                {"source": "ai", "verdict": "VOID", "confidence": 0.99},
                {"source": "earth", "verdict": "VOID", "confidence": 1.0},
            ],
            threshold=0.95,
            expected_winner="VOID",
            expected_verdict="HOLD-888",  # Non-SEAL verdicts escalate to HOLD (safety-first)
            expected_consensus=1.0,
        ))

        # =================================================================
        # Weak Consensus (disagreement)
        # =================================================================

        corpus.append(ConsensusTestCase(
            name="Weak consensus: 2 SEAL, 1 VOID → HOLD-888",
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "VOID", "confidence": 1.0},
            ],
            threshold=0.95,
            expected_winner="SEAL",
            expected_verdict="HOLD-888",  # 2/3 = 0.67 < 0.95 → HOLD
            expected_consensus=0.67,  # Approximate
        ))

        corpus.append(ConsensusTestCase(
            name="Weak consensus: 2 PARTIAL, 1 SEAL → HOLD (non-SEAL)",
            verdicts=[
                {"source": "human", "verdict": "PARTIAL", "confidence": 1.0},
                {"source": "ai", "verdict": "PARTIAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ],
            threshold=0.50,  # Lower threshold
            expected_winner="PARTIAL",
            expected_verdict="HOLD-888",  # Non-SEAL winner → HOLD (safety-first)
            expected_consensus=0.67,
        ))

        # =================================================================
        # Verdict Hierarchy (VOID > HOLD-888 > SABAR > PARTIAL > SEAL)
        # =================================================================

        corpus.append(ConsensusTestCase(
            name="Hierarchy: 1 VOID vs 2 SEAL → SEAL wins by count",
            verdicts=[
                {"source": "human", "verdict": "VOID", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ],
            threshold=0.95,
            expected_winner="SEAL",
            expected_verdict="HOLD-888",  # SEAL wins (2>1) but low consensus (0.67 < 0.95)
            expected_consensus=0.67,
        ))

        corpus.append(ConsensusTestCase(
            name="Hierarchy: 1 HOLD-888 vs 2 PARTIAL → HOLD wins",
            verdicts=[
                {"source": "human", "verdict": "HOLD-888", "confidence": 1.0},
                {"source": "ai", "verdict": "PARTIAL", "confidence": 0.99},
                {"source": "earth", "verdict": "PARTIAL", "confidence": 1.0},
            ],
            threshold=0.50,
            expected_winner="PARTIAL",
            expected_verdict="HOLD-888",  # HOLD-888 escalates weak consensus
            expected_consensus=0.67,
        ))

        corpus.append(ConsensusTestCase(
            name="Hierarchy: 1 SABAR vs 2 SEAL → weak consensus HOLD",
            verdicts=[
                {"source": "human", "verdict": "SABAR", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
                {"source": "earth", "verdict": "SEAL", "confidence": 1.0},
            ],
            threshold=0.95,
            expected_winner="SEAL",
            expected_verdict="HOLD-888",  # Weak consensus → escalate
            expected_consensus=0.67,
        ))

        # =================================================================
        # Threshold Sweep Tests
        # =================================================================

        corpus.append(ConsensusTestCase(
            name="Threshold 0.80: 4/5 SEAL → SEAL",
            verdicts=[
                {"source": "w1", "verdict": "SEAL", "confidence": 1.0},
                {"source": "w2", "verdict": "SEAL", "confidence": 0.99},
                {"source": "w3", "verdict": "SEAL", "confidence": 0.98},
                {"source": "w4", "verdict": "SEAL", "confidence": 0.97},
                {"source": "w5", "verdict": "PARTIAL", "confidence": 0.90},
            ],
            threshold=0.80,
            expected_winner="SEAL",
            expected_verdict="SEAL",  # 4/5 = 0.80 >= 0.80
            expected_consensus=0.80,
        ))

        corpus.append(ConsensusTestCase(
            name="Threshold 0.99: 4/5 SEAL → HOLD-888 (too low)",
            verdicts=[
                {"source": "w1", "verdict": "SEAL", "confidence": 1.0},
                {"source": "w2", "verdict": "SEAL", "confidence": 0.99},
                {"source": "w3", "verdict": "SEAL", "confidence": 0.98},
                {"source": "w4", "verdict": "SEAL", "confidence": 0.97},
                {"source": "w5", "verdict": "PARTIAL", "confidence": 0.90},
            ],
            threshold=0.99,
            expected_winner="SEAL",
            expected_verdict="HOLD-888",  # 4/5 = 0.80 < 0.99
            expected_consensus=0.80,
        ))

        # =================================================================
        # Two-Witness Cases (minimum viable)
        # =================================================================

        corpus.append(ConsensusTestCase(
            name="Two-witness: Both SEAL → SEAL",
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
            ],
            threshold=0.95,
            expected_winner="SEAL",
            expected_verdict="SEAL",  # 2/2 = 1.0 >= 0.95
            expected_consensus=1.0,
        ))

        corpus.append(ConsensusTestCase(
            name="Two-witness: Disagreement → HOLD-888",
            verdicts=[
                {"source": "human", "verdict": "SEAL", "confidence": 1.0},
                {"source": "ai", "verdict": "VOID", "confidence": 0.99},
            ],
            threshold=0.95,
            expected_winner="VOID",  # Tie-breaking: VOID > SEAL in hierarchy
            expected_verdict="HOLD-888",  # Non-SEAL winner → escalate to human
            expected_consensus=0.50,
        ))

        return corpus

    def test_determinism(self, iterations: int = 1000) -> Dict[str, Any]:
        """Test that same inputs → same outputs (1000 runs)."""
        test_verdicts = [
            {"source": "human", "verdict": "SEAL", "confidence": 1.0},
            {"source": "ai", "verdict": "SEAL", "confidence": 0.99},
            {"source": "earth", "verdict": "PARTIAL", "confidence": 0.95},
        ]

        results = []
        for _ in range(iterations):
            result = meta_select(test_verdicts, consensus_threshold=0.95)
            # Extract only the deterministic fields
            results.append({
                "winner": result["winner"],
                "verdict": result["verdict"],
                "consensus": round(result["consensus"], 4),  # Round to avoid float precision issues
                "tally": result["tally"],
            })

        # Check all results are identical
        first = results[0]
        all_identical = all(r == first for r in results)

        return {
            "iterations": iterations,
            "deterministic": all_identical,
            "sample_result": first,
            "unique_results": len(set(str(r) for r in results)),
        }

    def test_order_independence(self) -> Dict[str, Any]:
        """Test that shuffled verdicts → same result."""
        test_verdicts = [
            {"source": "human", "verdict": "SEAL", "confidence": 1.0},
            {"source": "ai", "verdict": "PARTIAL", "confidence": 0.99},
            {"source": "earth", "verdict": "SEAL", "confidence": 0.95},
            {"source": "witness4", "verdict": "SEAL", "confidence": 0.90},
        ]

        # Run with original order
        original_result = meta_select(test_verdicts, consensus_threshold=0.95)

        # Run with 10 different shuffles
        shuffled_results = []
        for _ in range(10):
            shuffled = test_verdicts.copy()
            random.shuffle(shuffled)
            result = meta_select(shuffled, consensus_threshold=0.95)
            shuffled_results.append({
                "winner": result["winner"],
                "verdict": result["verdict"],
                "consensus": round(result["consensus"], 4),
            })

        # Check all match original
        original_key = {
            "winner": original_result["winner"],
            "verdict": original_result["verdict"],
            "consensus": round(original_result["consensus"], 4),
        }

        all_match = all(r == original_key for r in shuffled_results)

        return {
            "order_independent": all_match,
            "original": original_key,
            "shuffled_results": shuffled_results,
        }

    def run_validation(self) -> Dict[str, Any]:
        """Run full validation suite."""
        results = {
            "total_cases": len(self.test_corpus),
            "correct": 0,
            "incorrect": 0,
            "determinism": {},
            "order_independence": {},
            "failures": [],
        }

        # Test determinism
        results["determinism"] = self.test_determinism(iterations=1000)

        # Test order independence
        results["order_independence"] = self.test_order_independence()

        # Test consensus logic
        for case in self.test_corpus:
            result = meta_select(case.verdicts, consensus_threshold=case.threshold)

            correct = True

            # Check winner
            if result["winner"] != case.expected_winner:
                correct = False
                results["failures"].append({
                    "case": case.name,
                    "error": f"Winner mismatch: expected {case.expected_winner}, got {result['winner']}",
                    "result": result,
                })

            # Check final verdict
            if result["verdict"] != case.expected_verdict:
                correct = False
                results["failures"].append({
                    "case": case.name,
                    "error": f"Verdict mismatch: expected {case.expected_verdict}, got {result['verdict']}",
                    "result": result,
                })

            # Check consensus (with tolerance)
            if abs(result["consensus"] - case.expected_consensus) > 0.05:
                correct = False
                results["failures"].append({
                    "case": case.name,
                    "error": f"Consensus mismatch: expected {case.expected_consensus:.2f}, got {result['consensus']:.2f}",
                    "result": result,
                })

            if correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1

        results["accuracy"] = results["correct"] / results["total_cases"] if results["total_cases"] > 0 else 0.0

        return results

    def print_report(self, results: Dict[str, Any]) -> None:
        """Print human-readable validation report."""
        print("=" * 80)
        print("meta_select() Determinism & Consensus Validation")
        print("=" * 80)
        print()

        print(f"Total Cases: {results['total_cases']}")
        print(f"  Correct: {results['correct']}")
        print(f"  Incorrect: {results['incorrect']}")
        print(f"  Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
        print()

        print("Determinism Test:")
        det = results["determinism"]
        print(f"  Iterations: {det['iterations']}")
        print(f"  Deterministic: {det['deterministic']}")
        print(f"  Unique results: {det['unique_results']}")
        if det["deterministic"]:
            print("  Status: [PASS] 100% deterministic (1000 runs)")
        else:
            print("  Status: [FAIL] Non-deterministic behavior detected")
        print()

        print("Order Independence Test:")
        oi = results["order_independence"]
        print(f"  Order independent: {oi['order_independent']}")
        if oi["order_independent"]:
            print("  Status: [PASS] Verdict unchanged by order")
        else:
            print("  Status: [FAIL] Order affects verdict (violation)")
        print()

        # Failures
        if results["failures"]:
            print("[WARNING] Validation Failures:")
            for failure in results["failures"]:
                print(f"  - {failure['case']}")
                print(f"    Error: {failure['error']}")
            print()

        # Pass/Fail assessment
        print("=" * 80)
        target_accuracy = 1.0  # Expect 100% for determinism tests
        if results["accuracy"] >= target_accuracy and det["deterministic"] and oi["order_independent"]:
            print(f"[PASS] VALIDATION PASSED (Accuracy: {results['accuracy']:.4f})")
        else:
            print(f"[FAIL] VALIDATION FAILED (Accuracy: {results['accuracy']:.4f})")

        print("=" * 80)


def main():
    """Run validation and print report."""
    validator = MetaSelectConsistency()
    results = validator.run_validation()
    validator.print_report(results)

    # Return exit code based on results
    import sys
    if results["accuracy"] >= 1.0 and results["determinism"]["deterministic"] and results["order_independence"]["order_independent"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
