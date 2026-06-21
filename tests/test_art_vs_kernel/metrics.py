"""
Metrics for ART vs Kernel comparison.

Records what happened in a scenario run: how many calls were allowed,
where the cut-off occurred, latency, false positives.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ArtVsKernelMetrics:
    """Outcome of one scenario under one configuration."""

    scenario: str
    config: str  # "baseline" or "art"
    total_calls: int
    calls_allowed: int
    calls_blocked: int
    cutoff_n: int | None  # first call index at which blocked (None = never)
    false_positives: int  # legitimate calls wrongly blocked
    latency_p50_ms: float
    latency_p99_ms: float
    gate_path_lengths: list[int] = field(default_factory=list)  # gates executed per call
    verdicts: list[str] = field(default_factory=list)  # SEAL / SABAR / HOLD / REJECT
    notes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_art_better(self, other: "ArtVsKernelMetrics") -> dict[str, bool]:
        """ART better than baseline on what dimensions?"""
        return {
            "fewer_bad_calls": self.calls_allowed < other.calls_allowed,
            "earlier_cutoff": (
                self.cutoff_n is not None
                and (other.cutoff_n is None or self.cutoff_n < other.cutoff_n)
            ),
            "no_false_positive_increase": (
                self.false_positives <= other.false_positives
            ),
            "faster_p50": self.latency_p50_ms <= other.latency_p50_ms,
            "shorter_gate_paths": (
                sum(self.gate_path_lengths) <= sum(other.gate_path_lengths)
            ),
        }


def merge_metrics(metrics_list: list[ArtVsKernelMetrics]) -> dict[str, Any]:
    """Aggregate metrics across runs."""
    if not metrics_list:
        return {}
    return {
        "n_runs": len(metrics_list),
        "total_calls": sum(m.total_calls for m in metrics_list),
        "calls_allowed": sum(m.calls_allowed for m in metrics_list),
        "calls_blocked": sum(m.calls_blocked for m in metrics_list),
        "false_positives": sum(m.false_positives for m in metrics_list),
        "latency_p50_ms_avg": sum(m.latency_p50_ms for m in metrics_list) / len(metrics_list),
        "latency_p99_ms_avg": sum(m.latency_p99_ms for m in metrics_list) / len(metrics_list),
        "cutoff_n_distribution": [m.cutoff_n for m in metrics_list if m.cutoff_n is not None],
    }
