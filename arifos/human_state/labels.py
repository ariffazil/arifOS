from enum import Enum


class StateDomain(str, Enum):
    BODY = "body"
    PEACE = "peace"
    ENERGY = "energy"
    AKAL = "akal"
    PRESENCE = "presence"
    AMANAH = "amanah"


class WitnessType(str, Enum):
    TEXTUAL = "textual"
    BIOLOGICAL = "biological"
    SOVEREIGN = "sovereign"


class TruthStatus(str, Enum):
    TEXT_SIGNAL_ONLY = "TEXT_SIGNAL_ONLY"
    TOOL_REPORTED = "TOOL_REPORTED"
    USER_CONFIRMED = "USER_CONFIRMED"
    CONTRADICTED = "CONTRADICTED"
    VOID_TELEMETRY = "VOID_TELEMETRY"
    HOLD = "HOLD"


class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
