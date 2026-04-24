"""
CanonicalProvider — 13-Tool LocalProvider
══════════════════════════════════════════

Registers the canonical arif_* tool surface on a LocalProvider.
"""
from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.providers import LocalProvider

from arifosmcp.tools import (
    arif_session_init,
    arif_sense_observe,
    arif_evidence_fetch,
    arif_mind_reason,
    arif_kernel_route,
    arif_reply_compose,
    arif_memory_recall,
    arif_heart_critique,
    arif_gateway_connect,
    arif_ops_measure,
    arif_judge_deliberate,
    arif_vault_seal,
    arif_forge_execute,
)

logger = logging.getLogger(__name__)

_TOOL_REGISTRY: list[tuple[str, Any]] = [
    ("arif_session_init", arif_session_init),
    ("arif_sense_observe", arif_sense_observe),
    ("arif_evidence_fetch", arif_evidence_fetch),
    ("arif_mind_reason", arif_mind_reason),
    ("arif_kernel_route", arif_kernel_route),
    ("arif_reply_compose", arif_reply_compose),
    ("arif_memory_recall", arif_memory_recall),
    ("arif_heart_critique", arif_heart_critique),
    ("arif_gateway_connect", arif_gateway_connect),
    ("arif_ops_measure", arif_ops_measure),
    ("arif_judge_deliberate", arif_judge_deliberate),
    ("arif_vault_seal", arif_vault_seal),
    ("arif_forge_execute", arif_forge_execute),
]


class CanonicalProvider(LocalProvider):
    """LocalProvider subclass that registers the 13 canonical arif_* tools."""

    def __init__(self, on_duplicate: str = "warn") -> None:
        super().__init__(on_duplicate=on_duplicate)  # type: ignore[arg-type]
        self._register_canonical_tools()

    def _register_canonical_tools(self) -> None:
        for name, fn in _TOOL_REGISTRY:
            try:
                self.tool(name=name)(fn)
                logger.debug(f"[CanonicalProvider] Registered tool: {name}")
            except Exception as e:
                logger.warning(f"[CanonicalProvider] Failed to register {name}: {e}")
        logger.info(f"[CanonicalProvider] {len(_TOOL_REGISTRY)} canonical tools registered")
