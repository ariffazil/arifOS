"""
arifosmcp/core/floors.py — Re-export shim to canonical /core/floors.py
────────────────────────────────────────────────────────────────────────
DITEMPA BUKAN DIBERI

Design note (2026-06-02):
    Tools under arifosmcp/tools/ import via
    'from arifosmcp.core.floors import X' to keep their import paths
    local to the arifosmcp package. The actual floor code lives at the
    top-level /core/floors.py to avoid duplicate maintenance.

    Per arifosmcp/core/__init__.py, this submodule exists *solely* to
    hold these re-exports. No re-exports are added to __init__.py to
    avoid shadowing the top-level /core/ namespace.

Split-brain context:
    /core/floors.py             — older, used by tools
    /core/shared/floors.py      — runtime SOT (THRESHOLDS dict)
    The split is logged as F13 sit-down work; do not consolidate
    without sovereign approval. See [[floor-consensus-fix-2026-06-02]].
"""

from core.floors import evaluate_tool_call  # noqa: F401 — re-export

__all__ = ["evaluate_tool_call"]
