"""
@PROMPT - Language Governance Codec + Router

The intelligent protocol layer that:
1. DECODES: Human input → arifOS signals (intent, risk, stakeholders)
2. ROUTES: Signals → appropriate engine(s) (AGI/ASI/APEX/TRINITY)
3. ENCODES: arifOS verdicts → human-readable responses

Position in arifOS:
    User Input → @PROMPT → [AGI|ASI|APEX|TRINITY] → @PROMPT → User Output

Architecture:
    arifos/core/prompt/
    ├── __init__.py         ← This file
    ├── codec.py            ← Encoder/Decoder (speaks both languages)
    └── router.py           ← Route to AGI/ASI/APEX/TRINITY

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from arifos.core.prompt.codec import (
    SignalExtractor,
    ResponseFormatter,
    PromptSignal,
    PromptResponse,
    IntentType,
    RiskLevel,
    EngineRoute,
)
from arifos.core.prompt.router import PromptRouter, EngineVerdictBundle

__all__ = [
    # Codec
    "SignalExtractor",
    "ResponseFormatter",
    "PromptSignal",
    "PromptResponse",
    # Enums
    "IntentType",
    "RiskLevel",
    "EngineRoute",
    # Router
    "PromptRouter",
    "EngineVerdictBundle",
]

__version__ = "v51.2.0"
