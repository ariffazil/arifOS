"""
arifOS MCP Tools (v53.0.0)
Human-Language Constitutional AI Framework

Tool Names (Interchangeable):
  v53 Human:     v52 Internal:
  authorize  <-> init_000 / mcp_000_init
  reason     <-> agi_genius / mcp_agi_genius
  evaluate   <-> asi_act / mcp_asi_act
  decide     <-> apex_judge / mcp_apex_judge
  seal       <-> vault_999 / mcp_999_vault

Verdict Translation:
  APPROVE     <-> SEAL
  CONDITIONAL <-> PARTIAL
  REJECT      <-> VOID
  ESCALATE    <-> 888_HOLD

DITEMPA BUKAN DIBERI
"""

# v53 Human-language tools (PREFERRED)
from .v53_human_layer import (
    # Tool functions
    authorize,
    reason,
    evaluate,
    decide,
    seal,
    # v52 name aliases
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
    # Verdict translation
    Verdict,
)

# v52 Internal tools (for backward compatibility)
from .mcp_aaa import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

__all__ = [
    # v53 Human-language tools (PREFERRED)
    "authorize",
    "reason",
    "evaluate",
    "decide",
    "seal",
    # v52 Short aliases
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999",
    # v52 Full names (backward compatible)
    "mcp_000_init",
    "mcp_agi_genius",
    "mcp_asi_act",
    "mcp_apex_judge",
    "mcp_999_vault",
    # Data classes
    "AuthorizeResult",
    "ReasonResult",
    "EvaluateResult",
    "DecideResult",
    "SealResult",
    "Verdict",
]
