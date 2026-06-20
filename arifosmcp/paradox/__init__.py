"""
arifosmcp/paradox/ — Constitutional Paradox Infrastructure

One matrix, five organs, zero authority collapse.

This package provides the SHARED INFRASTRUCTURE for paradox anchor
registration, injection, desensitization, and matrix geometry across
all five cognitive organs (Sense, Mind, Memory, Heart, Judge).

Each organ retains SOVEREIGNTY over:
- When an anchor fires (trigger semantics)
- Which anchor fires for which decision point
- How the injected anchor affects downstream behavior

This package provides SHARED:
- ParadoxAnchor dataclass and registry
- O(1) cell/ID lookup
- Anchor injection algorithm
- Wallpaper/desensitization detection
- 3×3 matrix geometry and verdict routing

DITEMPA BUKAN DIBERI — Forged, Not Given
"""
from arifosmcp.paradox.desensitization import (
    DESENSITIZATION_CRITICAL_THRESHOLD,
    DESENSITIZATION_WARNING_THRESHOLD,
    DesensitizationResult,
    check_desensitization,
)
from arifosmcp.paradox.injection import InjectedAnchor, inject_paradox_anchor
from arifosmcp.paradox.matrix import (
    MATRIX_CELLS,
    MATRIX_COLS,
    MATRIX_ROWS,
    ParadoxMatrix,
    cell_key,
    verdict_to_cell,
)
from arifosmcp.paradox.registry import (
    AnchorRegistry,
    ParadoxAnchor,
    build_organ_anchors,
    get_registry,
    register_organ,
)

__all__ = [
    # Registry
    "ParadoxAnchor",
    "AnchorRegistry",
    "build_organ_anchors",
    "register_organ",
    "get_registry",
    # Injection
    "inject_paradox_anchor",
    "InjectedAnchor",
    # Desensitization
    "check_desensitization",
    "DesensitizationResult",
    "DESENSITIZATION_WARNING_THRESHOLD",
    "DESENSITIZATION_CRITICAL_THRESHOLD",
    # Matrix
    "MATRIX_ROWS",
    "MATRIX_COLS",
    "MATRIX_CELLS",
    "cell_key",
    "verdict_to_cell",
    "ParadoxMatrix",
]
