"""
arifosmcp/paradox/injection.py — Unified Paradox Anchor Injection

Single inject_paradox_anchor() function that works for all 5 organs.
Resolves anchors via the unified registry. Handles keyword auto-detection
as a fallback when no explicit ID or cell is provided.

One injection engine, five organ contexts, zero authority collapse.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arifosmcp.paradox.desensitization import check_desensitization
from arifosmcp.paradox.registry import AnchorRegistry


@dataclass
class InjectedAnchor:
    """The payload injected into an organ's output at a decision point."""

    quote_id: str
    organ: str
    matrix_cell: str
    matrix_row: str
    matrix_col: str
    motto_binding: str
    quote: str
    author: str
    work: str
    year: str
    verification_level: str
    antithesis: str
    axis: str
    norm: str
    severity_on_fire: str
    risk_bias: str
    authority_scope: str
    binding_event: str
    trigger_context: str
    _matrix_note: str
    recursion_depth: int | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "quote_id": self.quote_id,
            "organ": self.organ,
            "matrix_cell": self.matrix_cell,
            "matrix_row": self.matrix_row,
            "matrix_col": self.matrix_col,
            "motto_binding": self.motto_binding,
            "quote": self.quote,
            "author": self.author,
            "work": self.work,
            "year": self.year,
            "verification_level": self.verification_level,
            "antithesis": self.antithesis,
            "axis": self.axis,
            "norm": self.norm,
            "severity_on_fire": self.severity_on_fire,
            "risk_bias": self.risk_bias,
            "authority_scope": self.authority_scope,
            "binding_event": self.binding_event,
            "trigger_context": self.trigger_context,
            "_matrix_note": self._matrix_note,
        }
        if self.recursion_depth is not None:
            d["recursion_depth"] = self.recursion_depth
        return d


def inject_paradox_anchor(
    output: dict,
    registry: AnchorRegistry,
    trigger_context: str,
    anchor_id: str | None = None,
    matrix_cell: str | None = None,
    recursion_depth: int | None = None,
    state_changed: bool = True,
    guard_existing: bool = True,
) -> dict:
    """
    Unified paradox anchor injection for any organ.

    Resolution order (determinism first):
      1. Explicit anchor_id → O(1) lookup in registry
      2. Explicit matrix_cell → O(1) lookup in registry
      3. Keyword auto-detect from trigger_context (last resort)

    Each injection logs to the desensitization detector via check_desensitization().
    Anchors that fire repeatedly without downstream state change are flagged as wallpaper.

    Args:
        output: The organ's output dict being built
        registry: The organ's AnchorRegistry
        trigger_context: Free-text description of what triggered the injection
        anchor_id: Explicit anchor ID to inject (priority 1)
        matrix_cell: Explicit matrix cell to resolve (priority 2)
        recursion_depth: Optional recursion depth (for Heart fractal critique)
        state_changed: Whether downstream state changed (affects desensitization)
        guard_existing: If True, don't overwrite an already-injected anchor

    Returns:
        The output dict with paradox_anchor injected (or unchanged if guard blocks)
    """
    # ── Guard: already anchored? ──────────────────────────────────────────
    if guard_existing and output.get("paradox_anchor"):
        return output

    # ── Resolution: ID → cell → keyword auto-detect ──────────────────────
    anchor: dict | None = None

    if anchor_id:
        anchor = registry.get_legacy_by_id(anchor_id)
    elif matrix_cell:
        anchor = registry.get_legacy_by_cell(matrix_cell)

    # Auto-detect: keyword overlap with binding triggers
    if anchor is None:
        ctx_words = set(trigger_context.lower().split())
        for legacy_anchor in registry:  # Iterates over ParadoxAnchor objects
            legacy = legacy_anchor.to_dict()
            trig = legacy.get("binding", {}).get("trigger", "")
            trig_words = set(trig.lower().split())
            if trig_words and len(ctx_words & trig_words) >= 2:
                anchor = legacy
                break

    if anchor is None:
        return output

    # ── Desensitization check ─────────────────────────────────────────────
    anchor_aid = anchor["id"]
    desens = check_desensitization(anchor_aid, state_changed)
    if desens.status in ("desensitized", "warning"):
        output["_anchor_health"] = desens.to_dict()

    # ── Build injection payload ───────────────────────────────────────────
    q = anchor["quote"]
    b = anchor.get("binding", {})
    injected = InjectedAnchor(
        quote_id=anchor["id"],
        organ=registry.organ,
        matrix_cell=anchor["matrix_cell"],
        matrix_row=anchor["matrix_row"],
        matrix_col=anchor["matrix_col"],
        motto_binding=anchor["motto_binding"],
        quote=q["text"],
        author=q["author"],
        work=q["work"],
        year=q["year"],
        verification_level=q.get("verification_level", ""),
        antithesis=anchor["antithesis"],
        axis=anchor["axis"],
        norm=anchor.get("norm", "WAJIB"),
        severity_on_fire=anchor.get("severity_on_fire", "warn"),
        risk_bias=anchor.get("risk_bias", "conservative"),
        authority_scope=anchor.get("authority_scope", registry.organ),
        binding_event=b.get("event", ""),
        trigger_context=trigger_context,
        recursion_depth=recursion_depth,
        _matrix_note=(
            f"Cell [{anchor['matrix_row']}×{anchor['matrix_col']}] — "
            f"Connected to arifOS PARADOX_MATRIX in core/shared/mottos.py"
        ),
    )

    output["paradox_anchor"] = injected.to_dict()
    return output
