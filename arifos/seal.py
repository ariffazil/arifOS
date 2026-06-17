"""
seal.py — High-level seal helper.

Convenience wrapper around `guards.seal`. Most agents only need this.
"""

from __future__ import annotations

from typing import Any

from arifos.client import ArifOSMCPClient
from arifos.decision import Decision
from arifos.guards import seal as _seal


async def seal(
    final_output: Any,
    decision_history: list[Decision],
    client: ArifOSMCPClient | None = None,
) -> Decision:
    """Seal the agent run. Returns a Decision with seal_pointer."""
    return await _seal(
        final_output=final_output,
        decision_history=decision_history,
        client=client,
    )
