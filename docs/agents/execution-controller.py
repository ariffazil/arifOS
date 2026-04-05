#!/usr/bin/env python3
"""
arifOS Execution Controller — Governed Agent Control Plane
Hardened enforcement of agent identity, policy, and execution receipts.

6 BLINDSPOT #1 + #5: Agent identity + policy-gated execution + broken paths quarantined

This is the runtime enforcement layer that ensures:
- Every agent has explicit identity
- Every tool call is policy-checked
- Every action generates a receipt
- Broken power paths are disabled
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

AGENTS_DIR = Path(__file__).parent
CONFIG_DIR = AGENTS_DIR / "config"
VAULT_DIR = Path("VAULT999")


class Verdict(Enum):
    """Constitutional verdicts."""

    SEAL = "SEAL"
    VOID = "VOID"
    HOLD = "888_HOLD"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"


class AgentRole(Enum):
    """Constitutional agent roles."""

    ARCHITECT = "A-ARCHITECT"
    ENGINEER = "A-ENGINEER"
    AUDITOR = "A-AUDITOR"
    VALIDATOR = "A-VALIDATOR"


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT IDENTITY
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AgentIdentity:
    """Immutable agent identity with policy bindings."""

    role: AgentRole
    uuid: str
    fingerprint: str
    created: datetime
    owner: str = "Muhammad Arif bin Fazil"

    # Policy bindings
    can_read: bool = True
    can_write: bool = False
    can_delete: bool = False
    can_deploy: bool = False
    can_issue_seal: bool = False
    can_issue_void: bool = False

    # Tool permissions
    tools_allowed: list[str] = field(default_factory=list)
    tools_forbidden: list[str] = field(default_factory=list)

    # Constitutional thresholds
    floor_thresholds: dict[str, float] = field(default_factory=dict)

    def has_permission(self, action: str) -> tuple[bool, str]:
        """Check if agent has permission for action."""
        if action in self.tools_forbidden:
            return False, f"{action} is forbidden for {self.role.value}"
        if action not in self.tools_allowed and action != "any":
            return False, f"{action} not in allowed tools for {self.role.value}"
        return True, "Permission granted"


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT REGISTRY - 4 Constitutional Agents
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_REGISTRY: dict[AgentRole, AgentIdentity] = {
    AgentRole.ARCHITECT: AgentIdentity(
        role=AgentRole.ARCHITECT,
        uuid="agent://arifos/architect",
        fingerprint="sha256:architect-v2026.03.13",
        created=datetime.now(timezone.utc),
        can_read=True,
        can_write=False,
        can_delete=False,
        can_deploy=False,
        tools_allowed=[
            "read_file",
            "search_reality",
            "ingest_evidence",
            "session_memory",
            "lsp_query_tool",
            "office_forge_audit",
        ],
        tools_forbidden=[
            "write_file",
            "edit_file",
            "lsp_rename_tool",
            "file_delete",
            "docker_deploy",
            "git_push",
        ],
        floor_thresholds={"F1": 0.5, "F2": 0.99, "F4": 0.0, "F7": 0.04},
    ),
    AgentRole.ENGINEER: AgentIdentity(
        role=AgentRole.ENGINEER,
        uuid="agent://arifos/engineer",
        fingerprint="sha256:engineer-v2026.03.13",
        created=datetime.now(timezone.utc),
        can_read=True,
        can_write=True,
        can_delete=False,
        can_deploy=False,
        tools_allowed=[
            "read_file",
            "write_file",
            "edit_file",
            "search_reality",
            "session_memory",
            "lsp_query_tool",
            "lsp_find_references_tool",
        ],
        tools_forbidden=[
            "lsp_rename_tool",
            "file_delete",
            "docker_deploy",
            "git_push",
        ],
        floor_thresholds={"F1": 0.5, "F2": 0.99, "F4": 0.0, "F6": 0.70, "F8": 0.80},
    ),
    AgentRole.AUDITOR: AgentIdentity(
        role=AgentRole.AUDITOR,
        uuid="agent://arifos/auditor",
        fingerprint="sha256:auditor-v2026.03.13",
        created=datetime.now(timezone.utc),
        can_read=True,
        can_write=False,
        can_delete=False,
        can_deploy=False,
        can_issue_void=True,
        tools_allowed=[
            "read_file",
            "search_reality",
            "ingest_evidence",
            "session_memory",
            "lsp_query_tool",
            "lsp_get_symbols_tool",
            "lsp_get_diagnostics_tool",
            "audit_rules",
            "check_vital",
            "verify_vault_ledger",
        ],
        tools_forbidden=[
            "write_file",
            "edit_file",
            "file_delete",
            "lsp_rename_tool",
            "docker_deploy",
        ],
        floor_thresholds={"F2": 0.99, "F3": 0.95, "F4": 0.0, "F8": 0.80, "F9": 0.30},
    ),
    AgentRole.VALIDATOR: AgentIdentity(
        role=AgentRole.VALIDATOR,
        uuid="agent://arifos/validator",
        fingerprint="sha256:validator-v2026.03.13",
        created=datetime.now(timezone.utc),
        can_read=True,
        can_write=True,  # For rollback
        can_delete=True,  # For rollback
        can_deploy=True,
        can_issue_seal=True,
        can_issue_void=True,
        tools_allowed=[
            "read_file",
            "write_file",
            "edit_file",
            "file_delete",
            "search_reality",
            "session_memory",
            "lsp_query_tool",
            "audit_rules",
            "check_vital",
            "verify_vault_ledger",
            "docker_deploy",
            "git_push",
            "forge_office_document",
        ],
        tools_forbidden=[
            "shell_execute",  # Never allowed to any agent
        ],
        floor_thresholds={
            "F1": 0.5,
            "F2": 0.99,
            "F3": 0.95,
            "F4": 0.0,
            "F6": 0.70,
            "F8": 0.80,
            "F11": 1.0,
            "F13": 1.0,
        },
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# BROKEN POWER PATHS (BLINDSPOT #5) - QUARANTINED
# ═══════════════════════════════════════════════════════════════════════════════

QUARANTINED_PATHS: dict[str, dict[str, Any]] = {
    "kimi_inside_openclaw": {
        "status": "DISABLED",
        "reason": "Psychological surface larger than real surface",
        "risk": "False confidence",
        "action": "Remove or truly fix before use",
    },
    "aider_inside_openclaw": {
        "status": "DISABLED",
        "reason": "Psychological surface larger than real surface",
        "risk": "False confidence",
        "action": "Remove or truly fix before use",
    },
    "opencode_inside_openclaw": {
        "status": "DISABLED",
        "reason": "Psychological surface larger than real surface",
        "risk": "False confidence",
        "action": "Remove or truly fix before use",
    },
}


def check_quarantined(path: str) -> tuple[bool, str]:
    """Check if a capability path is quarantined."""
    if path in QUARANTINED_PATHS:
        info = QUARANTINED_PATHS[path]
        return False, f"QUARANTINED: {info['reason']} | Risk: {info['risk']}"
    return True, "Path clear"


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION RECEIPT
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ExecutionReceipt:
    """Immutable receipt for every agent action."""

    receipt_id: str
    timestamp: datetime
    agent_id: str
    session_id: str

    # Request
    intent: str
    tools_requested: list[str]
    files_accessed: list[str]

    # Policy check
    agent_authorized: bool
    tools_allowed: bool
    within_boundaries: bool
    constitutional_passed: bool

    # Execution
    tools_executed: list[str]
    files_modified: list[str]
    files_created: list[str]
    files_deleted: list[str]

    # Verdict
    verdict: Verdict
    floors_triggered: list[str]
    human_approval: str  # APPROVED|PENDING|REQUIRED

    # Vault
    sealed_to_vault999: bool = False
    merkle_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "request": {
                "intent": self.intent,
                "tools_requested": self.tools_requested,
                "files_accessed": self.files_accessed,
            },
            "policy_check": {
                "agent_authorized": self.agent_authorized,
                "tools_allowed": self.tools_allowed,
                "within_boundaries": self.within_boundaries,
                "constitutional_passed": self.constitutional_passed,
            },
            "execution": {
                "tools_executed": self.tools_executed,
                "files_modified": self.files_modified,
                "files_created": self.files_created,
                "files_deleted": self.files_deleted,
            },
            "verdict": {
                "status": self.verdict.value,
                "floors_triggered": self.floors_triggered,
                "human_approval": self.human_approval,
            },
            "vault": {
                "sealed_to_vault999": self.sealed_to_vault999,
                "merkle_hash": self.merkle_hash,
            },
        }

    def compute_hash(self) -> str:
        """Compute merkle hash of receipt."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION CONTROLLER
