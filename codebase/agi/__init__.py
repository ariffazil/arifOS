"""
AGI (Mind/Δ) - Unified Neural Engine

v53.4.0 - Hardened v52 + v53 + Critical Gaps P1-P3

One Engine: engine.py (AGIEngine)
One Kernel: kernel.py (AGINeuralCore)

Stages:
    111 SENSE  → Parse facts, detect intent, hierarchical encoding (F12, F10)
    222 THINK  → Generate hypotheses with precision weighting (F2, F13)
    333 FORGE  → Converge, active inference, action selection (F7, F4)

Supporting Modules:
    hardening.py    - Constitutional safety (F9, F12)
    metrics.py      - Thermodynamic dashboard (Ω₀, ΔS)
    parallel.py     - Concurrent hypothesis matrix
    evidence.py     - Live fact injection
    precision.py    - v53.4.0 Kalman-style precision weighting (Gap P1)
    hierarchy.py    - v53.4.0 5-level cortical encoding (Gap P2)
    action.py       - v53.4.0 EFE minimization action selection (Gap P3)
    trinity_sync.py - 333 AGI↔ASI convergence with 6 paradoxes
    stages/         - Legacy stage executors
    agi_components.py - v53 NeuralSenseEngine, DeepThinkEngine, CognitiveForge

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

# Unified Engine (v52+v53+v54) — CANONICAL PIPELINE
from .engine import AGIEngine, AGIResult, execute_agi, get_agi_engine, cleanup_expired_sessions

# Unified Kernel (MCP interface)
from .kernel import AGINeuralCore, get_agi_core

# Backward compat alias
AGIKernel = AGINeuralCore

# Supporting modules (direct access if needed)
from .hardening import run_pre_checks, run_post_checks, HardeningResult, RiskLevel
from .metrics import ThermodynamicDashboard, get_dashboard

# v53.4.0: Critical Gap modules (now wired into engine.py pipeline)
from .precision import PrecisionEstimate, PrecisionWeighter, estimate_precision, update_belief_with_precision, cosine_similarity
from .hierarchy import HierarchyLevel, HierarchicalBelief, HierarchicalEncoder, encode_hierarchically, get_cumulative_delta_s
from .action import ActionType, ActionPolicy, BeliefState, ExpectedFreeEnergyCalculator, MotorOutput, compute_action_policy, execute_action

# v53.4.0: Trinity Sync (333 AGI↔ASI convergence)
from .trinity_sync import TrinitySync, ConvergenceResult, trinity_sync, PARADOXES

# v53.4.0: Hardened engine (standalone, not in live pipeline)
from .engine_hardened import AGIEngineHardened, execute_agi_hardened

__version__ = "v53.4.0-HARDENED"

__all__ = [
    # Main exports (canonical pipeline)
    "AGIEngine",
    "AGIResult",
    "execute_agi",
    "get_agi_engine",
    "cleanup_expired_sessions",
    "AGINeuralCore",
    "AGIKernel",
    "get_agi_core",
    # Hardening
    "run_pre_checks",
    "run_post_checks",
    "HardeningResult",
    "RiskLevel",
    # Metrics
    "ThermodynamicDashboard",
    "get_dashboard",
    # v53.4.0: Precision (Gap P1)
    "PrecisionEstimate",
    "PrecisionWeighter",
    "estimate_precision",
    "update_belief_with_precision",
    "cosine_similarity",
    # v53.4.0: Hierarchy (Gap P2)
    "HierarchyLevel",
    "HierarchicalBelief",
    "HierarchicalEncoder",
    "encode_hierarchically",
    "get_cumulative_delta_s",
    # v53.4.0: Active Inference (Gap P3)
    "ActionType",
    "ActionPolicy",
    "BeliefState",
    "ExpectedFreeEnergyCalculator",
    "MotorOutput",
    "compute_action_policy",
    "execute_action",
    # v53.4.0: Trinity Sync
    "TrinitySync",
    "ConvergenceResult",
    "trinity_sync",
    "PARADOXES",
    # v53.4.0: Hardened engine (standalone)
    "AGIEngineHardened",
    "execute_agi_hardened",
    # Version
    "__version__",
]
