#!/usr/bin/env python3
"""
arifOS Shadow Resolver — Step C0 (Observe-Only Evaluator)
═══════════════════════════════════════════════════════════
Calculates what WOULD be allowed/denied given current frontmatter
and capability contracts, but does NOT change what loads.

Emits decisions to a structured log without enforcing them.

This is the prerequisite for genuine runtime observation.

DITEMPA BUKAN DIBERI — observe-only, no mutations
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# === Constants ===

LOG_DIR = Path("/root/.local/share/arifos/shadow-resolver")
LOG_FILE = LOG_DIR / "decisions.jsonl"
MANIFEST_PATH = LOG_DIR / "latest-manifest.json"

# Authority levels (from authority-envelope.md)
class Authority(Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    FULL = "FULL"
    SOVEREIGN = "SOVEREIGN"

# Operation classes
class Operation(Enum):
    READ = "read"
    ANALYSE = "analyse"
    PROPOSE = "propose"
    MUTATE = "mutate"
    EXTERNAL_SEND = "external_send"

# Reversibility classes (R0-R5)
class Reversibility(Enum):
    R0 = "R0"  # Irreversible, catastrophic
    R1 = "R1"  # Irreversible, significant
    R2 = "R2"  # Reversible with cost
    R3 = "R3"  # Reversible, low cost
    R4 = "R4"  # Freely reversible
    R5 = "R5"  # No effect

# Compartments
class Compartment(Enum):
    A2H = "A2H"  # Agent ↔ Human
    A2A = "A2A"  # Agent ↔ Agent
    A2M = "A2M"  # Agent ↔ Machine

# === Data Classes ===

@dataclass
class ToolContract:
    """Capability contract for a single tool."""
    name: str
    operation: Operation
    compartment: Compartment
    reversibility: Reversibility
    requires_authority: Authority
    requires_f13: bool = False
    description: str = ""

@dataclass
class ShadowDecision:
    """A single shadow resolver decision."""
    trace_id: str
    timestamp: str
    tool_name: str
    operation: str
    compartment: str
    reversibility: str
    current_authority: str
    required_authority: str
    decision: str  # ALLOW | DENY | HOLD
    reason: str
    actor_id: str = "unknown"
    session_active: bool = False
    envelope_valid: bool = False

@dataclass
class ShadowManifest:
    """Full shadow resolver state."""
    timestamp: str
    tools_evaluated: int
    decisions: list
    authority_state: dict
    summary: dict

# === Tool Contracts (derived from kernel public registry) ===

TOOL_CONTRACTS = {
    "arif_init": ToolContract(
        name="arif_init",
        operation=Operation.READ,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R5,
        requires_authority=Authority.OBSERVE_ONLY,
        description="Session initialization and identity binding"
    ),
    "arif_observe": ToolContract(
        name="arif_observe",
        operation=Operation.READ,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R5,
        requires_authority=Authority.OBSERVE_ONLY,
        description="Read-only observation of federation state"
    ),
    "arif_think": ToolContract(
        name="arif_think",
        operation=Operation.ANALYSE,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R5,
        requires_authority=Authority.OBSERVE_ONLY,
        description="Internal reasoning and analysis"
    ),
    "arif_route": ToolContract(
        name="arif_route",
        operation=Operation.READ,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R5,
        requires_authority=Authority.OBSERVE_ONLY,
        description="Intent classification and organ routing"
    ),
    "arif_memory": ToolContract(
        name="arif_memory",
        operation=Operation.READ,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R3,
        requires_authority=Authority.LOW,
        description="Memory read/write operations"
    ),
    "arif_judge": ToolContract(
        name="arif_judge",
        operation=Operation.ANALYSE,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R3,
        requires_authority=Authority.MEDIUM,
        requires_f13=True,
        description="Constitutional judgment and verdict emission"
    ),
    "arif_forge": ToolContract(
        name="arif_forge",
        operation=Operation.MUTATE,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R3,
        requires_authority=Authority.HIGH,
        requires_f13=True,
        description="Execution gate — mutation of production state"
    ),
    "arif_seal": ToolContract(
        name="arif_seal",
        operation=Operation.MUTATE,
        compartment=Compartment.A2M,
        reversibility=Reversibility.R0,
        requires_authority=Authority.SOVEREIGN,
        requires_f13=True,
        description="Immutable seal — constitutional closure"
    ),
}

# Authority hierarchy for comparison
AUTHORITY_ORDER = {
    "OBSERVE_ONLY": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "FULL": 4,
    "SOVEREIGN": 5,
}

# === Core Resolver ===

class ShadowResolver:
    """
    Observe-only evaluator. Calculates what WOULD be allowed/denied
    given current state, without changing anything.
    """

    def __init__(self):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.session_active = False
        self.current_authority = Authority.OBSERVE_ONLY
        self.actor_id = "unknown"
        self.envelope_valid = False

    def probe_kernel_state(self) -> dict:
        """Read live kernel state via health endpoint (read-only)."""
        import urllib.request
        state = {
            "kernel_reachable": False,
            "status": "unknown",
            "tools_on_wire": 0,
            "runtime_drift": "unknown",
            "authority_scope": "unknown",
        }
        try:
            req = urllib.request.Request("http://localhost:8088/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                state["kernel_reachable"] = True
                state["status"] = data.get("status", "unknown")
                state["tools_on_wire"] = data.get("tools_registry_size", 0)
                state["runtime_drift"] = data.get("runtime_drift", {}).get("status", "unknown")
                state["authority_scope"] = data.get("authority_scope", "unknown")
        except Exception as e:
            state["error"] = str(e)
        return state

    def probe_session_state(self) -> dict:
        """Check if there's an active authenticated session (read-only)."""
        state = {
            "session_exists": False,
            "actor_verified": False,
            "authority_band": "NONE",
        }
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:8088/identity")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                state["session_exists"] = True
                state["actor_verified"] = data.get("actor_verified", False)
                state["authority_band"] = data.get("authority_band", "NONE")
        except Exception:
            pass
        return state

    def evaluate_tool(self, contract: ToolContract, kernel_state: dict, session_state: dict) -> ShadowDecision:
        """
        Evaluate a single tool against current state.
        Returns what WOULD happen — does not enforce.
        """
        trace_id = f"shadow-{int(time.time()*1000)}-{contract.name}"
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Determine current effective authority
        if session_state.get("actor_verified"):
            auth_str = session_state.get("authority_band", "OBSERVE_ONLY")
        else:
            auth_str = "OBSERVE_ONLY"

        current_level = AUTHORITY_ORDER.get(auth_str, 0)
        required_level = AUTHORITY_ORDER.get(contract.requires_authority.value, 0)

        # Decision logic
        if not kernel_state.get("kernel_reachable"):
            decision = "DENY"
            reason = "kernel_unreachable"
        elif not session_state.get("session_exists"):
            decision = "HOLD"
            reason = "no_active_session"
        elif not session_state.get("actor_verified") and contract.requires_f13:
            decision = "DENY"
            reason = "actor_unverified_requires_f13"
        elif current_level < required_level:
            decision = "DENY"
            reason = f"authority_{auth_str}_below_{contract.requires_authority.value}"
        else:
            decision = "ALLOW"
            reason = "authority_sufficient"

        return ShadowDecision(
            trace_id=trace_id,
            timestamp=timestamp,
            tool_name=contract.name,
            operation=contract.operation.value,
            compartment=contract.compartment.value,
            reversibility=contract.reversibility.value,
            current_authority=auth_str,
            required_authority=contract.requires_authority.value,
            decision=decision,
            reason=reason,
            actor_id=self.actor_id,
            session_active=self.session_active,
            envelope_valid=self.envelope_valid,
        )

    def resolve_all(self) -> ShadowManifest:
        """
        Run the shadow resolver across all tool contracts.
        Observe-only: reads state, calculates decisions, emits log.
        No mutations. No enforcement. No loading changes.
        """
        kernel_state = self.probe_kernel_state()
        session_state = self.probe_session_state()

        self.session_active = session_state.get("session_exists", False)
        self.actor_id = "unknown"  # Would be set by real session
        self.envelope_valid = session_state.get("actor_verified", False)

        decisions = []
        for name, contract in TOOL_CONTRACTS.items():
            decision = self.evaluate_tool(contract, kernel_state, session_state)
            decisions.append(asdict(decision))

        # Emit to structured log
        manifest = ShadowManifest(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            tools_evaluated=len(decisions),
            decisions=decisions,
            authority_state={
                "kernel_reachable": kernel_state.get("kernel_reachable", False),
                "session_exists": session_state.get("session_exists", False),
                "actor_verified": session_state.get("actor_verified", False),
                "authority_band": session_state.get("authority_band", "NONE"),
            },
            summary={
                "allow": sum(1 for d in decisions if d["decision"] == "ALLOW"),
                "deny": sum(1 for d in decisions if d["decision"] == "DENY"),
                "hold": sum(1 for d in decisions if d["decision"] == "HOLD"),
            }
        )

        # Write log (append-only)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(asdict(manifest)) + "\n")

        # Write latest manifest
        with open(MANIFEST_PATH, "w") as f:
            json.dump(asdict(manifest), f, indent=2)

        return manifest


def main():
    """CLI entry point for shadow resolver."""
    import sys
    resolver = ShadowResolver()
    manifest = resolver.resolve_all()

    print(f"Shadow Resolver — {manifest.tools_evaluated} tools evaluated")
    print(f"  ALLOW: {manifest.summary['allow']}")
    print(f"  DENY:  {manifest.summary['deny']}")
    print(f"  HOLD:  {manifest.summary['hold']}")
    print(f"  Log:   {LOG_FILE}")

    if "--verbose" in sys.argv:
        for d in manifest.decisions:
            print(f"  {d['tool_name']}: {d['decision']} ({d['reason']})")

    return 0 if manifest.summary["deny"] == 0 else 1


if __name__ == "__main__":
    exit(main())
