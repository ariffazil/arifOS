from __future__ import annotations

import asyncio
import csv
import json
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arifos.core.governance import ThermodynamicMetrics
from arifos.tools import (
    forge,
    gateway,
    heart_666,
    init_000,
    judge_888,
    kernel_444,
    memory_555,
    mind_333,
    ops_777,
    sabar,
    sense_111,
    vault_999,
    witness_222,
)

PRIMARY_METRIC_NAME = {
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

VITALITY_JSONL = Path(__file__).with_name("tool_vitality.jsonl")
VITALITY_TSV = Path(__file__).with_name("tool_vitality.tsv")
TSV_HEADER = [
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
    "latency_ms_p95",
    "memory_mb",
    "passed",
    "failed",
    "verdict",
    "description",
]


@dataclass
class PrimaryMetric:
    name: str
    value: float


@dataclass
class PerformanceMetrics:
    latency_ms_p50: float = 0.0
    latency_ms_p95: float = 0.0
    memory_mb: float = 0.0
    calls: int = 0


@dataclass
class CorrectnessMetrics:
    test_cases: int = 0
    passed: int = 0
    failed: int = 0


@dataclass
class VitalityRecord:
    tool_name: str
    run_id: str
    version: str
    ts: float
    primary_metric: PrimaryMetric
    governance: dict[str, Any]
    performance: PerformanceMetrics
    correctness: CorrectnessMetrics
    verdict: str
    description: str
    vitality_score: float


def compute_verdict(primary_value: float, g: ThermodynamicMetrics) -> str:
    if primary_value >= 0.9 and g.truth_score >= 0.99 and g.delta_s <= 0.0 and g.amanah_lock:
        return "SEAL"
    if g.truth_score >= 0.95 and g.delta_s <= 0.05 and g.stakeholder_safety >= 0.8:
        return "SABAR"
    if g.tri_witness_score < 0.95 or g.stakeholder_safety < 0.8:
        return "888_HOLD"
    return "VOID"


def vitality_score(primary_value: float, g: ThermodynamicMetrics) -> float:
    delta_s_reward = 1.0 if g.delta_s <= 0.0 else max(0.0, 1.0 - g.delta_s)
    peace_clamped = max(0.0, min(1.0, g.peace_squared))
    return round(
        0.35 * primary_value
        + 0.20 * g.truth_score
        + 0.15 * g.tri_witness_score
        + 0.15 * g.stakeholder_safety
        + 0.10 * peace_clamped
        + 0.05 * delta_s_reward,
        6,
    )


def append_vitality_record(rec: VitalityRecord) -> None:
    with VITALITY_JSONL.open("a", encoding="utf-8") as handle:
        json.dump(asdict(rec), handle)
        handle.write("\n")

    write_header = not VITALITY_TSV.exists()
    with VITALITY_TSV.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        if write_header:
            writer.writerow(TSV_HEADER)
        g = rec.governance
        writer.writerow(
            [
                rec.ts,
                rec.tool_name,
                rec.version,
                rec.primary_metric.name,
                rec.primary_metric.value,
                g["truth_score"],
                g["delta_s"],
                g["omega_0"],
                g["peace_squared"],
                g["tri_witness_score"],
                g["stakeholder_safety"],
                g["amanah_lock"],
                rec.performance.latency_ms_p95,
                rec.performance.memory_mb,
                rec.correctness.passed,
                rec.correctness.failed,
                rec.verdict,
                rec.description,
            ]
        )


TOOL_CALLS = {
    "arifos_000_init": (
        init_000,
        {"operator_id": "arif", "session_id": "vitality-test"},
    ),
    "arifos_111_sense": (
        sense_111,
        {
            "query": "system status",
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_222_witness": (
        witness_222,
        {"query": "tri witness", "operator_id": "arif", "session_id": "vitality-test"},
    ),
    "arifos_333_mind": (
        mind_333,
        {
            "problem_set": {"id": "demo"},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_444_kernel": (
        kernel_444,
        {
            "route_target": "MIND",
            "payload": {"demo": True},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_555_memory": (
        memory_555,
        {
            "action": "query",
            "query": "context",
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_666_heart": (
        heart_666,
        {
            "stakeholder_map": {"operator": "safe"},
            "action_proposal": {"mode": "review"},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_777_ops": (
        ops_777,
        {
            "operation_plan": {"step": "audit"},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_888_judge": (
        judge_888,
        {
            "evidence_bundle": {"evidence": True},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_999_vault": (
        vault_999,
        {
            "action": "append",
            "payload": {"audit": True},
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_forge": (
        forge,
        {
            "receipt": {"verdict": "SEAL"},
            "organ": "SYSTEM",
            "call": {"op": "dry-run"},
            "dry_run": True,
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_gateway": (
        gateway,
        {
            "a": "GEOX",
            "b": "WEALTH",
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
    "arifos_sabar": (
        sabar,
        {
            "hold_id": "H-888-001",
            "action": "status",
            "operator_id": "arif",
            "session_id": "vitality-test",
        },
    ),
}


async def run_tool_vitality(tool_name: str, version: str = "workspace") -> VitalityRecord:
    func, kwargs = TOOL_CALLS[tool_name]
    started = time.time()
    result = await func(**kwargs)
    duration_ms = (time.time() - started) * 1000
    governance = result["metrics"]
    metrics = ThermodynamicMetrics(**governance)
    primary_value = (
        1.0 if result["verdict"] == "SEAL" else 0.5 if result["verdict"] == "SABAR" else 0.0
    )
    record = VitalityRecord(
        tool_name=tool_name,
        run_id=str(uuid.uuid4()),
        version=version,
        ts=time.time(),
        primary_metric=PrimaryMetric(PRIMARY_METRIC_NAME[tool_name], primary_value),
        governance=governance,
        performance=PerformanceMetrics(
            latency_ms_p50=duration_ms, latency_ms_p95=duration_ms, calls=1
        ),
        correctness=CorrectnessMetrics(
            test_cases=1,
            passed=1 if result["verdict"] != "VOID" else 0,
            failed=1 if result["verdict"] == "VOID" else 0,
        ),
        verdict=compute_verdict(primary_value, metrics),
        description=f"Automated vitality audit for {tool_name}",
        vitality_score=vitality_score(primary_value, metrics),
    )
    append_vitality_record(record)
    return record


async def run_all() -> list[VitalityRecord]:
    return [await run_tool_vitality(tool_name) for tool_name in TOOL_CALLS]


if __name__ == "__main__":
    asyncio.run(run_all())
