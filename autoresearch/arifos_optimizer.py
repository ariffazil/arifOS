"""
arifOS Autoresearch — arifos_optimizer.py
==========================================
The autonomous optimization loop.

Orchestrates:
1. Read results.tsv to see what's been tried
2. Pick next experiment based on observations
3. Apply config via train.py
4. Run evaluation via prepare.py
5. Score result, keep or revert
6. Report to VAULT999

Usage:
    python arifos_optimizer.py --runs 10 --overnight
    python arifos_optimizer.py --experiment exp_042
    python arifos_optimizer.py --status

Authority: 888_JUDGE
Ditempa Bukan Diberi [ΔΩΨ]
"""

import asyncio
import json
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Local imports
from train import ExperimentConfig, apply_config, revert_config, BEST_KNOWN
from prepare import ConstitutionalEvaluator, TARGET_SCORE


# =============================================================================
# CONFIGURATION
# =============================================================================

AUTORESEARCH_DIR = Path(__file__).parent
RESULTS_TSV = AUTORESEARCH_DIR / "results.tsv"
OBSERVATIONS_MD = AUTORESEARCH_DIR / "observations.md"
EXPERIMENTS_DIR = AUTORESEARCH_DIR / "experiments"
CONFIG_CURRENT = AUTORESEARCH_DIR.parent / "config" / "current_thresholds.json"

BASELINE_SCORE = 0.72
TARGET_THROUGHPUT = 100.0
TARGET_VIOLATION_RATE = 0.05
MAX_CONSECUTIVE_FAILURES = 3


# =============================================================================
# EXPERIMENT ORCHESTRATOR
# =============================================================================

