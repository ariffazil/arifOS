"""G-02 regression — every tool the kernel actually dispatches must be mapped
by the Execution State Machine, or enabling enforcement HOLDs it.

Background (FLOW_GAPS.md G-02). `ARIFOS_STATE_MACHINE_ENFORCE` gates
`ExecutionStateMachine.can_execute` at the `kernel.py` dispatch path, and
kernel.py passes the RAW tool name (`canonical_name = tool_name`; the legacy
alias table was removed). `_TOOL_STATE_MAP` was written in the older naming
era and had no `arif_route` / `arif_memory` keys, so `can_execute` classified
two of the eight canonical kernel verbs as *unknown tools* and returned False.

That is why the gate sat off for six days: it was off **and unsafe to switch
on** — enabling it would have HOLDed `arif_route` and `arif_memory` for every
session, and the failure would have looked like the gate working.

Run:  python3 -m pytest tests/test_g02_canonical_tool_coverage.py -q
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.executor import ExecutionState, ExecutionStateMachine

# The kernel's public surface (ARIFOS_PUBLIC_SURFACE_MODE=forge_next_8), plus
# `arif_judge_deliberate` — an internal name the kernel recognises in tools.py
# `_LOOP_FREE` even though it is not exposed over MCP today. An unmapped name
# fails closed, so every name the dispatcher could receive belongs here.
CANONICAL_KERNEL_TOOLS = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_judge_deliberate",
    "arif_forge",
    "arif_seal",
]


@pytest.mark.parametrize("tool", CANONICAL_KERNEL_TOOLS)
def test_canonical_tool_has_state_mapping(tool: str) -> None:
    """An unmapped tool is denied outright once enforcement is on."""
    assert ExecutionStateMachine.get_allowed_states(tool), (
        f"{tool} is dispatched by the kernel but absent from _TOOL_STATE_MAP — "
        "enabling ARIFOS_STATE_MACHINE_ENFORCE would HOLD it (G-02)"
    )


def test_route_is_allowed_in_analyze() -> None:
    assert ExecutionStateMachine.can_execute("arif_route", ExecutionState.ANALYZE)


def test_memory_is_omni_state() -> None:
    """The memory governor must be callable regardless of pipeline position."""
    for state in ExecutionState:
        assert ExecutionStateMachine.can_execute("arif_memory", state), state


def test_route_progresses_to_simulate() -> None:
    assert (
        ExecutionStateMachine.get_next_state("arif_route", ExecutionState.ANALYZE)
        is ExecutionState.SIMULATE
    )


def test_memory_does_not_advance_the_pipeline() -> None:
    """Infrastructure must not move the session's stage."""
    assert (
        ExecutionStateMachine.get_next_state("arif_memory", ExecutionState.ANALYZE)
        is ExecutionState.ANALYZE
    )
