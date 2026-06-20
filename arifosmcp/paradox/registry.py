"""
arifosmcp/paradox/registry.py — Unified Paradox Anchor Registry

One source of truth for all 45 paradox anchors (9 per organ × 5 organs).
Provides O(1) lookup by ID, matrix cell, and organ.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHOR — Canonical dataclass
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=False)
class AnchorQuote:
    """A verified quote that stabilizes the paradox anchor."""
    text: str
    author: str
    work: str
    year: str
    verification_level: str = "traditional_attribution"
    translation_note: str | None = None
    adaptation_note: str | None = None


@dataclass(frozen=False)
class AnchorBinding:
    """What happens when the paradox anchor fires."""
    event: str
    trigger: str
    effect: str


@dataclass
class ParadoxAnchor:
    """
    A single paradox anchor — one cell in the 3×3 organ matrix.

    Each anchor connects a verified philosophical quote to a specific
    firing policy (binding). The quote is canon; the binding evolves.
    """
    anchor_id: str
    organ: str
    matrix_cell: str
    matrix_row: str  # TRUTH | CLARITY | HUMILITY
    matrix_col: str  # CARE | PEACE | JUSTICE

    # Motto
    motto_binding: str

    # Quote (canon — changes rarely)
    quote: AnchorQuote

    # Antithesis (the tension that makes it a paradox, not a slogan)
    antithesis: str
    axis: str

    # Binding (policy — may evolve faster than quote)
    binding: AnchorBinding

    # Severity
    severity_on_fire: str = "warn"  # info | warn | hold_bias | hard_gate
    risk_bias: str = "conservative"  # conservative | neutral | action_bias
    authority_scope: str = ""  # organ-specific | cross_organ
    norm: str = "WAJIB"  # WAJIB | HARUS | SUNAT

    def to_dict(self) -> dict[str, Any]:
        """Legacy dict format for backward compat with existing injection code."""
        return {
            "id": self.anchor_id,
            "organ": self.organ,
            "matrix_cell": self.matrix_cell,
            "matrix_row": self.matrix_row,
            "matrix_col": self.matrix_col,
            "motto_binding": self.motto_binding,
            "quote": {
                "text": self.quote.text,
                "author": self.quote.author,
                "work": self.quote.work,
                "year": self.quote.year,
                "verification_level": self.quote.verification_level,
            },
            "antithesis": self.antithesis,
            "axis": self.axis,
            "binding": {
                "event": self.binding.event,
                "trigger": self.binding.trigger,
                "effect": self.binding.effect,
            },
            "severity_on_fire": self.severity_on_fire,
            "risk_bias": self.risk_bias,
            "authority_scope": self.authority_scope,
            "norm": self.norm,
        }

    @classmethod
    def from_legacy_dict(cls, d: dict, organ: str) -> ParadoxAnchor:
        """Build from a legacy anchor dict (as used in organ files)."""
        q = d["quote"]
        b = d.get("binding", {})
        return cls(
            anchor_id=d["id"],
            organ=organ,
            matrix_cell=d["matrix_cell"],
            matrix_row=d["matrix_row"],
            matrix_col=d["matrix_col"],
            motto_binding=d["motto_binding"],
            quote=AnchorQuote(
                text=q["text"],
                author=q["author"],
                work=q["work"],
                year=q["year"],
                verification_level=q.get("verification_level", "traditional_attribution"),
            ),
            antithesis=d["antithesis"],
            axis=d["axis"],
            binding=AnchorBinding(
                event=b.get("event", ""),
                trigger=b.get("trigger", ""),
                effect=b.get("effect", ""),
            ),
            severity_on_fire=d.get("severity_on_fire", "warn"),
            risk_bias=d.get("risk_bias", "conservative"),
            authority_scope=d.get("authority_scope", organ),
            norm=d.get("norm", "WAJIB"),
        )


# ═══════════════════════════════════════════════════════════════════════════════
# ANCHOR REGISTRY — O(1) lookup across all 5 organs
# ═══════════════════════════════════════════════════════════════════════════════


class AnchorRegistry:
    """
    Unified registry for paradox anchors across all organs.

    Provides O(1) lookup by:
    - anchor ID (e.g., "J_TxC")
    - matrix cell (e.g., "truth_care")
    - (organ, cell) tuple

    Supports legacy dict access for backward compat with existing
    organ injection functions during Phase 1 migration.
    """

    def __init__(self, organ: str, anchors: list[ParadoxAnchor]):
        self.organ = organ
        self._anchors = list(anchors)
        self._by_id: dict[str, ParadoxAnchor] = {}
        self._by_cell: dict[str, ParadoxAnchor] = {}
        self._legacy_by_id: dict[str, dict] = {}
        self._legacy_by_cell: dict[str, dict] = {}

        for anchor in anchors:
            if anchor.anchor_id in self._by_id:
                raise ValueError(
                    f"Duplicate anchor ID '{anchor.anchor_id}' in organ '{organ}'"
                )
            if anchor.matrix_cell in self._by_cell:
                raise ValueError(
                    f"Duplicate matrix cell '{anchor.matrix_cell}' in organ '{organ}'"
                )
            self._by_id[anchor.anchor_id] = anchor
            self._by_cell[anchor.matrix_cell] = anchor
            legacy = anchor.to_dict()
            self._legacy_by_id[anchor.anchor_id] = legacy
            self._legacy_by_cell[anchor.matrix_cell] = legacy

    def __len__(self) -> int:
        return len(self._anchors)

    def __iter__(self):
        return iter(self._anchors)

    def get_by_id(self, anchor_id: str) -> ParadoxAnchor | None:
        """O(1) lookup by anchor ID."""
        return self._by_id.get(anchor_id)

    def get_by_cell(self, matrix_cell: str) -> ParadoxAnchor | None:
        """O(1) lookup by matrix cell."""
        return self._by_cell.get(matrix_cell)

    def get_by_row_col(self, row: str, col: str) -> ParadoxAnchor | None:
        """Lookup by (row, col) tuple."""
        return self._by_cell.get(f"{row.lower()}_{col.lower()}")

    def get_legacy_by_id(self, anchor_id: str) -> dict | None:
        """Backward-compat: legacy dict lookup by ID."""
        return self._legacy_by_id.get(anchor_id)

    def get_legacy_by_cell(self, matrix_cell: str) -> dict | None:
        """Backward-compat: legacy dict lookup by cell."""
        return self._legacy_by_cell.get(matrix_cell)

    def all_ids(self) -> list[str]:
        """All anchor IDs."""
        return list(self._by_id.keys())

    def all_cells(self) -> list[str]:
        """All matrix cell keys."""
        return list(self._by_cell.keys())

    # Legacy dict access patterns for backward compat
    def __contains__(self, key: str) -> bool:
        return key in self._legacy_by_id or key in self._legacy_by_cell

    def __getitem__(self, key: str) -> dict:
        if key in self._legacy_by_id:
            return self._legacy_by_id[key]
        if key in self._legacy_by_cell:
            return self._legacy_by_cell[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> dict | None:
        """Dict-like get for backward compat."""
        return self._legacy_by_id.get(key) or self._legacy_by_cell.get(key) or default


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL REGISTRY — All 45 anchors, loaded lazily
# ═══════════════════════════════════════════════════════════════════════════════

_global_registry: dict[str, AnchorRegistry] = {}


def register_organ(organ: str, anchors: list[ParadoxAnchor]) -> AnchorRegistry:
    """Register an organ's paradox anchors."""
    registry = AnchorRegistry(organ, anchors)
    _global_registry[organ] = registry
    return registry


def get_registry(organ: str) -> AnchorRegistry | None:
    """Get the anchor registry for a specific organ."""
    return _global_registry.get(organ)


def build_organ_anchors(organ: str, legacy_anchors: list[dict]) -> list[ParadoxAnchor]:
    """Convert legacy anchor dicts to ParadoxAnchor dataclass instances."""
    return [ParadoxAnchor.from_legacy_dict(a, organ) for a in legacy_anchors]
