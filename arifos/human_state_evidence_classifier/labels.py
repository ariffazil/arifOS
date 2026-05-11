from enum import Enum


class StateDomain(str, Enum):
    """Expression domains we can weakly classify from available evidence."""

    BODY = "body"
    PEACE = "peace"
    ENERGY = "energy"
    AKAL = "akal"
    PRESENCE = "presence"
    AMANAH = "amanah"


class WitnessType(str, Enum):
    """The channel through which evidence arrives."""

    TEXTUAL = "textual"
    BIOLOGICAL = "biological"
    SOVEREIGN = "sovereign"


class TruthStatus(str, Enum):
    """How validated the evidence is. Hierarchy: LOWEST → HIGHEST certainty."""

    TEXT_SIGNAL_ONLY = "TEXT_SIGNAL_ONLY"  # LLM text pattern only
    TOOL_REPORTED = "TOOL_REPORTED"  # Tool output, unverified by human
    USER_CONFIRMED = "USER_CONFIRMED"  # Arif explicitly confirmed
    CONTRADICTED = "CONTRADICTED"  # Arif rejected the interpretation
    VOID_TELEMETRY = "VOID_TELEMETRY"  # Telemetry contaminated or unavailable
    HOLD = "HOLD"  # No evidence available at all


class Confidence(str, Enum):
    """How much evidence supports the estimate."""

    LOW = "LOW"  # Weak or single-witness evidence
    MEDIUM = "MEDIUM"  # Moderate cross-witness support
    HIGH = "HIGH"  # Confirmed by sovereign witness
