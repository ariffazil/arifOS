"""
arifosmcp/paradox/matrix.py — 3×3 Paradox Matrix Geometry

The 3×3 orthogonal matrix underpins all 45 paradox anchors across
the 5 cognitive organs. Each cell is an intersection of a row
(TRUTH/CLARITY/HUMILITY) and a column (CARE/PEACE/JUSTICE).

This module provides:
- Matrix geometry primitives (rows, cols, cells)
- Verdict → cell routing for Judge
- Cell key construction

One matrix, five organs, zero authority collapse.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Literal

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX AXES
# ═══════════════════════════════════════════════════════════════════════════════

RowT = Literal["TRUTH", "CLARITY", "HUMILITY"]
ColT = Literal["CARE", "PEACE", "JUSTICE"]
CellT = Literal[
    "truth_care",
    "truth_peace",
    "truth_justice",
    "clarity_care",
    "clarity_peace",
    "clarity_justice",
    "humility_care",
    "humility_peace",
    "humility_justice",
]

MATRIX_ROWS: tuple[RowT, ...] = ("TRUTH", "CLARITY", "HUMILITY")
MATRIX_COLS: tuple[ColT, ...] = ("CARE", "PEACE", "JUSTICE")
MATRIX_CELLS: tuple[CellT, ...] = tuple(
    f"{r.lower()}_{c.lower()}"  # type: ignore
    for r in MATRIX_ROWS
    for c in MATRIX_COLS
)


def cell_key(row: str, col: str) -> str:
    """Construct a canonical matrix cell key."""
    return f"{row.lower()}_{col.lower()}"


# ═══════════════════════════════════════════════════════════════════════════════
# VERDICT → CELL ROUTING (Judge-specific geometry)
# ═══════════════════════════════════════════════════════════════════════════════

# Maps (verdict_type, action_tier) → matrix_cell for Judge paradox anchors
VERDICT_CELL_MAP: dict[tuple[str, str], str] = {
    # Standard verdict routing
    ("SABAR", "*"): "clarity_justice",  # J_CxJ — Parker/MLK: arc bends only if we bend it
    ("SEAL", "standard"): "truth_peace",  # J_TxP — Aristotle: every SEAL is partial justice
    ("SEAL", "sovereign"): "humility_justice",  # J_HxJ — Kant: universality not computable
    ("SEAL", "c4"): "humility_justice",
    ("SEAL", "c5"): "humility_justice",
    ("HOLD", "sovereign"): "truth_care",  # J_TxC — Marcus Aurelius: if not right, don't do it
    ("HOLD", "c4"): "truth_care",
    ("HOLD", "c5"): "truth_care",
}


def verdict_to_cell(verdict: str, action_tier: str = "standard") -> str | None:
    """
    Resolve which matrix cell a verdict should anchor to.

    Returns the matrix cell key (e.g., "truth_peace") or None.
    """
    # Exact match
    key = (verdict, action_tier)
    if key in VERDICT_CELL_MAP:
        return VERDICT_CELL_MAP[key]
    # Wildcard tier match
    key = (verdict, "*")
    if key in VERDICT_CELL_MAP:
        return VERDICT_CELL_MAP[key]
    # Partial verdict match
    for (v, t), cell in VERDICT_CELL_MAP.items():
        if v in verdict and t == action_tier:
            return cell
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX MATRIX — Geometry lookup class
# ═══════════════════════════════════════════════════════════════════════════════


class ParadoxMatrix:
    """
    Geometry lookup for the 3×3 paradox matrix.

    Not to be confused with the PARADOX_MATRIX in core/shared/mottos.py
    which stores MatrixCell objects. This is a lightweight geometry-only
    lookup that doesn't carry motto/quote data.
    """

    @staticmethod
    def cell(row: str, col: str) -> str:
        """Get the canonical cell key for a row/col intersection."""
        return cell_key(row, col)

    @staticmethod
    def row_of(cell: str) -> str:
        """Extract row from a cell key."""
        return cell.split("_")[0].upper()

    @staticmethod
    def col_of(cell: str) -> str:
        """Extract column from a cell key."""
        return cell.split("_")[1].upper()

    @staticmethod
    def is_valid_cell(cell: str) -> bool:
        """Check if a string is a valid matrix cell key."""
        return cell in MATRIX_CELLS

    @staticmethod
    def all_cells() -> tuple[str, ...]:
        """All 9 matrix cells."""
        return MATRIX_CELLS
