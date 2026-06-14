"""
mcp_gate — Constitutional MCP Gate for arifOS
=============================================
The wedge between AI intention and real-world consequence.

MCP exposes capability.
arifOS governs permission.
This gate decides whether execution proceeds.

DITEMPA BUKAN DIBERI
"""

from .mcp_gate_v0 import (
    ActionClass,
    ActionRisk,
    GateVerdict,
    MCPGateRequest,
    MCPGateResponse,
    MCPGateV0,
    judge_action,
)

__all__ = [
    "ActionClass",
    "ActionRisk",
    "GateVerdict",
    "MCPGateRequest",
    "MCPGateResponse",
    "MCPGateV0",
    "judge_action",
]
