"""
codebase/constants.py — Constitutional Floor Thresholds

This module provides the canonical threshold values for constitutional floors.
Source: 000_THEORY/000_LAW.md and constitutional_floors.py

DITEMPA BUKAN DIBERI
"""

# Floor Thresholds (Canonical)
TRUTH_THRESHOLD = 0.99          # F2: Minimum truth confidence
DELTA_S_THRESHOLD = 0.0         # F4: Clarity / entropy change (ΔS ≥ 0)
PEACE_SQUARED_THRESHOLD = 1.0   # F5: Minimum Peace² score
KAPPA_R_THRESHOLD = 0.70        # F4: Minimum empathy/care score (was 0.95 in old system)
OMEGA_0_MIN = 0.03              # F7: Minimum uncertainty (3%)
OMEGA_0_MAX = 0.05              # F7: Maximum uncertainty (5%)
TRI_WITNESS_THRESHOLD = 0.95    # F3: Minimum consensus score
GENIUS_THRESHOLD = 0.80         # F8: Minimum governed intelligence score
DARK_CLEVERNESS_CEILING = 0.30  # F9: Maximum dark cleverness
INJECTION_THRESHOLD = 0.85      # F12: Maximum injection risk

# Floor Types
FLOOR_TYPES = {
    "F1": "HARD",
    "F2": "HARD",
    "F3": "DERIVED",
    "F4": "SOFT",
    "F5": "SOFT",
    "F6": "HARD",
    "F7": "HARD",
    "F8": "DERIVED",
    "F9": "SOFT",
    "F10": "HARD",
    "F11": "HARD",
    "F12": "HARD",
    "F13": "HARD",
}


def get_lane_truth_threshold(lane: str = "SOFT") -> float:
    """
    Get truth threshold for a specific lane.
    
    Args:
        lane: Governance lane ("HARD" or "SOFT")
        
    Returns:
        Truth threshold for the lane
    """
    # HARD lane requires higher truth
    if lane.upper() == "HARD":
        return TRUTH_THRESHOLD  # 0.99
    else:
        return 0.90  # SOFT lane allows 90% truth


# Dataclass for floors verdict (simplified version)
class FloorsVerdict:
    """Result of floor checking."""
    
    def __init__(self, verdict: str, passed_floors: list, failed_floors: list, reason: str = ""):
        self.verdict = verdict
        self.passed_floors = passed_floors
        self.failed_floors = failed_floors
        self.reason = reason
        self.all_passed = len(failed_floors) == 0
