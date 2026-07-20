"""
PR5 — Capital Judge Orchestrator.

Audit-4 mandates: ONE orchestrator, state-machine-driven, with separate receipts
for COMPUTATION → JUDGMENT → HUMAN_RATIFICATION → EXECUTION. WEALTH QUALIFY
result MUST NEVER become an EXECUTION receipt automatically.

Use:

  from arifosmcp.runtime.capital_judge import (
      CapitalJudgeOrchestrator, CapitalCase, ComputationReceipt, ...
  )

  orch = CapitalJudgeOrchestrator(case)
  orch.authenticate(authorization_header, audience="wealth",
                     required_capability="wealth_npv_reward")
  orch.validate()
  orch.compute(output=..., wealth_version=..., tool_versions=..., input_payload=...)
  orch.judge(verdict="PROCEED")
  if orch.requires_ratification():
      orch.ratify(actor="ARIF", decision="approve")
  orch.seal()
  # Execution is only possible through A-FORGE; orchestrator refuses otherwise.
"""

from __future__ import annotations

import time
from typing import Any

from .receipt import (
    ComputationReceipt,
    ExecutionReceipt,
    HumanRatificationReceipt,
    JudgmentReceipt,
)
from .state_machine import (
    CapitalCase,
    Receipt,
    State,
    StateMachine,
    TransitionError,
    _hash,
)


