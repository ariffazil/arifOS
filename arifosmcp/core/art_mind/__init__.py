"""
ART Mind — The micro arifOS cognition substrate (federated under ART).

v0.1 (2026-06-21) — Advisory only. Generates ranked plans with confidence bands
BEFORE arif_judge_deliberate. Sits at the 333-REASON stage of the 000-999 pipeline.

This is the 5th organ of ART:
  1. Reflex   — runtime/art.py        (hot path, 3 checks, 4 states)
  2. Compat   — runtime/art_compat.py (legacy 6-check shim)
  3. Pusaka   — runtime/art_pusaka.py (doctrinal heritage)
  4. Library  — runtime/art_library.py (call history + RAG)
  5. Mind     — core/art_mind/        (cognition substrate — this package)

Doctrine: ART may recommend. Judge authorizes. Vault witnesses.
The reflex disciplines. The mind proposes. The doctrine constrains.

Architecture (intra-package):
  belief.py     — Bayesian posterior over world state (F2 TRUTH: explicit confidence)
  generator.py  — Candidate plan generation (3 canonical patterns)
  rollout.py    — Trajectory simulation over horizon
  utility.py    — Multi-objective expected utility with F1-F13 constraints
  constraints.py — F1-F13 → constraint mapping
  service.py    — Orchestrator (the entry point)
  schemas.py    — Pydantic v2 models for inputs/outputs
  config.py     — Weights + thresholds

Constitutional binding (F1-F13):
  F1  AMANAH    — irreversible plan → 888_HOLD
  F2  TRUTH     — explicit confidence bands, never point estimates
  F3  WITNESS   — provenance labels per observation
  F4  CLARITY   — ΔS ≤ 0 (no added confusion)
  F5  PEACE     — de-escalate, don't escalate
  F6  EMPATHY   — maruah hard floor (0.4), below → -inf utility
  F7  HUMILITY  — confidence cap at 0.99 (no fake certainty)
  F8  GENIUS    — preserve long-term intelligence
  F9  ANTIHANTU — this is a TOOL, not a mind (no consciousness claims)
  F10 ONTOLOGY  — AI-only ontology
  F11 AUTH      — caller identity required
  F12 INJECTION — input sanitized (5× patterns checked upstream)
  F13 SOVEREIGN — human veto is absolute; 888_HOLD gates irreversible

DITEMPA BUKAN DIBERI — Mind forged, not granted. Advises, never authorizes.
"""

from .service import MindaService
from .config import MindConfig
from .schemas import ThinkRequest, ThinkResponse, ScoredPlan
from .belief import BeliefState, BeliefEngine
from .generator import Plan, ToolAction, CandidateGenerator
from .rollout import RolloutEngine
from .utility import UtilityEngine, MARUAH_HARD_FLOOR
from .constraints import FConstraint, F_CONSTRAINTS


# ART federation aliases — the umbrella namespace uses these names
ArtMind = MindaService
ArtMindConfig = MindConfig

__all__ = [
    # Native names (used by core/art_mind/ directly)
    "MindaService",
    "MindConfig",
    "ThinkRequest",
    "ThinkResponse",
    "ScoredPlan",
    "BeliefState",
    "BeliefEngine",
    "Plan",
    "ToolAction",
    "CandidateGenerator",
    "RolloutEngine",
    "UtilityEngine",
    "FConstraint",
    "F_CONSTRAINTS",
    "MARUAH_HARD_FLOOR",
    # ART federation aliases (used by the umbrella arifosmcp.art namespace)
    "ArtMind",
    "ArtMindConfig",
]
