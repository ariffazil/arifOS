#!/usr/bin/env python3
"""
sealion_full_suite_v45.py - Comprehensive Live Evaluation Harness for SEA-LION v4 on arifOS v45Ω

COMPREHENSIVE TEST COVERAGE:
- Lane routing (PHATIC/SOFT/HARD/REFUSE)
- Constitutional floors (F1-F9)
- Ψ lane-scoped enforcement
- REFUSE short-circuit validation
- Identity truth lock
- Claim detection
- Verdict rendering
- Memory gating (multi-turn)
- Ledger integrity
- W@W federation (if wired)
- API routes (if runnable)

USAGE:
    # Smoke test (5 quick cases)
    python scripts/sealion_full_suite_v45.py --smoke

    # Core suite (all single-turn: lanes, floors, identity, refuse)
    python scripts/sealion_full_suite_v45.py --suite core

    # Memory suite (10 multi-turn scenarios)
    python scripts/sealion_full_suite_v45.py --suite memory

    # All suites
    python scripts/sealion_full_suite_v45.py --all

    # With custom model/provider
    python scripts/sealion_full_suite_v45.py --model gpt-4 --provider openai --smoke

    # Limit cases and fail fast
    python scripts/sealion_full_suite_v45.py --suite core --max-cases 10 --fail-fast

ENVIRONMENT VARIABLES (required):
    ARIF_LLM_API_KEY     - API key for LLM provider
    ARIF_LLM_MODEL       - Model identifier (optional, has default)
    ARIF_LLM_PROVIDER    - Provider (openai, anthropic, etc., optional)
    ARIF_LLM_API_BASE    - API base URL for custom endpoints (optional)

DITEMPA, BUKAN DIBERI
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Windows UTF-8 fix
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# arifOS imports
from arifos_core.integration.connectors.litellm_gateway import make_llm_generate, LiteLLMConfig
from arifos_core.integration.sealion_suite.test_packs import get_test_pack
from arifos_core.integration.sealion_suite.evaluator import (
    run_test_suite,
    create_suite_skip_result,
    detect_memory_capability,
    detect_ledger_capability,
    detect_api_capability,
    detect_waw_capability,
)
from arifos_core.integration.sealion_suite.artifact_writer import (
    create_run_directory,
    write_all_artifacts,
)


def print_banner():
    """Print startup banner."""
    print("\n" + "=" * 80)
    print(" " * 20 + "🦁 SEA-LION v4 Full Evaluation Suite 🦁")
    print(" " * 25 + "arifOS v45Ω Patch B.1")
    print("=" * 80)
    print()


def validate_environment() -> Dict[str, str]:
    """
    Validate required environment variables.

    Returns:
        Dict of relevant env vars

    Raises:
        ValueError if API key is missing
    """
    # Check API keys in priority order
    api_key_source = None
    api_key = os.getenv("ARIF_LLM_API_KEY")
    if api_key:
        api_key_source = "ARIF_LLM_API_KEY"
    else:
        api_key = os.getenv("SEALION_API_KEY")
        if api_key:
            api_key_source = "SEALION_API_KEY"
        else:
            api_key = os.getenv("LLM_API_KEY")
            if api_key:
                api_key_source = "LLM_API_KEY"
            else:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    api_key_source = "OPENAI_API_KEY"

    if not api_key:
        raise ValueError(
            "❌ API Key not found!\n\n"
            "Set one of these environment variables:\n"
            "  - ARIF_LLM_API_KEY (universal)\n"
            "  - SEALION_API_KEY (SEA-LION specific)\n"
            "  - LLM_API_KEY (generic)\n"
            "  - OPENAI_API_KEY (OpenAI specific)\n\n"
            "Example (Windows PowerShell):\n"
            "  $env:SEALION_API_KEY='your-api-key'\n\n"
            "Example (Linux/Mac):\n"
            "  export SEALION_API_KEY='your-api-key'\n"
        )

    env_vars = {
        "api_key_source": api_key_source,  # Track which key was used
        "ARIF_LLM_API_KEY": "***hidden***",
        "ARIF_LLM_MODEL": os.getenv("ARIF_LLM_MODEL", "not set"),
        "ARIF_LLM_PROVIDER": os.getenv("ARIF_LLM_PROVIDER", "not set"),
        "ARIF_LLM_API_BASE": os.getenv("ARIF_LLM_API_BASE", "not set"),
    }

    return env_vars


def run_smoke_test(args) -> int:
    """Run smoke test (5 quick cases)."""
    print("🚀 SMOKE TEST (5 quick validation cases)\n")

    test_pack = get_test_pack("smoke")
    print(f"📦 Test pack loaded: {len(test_pack)} cases\n")

    # Create LLM generate function
    try:
        llm_config = LiteLLMConfig(
            model=args.model,
            provider=args.provider,
            temperature=0.7,
            max_tokens=2048,
        )
        llm_generate = make_llm_generate(llm_config)
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return 1

    # Run tests
    run_dir = create_run_directory()
    print(f"📁 Run directory: {run_dir}\n")

    print("🏃 Running smoke tests...\n")
    results = run_test_suite(
        test_cases=test_pack,
        llm_generate=llm_generate,
        no_ledger=args.no_ledger,
        save_responses=args.save_responses,
        max_cases=args.max_cases,
        fail_fast=args.fail_fast,
    )

    # Write artifacts
    print(f"\n📝 Writing artifacts...\n")
    env_vars = validate_environment()
    summary = write_all_artifacts(
        run_dir=run_dir,
        results=results,
        suite_name="smoke",
        model=args.model or "unknown",
        provider=args.provider or "unknown",
        total_cases=len(test_pack),
        env_vars=env_vars,
    )

    # Print summary
    print_summary_table(summary, results)

    return 0 if all(r.passed or r.skipped for r in results) else 1


def run_suite(suite_name: str, args) -> int:
    """Run named test suite with capability detection."""
    print(f"🚀 SUITE: {suite_name.upper()}\n")

    # Capability detection for special suites
    if suite_name == "memory":
        is_available, skip_reason = detect_memory_capability()
        if not is_available:
            print(f"⏭️  SKIPPING {suite_name.upper()} suite: {skip_reason}\n")
            results = create_suite_skip_result(suite_name, skip_reason)
            run_dir = create_run_directory()
            print(f"📁 Run directory: {run_dir}\n")
            env_vars = validate_environment()
            summary = write_all_artifacts(
                run_dir=run_dir,
                results=results,
                suite_name=suite_name,
                model=args.model or "unknown",
                provider=args.provider or "unknown",
                total_cases=1,
                env_vars=env_vars,
            )
            print_summary_table(summary, results)
            return 0  # SKIP is not a failure

    elif suite_name == "ledger":
        is_available, skip_reason = detect_ledger_capability()
        if not is_available:
            print(f"⏭️  SKIPPING {suite_name.upper()} suite: {skip_reason}\n")
            results = create_suite_skip_result(suite_name, skip_reason)
            run_dir = create_run_directory()
            env_vars = validate_environment()
            summary = write_all_artifacts(
                run_dir=run_dir,
                results=results,
                suite_name=suite_name,
                model=args.model or "unknown",
                provider=args.provider or "unknown",
                total_cases=1,
                env_vars=env_vars,
            )
            print_summary_table(summary, results)
            return 0

    elif suite_name == "api":
        is_available, skip_reason = detect_api_capability()
        if not is_available:
            print(f"⏭️  SKIPPING {suite_name.upper()} suite: {skip_reason}\n")
            results = create_suite_skip_result(suite_name, skip_reason)
            run_dir = create_run_directory()
            env_vars = validate_environment()
            summary = write_all_artifacts(
                run_dir=run_dir,
                results=results,
                suite_name=suite_name,
                model=args.model or "unknown",
                provider=args.provider or "unknown",
                total_cases=1,
                env_vars=env_vars,
            )
            print_summary_table(summary, results)
            return 0

    elif suite_name == "waw":
        is_available, skip_reason = detect_waw_capability()
        if not is_available:
            print(f"⏭️  SKIPPING {suite_name.upper()} suite: {skip_reason}\n")
            results = create_suite_skip_result(suite_name, skip_reason)
            run_dir = create_run_directory()
            env_vars = validate_environment()
            summary = write_all_artifacts(
                run_dir=run_dir,
                results=results,
                suite_name=suite_name,
                model=args.model or "unknown",
                provider=args.provider or "unknown",
                total_cases=1,
                env_vars=env_vars,
            )
            print_summary_table(summary, results)
            return 0

    # Load test pack (if capability check passed or not applicable)
    test_pack = get_test_pack(suite_name)
    if not test_pack and suite_name not in ["ledger", "api", "waw", "memory"]:
        print(f"❌ Unknown suite: {suite_name}")
        print(f"Available suites: smoke, core, memory, ledger, api, waw, all")
        return 1

    print(f"📦 Test pack loaded: {len(test_pack)} cases\n")

    # Create LLM generate function
    try:
        llm_config = LiteLLMConfig(
            model=args.model,
            provider=args.provider,
            temperature=0.7,
            max_tokens=2048,
        )
        llm_generate = make_llm_generate(llm_config)
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return 1

    # Run tests
    run_dir = create_run_directory()
    print(f"📁 Run directory: {run_dir}\n")

    print(f"🏃 Running {suite_name} suite...\n")
    results = run_test_suite(
        test_cases=test_pack,
        llm_generate=llm_generate,
        no_ledger=args.no_ledger,
        save_responses=args.save_responses,
        max_cases=args.max_cases,
        fail_fast=args.fail_fast,
    )

    # Write artifacts
    print(f"\n📝 Writing artifacts...\n")
    env_vars = validate_environment()
    summary = write_all_artifacts(
        run_dir=run_dir,
        results=results,
        suite_name=suite_name,
        model=args.model or "unknown",
        provider=args.provider or "unknown",
        total_cases=len(test_pack),
        env_vars=env_vars,
    )

    # Print summary
    print_summary_table(summary, results)

    return 0 if all(r.passed or r.skipped for r in results) else 1


def run_all_suites(args) -> int:
    """Run all test suites sequentially."""
    print("🚀 RUNNING ALL SUITES\n")

    suites = ["core", "memory"]  # Start with these, add more as implemented

    all_results = []
    all_summaries = []

    for suite_name in suites:
        print(f"\n{'='*80}")
        print(f"  SUITE: {suite_name.upper()}")
        print(f"{'='*80}\n")

        test_pack = get_test_pack(suite_name)
        print(f"📦 Test pack loaded: {len(test_pack)} cases\n")

        # Create LLM generate function
        try:
            llm_config = LiteLLMConfig(
                model=args.model,
                provider=args.provider,
                temperature=0.7,
                max_tokens=2048,
            )
            llm_generate = make_llm_generate(llm_config)
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            return 1

        # Run tests
        print(f"🏃 Running {suite_name} suite...\n")
        results = run_test_suite(
            test_cases=test_pack,
            llm_generate=llm_generate,
            no_ledger=args.no_ledger,
            save_responses=args.save_responses,
            max_cases=args.max_cases,
            fail_fast=args.fail_fast,
        )

        all_results.extend(results)

        # Quick summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        print(f"\n  {suite_name.upper()}: {passed}/{total} passed\n")

        if args.fail_fast and passed < total:
            print("⚠️  Stopping --all due to failures in this suite")
            break

    # Write combined artifacts
    run_dir = create_run_directory()
    print(f"\n📁 Combined run directory: {run_dir}\n")

    env_vars = validate_environment()
    summary = write_all_artifacts(
        run_dir=run_dir,
        results=all_results,
        suite_name="all_suites",
        model=args.model or "unknown",
        provider=args.provider or "unknown",
        total_cases=len(all_results),
        env_vars=env_vars,
    )

    # Print final summary
    print("\n" + "=" * 80)
    print("  COMBINED RESULTS")
    print("=" * 80 + "\n")
    print_summary_table(summary, all_results)

    return 0 if all(r.passed or r.skipped for r in all_results) else 1


def print_summary_table(summary: Dict[str, Any], results):
    """Print summary table to console."""
    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80 + "\n")

    totals = summary["totals"]
    print(f"Total Cases:  {totals['total']}")
    print(f"Passed:       {totals['passed']} ✅")
    print(f"Failed:       {totals['failed']} ❌")
    print(f"Errors:       {totals['errors']} 🔴")
    print(f"Skipped:      {totals['skipped']} ⏭️")
    print(f"Pass Rate:    {totals['pass_rate']}")

    print(f"\n{'─'*80}\n")

    # Verdict counts
    print("Verdicts:")
    for verdict, count in summary["verdict_distribution"].items():
        print(f"  {verdict}: {count}")

    print(f"\n{'─'*80}\n")

    # Lane counts
    print("Lanes:")
    for lane, count in summary["lane_distribution"].items():
        print(f"  {lane}: {count}")

    print(f"\n{'─'*80}\n")

    # LLM calls
    llm = summary["llm_calls"]
    print(f"LLM Calls:")
    print(f"  Called:     {llm['called']}")
    print(f"  Not Called: {llm['not_called']} (REFUSE short-circuit / templates)")

    print(f"\n{'─'*80}\n")

    # Performance
    perf = summary["performance"]
    print(f"Performance:")
    print(f"  Avg execution time: {perf['avg_execution_time_ms']:.0f}ms")
    print(f"  Total time:         {perf['total_execution_time_ms']/1000:.1f}s")

    # Show first few failures
    failures = [r for r in results if not r.passed and not r.skipped]
    if failures:
        print(f"\n{'─'*80}\n")
        print(f"First {min(3, len(failures))} Failures:\n")
        for r in failures[:3]:
            print(f"  [{r.test_id}] {r.test_name}")
            for failure in r.validation_failures[:2]:
                print(f"    ⚠️  {failure}")
            print()

    print("=" * 80 + "\n")


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="SEA-LION v4 Full Evaluation Suite for arifOS v45Ω",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--smoke", action="store_true", help="Run smoke test (5 cases)")
    mode_group.add_argument(
        "--suite",
        type=str,
        choices=["core", "memory", "ledger", "api", "waw"],
        help="Run specific test suite",
    )
    mode_group.add_argument("--all", action="store_true", help="Run all suites")

    # Model configuration
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("ARIF_LLM_MODEL", "Qwen-SEA-LION-v4-32B-IT"),
        help="Model identifier (default: Qwen-SEA-LION-v4-32B-IT or ARIF_LLM_MODEL env var)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=os.getenv("ARIF_LLM_PROVIDER", "sealion"),
        help="Provider (sealion, openai, anthropic, etc., default: sealion)",
    )

    # Execution control
    parser.add_argument(
        "--max-cases", type=int, default=None, help="Maximum cases to run (None = all)"
    )
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first failure"
    )
    parser.add_argument(
        "--no-ledger", action="store_true", help="Disable ledger writing"
    )
    parser.add_argument(
        "--save-responses",
        type=str,
        choices=["full", "snippets", "none"],
        default="snippets",
        help="How to save LLM responses (default: snippets)",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Validate environment
    try:
        env_vars = validate_environment()
        print("✅ Environment validated")
        print(f"   Model: {args.model}")
        print(f"   Provider: {args.provider}")
        print()
    except ValueError as e:
        print(e)
        return 1

    # Run appropriate mode
    try:
        if args.smoke:
            return run_smoke_test(args)
        elif args.suite:
            return run_suite(args.suite, args)
        elif args.all:
            return run_all_suites(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
