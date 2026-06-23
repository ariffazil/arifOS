#!/usr/bin/env python3
"""
arifosmcp/kernel_mcp.py — Reference narrow kernel MCP surface (arifOS side).

This is the canonical-side illustration of "transport the kernel to MCP agentically and optimally".

It is intentionally minimal (<200 LOC target for the server logic).

It demonstrates:
- Import pure logic from core/constitution_kernel, core/cooling_ledger, etc.
- Expose only governance + state + rhythm hooks.
- Read-first, escalation always explicit.
- Designed to be consumable by Grok Build narrow clients (mcp-arifos-kernel is the client-optimized sibling in A-FORGE/services/grok-build-mcp).

In production the full surface is still served by server.py + register_tools (runtime/tools.py).

Use this module or the A-FORGE grok-build copy when you want low-entropy kernel-only access.

Run:
  python -m arifosmcp.kernel_mcp
  python arifosmcp/kernel_mcp.py --http --port 18793

See also:
- A-FORGE/services/grok-build-mcp/mcp_arifos_kernel.py (Grok Build primary)
- constitutional_map.py (full CANONICAL_TOOLS incl. arif_kernel_* and arif_judge)
- core/constitution_kernel.py
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Make sure package resolves when run directly
HERE = Path(__file__).parent
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))

from fastmcp import FastMCP

# Attempt real core imports (graceful fallback for minimal env)
try:
    from arifosmcp.core.constitution_kernel import get_kernel  # type: ignore
except Exception:
    get_kernel = None  # type: ignore

try:
    from arifosmcp.core.cooling_ledger import CoolingLedger  # type: ignore
except Exception:
    CoolingLedger = None  # type: ignore

mcp = FastMCP(
    name="arifos-kernel-mcp",
    instructions="Reference narrow constitutional kernel surface. Read + gated judgment entry. Part of entropy reduction effort. Prefer the Grok Build mcp-arifos-kernel sibling for CLI use.",
    version="2026.06.23-ref",
)

ROOT = Path(os.environ.get("REPO_ROOT", "/root"))


@mcp.tool()
def arif_kernel_health() -> Dict[str, Any]:
    """Light kernel health using core if available, else FS signals."""
    info: Dict[str, Any] = {"status": "ok", "source": "arifosmcp/kernel_mcp (reference)"}
    if get_kernel:
        try:
            k = get_kernel()
            info["core_kernel"] = str(type(k))
        except Exception as e:
            info["core_error"] = str(e)[:120]
    # Always include entropy summary pointer
    er = ROOT / "arifOS" / "entropy-report.json"
    info["entropy_report"] = str(er) if er.exists() else "missing"
    info["note"] = "Full surfaces: arif_judge / arif_seal via main MCP. Use narrow mcp-arifos-kernel for Grok Build."
    return info


@mcp.tool()
def arif_kernel_check(action: str) -> Dict[str, Any]:
    """Pre-flight floor hint. Real 888 is arif_judge + human."""
    risky = any(w in action.lower() for w in ["delete", "deploy", "seal", "prod", "force"])
    return {
        "status": "ok",
        "risk_hint": "high" if risky else "low",
        "escalate_to": "arif_judge (MCP) or A2A 888 or mcp-arifos-kernel submit_for_judgment",
    }


if __name__ == "__main__":
    import sys as _sys
    if "--http" in _sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=18793)
    else:
        mcp.run(transport="stdio")
