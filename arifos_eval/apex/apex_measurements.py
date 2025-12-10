"""
APEX Measurement Layer v36.1Ω
Reference implementation for arifOS judiciary metrics.

Epoch: v36.1Ω (Truth Polarity Crystallization)
Status: SEALED · Canonical Reference Implementation

PHOENIX SOVEREIGNTY Update (v36.1.1):
    - AmanahDetector integration: Python-sovereign F1 detection
    - Python veto OVERRIDES LLM self-reported amanah
    - "Measure, don't ask"
"""

import json
import re
from typing import Dict, Any, Optional

# PHOENIX SOVEREIGNTY: Import Python-sovereign Amanah detector
try:
    from arifos_core.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR
    AMANAH_DETECTOR_AVAILABLE = True
except ImportError:
    AMANAH_DETECTOR_AVAILABLE = False
    AMANAH_DETECTOR = None

# ==============================================================================
# §10.1 CORE FUNCTIONS (Tier 1 Physics)
# ==============================================================================

def measure_genius(A: float, P: float, E: float, X: float, normalizer: 'Normalizer') -> float:
    """Calculates G based on §3.1."""
    G_raw = A * P * E * X
    return normalizer.normalize_genius(G_raw)

def measure_dark_cleverness(A: float, P: float, X: float, E: float, normalizer: 'Normalizer') -> float:
    """Calculates C_dark based on §4.1."""
    C_raw = A * (1 - P) * (1 - X) * E
    return normalizer.normalize_cdark(C_raw)

def compute_vitality(delta_s: float, peace2: float, kr: float, rasa: float,
                     amanah: float, entropy: float, epsilon: float) -> float:
    """Calculates Ψ based on §5.1."""
    numerator = delta_s * peace2 * kr * rasa * amanah
    denominator = entropy + epsilon
    return numerator / denominator

# ==============================================================================
# HELPER CLASSES (Tier 2 Logic)
# ==============================================================================

class Normalizer:
    def __init__(self, config: Dict[str, Any]):
        self.g_config = config["genius"]
        self.c_config = config["cdark"]

    def normalize_genius(self, raw_val: float) -> float:
        scale = self.g_config["parameters"]["scale"]
        bias = self.g_config["parameters"]["bias"]
        val = (raw_val * scale) + bias
        min_val, max_val = self.g_config["output_range"]
        return max(min_val, min(val, max_val))

    def normalize_cdark(self, raw_val: float) -> float:
        scale = self.c_config["parameters"]["scale"]
        clamp_max = self.c_config["parameters"]["clamp_max"]
        val = raw_val * scale
        min_out, max_out = self.c_config["output_range"]
        return max(min_out, min(val, min(clamp_max, max_out)))

class AntiHantuDetector:
    def __init__(self, config: Dict[str, Any]):
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) for p in config["patterns"]]
        self.exceptions = [re.compile(e, re.IGNORECASE) for e in config["exceptions"]]

    def check(self, text: str) -> bool:
        # 1. Allow-list first
        for exc in self.exceptions:
            if exc.search(text):
                return True
        # 2. Blocklist
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                return False
        return True

# ==============================================================================
# §10.2 APEX MEASUREMENT INTERFACE
# ==============================================================================

