"""
arifOS v51.2.0 Constitutional Kernel
5-Tool Trinity Framework

Modules:
  arifos.mcp       - MCP Server (Trinity 5-tool)
  arifos.core      - AGI/ASI/APEX kernels
  arifos.protocol  - Protocol handlers
  arifos.api       - Body API (FastAPI, deprecated shim)

Usage:
  python -m arifos.mcp              # Trinity stdio (5 tools)
  python -m arifos.mcp trinity-sse  # Trinity SSE for Railway
  python -m arifos.api.server       # Body API (HTTP, deprecated shim)

DITEMPA BUKAN DIBERI
"""

# Core enforcement and system components (requires spec files)
try:
    from .core import *
    _CORE_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    # Spec files not available - orchestrator can still work independently
    import warnings
    warnings.warn(
        f"arifOS core unavailable (likely missing spec files): {e}. "
        "Orchestrator subpackage will work independently.",
        ImportWarning,
        stacklevel=2
    )
    _CORE_AVAILABLE = False

# Protocol components
try:
    from .protocol import *
    _PROTOCOL_AVAILABLE = True
except (ImportError, RuntimeError) as e:
    import warnings
    warnings.warn(
        f"arifOS protocol unavailable: {e}",
        ImportWarning,
        stacklevel=2
    )
    _PROTOCOL_AVAILABLE = False
