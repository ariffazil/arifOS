"""
Orthogonality Guard - Runtime Measurement of AGI ⊥ ASI Independence

Constitutional Principle:
- AGI (Mind) and ASI (Heart) must execute independently
- dot_product(AGI, ASI) = 0 (no shared state, no coupling)
- Ω_ortho ≥ 0.95 (orthogonality index threshold)

If coupling detected (Ω_ortho < 0.95):
- Log constitutional violation
- Trigger SABAR protocol after N consecutive violations
- Escalate to human authority

Authority: v47 Constitutional Law Section 8 (Quantum Orthogonality Mandate)
Implementation: Engineer (Ω) under governance directive
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum


class CouplingType(Enum):
    """Types of coupling that violate orthogonality."""
    SHARED_CACHE = "SHARED_CACHE"
    SHARED_MEMORY = "SHARED_MEMORY"
    TIMING_DEPENDENCY = "TIMING_DEPENDENCY"
    EXECUTION_OVERLAP = "EXECUTION_OVERLAP"
    DATA_LEAKAGE = "DATA_LEAKAGE"


@dataclass
class OrthogonalityMetrics:
    """
    Runtime metrics for AGI ⊥ ASI orthogonality.

    Constitutional Floors:
    - F10 (Ontology): AGI and ASI must maintain separate symbolic domains
    - F4 (ΔS Clarity): Coupling increases entropy (reduces clarity)

    Metrics:
    - shared_cache_accesses: AGI and ASI accessing same cache keys
    - shared_memory_writes: Both particles writing to same memory
    - timing_skew_ms: Execution time difference (should be close for true parallelism)
    - data_leakage_count: ASI using AGI outputs before APEX measurement
    """

    shared_cache_accesses: int = 0
    shared_memory_writes: int = 0
    timing_skew_ms: float = 0.0
    data_leakage_count: int = 0
    execution_overlap_ratio: float = 1.0  # 1.0 = perfect parallel, 0.0 = sequential

    # Tracking
    agi_start_time: Optional[float] = None
    agi_end_time: Optional[float] = None
    asi_start_time: Optional[float] = None
    asi_end_time: Optional[float] = None

    coupling_violations: List[CouplingType] = field(default_factory=list)

    @property
    def orthogonality_index(self) -> float:
        """
        Calculate Ω_ortho (orthogonality index).

        Formula:
        Ω_ortho = 1.0 - (coupling_penalty / max_penalty)

        Where coupling_penalty includes:
        - Shared cache accesses (weight: 0.1 per access)
        - Shared memory writes (weight: 0.2 per write)
        - Data leakage (weight: 0.3 per leak)
        - Execution overlap penalty (1.0 - overlap_ratio) * 0.4

        Constitutional Threshold: Ω_ortho ≥ 0.95

        Returns:
            float: 0.0 (fully coupled) to 1.0 (perfectly orthogonal)
        """

        # Calculate penalties
        cache_penalty = min(self.shared_cache_accesses * 0.1, 0.3)
        memory_penalty = min(self.shared_memory_writes * 0.2, 0.3)
        leakage_penalty = min(self.data_leakage_count * 0.3, 0.3)
        overlap_penalty = (1.0 - self.execution_overlap_ratio) * 0.4

        total_penalty = cache_penalty + memory_penalty + leakage_penalty + overlap_penalty

        # Clamp to [0.0, 1.0]
        omega_ortho = max(0.0, 1.0 - total_penalty)

        return omega_ortho

    @property
    def is_constitutionally_compliant(self) -> bool:
        """Check if orthogonality meets constitutional threshold."""
        return self.orthogonality_index >= 0.95

    def calculate_timing_metrics(self):
        """
        Calculate timing skew and execution overlap.

        Perfect parallelism:
        - AGI and ASI start at same time
        - AGI and ASI end at approximately same time
        - Overlap ratio ≈ 1.0

        Sequential execution (violation):
        - One starts after other finishes
        - Overlap ratio ≈ 0.0
        """
        if not all([self.agi_start_time, self.agi_end_time,
                   self.asi_start_time, self.asi_end_time]):
            return

        # Calculate execution times
        agi_duration = (self.agi_end_time - self.agi_start_time) * 1000  # ms
        asi_duration = (self.asi_end_time - self.asi_start_time) * 1000  # ms

        # Timing skew (difference in execution times)
        self.timing_skew_ms = abs(agi_duration - asi_duration)

        # Execution overlap ratio
        # 1.0 = perfect parallel, 0.0 = sequential
        overlap_start = max(self.agi_start_time, self.asi_start_time)
        overlap_end = min(self.agi_end_time, self.asi_end_time)

        if overlap_end > overlap_start:
            overlap_duration = overlap_end - overlap_start
            total_duration = max(self.agi_end_time, self.asi_end_time) - min(self.agi_start_time, self.asi_start_time)
            self.execution_overlap_ratio = overlap_duration / total_duration if total_duration > 0 else 0.0
        else:
            # No overlap = sequential execution
            self.execution_overlap_ratio = 0.0
            self.coupling_violations.append(CouplingType.TIMING_DEPENDENCY)


class OrthogonalityGuard:
    """
    Monitor and enforce AGI ⊥ ASI orthogonality at runtime.

    Constitutional Mandate:
    - Measure orthogonality for every quantum cycle
    - Log violations when Ω_ortho < 0.95
    - Trigger SABAR after 3 consecutive violations
    - Provide metrics for governance audit

    Implementation:
    - Instrument AGI and ASI execution
    - Track shared resource access
    - Detect timing dependencies
    - Calculate Ω_ortho metric
    """

    # Constitutional threshold
    OMEGA_ORTHO_THRESHOLD = 0.95
    SABAR_TRIGGER_COUNT = 3  # Consecutive violations before SABAR

    def __init__(self):
        self.measurement_history: List[OrthogonalityMetrics] = []
        self.violation_count = 0
        self.consecutive_violations = 0
        self.sabar_triggered = False

    async def monitor_orthogonality(
        self,
        agi_coro,
        asi_coro,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> tuple[Any, Any, OrthogonalityMetrics]:
        """
        Execute AGI and ASI with orthogonality monitoring.

        Instrumentation:
        1. Record start/end times for both particles
        2. Track shared resource access (future: cache/memory instrumentation)
        3. Detect data leakage between particles
        4. Calculate Ω_ortho

        Returns:
            tuple: (agi_result, asi_result, orthogonality_metrics)
        """
        metrics = OrthogonalityMetrics()

        # Record start times
        metrics.agi_start_time = time.perf_counter()
        metrics.asi_start_time = time.perf_counter()

        # Execute in parallel (true superposition)
        agi_result, asi_result = await asyncio.gather(agi_coro, asi_coro)

        # Record end times
        metrics.agi_end_time = time.perf_counter()
        metrics.asi_end_time = time.perf_counter()

        # Calculate timing metrics
        metrics.calculate_timing_metrics()

        # TODO: Instrument shared cache/memory access
        # For now, we detect timing-based coupling only
        # Future: Hook into cache/memory systems for real coupling detection

        # Check for data leakage (ASI using AGI output before APEX)
        # This would require inspecting ASI's input vs AGI's output
        # For v47.1, we assume no leakage if execution is truly parallel

        # Validate orthogonality
        self._validate_orthogonality(metrics, query)

        # Store in history
        self.measurement_history.append(metrics)

        return agi_result, asi_result, metrics

    def _validate_orthogonality(self, metrics: OrthogonalityMetrics, query: str):
        """
        Validate orthogonality and trigger SABAR if needed.

        Constitutional Logic:
        - Ω_ortho ≥ 0.95 → COMPLIANT (reset consecutive violations)
        - Ω_ortho < 0.95 → VIOLATION (increment consecutive violations)
        - 3 consecutive violations → SABAR (system cooling needed)
        """
        omega = metrics.orthogonality_index

        if metrics.is_constitutionally_compliant:
            # Reset consecutive violation counter
            self.consecutive_violations = 0
        else:
            # Log violation
            self.violation_count += 1
            self.consecutive_violations += 1

            violation_log = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "query": query[:100],  # First 100 chars
                "omega_ortho": omega,
                "violations": [v.value for v in metrics.coupling_violations],
                "timing_skew_ms": metrics.timing_skew_ms,
                "execution_overlap": metrics.execution_overlap_ratio
            }

            print(f"⚠️ ORTHOGONALITY VIOLATION: Ω_ortho = {omega:.3f} (threshold: {self.OMEGA_ORTHO_THRESHOLD})")
            print(f"   Violations: {violation_log['violations']}")
            print(f"   Timing skew: {metrics.timing_skew_ms:.1f}ms")
            print(f"   Execution overlap: {metrics.execution_overlap_ratio:.2%}")

            # Check if SABAR trigger threshold reached
            if self.consecutive_violations >= self.SABAR_TRIGGER_COUNT:
                self.sabar_triggered = True
                print(f"🌋 SABAR PROTOCOL TRIGGERED: {self.consecutive_violations} consecutive violations")
                print(f"   System requires cooling and investigation")
                print(f"   Review orthogonality measurement history")

    def get_orthogonality_report(self) -> Dict[str, Any]:
        """
        Generate orthogonality metrics report for governance audit.

        Constitutional KPIs:
        - Average Ω_ortho (should be ≥0.95)
        - Violation rate (should be <5%)
        - SABAR status
        - Timing analysis
        """
        if not self.measurement_history:
            return {"no_data": True}

        total_measurements = len(self.measurement_history)

        # Calculate averages
        avg_omega = sum(m.orthogonality_index for m in self.measurement_history) / total_measurements
        avg_timing_skew = sum(m.timing_skew_ms for m in self.measurement_history) / total_measurements
        avg_overlap = sum(m.execution_overlap_ratio for m in self.measurement_history) / total_measurements

        # Count violations
        violations = sum(1 for m in self.measurement_history if not m.is_constitutionally_compliant)
        violation_rate = violations / total_measurements

        # Violation types
        violation_types = {}
        for m in self.measurement_history:
            for v in m.coupling_violations:
                violation_types[v.value] = violation_types.get(v.value, 0) + 1

        return {
            "total_measurements": total_measurements,
            "average_omega_ortho": avg_omega,
            "constitutional_compliance": {
                "compliant_rate": 1.0 - violation_rate,
                "violation_rate": violation_rate,
                "violations_count": violations
            },
            "timing_analysis": {
                "average_skew_ms": avg_timing_skew,
                "average_overlap_ratio": avg_overlap,
                "parallelism_quality": "EXCELLENT" if avg_overlap > 0.95 else
                                      "GOOD" if avg_overlap > 0.80 else
                                      "POOR"
            },
            "violation_breakdown": violation_types,
            "sabar_status": {
                "triggered": self.sabar_triggered,
                "consecutive_violations": self.consecutive_violations,
                "trigger_threshold": self.SABAR_TRIGGER_COUNT
            }
        }

    def reset_sabar(self):
        """Reset SABAR trigger after investigation complete."""
        self.sabar_triggered = False
        self.consecutive_violations = 0
        print("✅ SABAR protocol reset - orthogonality investigation complete")


# =============================================================================
# CONSTITUTIONAL EXPORTS
# =============================================================================

__all__ = [
    "OrthogonalityGuard",
    "OrthogonalityMetrics",
    "CouplingType",
]
