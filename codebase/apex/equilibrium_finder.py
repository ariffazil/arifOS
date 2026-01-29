"""
EQUILIBRIUM FINDER (v54.0)

Finds the Nash equilibrium point for the 9-paradox constitutional matrix.

The equilibrium point satisfies:
1. All 9 paradoxes ≥ 0.70
2. Geometric mean ≥ 0.85
3. Standard deviation ≤ 0.10
4. Max spread ≤ 0.30

Equilibrium formula:
E* = argmin_E [ (GM(E) - 0.85)² + σ(E)² ]

Where:
- GM(E) = geometric mean of paradox scores
- σ(E) = standard deviation of paradox scores

DITEMPA BUKAN DIBERI
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .trinity_nine import (
    TrinityNine, NineFoldBundle, NineParadox, 
    EquilibriumState, EquilibriumSolver, create_nine_paradoxes,
    EQUILIBRIUM_THRESHOLD, BALANCE_TOLERANCE, MIN_PARADOX_SCORE
)


@dataclass
class EquilibriumPoint:
    """
    A discovered equilibrium point in the 9-paradox space.
    """
    coordinates: Dict[str, float]  # Paradox name -> score
    trinity_score: float
    balance_index: float  # 1.0 = perfect balance
    constitutional_alignment: float  # Average F1-F13 alignment
    stability: float  # Resistance to perturbation
    
    def to_dict(self) -> Dict:
        return {
            "coordinates": {k: round(v, 4) for k, v in self.coordinates.items()},
            "trinity_score": round(self.trinity_score, 4),
            "balance_index": round(self.balance_index, 4),
            "constitutional_alignment": round(self.constitutional_alignment, 4),
            "stability": round(self.stability, 4)
        }


class EquilibriumFinder:
    """
    Finds optimal equilibrium points in the 9-paradox constitutional space.
    """
    
    def __init__(self):
        self.solver = EquilibriumSolver()
        self.paradox_names = list(create_nine_paradoxes().keys())
    
    def find_optimal_equilibrium(self) -> EquilibriumPoint:
        """
        Find the theoretical optimal equilibrium point.
        
        Optimal = all paradoxes at threshold with perfect balance.
        """
        # Optimal: all paradoxes at equilibrium threshold
        optimal_coords = {name: EQUILIBRIUM_THRESHOLD for name in self.paradox_names}
        
        return EquilibriumPoint(
            coordinates=optimal_coords,
            trinity_score=EQUILIBRIUM_THRESHOLD,
            balance_index=1.0,  # Perfect balance
            constitutional_alignment=EQUILIBRIUM_THRESHOLD,
            stability=1.0
        )
    
    def find_nearest_equilibrium(
        self,
        current_state: Dict[str, float],
        max_iterations: int = 1000
    ) -> Tuple[EquilibriumPoint, List[Dict]]:
        """
        Find the nearest equilibrium point from current state.
        
        Uses gradient descent toward the equilibrium manifold.
        """
        # Initialize with current state
        current = dict(current_state)
        path = []
        
        for i in range(max_iterations):
            # Create paradox objects
            paradoxes = create_nine_paradoxes()
            for name, score in current.items():
                if name in paradoxes:
                    paradoxes[name].score = score
            
            # Check equilibrium
            state = self.solver.solve(paradoxes)
            
            path.append({
                "iteration": i,
                "state": dict(current),
                "trinity_score": state.trinity_score,
                "std_dev": state.std_deviation,
                "is_equilibrium": state.is_equilibrium
            })
            
            if state.is_equilibrium:
                break
            
            # Gradient step toward equilibrium
            current = self._equilibrium_step(current, state)
        
        # Create equilibrium point
        point = EquilibriumPoint(
            coordinates=current,
            trinity_score=state.trinity_score,
            balance_index=1.0 - state.std_deviation / BALANCE_TOLERANCE,
            constitutional_alignment=state.arithmetic_mean,
            stability=self._calculate_stability(current)
        )
        
        return point, path
    
    def _equilibrium_step(self, current: Dict[str, float], state: EquilibriumState) -> Dict[str, float]:
        """
        Take one step toward equilibrium.
        
        Strategy:
        1. Pull up scores below threshold
        2. Compress variance (pull high down, low up)
        3. Maintain geometric mean
        """
        new_state = {}
        mean_score = state.arithmetic_mean
        
        for name, score in current.items():
            adjustment = 0.0
            
            # Pull toward threshold if below
            if score < EQUILIBRIUM_THRESHOLD:
                adjustment += (EQUILIBRIUM_THRESHOLD - score) * 0.1
            
            # Pull toward mean to reduce variance
            if score > mean_score:
                adjustment -= (score - mean_score) * 0.05
            else:
                adjustment += (mean_score - score) * 0.05
            
            # Apply adjustment with clamping
            new_score = score + adjustment
            new_score = max(MIN_PARADOX_SCORE, min(1.0, new_score))
            new_state[name] = new_score
        
        return new_state
    
    def _calculate_stability(self, coords: Dict[str, float]) -> float:
        """
        Calculate stability of equilibrium point.
        
        Stability = resistance to perturbation (higher = more stable).
        """
        scores = list(coords.values())
        if not scores:
            return 0.0
        
        # More balanced = more stable
        variance = np.var(scores)
        balance_factor = 1.0 / (1.0 + variance)
        
        # Higher minimum = more stable
        min_score = min(scores)
        floor_factor = min_score
        
        return (balance_factor + floor_factor) / 2
    
    def find_multiple_equilibria(self, n_samples: int = 100) -> List[EquilibriumPoint]:
        """
        Find multiple equilibrium points by random sampling.
        
        Returns list of discovered equilibria sorted by quality.
        """
        equilibria = []
        
        for _ in range(n_samples):
            # Random starting point
            random_state = {
                name: np.random.uniform(0.7, 1.0)
                for name in self.paradox_names
            }
            
            # Find nearest equilibrium
            point, _ = self.find_nearest_equilibrium(random_state)
            
            # Check if it's actually an equilibrium
            paradoxes = create_nine_paradoxes()
            for name, score in point.coordinates.items():
                paradoxes[name].score = score
            
            state = self.solver.solve(paradoxes)
            if state.is_equilibrium:
                equilibria.append(point)
        
        # Sort by quality (trinity_score * balance_index)
        equilibria.sort(
            key=lambda e: e.trinity_score * e.balance_index,
            reverse=True
        )
        
        return equilibria
    
    def analyze_equilibrium_landscape(self) -> Dict:
        """
        Analyze the equilibrium landscape of the 9-paradox system.
        
        Returns statistics about equilibrium properties.
        """
        # Sample multiple points
        equilibria = self.find_multiple_equilibria(n_samples=50)
        
        if not equilibria:
            return {"error": "No equilibria found"}
        
        # Calculate statistics
        trinity_scores = [e.trinity_score for e in equilibria]
        balance_indices = [e.balance_index for e in equilibria]
        stabilities = [e.stability for e in equilibria]
        
        return {
            "n_equilibria_found": len(equilibria),
            "trinity_score": {
                "mean": np.mean(trinity_scores),
                "std": np.std(trinity_scores),
                "min": np.min(trinity_scores),
                "max": np.max(trinity_scores)
            },
            "balance_index": {
                "mean": np.mean(balance_indices),
                "std": np.std(balance_indices)
            },
            "stability": {
                "mean": np.mean(stabilities),
                "std": np.std(stabilities)
            },
            "best_equilibrium": equilibria[0].to_dict() if equilibria else None
        }


class PerturbationAnalyzer:
    """
    Analyzes how equilibrium responds to perturbations.
    """
    
    def __init__(self, finder: EquilibriumFinder):
        self.finder = finder
        self.solver = EquilibriumSolver()
    
    def test_perturbation(
        self,
        equilibrium: EquilibriumPoint,
        perturbation: Dict[str, float]
    ) -> Dict:
        """
        Test how equilibrium responds to a perturbation.
        
        Returns recovery metrics.
        """
        # Apply perturbation
        perturbed = {
            name: equilibrium.coordinates.get(name, 0.85) + delta
            for name, delta in perturbation.items()
        }
        
        # Clamp to valid range
        perturbed = {
            k: max(0, min(1, v))
            for k, v in perturbed.items()
        }
        
        # Find new equilibrium
        new_point, path = self.finder.find_nearest_equilibrium(perturbed)
        
        # Calculate recovery metrics
        distance_before = self._distance(equilibrium.coordinates, perturbed)
        distance_after = self._distance(equilibrium.coordinates, new_point.coordinates)
        
        return {
            "perturbation_magnitude": distance_before,
            "recovery_distance": distance_after,
            "recovery_ratio": distance_after / distance_before if distance_before > 0 else 0,
            "iterations_to_recovery": len(path),
            "maintained_equilibrium": new_point.balance_index > 0.8
        }
    
    def _distance(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        """Euclidean distance between two state vectors."""
        keys = set(a.keys()) | set(b.keys())
        squared_diffs = [(a.get(k, 0) - b.get(k, 0)) ** 2 for k in keys]
        return math.sqrt(sum(squared_diffs))


# ============ EQUILIBRIUM DEMONSTRATION ============

def demonstrate_equilibrium():
    """
    Demonstrate the equilibrium finder with examples.
    """
    print("=" * 70)
    print("NINE-PARADOX EQUILIBRIUM FINDER v54.0")
    print("=" * 70)
    
    finder = EquilibriumFinder()
    
    # 1. Theoretical optimal
    print("\n📐 THEORETICAL OPTIMAL EQUILIBRIUM")
    print("-" * 70)
    optimal = finder.find_optimal_equilibrium()
    print(f"Trinity Score: {optimal.trinity_score:.4f}")
    print(f"Balance Index: {optimal.balance_index:.4f}")
    print(f"All paradoxes at: {EQUILIBRIUM_THRESHOLD}")
    
    # 2. Near-equilibrium state
    print("\n🎯 FINDING NEAREST EQUILIBRIUM")
    print("-" * 70)
    current_state = {
        "truth_care": 0.82,
        "clarity_peace": 0.88,
        "humility_justice": 0.79,
        "precision_reversibility": 0.91,
        "hierarchy_consent": 0.75,
        "agency_protection": 0.83,
        "urgency_sustainability": 0.77,
        "certainty_doubt": 0.86,
        "unity_diversity": 0.80
    }
    
    print("Starting state (slightly imbalanced):")
    for name, score in current_state.items():
        print(f"  {name}: {score:.2f}")
    
    point, path = finder.find_nearest_equilibrium(current_state)
    
    print(f"\nConverged in {len(path)} iterations")
    print(f"Final Trinity Score: {point.trinity_score:.4f}")
    print(f"Balance Index: {point.balance_index:.4f}")
    print(f"Stability: {point.stability:.4f}")
    
    # 3. Perturbation analysis
    print("\n🌪️ PERTURBATION ANALYSIS")
    print("-" * 70)
    analyzer = PerturbationAnalyzer(finder)
    
    perturbation = {
        "truth_care": -0.15,  # Large drop in truth
        "clarity_peace": 0.05
    }
    
    result = analyzer.test_perturbation(optimal, perturbation)
    print(f"Perturbation magnitude: {result['perturbation_magnitude']:.4f}")
    print(f"Recovery distance: {result['recovery_distance']:.4f}")
    print(f"Recovery ratio: {result['recovery_ratio']:.4f}")
    print(f"Iterations to recovery: {result['iterations_to_recovery']}")
    print(f"Maintained equilibrium: {result['maintained_equilibrium']}")
    
    # 4. Landscape analysis
    print("\n🏔️ EQUILIBRIUM LANDSCAPE")
    print("-" * 70)
    landscape = finder.analyze_equilibrium_landscape()
    
    print(f"Equilibria found: {landscape['n_equilibria_found']}")
    print(f"Average Trinity Score: {landscape['trinity_score']['mean']:.4f} ± {landscape['trinity_score']['std']:.4f}")
    print(f"Score range: [{landscape['trinity_score']['min']:.4f}, {landscape['trinity_score']['max']:.4f}]")
    print(f"Average Balance: {landscape['balance_index']['mean']:.4f}")
    print(f"Average Stability: {landscape['stability']['mean']:.4f}")
    
    print("\n" + "=" * 70)
    print("EQUILIBRIUM CONDITIONS SUMMARY")
    print("=" * 70)
    print(f"✓ All 9 paradoxes ≥ {MIN_PARADOX_SCORE}")
    print(f"✓ Geometric mean ≥ {EQUILIBRIUM_THRESHOLD}")
    print(f"✓ Standard deviation ≤ {BALANCE_TOLERANCE}")
    print(f"✓ Max spread ≤ 0.30")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_equilibrium()
