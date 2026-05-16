# arifOS SENSE Pipeline — Phase 4E Pipeline Metrics Tests
# DITEMPA BUKAN DIBERI

from __future__ import annotations


from arifosmcp.runtime.planner_metrics import (
    MetricsCollector,
    PipelineStage,
    StageMetrics,
)


class TestT1MetricsCollector:
    def test_stage_context_times_execution(self):
        collector = MetricsCollector(query="python tutorial", query_mode="realtime")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
            m.output_count = 3
        assert len(collector._pipeline_metrics.stages) == 1
        assert collector._pipeline_metrics.stages[0].stage == PipelineStage.QUERY_PLANNING
        assert collector._pipeline_metrics.stages[0].duration_ms > 0

    def test_multiple_stages_accumulate(self):
        collector = MetricsCollector(query="python tutorial", query_mode="realtime")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
            m.output_count = 3
        with collector.stage(PipelineStage.PROVIDER_SEARCH) as m:
            m.input_count = 3
            m.output_count = 10
        assert len(collector._pipeline_metrics.stages) == 2
        assert collector._pipeline_metrics.stages[0].stage == PipelineStage.QUERY_PLANNING
        assert collector._pipeline_metrics.stages[1].stage == PipelineStage.PROVIDER_SEARCH

    def test_stage_error_count(self):
        collector = MetricsCollector(query="test", query_mode="realtime")
        with collector.stage(PipelineStage.NORMALIZATION) as m:
            m.input_count = 5
            m.output_count = 4
            m.error_count = 1
        assert collector._pipeline_metrics.stages[0].error_count == 1


class TestT2StageMetrics:
    def test_throughput_calculation(self):
        m = StageMetrics(stage=PipelineStage.QUERY_PLANNING, duration_ms=100.0, input_count=50)
        assert m.throughput == 500.0

    def test_pass_rate(self):
        m = StageMetrics(
            stage=PipelineStage.PREFILTER, duration_ms=10.0, input_count=10, output_count=7
        )
        assert m.pass_rate == 0.7

    def test_error_rate(self):
        m = StageMetrics(
            stage=PipelineStage.VERIFICATION, duration_ms=50.0, input_count=20, error_count=2
        )
        assert m.error_rate == 0.1

    def test_zero_duration_throughput(self):
        m = StageMetrics(stage=PipelineStage.RERANKING, duration_ms=0.0, input_count=10)
        assert m.throughput == 0.0

    def test_zero_input_pass_rate(self):
        m = StageMetrics(stage=PipelineStage.SPAN_EXTRACTION, duration_ms=5.0, input_count=0)
        assert m.pass_rate == 0.0


class TestT3PipelineMetrics:
    def test_finish_calculates_total_duration(self):
        collector = MetricsCollector(query="python", query_mode="realtime")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
            m.output_count = 3
        with collector.stage(PipelineStage.PROVIDER_SEARCH) as m:
            m.input_count = 3
            m.output_count = 10
        metrics = collector.finish(final_result_count=10)
        assert metrics.total_duration_ms() > 0
        assert len(metrics.stages) == 2

    def test_final_result_count(self):
        collector = MetricsCollector(query="python", query_mode="semantic")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
        metrics = collector.finish(final_result_count=7, final_trusted_count=3)
        assert metrics.final_result_count == 7
        assert metrics.final_trusted_count == 3

    def test_total_input_count(self):
        collector = MetricsCollector(query="test", query_mode="research")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
        with collector.stage(PipelineStage.PROVIDER_SEARCH) as m:
            m.input_count = 5
        with collector.stage(PipelineStage.NORMALIZATION) as m:
            m.input_count = 20
        metrics = collector.finish()
        assert metrics.total_input_count() == 26

    def test_overall_pass_rate(self):
        collector = MetricsCollector(query="test", query_mode="realtime")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 10
        metrics = collector.finish(final_result_count=6)
        assert metrics.overall_pass_rate() == 0.6

    def test_summary(self):
        collector = MetricsCollector(query="python tutorial", query_mode="realtime")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
        metrics = collector.finish(final_result_count=5)
        summary = metrics.summary()
        assert "python tutorial" in summary
        assert "realtime" in summary
        assert "Results: 5" in summary

    def test_to_dict(self):
        collector = MetricsCollector(query="test", query_mode="semantic")
        with collector.stage(PipelineStage.QUERY_PLANNING) as m:
            m.input_count = 1
            m.output_count = 2
        metrics = collector.finish(final_result_count=2)
        d = metrics.to_dict()
        assert d["query"] == "test"
        assert d["query_mode"] == "semantic"
        assert d["final_result_count"] == 2
        assert len(d["stages"]) == 1


class TestT4EmptyPipeline:
    def test_finish_with_zero_results(self):
        collector = MetricsCollector(query="nothing found", query_mode="realtime")
        metrics = collector.finish(final_result_count=0, final_trusted_count=0)
        assert metrics.final_result_count == 0
        assert metrics.overall_pass_rate() == 0.0
        assert len(metrics.stages) == 0

    def test_total_errors_on_empty(self):
        collector = MetricsCollector(query="test", query_mode="realtime")
        metrics = collector.finish()
        assert metrics.total_errors() == 0


class TestT5PipelineStages:
    def test_all_stages_present(self):
        stages = list(PipelineStage)
        expected = [
            "query_planning",
            "provider_search",
            "normalization",
            "prefilter",
            "reranking",
            "curation",
            "span_extraction",
            "verification",
        ]
        assert len(stages) == 8
        assert [s.value for s in stages] == expected

    def test_stage_string_values(self):
        assert PipelineStage.QUERY_PLANNING.value == "query_planning"
        assert PipelineStage.VERIFICATION.value == "verification"
