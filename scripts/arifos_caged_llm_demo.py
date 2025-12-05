#!/usr/bin/env python3
"""
arifos_caged_llm_demo.py — Caged LLM Harness for arifOS v35Ω

This script demonstrates how to run an arbitrary LLM through the full
arifOS constitutional governance stack:

    User Prompt → call_model() → W@W Federation → @EYE → APEX PRIME → Verdict

Usage (CLI):
    python -m scripts.arifos_caged_llm_demo "What is the capital of Malaysia?"
    python -m scripts.arifos_caged_llm_demo --high-stakes "Should I invest in crypto?"

Usage (Python/Colab):
    from scripts.arifos_caged_llm_demo import cage_llm_response, CagedResult

    result = cage_llm_response(
        prompt="What is the capital of Malaysia?",
        call_model=my_openai_call,  # Your LLM function
    )
    print(result.verdict, result.final_response)

The key integration point is `call_model(messages) -> str`:
- Replace the stub with your LLM provider (OpenAI, Claude, HuggingFace, etc.)
- See PROVIDER INTEGRATION section below for examples

Author: arifOS Project
Version: v35Ω
"""

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# Add parent to path for imports when run as script
if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifos_core.pipeline import Pipeline, PipelineState, StakesClass
from arifos_core.metrics import Metrics, check_anti_hantu
from arifos_core.eye_sentinel import EyeSentinel
from arifos_core.waw import WAWFederationCore, FederationVerdict
from arifos_core.APEX_PRIME import ApexVerdict


# =============================================================================
# RESULT DATACLASS
# =============================================================================

@dataclass
class CagedResult:
    """
    Result from running an LLM response through arifOS constitutional cage.

    Attributes:
        prompt: Original user prompt
        raw_llm_response: Raw response from call_model()
        final_response: Final response after constitutional processing
        verdict: APEX PRIME verdict (SEAL/PARTIAL/VOID/888_HOLD/SABAR)
        metrics: Constitutional metrics snapshot
        waw_verdict: W@W Federation verdict (if evaluated)
        eye_blocking: Whether @EYE raised a blocking issue
        stage_trace: Pipeline stages traversed
        floor_failures: List of failed floor reasons
        job_id: Unique job identifier
    """
    prompt: str
    raw_llm_response: str
    final_response: str
    verdict: ApexVerdict
    metrics: Optional[Metrics]
    waw_verdict: Optional[FederationVerdict]
    eye_blocking: bool
    stage_trace: List[str]
    floor_failures: List[str]
    job_id: str

    def is_sealed(self) -> bool:
        """Check if response was fully approved (SEAL)."""
        return self.verdict == "SEAL"

    def is_blocked(self) -> bool:
        """Check if response was blocked (VOID/SABAR)."""
        return self.verdict in ("VOID", "SABAR")

    def summary(self) -> str:
        """Return a short summary string."""
        status = "✓" if self.is_sealed() else "⚠" if self.verdict == "PARTIAL" else "✗"
        return f"[{status} {self.verdict}] {self.job_id}"


# =============================================================================
# CALL_MODEL STUB — REPLACE WITH YOUR LLM PROVIDER
# =============================================================================

def stub_call_model(messages: List[Dict[str, str]]) -> str:
    """
    STUB: Replace this with your actual LLM call.

    This stub just echoes back a structured response for testing.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
                  e.g. [{"role": "user", "content": "Hello"}]

    Returns:
        Raw string response from the LLM

    PROVIDER INTEGRATION EXAMPLES:

    # OpenAI
    def call_openai(messages):
        import openai
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )
        return response.choices[0].message.content

    # Anthropic Claude
    def call_claude(messages):
        import anthropic
        client = anthropic.Anthropic()
        # Convert to Claude format
        user_content = messages[-1]["content"] if messages else ""
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_content}],
        )
        return response.content[0].text

    # HuggingFace Transformers (local)
    def call_huggingface(messages):
        from transformers import pipeline
        generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")
        prompt = messages[-1]["content"] if messages else ""
        result = generator(prompt, max_new_tokens=256)
        return result[0]["generated_text"]

    # SEA-LION (via arifOS adapter)
    def call_sealion(messages):
        from arifos_core.adapters.llm_sealion import make_llm_generate
        generate = make_llm_generate(model_shorthand="qwen-7b")
        prompt = messages[-1]["content"] if messages else ""
        return generate(prompt)
    """
    # Extract user content from messages
    user_content = ""
    for msg in messages:
        if msg.get("role") == "user":
            user_content = msg.get("content", "")

    # Stub response
    return (
        f"[STUB RESPONSE] I received your query: '{user_content[:100]}...'\n\n"
        f"This is a placeholder response. Replace stub_call_model() with your "
        f"actual LLM provider to get real responses.\n\n"
        f"The response demonstrates constitutional governance in action."
    )


