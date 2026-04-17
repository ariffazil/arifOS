"""
Verdict — Constitutional verdict types
DITEMPA BUKAN DIBERI
"""

from enum import Enum


class Verdict(str, Enum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    SEAL = "SEAL"
    VOID = "VOID"


class VerdictStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


TERMINAL_VERDICTS = {Verdict.SEAL, Verdict.BLOCK, Verdict.VOID}


def isTerminalVerdict(v: Verdict) -> bool:
    return v in TERMINAL_VERDICTS


def requiresHumanReview(v: Verdict) -> bool:
    return v == Verdict.HOLD