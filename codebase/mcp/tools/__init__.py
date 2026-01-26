"""
MCP Tools v53 - Human Language Constitutional AI Framework
Codebase Integration Layer

Exports both human-language tools (v53) and internal aliases (v52):

Human Names (v53):       Internal Names (v52):
  authorize        <->     init_000
  reason           <->     agi_genius
  evaluate         <->     asi_act
  decide           <->     apex_judge
  seal             <->     vault_999

Both names call the same function - semantic interchangeability
for governance across any LLM.

DITEMPA BUKAN DIBERI
"""

from .mcp_tools_v53 import (
    # Data classes
    AuthorizeResult,
    ReasonResult,
    EvaluateResult,
    DecideResult,
    SealResult,
    Verdict,
    # v53 Human-language tools
    authorize,
    reason,
    evaluate,
    decide,
    seal,
    # v52 Internal aliases (same functions)
    init_000,
    agi_genius,
    asi_act,
    apex_judge,
    vault_999,
)

from .integration_claude_api import (
    TOOL_DEFINITIONS,
    execute_tool,
    get_tool_definitions,
    ConstitutionalAIAssistant,
    run_constitutional_pipeline,
)

__all__ = [
    # Data classes
    "AuthorizeResult",
    "ReasonResult",
    "EvaluateResult",
    "DecideResult",
    "SealResult",
    "Verdict",
    # v53 Human-language tools (preferred)
    "authorize",
    "reason",
    "evaluate",
    "decide",
    "seal",
    # v52 Internal aliases (backward compatible)
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999",
    # Claude API integration
    "TOOL_DEFINITIONS",
    "execute_tool",
    "get_tool_definitions",
    "ConstitutionalAIAssistant",
    "run_constitutional_pipeline",
]
