from functools import wraps
from typing import Callable, Any, Dict, Optional, List
from . import Metrics, apex_review, log_cooling_entry, ApexVerdict
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
) -> Callable[[Callable[..., str]], Callable[..., str]]:
    """Decorator to enforce APEX PRIME governance around an answer-generation function.

    compute_metrics(user_input, raw_answer, context) -> Metrics

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
            if "user_input" in kwargs:
                user_input = kwargs["user_input"]
            elif len(args) >= 1:
                user_input = args[0]
            else:
                raise GuardrailError("Expected user_input as first arg or kwarg.")

            raw_answer: str = fn(*args, **kwargs)
            context: Dict[str, Any] = {**kwargs}

            metrics: Metrics = compute_metrics(user_input, raw_answer, context)
            verdict: ApexVerdict = apex_review(
                metrics,
                high_stakes=high_stakes,
                tri_witness_threshold=tri_witness_threshold,
            )

            job_id: str = context.get("job_id", "unknown")
            pipeline_path: List[str] = context.get("pipeline_path", [])
            stakes: str = context.get("stakes", "high" if high_stakes else "normal")

            ledger_entry = log_cooling_entry(
                job_id=job_id,
                verdict=verdict,
                metrics=metrics,
                stakes=stakes,
                pipeline_path=pipeline_path,
                context_summary=context.get("context_summary", ""),
                tri_witness_components=context.get("tri_witness_components"),
                logger=logger,
            )

            if cooling_ledger_sink:
                cooling_ledger_sink(ledger_entry)

            if verdict == "VOID":
                return "[VOID] This answer was refused by ArifOS floors."
            if verdict == "PARTIAL":
                # By default we return the raw answer; callers may wrap or adjust further.
                return raw_answer
            return raw_answer

        return wrapper

    return decorator
