"""
arifOS Autoresearch — train.py
==============================
THE ONLY FILE THE AGENT MODIFIES.

This is the experiment file. Unlike prepare.py (which is FIXED),
this file IS editable by the autonomous agent.

Purpose:
- Define the experiment configuration (what to tune)
- Apply changes to arifOS config
- The changes are evaluated by prepare.py

AGENT INSTRUCTIONS:
- Edit THIS file to define experiments
- DO NOT edit prepare.py (it's fixed)
- DO NOT directly modify server.py (work through config files)
- Run: python prepare.py --experiment-id <id> --change "<desc>"

Current baseline config:
- Throughput: 45.5 req/s
- Violation Rate: 8%
- Composite Score: 0.72

TARGET:
- Throughput: >100 req/s
- Violation Rate: <5%
- Composite Score: >0.90

Ditempa Bukan Diberi [ΔΩΨ|888]
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

# =============================================================================
# EXPERIMENT CONFIGURATION
# =============================================================================

@dataclass
class ExperimentConfig:
    """
    Configuration for a single experiment.
    Agent edits these values to optimize arifOS.
    """
    
    # Experiment identity
    experiment_id: str = "exp_001"
    change_description: str = "baseline (no changes)"
    
    # ---- Omega Calibration ----
    # Ω (Omega) = Humility. Must stay in [0.03, 0.05] GOLDILOCKS zone.
    # Dynamic omega based on task complexity.
    omega_simple_tasks: float = 0.03      # Ω for simple tasks (complexity < 0.3)
    omega_medium_tasks: float = 0.04       # Ω for medium tasks (complexity 0.3-0.7)
    omega_complex_tasks: float = 0.05      # Ω for complex tasks (complexity > 0.7)
    
    # ---- Stage Timing Budgets (seconds) ----
    # Total budget: ~6 seconds per request for 100 req/s target
    stage_000_init: float = 0.3           # 5% - Fast anchor
    stage_111_sense: float = 0.6          # 10% - Parse intent
    stage_333_mind: float = 1.2           # 20% - Deep reasoning
    stage_444_rout: float = 0.6           # 10% - Route action
    stage_555_mem: float = 0.6            # 10% - Memory retrieval
    stage_666_heart: float = 0.9          # 15% - Safety critique
    stage_777_ops: float = 0.6            # 10% - Thermo estimate
    stage_888_judge: float = 0.9          # 15% - Final verdict
    stage_999_seal: float = 0.3          # 5% - Seal vault
    
    # ---- W³ Consensus Weights ----
    # W³ = W_theory × W_constitution × W_manifesto >= threshold
    w3_threshold: float = 0.95             # Minimum consensus for SEAL
    w3_entropy_boost: float = 0.05        # Adaptive boost for high-entropy decisions
    
    # ---- Constitutional Floor Thresholds ----
    # Previously optimized values (floor_opt_004)
    f4_clarity_max_delta_s: float = 0.3  # ΔS must be <= this
    f7_omega_min: float = 0.015           # Ω must be >= this
    f7_omega_max: float = 0.20            # Ω must be <= this
    
    # ---- Cache Configuration ----
    cache_ttl_short_term: int = 300       # 5 min - volatile context
    cache_ttl_medium_term: int = 1800     # 30 min - session context
    cache_ttl_long_term: int = 86400      # 24 hr - constitutional context
    
    # ---- Parallel Execution ----
    # Enable parallel execution for non-conflicting stages
    enable_parallel_555_666: bool = True  # [555_MEM || 666_HEART] in parallel
    
    # ---- Early Exit ----
    enable_early_exit: bool = True        # Exit pipeline when entropy plateaus
    early_exit_epsilon: float = 0.01      # Minimum ΔS reduction to continue
    early_exit_min_stages: int = 3        # Minimum stages before early exit
    
    # ---- Tool Routing ----
    # Confidence thresholds for tool selection
    tool_routing_confidence_min: float = 0.85
    
    def to_config_dict(self) -> Dict[str, Any]:
        """Export config as dictionary for JSON serialization."""
        return {
            "experiment_id": self.experiment_id,
            "change_description": self.change_description,
            "omega_calibration": {
                "simple_tasks": self.omega_simple_tasks,
                "medium_tasks": self.omega_medium_tasks,
                "complex_tasks": self.omega_complex_tasks,
            },
            "stage_budgets": {
                "000_INIT": self.stage_000_init,
                "111_SENSE": self.stage_111_sense,
                "333_MIND": self.stage_333_mind,
                "444_ROUT": self.stage_444_rout,
                "555_MEM": self.stage_555_mem,
                "666_HEART": self.stage_666_heart,
                "777_OPS": self.stage_777_ops,
                "888_JUDGE": self.stage_888_judge,
                "999_SEAL": self.stage_999_seal,
            },
            "w3_consensus": {
                "threshold": self.w3_threshold,
                "entropy_boost": self.w3_entropy_boost,
            },
            "floor_thresholds": {
                "F4_CLARITY_MAX_delta_s": self.f4_clarity_max_delta_s,
                "F7_OMEGA_MIN": self.f7_omega_min,
                "F7_OMEGA_MAX": self.f7_omega_max,
            },
            "cache_ttl": {
                "short_term": self.cache_ttl_short_term,
                "medium_term": self.cache_ttl_medium_term,
                "long_term": self.cache_ttl_long_term,
            },
            "parallel_execution": {
                "enable_555_666": self.enable_parallel_555_666,
            },
            "early_exit": {
                "enabled": self.enable_early_exit,
                "epsilon": self.early_exit_epsilon,
                "min_stages": self.early_exit_min_stages,
            },
            "tool_routing": {
                "confidence_min": self.tool_routing_confidence_min,
            },
        }


# =============================================================================
# CONFIGURATION TARGETS
# Where to apply config changes in arifOS
# =============================================================================

ARIFOS_CONFIG_DIR = Path("/root/arifOS/config")
ARIFOS_CONFIG_CURRENT = ARIFOS_CONFIG_DIR / "current_thresholds.json"


def apply_config(config: ExperimentConfig) -> bool:
    """
    Apply experiment configuration to arifOS.
    
    This is called BEFORE running prepare.py.
    The agent edits train.py → calls apply_config → runs prepare.py → measures result.
    
    Returns:
        True if config applied successfully
    """
    print(f"\n{'='*60}")
    print(f"APPLYING CONFIG: {config.experiment_id}")
    print(f"Change: {config.change_description}")
    print(f"{'='*60}")
    
    # Create config payload
    config_payload = config.to_config_dict()
    
    # Save experiment config
    exp_config_path = Path("/root/arifOS/autoresearch/experiments") / f"{config.experiment_id}.json"
    exp_config_path.parent.mkdir(parents=True, exist_ok=True)
    exp_config_path.write_text(json.dumps(config_payload, indent=2))
    print(f"📝 Saved experiment config: {exp_config_path}")
    
    # Update current thresholds (this is what arifOS reads)
    ARIFOS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ARIFOS_CONFIG_CURRENT.write_text(json.dumps(config_payload, indent=2))
    print(f"📝 Updated current thresholds: {ARIFOS_CONFIG_CURRENT}")
    
    print(f"\n✅ Config applied. Run prepare.py to evaluate.\n")
    return True


def revert_config():
    """
    Revert to baseline configuration.
    Called when experiment score degrades.
    """
    baseline = ExperimentConfig(
        experiment_id="baseline",
        change_description="reverted to baseline"
    )
    apply_config(baseline)
    print("🔄 Reverted to baseline configuration\n")


# =============================================================================
# EXPERIMENT DEFINITIONS
# Add your experiments here. Agent will modify these.
# =============================================================================

# Current best known config (from floor_opt_004)
BEST_KNOWN = ExperimentConfig(
    experiment_id="best_known",
    change_description="floor_opt_004: F4=0.3, F7=[0.015,0.20]",
    omega_simple_tasks=0.03,
    omega_medium_tasks=0.04,
    omega_complex_tasks=0.05,
    f4_clarity_max_delta_s=0.3,
    f7_omega_min=0.015,
    f7_omega_max=0.20,
)

# Experiment templates for agent to try
EXPERIMENT_TEMPLATES = {
    "omega_tune_001": ExperimentConfig(
        experiment_id="omega_tune_001",
        change_description="omega_dynamic: simple=0.025, medium=0.04, complex=0.05",
        omega_simple_tasks=0.025,
        omega_medium_tasks=0.04,
        omega_complex_tasks=0.05,
    ),
    "parallel_001": ExperimentConfig(
        experiment_id="parallel_001",
        change_description="parallel_555_666: enabled",
        enable_parallel_555_666=True,
    ),
    "early_exit_001": ExperimentConfig(
        experiment_id="early_exit_001",
        change_description="early_exit: enabled with epsilon=0.01",
        enable_early_exit=True,
        early_exit_epsilon=0.01,
    ),
    "cache_001": ExperimentConfig(
        experiment_id="cache_001",
        change_description="cache_ttl: short=600s, medium=3600s",
        cache_ttl_short_term=600,
        cache_ttl_medium_term=3600,
    ),
    "w3_tight_001": ExperimentConfig(
        experiment_id="w3_tight_001",
        change_description="w3_threshold: 0.97 (tightened)",
        w3_threshold=0.97,
    ),
}


# =============================================================================
# AGENT INTERFACE
# =============================================================================

def run_experiment(
    experiment_id: str,
    change_description: str,
    config_overrides: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Main entry point for running an experiment.
    
    Agent usage:
        from train import run_experiment
        run_experiment(
            experiment_id="exp_042",
            change_description="omega tuned for simple tasks",
            config_overrides={"omega_simple_tasks": 0.025}
        )
    """
    # Build config
    config = ExperimentConfig(
        experiment_id=experiment_id,
        change_description=change_description,
    )
    
    # Apply overrides
    if config_overrides:
        for key, value in config_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print(f"⚠️ Unknown config key: {key}")
    
    # Apply to arifOS
    apply_config(config)
    
    # Return success (prepare.py will handle evaluation)
    return True


# =============================================================================
# CLI for manual runs
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="arifOS train.py — Experiment Config")
    parser.add_argument("--experiment-id", required=True, help="Experiment ID")
    parser.add_argument("--change", required=True, help="Change description")
    parser.add_argument("--apply", action="store_true", help="Apply config and exit")
    parser.add_argument("--revert", action="store_true", help="Revert to baseline")
    parser.add_argument("--print-config", action="store_true", help="Print current config")
    
    args = parser.parse_args()
    
    if args.revert:
        revert_config()
    elif args.print_config:
        config = BEST_KNOWN
        print(json.dumps(config.to_config_dict(), indent=2))
    elif args.apply:
        config = BEST_KNOWN
        config.experiment_id = args.experiment_id
        config.change_description = args.change
        apply_config(config)
    else:
        print("arifOS train.py — Use --help for usage")
        print("\nExample experiments:")
        for name, exp in EXPERIMENT_TEMPLATES.items():
            print(f"  {name}: {exp.change_description}")