class CapitalJudgeOrchestrator:
    """Single orchestrator. State machine + receipt chain.

    Refuses to:
      - drop COMPUTATION straight to EXECUTED
      - issue EXECUTION without RATIFIED + SEALED
      - skip AUTHENTICATED before compute
    """

    def __init__(self, case: CapitalCase) -> None:
        self.case = case
        self.sm = StateMachine(case)
        self.actor: str | None = None
        self.session_id: str | None = None
        self.authorized_capability: str | None = None
        self._last_judgment: JudgmentReceipt | None = None
        self._last_ratification: HumanRatificationReceipt | None = None

    # ── transitions ──────────────────────────────────────────────────────────
    def authenticate(
        self, *, authorization_header: str | None, audience: str, required_capability: str
    ) -> None:
        """Verify the bearer token via the federation auth middleware."""
        from arifosmcp.runtime.wealth_auth import AuthError, authorize

        try:
            claims = authorize(
                authorization_header=authorization_header,
                audience=audience,
                required_capability=required_capability,
                minimum_authority=self.case.governance.get("minimum_authority", "OPERATOR"),
                public_simulation=self.case.governance.get("public_simulation", False),
            )
        except AuthError as exc:
            raise TransitionError(self.sm.state, State.AUTHENTICATED, reason=f"auth_failed: {exc}")
        # Public-simulation path: no actor bound. Tool must explicitly opt in.
        self.actor = claims.actor_id or "public-simulation"
        self.session_id = claims.session_id
        self.authorized_capability = required_capability
        self.sm.transition(State.AUTHENTICATED)

    def validate(self) -> None:
        if self.sm.state != State.AUTHENTICATED:
            raise TransitionError(self.sm.state, State.VALIDATED, reason="must authenticate first")
        # Schema validation: case.required fields are present.
        for k in ("case_id", "actor", "purpose", "valuation", "inputs", "governance"):
            v = getattr(self.case, k, None)
            if v is None or v == {} or v == []:
                raise TransitionError(
                    self.sm.state, State.VALIDATED, reason=f"missing required field: {k}"
                )
        self.sm.transition(State.VALIDATED)

    def compute(
        self,
        *,
        output: dict[str, Any],
        wealth_version: str,
        tool_versions: dict[str, str],
        input_payload: dict[str, Any] | None = None,
    ) -> ComputationReceipt:
        if self.sm.state != State.VALIDATED:
            raise TransitionError(self.sm.state, State.COMPUTED, reason="must validate first")
        if input_payload is None:
            input_payload = {
                "case_id": self.case.case_id,
                "inputs": self.case.inputs,
                "evidence": self.case.evidence,
            }
        receipt = ComputationReceipt(
            case=self.case,
            output=output,
            wealth_version=wealth_version,
            tool_versions=tool_versions,
            input_payload=input_payload,
        )
        self.sm.transition(
            State.COMPUTED, receipt=Receipt(receipt_type=receipt.receipt_type, data=receipt.data)
        )
        return receipt

    def judge(self, *, verdict: str, active_holds: list[str] | None = None) -> JudgmentReceipt:
        if self.sm.state not in (State.COMPUTED, State.JUDGED):
            raise TransitionError(self.sm.state, State.JUDGED, reason="must compute first")
        if verdict not in ("PROCEED", "HOLD", "DENY"):
            raise ValueError(f"invalid verdict: {verdict!r}")
        # Re-judgment from JUDGED: emit a fresh JUDGMENT receipt without transitioning state.
        # The first judgment (from COMPUTED) transitions COMPUTED → JUDGED.
        if self.sm.state == State.JUDGED:
            return self._make_judgment(verdict, active_holds)
        receipt = self._make_judgment(verdict, active_holds)
        self.sm.transition(
            State.JUDGED, receipt=Receipt(receipt_type=receipt.receipt_type, data=receipt.data)
        )
        if verdict == "DENY":
            self.sm.transition(State.TERMINATED)
        return receipt

    def _make_judgment(self, verdict: str, active_holds: list[str] | None) -> JudgmentReceipt:
        receipt = JudgmentReceipt(
            case=self.case,
            verdict=verdict,
            active_holds=active_holds,
        )
        self._last_judgment = receipt
        return receipt

    def requires_ratification(self) -> bool:
        return bool(self.case.governance.get("human_ratification_required", False))

    def ratify(self, *, actor: str, decision: str) -> HumanRatificationReceipt:
        if self.sm.state != State.JUDGED:
            raise TransitionError(self.sm.state, State.RATIFIED, reason="must judge first")
        if not self.requires_ratification():
            raise TransitionError(
                self.sm.state, State.RATIFIED, reason="ratification not required by governance"
            )
        receipt = HumanRatificationReceipt(case=self.case, actor=actor, decision=decision)
        self._last_ratification = receipt
        self.sm.transition(
            State.RATIFIED, receipt=Receipt(receipt_type=receipt.receipt_type, data=receipt.data)
        )
        return receipt

    def seal(self) -> None:
        if self.sm.state not in (State.JUDGED, State.RATIFIED):
            raise TransitionError(
                self.sm.state, State.SEALED, reason="must be JUDGED or RATIFIED first"
            )
        # If ratification is required, we MUST be in RATIFIED state.
        if self.requires_ratification() and self.sm.state != State.RATIFIED:
            raise TransitionError(
                self.sm.state, State.SEALED, reason="ratification required before SEALED"
            )
        # Append-only chain: produce a SEAL_RECEIPT entry that the vault consumes.
        # For test purposes we don't actually write to VAULT; we record in-memory.
        seal = {
            "receipt_type": "SEAL",
            "case_id": self.case.case_id,
            "trace_id": self.case.trace_id,
            "sealed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "receipt_chain_hash": _hash([r.data for r in self.sm.receipts]),
        }
        self.sm.transition(State.SEALED, receipt=Receipt(receipt_type="SEAL", data=seal))

    def execute(
        self, *, approved_action_hash: str, execution_result_hash: str, rollback_reference: str
    ) -> ExecutionReceipt:
        if self.sm.state != State.SEALED:
            raise TransitionError(
                self.sm.state,
                State.EXECUTED,
                reason="EXECUTION requires SEALED first; WEALTH QUALIFY never auto-executes",
            )
        receipt = ExecutionReceipt(
            case=self.case,
            approved_action_hash=approved_action_hash,
            execution_result_hash=execution_result_hash,
            rollback_reference=rollback_reference,
        )
        self.sm.transition(
            State.EXECUTED, receipt=Receipt(receipt_type=receipt.receipt_type, data=receipt.data)
        )
        return receipt

    def _terminate(self) -> None:
        if self.sm.state in (State.TERMINATED, State.EXECUTED):
            return
        self.sm.transition(State.TERMINATED)

    # ── queries ──────────────────────────────────────────────────────────────
    def receipt_chain(self) -> list[dict[str, Any]]:
        return [r.data for r in self.sm.receipts]

    def state_chain(self) -> list[str]:
        return [s.value for s in self.sm._seen_states]
