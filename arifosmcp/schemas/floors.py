"""
Canonical Constitutional Floors (F1–F13) + Adat primitives
═══════════════════════════════════════════════════════════

This is the **single machine-readable source of truth** for the 13 floors
and core Adat Agentik elements.

Human / constitutional source of truth:
    /root/arifOS/GENESIS/000_KERNEL_CANON.md   (exact names + rules)
    /root/arifOS/GENESIS/010_ADAT_AGENTIC.md   (permission doctrine)

All code, tests, deliberation, renderers, and enforcement MUST import from
here instead of hard-coding lists or copying markdown text.

Never edit the values below without also updating the GENESIS source and
running the alignment gate.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


FloorType = Literal["HARD", "SOFT", "DERIVED"]


class ConstitutionalFloor(BaseModel):
    """One constitutional floor with its canonical identity."""

    id: str = Field(..., pattern=r"^F(1[0-3]|[1-9])$", description="F1, F2, ..., F13")
    name: str = Field(..., description="Canonical short name, e.g. AMANAH, TRUTH")
    rule: str = Field(..., description="One-line rule from GENESIS/000_KERNEL_CANON.md")
    type: FloorType = Field(..., description="HARD | SOFT | DERIVED (from CLAUDE.md classification)")

    @model_validator(mode="after")
    def _check_consistency(self) -> "ConstitutionalFloor":
        # Keep the model self-describing and hard to misuse
        if not self.name or not self.rule:
            raise ValueError("name and rule are required")
        return self


# ──────────────────────────────────────────────────────────────────────────────
# THE 13 CONSTITUTIONAL FLOORS
# Exact content from arifOS/GENESIS/000_KERNEL_CANON.md (as of 2026-06-24)
# ──────────────────────────────────────────────────────────────────────────────

FLOORS: list[ConstitutionalFloor] = [
    ConstitutionalFloor(
        id="F1",
        name="AMANAH",
        rule="Reversible first. Irreversible → 888 HOLD",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F2",
        name="TRUTH",
        rule="P(truth) ≥ 0.99. Cheap claims = VOID",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F3",
        name="TRI-WITNESS",
        rule="Human + AI + Earth witness ≥ 0.75",
        type="DERIVED",
    ),
    ConstitutionalFloor(
        id="F4",
        name="CLARITY",
        rule="Every output must reduce entropy (ΔS ≤ 0)",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F5",
        name="PEACE²",
        rule="Non-destructive power",
        type="SOFT",
    ),
    ConstitutionalFloor(
        id="F6",
        name="EMPATHY",
        rule="Protect weakest stakeholder",
        type="SOFT",
    ),
    ConstitutionalFloor(
        id="F7",
        name="HUMILITY",
        rule="No fake certainty (Ω₀ ∈ [0.03, 0.05])",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F8",
        name="GENIUS",
        rule="G ≥ 0.80 for complex actions",
        type="DERIVED",
    ),
    ConstitutionalFloor(
        id="F9",
        name="ANTIHANTU",
        rule="No deception, manipulation, consciousness claims",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F10",
        name="ONTOLOGY",
        rule="AI-only ontology. Soul = VOID; map to harness content",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F11",
        name="AUDITABILITY",
        rule="Every decision logged. Provenance per field.",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F12",
        name="RESILIENCE",
        rule="Injection defense",
        type="HARD",
    ),
    ConstitutionalFloor(
        id="F13",
        name="SOVEREIGN",
        rule="Human veto FINAL. Harness switch belongs to sovereign.",
        type="HARD",
    ),
]


# ──────────────────────────────────────────────────────────────────────────────
# Derived constants (use these everywhere in code)
# ──────────────────────────────────────────────────────────────────────────────

FLOOR_IDS: list[str] = [f.id for f in FLOORS]
FLOOR_NAMES: list[str] = [f.name for f in FLOORS]
FLOOR_BY_ID: dict[str, ConstitutionalFloor] = {f.id: f for f in FLOORS}
FLOOR_BY_NAME: dict[str, ConstitutionalFloor] = {f.name: f for f in FLOORS}


def get_floor(floor_id: str) -> ConstitutionalFloor:
    """Return the canonical floor or raise KeyError."""
    fid = floor_id.upper()
    if fid not in FLOOR_BY_ID:
        raise KeyError(f"Unknown floor: {floor_id}. Valid: {FLOOR_IDS}")
    return FLOOR_BY_ID[fid]


def is_canonical_floor(floor_id: str) -> bool:
    """True if this is one of the official 13 floors."""
    return floor_id.upper() in FLOOR_BY_ID


def validate_floors(floor_ids: list[str]) -> list[str]:
    """Return the subset of invalid floor ids (empty list = all good)."""
    return [fid for fid in floor_ids if not is_canonical_floor(fid)]


# ──────────────────────────────────────────────────────────────────────────────
# ADAT AGENTIK (core primitives — keep minimal here; full doctrine in 010)
# ──────────────────────────────────────────────────────────────────────────────

ADAT_TERAS: list[str] = [
    "Kejujuran",
    "Maruah",
    "Veto",
    "Kesungguhan",
    "Kerahasiaan",
    "Keinsafan",
    "Tebus-Salah",
]

FIQH_TIERS: list[str] = ["WAJIB", "SUNAT", "HARUS", "MAKRUH", "HARAM"]


# ──────────────────────────────────────────────────────────────────────────────
# Convenience for JSON / other languages / deliberation
# ──────────────────────────────────────────────────────────────────────────────

def as_dict_list() -> list[dict]:
    """Pure data form (safe for serialization and cross-language use)."""
    return [
        {
            "id": f.id,
            "name": f.name,
            "rule": f.rule,
            "type": f.type,
        }
        for f in FLOORS
    ]


def as_names_only() -> list[str]:
    return FLOOR_NAMES.copy()


# Quick sanity at import time
assert len(FLOORS) == 13, "There must be exactly 13 constitutional floors"
assert len(set(FLOOR_IDS)) == 13
assert "F13" in FLOOR_BY_ID and FLOOR_BY_ID["F13"].name == "SOVEREIGN"
