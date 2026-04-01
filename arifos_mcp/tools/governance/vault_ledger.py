"""
arifOS vault_ledger Tool
========================

Canonical vault_ledger implementation.

Stage: 999_VAULT
Trinity: Ψ (Execution/Audit)
Floors: F1, F13

Status: PHASE 3 - Migration to Tool base class
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifos_mcp.tools.base import Tool
from arifos_mcp.abi.v1_0 import VaultLedgerRequest, VaultLedgerResponse
from core.shared.types import Verdict


_tool_instance = None


def get_instance() -> Tool:
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _VaultLedgerTool()
    return _tool_instance


class _VaultLedgerTool(Tool):
    """vault_ledger - Immutable audit log and decision recording."""

    name = "vault_ledger"
    stage = "999_VAULT"
    floors = ["F1", "F13"]
    readonly = False

    async def execute(self, payload: dict) -> dict:
        from arifos_mcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP
        from arifos_mcp.runtime.tools_internal import vault_ledger_dispatch_impl
        from arifos_mcp.runtime.compat import CurrentContext

        mode = payload.get("mode", "query")
        session_id = payload.get("session_id")
        risk_tier = payload.get("risk_tier", "medium")
        dry_run = payload.get("dry_run", True)
        auth_context = payload.get("auth_context")

        if "vault_ledger" in HARDENED_DISPATCH_MAP:
            res = await HARDENED_DISPATCH_MAP["vault_ledger"](mode=mode, payload=payload)
        else:
            res = await vault_ledger_dispatch_impl(
                mode=mode,
                payload=payload,
                auth_context=auth_context,
                risk_tier=risk_tier,
                dry_run=dry_run,
                ctx=CurrentContext(),
            )

        if isinstance(res, RuntimeEnvelope):
            return res.model_dump() if hasattr(res, 'model_dump') else res.dict()
        if hasattr(res, 'model_dump'):
            return res.model_dump()
        if hasattr(res, 'dict'):
            return res.dict()
        return res


from core.shared.types import RuntimeEnvelope
from arifos_mcp.tools.base import ToolRegistry
ToolRegistry.register(_VaultLedgerTool())
