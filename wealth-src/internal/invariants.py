"""
WEALTH — 7 Civilizational Invariants
Chronological Truth: 2026.04.29

Finalized G-Score Instrumentation (v1.0 Blueprint).
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from internal.kernel_math import RobustRegimeKalmanFilter, calculate_g_score, estimate_lyapunov, HoltSmoothing

class GScoreEngine:
    """
    Sovereign G-Score Engine with MEPP amplification and MS-SSM regime switching.
    """
    def __init__(self):
        self.kf = RobustRegimeKalmanFilter()
        self.holt = HoltSmoothing(alpha=0.3, beta=0.1)
        self.g_history: List[float] = [0.7] * 12 
        self.s_history: List[float] = [0.3] * 12
        self.mahalanobis_flags: List[bool] = []

    def get_regime(self, params: Dict[str, Any]) -> str:
        # Initial heuristic for Phase 1
        if params.get("irreversible") or params.get("critical"):
            return "simulative"
        if params.get("maruah_score", 0.5) < 0.3:
            return "extractive"
        return "inclusive"

    def compute_signals(self, params: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes z(t) and regime-dependent Theta(t).
        Incorporates MEPP (Maximum Entropy Production Principle) near boundaries.
        """
        # --- Observation Vector z(t) ---
        time_sig = np.clip(params.get("horizon_years", 5) / 50.0, 0.0, 1.0)
        uncertainty_sig = np.clip(params.get("volatility", 0.2) * 2.0, 0.0, 1.0)
        
        runway = params.get("runway_months", 12.0)
        if runway == float('inf'): runway = 60.0
        survival_sig = np.clip(runway / 36.0, 0.0, 1.0)
        
        truth_sig = np.clip(params.get("trust_index", 0.5), 0.0, 1.0)
        constraint_sig = np.clip(len(params.get("violations", [])) * 0.2, 0.0, 1.0)
        coordination_sig = np.clip(params.get("maruah_score", 0.5), 0.0, 1.0)
        
        # MEPP Boundary Amplification
        boundary_stress = params.get("resource_utilization", 0.8) # Default 80%
        if boundary_stress > 0.90:
            # MEPP Amplification factor increases S loading
            mepp_factor = 1.0 + (boundary_stress - 0.90) * 10.0
            boundary_sig = np.clip(1.0 * mepp_factor, 0.0, 5.0) # Entropy spike
        else:
            boundary_sig = 1.0 if params.get("critical", False) else 0.0
            
        z = np.array([
            time_sig, uncertainty_sig, survival_sig, 
            truth_sig, constraint_sig, coordination_sig, 
            boundary_sig
        ])

        # --- Regime-Dependent Noise Theta(t) ---
        regime = self.get_regime(params)
        # Base Noise: Truth > Coordination > DCF > Liquidity > Constraints
        # [Time, Uncertainty, Survival, Truth, Constraints, Coordination, Boundaries]
        theta_diag = [0.2, 0.2, 0.1, 0.5, 0.2, 0.4, 0.2]
        
        if regime in ("extractive", "simulative"):
            # Inflate noise for Truth, Constraints, and Boundaries (manipulation risk)
            theta_diag[3] *= 2.0 # Truth noise ++
            theta_diag[4] *= 1.5 # Constraints noise +
            theta_diag[6] *= 1.5 # Boundaries noise +
            
        return z, np.diag(theta_diag)

    def evaluate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        regime = self.get_regime(params)
        z, theta = self.compute_signals(params)
        
        # Kalman Cycle
        self.kf.predict(regime=regime)
        state, is_outlier = self.kf.update_robust(z, theta)
        
        omega, s = state[0][0], state[1][0]
        g_score = calculate_g_score(omega, s)
        
        # Delta S via Holt Smoothing
        delta_s = self.holt.update(s)
        
        self.g_history.append(g_score)
        self.s_history.append(s)
        self.mahalanobis_flags.append(is_outlier)
        
        lyapunov_lambda = estimate_lyapunov(self.g_history)
        
        # Decision Logic (G-Score + Delta S + Lyapunov)
        verdict = "GO"
        if g_score < 0.45 or lyapunov_lambda > 0.1:
            verdict = "STOP"
        elif g_score < 0.60 or delta_s > 0.05:
            verdict = "HOLD"
            
        return {
            "g_score": round(g_score, 4),
            "delta_s": round(delta_s, 4),
            "lyapunov_lambda": round(lyapunov_lambda, 4),
            "omega_capacity": round(omega, 4),
            "entropy_s": round(s, 4),
            "verdict": verdict,
            "regime": regime,
            "is_outlier": is_outlier,
            "boundary_stress": params.get("resource_utilization", 0.8)
        }

# Global singleton
engine = GScoreEngine()

def get_g_score(params: Dict[str, Any]) -> Dict[str, Any]:
    return engine.evaluate(params)
