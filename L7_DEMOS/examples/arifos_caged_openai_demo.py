# scripts/arifos_caged_openai_demo.py
"""
arifOS Caged OpenAI Demo with PHOENIX SOVEREIGNTY (v36.1Omega)

This script demonstrates Python-sovereign governance for OpenAI GPT models.

PHOENIX SOVEREIGNTY:
    - Real OpenAI via existing adapter (llm_openai.py)
    - Python-sovereign verdict via ApexMeasurement.judge()
    - If Amanah fails, verdict is VOID (no negotiation)
    - Same governance as Claude/SEA-LION (One Law for All Models)

Usage (from repo root):

    # Mock mode (default):
    python -m scripts.arifos_caged_openai_demo --query "Explain quantum computing."

    # Real OpenAI mode:
    OPENAI_API_KEY=sk-... python -m scripts.arifos_caged_openai_demo --query "..." --real

    # Force mock mode explicitly:
    python -m scripts.arifos_caged_openai_demo --mock --query "..."

Author: arifOS Project
License: Apache 2.0
Version: 36.1Omega
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# PHOENIX SOVEREIGNTY: Import real OpenAI adapter (optional)
_REAL_LLM_AVAILABLE = False
_make_llm_generate: Optional[Callable] = None

try:
    from arifos_core.adapters.llm_openai import make_llm_generate as _make_llm_generate
    _REAL_LLM_AVAILABLE = True
except ImportError:
    pass

# PHOENIX SOVEREIGNTY: Import ApexMeasurement for Python-sovereign verdicts
_APEX_AVAILABLE = False
_ApexMeasurement = None
_STANDARDS_PATH = Path(__file__).parent.parent / "arifos_eval" / "apex" / "apex_standards_v36.json"

try:
    from arifos_eval.apex.apex_measurements import ApexMeasurement as _ApexMeasurement
    _APEX_AVAILABLE = True
except ImportError:
    pass


def mock_llm_call(prompt: str) -> str:
    """
    Placeholder for real OpenAI call.
    Returns a simple governed response.
    """
    user_query = "your query"
    if "USER QUERY:" in prompt:
        start = prompt.find("USER QUERY:") + len("USER QUERY:")
        end = prompt.find("\n", start)
        if end > start:
            user_query = prompt[start:end].strip()

    return (
        "MOCK ANSWER (OpenAI):\n"
        f"User asked: {user_query}\n\n"
        "This is a mock response. In a real deployment, GPT would "
        "provide a helpful, governed answer here."
    )


def _build_governed_prompt(user_query: str) -> str:
    """
    Build a governed prompt for the LLM.
    """
    return f"""You are operating under arifOS v36Omega constitutional governance.

USER QUERY: {user_query}

GOVERNANCE CONSTRAINTS:
- Do NOT suggest destructive commands (rm -rf, DROP TABLE, etc.)
- Do NOT output credentials, API keys, or secrets
- Acknowledge uncertainty with Omega_0 = 0.04 (4%)
- Prefer reversible, auditable actions

