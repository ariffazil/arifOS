"""
AGI (Mind/Δ) — v53.5.0 WIRED

Live Engine: engine_hardened.py (AGIEngineHardened)
Stages: 111 SENSE → 222 THINK → 333 FORGE

Modules:
    precision.py            - Kalman-style precision weighting (P1)
    hierarchy.py            - 5-level cortical encoding (P2)
    action.py               - EFE minimization action selection (P3)
    trinity_sync.py         - 333 AGI↔ASI 6-paradox convergence
    trinity_sync_hardened.py - Hardened sync with geometric synthesis
    engine_hardened.py      - Full hardened pipeline (LIVE)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

import logging as _logging
_agi_init_logger = _logging.getLogger("codebase.agi")

# v53.5.0: Hardened engine (NOW LIVE — wired into kernel.py)
from .engine_hardened import AGIEngineHardened, execute_agi_hardened

# v53.4.0: Gap modules (wired into engine_hardened pipeline)
from .precision import PrecisionEstimate, PrecisionWeighter, estimate_precision, update_belief_with_precision, cosine_similarity
from .hierarchy import HierarchyLevel, HierarchicalBelief, HierarchicalEncoder, encode_hierarchically, get_cumulative_delta_s
from .action import ActionType, ActionPolicy, BeliefState, ExpectedFreeEnergyCalculator, MotorOutput, compute_action_policy, execute_action

# v53.4.0: Trinity Sync (333 convergence)
from .trinity_sync import TrinitySync, ConvergenceResult, trinity_sync, PARADOXES
from .trinity_sync_hardened import TrinitySyncHardened, synthesize_paradox, compute_trinity_score

# Legacy engine + kernel (safe import — may depend on archived modules)
try:
    from .engine import AGIEngine, AGIResult, execute_agi, get_agi_engine, cleanup_expired_sessions
except ImportError as _e:
    _agi_init_logger.warning(f"Legacy AGIEngine unavailable (archived deps): {_e}")
    AGIEngine = AGIResult = execute_agi = get_agi_engine = cleanup_expired_sessions = None

try:
    from .kernel import AGINeuralCore as _LegacyAGINeuralCore, get_agi_core
except ImportError as _e:
    _agi_init_logger.warning(f"Legacy AGINeuralCore unavailable: {_e}")
    _LegacyAGINeuralCore = get_agi_core = None

# Backward compat alias
AGIKernel = _LegacyAGINeuralCore

__version__ = "v53.5.0-WIRED"

__all__ = [
    # Live engine
    "AGIEngineHardened",
    "execute_agi_hardened",
    # Precision (P1)
    "PrecisionEstimate", "PrecisionWeighter", "estimate_precision",
    "update_belief_with_precision", "cosine_similarity",
    # Hierarchy (P2)
    "HierarchyLevel", "HierarchicalBelief", "HierarchicalEncoder",
    "encode_hierarchically", "get_cumulative_delta_s",
    # Active Inference (P3)
    "ActionType", "ActionPolicy", "BeliefState",
    "ExpectedFreeEnergyCalculator", "MotorOutput",
    "compute_action_policy", "execute_action",
    # Trinity Sync
    "TrinitySync", "ConvergenceResult", "trinity_sync", "PARADOXES",
    "TrinitySyncHardened", "synthesize_paradox", "compute_trinity_score",
    # Legacy (may be None)
    "AGIEngine", "AGIResult", "execute_agi", "get_agi_engine",
    "cleanup_expired_sessions", "AGIKernel", "get_agi_core",
    "__version__",
]
