"""
arifOS SEA-LION Integration (v36.1Omega)

Constitutional AI for Southeast Asia.
Wraps SEA-LION regional models with arifOS governance.

PHOENIX SOVEREIGNTY (v36.1.1):
    - Python-sovereign Amanah detection via AMANAH_DETECTOR
    - One Law for All Models (Claude, SEA-LION, GPT, etc.)
    - If SEA-LION outputs "rm -rf /", Python says NO

Usage (Legacy - GovernedSEALION):
    from integrations.sealion import GovernedSEALION
    client = GovernedSEALION(api_key="your-key")
    result = client.chat("What is AI governance?")

Usage (New - SealionEngine with Amanah Lock):
    from integrations.sealion import SealionEngine
    engine = SealionEngine(api_key="your-key")
    result = engine.generate("What is AI governance?")
    if result.amanah_blocked:
        print("BLOCKED:", result.amanah_violations)

Usage (Judge for verdict):
    from integrations.sealion import SealionJudge
    judge = SealionJudge()
    judgment = judge.evaluate("LLM output here")
    print(judgment.verdict)  # SEAL, PARTIAL, VOID, or SABAR
"""

# Legacy exports (v34-v35 compatibility)
from .arifos_sealion import (
    GovernedSEALION,
    FloorComputer,
    StandaloneCoolingLedger,
    Metrics,
    SEALION_MODELS,
    THRESHOLDS,
    create_client,
    quick_chat,
)

# PHOENIX SOVEREIGNTY exports (v36.1Omega)
from .engine import (
    SealionConfig,
    SealionResult,
    SealionEngine,
    MockSealionEngine,
)

from .judge import (
    JudgmentResult,
    SealionJudge,
    quick_judge,
    check_sealion_output,
)

__version__ = "36.1Omega"
__all__ = [
    # Legacy
    "GovernedSEALION",
    "FloorComputer",
    "StandaloneCoolingLedger",
    "Metrics",
    "SEALION_MODELS",
    "THRESHOLDS",
    "create_client",
    "quick_chat",
    # PHOENIX SOVEREIGNTY
    "SealionConfig",
    "SealionResult",
    "SealionEngine",
    "MockSealionEngine",
    "JudgmentResult",
    "SealionJudge",
    "quick_judge",
    "check_sealion_output",
]