class ApexMeasurement:
    def __init__(self, standards_path: str, external_detectors: Optional[Dict] = None):
        """
        Initialize with path to apex_standards_v36.json.
        external_detectors: Optional dict of callable detectors for complex floors.
        """
        self.standards = self._load_standards(standards_path)

        # Helpers
        self.normalizer = Normalizer(self.standards["normalizers"])
        self.anti_hantu = AntiHantuDetector(self.standards["anti_hantu"])
        self.external_detectors = external_detectors or {}

        # Constants from JSON
        self.verdict_gates = self.standards["acceptance_gates"]["verdict"]
        self.shadow_truth_cfg = self.standards["acceptance_gates"].get("shadow_truth", {})
        self.epsilon_psi = self.standards["epsilon"]["psi"]
        self.hard_floors = ["Truth", "Amanah", "Anti_Hantu"]

    def _load_standards(self, path: str) -> Dict[str, Any]:
        with open(path, "r") as f:
            return json.load(f)

    def compute_state(self, dials: Dict[str, float]) -> Dict[str, float]:
        A, P, E, X = dials["A"], dials["P"], dials["E"], dials["X"]
        G = measure_genius(A, P, E, X, self.normalizer)
        C_dark = measure_dark_cleverness(A, P, X, E, self.normalizer)
        return {"G": G, "C_dark": C_dark}

    def compute_flow(self, output_metrics: Dict[str, float]) -> float:
        return compute_vitality(
            delta_s=output_metrics["delta_s"],
            peace2=output_metrics["peace2"],
            kr=output_metrics["k_r"],
            rasa=output_metrics["rasa"],
            amanah=output_metrics["amanah"],
            entropy=output_metrics["entropy"],
            epsilon=self.epsilon_psi,
        )

    def check_floors(self, output_text: str, context_data: Optional[Dict] = None) -> Dict[str, bool]:
        """
        Check all constitutional floors.

        PHOENIX SOVEREIGNTY (v36.1.1):
            - Amanah is now Python-sovereign via AmanahDetector
            - Python veto OVERRIDES any LLM self-reported amanah
            - If Python says NO, verdict is VOID (no negotiation)

        Returns:
            Dict mapping floor names to pass/fail booleans
        """
        results: Dict[str, bool] = {}

        # 1. Anti-Hantu via internal regex (Python-sovereign)
        results["Anti_Hantu"] = self.anti_hantu.check(output_text)

        # 2. PHOENIX SOVEREIGNTY: Amanah via Python-sovereign detector
        #    This OVERRIDES any LLM self-report
        if AMANAH_DETECTOR_AVAILABLE and AMANAH_DETECTOR is not None:
            amanah_result = AMANAH_DETECTOR.check(output_text)
            results["Amanah"] = amanah_result.is_safe
            # Store detailed result for telemetry
            self._last_amanah_result = amanah_result
        elif "Amanah" in self.external_detectors:
            # Fallback to external detector if provided
            results["Amanah"] = self.external_detectors["Amanah"](output_text, context_data)
        else:
            # Default pass (legacy behavior) - NOT RECOMMENDED
            results["Amanah"] = True

        # 3. Other floors (external detectors or default pass)
        floors_to_check = ["Truth", "DeltaS", "Peace2", "Kr", "Omega0", "RASA", "Tri_Witness"]
        for floor in floors_to_check:
            if floor in self.external_detectors:
                results[floor] = self.external_detectors[floor](output_text, context_data)
            else:
                results[floor] = True  # default pass

        return results

    def _verdict_algorithm(self, G: float, Psi: float, floors: Dict[str, bool], C_dark: float) -> str:
        """
        Implements §7 Verdict Logic with Truth Polarity (v36.1Ω).
        """
        G_SEAL = self.verdict_gates["G_seal"]
        G_VOID = self.verdict_gates["G_void"]
        PSI_SEAL = self.verdict_gates["Psi_seal"]
        PSI_SABAR = self.verdict_gates["Psi_sabar"]
        CDARK_SEAL = self.verdict_gates["Cdark_seal"]
        CDARK_WARN = self.verdict_gates["Cdark_warn"]

        use_shadow = self.shadow_truth_cfg.get("use_negative_deltaS_with_truth", True)
        sabar_on_neg = self.shadow_truth_cfg.get("sabar_on_negative_deltaS", True)

        # 1. Hard floors → VOID
        for f in self.hard_floors:
            if f in floors and not floors[f]:
                return "VOID"

        # 1A. Shadow-Truth detection (Truth Polarity)
        # Here we assume external detector set floors["DeltaS"] = False when ΔS < 0.
        if use_shadow and floors.get("Truth", True) and ("DeltaS" in floors and not floors["DeltaS"]):
            # If Amanah fail, we would already be VOID above (hard floor).
            if sabar_on_neg:
                return "SABAR"

        # 2. Dark cleverness: high → SABAR
        if C_dark > CDARK_WARN:
            return "SABAR"

        # 3. Vitality: low → SABAR
        if Psi < PSI_SABAR:
            return "SABAR"

        # 4. Genius: very low → VOID
        if G < G_VOID:
            return "VOID"

        # 5. Borderline → PARTIAL
        if G < G_SEAL or Psi < PSI_SEAL:
            return "PARTIAL"

        # 6. Full SEAL
        if all(floors.values()) and G >= G_SEAL and Psi >= PSI_SEAL and C_dark < CDARK_SEAL:
            return "SEAL"

        return "PARTIAL"

    def judge(self, dials: Dict[str, float], output_text: str, output_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Main pipeline entry point.
        Returns verdict + telemetry for Cooling Ledger.

        PHOENIX SOVEREIGNTY (v36.1.1):
            - Includes amanah_telemetry with Python-sovereign detection results
            - If Amanah fails (Python veto), verdict is VOID regardless of other metrics
        """
        # Reset last amanah result
        self._last_amanah_result = None

        state = self.compute_state(dials)
        G = state["G"]
        C_dark = state["C_dark"]
        Psi = self.compute_flow(output_metrics)
        floors = self.check_floors(output_text, context_data=output_metrics)
        verdict = self._verdict_algorithm(G, Psi, floors, C_dark)

        result = {
            "verdict": verdict,
            "G": G,
            "C_dark": C_dark,
            "Psi": Psi,
            "floors": floors,
        }

        # PHOENIX SOVEREIGNTY: Add Amanah telemetry if available
        if hasattr(self, '_last_amanah_result') and self._last_amanah_result is not None:
            result["amanah_telemetry"] = self._last_amanah_result.to_dict()

        return result