Please provide a helpful, governed response."""


def _get_llm_generator(use_real: bool, model: str) -> Callable[[str], str]:
    """
    Get LLM generator function based on mode.
    """
    if use_real and _REAL_LLM_AVAILABLE and _make_llm_generate is not None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            print("[WARN] --real specified but OPENAI_API_KEY not set. Falling back to mock.")
            return mock_llm_call
        return _make_llm_generate(api_key=api_key, model=model)

    return mock_llm_call


def _run_apex_judgment(answer: str, high_stakes: bool) -> Dict[str, Any]:
    """
    Run ApexMeasurement.judge() on LLM output.

    PHOENIX SOVEREIGNTY:
    - Python-sovereign verdict via AmanahDetector
    - If Amanah fails, verdict is VOID (no negotiation)
    """
    if not _APEX_AVAILABLE or _ApexMeasurement is None:
        return {
            "verdict": "PARTIAL",
            "G": 0.85,
            "C_dark": 0.10,
            "Psi": 1.05,
            "floors": {"Amanah": True, "Truth": True},
            "note": "ApexMeasurement not available - using stub",
        }

    apex = _ApexMeasurement(str(_STANDARDS_PATH))

    dials = {
        "A": 0.88,  # Ability - GPT is capable
        "P": 0.82,  # Prosociality - governed prompt
        "E": 0.78,  # Energy - standard operation
        "X": 0.88,  # Experience - GPT has training
    }

    output_metrics = {
        "delta_s": 0.08,
        "peace2": 1.03,
        "k_r": 0.95,
        "rasa": 1.0,
        "amanah": 1.0,  # Will be overridden by Python detector
        "entropy": 0.32,
    }

    if high_stakes:
        dials["E"] = 0.68
        output_metrics["entropy"] = 0.42

    result = apex.judge(dials, answer, output_metrics)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="arifOS caged OpenAI demo with PHOENIX SOVEREIGNTY (v36.1Omega)."
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="User query.",
    )
    parser.add_argument(
        "--high-stakes",
        action="store_true",
        help="Mark this query as high-stakes.",
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Use real OpenAI API (requires OPENAI_API_KEY).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock LLM mode.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model ID (default: gpt-4o-mini).",
    )
    args = parser.parse_args()

    user_query = args.query
    high_stakes = args.high_stakes

    use_real = args.real
    if args.mock:
        use_real = False

    llm_mode = "REAL OPENAI" if use_real else "MOCK"

    print("\n" + "=" * 60)
    print("arifOS PHOENIX SOVEREIGNTY - OpenAI Demo (v36.1Omega)")
    print("=" * 60)
    print(f"Query      : {user_query}")
    print(f"High-stakes: {high_stakes}")
    print(f"LLM Mode   : {llm_mode}")
    if use_real:
        print(f"Model      : {args.model}")

    # Step 1: Call LLM
    print(f"\n[LLM CALL ({llm_mode})]")
    llm_generate = _get_llm_generator(use_real, args.model)
    governed_prompt = _build_governed_prompt(user_query)
    answer = llm_generate(governed_prompt)
    print(answer)

    # Step 2: PHOENIX SOVEREIGNTY - Run ApexMeasurement judgment
    print("\n[APEX JUDGMENT - PHOENIX SOVEREIGNTY]")
    apex_result = _run_apex_judgment(answer, high_stakes)

    apex_verdict = apex_result.get("verdict", "PARTIAL")
    apex_G = apex_result.get("G", 0.0)
    apex_Cdark = apex_result.get("C_dark", 0.0)
    apex_Psi = apex_result.get("Psi", 0.0)
    apex_floors = apex_result.get("floors", {})
    amanah_telemetry = apex_result.get("amanah_telemetry")

    print(f"Verdict    : {apex_verdict}")
    print(f"G (Genius) : {apex_G:.3f}")
    print(f"C_dark     : {apex_Cdark:.3f}")
    print(f"Psi        : {apex_Psi:.3f}")
    print(f"Floors     : {apex_floors}")

    if amanah_telemetry:
        print(f"Amanah Safe: {amanah_telemetry.get('is_safe', 'N/A')}")
        if amanah_telemetry.get("violations"):
            print(f"Violations : {amanah_telemetry['violations']}")

    # Step 3: PHOENIX SOVEREIGNTY - If VOID, warn user
    if apex_verdict == "VOID":
        print("\n[PHOENIX SOVEREIGNTY] WARNING: VERDICT VOID - Python veto applied!")
        print("  The LLM output was blocked by Python-sovereign governance.")
        print("  Amanah violations detected - response NOT safe for release.")
        if amanah_telemetry and amanah_telemetry.get("violations"):
            print(f"  Violations: {amanah_telemetry['violations']}")

    print("\n" + "=" * 60)
    print(f"DONE - Verdict: {apex_verdict}")
    print("=" * 60)

    return 1 if apex_verdict == "VOID" else 0


if __name__ == "__main__":
    sys.exit(main())
