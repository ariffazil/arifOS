"""
GEOX — Earth Intelligence Core
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI — Forged, Not Given
Version: v2026.04.10-EIC (Earth Intelligence Core)

Simplified, focused, essential.

The 7 Tools:
1. geox_compute_ac_risk — ToAC calculation (THE CORE)
2. geox_load_seismic_line — Seismic with F4 Clarity
3. geox_build_structural_candidates — Multi-model interpretation
4. geox_verify_geospatial — Coordinate grounding
5. geox_feasibility_check — Constitutional firewall
6. geox_evaluate_prospect — Prospect verdict with 888_HOLD
7. geox_earth_signals — Live Earth observations

Constitutional Floors: F1, F2, F4, F7, F9, F11, F13
"""

__version__ = "v2026.04.10-EIC"
__seal__ = "DITEMPA BUKAN DIBERI"

from geox.core.ac_risk import compute_ac_risk, AC_RiskResult
from geox.core.tool_registry import ToolRegistry, ToolStatus, ErrorCode

__all__ = [
    "__version__",
    "__seal__",
    "compute_ac_risk",
    "AC_RiskResult",
    "ToolRegistry",
    "ToolStatus",
    "ErrorCode",
]
