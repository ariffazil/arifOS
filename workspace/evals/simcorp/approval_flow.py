#!/usr/bin/env python3
"""P1 (888 audit 2026-09-05): Scoped approval-to-execution loop — SIMULATED.

Completes the commercial circuit the HOLD scenario stops at:

  Agent proposal → Governance HOLD → Scoped human approval item
  → Approver view (customer/amount/destination/evidence/policy limit/
    expiry/action digest) → Approve/Reject → SAME payload digest
  executed EXACTLY ONCE → linked receipt chain (hold→approval→execution)

Honesty markers (auditor's 888 HOLD #2):
  - execution adapter is SIMULATED — no real money moves, no real API called
  - replay of an approved digest is rejected (once-only semantics)
  - approval expiry enforced (expired approval ≠ authority)

Run: python3 approval_flow.py   (deterministic; prints the full loop)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)
POLICY = {"policy_id": "refunds-v1", "auto_ceiling_myr": 100.0, "approver_role": "finance.supervisor"}


def _h(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


@dataclass
class ApprovalItem:
    item_id: str
    hold_receipt_id: str
    action: str
    payload: dict            # the EXACT proposed action — digest binds this
    payload_digest: str
    policy_id: str
    policy_limit_myr: float
    approver_role: str
    evidence: list
    expires_at: str
    status: str = "PENDING"  # PENDING → APPROVED/REJECTED/EXPIRED/CONSUMED
    decided_by: str | None = None
    decided_at: str | None = None


@dataclass
class ExecutionReceipt:
    execution_id: str
    approval_item_id: str
    payload_digest: str
    executed_at: str
    adapter: str
    result: str
    linked_hold_receipt: str
    chain_hash: str


class ApprovalLedger:
    """Once-only scoped execution: digest consumed on use; expiry enforced."""

    def __init__(self):
        self.items: dict[str, ApprovalItem] = {}
        self.executions: list[ExecutionReceipt] = []

    def create_item(self, hold_receipt_id, action, payload, evidence) -> ApprovalItem:
        digest = _h(payload)
        item = ApprovalItem(
            item_id=f"APR-{digest[:16].upper()}",
            hold_receipt_id=hold_receipt_id,
            action=action,
            payload=payload,
            payload_digest=digest,
            policy_id=POLICY["policy_id"],
            policy_limit_myr=POLICY["auto_ceiling_myr"],
            approver_role=POLICY["approver_role"],
            evidence=evidence,
            expires_at=(NOW + timedelta(minutes=15)).isoformat(),
        )
        self.items[item.item_id] = item
        return item

    def approve(self, item_id, approver: str, role: str) -> ApprovalItem:
        it = self.items[item_id]
        if datetime.now(timezone.utc) > datetime.fromisoformat(it.expires_at):
            it.status = "EXPIRED"
            raise PermissionError("approval expired — human authority lapsed")
        if role != it.approver_role:
            raise PermissionError(f"wrong approver role: {role} ≠ {it.approver_role}")
        it.status, it.decided_by, it.decided_at = "APPROVED", approver, datetime.now(timezone.utc).isoformat()
        return it

    def execute(self, item_id, payload) -> ExecutionReceipt:
        it = self.items[item_id]
        if it.status != "APPROVED":
            raise PermissionError(f"cannot execute: item status={it.status}")
        digest = _h(payload)
        if digest != it.payload_digest:
            raise PermissionError("payload digest mismatch — approved EXACT action only")
        if it.status == "CONSUMED":
            raise PermissionError("digest already consumed — one-time authority")
        it.status = "CONSUMED"  # once-only
        r = ExecutionReceipt(
            execution_id=f"EXEC-{digest[:12].upper()}",
            approval_item_id=item_id,
            payload_digest=digest,
            executed_at=datetime.now(timezone.utc).isoformat(),
            adapter="SIMULATED.enterprise.billing.issue_refund",
            result="SUCCESS (simulated) — RM5,000.00 refund issued to ACCOUNT-8842",
            linked_hold_receipt=it.hold_receipt_id,
            chain_hash=_h({"hold": it.hold_receipt_id, "approval": asdict(it), "digest": digest}),
        )
        self.executions.append(r)
        return r


def main():
    print("═" * 72)
    print("SIMULATED WORKFLOW · policy refunds-v1 · demo/eval only — no real funds move")
    print("═" * 72)

    # 1. Agent proposal (from FI-003 demo scenario #3 — HOLD receipt)
    payload = {"customer": "CUST-1024", "action": "issue_refund",
               "amount_myr": 5000.00, "destination": "ACCOUNT-8842", "reason": "SLA breach comp"}
    hold = "RCPT-78A8C94D39AD484F"  # live demo receipt: RM5,000 > RM100 ceiling → HOLD
    print(f"\n[1] Agent proposes: refund RM{payload['amount_myr']:,.2f} → {payload['destination']}")
    print(f"[2] arifOS: RM5,000 exceeds policy ceiling RM{POLICY['auto_ceiling_myr']:,.0f} → HOLD ({hold})")

    ledger = ApprovalLedger()
    item = ledger.create_item(hold, "enterprise.billing.issue_refund", payload,
                              evidence=[hold, "SLA-breach ticket #4471", "customer tenure 3y"])
    print(f"\n[3] Scoped approval item created → {item.item_id}")
    print("    ┌─ APPROVER VIEW ───────────────────────────────────────────")
    for k in ("action", "policy_limit_myr", "approver_role", "expires_at"):
        print(f"    │ {k:<18}: {getattr(item, k)}")
    print(f"    │ customer          : {payload['customer']}  ({payload['reason']})")
    print(f"    │ amount / dest     : RM{payload['amount_myr']:,.2f} → {payload['destination']}")
    print(f"    │ action digest     : {item.payload_digest[:32]}…")
    print(f"    │ evidence          : {len(item.evidence)} items linked")
    print("    └────────────────────────────────────────────────────────────")

    # wrong-role attempt
    print("\n[4] Wrong approver (role=intern) →", end=" ")
    try:
        ledger.approve(item.item_id, "intern-x", "intern")
    except PermissionError as e:
        print(f"REJECTED ✓ ({e})")

    print("[5] Designated supervisor approves →", end=" ")
    ledger.approve(item.item_id, "Siti (finance.supervisor)", "finance.supervisor")
    print("APPROVED ✓")

    print("[6] Tampered payload FIRST (RM50,000 swap on approved digest) →", end=" ")
    try:
        ledger.execute(item.item_id, {**payload, "amount_myr": 50000})
    except PermissionError as e:
        print(f"REJECTED ✓ ({e})")

    print("[7] Execute with SAME payload digest →", end=" ")
    r = ledger.execute(item.item_id, payload)
    print(f"EXECUTED ONCE ✓ ({r.execution_id}, adapter={r.adapter})")

    print("[8] Replay attempt (same digest again) →", end=" ")
    try:
        ledger.execute(item.item_id, payload)
    except PermissionError as e:
        print(f"REJECTED ✓ ({e})")

    print(f"\n[9] Final linked receipt: hold {r.linked_hold_receipt[:20]}… → approval {r.approval_item_id} → exec {r.execution_id}")
    print(f"    chain_hash: {r.chain_hash[:32]}…")
    out = {"badges": ["DEMO / SIMULATED WORKFLOW", f"policy {POLICY['policy_id']}",
                      "evidence: linked receipt chain"],
           "approval_item": asdict(item), "execution": asdict(r)}
    print("\n" + "═" * 72)
    print("LOOP COMPLETE: proposal → HOLD → scoped human approval → digest-bound")
    print("once-only execution → linked receipt. Bounded authority, zero real funds.")
    return out


if __name__ == "__main__":
    main()
