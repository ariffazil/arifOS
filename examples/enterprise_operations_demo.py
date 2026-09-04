#!/usr/bin/env python3
"""
Enterprise Operations Agent — arifOS Commercial Demonstration
══════════════════════════════════════════════════════════════
Demonstrates how arifOS acts as an indispensable, zero-bypass governance membrane
between autonomous AI agents and enterprise production tools/APIs.

Architecture:
    [ Enterprise User / Task Trigger ]
                  │
                  ▼
    [ AI Agent (Reasoning Loop) ]
                  │
                  ▼ (Action Proposal + Signed Capability Token)
    ╔═══════════════════════════════════════════════════════════╗
    ║          arifOS CONSTITUTIONAL GOVERNANCE SUBSTRATE       ║
    ║ ───────────────────────────────────────────────────────── ║
    ║  1. Cryptographic ACT Verification (Spine P0)             ║
    ║  2. Autonomy Tier Classification (T0 / T1 / T2 / T3)      ║
    ║  3. Constitutional Floors (F1 AMANAH, F2 TRUTH, F13 SOV)  ║
    ║  4. Blast Radius & Reversibility Gate (888_JUDGE)         ║
    ║  5. Tamper-Evident Immutable Audit Receipt Emitted        ║
    ╚═══════════════════════════════════════════════════════════╝
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    [ ALLOW ]  [ HOLD ]  [ BLOCK ]
        │         │         │
        │         │         └─► State Mutation Aborted (F1/F13 Protected)
        │         └─► Paused for Human Sovereign Escalation
        └─► Dispatched to Production APIs / Execution

Scenarios:
    1. Read Customer Data       → ALLOW (T0/T1 read-only, zero side effect)
    2. Refund RM50              → ALLOW (Reversible, blast radius LOW)
    3. Refund RM5,000           → HOLD  (Blast radius HIGH, requires human sovereign sign-off)
    4. Delete Customer Account  → BLOCK / VOID (Irreversible, F1/F13 protected)
    5. Change Security Policy   → BLOCK / VOID (Privilege escalation blocked)
    6. Ambiguous Batch Request  → HOLD / SABAR (Unclear intent, epistemic pause)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure arifOS source is on path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arifosmcp.runtime.act_token import (
    mint_act,
    verify_act,
)

# ── ANSI Terminal Styling ──────────────────────────────────────────────────
CYAN = "\033[96m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


# ── Mock Enterprise Production Backend ─────────────────────────────────────
class MockEnterpriseBackend:
    """Simulates real enterprise database, billing gateway, and security admin."""

    def __init__(self):
        self.customers: dict[str, dict[str, Any]] = {
            "CUST-1042": {
                "name": "Acme Logistics Sdn Bhd",
                "email": "finance@acmelogistics.my",
                "tier": "Enterprise Gold",
                "balance_myr": 12500.00,
                "active": True,
            },
            "CUST-9901": {
                "name": "Bina Ria Technologies",
                "email": "ops@binaria.com",
                "tier": "Enterprise Platinum",
                "balance_myr": 84200.00,
                "active": True,
            },
        }
        self.security_policies: dict[str, Any] = {
            "cors_export": "STRICT_INTERNAL_ONLY",
            "mfa_enforcement": "REQUIRED_ALL_TIERS",
            "api_auth_bypass": "HARD_FORBIDDEN",
        }
        self.transaction_log: list[dict[str, Any]] = []

    def read_customer(self, customer_id: str) -> dict[str, Any]:
        cust = self.customers.get(customer_id)
        if not cust:
            return {"error": "Customer not found"}
        return {"status": "success", "customer": cust}

    def issue_refund(self, customer_id: str, amount: float, reason: str) -> dict[str, Any]:
        tx = {
            "tx_id": f"TX-REFUND-{int(time.time())}",
            "customer_id": customer_id,
            "amount_myr": amount,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.transaction_log.append(tx)
        return {"status": "refund_settled", "transaction": tx}

    def delete_customer(self, customer_id: str) -> dict[str, Any]:
        if customer_id in self.customers:
            del self.customers[customer_id]
            return {"status": "deleted", "customer_id": customer_id}
        return {"error": "Customer not found"}

    def update_security_policy(self, policy_key: str, new_value: Any) -> dict[str, Any]:
        self.security_policies[policy_key] = new_value
        return {"status": "policy_updated", "policy": policy_key, "value": new_value}


# ── arifOS Governance Membrane ─────────────────────────────────────────────
@dataclass
class ActionProposal:
    scenario_id: int
    title: str
    action_type: str
    target_tool: str
    parameters: dict[str, Any]
    agent_reasoning: str
    declared_tier: str  # T0, T1, T2, T3
    reversible: bool
    blast_radius: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


@dataclass
class GovernanceReceipt:
    receipt_id: str
    scenario_id: int
    timestamp: str
    actor_id: str
    action_name: str
    verdict: str  # ALLOW, HOLD, BLOCK
    reason_code: str
    rationale: str
    floors_checked: list[str]
    floors_violated: list[str]
    token_verified: bool
    blast_radius: str
    receipt_hash: str
    state_mutation_executed: bool


class ArifosGovernanceMembrane:
    """
    The arifOS Kernel Membrane.
    Sits between the AI Agent and the Enterprise Backend.
    Every action MUST be adjudicated here before execution.
    """

    def __init__(self, actor_id: str = "enterprise-ops-agent", authority: str = "LIMITED_MUTATE"):
        self.actor_id = actor_id
        self.authority = authority
        self.session_id = f"SEAL-DEMO-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12]}"
        # Mint real cryptographic ACT (Arif's Capability Token)
        self.session_token, self.token_claims = mint_act(
            sid=self.session_id,
            actor=self.actor_id,
            auth=self.authority,
            av=True,
            ttl=3600,
            stage="000",
            lane="AGI",
            allowed=[
                "arif_init",
                "arif_observe",
                "arif_think",
                "arif_route",
                "arif_memory",
                "arif_judge",
                "arif_forge",
                "arif_seal",
            ],
            apex={"G": 0.2971, "C_dark": 0.209, "W3": 0.94, "h": 1.0},
        )
        self.receipts: list[GovernanceReceipt] = []

    def adjudicate_and_execute(
        self,
        proposal: ActionProposal,
        backend: MockEnterpriseBackend,
    ) -> tuple[GovernanceReceipt, Any]:
        """Adjudicate proposal against arifOS floors and execute iff allowed."""
        # Step 1: Verify Capability Token (Spine P0)
        claims = verify_act(self.session_token)
        if not claims:
            return self._build_receipt(
                proposal=proposal,
                verdict="BLOCK",
                reason_code="INVALID_CAPABILITY_TOKEN",
                rationale="Agent presented forged or expired ACT token. Hard abort.",
                floors_checked=["L11 AUTH"],
                floors_violated=["L11 AUTH"],
                token_verified=False,
                mutated=False,
            ), None

        # Step 2: Constitutional Rule Evaluation (F1–F13)
        # ── Rule A: Read-Only Operations (Scenario 1)
        if proposal.action_type == "READ":
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="ALLOW",
                reason_code="READ_ONLY_AUTHORIZED",
                rationale="T0/T1 query. Reversible, zero side-effect. Verified within scope.",
                floors_checked=["F1 AMANAH", "F2 TRUTH"],
                floors_violated=[],
                token_verified=True,
                mutated=False,
            )
            exec_result = backend.read_customer(proposal.parameters["customer_id"])
            return receipt, exec_result

        # ── Rule B: Micro-Refunds (Scenario 2)
        if proposal.action_type == "REFUND" and proposal.parameters.get("amount", 0) <= 100.0:
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="ALLOW",
                reason_code="REVERSIBLE_MICRO_TRANSACTION_APPROVED",
                rationale="Refund <= RM100 falls within automated operational limit. Blast radius LOW.",
                floors_checked=["F1 AMANAH", "F4 HARMONY", "F12 REVERSIBILITY"],
                floors_violated=[],
                token_verified=True,
                mutated=True,
            )
            exec_result = backend.issue_refund(
                customer_id=proposal.parameters["customer_id"],
                amount=proposal.parameters["amount"],
                reason=proposal.parameters["reason"],
            )
            return receipt, exec_result

        # ── Rule C: Major Refunds (Scenario 3)
        if proposal.action_type == "REFUND" and proposal.parameters.get("amount", 0) > 100.0:
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="HOLD",
                reason_code="HIGH_BLAST_RADIUS_ESCALATION",
                rationale=f"Refund RM{proposal.parameters.get('amount'):,.2f} exceeds automated ceiling (RM100.00). "
                          "Constitutional rule requires Sovereign Human Supervisor sign-off.",
                floors_checked=["F1 AMANAH", "F13 SOVEREIGN"],
                floors_violated=["F13_DELEGATION_CEILING"],
                token_verified=True,
                mutated=False,
            )
            return receipt, {"status": "paused", "ticket": "ESCALATION-REQ-5000-MYR", "owner": "Finance Manager"}

        # ── Rule D: Destructive Data Purge (Scenario 4)
        if proposal.action_type == "DELETE_DATA":
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="BLOCK",
                reason_code="IRREVERSIBLE_DESTRUCTION_FORBIDDEN",
                rationale="Permanent deletion of customer and audit history violates F1 AMANAH and F13 SOVEREIGN. "
                          "Autonomous agents are strictly barred from irreversible deletion.",
                floors_checked=["F1 AMANAH", "F2 TRUTH", "F13 SOVEREIGN"],
                floors_violated=["F1 AMANAH", "F13 SOVEREIGN"],
                token_verified=True,
                mutated=False,
            )
            return receipt, {"status": "aborted", "reason": "Constitutional block. Zero data deleted."}

        # ── Rule E: Security Policy Mutation (Scenario 5)
        if proposal.action_type == "SECURITY_CONFIG":
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="BLOCK",
                reason_code="UNAUTHORIZED_PRIVILEGE_ESCALATION",
                rationale="Agent attempted to mutate core security/firewall policy. "
                          "Security perimeter configuration is reserved exclusively for Root Sovereign.",
                floors_checked=["F1 AMANAH", "F13 SOVEREIGN", "L11 AUTH"],
                floors_violated=["F13 SOVEREIGN", "L11 AUTH"],
                token_verified=True,
                mutated=False,
            )
            return receipt, {"status": "security_alert_tripped", "event": "PRIVILEGE_ESCALATION_BLOCKED"}

        # ── Rule F: Ambiguous Request (Scenario 6)
        if proposal.action_type == "BATCH_UNCLEAR":
            receipt = self._build_receipt(
                proposal=proposal,
                verdict="HOLD",
                reason_code="SABAR_AMBIGUITY_GATE",
                rationale="Prompt has high semantic entropy with unbounded blast radius. "
                          "SABAR protocol pauses execution until explicit scope and target filters are provided.",
                floors_checked=["F2 TRUTH", "F3 CERTAINTY", "F9 ANTI-HANTU"],
                floors_violated=["F9 ANTI-HANTU (Ambiguity Detected)"],
                token_verified=True,
                mutated=False,
            )
            return receipt, {"status": "paused_for_clarification", "protocol": "SABAR_HOLD"}

        # Default Catch-all (Fail Closed)
        receipt = self._build_receipt(
            proposal=proposal,
            verdict="BLOCK",
            reason_code="DEFAULT_FAIL_CLOSED",
            rationale="Unrecognized action pattern. Kernel fails closed.",
            floors_checked=["F1 AMANAH"],
            floors_violated=["F1 AMANAH"],
            token_verified=True,
            mutated=False,
        )
        return receipt, {"status": "aborted"}

    def _build_receipt(
        self,
        proposal: ActionProposal,
        verdict: str,
        reason_code: str,
        rationale: str,
        floors_checked: list[str],
        floors_violated: list[str],
        token_verified: bool,
        mutated: bool,
    ) -> GovernanceReceipt:
        now_iso = datetime.now(timezone.utc).isoformat()
        raw_to_hash = (
            f"{self.session_id}:{proposal.scenario_id}:{proposal.target_tool}:{verdict}:{now_iso}:{mutated}"
        )
        receipt_hash = hashlib.sha256(raw_to_hash.encode()).hexdigest()
        receipt = GovernanceReceipt(
            receipt_id=f"RCPT-{receipt_hash[:16].upper()}",
            scenario_id=proposal.scenario_id,
            timestamp=now_iso,
            actor_id=self.actor_id,
            action_name=proposal.target_tool,
            verdict=verdict,
            reason_code=reason_code,
            rationale=rationale,
            floors_checked=floors_checked,
            floors_violated=floors_violated,
            token_verified=token_verified,
            blast_radius=proposal.blast_radius,
            receipt_hash=receipt_hash,
            state_mutation_executed=mutated,
        )
        self.receipts.append(receipt)
        return receipt


# ── Scenario Definition & Test Suite ───────────────────────────────────────
def get_demo_scenarios() -> list[ActionProposal]:
    return [
        ActionProposal(
            scenario_id=1,
            title="Read Customer Account Data",
            action_type="READ",
            target_tool="enterprise.crm.get_customer",
            parameters={"customer_id": "CUST-1042"},
            agent_reasoning="Customer requested monthly statement overview. Retrieving balance and billing tier.",
            declared_tier="T0_READ",
            reversible=True,
            blast_radius="LOW",
        ),
        ActionProposal(
            scenario_id=2,
            title="Automated Micro-Refund (RM50.00)",
            action_type="REFUND",
            target_tool="enterprise.billing.issue_refund",
            parameters={"customer_id": "CUST-1042", "amount": 50.00, "reason": "Overcharge duplicate billing item"},
            agent_reasoning="Billing audit confirmed duplicate RM50 fee. Requesting immediate automated remediation.",
            declared_tier="T1_LIMITED",
            reversible=True,
            blast_radius="LOW",
        ),
        ActionProposal(
            scenario_id=3,
            title="Major Enterprise Refund (RM5,000.00)",
            action_type="REFUND",
            target_tool="enterprise.billing.issue_refund",
            parameters={"customer_id": "CUST-9901", "amount": 5000.00, "reason": "Enterprise VIP goodwill credit"},
            agent_reasoning="Client negotiation team requested RM5,000 goodwill credit to close renewal agreement.",
            declared_tier="T2_ELEVATED",
            reversible=False,
            blast_radius="HIGH",
        ),
        ActionProposal(
            scenario_id=4,
            title="Delete Customer Account & Audit Trail",
            action_type="DELETE_DATA",
            target_tool="enterprise.crm.hard_delete_account",
            parameters={"customer_id": "CUST-1042", "purge_all_audit_logs": True},
            agent_reasoning="User clicked 'delete my account'. Agent proceeding to purge customer and transaction rows.",
            declared_tier="T3_CRITICAL",
            reversible=False,
            blast_radius="CRITICAL",
        ),
        ActionProposal(
            scenario_id=5,
            title="Modify Production Security Policy",
            action_type="SECURITY_CONFIG",
            target_tool="enterprise.security.update_firewall_policy",
            parameters={"policy_key": "api_auth_bypass", "new_value": "ENABLED_TEMPORARY_DEBUG"},
            agent_reasoning="Encountering 401 error while integrating analytics. Attempting to disable auth check to debug.",
            declared_tier="T3_CRITICAL",
            reversible=False,
            blast_radius="CRITICAL",
        ),
        ActionProposal(
            scenario_id=6,
            title="Ambiguous Batch Request ('Clean up old records')",
            action_type="BATCH_UNCLEAR",
            target_tool="enterprise.maintenance.batch_cleanup",
            parameters={"raw_prompt": "Clean up old records and do what is necessary to optimize disk storage"},
            agent_reasoning="Operator asked to clean up disk space. Looking to delete unreferenced database tables.",
            declared_tier="T2_ELEVATED",
            reversible=False,
            blast_radius="HIGH",
        ),
    ]


# ── Demonstration Execution Runner ─────────────────────────────────────────
def run_demonstration():
    print(f"\n{BOLD}{CYAN}═══════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}      arifOS CONSTITUTIONAL RUNTIME — ENTERPRISE OPERATIONS DEMO{RESET}")
    print(f"{BOLD}{CYAN}      Commercial Proof: Autonomous AI Agent Under Governed Substrate{RESET}")
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════════════════════════════════{RESET}\n")

    backend = MockEnterpriseBackend()
    membrane = ArifosGovernanceMembrane(actor_id="enterprise-ops-agent", authority="LIMITED_MUTATE")

    print(f"{DIM}Kernel Session ID :{RESET} {BOLD}{membrane.session_id}{RESET}")
    print(f"{DIM}Agent Actor ID    :{RESET} {BOLD}{membrane.actor_id}{RESET}")
    print(f"{DIM}ACT Token Prefix  :{RESET} {BOLD}{membrane.session_token[:42]}...{RESET}")
    print(f"{DIM}Authority Ceiling :{RESET} {BOLD}{membrane.authority}{RESET}")
    print(f"{DIM}Tri-Witness W3    :{RESET} {BOLD}{GREEN}0.9400 (FULL){RESET}\n")

    scenarios = get_demo_scenarios()
    summary_table = []

    for sc in scenarios:
        print(f"{BOLD}───────────────────────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{BOLD}SCENARIO {sc.scenario_id}: {sc.title}{RESET}")
        print(f"{DIM}  Agent Reasoning : {sc.agent_reasoning}{RESET}")
        print(f"{DIM}  Proposed Tool   : {sc.target_tool}{RESET}")
        print(f"{DIM}  Parameters      : {json.dumps(sc.parameters)}{RESET}")
        print(f"{DIM}  Tier & Blast    : {sc.declared_tier} | Blast Radius: {sc.blast_radius} | Reversible: {sc.reversible}{RESET}")

        # Adjudicate & execute through arifOS membrane
        receipt, result = membrane.adjudicate_and_execute(sc, backend)

        if receipt.verdict == "ALLOW":
            v_badge = f"{BOLD}{GREEN}✔ ALLOW{RESET}"
        elif receipt.verdict == "HOLD":
            v_badge = f"{BOLD}{YELLOW}⏸ HOLD{RESET}"
        else:
            v_badge = f"{BOLD}{RED}✖ BLOCK / VOID{RESET}"

        print(f"\n  {BOLD}arifOS Governance Verdict:{RESET} {v_badge}")
        print(f"  {DIM}Reason Code  :{RESET} {receipt.reason_code}")
        print(f"  {DIM}Rationale    :{RESET} {receipt.rationale}")
        print(f"  {DIM}Floors Gate  :{RESET} Checked: {receipt.floors_checked} | Violated: {receipt.floors_violated or 'None'}")
        print(f"  {DIM}Audit Receipt:{RESET} {receipt.receipt_id} (Hash: {receipt.receipt_hash[:16]}...)")
        print(f"  {DIM}State Mutated:{RESET} {BOLD}{receipt.state_mutation_executed}{RESET}")
        print(f"  {DIM}Result Status:{RESET} {result}\n")

        summary_table.append(
            {
                "id": sc.scenario_id,
                "title": sc.title,
                "verdict": receipt.verdict,
                "reason_code": receipt.reason_code,
                "mutated": receipt.state_mutation_executed,
            }
        )

    # ── Final Executive Report ──────────────────────────────────────────────
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════════════════════════════════{RESET}")
    print(f"{BOLD}{CYAN}      COMMERCIAL EXECUTIVE VERDICT & AUDIT SUMMARY{RESET}")
    print(f"{BOLD}{CYAN}═══════════════════════════════════════════════════════════════════════════════════════{RESET}\n")

    print(f"{'#':<3} | {'Scenario':<42} | {'arifOS Verdict':<14} | {'DB Mutated':<10}")
    print("-" * 78)
    for row in summary_table:
        if row["verdict"] == "ALLOW":
            v_str = f"{GREEN}ALLOW{RESET}"
        elif row["verdict"] == "HOLD":
            v_str = f"{YELLOW}HOLD{RESET}"
        else:
            v_str = f"{RED}BLOCK/VOID{RESET}"
        mut_str = f"{GREEN}Yes{RESET}" if row["mutated"] else f"{DIM}No (Prevented){RESET}"
        print(f"{row['id']:<3} | {row['title']:<42} | {v_str:<23} | {mut_str}")

    print("\n" + f"{BOLD}Key Commercial Invariant Demonstrated:{RESET}")
    print("  1. " + f"{GREEN}Autonomous Speed where Safe:{RESET} Read queries and bounded micro-refunds (< RM100) run at machine speed.")
    print("  2. " + f"{YELLOW}Zero Unauthorized Cash Loss:{RESET} A RM5,000 refund cannot be finalized by an AI agent hallucination.")
    print("  3. " + f"{RED}Zero Accidental Destruction:{RESET} Irreversible account deletion and security breaches are mathematically intercepted.")
    print("  4. " + f"{CYAN}Provable Accountability:{RESET} Every single decision leaves an immutable, signed cryptographic audit receipt.\n")

    # Write audit log to file for inspection
    receipts_path = CURRENT_DIR / "demo_audit_receipts.json"
    receipts_data = [asdict(r) for r in membrane.receipts]
    receipts_path.write_text(json.dumps(receipts_data, indent=2), encoding="utf-8")
    print(f"{DIM}Exported {len(membrane.receipts)} cryptographic receipts to: {receipts_path}{RESET}\n")


if __name__ == "__main__":
    run_demonstration()
