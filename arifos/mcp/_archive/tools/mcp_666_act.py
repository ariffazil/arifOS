"""
666_ACT: Executor (Refactored for Phase 1 Consent).

A tool that takes a command and runs it.
This is DANGEROUS and SHOULD NOT RUN without Tri-Witness approval (F3).

Constitutional Requirements:
  - Required Floor: F5 (Peace) minimum; F11 (Command Auth) for destructive.
  - Idempotent: False (actions have side effects).
  - Destructive: True (may delete, modify, exfiltrate).
  - Cost: High (compute, latency, trust).
  - Tri-Witness Threshold: 2 (requires two independent signers).

DITEMPA BUKAN DIBERI - Forged v50.4
"""

import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from arifos.core.governance.authority import Authority


@dataclass
class ToolMetadata:
    """Metadata about a tool's authority requirements and risk profile."""
    name: str
    required_floor: str           # Minimum Floor to invoke
    idempotent: bool              # True = safe to retry; False = has side-effects
    destructive: bool             # True = irreversible state change
    cost_estimate: dict           # {"tokens": N, "latency_ms": N}
    tri_witness_threshold: int    # 0 = no witnesses, 1 = self-witnessing, 2+ = require independent signers
    description: str

# 666_act metadata
EXECUTOR_METADATA = ToolMetadata(
    name="666_act",
    required_floor="F11",  # Command Authority (implies F5 Peace)
    idempotent=False,
    destructive=True,
    cost_estimate={"tokens": 100, "latency_ms": 5000},
    tri_witness_threshold=2,  # MUST have 2 independent witnesses
    description="Execute shell command. Requires F11 (Command Auth) + 2 tri-witnesses (F3)."
)

async def mcp_666_act(
    action: str,
    authority: Authority = None, # Injected by UnifiedServer
    vault_manager: Any = None,   # Injected by UnifiedServer
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a command with Constitutional Tri-Witness Gating.

    Workflow:
    1. Authority check: Can △ invoke tools requiring F11?
    2. Cost check: Does △'s budget afford this?
    3. Witness collection: Solicit signatures from 2 independent observers.
    4. Execution: If all checks pass + witnesses sign, execute the command.
    5. Audit: Log command, output, witnesses, and tri-witness proof to Vault.
    """

    # Legacy fallbacks for calls not yet updated to inject authority
    if authority is None:
        # Default to a sandbox authority if none provided
        from arifos.core.governance.authority import Authority, AuthorityLevel
        authority = Authority("legacy_caller", AuthorityLevel.SANDBOX, set(), {}, 1, "auto", "now")

    command = kwargs.get("command", "")

    # --------------------------------------------------------------------------
    # ACTION: EXECUTE (The Dangerous One)
    # --------------------------------------------------------------------------
    if action == "execute":
        # Step 1: Authority check
        if "F11" not in authority.scope_floors:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Authority △{authority.agent_id} does not have F11 (Command Auth). Cannot execute."
                }]
            }

        # Step 2: Cost check
        cost = EXECUTOR_METADATA.cost_estimate
        if not authority.can_afford(cost):
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"Cost budget exceeded. Requested: {cost}. Available: {authority.cost_budget}."
                }]
            }

        # Step 3: Witness collection (Interactive Consent)
        # We create a pending request ID
        witness_request_id = str(uuid.uuid4())

        # In a real system, we'd persist this PRE-execution intent to Vault
        if vault_manager:
            # vault_manager.create_pending_execution(...)
            # (Assumed implemented or TODO in Phase 1b)
            pass

        return {
            "isError": False,
            "content": [{
                "type": "text",
                "text": f"Command queued for tri-witness approval. Request ID: {witness_request_id}. Waiting for {EXECUTOR_METADATA.tri_witness_threshold} independent signers."
            }],
            "meta": {
                "witness_request_id": witness_request_id,
                "status": "PENDING_APPROVAL",
                "tri_witness_threshold": EXECUTOR_METADATA.tri_witness_threshold,
                "command_preview": command[:50] + "..." if len(command) > 50 else command
            }
        }

    # --------------------------------------------------------------------------
    # ACTION: SKILL (Safe-ish, but still needs F5)
    # --------------------------------------------------------------------------
    elif action == "skill":
        # Check basic F5 Peace
        if "F5" not in authority.scope_floors:
             return {"isError": True, "content": [{"type": "text", "text": "Missing F5 (Peace) for Skills."}]}

        # Pass through to existing Codex implementation
        # (We assume helper _codex_skills is available or we re-import)
        from .codex_skills import CodexConstitutionalSkills
        _skills = CodexConstitutionalSkills()

        skill_name = kwargs.get("skill_name", "")
        if skill_name == "codex_code_analysis":
             return await _skills.analyze_code(
                 kwargs.get("code", ""),
                 kwargs.get("analysis_type", "general"),
                 kwargs.get("user_id", "default"),
                 kwargs.get("context", {})
             )
        # ... other skills ...
        return {"error": f"Unknown skill: {skill_name}"}

    # --------------------------------------------------------------------------
    # ACTION: ALIGN (Safe)
    # --------------------------------------------------------------------------
    elif action == "align":
        return {"message": "Alignment check passed (Stub)"}

    return {"error": f"Unknown action: {action}"}
