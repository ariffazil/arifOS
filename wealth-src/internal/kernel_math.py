import numpy as np
from typing import Tuple, List, Optional, Dict

class RobustRegimeKalmanFilter:
    """
    Advanced Markov-Switching State-Space Model (MS-SSM)
    with GMM (Gaussian Mixture Model) Robust Noise Handling.
    """
    def __init__(self):
        # States: [Omega (Capacity), S (Entropy)]
        self.x = np.array([[0.7], [0.3]])
        self.P = np.eye(2) * 0.1
        self.Q = np.eye(2) * 0.01
        
        # Observation Matrix C
        self.C = np.array([
            [1.0, 0.0],   # Time
            [0.0, 1.0],   # Uncertainty
            [1.0, -0.5],  # Survival
            [0.5, -0.5],  # Truth (SNR)
            [-0.2, 1.0],  # Constraints
            [0.5, -0.2],  # Coordination
            [-0.1, 1.0]   # Boundaries
        ])

        # Regime-switching transition matrices A(r)
        self.regimes = {
            "inclusive": np.array([[1.0, 0.0], [0.0, 0.9]]),   # S decays
            "simulative": np.array([[1.0, 0.0], [0.05, 1.0]]), # S creeps
            "extractive": np.array([[0.9, 0.0], [0.1, 1.1]])   # Omega decays, S grows
        }

    def predict(self, regime: str):
        A = self.regimes.get(regime, self.regimes["inclusive"])
        self.x = np.dot(A, self.x)
        self.P = np.dot(np.dot(A, self.P), A.T) + self.Q
        return self.x

    def update_robust(self, z: np.ndarray, base_theta: np.ndarray):
        """
        Update using GMM-based robust noise handling.
        theta ~ pi*N(0, Sigma) + (1-pi)*N(0, 10*Sigma)
        """
        # Innovation
        y = z - np.dot(self.C, self.x)
        S_cov = np.dot(self.C, np.dot(self.P, self.C.T)) + base_theta
        
        # Calculate Mahalanobis distance for outlier detection
        # FIX: use solve (numerically stable) instead of inv, and clamp sqrt arg to prevent NaN
        mahalanobis = 0.0
        with np.errstate(all='ignore'):
            try:
                # solve(S_cov, y) is equivalent to S_cov^-1 @ y but more stable
                S_inv_y = np.linalg.solve(S_cov, y)
                mahalanobis_raw = float(np.dot(y.T, S_inv_y)[0][0])
                mahalanobis = np.sqrt(max(mahalanobis_raw, 0.0))
            except (np.linalg.LinAlgError, ValueError, FloatingPointError):
                mahalanobis = 0.0

        # GMM weight adjustment: if mahalanobis is high, inflate Theta (outlier)
        # Threshold k=3 for innovation gating
        multiplier = 1.0
        if mahalanobis > 3.0:
            multiplier = 5.0 # Outlier down-weighting
            
        effective_theta = base_theta * multiplier
        
        # Standard Kalman update with effective_theta
        S_robust = np.dot(self.C, np.dot(self.P, self.C.T)) + effective_theta
        K = np.dot(np.dot(self.P, self.C.T), np.linalg.inv(S_robust))
        
        self.x = self.x + np.dot(K, y)
        I = np.eye(self.x.shape[0])
        self.P = np.dot((I - np.dot(K, self.C)), self.P)
        
        return self.x, multiplier > 1.0

class HoltSmoothing:
    """Double Exponential Smoothing for Delta S Trend."""
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta
        self.level: Optional[float] = None
        self.trend: Optional[float] = None

    def update(self, value: float) -> float:
        if self.level is None:
            self.level = value
            self.trend = 0.0
            return 0.0
        
        last_level = self.level
        self.level = self.alpha * value + (1 - self.alpha) * (self.level + self.trend)
        self.trend = self.beta * (self.level - last_level) + (1 - self.beta) * self.trend
        return self.trend

def calculate_g_score(omega: float, s: float) -> float:
    denom = omega + s
    return float(np.clip(omega / denom, 0.0, 1.0)) if denom > 0 else 0.0

def estimate_lyapunov(history: List[float], window: int = 12) -> float:
    """Lyapunov Exponent (lambda) detection."""
    if len(history) < window: return 0.0
    recent = np.array(history[-window:])
    # Divergence of logs
    diffs = np.diff(np.log(np.abs(recent) + 1e-9))
    return float(np.mean(diffs))
