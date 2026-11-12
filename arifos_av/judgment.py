"""Doer != Judge.

The actor that performs an action can never certify it (Godel: no
self-certification). Verification is the terminal state: "done" is a
verdict, not a feeling, and never the doer's own report.
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass(frozen=True)
class Evidence:
    """A single piece of proof. Labels travel with data, always."""

    label: str   # OBS / DER / HYP / UNKNOWN
    data: str


class Judge:
    """Independent witness."""

    def __init__(self, name: str):
        self.name = name

    def verify(self, claim: str, evidence, falsifier=None) -> Verdict:
        if not evidence:
            return Verdict.UNVERIFIED
        if falsifier is not None and falsifier(claim, evidence):
            return Verdict.FAILED
        return Verdict.VERIFIED


def complete(verdict: Verdict) -> bool:
    """A task is complete ONLY when verified. Everything else is open."""
    return verdict is Verdict.VERIFIED
