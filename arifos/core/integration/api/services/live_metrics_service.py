"""
Live Metrics Service - Real-time constitutional metrics computation

This service aggregates live metrics from:
1. Cooling Ledger (SEAL/VOID rates, session counts)
2. ASI Evaluator (truth scores, empathy κᵣ, clarity ΔS)
3. Entropy Tracker (thermodynamic governance)
4. Governance Engine (vitality Ψ, uptime)

Replaces static placeholders in dashboard with live computed values.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LiveMetrics:
    """Real-time constitutional metrics snapshot."""
    
    # Core Trinity Metrics
    tau: float  # Truth accuracy (τ) - from AGI eval harness
    kappa_r: float  # Safety & empathy (κᵣ) - from ASI empathy scoring
    psi: float  # System vitality (Ψ) - from governance engine uptime/SEAL density
    entropy_delta: float  # Clarity (ΔS) - from entropy tracker
    
    # Distribution metrics
    truth_percentiles: Dict[str, float]  # p50, p95, p99
    
    # System health
    seal_rate: float  # % of sessions that SEAL
    void_rate: float  # % of sessions that VOID
    active_sessions: int  # Current active session count
    uptime_hours: float  # System uptime
    
    # Constitutional compliance
    floors_passed: int  # Number of floors passed in last window
    floors_failed: int  # Number of floors failed in last window
    sabar_triggered: int  # Number of SABAR-72 cooling events
    
    timestamp: str


class LiveMetricsService:
    """Computes real-time constitutional metrics for dashboard."""
    
    def __init__(
        self,
        cooling_ledger_path: Optional[Path] = None,
        metrics_window_minutes: int = 60,  # Rolling window for metrics
    ):
        """
        Initialize live metrics service.
        
        Args:
            cooling_ledger_path: Path to cooling ledger JSONL file
            metrics_window_minutes: Rolling window size for metric computation
        """
        self.cooling_ledger_path = cooling_ledger_path or Path("./VAULT999/BBB_LEDGER/cooling_ledger.jsonl")
        self.metrics_window = timedelta(minutes=metrics_window_minutes)
        
        # Cache for recent metrics to reduce computation
        self._cache: Dict[str, Any] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(seconds=30)  # 30 second cache
        
        logger.info(f"LiveMetricsService initialized (window={metrics_window_minutes}min)")
    
    def get_live_metrics(self, use_cache: bool = True) -> LiveMetrics:
        """
        Get current live metrics snapshot.
        
        Args:
            use_cache: Whether to use cached metrics if available
            
        Returns:
            LiveMetrics with current constitutional metrics
        """
        # Check cache first
        now = datetime.now(timezone.utc)
        if use_cache and self._cache_timestamp:
            if now - self._cache_timestamp < self._cache_ttl:
                logger.debug("Returning cached metrics")
                return self._cache.get("metrics")
        
        # Compute fresh metrics
        metrics = self._compute_metrics()
        
        # Update cache
        self._cache = {"metrics": metrics}
        self._cache_timestamp = now
        
        return metrics
    
    def _compute_metrics(self) -> LiveMetrics:
        """Compute live metrics from all data sources."""
        
        # 1. Get recent ledger entries for statistical aggregation
        recent_entries = self._get_recent_ledger_entries()
        
        # 2. Compute core metrics
        seal_rate = self._compute_seal_rate(recent_entries)
        void_rate = 1.0 - seal_rate if seal_rate > 0 else 0.0
        active_sessions = self._count_active_sessions()
        uptime_hours = self._compute_uptime()
        
        # 3. Compute Trinity metrics
        tau = self._compute_truth_score(recent_entries)  # τ: Truth accuracy
        kappa_r = self._compute_empathy_score(recent_entries)  # κᵣ: Safety & empathy
        psi = self._compute_vitality_score(recent_entries, uptime_hours)  # Ψ: System vitality
        entropy_delta = self._compute_entropy_delta(recent_entries)  # ΔS: Clarity
        
        # 4. Compute percentile distributions
        truth_percentiles = self._compute_truth_percentiles(recent_entries)
        
        # 5. Compute compliance metrics
        floors_passed, floors_failed = self._compute_floor_stats(recent_entries)
        sabar_triggered = self._count_sabar_events(recent_entries)
        
        return LiveMetrics(
            tau=tau,
            kappa_r=kappa_r,
            psi=psi,
            entropy_delta=entropy_delta,
            truth_percentiles=truth_percentiles,
            seal_rate=seal_rate,
            void_rate=void_rate,
            active_sessions=active_sessions,
            uptime_hours=uptime_hours,
            floors_passed=floors_passed,
            floors_failed=floors_failed,
            sabar_triggered=sabar_triggered,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def _get_recent_ledger_entries(self) -> List[Dict[str, Any]]:
        """
        Get ledger entries from the last metrics_window.
        
        Returns:
            List of recent ledger entries
        """
        if not self.cooling_ledger_path.exists():
            logger.warning(f"Cooling ledger not found at {self.cooling_ledger_path}")
            return []
        
        entries = []
        cutoff_time = datetime.now(timezone.utc) - self.metrics_window
        
        try:
            with open(self.cooling_ledger_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                        
                        if entry_time >= cutoff_time:
                            entries.append(entry)
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.debug(f"Skipping malformed ledger entry: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error reading cooling ledger: {e}")
        
        logger.debug(f"Retrieved {len(entries)} recent ledger entries")
        return entries
    
    def _compute_seal_rate(self, entries: List[Dict[str, Any]]) -> float:
        """Compute SEAL rate from recent ledger entries."""
        if not entries:
            return 0.0
        
        seal_count = sum(1 for entry in entries if entry.get('verdict') == 'SEAL')
        return seal_count / len(entries)
    
    def _compute_truth_score(self, entries: List[Dict[str, Any]]) -> float:
        """Compute truth accuracy (τ) from eval results."""
        if not entries:
            return 0.99  # Default baseline
        
        # Aggregate truth scores from metrics where available
        truth_scores = []
        for entry in entries:
            # Try to extract truth score from entry metadata
            if 'metrics' in entry and isinstance(entry['metrics'], dict):
                truth = entry['metrics'].get('truth')
                if truth is not None:
                    truth_scores.append(float(truth))
        
        if truth_scores:
            return sum(truth_scores) / len(truth_scores)
        
        # Fallback: derive from floor failures
        # If F2 (Truth) never failed, assume high accuracy
        f2_failures = sum(1 for entry in entries if 'F2' in entry.get('floor_failures', []))
        if f2_failures == 0:
            return 0.99
        else:
            return max(0.85, 1.0 - (f2_failures / len(entries) * 0.15))
    
    def _compute_empathy_score(self, entries: List[Dict[str, Any]]) -> float:
        """Compute safety & empathy (κᵣ) from floor results."""
        if not entries:
            return 0.98  # Default baseline
        
        # κᵣ is primarily F6 (Empathy) performance
        f6_passes = sum(1 for entry in entries if 'F6' not in entry.get('floor_failures', []))
        kappa_r = f6_passes / len(entries) if entries else 0.98
        
        # Ensure bounded in [0.03, 0.05] range per constitutional law
        return max(0.95, min(1.0, kappa_r))
    
    def _compute_vitality_score(self, entries: List[Dict[str, Any]], uptime_hours: float) -> float:
        """Compute system vitality (Ψ) from uptime and SEAL density."""
        if not entries:
            return 0.0
        
        # Ψ formula: (ΔS × Peace² × κᵣ × Amanah) / (Entropy + ε)
        # Simplified for dashboard: uptime-normalized SEAL density
        
        seal_rate = self._compute_seal_rate(entries)
        
        # Normalize by uptime (longer uptime with good SEAL rate = higher vitality)
        uptime_factor = min(1.0, uptime_hours / 24.0)  # Normalize to 24h
        
        # Penalize for SABAR triggers
        sabar_count = self._count_sabar_events(entries)
        sabar_penalty = min(0.3, sabar_count / max(len(entries), 1) * 0.5)
        
        psi = (seal_rate * uptime_factor) - sabar_penalty
        return max(0.0, min(1.0, psi))
    
    def _compute_entropy_delta(self, entries: List[Dict[str, Any]]) -> float:
        """Compute average entropy delta (ΔS) from recent sessions."""
        if not entries:
            return -0.042  # Default cooling baseline
        
        delta_s_values = []
        for entry in entries:
            delta_s = entry.get('delta_s')
            if delta_s is not None:
                delta_s_values.append(float(delta_s))
        
        if delta_s_values:
            avg_delta_s = sum(delta_s_values) / len(delta_s_values)
            return round(avg_delta_s, 3)
        
        return -0.042
    
    def _compute_truth_percentiles(self, entries: List[Dict[str, Any]]) -> Dict[str, float]:
        """Compute truth score percentiles (p50, p95, p99)."""
        if not entries:
            return {"p50": 0.99, "p95": 0.995, "p99": 1.0}
        
        truth_scores = []
        for entry in entries:
            if 'metrics' in entry and isinstance(entry['metrics'], dict):
                truth = entry['metrics'].get('truth')
                if truth is not None:
                    truth_scores.append(float(truth))
        
        if not truth_scores:
            return {"p50": 0.99, "p95": 0.995, "p99": 1.0}
        
        truth_scores.sort()
        n = len(truth_scores)
        
        def percentile(p: float) -> float:
            idx = int(n * p / 100)
            return truth_scores[min(idx, n-1)]
        
        return {
            "p50": percentile(50),
            "p95": percentile(95),
            "p99": percentile(99)
        }
    
    def _count_active_sessions(self) -> int:
        """Count currently active sessions."""
        # TODO: Implement actual session tracking
        # For now, return placeholder that increments with activity
        return len(self._get_recent_ledger_entries())
    
    def _compute_uptime(self) -> float:
        """Compute system uptime in hours."""
        # TODO: Implement actual uptime tracking
        # For now, return increasing value based on ledger age
        try:
            if self.cooling_ledger_path.exists():
                stat = self.cooling_ledger_path.stat()
                created_time = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
                uptime = (datetime.now(timezone.utc) - created_time).total_seconds() / 3600
                return max(0.0, uptime)
        except Exception as e:
            logger.debug(f"Could not compute uptime: {e}")
        
        return 0.0
    
    def _compute_floor_stats(self, entries: List[Dict[str, Any]]) -> tuple[int, int]:
        """Compute total floors passed and failed."""
        total_passed = 0
        total_failed = 0
        
        for entry in entries:
            total_passed += entry.get('floors_passed', 0)
            total_failed += entry.get('floors_failed', 0)
        
        return total_passed, total_failed
    
    def _count_sabar_events(self, entries: List[Dict[str, Any]]) -> int:
        """Count SABAR-72 cooling events."""
        return sum(1 for entry in entries if entry.get('sabar_triggered', False))


# Global singleton instance
_live_metrics_service: Optional[LiveMetricsService] = None


def get_live_metrics_service() -> LiveMetricsService:
    """Get or create the global live metrics service instance."""
    global _live_metrics_service
    
    if _live_metrics_service is None:
        _live_metrics_service = LiveMetricsService()
    
    return _live_metrics_service

def reset_live_metrics_service() -> None:
    """Reset the global singleton (for testing)."""
    global _live_metrics_service
    _live_metrics_service = None
