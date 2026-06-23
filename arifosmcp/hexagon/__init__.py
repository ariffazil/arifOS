"""
arifOS HEXAGON Integration Module — Constitutional Agent Parliament (5 roles)

Ratified: 2026-06-02 (HEXAGON-AGENTS-FORGE-20260602, chain 2505)
Renamed from agentzero: 2026-06-06 (HEXAGON-NAME-CANON-20260606)

The 5-Class Agent Parliament (HEXAGON architecture):
- 333-AGI (Δ MIND): reasons + executes (FORGE subsumed)
- 555-ASI (Ω HEART): ethical + memory + audit lineage
- 888-APEX (ΦΙ JUDGE): constitutional judge, F1-F13 arbitration
- A-AUDIT (APEX oversight): continuous ethical + safety monitor
- A-ARCHIVE (ASI service): immutable ledger keeper

MVP scope (live): APEXAgent + AGIAgent + PromptArmor + HoldStateManager
+ ConstitutionalMemoryStore (basis for 555-ASI stub)
Stubs deferred: A-AUDIT (→ arif_measure), A-ARCHIVE (→ arif_seal)
"""

__version__ = "2026.06.06-HEXAGON"
__author__ = "Muhammad Arif bin Fazil [ΔΩΨ | ARIF]"

from .agents.base import ConstitutionalAgent, TrinityRole, Verdict
from .agents.engineer import AGIAgent
from .agents.validator import APEXAgent
from .escalation.hold_state import HoldStateManager
from .memory.constitutional_memory import ConstitutionalMemoryStore
from .security.prompt_armor import PromptArmor

# Backward-compat aliases (HEXAGON-NAME-CANON-20260606)
# Old code paths still work; new code should use the HEXAGON names.
EngineerAgent = AGIAgent  # was EngineerAgent (Ω) — reclassified to Δ MIND
ValidatorAgent = APEXAgent  # was ValidatorAgent (Ψ) — kept as APEX alias

__all__ = [
    "ConstitutionalAgent",
    "TrinityRole",
    "Verdict",
    "APEXAgent",
    "AGIAgent",
    "ValidatorAgent",  # backward-compat alias
    "EngineerAgent",  # backward-compat alias
    "PromptArmor",
    "HoldStateManager",
    "ConstitutionalMemoryStore",
]
