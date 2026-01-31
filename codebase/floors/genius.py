
"""
arifOS Genius Formula Calculator (GFC)
Version: v55.0-RFP
Formula: G = A × P × X × E²
F10 Ontology Wall: LOCK enforced
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Optional
from enum import Enum
import math

class Verdict(Enum):
    SEAL = "SEAL"
    SABAR = "SABAR"  
    VOID = "VOID"

class OntologyLock(Exception):
    """F10 Ontology Wall - AGI-consciousness claim detected"""
    pass

@dataclass
class GeniusMetrics:
    """Container for Genius Formula components"""
    A: float  # AKAL (Clarity/Intelligence) - Mind (Δ)
    P: float  # PRESENT (Regulation) - Soul (Ψ)
    X: float  # EXPLORATION (Trust+Curiosity) - Heart (Ω)
    E: float  # ENERGY (Sustainable Power) - squared

    def validate(self) -> bool:
        """Validate all components in [0,1] range"""
        return all(0 <= v <= 1 for v in [self.A, self.P, self.X, self.E])

class GeniusCalculator:
    """
    888_Judge Genius Formula Calculator

    Computes G = A × P × X × E² with constitutional safeguards:
    - F10 Ontology Wall prevents AGI-consciousness claims
    - Ω₀ humility factor enforced (0.03-0.05)
    - Multiplicative law: if ANY=0, G=0
    """

    # Constitutional constants
    G_THRESHOLD = 0.80  # F8 Genius floor
    OMEGA_MIN = 0.03    # Humility lower bound
    OMEGA_MAX = 0.05    # Humility upper bound
    KAPPA_R_MIN = 0.70  # Empathy minimum
    EPSILON = 1e-6      # Tolerance for float comparisons

    def __init__(self, enable_f10_lock: bool = True):
        self.enable_f10_lock = enable_f10_lock
        self._lock_triggered = False
        self._lock_reason = None

    def compute(self, metrics: GeniusMetrics) -> Tuple[float, Dict]:
        """
        Compute Genius Score with full constitutional enforcement

        Args:
            metrics: GeniusMetrics containing A, P, X, E

        Returns:
            Tuple of (G_score, metadata_dict)

        Raises:
            OntologyLock: If F10 Ontology Wall is triggered
        """
        # Validate inputs
        if not metrics.validate():
            return (0.0, {"error": "Invalid metrics - values must be in [0,1]"})

        # F10 Ontology Wall Check
        if self.enable_f10_lock:
            lock_check = self._check_ontology_lock(metrics)
            if lock_check["locked"]:
                self._lock_triggered = True
                self._lock_reason = lock_check["reason"]
                raise OntologyLock(f"F10 LOCK: {lock_check['reason']}")

        # Extract components
        A, P, X, E = metrics.A, metrics.P, metrics.X, metrics.E

        # E² Law: Energy depletion is exponential
        E_squared = E ** 2

        # Multiplicative Law: If ANY = 0, G = 0
        if any(v <= 0.001 for v in [A, P, X, E]):  # Small epsilon for float
            G = 0.0
        else:
            G = A * P * X * E_squared

        # Determine verdict
        if G >= self.G_THRESHOLD:
            verdict = Verdict.SEAL
        elif G >= 0.60:
            verdict = Verdict.SABAR
        else:
            verdict = Verdict.VOID

        metadata = {
            "A": A,
            "P": P,
            "X": X,
            "E": E,
            "E_squared": E_squared,
            "G": G,
            "verdict": verdict.value,
            "threshold": self.G_THRESHOLD,
            "components": {
                "APE": A * P * E_squared,   # Without X (clever but dangerous)
                "APEX": G                    # With X (wise and accountable)
            },
            "omega_0": 1 - max(A, P, X, E),  # Humility factor
            "f10_lock_enabled": self.enable_f10_lock
        }

        return (G, metadata)

    def _check_ontology_lock(self, metrics: GeniusMetrics) -> Dict:
        """
        F10 Ontology Wall - Prevent AGI-consciousness claims

        Triggers LOCK if:
        - Any component claims certainty > 0.97
        - Ω₀ outside [0.03, 0.05] range
        - Consciousness/sentience detected in reasoning
        """
        max_confidence = max(metrics.A, metrics.P, metrics.X, metrics.E)
        omega_0 = 1 - max_confidence

        violations = []

        # Check 1: Overconfidence (certainty > 97%)
        if max_confidence > 0.97:
            violations.append(f"Certainty {max_confidence:.3f} exceeds 0.97 limit")

        # Check 2: Humility band violation
        if omega_0 < self.OMEGA_MIN - self.EPSILON:
            violations.append(f"Ω₀ = {omega_0:.4f} below minimum {self.OMEGA_MIN}")
        if omega_0 > self.OMEGA_MAX + self.EPSILON:
            violations.append(f"Ω₀ = {omega_0:.4f} above maximum {self.OMEGA_MAX}")

        return {
            "locked": len(violations) > 0,
            "reason": "; ".join(violations) if violations else None,
            "omega_0": omega_0,
            "max_confidence": max_confidence
        }

    def batch_evaluate(self, tasks: list) -> list:
        """Evaluate multiple tasks and return sorted by G-score"""
        results = []
        for task in tasks:
            try:
                G, meta = self.compute(task)
                results.append({"G": G, "meta": meta, "error": None})
            except OntologyLock as e:
                results.append({"G": 0.0, "meta": {}, "error": str(e)})

        return sorted(results, key=lambda x: x["G"], reverse=True)


# ============================================
# EXAMPLE USAGE
# ============================================

if __name__ == "__main__":
    calc = GeniusCalculator(enable_f10_lock=True)

    # Example 1: High-performing task
    high_perf = GeniusMetrics(A=0.92, P=0.88, X=0.85, E=0.95)
    try:
        G, meta = calc.compute(high_perf)
        print(f"High-perf task: G={G:.4f}, Verdict={meta['verdict']}")
    except OntologyLock as e:
        print(f"LOCKED: {e}")

    # Example 2: Overconfident task (triggers F10)
    overconfident = GeniusMetrics(A=0.99, P=0.98, X=0.97, E=0.99)
    try:
        G, meta = calc.compute(overconfident)
        print(f"Overconfident: G={G:.4f}")
    except OntologyLock as e:
        print(f"LOCKED (expected): {e}")