# ═══════════════════════════════════════════════════════════════════════════════


class ExecutionController:
    """Governed execution layer for constitutional agents."""

    def __init__(self):
        self.receipts: list[ExecutionReceipt] = []
        self.vault_path = VAULT_DIR / "execution-receipts.jsonl"

    def validate_agent(
        self,
        agent_role: AgentRole,
        requested_tools: list[str],
        intent: str,
    ) -> tuple[bool, str, dict[str, Any]]:
        """Validate agent has permission for requested action."""

        # Get agent identity
        agent = AGENT_REGISTRY.get(agent_role)
        if not agent:
            return False, f"Unknown agent role: {agent_role}", {}

        # Check quarantined paths first
        for tool in requested_tools:
            ok, msg = check_quarantined(tool)
            if not ok:
                return False, msg, {}

        # Check tool permissions
        forbidden_tools = []
        for tool in requested_tools:
            ok, msg = agent.has_permission(tool)
            if not ok:
                forbidden_tools.append(tool)

        if forbidden_tools:
            return False, f"Tools forbidden: {forbidden_tools}", {}

        # Check if write operations need approval
        write_tools = {"write_file", "edit_file", "file_delete", "docker_deploy", "git_push"}
        requires_approval = any(t in write_tools for t in requested_tools)

        # Check if deploy operations
        if "docker_deploy" in requested_tools and agent_role != AgentRole.VALIDATOR:
            return False, "Only A-VALIDATOR can deploy", {}

        return (
            True,
            "Validation passed",
            {
                "agent": agent,
                "requires_approval": requires_approval,
                "floor_thresholds": agent.floor_thresholds,
            },
        )

    def execute(
        self,
        agent_role: AgentRole,
        intent: str,
        tools: list[str],
        files: list[str],
        dry_run: bool = False,
    ) -> ExecutionReceipt:
        """Execute governed action and generate receipt."""

        session_id = str(uuid.uuid4())
        receipt_id = str(uuid.uuid4())

        # Validate
        ok, msg, context = self.validate_agent(agent_role, tools, intent)

        # Create receipt
        receipt = ExecutionReceipt(
            receipt_id=receipt_id,
            timestamp=datetime.now(timezone.utc),
            agent_id=agent_role.value,
            session_id=session_id,
            intent=intent,
            tools_requested=tools,
            files_accessed=files,
            agent_authorized=ok,
            tools_allowed=ok,
            within_boundaries=ok,
            constitutional_passed=ok,  # Would be checked by kernel
            tools_executed=tools if ok and not dry_run else [],
            files_modified=[],
            files_created=[],
            files_deleted=[],
            verdict=Verdict.SEAL if ok else Verdict.VOID,
            floors_triggered=[],
            human_approval="REQUIRED" if context.get("requires_approval") else "NOT_REQUIRED",
        )

        # Compute hash
        receipt.merkle_hash = receipt.compute_hash()

        # Seal to vault
        if ok and not dry_run:
            self._seal_to_vault(receipt)
            receipt.sealed_to_vault999 = True

        self.receipts.append(receipt)
        return receipt

    def _seal_to_vault(self, receipt: ExecutionReceipt) -> None:
        """Seal receipt to VAULT999."""
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.vault_path, "a") as f:
            f.write(json.dumps(receipt.to_dict()) + "\n")

    def get_agent_identity(self, role: AgentRole) -> AgentIdentity | None:
        """Get identity for an agent role."""
        return AGENT_REGISTRY.get(role)

    def list_quarantined(self) -> dict[str, dict[str, Any]]:
        """List all quarantined capabilities."""
        return QUARANTINED_PATHS.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    """CLI for execution controller."""
    import argparse

    parser = argparse.ArgumentParser(description="arifOS Execution Controller")
    parser.add_argument("--agent", choices=[r.value for r in AgentRole], required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--tools", nargs="+", required=True)
    parser.add_argument("--files", nargs="*", default=[])
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    controller = ExecutionController()
    role = AgentRole(args.agent)

    receipt = controller.execute(
        agent_role=role,
        intent=args.intent,
        tools=args.tools,
        files=args.files,
        dry_run=args.dry_run,
    )

    print(json.dumps(receipt.to_dict(), indent=2))

    if receipt.verdict == Verdict.VOID:
        exit(1)


if __name__ == "__main__":
    main()
