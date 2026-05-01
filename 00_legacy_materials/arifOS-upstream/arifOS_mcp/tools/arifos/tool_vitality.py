"""
arifOS Tool Vitality Contract — Canonical Performance + Governance Ledger
DITEMPA BUKAN DIBERI — 999 SEAL

Canonical schema: one vitality record per tool run.
Dual ledger: tool_vitality.jsonl (machine) + tool_vitality.tsv (human/diff).

Health model:
  vitality_score = 0.35*primary + 0.20*truth + 0.15*tri_witness
                 + 0.15*stakeholder_safety + 0.10*clamp(peace2,0,1)
                 + 0.05*delta_s_reward

Verdicts: SEAL | SABAR | HOLD_888 | VOID
"""

from __future__ import annotations
import csv
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Verdict
# ──────────────────────────────────────────────────────────────────────────────


class Verdict:
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD_888 = "888_HOLD"
    VOID = "VOID"


# ──────────────────────────────────────────────────────────────────────────────
# Per-tool primary metrics
# ──────────────────────────────────────────────────────────────────────────────

PRIMARY_METRICS: Dict[str, str] = {
    "arifos_000_init": "identity_consistency_rate",
    "arifos_111_sense": "snr_improvement",
    "arifos_222_witness": "witness_consistency",
    "arifos_333_mind": "logical_consistency_rate",
    "arifos_444_kernel": "orthogonality_score",
    "arifos_555_memory": "temporal_coherence",
    "arifos_666_heart": "harm_avoidance_rate",
    "arifos_777_ops": "cost_accuracy",
    "arifos_888_judge": "verdict_calibration",
    "arifos_999_vault": "ledger_integrity",
    "arifos_forge": "safe_execution_rate",
    "arifos_gateway": "cross_organ_leakage_rate",
    "arifos_sabar": "cooling_compliance",
}


# ──────────────────────────────────────────────────────────────────────────────
# Governance / Thermodynamic Metrics
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class GovernanceMetrics:
    truth_score: float  # F2: must be >= 0.99
    delta_s: float  # F4: must be <= 0
    omega_0: float  # F7: must be in [0.03, 0.05]
    peace_squared: float  # F5: must be >= 1.0
    amanah_lock: bool  # F1: must be True
    tri_witness_score: float  # F3: must be >= 0.95 for high-stakes
    stakeholder_safety: float = 1.0  # F6: should be >= 0.9


# ──────────────────────────────────────────────────────────────────────────────
# Performance Metrics
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class PerformanceMetrics:
    latency_ms_p50: float = 0.0
    latency_ms_p95: float = 0.0
    memory_mb: float = 0.0
    calls: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Correctness Metrics
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class CorrectnessMetrics:
    test_cases: int = 0
    passed: int = 0
    failed: int = 0


# ──────────────────────────────────────────────────────────────────────────────
# Primary Metric
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class PrimaryMetric:
    name: str
    value: float