class ArifOSOptimizer:
    """
    Main optimization loop for arifOS autoresearch.
    
    Reads history, picks next experiment, runs evaluation,
    decides to keep or revert.
    """
    
    def __init__(self):
        self.evaluator = ConstitutionalEvaluator()
        self.experiments_run = 0
        self.experiments_kept = 0
        self.experiments_discarded = 0
        self.consecutive_failures = 0
        self.best_score = BASELINE_SCORE
        self.best_experiment_id = "baseline"
        self.run_history: List[Dict] = []
    
    # -------------------------------------------------------------------------
    # History Analysis
    # -------------------------------------------------------------------------
    
    def load_history(self) -> List[Dict]:
        """Load experiment history from results.tsv."""
        if not RESULTS_TSV.exists():
            return []
        
        history = []
        lines = RESULTS_TSV.read_text().strip().split("\n")
        
        if len(lines) <= 1:
            return []
        
        # Skip header
        for line in lines[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 11:
                history.append({
                    "timestamp": parts[0],
                    "experiment_id": parts[1],
                    "change_description": parts[2],
                    "throughput": float(parts[3]),
                    "violation_rate": float(parts[4]),
                    "avg_omega": float(parts[5]),
                    "omega_in_range_pct": float(parts[6]),
                    "avg_W_cube": float(parts[7]),
                    "composite_score": float(parts[8]),
                    "kept": parts[9].lower() == "true",
                    "notes": parts[10],
                })
        
        self.run_history = history
        return history
    
    def get_next_experiment_id(self) -> str:
        """Generate next experiment ID."""
        history = self.load_history()
        next_num = len(history) + 1
        return f"exp_{next_num:03d}"
    
    def suggest_next_experiment(self) -> Tuple[str, Dict]:
        """
        Suggest next experiment based on history analysis.
        
        Returns:
            (experiment_id, config_overrides)
        """
        history = self.load_history()
        
        # Track what's been tried
        tried_variants = set()
        for entry in history:
            tried_variants.add(entry["change_description"])
        
        # Strategy: explore around what worked
        kept_experiments = [e for e in history if e["kept"]]
        
        if not kept_experiments:
            # Nothing kept yet — try the best known config
            return "exp_next", {
                "omega_simple_tasks": 0.025,
                "omega_medium_tasks": 0.04,
                "omega_complex_tasks": 0.05,
            }
        
        # Find the best kept experiment
        best_kept = max(kept_experiments, key=lambda x: x["composite_score"])
        
        # Variation strategies
        variations = [
            ("throughput_focus", {"stage_333_mind": 1.0, "stage_888_judge": 0.8}),
            ("parallel_max", {"enable_parallel_555_666": True}),
            ("early_exit_aggressive", {"enable_early_exit": True, "early_exit_epsilon": 0.005}),
            ("cache_aggressive", {"cache_ttl_short_term": 600, "cache_ttl_medium_term": 3600}),
            ("w3_tight", {"w3_threshold": 0.97}),
            ("omega_humble", {"omega_simple_tasks": 0.035, "omega_medium_tasks": 0.045}),
        ]
        
        # Pick a variation not yet tried
        random.shuffle(variations)
        for name, overrides in variations:
            desc = f"variation: {name}"
            if desc not in tried_variants:
                return f"exp_next", overrides
        
        # If all variations tried, pick the best kept and try to refine it
        return "exp_next", {
            "omega_simple_tasks": 0.03,
            "omega_medium_tasks": 0.04,
        }
    
    # -------------------------------------------------------------------------
    # Experiment Execution
    # -------------------------------------------------------------------------
    
    def run_single_experiment(
        self,
        experiment_id: str,
        change_description: str,
        config_overrides: Optional[Dict] = None,
        duration_seconds: int = 300
    ) -> Dict:
        """
        Run a single experiment.
        
        1. Build config with overrides
        2. Apply via train.py
        3. Evaluate via prepare.py
        4. Decide keep/revert
        """
        print(f"\n{'#'*70}")
        print(f"# RUNNING EXPERIMENT: {experiment_id}")
        print(f"# CHANGE: {change_description}")
        print(f"{'#'*70}")
        
        # Build config
        config = ExperimentConfig(
            experiment_id=experiment_id,
            change_description=change_description,
        )
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Apply config
        apply_config(config)
        
        # Run evaluation
        result = asyncio.run(self.evaluator.evaluate(
            experiment_id=experiment_id,
            change_description=change_description,
            duration_seconds=duration_seconds,
            concurrency=10
        ))
        
        # Track stats
        self.experiments_run += 1
        
        if result.kept:
            self.experiments_kept += 1
            self.consecutive_failures = 0
            if result.composite_score > self.best_score:
                self.best_score = result.composite_score
                self.best_experiment_id = experiment_id
                print(f"🆕 NEW BEST: {self.best_score:.4f}")
        else:
            self.experiments_discarded += 1
            self.consecutive_failures += 1
            print(f"❌ Experiment discarded. Reverting...")
            revert_config()
        
        return {
            "experiment_id": experiment_id,
            "change_description": change_description,
            "score": result.composite_score,
            "kept": result.kept,
        }
    
    def run_overnight(
        self,
        max_experiments: int = 20,
        experiment_duration: int = 300,
        sleep_between: int = 10
    ):
        """
        Run experiments overnight (or until max_experiments reached).
        
        5 min per experiment × 20 = ~100 min of experiments
        With 10s between = ~3.5 hours total
        """
        print(f"\n🌙 OVERNIGHT MODE")
        print(f"Max experiments: {max_experiments}")
        print(f"Duration per experiment: {experiment_duration}s ({experiment_duration/60:.1f} min)")
        print(f"Total estimated time: {(experiment_duration + sleep_between) * max_experiments / 60:.1f} min")
        print()
        
        target_end = datetime.now() + timedelta(hours=8)  # 8 hour overnight window
        
        for i in range(max_experiments):
            # Check time budget
            if datetime.now() >= target_end:
                print(f"\n⏰ Time budget exhausted. Stopping.")
                break
            
            # Check consecutive failures
            if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"\n⚠️ {MAX_CONSECUTIVE_FAILURES} consecutive failures. Stopping — system may be at local optimum.")
                break
            
            # Suggest next experiment
            exp_id = self.get_next_experiment_id()
            change, overrides = self.suggest_next_experiment()
            change = f"auto: {change}"
            
            # Run it
            result = self.run_single_experiment(
                experiment_id=exp_id,
                change_description=change,
                config_overrides=overrides,
                duration_seconds=experiment_duration
            )
            
            # Print progress
            print(f"\n📊 Progress: {i+1}/{max_experiments} | Kept: {self.experiments_kept} | Discarded: {self.experiments_discarded} | Best: {self.best_score:.4f} ({self.best_experiment_id})")
            
            # Sleep between experiments
            if i < max_experiments - 1:
                print(f"💤 Sleeping {sleep_between}s before next experiment...")
                time.sleep(sleep_between)
        
        self.print_summary()
    
    def print_summary(self):
        """Print final summary."""
        print(f"\n{'='*70}")
        print(f"OVERNIGHT SUMMARY")
        print(f"{'='*70}")
        print(f"Experiments run: {self.experiments_run}")
        print(f"Kept: {self.experiments_kept}")
        print(f"Discarded: {self.experiments_discarded}")
        print(f"Best score: {self.best_score:.4f} ({self.best_experiment_id})")
        print()
        
        # Load history for detailed summary
        history = self.load_history()
        if history:
            print("Top 5 experiments:")
            sorted_history = sorted(history, key=lambda x: x["composite_score"], reverse=True)
            for i, exp in enumerate(sorted_history[:5], 1):
                print(f"  {i}. {exp['experiment_id']}: {exp['composite_score']:.4f} ({exp['change_description'][:50]})")
        
        print(f"\n{'='*70}")
        
        # Check if target achieved
        if self.best_score >= TARGET_SCORE:
            print(f"🎉 TARGET ACHIEVED: {self.best_score:.4f} >= {TARGET_SCORE}")
            print(f"✅ Ready for 888_JUDGE review for production promotion")
        else:
            print(f"📈 Target not yet achieved: {self.best_score:.4f} < {TARGET_SCORE}")
            print(f"💡建议: More experiments, or try different variation strategies")
        
        print(f"{'='*70}\n")
    
    def print_status(self):
        """Print current status without running experiments."""
        history = self.load_history()
        
        print(f"\n{'='*70}")
        print(f"AUTORESEARCH STATUS")
        print(f"{'='*70}")
        print(f"Experiments in history: {len(history)}")
        
        if history:
            kept = sum(1 for e in history if e["kept"])
            discarded = len(history) - kept
            best = max(history, key=lambda x: x["composite_score"])
            
            print(f"Kept: {kept} | Discarded: {discarded}")
            print(f"Best: {best['experiment_id']} = {best['composite_score']:.4f}")
            print(f"  Change: {best['change_description']}")
            print()
            print("Recent experiments:")
            for exp in history[-5:]:
                status = "✅" if exp["kept"] else "❌"
                print(f"  {status} {exp['experiment_id']}: {exp['composite_score']:.4f} — {exp['change_description'][:40]}")
        else:
            print(f"No experiments run yet.")
            print(f"Run: python arifos_optimizer.py --runs 5")
        
        print(f"{'='*70}\n")


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="arifOS Autoresearch Optimizer")
    parser.add_argument("--status", action="store_true", help="Show status and exit")
    parser.add_argument("--runs", type=int, default=0, help="Number of experiments to run")
    parser.add_argument("--overnight", action="store_true", help="Run overnight mode (up to 20 experiments)")
    parser.add_argument("--experiment", type=str, help="Run a specific experiment")
    parser.add_argument("--change", type=str, help="Change description for specific experiment")
    parser.add_argument("--duration", type=int, default=300, help="Experiment duration in seconds (default: 300)")
    
    args = parser.parse_args()
    
    optimizer = ArifOSOptimizer()
    
    if args.status:
        optimizer.print_status()
        return 0
    
    if args.experiment:
        # Run specific experiment
        change = args.change or f"manual: {args.experiment}"
        overrides = {}
        optimizer.run_single_experiment(
            experiment_id=args.experiment,
            change_description=change,
            config_overrides=overrides,
            duration_seconds=args.duration
        )
        return 0
    
    if args.overnight:
        # Overnight mode
        optimizer.run_overnight(
            max_experiments=20,
            experiment_duration=args.duration
        )
        return 0
    
    if args.runs > 0:
        # Fixed number of runs
        for i in range(args.runs):
            exp_id = optimizer.get_next_experiment_id()
            change, overrides = optimizer.suggest_next_experiment()
            optimizer.run_single_experiment(
                experiment_id=exp_id,
                change_description=f"auto: {change}",
                config_overrides=overrides,
                duration_seconds=args.duration
            )
            time.sleep(5)
        optimizer.print_summary()
        return 0
    
    # Default: show status
    optimizer.print_status()
    print("Usage:")
    print("  python arifos_optimizer.py --status")
    print("  python arifos_optimizer.py --runs 5 --duration 300")
    print("  python arifos_optimizer.py --overnight")
    print("  python arifos_optimizer.py --experiment exp_042 --change 'omega tuning'")
    return 0


if __name__ == "__main__":
    exit(main())
