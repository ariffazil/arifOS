"""
codebase/constants.py — Constitutional Floor Thresholds

This module provides the canonical threshold values for constitutional floors.
Source: 000_THEORY/000_LAW.md and constitutional_floors.py

DITEMPA BUKAN DIBERI
"""

# Floor Thresholds (Canonical)
TRUTH_THRESHOLD = 0.99          # F2: Minimum truth confidence
DELTA_S_THRESHOLD = 0.0         # F6: Clarity / entropy change (ΔS ≤ 0)
PEACE_SQUARED_THRESHOLD = 1.0   # F3: Minimum Peace² score (Target)
KAPPA_R_THRESHOLD = 0.70        # F4: Minimum empathy/care score
OMEGA_0_MIN = 0.03              # F5: Minimum uncertainty (Humility)
OMEGA_0_MAX = 0.05              # F5: Maximum uncertainty (Humility)
TRI_WITNESS_THRESHOLD = 0.95    # F8: Minimum consensus score
GENIUS_THRESHOLD = 0.80         # F8: Minimum governed intelligence score
DARK_CLEVERNESS_CEILING = 0.30  # F9: Maximum dark cleverness
INJECTION_THRESHOLD = 0.85      # F12: Maximum injection risk score (pass if <= 0.85)
AUTH_STRICTNESS = 1.0           # F11: Command Authority (Binary)
ONTOLOGY_SCORE = 1.0            # F10: Ontology integrity (Binary)
CURIOSITY_MIN_PATHS = 3         # F13: Minimum explored paths

# Floor Types
# HARD: Must pass or VOID/SABAR
# SOFT: Warning/PARTIAL if failed
# DERIVED: Calculated from other metrics
FLOOR_TYPES = {
    "F1": "HARD",    # Amanah (Trust)
    "F2": "HARD",    # Truth
    "F3": "SOFT",    # Peace Check (Derived from Peace²)
    "F4": "SOFT",    # Empathy (Kappa_r)
    "F5": "HARD",    # Humility (Omega_0) - Hard per v53
    "F6": "HARD",    # Clarity (Delta_S)
    "F7": "HARD",    # RASA (Data integrity)
    "F8": "DERIVED", # Tri-Witness / Genius
    "F9": "HARD",    # Anti-Hantu (Dark Cleverness)
    "F10": "HARD",   # Ontology (Hypervisor) -> SABAR
    "F11": "HARD",   # Command Auth (Hypervisor) -> SABAR
    "F12": "HARD",   # Injection (Hypervisor) -> SABAR
    "F13": "SOFT",   # Curiosity
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
