"""
Thermodynamic Dashboard - Real-time Constitutional Metrics
ARIF Loop v52.6.0 - AGI Room (Mind/Δ)

Tracks ΔS (entropy), Ω₀ (humility), Peace², cost in real-time
Purpose: Make AGI reasoning observable and improvable

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import time
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

from codebase.system.types import Metrics
from codebase.constants import TRUTH_THRESHOLD, OMEGA_0_MIN, OMEGA_0_MAX


@dataclass
class MetricSnapshot:
    """Single point-in-time measurement of constitutional metrics"""
    timestamp: float
    stage: str  # "111", "222", "333"
    delta_s: float  # F4: Entropy change (bits)
    omega_0: float  # F6: Humility (1 - confidence)
    truth_confidence: float  # F2: Truth confidence
    peace_squared: float  # F3: Peace² ratio
    cost_usd: float  # Economic cost
    session_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "stage": self.stage,
            "delta_s": round(self.delta_s, 4),
            "omega_0": round(self.omega_0, 4),
            "truth_confidence": round(self.truth_confidence, 4),
            "peace_squared": round(self.peace_squared, 4),
            "cost_usd": round(self.cost_usd, 6),
            "constitutional_status": self.check_constitutional()
        }
    
    def check_constitutional(self) -> Dict[str, str]:
        """Check which floors are satisfied"""
        status = {}
        
        # F2: Truth (≥ 0.99)
        status["F2_Truth"] = "PASS" if self.truth_confidence >= 0.99 else "FAIL"
        
        # F4: Clarity (ΔS ≤ 0)
        status["F4_Clarity"] = "PASS" if self.delta_s <= 0 else "FAIL"
        
        # F6: Humility (Ω₀ ∈ [0.03, 0.05])
        status["F6_Humility"] = "PASS" if OMEGA_0_MIN <= self.omega_0 <= OMEGA_0_MAX else "FAIL"
        
        # F3: Peace² (≥ 1.0)
        status["F3_Peace"] = "PASS" if self.peace_squared >= 1.0 else "FAIL"
        
        return status


class ThermodynamicDashboard:
    """Real-time tracker for all constitutional metrics"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.metrics_stream: List[MetricSnapshot] = []
        self.start_time = time.time()
        self.total_cost = 0.0
        
    def record_stage_metric(
        self,
        stage: str,
        delta_s: float,
        confidence: float,
        peace_squared: float,
        cost_usd: float = 0.0
    ) -> MetricSnapshot:
        """Record metrics for a stage and check constitutional compliance"""
        
        omega_0 = 1.0 - confidence  # F6: Humility = 1 - confidence
        
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            stage=stage,
            delta_s=delta_s,
            omega_0=omega_0,
            truth_confidence=confidence,
            peace_squared=peace_squared,
            cost_usd=cost_usd,
            session_id=self.session_id
        )
        
        self.metrics_stream.append(snapshot)
        self.total_cost += cost_usd
        
        # F4: Alert if entropy not decreasing
        if len(self.metrics_stream) > 1:
            if delta_s >= self.metrics_stream[-2].delta_s - 0.01:  # Allow tiny increase
                self._trigger_sabar_alert(
                    f"ΔS stall at stage {stage}: {delta_s:.3f} (insufficient cooling)"
                )
        
        # F6: Alert if overconfident (Ω₀ too low)
        if omega_0 < 0.02:  # Overconfident territory
            self._trigger_humility_violation(omega_0)
        
        # F2: Alert if truth confidence too low
        if confidence < 0.95:  # Below safe threshold
            self._trigger_truth_warning(confidence)
        
        return snapshot
    
    def _trigger_sabar_alert(self, reason: str):
        """Trigger SABAR when entropy reduction stalls"""
        logger.warning(f"[Constitutional Alert] {reason} - Session: {self.session_id}")
        # Store in VAULT for audit
        record_session_alert(self.session_id, "SABAR", reason)
    
    def _trigger_humility_violation(self, omega_0: float):
        """Alert when humility fails (F6)"""
        logger.warning(f"[F6 Violation] Ω₀ = {omega_0:.4f} (outside [0.03, 0.05]) - Session: {self.session_id}")
        record_session_alert(self.session_id, "F6_HUMILITY", f"Ω₀ = {omega_0:.4f}")
    
    def _trigger_truth_warning(self, confidence: float):
        """Alert when truth confidence is low (F2)"""
        logger.warning(f"[F2 Warning] Confidence = {confidence:.4f} (< 0.95) - Session: {self.session_id}")
        record_session_alert(self.session_id, "F2_TRUTH", f"Confidence = {confidence:.4f}")
    
    def get_convergence_stats(self) -> Dict[str, Any]:
        """Calculate convergence statistics"""
        if not self.metrics_stream:
            return {"status": "no_data"}
        
        delta_s_values = [m.delta_s for m in self.metrics_stream]
        confidence_values = [m.truth_confidence for m in self.metrics_stream]
        omega_values = [m.omega_0 for m in self.metrics_stream]
        
        return {
            "total_stages": len(self.metrics_stream),
            "total_time": time.time() - self.start_time,
            "total_cost_usd": round(self.total_cost, 6),
            "total_delta_s": round(sum(delta_s_values), 4),
            "average_delta_s": round(statistics.mean(delta_s_values), 4),
            "average_confidence": round(statistics.mean(confidence_values), 4),
            "average_omega": round(statistics.mean(omega_values), 4),
            "convergence_rate": self._calculate_convergence_rate(),
            "constitutional_score": self._calculate_constitutional_score()
        }
    
    def _calculate_convergence_rate(self) -> float:
        """How fast is entropy decreasing?"""
        if len(self.metrics_stream) < 2:
            return 0.0
        
        # Linear regression on delta_s over time
        times = [m.timestamp for m in self.metrics_stream]
        deltas = [m.delta_s for m in self.metrics_stream]
        
        # Slope = convergence rate (more negative = faster cooling)
        n = len(times)
        sum_x = sum(times)
        sum_y = sum(deltas)
        sum_xy = sum(t * d for t, d in zip(times, deltas))
        sum_x2 = sum(t * t for t in times)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return round(slope, 6)
    
    def _calculate_constitutional_score(self) -> float:
        """Overall constitutional compliance (0.0 to 1.0)"""
        if not self.metrics_stream:
            return 0.0
        
        scores = []
        for metric in self.metrics_stream:
            checks = metric.check_constitutional()
            passed = sum(1 for status in checks.values() if status == "PASS")
            scores.append(passed / len(checks))
        
        return round(statistics.mean(scores), 4)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard report"""
        return {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "convergence_stats": self.get_convergence_stats(),
            "stage_metrics": [m.to_dict() for m in self.metrics_stream],
            "constitutional_summary": {
                "overall_score": self._calculate_constitutional_score(),
                "floors_passed": self._count_passed_floors(),
                "floors_failed": self._count_failed_floors()
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _count_passed_floors(self) -> Dict[str, int]:
        """Count how many times each floor passed"""
        counts = {"F2": 0, "F3": 0, "F4": 0, "F6": 0}
        for metric in self.metrics_stream:
            checks = metric.check_constitutional()
            for floor, status in checks.items():
                if status == "PASS":
                    counts[floor] += 1
        return counts
    
    def _count_failed_floors(self) -> Dict[str, int]:
        """Count how many times each floor failed"""
        counts = {"F2": 0, "F3": 0, "F4": 0, "F6": 0}
        for metric in self.metrics_stream:
            checks = metric.check_constitutional()
            for floor, status in checks.items():
                if status == "FAIL":
                    counts[floor] += 1
        return counts
    
    def _generate_recommendations(self) -> List[str]:
        """AI-generated recommendations for improvement"""
        recommendations = []
        stats = self.get_convergence_stats()
        
        if stats["average_delta_s"] > -0.1:
            recommendations.append("Consider adding more evidence or deeper reasoning to increase entropy reduction")
        
        if stats["average_confidence"] < 0.95:
            recommendations.append("Truth confidence is low - verify sources and reasoning steps")
        
        if stats["average_omega"] < 0.03:
            recommendations.append("Overconfident - express more uncertainty in conclusions")
        
        if stats["convergence_rate"] > -0.05:
            recommendations.append("Slow convergence - try parallel hypothesis generation")
        
        return recommendations


# Global registry for active dashboards
_active_dashboards: Dict[str, ThermodynamicDashboard] = {}


def get_dashboard(session_id: str) -> ThermodynamicDashboard:
    """Get or create dashboard for session"""
    if session_id not in _active_dashboards:
        _active_dashboards[session_id] = ThermodynamicDashboard(session_id)
    return _active_dashboards[session_id]


def cleanup_dashboard(session_id: str):
    """Remove dashboard from registry"""
    if session_id in _active_dashboards:
        del _active_dashboards[session_id]


async def record_session_alert(session_id: str, alert_type: str, reason: str):
    """Record constitutional alert in VAULT"""
    # This would integrate with VAULT-999
    # For now, log it
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[VAULT] Alert: {alert_type} - {reason} - Session: {session_id}")
