"""
HEXAGON Agent Classes (was: AgentZero Agent Classes)

5-Class Constitutional Parliament per HEXAGON canon (AAA/agents/HEXAGON.yaml).
- 333-AGI (Δ MIND)  → AGIAgent      (was EngineerAgent, reclassified Δ from Ω)
- 555-ASI (Ω HEART) → ASIAgent stub (deferred — wraps ConstitutionalMemoryStore)
- 888-APEX (ΦΙ)     → APEXAgent     (was ValidatorAgent)
- A-AUDIT           → AuditAgent stub (deferred — wraps arif_measure)
- A-ARCHIVE         → ArchiveAgent stub (deferred — wraps arif_seal)
"""

from .base import ConstitutionalAgent, TrinityRole, Verdict
from .engineer import AGIAgent  # was EngineerAgent
from .validator import APEXAgent  # was ValidatorAgent

# Backward-compat aliases (HEXAGON-NAME-CANON-20260606)
EngineerAgent = AGIAgent
ValidatorAgent = APEXAgent

__all__ = [
    "ConstitutionalAgent",
    "TrinityRole",
    "Verdict",
    "AGIAgent",  # was EngineerAgent
    "APEXAgent",  # was ValidatorAgent
    "EngineerAgent",  # backward-compat alias
    "ValidatorAgent",  # backward-compat alias
]
