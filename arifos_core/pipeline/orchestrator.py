"""
arifos_core/pipeline/orchestrator.py

PipelineOrchestrator - Chains stages 000→999

Executes the constitutional evaluation pipeline:
000 (Hypervisor) → 333 (Delta) → 555 (Omega) → 888 (Psi) → 999 (Seal)

Handles short-circuiting on SABAR/VOID verdicts.

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from typing import Callable, List

from arifos_core.apex.psi_kernel import Verdict

from .context import PipelineContext
from .stage_000_hypervisor import stage_000_hypervisor
from .stage_333_reason import stage_333_reason
from .stage_555_feel import stage_555_feel
from .stage_888_witness import stage_888_witness
from .stage_999_seal import stage_999_seal


class PipelineOrchestrator:
    """
    PipelineOrchestrator - Executes stages 000→999.

    Orchestrates the constitutional evaluation pipeline:
    1. Stage 000: Hypervisor preprocessing (F10-F12)
    2. Stage 333: Delta evaluation (F1-F2)
    3. Stage 555: Omega evaluation (F3-F7, F9)
    4. Stage 888: Psi verdict (F8 + final judgment)
    5. Stage 999: Seal to ledger

    Short-circuits on SABAR (hypervisor block).
    Continues through all stages even on failures (to accumulate all floor violations).

    Example:
        orchestrator = PipelineOrchestrator()
        context = PipelineContext(
            query="What is 2+2?",
            response="The answer is 4."
        )
        result = orchestrator.execute(context)
        print(result.final_verdict)  # Verdict.SEAL
    """

    def __init__(self):
        """Initialize orchestrator with default stage chain."""
        self.stages: List[Callable[[PipelineContext], PipelineContext]] = [
            stage_000_hypervisor,
            stage_333_reason,
            stage_555_feel,
            stage_888_witness,
            stage_999_seal,
        ]

    def execute(self, context: PipelineContext) -> PipelineContext:
        """
        Execute pipeline stages 000→999.

        Args:
            context: Initial pipeline context with query

        Returns:
            Final context with verdict and ledger receipt

        Raises:
            Exception: If any stage raises an exception
        """
        # Execute stages in sequence
        for stage in self.stages:
            try:
                context = stage(context)

                # Short-circuit on SABAR (hypervisor block)
                if (
                    context.psi_verdict
                    and context.psi_verdict.verdict == Verdict.SABAR
                ):
                    # Skip remaining stages, jump to seal
                    context = stage_999_seal(context)
                    break

            except Exception as e:
                # Capture stage failure
                context.failures.append(f"Stage {context.stage_reached} error: {str(e)}")
                context.metadata["pipeline_error"] = str(e)
                # Write to ledger even on pipeline failure
                context = stage_999_seal(context)
                raise

        return context

    def evaluate_query_response(
        self,
        query: str,
        response: str,
        user_id: str = None,
        session_id: str = None,
        **metrics
    ) -> PipelineContext:
        """
        Convenience method: Evaluate a query-response pair.

        Args:
            query: User input
            response: AI output
            user_id: Optional user identifier
            session_id: Optional session identifier
            **metrics: Optional ASI metrics (tri_witness, peace_squared, etc.)

        Returns:
            Final context with verdict

        Example:
            result = orchestrator.evaluate_query_response(
                query="What is arifOS?",
                response="arifOS is a constitutional AI governance framework.",
                tri_witness=0.98,
                genius_score=0.85
            )
            assert result.passed is True
        """
        context = PipelineContext(
            query=query,
            response=response,
            user_id=user_id,
            session_id=session_id,
            **metrics  # Allow overriding default metrics
        )

        return self.execute(context)


__all__ = ["PipelineOrchestrator"]
