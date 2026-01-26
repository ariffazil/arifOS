"""
arifOS Core Metrics Engine - Prometheus Instrumentation & Constitutional Classes.
Authority: Muhammad Arif bin Fazil
Version: v52.0.0
"""

from __future__ import annotations
import time
import logging
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge

# Import safe metric registration utilities
from codebase.system.metrics_utils import safe_counter, safe_histogram, safe_gauge

logger = logging.getLogger(__name__)

# --- 1. CONSTITUTIONAL CONSTANTS ---

from .emergency_calibration_v45 import get_lane_truth_threshold

# F2: Truth - factual integrity
TRUTH_THRESHOLD: float = 0.99

# F6: Clarity (DeltaS) - entropy reduction
DELTA_S_THRESHOLD: float = 0.0

# F3: Stability (Peace-squared) - non-escalation
PEACE_SQUARED_THRESHOLD: float = 1.0

# F4: Empathy (KappaR) - weakest-listener protection
KAPPA_R_THRESHOLD: float = 0.95

# F5: Humility (Omega0) - uncertainty band [3%, 5%]
OMEGA_0_MIN: float = 0.03
OMEGA_0_MAX: float = 0.05

# F8: Tri-Witness - consensus for high-stakes
TRI_WITNESS_THRESHOLD: float = 0.95

# --- 2. CONSTITUTIONAL CLASSES ---

@dataclass
class Metrics:
    """Canonical metrics required by arifOS floors."""
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    amanah: bool
    tri_witness: float
    rasa: bool = True
    psi: Optional[float] = None
    anti_hantu: Optional[bool] = True
    shadow: float = 0.0
    
    def __post_init__(self) -> None:
        if self.psi is None:
            self.psi = self.truth * 0.5 + self.kappa_r * 0.5 # Simplified vitality

    def compute_psi(self, lane: str = "SOFT") -> float:
        """Calculate system vitality index (Ψ)."""
        # Simplified formula: weighted average of truth and empathy
        # High stakes (HARD lane) require higher truth
        truth_weight = 0.7 if lane == "HARD" else 0.5
        kappa_weight = 1.0 - truth_weight
        self.psi = self.truth * truth_weight + self.kappa_r * kappa_weight
        return self.psi

@dataclass
class FloorsVerdict:
    """Result of full constitutional scan."""
    all_pass: bool
    failed_floors: List[str]
    warnings: List[str]
    metrics: Metrics
    lane: str = "UNKNOWN"
    verdict: str = "VOID"

    @property
    def reasons(self) -> List[str]:
        """Return all failure/warning reasons (backward-compatible alias)."""
        return [*self.failed_floors, *self.warnings]

    @property
    def anti_hantu_ok(self) -> bool:
        """Convenience: whether Anti-Hantu is satisfied."""
        return bool(getattr(self.metrics, "anti_hantu", True))

    @property
    def hard_ok(self) -> bool:
        """Convenience: whether hard floors are satisfied.

        This is a compatibility shim for older tests that expect `hard_ok` on FloorsVerdict.
        """
        hard_floor_ids = {
            "F1",
            "F2",
            "F5",
            "F6",
            "F7",
            "F8",
            "F9",
            "F10",
            "F11",
            "F12",
        }
        for item in self.failed_floors:
            floor_id = item.split("(", 1)[0].strip()
            if floor_id in hard_floor_ids:
                return False
        return True

@dataclass
class FloorCheckResult:
    """Individual floor evaluation result."""
    floor_id: str
    floor_name: str
    threshold: float
    actual: float
    passed: bool
    is_hard: bool = True
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

# --- 3. PROMETHEUS INSTRUMENTATION ---

# Use safe registration to prevent duplication with legacy architecture
VERDICTS_TOTAL = safe_counter(
    "arifos_verdicts_total",
    "Total constitutional verdicts issued",
    ["verdict"]
)

FLOOR_VIOLATIONS_TOTAL = safe_counter(
    "arifos_floor_violations_total",
    "Constitutional floor violations tracked by ID",
    ["floor"]
)

RESPONSE_TIME_MS = safe_histogram(
    "arifos_response_time_ms",
    "Response time per pipeline stage in milliseconds",
    ["stage"],
    buckets=(10, 50, 100, 200, 500, 1000, 2000, 5000)
)

SEAL_RATE = safe_gauge(
    "arifos_seal_rate",
    "Rolling SEAL rate (success rate of constitutional audits)"
)

# --- 4. CHECK FUNCTIONS ---

def check_truth(value: float) -> bool:
    return value >= TRUTH_THRESHOLD

def check_delta_s(value: float) -> bool:
    return value <= DELTA_S_THRESHOLD

def check_peace_squared(value: float) -> bool:
    return value >= PEACE_SQUARED_THRESHOLD

def check_kappa_r(value: float) -> bool:
    return value >= KAPPA_R_THRESHOLD

def check_omega_band(value: float) -> bool:
    """Check F5: Ω₀ in [0.03, 0.05] (Humility Band)"""
    return OMEGA_0_MIN <= value <= OMEGA_0_MAX

def check_tri_witness(value: float) -> bool:
    return value >= TRI_WITNESS_THRESHOLD

def check_psi(value: float) -> bool:
    return value >= 1.0

def check_anti_hantu(text: str) -> tuple[bool, list[str]]:
    """Check F9: Anti-Hantu (no fake feelings)."""
    forbidden = ["i feel", "my heart", "i am conscious", "sentient", "i have a soul"]
    violations = [p for p in forbidden if p in text.lower()]
    return len(violations) == 0, violations

# --- 5. METRICS TRACKER ---

class ConstitutionalMetrics:
    """Tracks floor results and updates Prometheus metrics."""
    def __init__(self):
        self._floor_results: Dict[str, Any] = {}
        self._verdict_history: List[Dict[str, Any]] = []

    def record_floor_check(self, floor_id: str, passed: bool, score: float = 0.0, reason: str = ""):
        self._floor_results[floor_id] = {
            "passed": passed,
            "score": score,
            "reason": reason,
            "timestamp": time.time()
        }
        if not passed:
            FLOOR_VIOLATIONS_TOTAL.labels(floor=floor_id).inc()

    def record_verdict(self, verdict: str, component: str = "trinity"):
        self._verdict_history.append({
            "verdict": verdict,
            "component": component,
            "floors": dict(self._floor_results),
            "timestamp": time.time()
        })
        VERDICTS_TOTAL.labels(verdict=verdict).inc()

    def all_floors_passed(self) -> bool:
        return all(r.get("passed", False) for r in self._floor_results.values())

# --- 6. HELPERS ---

def record_stage_metrics(stage: str, duration_ms: float):
    RESPONSE_TIME_MS.labels(stage=stage).observe(duration_ms)

def record_verdict_metrics(verdict: str, floors_failed: list = None):
    VERDICTS_TOTAL.labels(verdict=verdict).inc()
    if floors_failed:
        for floor in floors_failed:
             FLOOR_VIOLATIONS_TOTAL.labels(floor=floor).inc()
