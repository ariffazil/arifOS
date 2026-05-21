# arifOS SENSE Pipeline — Metrics Collection
# 8-stage pipeline metrics for SENSE pipeline observability
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class PipelineStage(StrEnum):
    QUERY_PLANNING = "query_planning"
    PROVIDER_SEARCH = "provider_search"
    NORMALIZATION = "normalization"
    PREFILTER = "prefilter"
    RERANKING = "reranking"
    CURATION = "curation"
    SPAN_EXTRACTION = "span_extraction"
    VERIFICATION = "verification"


@dataclass
class StageMetrics:
    stage: PipelineStage
    duration_ms: float
    input_count: int = 0
    output_count: int = 0
    error_count: int = 0

    @property
    def throughput(self) -> float:
        if self.duration_ms <= 0:
            return 0.0
        return self.input_count / (self.duration_ms / 1000.0)

    @property
    def pass_rate(self) -> float:
        if self.input_count == 0:
            return 0.0
        return self.output_count / self.input_count

    @property
    def error_rate(self) -> float:
        if self.input_count == 0:
            return 0.0
        return self.error_count / self.input_count


@dataclass
class PipelineMetrics:
    query: str
    query_mode: str
    stages: list[StageMetrics] = field(default_factory=list)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    final_result_count: int = 0
    final_trusted_count: int = 0

    def add_stage(self, metrics: StageMetrics) -> None:
        self.stages.append(metrics)

    def total_duration_ms(self) -> float:
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds() * 1000
        return sum(s.duration_ms for s in self.stages)

    def total_input_count(self) -> int:
        return sum(s.input_count for s in self.stages)

    def total_errors(self) -> int:
        return sum(s.error_count for s in self.stages)

    def overall_pass_rate(self) -> float:
        if not self.stages:
            return 0.0
        first = self.stages[0]
        if first.input_count == 0:
            return 0.0
        return self.final_result_count / first.input_count

    def finish(self, final_result_count: int = 0, final_trusted_count: int = 0) -> PipelineMetrics:
        self.finished_at = datetime.now(UTC)
        self.final_result_count = final_result_count
        self.final_trusted_count = final_trusted_count
        return self

    def summary(self) -> str:
        stages_str = ", ".join(s.stage.value for s in self.stages)
        return (
            f"Query: {self.query!r} [{self.query_mode}] | "
            f"Stages: {len(self.stages)} ({stages_str}) | "
            f"Results: {self.final_result_count} "
            f"(trusted: {self.final_trusted_count}) | "
            f"Duration: {self.total_duration_ms():.1f}ms"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "query_mode": self.query_mode,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "total_duration_ms": self.total_duration_ms(),
            "total_input_count": self.total_input_count(),
            "total_errors": self.total_errors(),
            "overall_pass_rate": self.overall_pass_rate(),
            "final_result_count": self.final_result_count,
            "final_trusted_count": self.final_trusted_count,
            "stages": [
                {
                    "stage": s.stage.value,
                    "duration_ms": s.duration_ms,
                    "input_count": s.input_count,
                    "output_count": s.output_count,
                    "error_count": s.error_count,
                    "throughput": s.throughput,
                    "pass_rate": s.pass_rate,
                    "error_rate": s.error_rate,
                }
                for s in self.stages
            ],
        }


class MetricsCollector:
    __slots__ = ("query", "query_mode", "_pipeline_metrics")

    def __init__(self, query: str, query_mode: str = "realtime") -> None:
        self.query = query
        self.query_mode = query_mode
        self._pipeline_metrics = PipelineMetrics(query=query, query_mode=query_mode)

    @contextmanager
    def stage(self, stage: PipelineStage) -> Generator[StageMetrics, None, None]:
        metrics = StageMetrics(stage=stage, duration_ms=0.0)
        start = time.monotonic()
        try:
            yield metrics
        finally:
            metrics.duration_ms = (time.monotonic() - start) * 1000
            self._pipeline_metrics.add_stage(metrics)

    def finish(self, final_result_count: int = 0, final_trusted_count: int = 0) -> PipelineMetrics:
        return self._pipeline_metrics.finish(
            final_result_count=final_result_count,
            final_trusted_count=final_trusted_count,
        )
