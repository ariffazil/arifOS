"""
codebase MCP Server Package (v53.0.0-SEAL)

Model Context Protocol implementation for arifOS constitutional AI governance.

Entry points:
- python -m arifos.mcp         # stdio transport (Claude Desktop)
- python -m arifos.mcp sse     # SSE transport (Railway/Cloud)

Tool names (interchangeable):
  v53 Human:     v52 Internal:
  authorize  <-> init_000
  reason     <-> agi_genius
  evaluate   <-> asi_act
  decide     <-> apex_judge
  seal       <-> vault_999

DITEMPA BUKAN DIBERI
"""

__version__ = "v53.0.0-SEAL"

# v53 Human-language tools (preferred)
from codebase.mcp.tools import (
    authorize,
    reason,
    evaluate,
    decide,
    seal,
    # v52 internal aliases
    init_000,
    agi_genius,
    asi_act,
    apex_judge,
    vault_999,
    # Data classes
    AuthorizeResult,
    ReasonResult,
    EvaluateResult,
    DecideResult,
    SealResult,
    Verdict,
    # Claude API integration
    run_constitutional_pipeline,
)

__all__ = [
    # v53 Human-language tools
    "authorize",
    "reason",
    "evaluate",
    "decide",
    "seal",
    # v52 Internal aliases
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999",
    # Data classes
    "AuthorizeResult",
    "ReasonResult",
    "EvaluateResult",
    "DecideResult",
    "SealResult",
    "Verdict",
    # Pipeline
    "run_constitutional_pipeline",
]
