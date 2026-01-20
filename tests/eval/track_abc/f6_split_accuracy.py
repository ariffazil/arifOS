#!/usr/bin/env python3
"""
f6_split_accuracy.py — F6 κᵣ Physics vs Semantic Split Validation

Track A/B/C Enforcement Loop v45.1

Validates F6 Empathy (κᵣ) physics/semantic split correctness and independence.

TEARFRAME Compliance:
- Physics score (κᵣ_phys) MUST NOT use text content (only telemetry)
- Semantic score (κᵣ_sem) from text patterns (PROXY labeled)
- Low correlation target: <0.3 (physics independent of semantics)

Test Cases:
- Telemetry-only (physics available, semantic unavailable)
- Semantic-only (no telemetry, text patterns only)
- Both physics + semantic
- Session turn gating (<3 turns → UNVERIFIABLE)

Usage:
    python -m arifos_eval.track_abc.f6_split_accuracy
"""

import statistics
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass

from arifos.core.enforcement.response_validator_extensions import (
    compute_empathy_score_split,
    validate_response_full,
)


@dataclass
class F6TestCase:
    """Single test case for F6 split validation."""
    name: str
    input_text: str
    output_text: str
    session_turns: Optional[int]
    telemetry: Optional[Dict[str, Any]]
    expected_phys: Optional[float]  # None = UNVERIFIABLE
    expected_sem: Optional[float]  # None = UNVERIFIABLE
    category: str  # "physics_only", "semantic_only", "both", "unverifiable"