# =============================================================================
# METRICS COMPUTATION HELPER
# =============================================================================

def compute_metrics_from_response(
    query: str,
    response: str,
    context: Dict[str, Any],
) -> Metrics:
    """
    Compute constitutional metrics for an LLM response.

    This is a simple heuristic implementation. In production, you might:
    - Use embeddings for semantic similarity (Truth)
    - Use sentiment analysis (Peace²)
    - Use actual token entropy (ΔS)

    Args:
        query: Original user query
        response: LLM response text
        context: Additional context dict

    Returns:
        Metrics object with all floor values
    """
    response_lower = response.lower()

    # F1: Truth heuristic - longer, structured responses score higher
    truth_score = 0.99 if len(response) > 50 else 0.85

    # F2: Clarity (ΔS) - responses with structure add clarity
    delta_s = 0.15 if len(response) > 100 else 0.05

    # F3: Stability (Peace²) - baseline
    peace_squared = 1.2

    # F4: Empathy (κᵣ) - check for empathy phrases
    empathy_phrases = ["i understand", "that sounds", "thank you", "let me help"]
    empathy_bonus = sum(0.01 for p in empathy_phrases if p in response_lower)
    kappa_r = min(1.0, 0.96 + empathy_bonus)

    # F9: Anti-Hantu check
    anti_hantu_pass, violations = check_anti_hantu(response)

    return Metrics(
        truth=truth_score,
        delta_s=delta_s,
        peace_squared=peace_squared,
        kappa_r=kappa_r,
        omega_0=0.04,  # Fixed humility band per spec
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        anti_hantu=anti_hantu_pass,
    )


# =============================================================================
# CORE CAGE FUNCTION
# =============================================================================

