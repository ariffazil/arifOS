"""mode_contract_gate.py — per-mode contract resolution for the execution gate.

WHY (2026-10-20, FI-002; defect observed live):
    `pre_execution_gate.resolve_action_class_for_mode` reads ONE manifest entry
    per TOOL (`CANONICAL_TOOL_MANIFEST`) plus two mode lists. Three consequences
    were proved by reading the code against the live wire:

    1. arif_memory declares action_class=OBSERVE with forget/promote/revise in
       `dangerous_modes`. Because the manifest class is OBSERVE, the
       "prefer manifest default for dangerous modes when stronger" branch is
       skipped (OBSERVE is not MUTATE/IRREVERSIBLE), and the call falls through
       to `return requested_action`. So `arif_memory(mode=forget)` — a permanent
       deletion — is admitted as OBSERVE by this gate. It is refused in practice
       by the capability-authority layer, which is a DIFFERENT mechanism.
    2. arif_route's manifest lists only route/delegate/bridge; the live tool also
       serves triage/status/kernel/metabolize. Unknown modes fall through.
    3. arif_report is absent from the manifest entirely → `entry is None` →
       `return requested_action`. A write path inherits the caller's claim.

    The rule this module adds: a mode with no declared contract cannot inherit a
    permissive class. Unknown + mutating = HOLD.

WHAT THIS MODULE IS NOT
    It does not dispatch, execute, or mutate. Pure functions only. Wiring it into
    `pre_execution_gate.pre_execution_gate()` is a separate, reviewed change.
"""

from __future__ import annotations

from typing import Any

# Contract action_class → gate ActionClass name. Kept as strings so this module
# imports nothing from the gate (no import cycle, testable in isolation).
CONTRACT_TO_GATE: dict[str, str] = {
    "OBSERVE": "OBSERVE",
    "PREPARE": "ANALYZE",  # reasoning/decision output, no state change
    "MATERIAL": "MUTATE",  # reversible state change
    "EXTERNAL_SIDE_EFFECT": "EXTERNAL_SIDE_EFFECT",  # open-internet egress or
    # other effect no rollback can undo (e.g. arif_report.flush paging the
    # human over Telegram). Contract-vocabulary key added 2026-10-25; takes
    # effect for declarations using this class only after this module is
    # reloaded (kernel restart). Until then declare MATERIAL (strictest class
    # the live resolver can apply) — see abi/mode_contracts.json arif_report.flush.
    "IRREVERSIBLE": "IRREVERSIBLE",
}

# Gate classes that change state. A contract-less mode may not inherit any of these.
MUTATING_CLASSES = frozenset({"MUTATE", "IRREVERSIBLE", "EXTERNAL_SIDE_EFFECT"})


class ContractUnavailable(Exception):
    """No contract exists for this tool.mode and the request would mutate state."""

    def __init__(self, tool: str, mode: str, requested: str, detail: str = "") -> None:
        self.tool = tool
        self.mode = mode
        self.requested = requested
        super().__init__(
            f"NO_CONTRACT: {tool}.{mode or '<no-mode>'} requests {requested} "
            f"but declares no execution contract{(' — ' + detail) if detail else ''}"
        )


def _contracts() -> dict[str, Any]:
    from arifosmcp.abi.kernel_abi import mode_contracts

    return mode_contracts()["contracts"]


RANK: dict[str, int] = {
    "OBSERVE": 0,
    "ANALYZE": 1,
    "DRAFT": 2,
    "MUTATE": 3,
    "EXTERNAL_SIDE_EFFECT": 4,
    "IRREVERSIBLE": 5,
}


def resolve_contract_class(
    tool_name: str,
    tool_mode: str,
    requested_class: str,
    manifest_class: str | None = None,
) -> tuple[str, str]:
    """Return (gate_action_class, reason).

    Two declaration sources exist and neither may weaken the other:
      - mode_contracts.json  (per-mode, precise)
      - the gate's CANONICAL_TOOL_MANIFEST (per-tool, coarse)

    When both speak, the STRICTER wins and the disagreement is reported in the
    reason string. A single-source resolver would have let the contract's
    OBSERVE for arif_think.axioms silently weaken the manifest's ANALYZE.

    Caller may ask for a MORE conservative class than resolved; asking for a
    less conservative one is a downgrade and is refused.
    """
    mode = (tool_mode or "").strip().lower()
    contracts = _contracts()
    key = f"{tool_name}.{mode}" if mode else None
    spec = contracts.get(key) if key else None

    if spec is None:
        if requested_class in MUTATING_CLASSES:
            raise ContractUnavailable(
                tool_name,
                mode,
                requested_class,
                "declare it in abi/mode_contracts.json, or request OBSERVE",
            )
        return requested_class, f"no contract for {key or tool_name}; non-mutating request honoured"

    declared = CONTRACT_TO_GATE[spec["action_class"]]
    reason = f"contract {key}: {spec['action_class']} → {declared}"

    if manifest_class and manifest_class in RANK:
        if RANK[manifest_class] > RANK[declared]:
            reason += f"; manifest says {manifest_class} — stricter wins"
            declared = manifest_class
        elif RANK[manifest_class] < RANK[declared]:
            reason += f"; manifest says {manifest_class} — contract stricter, kept"

    if RANK.get(requested_class, 0) < RANK[declared]:
        raise ContractUnavailable(
            tool_name,
            mode,
            requested_class,
            f"{reason}; caller asked for {requested_class} (downgrade refused)",
        )
    return declared, reason


def contract_summary(tool_name: str, tool_mode: str) -> dict[str, Any] | None:
    """Read-only view used by tests and by future receipt lines."""
    mode = (tool_mode or "").strip().lower()
    spec = _contracts().get(f"{tool_name}.{mode}")
    if spec is None:
        return None
    return {
        "contract_id": f"{tool_name}.{mode}",
        "action_class": spec["action_class"],
        "authority_required": spec["authority_required"],
        "reversible": not spec.get("irreversible", False),
        "verifier": spec.get("verifier"),
        "recovery": spec.get("recovery"),
    }
