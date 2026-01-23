"""
arifos_well - @WELL Universal Migration Tool

Universal file care module for governed migrations across all AI coding agents:
- Claude MCP (Model Context Protocol)
- GitHub Copilot
- ChatGPT Codex
- Google Gemini CLI

Architecture:
- L3_KERNEL/arifos_core/waw/well_file_care.py (Core logic)
- L4_MCP/arifos_well/server/app.py (REST API - Universal Interface)
- L4_MCP/arifos_well/bindings/ (Platform-specific bindings)

Version: v42.0.0
License: AGPL-3.0
"""

__version__ = "42.0.0"
__author__ = "arifOS Project"

# Re-export from core module for convenience
try:
    from arifos_core.integration.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        WellOperationType,
        WellOperationStatus,
        WellAuditEntry,
        WellHealthReport,
        WellOperationResult,
        create_well_file_care,
    )

    __all__ = [
        "WellConstants",
        "WellFileCare",
        "WellOperationType",
        "WellOperationStatus",
        "WellAuditEntry",
        "WellHealthReport",
        "WellOperationResult",
        "create_well_file_care",
    ]
except ImportError:
    # Core not installed, just expose version
    __all__ = ["__version__"]