# ──────────────────────────────────────────────────────────────────────────────
# Canonical Vitality Record
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class VitalityRecord:
    tool_name: str
    run_id: str
    version: str
    ts: int
    primary_metric: PrimaryMetric
    governance: GovernanceMetrics
    performance: PerformanceMetrics
    correctness: CorrectnessMetrics
    verdict: str
    description: str = ""
    vitality_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "run_id": self.run_id,
            "version": self.version,
            "ts": self.ts,
            "primary_metric": asdict(self.primary_metric),
            "governance": asdict(self.governance),
            "performance": asdict(self.performance),
            "correctness": asdict(self.correctness),
            "verdict": self.verdict,
            "description": self.description,
            "vitality_score": round(self.vitality_score, 6),
        }

    def to_tsv_row(self) -> Dict[str, Any]:
        g = self.governance
        p = self.performance
        c = self.correctness
        pm = self.primary_metric
        return {
            "ts": self.ts,
            "tool_name": self.tool_name,
            "version": self.version,
            "primary_metric_name": pm.name,
            "primary_metric_value": pm.value,
            "truth_score": g.truth_score,
            "delta_s": g.delta_s,
            "omega_0": g.omega_0,
            "peace_squared": g.peace_squared,
            "tri_witness_score": g.tri_witness_score,
            "stakeholder_safety": g.stakeholder_safety,
            "amanah_lock": g.amanah_lock,
            "latency_ms_p50": p.latency_ms_p50,
            "latency_ms_p95": p.latency_ms_p95,
            "memory_mb": p.memory_mb,
            "calls": p.calls,
            "passed": c.passed,
            "failed": c.failed,
            "verdict": self.verdict,
            "vitality_score": round(self.vitality_score, 4),
            "description": self.description,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Health Model — verdict determination
# ──────────────────────────────────────────────────────────────────────────────


def compute_verdict(
    governance: GovernanceMetrics,
    primary_metric_value: float,
    primary_metric_threshold: float = 0.80,
) -> str:
    """
    Determine verdict from governance + primary metric.
    """
    g = governance

    # Hard VOID gates (F1, F2, F4)
    if not g.amanah_lock:
        return Verdict.VOID
    if g.truth_score < 0.99:
        return Verdict.VOID
    if g.delta_s > 0.0:
        return Verdict.VOID

    # Primary metric must pass
    if primary_metric_value < primary_metric_threshold:
        return Verdict.SABAR

    # Soft SABAR gates (F5, F7)
    if g.peace_squared < 1.0:
        return Verdict.SABAR
    if not (0.03 <= g.omega_0 <= 0.05):
        return Verdict.SABAR

    # HOLD_888 gate (F3)
    if g.tri_witness_score < 0.95:
        return Verdict.HOLD_888

    # F6 stakeholder safety
    if g.stakeholder_safety < 0.9:
        return Verdict.HOLD_888

    return Verdict.SEAL


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def compute_vitality_score(
    primary_metric_value: float,
    governance: GovernanceMetrics,
) -> float:
    """
    Scalar health score [0..1] for dashboard.
    """
    g = governance
    delta_s_reward = 1.0 if g.delta_s <= 0.0 else max(0.0, 1.0 + g.delta_s)

    score = (
        0.35 * clamp(primary_metric_value, 0.0, 1.0)
        + 0.20 * clamp(g.truth_score, 0.0, 1.0)
        + 0.15 * clamp(g.tri_witness_score, 0.0, 1.0)
        + 0.15 * clamp(g.stakeholder_safety, 0.0, 1.0)
        + 0.10 * clamp(g.peace_squared, 0.0, 1.0)
        + 0.05 * delta_s_reward
    )
    return round(score, 6)


# ──────────────────────────────────────────────────────────────────────────────
# Ledger Writer
# ──────────────────────────────────────────────────────────────────────────────

TOOL_VITALITY_JSONL = "tool_vitality.jsonl"
TOOL_VITALITY_TSV = "tool_vitality.tsv"

TSV_COLUMNS = [
    "ts",
    "tool_name",
    "version",
    "primary_metric_name",
    "primary_metric_value",
    "truth_score",
    "delta_s",
    "omega_0",
    "peace_squared",
    "tri_witness_score",
    "stakeholder_safety",
    "amanah_lock",
    "latency_ms_p50",
    "latency_ms_p95",
    "memory_mb",
    "calls",
    "passed",
    "failed",
    "verdict",
    "vitality_score",
    "description",
]


class VitalityLedger:
    """
    Appends canonical vitality records to both JSONL (machine) and TSV (human).
    """

    def __init__(self, ledger_dir: Optional[str] = None):
        self.ledger_dir = Path(ledger_dir) if ledger_dir else Path(".")
        self.jsonl_path = self.ledger_dir / TOOL_VITALITY_JSONL
        self.tsv_path = self.ledger_dir / TOOL_VITALITY_TSV
        self._init_tsv()

    def _init_tsv(self) -> None:
        if not self.tsv_path.exists():
            with open(self.tsv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=TSV_COLUMNS, delimiter="\t")
                writer.writeheader()

    def emit(self, record: VitalityRecord) -> None:
        d = record.to_dict()

        # JSONL — append only
        with open(self.jsonl_path, "a") as f:
            f.write(json.dumps(d) + "\n")

        # TSV — append row
        with open(self.tsv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=TSV_COLUMNS, delimiter="\t")
            writer.writerow(record.to_tsv_row())

    def last_verdict(self, tool_name: str) -> Optional[str]:
        """Return most recent verdict for a tool from JSONL."""
        if not self.jsonl_path.exists():
            return None
        with open(self.jsonl_path) as f:
            lines = f.readlines()
        for line in reversed(lines):
            try:
                r = json.loads(line)
                if r.get("tool_name") == tool_name:
                    return r.get("verdict")
            except json.JSONDecodeError:
                continue
        return None

    def best_vitality(self, tool_name: str) -> Optional[float]:
        """Return highest vitality_score for a tool."""
        if not self.jsonl_path.exists():
            return None
        best = 0.0
        with open(self.jsonl_path) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("tool_name") == tool_name:
                        best = max(best, r.get("vitality_score", 0.0))
                except json.JSONDecodeError:
                    continue
        return best or None


# ──────────────────────────────────────────────────────────────────────────────
# Convenience: build record + emit in one call
# ──────────────────────────────────────────────────────────────────────────────


def emit_vitality(
    tool_name: str,
    primary_metric_value: float,
    governance: GovernanceMetrics,
    performance: Optional[PerformanceMetrics] = None,
    correctness: Optional[CorrectnessMetrics] = None,
    description: str = "",
    version: Optional[str] = None,
    ledger_dir: Optional[str] = None,
) -> VitalityRecord:
    """
    One-call helper to build and emit a vitality record.
    """
    governance = governance
    verdict = compute_verdict(governance, primary_metric_value)
    vitality_score = compute_vitality_score(primary_metric_value, governance)

    perf = performance or PerformanceMetrics()
    corr = correctness or CorrectnessMetrics()
    version = version or _git_sha()
    pm_name = PRIMARY_METRICS.get(tool_name, "unknown")

    record = VitalityRecord(
        tool_name=tool_name,
        run_id=str(uuid.uuid4()),
        version=version,
        ts=int(datetime.now(timezone.utc).timestamp()),
        primary_metric=PrimaryMetric(name=pm_name, value=primary_metric_value),
        governance=governance,
        performance=perf,
        correctness=corr,
        verdict=verdict,
        description=description,
        vitality_score=vitality_score,
    )

    ledger = VitalityLedger(ledger_dir)
    ledger.emit(record)
    return record


def _git_sha() -> str:
    try:
        import subprocess

        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"
