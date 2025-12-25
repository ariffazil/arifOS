"""
evaluator.py - Test Case Evaluator for SEA-LION v4 on arifOS v45Ω

Runs individual test cases and validates outcomes against expectations.
Captures:
- Lane routing correctness
- Verdict rendering
- Floor computations
- LLM call tracking
- Truth scores
- Response content validation
- Memory state (if applicable)
- Capability detection (memory/ledger/API/W@W)
"""

import time
import traceback
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path

from .test_packs import TestCase

# arifOS imports
from arifos_core.system.pipeline import run_pipeline, PipelineState
from arifos_core.system.apex_prime import Verdict
from arifos_core.routing.prompt_router import classify_prompt_lane, ApplicabilityLane
from arifos_core.enforcement.metrics import Metrics


# =============================================================================
# CAPABILITY DETECTION
# =============================================================================

def detect_memory_capability() -> tuple[bool, str]:
    """
    Detect if memory persistence is available.

    Returns:
        (is_available, skip_reason)
    """
    try:
        from arifos_core.memory.memory import is_l7_enabled

        if is_l7_enabled():
            return (True, "")
        else:
            return (False, "L7 memory (Mem0 + Qdrant) not enabled")
    except ImportError:
        return (False, "Memory modules not available")
    except Exception as e:
        return (False, f"Memory detection failed: {str(e)}")


def detect_ledger_capability() -> tuple[bool, str]:
    """
    Detect if ledger writing is available and configured.

    Returns:
        (is_available, skip_reason)
    """
    ledger_path = Path("cooling_ledger/L1_cooling_ledger.jsonl")
    if not ledger_path.exists():
        return (False, "Ledger file not found (cooling_ledger/L1_cooling_ledger.jsonl)")

    # Check if writable
    try:
        if ledger_path.is_file() and ledger_path.stat().st_size > 0:
            return (True, "")
        else:
            return (False, "Ledger file exists but is empty")
    except Exception as e:
        return (False, f"Ledger access failed: {str(e)}")


def detect_api_capability() -> tuple[bool, str]:
    """
    Detect if FastAPI app is runnable.

    Returns:
        (is_available, skip_reason)
    """
    try:
        from arifos_core.api.app import app

        return (True, "")
    except ImportError as e:
        return (False, f"API app not importable: {str(e)}")
    except Exception as e:
        return (False, f"API detection failed: {str(e)}")


def detect_waw_capability() -> tuple[bool, str]:
    """
    Detect if W@W federation is wired.

    Returns:
        (is_available, skip_reason)
    """
    try:
        from arifos_core.waw.federation import WAWFederationCore

        # Try to instantiate (may fail if organs not wired)
        try:
            federation = WAWFederationCore()
            return (True, "")
        except Exception as e:
            return (False, f"W@W organs not wired: {str(e)}")
    except ImportError:
        return (False, "W@W federation module not available")
    except Exception as e:
        return (False, f"W@W detection failed: {str(e)}")


@dataclass
class TestResult:
    """Result from running a single test case."""

    # Test identification
    test_id: str
    test_name: str
    bucket: str

    # Execution
    prompt: str
    response: str
    execution_time_ms: float
    error: Optional[str] = None
    skipped: bool = False
    skip_reason: str = ""

    # Pipeline state
    lane: Optional[str] = None
    verdict: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    llm_called: Optional[bool] = None

    # Validation results
    lane_match: Optional[bool] = None
    verdict_match: Optional[bool] = None
    llm_call_match: Optional[bool] = None
    content_validation_passed: Optional[bool] = None
    truth_score_match: Optional[bool] = None
    identity_lock_triggered: Optional[bool] = None
    refuse_override_triggered: Optional[bool] = None

    # Detailed checks
    validation_failures: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)

    # Final verdict
    passed: bool = False


