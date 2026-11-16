"""The governance kernel: one bounded decision pipeline.

propose() runs: capability gate -> lease check -> independent judgment ->
receipt -> execute | handover | stop. Every step lands on the ledger.
"""

from dataclasses import dataclass

from .authority import SpeechAct, Tier, require_grant
from .capability import Capability, CapabilityGate
from .handover import HandoverRequest, HumanSovereign
from .judgment import Judge, complete
from .receipts import ReceiptLedger


@dataclass(frozen=True)
class DriveAction:
    name: str
    tier: Tier
    target: str
    explain: str = ""


class AVGovernanceKernel:
    def __init__(self, judge_name: str = "outer-witness",
                 sovereign_name: str = "operator"):
        self.gate = CapabilityGate()
        self.judge = Judge(judge_name)
        self.sovereign = HumanSovereign(sovereign_name)
        self.ledger = ReceiptLedger()

    def propose(self, action: DriveAction, cap: Capability, act: SpeechAct,
                grants=(), evidence=(), falsifier=None) -> dict:
        gv = self.gate.check(cap)
        self.ledger.append("capability_check",
                           {"action": action.name, "allowed": gv.allowed,
                            "reason": gv.reason})
        if not gv.allowed:
            return self._stop(action, gv.reason)

        if not require_grant(act, action.tier, action.target, grants):
            return self._stop(action, "bare speech-act is not a lease")

        self.ledger.append("authority_check",
                           {"action": action.name, "tier": action.tier.value,
                            "act": act.value})

        verdict = self.judge.verify(action.name, list(evidence), falsifier)
        self.ledger.append("judgment",
                           {"action": action.name, "verdict": verdict.value})
        if not complete(verdict):
            return self._handover(action)

        self.ledger.append("execute", {"action": action.name})
        return {"status": "executed", "action": action.name}

    def _stop(self, action: DriveAction, reason: str) -> dict:
        self.ledger.append("stop", {"action": action.name, "reason": reason})
        return {"status": "stopped", "action": action.name, "reason": reason}

    def _handover(self, action: DriveAction) -> dict:
        req = HandoverRequest(
            situation=action.name,
            options=("proceed", "hold", "abort"),
            urgency_s=3,
            explained=bool(action.explain),
            recommendation="hold" if not action.explain else "proceed with care",
        )
        self.ledger.append("handover", {"action": action.name})
        return {"status": "handover", "action": action.name, "request": req}