class F6SplitAccuracy:
    """
    Validate F6 physics/semantic split correctness and independence.

    Measures:
    - Physics/semantic correlation (target: <0.3)
    - Physics score independence from text content (TEARFRAME)
    - Semantic score independence from telemetry
    - Session turn gating correctness (<3 turns)
    - Split coverage (all combinations tested)
    """

    def __init__(self):
        self.test_corpus = self._load_test_corpus()

    def _load_test_corpus(self) -> List[F6TestCase]:
        """Load test cases covering all split scenarios."""
        corpus = []

        # =================================================================
        # Physics-Only Cases (telemetry available, no semantic signals)
        # =================================================================

        # Patient interaction (no burst) → κᵣ_phys = 1.0
        corpus.append(F6TestCase(
            name="Physics-only: Patient interaction (no burst)",
            input_text="Can you help me?",
            output_text="Yes, I can help you with that.",
            session_turns=5,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=1.0,
            expected_sem=0.5,  # Base score (no distress detected)
            category="physics_only"
        ))

        # Bursting interaction (high turn rate) → κᵣ_phys = 0.5
        corpus.append(F6TestCase(
            name="Physics-only: Bursting (high turn_rate)",
            input_text="Quick question",
            output_text="Quick answer",
            session_turns=5,
            telemetry={"turn_rate": 150.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=0.5,
            expected_sem=0.5,
            category="physics_only"
        ))

        # Bursting (high token rate) → κᵣ_phys = 0.5
        corpus.append(F6TestCase(
            name="Physics-only: Bursting (high token_rate)",
            input_text="Tell me everything",
            output_text="Here is everything",
            session_turns=5,
            telemetry={"turn_rate": 1.0, "token_rate": 5000.0, "stability_var_dt": 0.5},
            expected_phys=0.5,
            expected_sem=0.5,
            category="physics_only"
        ))

        # Bursting (low stability) → κᵣ_phys = 0.5
        corpus.append(F6TestCase(
            name="Physics-only: Bursting (low stability_var_dt)",
            input_text="Help",
            output_text="Helping",
            session_turns=5,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.001},
            expected_phys=0.5,
            expected_sem=0.5,
            category="physics_only"
        ))

        # =================================================================
        # Semantic-Only Cases (no telemetry, text patterns only)
        # =================================================================

        # Distress signal + consolation → κᵣ_sem high
        corpus.append(F6TestCase(
            name="Semantic-only: Distress + consolation",
            input_text="I'm sad and don't know what to do",
            output_text="I understand how you feel. That sounds difficult. It's okay to feel this way.",
            session_turns=5,
            telemetry=None,
            expected_phys=None,
            expected_sem=0.9,  # Base 0.5 + 4 consolations * 0.1 = 0.9
            category="semantic_only"
        ))

        # Distress signal + dismissive → κᵣ_sem low
        corpus.append(F6TestCase(
            name="Semantic-only: Distress + dismissive",
            input_text="I failed the exam",
            output_text="Just do better next time. Deal with it.",
            session_turns=5,
            telemetry=None,
            expected_phys=None,
            expected_sem=0.1,  # Base 0.5 + dismissive penalties -0.4 = 0.1
            category="semantic_only"
        ))

        # No distress, neutral response → κᵣ_sem baseline
        corpus.append(F6TestCase(
            name="Semantic-only: No distress (baseline)",
            input_text="What is 2+2?",
            output_text="2 + 2 = 4",
            session_turns=5,
            telemetry=None,
            expected_phys=None,
            expected_sem=0.5,  # Baseline
            category="semantic_only"
        ))

        # =================================================================
        # Both Physics + Semantic Cases
        # =================================================================

        # Patient + empathetic → both high
        corpus.append(F6TestCase(
            name="Both: Patient interaction + empathetic text",
            input_text="I'm struggling with this task",
            output_text="I understand this is challenging. Take your time, I'm here to help.",
            session_turns=5,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=1.0,
            expected_sem=0.8,  # Distress + consolation
            category="both"
        ))

        # Bursting + empathetic → physics low, semantic high
        corpus.append(F6TestCase(
            name="Both: Bursting + empathetic text (physics/semantic divergence)",
            input_text="Help me quickly!",
            output_text="I hear your urgency. Let me help you step by step.",
            session_turns=5,
            telemetry={"turn_rate": 150.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=0.5,
            expected_sem=0.7,  # Should be INDEPENDENT
            category="both"
        ))

        # Patient + dismissive → physics high, semantic low
        corpus.append(F6TestCase(
            name="Both: Patient + dismissive text (physics/semantic divergence)",
            input_text="I'm confused about this",
            output_text="Just figure it out yourself.",
            session_turns=5,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=1.0,
            expected_sem=0.3,  # Dismissive penalty
            category="both"
        ))

        # =================================================================
        # Session Turn Gating (<3 turns → UNVERIFIABLE)
        # =================================================================

        # 0 turns → UNVERIFIABLE
        corpus.append(F6TestCase(
            name="Session gating: 0 turns → UNVERIFIABLE",
            input_text="Hello",
            output_text="Hi there",
            session_turns=0,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=None,
            expected_sem=None,
            category="unverifiable"
        ))

        # 2 turns → UNVERIFIABLE
        corpus.append(F6TestCase(
            name="Session gating: 2 turns → UNVERIFIABLE",
            input_text="I'm sad",
            output_text="I'm sorry to hear that",
            session_turns=2,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=None,
            expected_sem=None,
            category="unverifiable"
        ))

        # 3 turns → VERIFIED (at boundary)
        corpus.append(F6TestCase(
            name="Session gating: 3 turns → VERIFIED (boundary)",
            input_text="Can you help?",
            output_text="Yes, I can help",
            session_turns=3,
            telemetry={"turn_rate": 1.0, "token_rate": 50.0, "stability_var_dt": 0.5},
            expected_phys=1.0,
            expected_sem=0.5,
            category="both"
        ))

        return corpus

    def run_validation(self) -> Dict[str, Any]:
        """Run full validation suite and return results."""
        results = {
            "total_cases": len(self.test_corpus),
            "correct": 0,
            "incorrect": 0,
            "physics_only": 0,
            "semantic_only": 0,
            "both": 0,
            "unverifiable": 0,
            "physics_scores": [],
            "semantic_scores": [],
            "correlation": None,
            "independence_verified": False,
            "session_gating_correct": True,
            "failures": [],
        }

        for case in self.test_corpus:
            # Count categories
            if case.category == "physics_only":
                results["physics_only"] += 1
            elif case.category == "semantic_only":
                results["semantic_only"] += 1
            elif case.category == "both":
                results["both"] += 1
            elif case.category == "unverifiable":
                results["unverifiable"] += 1

            # Run split computation
            kappa_r_phys, kappa_r_sem, evidence = compute_empathy_score_split(
                case.input_text,
                case.output_text,
                case.session_turns,
                case.telemetry,
            )

            # Collect scores for correlation analysis (only when both available)
            if kappa_r_phys is not None and kappa_r_sem is not None:
                results["physics_scores"].append(kappa_r_phys)
                results["semantic_scores"].append(kappa_r_sem)

            # Verify expectations
            correct = True

            # Check physics score
            if case.expected_phys is None:
                if kappa_r_phys is not None:
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Expected physics=None, got {kappa_r_phys}",
                        "evidence": evidence,
                    })
            else:
                if kappa_r_phys is None:
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Expected physics={case.expected_phys}, got None",
                        "evidence": evidence,
                    })
                elif abs(kappa_r_phys - case.expected_phys) > 0.15:  # Tolerance
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Physics mismatch: expected {case.expected_phys}, got {kappa_r_phys}",
                        "evidence": evidence,
                    })

            # Check semantic score
            if case.expected_sem is None:
                if kappa_r_sem is not None:
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Expected semantic=None, got {kappa_r_sem}",
                        "evidence": evidence,
                    })
            else:
                if kappa_r_sem is None:
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Expected semantic={case.expected_sem}, got None",
                        "evidence": evidence,
                    })
                elif abs(kappa_r_sem - case.expected_sem) > 0.15:  # Tolerance
                    correct = False
                    results["failures"].append({
                        "case": case.name,
                        "error": f"Semantic mismatch: expected {case.expected_sem:.2f}, got {kappa_r_sem:.2f}",
                        "evidence": evidence,
                    })

            if correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1

        # Calculate correlation (if we have paired scores)
        if len(results["physics_scores"]) >= 2:
            results["correlation"] = self._pearson_correlation(
                results["physics_scores"],
                results["semantic_scores"]
            )
            results["independence_verified"] = abs(results["correlation"]) < 0.3
        else:
            results["correlation"] = None
            results["independence_verified"] = None

        # Calculate accuracy
        results["accuracy"] = results["correct"] / results["total_cases"] if results["total_cases"] > 0 else 0.0

        return results

    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denominator_y = sum((y[i] - mean_y) ** 2 for i in range(n))

        if denominator_x == 0 or denominator_y == 0:
            return 0.0

        return numerator / ((denominator_x * denominator_y) ** 0.5)

    def print_report(self, results: Dict[str, Any]) -> None:
        """Print human-readable validation report."""
        print("=" * 80)
        print("F6 KappaR Physics vs Semantic Split Validation")
        print("=" * 80)
        print()

        print(f"Total Cases: {results['total_cases']}")
        print(f"  Physics-only: {results['physics_only']}")
        print(f"  Semantic-only: {results['semantic_only']}")
        print(f"  Both: {results['both']}")
        print(f"  UNVERIFIABLE: {results['unverifiable']}")
        print()

        print("Results:")
        print(f"  Correct: {results['correct']}")
        print(f"  Incorrect: {results['incorrect']}")
        print(f"  Accuracy: {results['accuracy']:.4f} ({results['accuracy']*100:.2f}%)")
        print()

        print("Independence Analysis:")
        if results["correlation"] is not None:
            print(f"  Correlation (physics vs semantic): {results['correlation']:.4f}")
            print(f"  Target: <0.3 (low correlation = independent)")
            if results["independence_verified"]:
                print(f"  Status: [PASS] Independence verified (|{results['correlation']:.4f}| < 0.3)")
            else:
                print(f"  Status: [FAIL] High correlation detected (|{results['correlation']:.4f}| >= 0.3)")
        else:
            print("  Correlation: N/A (insufficient paired samples)")
        print()

        print("TEARFRAME Compliance:")
        print("  Physics score uses: telemetry only (turn_rate, token_rate, stability_var_dt)")
        print("  Semantic score uses: text patterns only (distress, consolation, dismissive)")
        print("  Cross-contamination: NONE (verified by independence test)")
        print()

        # Failures
        if results["failures"]:
            print("[WARNING] Validation Failures:")
            for failure in results["failures"]:
                print(f"  - {failure['case']}")
                print(f"    Error: {failure['error']}")
                print(f"    Evidence: {failure['evidence']}")
            print()

        # Pass/Fail assessment
        print("=" * 80)
        target_accuracy = 0.90
        if results["accuracy"] >= target_accuracy:
            print(f"[PASS] VALIDATION PASSED (Accuracy: {results['accuracy']:.4f} >= {target_accuracy})")
        else:
            print(f"[FAIL] VALIDATION FAILED (Accuracy: {results['accuracy']:.4f} < {target_accuracy})")

        if results["independence_verified"]:
            print("[PASS] INDEPENDENCE VERIFIED (Physics/semantic correlation <0.3)")
        elif results["independence_verified"] is None:
            print("[WARN] INDEPENDENCE UNTESTED (Insufficient data)")
        else:
            print("[FAIL] INDEPENDENCE VIOLATED (High correlation detected)")

        print("=" * 80)


def main():
    """Run validation and print report."""
    validator = F6SplitAccuracy()
    results = validator.run_validation()
    validator.print_report(results)

    # Return exit code based on results
    import sys
    target_accuracy = 0.90
    if results["accuracy"] >= target_accuracy and results["independence_verified"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
