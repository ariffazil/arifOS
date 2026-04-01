#!/usr/bin/env python3
"""
arifOS Autoresearch — run_experiment.py
=======================================
CLI to run a single experiment end-to-end.

Usage:
    python run_experiment.py                              # Interactive
    python run_experiment.py --experiment exp_001 --change "omega tune" --apply
    python run_experiment.py --baseline                    # Run baseline
    python run_experiment.py --list                        # List experiments
    python run_experiment.py --validate                    # Validate setup

Ditempa Bukan Diberi [ΔΩΨ|888]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# =============================================================================
# SETUP
# =============================================================================

AUTORESEARCH_DIR = Path(__file__).parent
sys.path.insert(0, str(AUTORESEARCH_DIR))

from train import ExperimentConfig, EXPERIMENT_TEMPLATES, apply_config
from arifos_optimizer import ArifOSOptimizer


# =============================================================================
# VALIDATION
# =============================================================================

def validate_setup():
    """Validate that all required files and dependencies exist."""
    errors = []
    warnings = []
    
    required_files = [
        "train.py",
        "prepare.py",
        "results.tsv",
        "observations.md",
        "arifos_optimizer.py",
        "program.md",
    ]
    
    for fname in required_files:
        path = AUTORESEARCH_DIR / fname
        if not path.exists():
            errors.append(f"Missing: {fname}")
    
    # Check metrics/benchmark.py
    benchmark_path = AUTORESEARCH_DIR / "metrics" / "benchmark.py"
    if not benchmark_path.exists():
        errors.append(f"Missing: metrics/benchmark.py")
    
    # Check arifOS structure
    arifOS_path = AUTORESEARCH_DIR.parent
    if not arifOS_path.exists():
        errors.append(f"arifOS parent not found: {arifOS_path}")
    
    # Print results
    print("=" * 60)
    print("AUTORESEARCH SETUP VALIDATION")
    print("=" * 60)
    
    if not errors and not warnings:
        print("✅ All checks passed")
        print("=" * 60)
        return True
    
    if errors:
        print("❌ ERRORS:")
        for e in errors:
            print(f"  - {e}")
    
    if warnings:
        print("⚠️  WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
    
    print("=" * 60)
    return len(errors) == 0


# =============================================================================
# EXPERIMENTS
# =============================================================================

def list_experiments():
    """List available experiment templates."""
    print("\nAvailable experiments from train.py:")
    print("-" * 60)
    
    for name, exp in EXPERIMENT_TEMPLATES.items():
        print(f"\n{name}:")
        print(f"  ID: {exp.experiment_id}")
        print(f"  Change: {exp.change_description}")
        print(f"  Config:")
        for key in ["omega_simple_tasks", "omega_medium_tasks", "omega_complex_tasks"]:
            val = getattr(exp, key, None)
            if val is not None:
                print(f"    {key}: {val}")
    
    print("\n" + "=" * 60)
    print(f"\nAlso: --baseline (revert to baseline)")
    print(f"And:  --custom for interactive custom experiment\n")


def run_baseline():
    """Run baseline (no changes) to establish control."""
    print("\n" + "=" * 60)
    print("RUNNING BASELINE EXPERIMENT")
    print("=" * 60)
    
    config = ExperimentConfig(
        experiment_id="baseline_001",
        change_description="baseline (no changes)"
    )
    apply_config(config)
    
    # Run prepare.py
    result = subprocess.run([
        sys.executable, "prepare.py",
        "--experiment-id", "baseline_001",
        "--change", "baseline (no changes)",
        "--duration", "300"
    ], cwd=AUTORESEARCH_DIR)
    
    return result.returncode == 0


def run_custom(experiment_id: str, change: str, config_overrides: dict):
    """Run a custom experiment."""
    print("\n" + "=" * 60)
    print(f"RUNNING CUSTOM EXPERIMENT: {experiment_id}")
    print(f"Change: {change}")
    print("=" * 60)
    
    config = ExperimentConfig(
        experiment_id=experiment_id,
        change_description=change,
        **config_overrides
    )
    apply_config(config)
    
    # Run prepare.py
    result = subprocess.run([
        sys.executable, "prepare.py",
        "--experiment-id", experiment_id,
        "--change", change,
        "--duration", "300"
    ], cwd=AUTORESEARCH_DIR)
    
    return result.returncode == 0


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="arifOS Autoresearch Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_experiment.py --validate           # Check setup
  python run_experiment.py --list               # Show available experiments
  python run_experiment.py --baseline            # Run baseline
  python run_experiment.py --experiment exp_001 --change "omega tuning" --apply
  python run_experiment.py --overnight           # Run optimizer overnight mode
        """
    )
    
    parser.add_argument("--validate", action="store_true", help="Validate setup")
    parser.add_argument("--list", action="store_true", help="List available experiments")
    parser.add_argument("--baseline", action="store_true", help="Run baseline experiment")
    parser.add_argument("--overnight", action="store_true", help="Run overnight optimization")
    parser.add_argument("--status", action="store_true", help="Show status")
    
    parser.add_argument("--experiment", type=str, help="Experiment ID")
    parser.add_argument("--change", type=str, help="Change description")
    parser.add_argument("--apply", action="store_true", help="Apply config and run")
    
    parser.add_argument("--duration", type=int, default=300, help="Experiment duration (seconds)")
    
    args = parser.parse_args()
    
    # No args = interactive help
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nRun --validate first to check setup.")
        return 0
    
    # Validate
    if args.validate:
        success = validate_setup()
        return 0 if success else 1
    
    # List experiments
    if args.list:
        list_experiments()
        return 0
    
    # Status
    if args.status:
        optimizer = ArifOSOptimizer()
        optimizer.print_status()
        return 0
    
    # Baseline
    if args.baseline:
        success = run_baseline()
        return 0 if success else 1
    
    # Overnight mode
    if args.overnight:
        optimizer = ArifOSOptimizer()
        optimizer.run_overnight(experiment_duration=args.duration)
        return 0
    
    # Custom experiment
    if args.experiment and args.change and args.apply:
        success = run_custom(args.experiment, args.change, {})
        return 0 if success else 1
    
    # Missing args
    print("❌ Invalid combination. Use --help for usage.")
    return 1


if __name__ == "__main__":
    exit(main())