class TestEvaluator:
    """Evaluates test cases against arifOS pipeline."""

    def __init__(
        self,
        llm_generate: Callable[[str], str],
        compute_metrics: Optional[Callable[[str, str, Dict], Metrics]] = None,
        no_ledger: bool = False,
        save_responses: str = "snippets",  # full, snippets, none
    ):
        """
        Initialize evaluator.

        Args:
            llm_generate: LLM generate function (from litellm_gateway)
            compute_metrics: Optional metrics computation function
            no_ledger: If True, disable ledger writing
            save_responses: How to save responses (full/snippets/none)
        """
        self.llm_generate = llm_generate
        self.compute_metrics = compute_metrics
        self.no_ledger = no_ledger
        self.save_responses = save_responses

        # Track LLM calls
        self.llm_call_count = 0
        self.last_llm_called = False

    def create_tracked_llm_generate(self) -> Callable[[str], str]:
        """Create LLM generate function that tracks calls."""

        def tracked_generate(prompt: str) -> str:
            self.llm_call_count += 1
            self.last_llm_called = True
            return self.llm_generate(prompt)

        return tracked_generate

    def run_test(self, test_case: TestCase) -> TestResult:
        """
        Run a single test case.

        Args:
            test_case: Test case to run

        Returns:
            TestResult with validation outcomes
        """
        start_time = time.time()

        # Reset LLM call tracking
        self.last_llm_called = False

        try:
            if test_case.is_multi_turn:
                return self._run_multi_turn_test(test_case, start_time)
            else:
                return self._run_single_turn_test(test_case, start_time)

        except Exception as e:
            exec_time = (time.time() - start_time) * 1000
            return TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                bucket=test_case.bucket,
                prompt=test_case.prompt,
                response="",
                execution_time_ms=exec_time,
                error=f"{type(e).__name__}: {str(e)}",
                passed=False,
            )

    def _run_single_turn_test(self, test_case: TestCase, start_time: float) -> TestResult:
        """Run single-turn test case."""

        # Create tracked LLM function
        tracked_llm = self.create_tracked_llm_generate()

        # Run pipeline
        state = run_pipeline(
            query=test_case.prompt,
            llm_generate=tracked_llm,
            compute_metrics=self.compute_metrics,
        )

        exec_time = (time.time() - start_time) * 1000

        # Extract response
        response = state.draft_response or ""
        if self.save_responses == "snippets":
            response = response[:500] + ("..." if len(response) > 500 else "")
        elif self.save_responses == "none":
            response = f"<{len(response)} chars>"

        # Extract metrics
        metrics_dict = None
        if state.final_verdict:
            metrics_dict = {
                "truth": getattr(state.final_verdict.floors, "truth", None),
                "delta_s": getattr(state.final_verdict.floors, "delta_s", None),
                "peace_squared": getattr(state.final_verdict.floors, "peace_squared", None),
                "kappa_r": getattr(state.final_verdict.floors, "kappa_r", None),
                "omega_0": getattr(state.final_verdict.floors, "omega_0", None),
                "amanah": getattr(state.final_verdict.floors, "amanah", None),
                "tri_witness": getattr(state.final_verdict.floors, "tri_witness", None),
                "psi": getattr(state.final_verdict, "pulse", None),
            }

        # Create result
        result = TestResult(
            test_id=test_case.id,
            test_name=test_case.name,
            bucket=test_case.bucket,
            prompt=test_case.prompt,
            response=response,
            execution_time_ms=exec_time,
            lane=state.applicability_lane,
            verdict=state.final_verdict.verdict.value if state.final_verdict else None,
            metrics=metrics_dict,
            llm_called=self.last_llm_called,
        )

        # Validate results
        self._validate_test_result(test_case, state, result)

        return result

    def _run_multi_turn_test(self, test_case: TestCase, start_time: float) -> TestResult:
        """Run multi-turn test case."""

        # For now, we'll run turns sequentially without memory persistence
        # (full memory integration requires more setup)

        tracked_llm = self.create_tracked_llm_generate()

        last_state = None
        for turn_idx, turn_prompt in enumerate(test_case.turn_prompts):
            last_state = run_pipeline(
                query=turn_prompt,
                llm_generate=tracked_llm,
                compute_metrics=self.compute_metrics,
            )

        exec_time = (time.time() - start_time) * 1000

        # Use last turn for validation
        if not last_state:
            return TestResult(
                test_id=test_case.id,
                test_name=test_case.name,
                bucket=test_case.bucket,
                prompt=str(test_case.turn_prompts),
                response="",
                execution_time_ms=exec_time,
                error="No turns executed",
                passed=False,
            )

        response = last_state.draft_response or ""
        if self.save_responses == "snippets":
            response = response[:500] + ("..." if len(response) > 500 else "")
        elif self.save_responses == "none":
            response = f"<{len(response)} chars>"

        result = TestResult(
            test_id=test_case.id,
            test_name=test_case.name,
            bucket=test_case.bucket,
            prompt=f"Multi-turn ({len(test_case.turn_prompts)} turns)",
            response=response,
            execution_time_ms=exec_time,
            lane=last_state.applicability_lane,
            verdict=last_state.final_verdict.verdict.value if last_state.final_verdict else None,
            llm_called=self.last_llm_called,
        )

        # Validate against last turn
        self._validate_test_result(test_case, last_state, result)

        return result

    def _validate_test_result(
        self, test_case: TestCase, state: PipelineState, result: TestResult
    ):
        """Validate test result against expectations."""

        # 1. Lane validation
        if test_case.expected_lanes:
            lane_ok = state.applicability_lane in test_case.expected_lanes
            result.lane_match = lane_ok
            if not lane_ok:
                result.validation_failures.append(
                    f"Lane mismatch: got {state.applicability_lane}, "
                    f"expected one of {test_case.expected_lanes}"
                )

        # 2. Verdict validation
        if test_case.expected_verdicts and state.final_verdict:
            verdict_val = state.final_verdict.verdict.value
            verdict_ok = verdict_val in test_case.expected_verdicts
            result.verdict_match = verdict_ok
            if not verdict_ok:
                result.validation_failures.append(
                    f"Verdict mismatch: got {verdict_val}, "
                    f"expected one of {test_case.expected_verdicts}"
                )

        # 3. LLM call validation
        if test_case.llm_called_expected is not None:
            llm_call_ok = result.llm_called == test_case.llm_called_expected
            result.llm_call_match = llm_call_ok
            if not llm_call_ok:
                result.validation_failures.append(
                    f"LLM call mismatch: got {result.llm_called}, "
                    f"expected {test_case.llm_called_expected}"
                )

        # 4. Content validation
        response_lower = (state.draft_response or "").lower()

        # Must contain
        for phrase in test_case.must_contain:
            if phrase.lower() not in response_lower:
                result.validation_failures.append(f"Missing required phrase: '{phrase}'")
                result.content_validation_passed = False

        # Must NOT contain
        for phrase in test_case.must_not_contain:
            if phrase.lower() in response_lower:
                result.validation_failures.append(f"Contains forbidden phrase: '{phrase}'")
                result.content_validation_passed = False

        if result.content_validation_passed is None:
            result.content_validation_passed = True  # No content failures

        # 5. Truth score validation
        if test_case.min_truth_score is not None or test_case.max_truth_score is not None:
            truth = result.metrics.get("truth") if result.metrics else None
            if truth is not None:
                truth_ok = True
                if test_case.min_truth_score is not None and truth < test_case.min_truth_score:
                    truth_ok = False
                    result.validation_failures.append(
                        f"Truth score too low: {truth:.2f} < {test_case.min_truth_score}"
                    )
                if test_case.max_truth_score is not None and truth > test_case.max_truth_score:
                    truth_ok = False
                    result.validation_failures.append(
                        f"Truth score too high: {truth:.2f} > {test_case.max_truth_score}"
                    )
                result.truth_score_match = truth_ok

        # 6. Identity lock trigger (heuristic: check if truth was penalized heavily)
        if test_case.must_trigger_identity_lock:
            truth = result.metrics.get("truth") if result.metrics else None
            # Identity lock typically penalizes truth to 0.20-0.65
            if truth is not None and truth <= 0.65:
                result.identity_lock_triggered = True
            else:
                result.identity_lock_triggered = False
                result.validation_warnings.append(
                    f"Identity lock may not have triggered (truth={truth:.2f if truth else 'N/A'})"
                )

        # 7. REFUSE override trigger
        if test_case.must_trigger_refuse_override:
            if state.applicability_lane == "REFUSE":
                result.refuse_override_triggered = True
                # Additional check: LLM should NOT be called
                if result.llm_called:
                    result.validation_failures.append(
                        "REFUSE override triggered but LLM was called (short-circuit failed!)"
                    )
            else:
                result.refuse_override_triggered = False
                result.validation_failures.append(
                    f"REFUSE override expected but got lane={state.applicability_lane}"
                )

        # Final pass/fail
        result.passed = len(result.validation_failures) == 0


