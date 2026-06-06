"""
LawResult — Constitutional floor evaluation result
DITEMPA BUKAN DIBERI
"""

from typing import List
from pydantic import BaseModel


class FloorViolation(BaseModel):
    floor: str
    gate: str
    description: str
    severity: str


class LawResult(BaseModel):
    passed: bool
    verdict: str
    floors_checked: List[str]
    violations: List[FloorViolation]
    holds: List[str]
    warnings: List[str]
    maruah_band: str


FLOOR_NAMES = {
    "F1": "Amanah",
    "F2": "Truth",
    "F3": "Tri-Witness",
    "F4": "ΔS Clarity",
    "F5": "Peace²",
    "F6": "κᵣ Empathy",
    "F7": "Ω₀ Humility",
    "F8": "G Genius",
    "F9": "Ethics",
    "L10": "Conscience",
    "L11": "Audit",
    "L12": "Injection",
    "L13": "Sovereign",
}

FLOOR_ORDER = [
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "L10",
    "L11",
    "L12",
    "L13",
]