def cage_llm_response(
    prompt: str,
    call_model: Optional[Callable[[List[Dict[str, str]]], str]] = None,
    high_stakes: bool = False,
    run_waw: bool = True,
    job_id: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> CagedResult:
    """
    Run an LLM response through the full arifOS constitutional cage.

    This is the main entry point for caged LLM execution.

    Flow:
        1. Build messages structure
        2. Call LLM via call_model()
        3. Run through 000→999 pipeline (AAA engines, @EYE, APEX PRIME)
        4. Optionally run W@W Federation evaluation
        5. Return CagedResult with verdict and audit trail

    Args:
        prompt: User prompt/query
        call_model: Function that takes messages and returns response string.
                   If None, uses stub_call_model() for testing.
        high_stakes: Force high-stakes (Class B) routing
        run_waw: Whether to run W@W Federation evaluation (default True)
        job_id: Optional job identifier for tracking
        system_prompt: Optional system prompt to prepend

    Returns:
        CagedResult with verdict, metrics, and audit trail

    Example:
        # With stub (for testing)
        result = cage_llm_response("What is 2+2?")

        # With real OpenAI
        result = cage_llm_response(
            prompt="Explain quantum computing",
            call_model=my_openai_function,
            high_stakes=False,
        )
    """
    # Use stub if no call_model provided
    if call_model is None:
        call_model = stub_call_model

    # Generate job ID
    job_id = job_id or str(uuid.uuid4())[:8]

    # Build messages
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Step 1: Call the LLM
    raw_response = call_model(messages)

    # Step 2: Create LLM wrapper for pipeline
    # The pipeline expects llm_generate(prompt_str) -> str
    def llm_generate(prompt_str: str) -> str:
        return raw_response  # Return the already-generated response

    # Step 3: Create @EYE Sentinel
    eye_sentinel = EyeSentinel()

    # Step 4: Run through pipeline
    pipeline = Pipeline(
        llm_generate=llm_generate,
        compute_metrics=compute_metrics_from_response,
        eye_sentinel=eye_sentinel,
    )

    state: PipelineState = pipeline.run(
        query=prompt,
        job_id=job_id,
        force_class=StakesClass.CLASS_B if high_stakes else None,
    )

    # Step 5: Optional W@W Federation evaluation
    waw_verdict: Optional[FederationVerdict] = None
    if run_waw and state.metrics is not None:
        waw_federation = WAWFederationCore()
        waw_verdict = waw_federation.evaluate(
            output_text=state.draft_response or raw_response,
            metrics=state.metrics,
            context={"high_stakes": high_stakes},
        )

    # Step 6: Check @EYE blocking
    eye_blocking = False
    if state.metrics is not None:
        eye_report = eye_sentinel.audit(
            draft_text=state.draft_response or raw_response,
            metrics=state.metrics,
            context={},
        )
        eye_blocking = eye_report.has_blocking_issue()

    # Step 7: Build result
    return CagedResult(
        prompt=prompt,
        raw_llm_response=raw_response,
        final_response=state.raw_response,
        verdict=state.verdict or "VOID",
        metrics=state.metrics,
        waw_verdict=waw_verdict,
        eye_blocking=eye_blocking,
        stage_trace=state.stage_trace,
        floor_failures=state.floor_failures if hasattr(state, 'floor_failures') else [],
        job_id=job_id,
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point for caged LLM demo."""
    parser = argparse.ArgumentParser(
        description="Run LLM responses through arifOS constitutional cage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m scripts.arifos_caged_llm_demo "What is the capital of Malaysia?"
    python -m scripts.arifos_caged_llm_demo --high-stakes "Should I invest in crypto?"
    echo "Hello world" | python -m scripts.arifos_caged_llm_demo --stdin

Integration:
    Replace stub_call_model() in this file with your LLM provider.
    See the docstring for OpenAI, Claude, and HuggingFace examples.
        """,
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="User prompt to process",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read prompt from stdin",
    )
    parser.add_argument(
        "--high-stakes",
        action="store_true",
        help="Force high-stakes (Class B) routing",
    )
    parser.add_argument(
        "--no-waw",
        action="store_true",
        help="Skip W@W Federation evaluation",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output",
    )

    args = parser.parse_args()

    # Get prompt
    if args.stdin:
        prompt = sys.stdin.read().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.print_help()
        sys.exit(1)

    if not prompt:
        print("Error: No prompt provided", file=sys.stderr)
        sys.exit(1)

    # Run through cage
    print(f"{'='*60}")
    print(f"arifOS v35Ω — Caged LLM Demo")
    print(f"{'='*60}")
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    print(f"High-stakes: {args.high_stakes}")
    print(f"{'='*60}\n")

    result = cage_llm_response(
        prompt=prompt,
        call_model=stub_call_model,  # Replace with your LLM
        high_stakes=args.high_stakes,
        run_waw=not args.no_waw,
    )

    # Print results
    print(f"Job ID: {result.job_id}")
    print(f"Verdict: {result.verdict}")
    print(f"Eye Blocking: {result.eye_blocking}")
    print(f"Stage Trace: {' → '.join(result.stage_trace)}")

    if result.metrics:
        print(f"\nMetrics:")
        print(f"  Truth: {result.metrics.truth:.3f}")
        print(f"  ΔS: {result.metrics.delta_s:.3f}")
        print(f"  Peace²: {result.metrics.peace_squared:.3f}")
        print(f"  κᵣ: {result.metrics.kappa_r:.3f}")
        print(f"  Ω₀: {result.metrics.omega_0:.3f}")
        print(f"  Ψ: {result.metrics.psi:.3f}" if result.metrics.psi else "  Ψ: N/A")
        print(f"  Anti-Hantu: {result.metrics.anti_hantu}")

    if result.waw_verdict:
        print(f"\nW@W Federation:")
        print(f"  Verdict: {result.waw_verdict.verdict}")
        print(f"  Veto organs: {result.waw_verdict.veto_organs}")

    if args.verbose or result.is_blocked():
        print(f"\n{'='*60}")
        print("RAW LLM RESPONSE:")
        print(f"{'='*60}")
        print(result.raw_llm_response)

    print(f"\n{'='*60}")
    print("FINAL (CAGED) RESPONSE:")
    print(f"{'='*60}")
    print(result.final_response)

    # Exit code based on verdict
    if result.is_sealed():
        sys.exit(0)
    elif result.verdict == "PARTIAL":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
