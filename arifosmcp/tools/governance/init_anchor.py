"""
arifOS init_anchor Tool
=======================

Canonical init_anchor implementation.

Stage: 000_INIT
Trinity: PSI Ψ
Floors: F11, F12, F13

Status: PHASE 1 - Reference implementation
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.base import Tool
from arifosmcp.abi.v1_0 import (
    InitAnchorRequest,
    InitAnchorResponse,
    IdentityResolution,
)
from core.shared.types import Verdict, RuntimeStatus, RuntimeEnvelope


# Tool singleton instance for registration
_tool_instance = None


def get_instance() -> Tool:
    """Get or create the init_anchor tool instance."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = _InitAnchorTool()
    return _tool_instance


class _InitAnchorTool(Tool):
    """
    init_anchor - Constitutional session initialization.

    This tool establishes identity and constitutional context
    for all subsequent operations in a session.
    """

    name = "init_anchor"
    stage = "000_INIT"
    floors = ["F11", "F12", "F13"]
    readonly = True

    async def execute(self, payload: dict) -> dict:
        """
        Execute init_anchor.

        Args:
            payload: Validated InitAnchorRequest as dict

        Returns:
            InitAnchorResponse as dict
        """
        # Extract parameters
        actor_id = payload.get("actor_id", "anonymous")
        declared_name = payload.get("declared_name")
        mode = payload.get("mode", "init")

        # Resolve identity
        identity = self._resolve_identity(actor_id, declared_name)

        # Generate or validate session ID
        session_id = self._get_session_id(payload.get("session_id"), actor_id)

        # Determine auth state
        auth_state = self._determine_auth_state(identity)

        # Determine allowed next tools based on auth state
        allowed_tools = self._get_allowed_tools(auth_state)

        # Build response
        response = InitAnchorResponse(
            ok=True,
            session_id=session_id,
            auth_state=auth_state,
            identity=identity,
            allowed_next_tools=allowed_tools,
            verdict=Verdict.SEAL.value,
        )

        return response.model_dump() if hasattr(response, 'model_dump') else response.dict()

    def _resolve_identity(self, actor_id: str, declared_name: str | None) -> IdentityResolution:
        """Resolve the claimed identity."""
        normalized = actor_id.strip().lower().replace(" ", "-").replace("_", "-")

        if normalized == "anonymous":
            claim_status = "anonymous"
        elif normalized in ["arif", "arif-fazil", "ariffazil"]:
            claim_status = "verified"
        else:
            claim_status = "claimed"

        return IdentityResolution(
            claimed_actor_id=actor_id,
            resolved_actor_id=normalized,
            claim_status=claim_status,
            reason=None if claim_status != "anonymous" else "No identity claimed",
        )

    def _get_session_id(self, provided: str | None, actor_id: str) -> str:
        """Get or generate session ID."""
        import uuid

        if provided:
            return provided

        return f"{actor_id}-{uuid.uuid4().hex[:8]}"

    def _determine_auth_state(self, identity: IdentityResolution) -> str:
        """Determine authentication state from identity."""
        if identity.claim_status == "verified":
            return "verified"
        elif identity.claim_status == "claimed":
            return "anchored"
        return "unverified"

    def _get_allowed_tools(self, auth_state: str) -> list[str]:
        """Get allowed next tools based on auth state."""
        tools_by_state = {
            "unverified": [
                "init_anchor",
                "math_estimator",
                "architect_registry"
            ],
            "anchored": [
                "init_anchor",
                "math_estimator",
                "architect_registry",
                "agi_mind",
                "apex_judge",
            ],
            "verified": [
                "init_anchor",
                "math_estimator",
                "architect_registry",
                "agi_mind",
                "apex_judge",
                "arifOS_kernel",
                "vault_ledger",
                "engineering_memory",
            ],
        }
        return tools_by_state.get(auth_state, tools_by_state["unverified"])


# Auto-register on import
from arifosmcp.tools.base import ToolRegistry
ToolRegistry.register(_InitAnchorTool())
