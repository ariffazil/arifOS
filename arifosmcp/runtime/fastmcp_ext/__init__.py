"""FastMCP extension layer for arifOS AAA MCP.

This package isolates FastMCP-specific integration concerns outside `core/`.

Audit 2026-07-28 Phase C: do NOT rely on import side effects for
resource/prompt registration. The kernel server (`arifosmcp.server`)
must call ONE explicit function `register_public_resources_and_prompts(server)`
with the live FastMCP instance. Two related invariants:

  1. The canonical kernel server is `mcp = FastMCP("ARIFOS MCP", ...)` at
     `arifosmcp/server.py`. There is exactly one FastMCP instance per process
     for the canonical surface. Other FastMCP instances exist (`mind_mcp.py`,
     `kernel_mcp.py`, `mcp_tools.py`) for organ-specific narrow surfaces —
     they are NOT the production server.
  2. Resources and prompts are registered EXPLICITLY at server.py boot,
     not via module-import side effects. Tests must invoke the actual
     canonical server boot path (or a test instance bound to the same
     registration function) to verify resource/prompt exposure.
"""

from .discovery import build_surface_discovery
from .resources import register_arifos_resources
from .transports import run_server


def register_public_resources_and_prompts(server) -> dict:
    """Register all arifOS MCP resources + prompts on the canonical server.

    Audit 2026-07-28 Phase C: this is the SINGLE registration entry point.
    No import side effects, no hidden singleton. Caller passes the live
    FastMCP instance explicitly.

    Returns a dict with `resources` (list of URIs) and `prompts` (list of
    names). Caller is responsible for surfacing failures (we return what
    succeeded, plus any exception per section).
    """
    result: dict = {"resources": [], "prompts": [], "errors": []}

    try:
        result["resources"] = list(register_arifos_resources(server))
    except Exception as e:
        result["errors"].append(f"resources: {e!r}")

    try:
        # Avoid the circular import at module load — load on demand.
        from .prompts import register_arifos_prompts

        result["prompts"] = list(register_arifos_prompts(server))
    except Exception as e:
        result["errors"].append(f"prompts: {e!r}")

    return result


__all__ = [
    "run_server",
    "build_surface_discovery",
    "register_arifos_resources",
    "register_public_resources_and_prompts",
]
