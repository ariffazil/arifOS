from functools import wraps
from typing import Callable, Any, Dict, Optional, List

# CORRECTED IMPORTS — Direct imports from source modules, not __init__
from .metrics import Metrics
from .APEX_PRIME import apex_review, ApexVerdict
from .eye_sentinel import EyeSentinel, EyeReport
from .memory.cooling_ledger import log_cooling_entry

import logging

logger = logging.getLogger("arifos_core.guard")


class GuardrailError(Exception):
    """Raised when apex_guardrail is misconfigured."""
    pass


def apex_guardrail(
    *,
    high_stakes: bool = False,
    tri_witness_threshold: float = 0.95,
    compute_metrics: Callable[[str, str, Dict[str, Any]], Metrics],
    cooling_ledger_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
    eye_sentinel: Optional[EyeSentinel] = None,
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """
    Decorator to enforce APEX PRIME governance around an answer-generation function.

    compute_metrics(user_input, raw_answer, context) → Metrics

    This decorator:
    - Calls the wrapped function to obtain a raw answer
    - Computes metrics
    - Applies apex_review to decide SEAL / PARTIAL / VOID
    - Logs a Cooling Ledger entry
    - Returns answer or refusal text based on verdict
    """
    if compute_metrics is None:
        raise GuardrailError("apex_guardrail requires a compute_metrics callable.")

    def decorator(fn: Callable[..., str]) -> Callable[..., str]:
        @wraps(fn)
        def wrapper(*args, **kwargs) -> str:
            # Extract user_input
            if "user_input" in kwargs:
                user_input = kwargs["user_input"]
            elif len(args) >= 1:
                user_input = args[0]
            else:
                raise GuardrailError("Expected user_input as first arg or kwarg.")

            raw_answer: str = fn(*args, **kwargs)
            context: Dict[str, Any] = {**kwargs}

            # Compute constitutional metrics
            metrics: Metrics = compute_metrics(user_input, raw_answer, context)

            # Optional @EYE Sentinel audit
            eye_report: Optional[EyeReport] = None
            eye_blocking: bool = False
            if eye_sentinel is not None:
                try:
                    eye_report = eye_sentinel.audit(
                        draft_text=raw_answer,
                        metrics=metrics,
                        context=context,
                    )
                    eye_blocking = eye_report.has_blocking_issue()
                except Exception:
                    # @EYE failures must never break the guarded function
                    logger.exception(
                        "@EYE Sentinel audit failed; proceeding without @EYE blocking."
                    )

            # APEX PRIME judgment
            verdict: ApexVerdict = apex_review(
                metrics,
                high_stakes=high_stakes,
                tri_witness_threshold=tri_witness_threshold,
                eye_blocking=eye_blocking,
            )

            # Prepare ledger context
            job_id: str = context.get("job_id", "unknown")
            pipeline_path: List[str] = context.get("pipeline_path", [])
            stakes: str = context.get("stakes", "high" if high_stakes else "normal")

            # Log to Cooling Ledger
            ledger_entry = log_cooling_entry(
                job_id=job_id,
                verdict=verdict,
                metrics=metrics,
                query=str(user_input),
                candidate_output=raw_answer,
                eye_report=eye_report,
                stakes=stakes,
                pipeline_path=pipeline_path,
                context_summary=context.get("context_summary", ""),
                tri_witness_components=context.get("tri_witness_components"),
                logger=logger,
                high_stakes=high_stakes,
            )

            if cooling_ledger_sink:
                cooling_ledger_sink(ledger_entry)

            # Final emission based on verdict (v35Ω verdict hierarchy)
            if verdict == "SABAR":
                return (
                    "[SABAR] Stop. Acknowledge. Breathe. Adjust. Resume. "
                    "@EYE Sentinel detected a blocking issue."
                )
            if verdict == "VOID":
                return "[VOID] This answer was refused by ArifOS constitutional floors."
            if verdict == "888_HOLD":
                return (
                    "[888_HOLD] Constitutional judiciary hold — extended floor failure. "
                    "Please clarify or rephrase."
                )
            if verdict == "PARTIAL":
                return (
                    f"[PARTIAL] {raw_answer}\n\n"
                    "(Answer issued with constitutional hedges due to floor concerns)"
                )

            return raw_answer  # SEALED — safe to emit

        return wrapper

    return decorator


__all__ = ["apex_guardrail", "GuardrailError"]
