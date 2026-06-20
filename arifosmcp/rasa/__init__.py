"""
arifOS Rasa Module — Human Rasa Governance Pipeline

DITEMPA BUKAN DIBERI — Forged, Not Given.

This module implements the 5-organ human rasa decoding pipeline
mapped to the canonical 000-999 metabolic pipeline:

    000 → 111 → 222 → 333 → 444 → 555m → 555 → 888 → 999

The Rasa Contract treats human rasa as SACRED FIRST-CLASS EVIDENCE.
It NEVER claims qualia. It NEVER simulates feelings.
It governs the machine's response to protect dignity, peace, and
the human-machine boundary.

IMPORTANT: This module is for HUMAN rasa governance only.
For AGENT self-monitoring, see arifosmcp.boot.internal_rasa.
For memory qualia, see core.vault999.phenomenological.qualia_trace.

MODULES:
  rasa_contract.py      — Core 5-organ pipeline (RasaContract)
  rasa_schemas.py       — Pydantic v2 schemas for all rasa types
  rasa_integration.py   — Adapter hooks for kernel integration
  rasa_telemetry.py     — Shadow telemetry logger (append-only JSONL)
  rasa_wiring.py        — Kernel wrappers + reversible activation
  rasa_wiring_config.py — Feature flag configuration (RASA_CONTRACT_MODE)
"""

from arifosmcp.rasa.rasa_contract import RasaContract
from arifosmcp.rasa.rasa_integration import (
    rasa_check_floors,
    rasa_governed_execute,
    rasa_heart_hook,
    rasa_integration_diagnostics,
    rasa_judge_hook,
    rasa_memory_hook,
    rasa_mind_hook,
    rasa_sense_hook,
)
from arifosmcp.rasa.rasa_schemas import (
    BiologicalClaimLevel,
    BiologicalSignal,
    BiologicalSource,
    ConstitutionPosture,
    ExistentialPosture,
    ExistentialTag,
    OrganHealth,
    OrganHealthStatus,
    RasaContext,
    RasaContractResult,
    RasaDetection,
    RasaEmotionTag,
    RasaHeartVerdict,
    RasaIntensity,
    RasaJudgeVerdict,
    RasaMemoryPattern,
    RasaRiskBand,
    RasaUncertaintyBand,
    RelationshipType,
    SocialContext,
)
from arifosmcp.rasa.rasa_telemetry import RasaTelemetry
from arifosmcp.rasa.rasa_wiring import (
    activate_rasa_wiring,
    deactivate_rasa_wiring,
    is_rasa_wired,
    rasa_wiring_diagnostics,
    rasa_wrap_heart,
    rasa_wrap_judge,
    rasa_wrap_memory,
    rasa_wrap_mind,
    rasa_wrap_sense,
    rasa_wrap_session_init,
)
from arifosmcp.rasa.rasa_wiring_config import (
    RasaContractMode,
    get_rasa_contract_mode,
    mode_allows_enforcement,
)

__all__ = [
    # Core contract
    "RasaContract",
    # Schemas
    "RasaEmotionTag",
    "RasaIntensity",
    "RasaRiskBand",
    "RasaUncertaintyBand",
    "ConstitutionPosture",
    "RasaDetection",
    "RasaContext",
    "RasaMemoryPattern",
    "RasaHeartVerdict",
    "RasaJudgeVerdict",
    "RasaContractResult",
    # Phase 2 Coverage Honesty schemas
    "BiologicalSource",
    "BiologicalClaimLevel",
    "BiologicalSignal",
    "RelationshipType",
    "SocialContext",
    "ExistentialTag",
    "ExistentialPosture",
    "OrganHealthStatus",
    "OrganHealth",
    # Integration hooks
    "rasa_sense_hook",
    "rasa_mind_hook",
    "rasa_memory_hook",
    "rasa_heart_hook",
    "rasa_judge_hook",
    "rasa_governed_execute",
    "rasa_integration_diagnostics",
    "rasa_check_floors",
    # Telemetry
    "RasaTelemetry",
    # Wiring
    "rasa_wrap_sense",
    "rasa_wrap_mind",
    "rasa_wrap_heart",
    "rasa_wrap_memory",
    "rasa_wrap_judge",
    "rasa_wrap_session_init",
    "activate_rasa_wiring",
    "deactivate_rasa_wiring",
    "is_rasa_wired",
    "rasa_wiring_diagnostics",
    # Config
    "RasaContractMode",
    "get_rasa_contract_mode",
    "mode_allows_enforcement",
]