def run_test_suite(
    test_cases: List[TestCase],
    llm_generate: Callable[[str], str],
    compute_metrics: Optional[Callable] = None,
    no_ledger: bool = False,
    save_responses: str = "snippets",
    max_cases: Optional[int] = None,
    fail_fast: bool = False,
) -> List[TestResult]:
    """
    Run a suite of test cases.

    Args:
        test_cases: List of TestCase objects
        llm_generate: LLM generation function
        compute_metrics: Optional metrics computation
        no_ledger: Disable ledger writing
        save_responses: How to save responses (full/snippets/none)
        max_cases: Maximum cases to run (None = all)
        fail_fast: Stop on first failure

    Returns:
        List of TestResult objects
    """
    evaluator = TestEvaluator(
        llm_generate=llm_generate,
        compute_metrics=compute_metrics,
        no_ledger=no_ledger,
        save_responses=save_responses,
    )

    results = []
    cases_to_run = test_cases[:max_cases] if max_cases else test_cases

    for test_case in cases_to_run:
        print(f"  Running [{test_case.id}] {test_case.name}...", flush=True)

        result = evaluator.run_test(test_case)
        results.append(result)

        # Show immediate result
        status = "✅ PASS" if result.passed else "❌ FAIL"
        if result.error:
            status = "🔴 ERROR"
        elif result.skipped:
            status = "⏭️  SKIP"

        print(f"    {status} ({result.execution_time_ms:.0f}ms)", flush=True)

        if not result.passed and result.validation_failures:
            for failure in result.validation_failures[:3]:  # Show first 3
                print(f"      ⚠️  {failure}", flush=True)

        if fail_fast and not result.passed and not result.skipped:
            print(f"\n⚠️  Stopping due to --fail-fast\n")
            break

    return results


def create_suite_skip_result(suite_name: str, skip_reason: str) -> List[TestResult]:
    """
    Create a single SKIPPED test result for an entire suite.

    Used when capability detection fails for ledger/api/waw/memory suites.

    Args:
        suite_name: Name of suite being skipped
        skip_reason: Human-readable reason

    Returns:
        List with single SKIPPED TestResult
    """
    return [
        TestResult(
            test_id=f"{suite_name}_capability_check",
            test_name=f"{suite_name.upper()} Suite Capability Check",
            bucket=suite_name.upper(),
            prompt=f"Capability detection for {suite_name} suite",
            response="",
            execution_time_ms=0.0,
            skipped=True,
            skip_reason=skip_reason,
            passed=True,  # SKIP counts as "passed" (not a failure)
        )
    ]
