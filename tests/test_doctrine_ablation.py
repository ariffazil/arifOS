"""Doctrine Ablation harness tests — canon retirement needs removal evidence.

Configs A (full corpus) / B (compressed AGENTS.md) / C (constitution+contracts) /
D (runtime only). The degenerate-objective guard is tested here: human-attention
metrics must never gate, and scores without receipts are theatre.
"""

from __future__ import annotations

from arifosmcp.runtime.doctrine_ablation import (
    ABLATION_THEATER,
    ADVISORY_ONLY_METRICS,
    ATTENTION_AS_GATE,
    CONFIGS,
    GATE_METRICS,
    MissionResult,
    VERDICT_ARCHITECTURE,
    VERDICT_INSUFFICIENT,
    VERDICT_RUNTIME_WORK,
    ablation_verdict,
    fitness_report,
)

BASE = {
    "truthfulness": 0.9,
    "authority_compliance": 1.0,
    "verification_rate": 0.8,
    "successful_completion": 0.85,
    "rollback_rate": 0.05,
    "unsupported_claims": 0.02,
    "real_world_outcome": 0.8,
    "attention_cost": 0.4,
    "human_interrupts": 0.2,
}


def _m(mid: str, config: str, receipts=("rcpt-1",), **overrides) -> MissionResult:
    metrics = dict(BASE)
    metrics.update(overrides)
    return MissionResult(mission_id=mid, config=config, metrics=metrics, receipts=tuple(receipts))


def test_configs_are_exactly_a_b_c_d() -> None:
    assert CONFIGS == ("A", "B", "C", "D")
    assert len(GATE_METRICS) == 7
    assert set(ADVISORY_ONLY_METRICS) == {"attention_cost", "human_interrupts"}
    assert len(GATE_METRICS) + len(ADVISORY_ONLY_METRICS) == 9


def test_scores_without_receipts_are_theatre() -> None:
    r = ablation_verdict([_m("m1", "A", receipts=()), _m("m1", "C")])
    assert r["verdict"] == "REJECTED"
    assert r["reason"] == ABLATION_THEATER


def test_attention_metrics_never_gate() -> None:
    good = [_m("m1", "A"), _m("m1", "C", attention_cost=999.0, human_interrupts=999.0)]
    bad = [_m("m1", "A"), _m("m1", "C")]
    v1 = ablation_verdict(good)
    v2 = ablation_verdict(bad)
    assert v1["verdict"] == v2["verdict"] == VERDICT_ARCHITECTURE
    rep = fitness_report(good)
    assert rep["advisory_only"] == list(ADVISORY_ONLY_METRICS)
    assert "REPORT_AND_TREND_ONLY" in rep["usage"]


def test_c_within_tolerance_of_a_is_architecture() -> None:
    r = ablation_verdict(
        [_m("m1", "A"), _m("m1", "C", truthfulness=0.88), _m("m1", "D", truthfulness=0.87)]
    )
    assert r["verdict"] == VERDICT_ARCHITECTURE
    assert r["pairs"] == 2


def test_c_collapse_means_doctrine_still_runtime_work() -> None:
    r = ablation_verdict([_m("m1", "A"), _m("m1", "C", truthfulness=0.5, authority_compliance=0.4)])
    assert r["verdict"] == VERDICT_RUNTIME_WORK
    assert any("truthfulness" in c for c in r["collapses"])
    assert any("authority_compliance" in c for c in r["collapses"])


def test_failure_counts_gap_direction() -> None:
    # unsupported_claims is lower-is-better: C having MORE claims is a collapse.
    r = ablation_verdict(
        [_m("m1", "A", unsupported_claims=0.02), _m("m1", "C", unsupported_claims=0.30)]
    )
    assert r["verdict"] == VERDICT_RUNTIME_WORK
    assert any("unsupported_claims" in c for c in r["collapses"])


def test_no_pairs_is_insufficient_evidence() -> None:
    r = ablation_verdict([_m("m1", "A")])
    assert r["verdict"] == VERDICT_INSUFFICIENT
    assert r["pairs"] == 0


def test_unknown_config_rejected() -> None:
    r = ablation_verdict([_m("m1", "Z")])
    assert r["verdict"] == "REJECTED"
