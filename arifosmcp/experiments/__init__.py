"""arifOS experiments — the world-model loop.

probe → observe → compare → update → close
"""

from arifosmcp.experiments.loop import (
    CompareResult,
    ExperimentCard,
    ExperimentStage,
    ExperimentVerdict,
    Hypothesis,
    LoopContext,
    Observation,
    ProbeSpec,
    compare,
    observe,
    open_experiment,
    run_simple_experiment,
    update,
)

__all__ = [
    "CompareResult",
    "ExperimentCard",
    "ExperimentStage",
    "ExperimentVerdict",
    "Hypothesis",
    "LoopContext",
    "Observation",
    "ProbeSpec",
    "compare",
    "observe",
    "open_experiment",
    "run_simple_experiment",
    "update",
]
