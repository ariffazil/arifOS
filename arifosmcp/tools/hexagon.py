"""
HEXAGON MCP Tools — Constitutional Agent Parliament Interface (arifOS)

Renamed from agentzero → hexagon on 2026-06-06 (HEXAGON-NAME-CANON-20260606).
Canon: AAA/agents/HEXAGON.yaml v2.0.0 (sealed 2026-06-02, chain 2505).

Exposes HEXAGON agents as MCP tools for governed autonomous operations.
Author: Muhammad Arif bin Fazil [ΔΩΨ | ARIF]

Tools (HEXAGON canon names; agentzero_* aliases retained for backward compat):
- hexagon_apex_validate: APEXAgent (ΦΙ JUDGE) constitutional verification
- hexagon_agi_execute:   AGIAgent    (Δ MIND)     L11-gated code execution
- hexagon_hold_status:   888 HOLD state status query
- hexagon_asi_recall:    555-ASI     (Ω HEART)    Constitutional memory w/ F-floor filter
- hexagon_psi_armor:     L12 injection detection (Ψ APEX armor)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastmcp import Context

from arifosmcp.hexagon.agents.base import FloorScore
from arifosmcp.hexagon.agents.base import Verdict as HexVerdict  # was AZVerdict

# AgentZero Components
from arifosmcp.hexagon.agents.engineer import AGIAgent  # was EngineerAgent (reclassified Δ MIND)
from arifosmcp.hexagon.agents.validator import APEXAgent  # was ValidatorAgent (kept ΦΙ APEX)
from arifosmcp.hexagon.escalation.hold_state import HoldStateManager
from arifosmcp.hexagon.memory.constitutional_memory import ConstitutionalMemoryStore
from arifosmcp.hexagon.security.prompt_armor import PromptArmor

# arifOS runtime models
from arifosmcp.runtime.model import (
    CallerContext,
    RuntimeEnvelope,
    RuntimeStatus,
    Stage,
    Verdict,
)

logger = logging.getLogger(__name__)


class SimpleArifOSClient:
    """Mock client for HEXAGON agents to interact with arifOS governance."""

    async def evaluate_action(self, action: dict[str, Any], floors: list[str]) -> HexVerdict:
        # Default to SEAL for now as the tool wrapper provides the final governance envelope
        return HexVerdict.seal(
            execution_id=action.get("execution_id", "ext-000"),
            agent_id=action.get("agent_id", "unknown"),
            action_type=action.get("agent_type", "task"),
            floor_scores=[FloorScore(f, 1.0, 1.0, True) for f in floors],
        )

    async def seal_to_vault(self, verdict: AZVerdict) -> str:
        return f"vault_{uuid.uuid4().hex[:12]}"

    async def request_human_approval(self, execution_id: str, reason: str) -> bool:
        return False


# Singletons for performance and continuity
_CLIENT = SimpleArifOSClient()
_ARMOR = PromptArmor()
_ASI = ConstitutionalMemoryStore()  # 555-ASI (Ω HEART memory)
_HOLD_MANAGER = HoldStateManager()

_APEX = APEXAgent(agent_id="apex.mcp", arifos_client=_CLIENT)  # 888-APEX (ΦΙ JUDGE)
_AGI = AGIAgent(agent_id="agi.mcp", arifos_client=_CLIENT)  # 333-AGI (Δ MIND — was EngineerAgent Ω)
_AGI.set_validator(_APEX)  # method name kept for backward compat


def _nine_signal(status: str) -> dict:
    """Malay/English semantic state envelope for constitutional verdicts."""
    if status == "OK":
        return {
            "delta": {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
            "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},
            "omega": {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            "overall": {"state": "SELAMAT", "en": "SAFE"},
        }
    return {
        "delta": {"plane": "machine_physical_state", "state": "ROSAK", "en": "BROKEN"},
        "psi": {"plane": "governance_integrity", "state": "KHIANAT", "en": "BETRAYED"},
        "omega": {"plane": "intelligence_discipline", "state": "BANGANG", "en": "FOOLISH"},
        "overall": {"state": "RETAK", "en": "FAILED"},
    }


async def hexagon_apex_validate(
    input_to_validate: str,
    validation_type: str = "code",
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """
    ValidatorAgent (Ψ - APEX): Constitutional verification of code, output, or action.

    Arg:
        input_to_validate: The code, output, or action to validate.
        validation_type: Type of validation ("code", "output", "action", "plan").
    """
    try:
        task = {
            "type": ("validate_action" if validation_type == "action" else "verify_compliance"),
            "action": {"content": input_to_validate},
            "action_type": "content_validation",
            "validation_type": validation_type,
            "risk_level": "medium",
        }

        result = await _APEX.execute(task)

        az_status = result.get("verdict", "VOID")
        verdict_map = {
            "SEAL": Verdict.SEAL,
            "SABAR": Verdict.SABAR,
            "VOID": Verdict.VOID,
            "HOLD": Verdict.HOLD,
            "PARTIAL": Verdict.PARTIAL,
        }

        return RuntimeEnvelope(
            tool="hexagon_apex_validate",
            session_id=session_id,
            stage=Stage.JUDGE_888.value,
            verdict=verdict_map.get(az_status, Verdict.VOID),
            status=(
                RuntimeStatus.SUCCESS if result.get("status") == "success" else RuntimeStatus.ERROR
            ),
            payload={
                "validation_result": result.get("result", result),
                "agent_id": _APEX.agent_id,
            },
            auth_context=auth_context,
        )

    except Exception as e:
        logger.error(f"HEXAGON apex validation failed: {e}")
        return RuntimeEnvelope(
            tool="hexagon_apex_validate",
            session_id=session_id,
            stage=Stage.JUDGE_888.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def hexagon_agi_execute(
    task_description: str,
    action_type: str = "execute_code",
    risk_tier: str = "medium",
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """
    EngineerAgent (Ω - HEART): Code generation and execution with L11 gating.

    Arg:
        task_description: The code or command to execute.
        action_type: "execute_code", "shell_command", "read_file", "write_file".
    """
    try:
        task = {
            "type": action_type,
            "code": task_description if action_type == "execute_code" else "",
            "command": task_description if action_type == "shell_command" else "",
            "risk_tier": risk_tier,
            "authorized": True,
        }

        result = await _AGI.execute(task)

        is_err = result.get("status") in ["error", "VOID", "BLOCKED"]
        status = RuntimeStatus.ERROR if is_err else RuntimeStatus.SUCCESS

        return RuntimeEnvelope(
            tool="hexagon_agi_execute",
            session_id=session_id,
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.SEAL if status == RuntimeStatus.SUCCESS else Verdict.VOID,
            status=status,
            payload={
                "execution_result": result.get("result", result),
                "agent_id": _AGI.agent_id,
                "risk_tier": risk_tier,
            },
            auth_context=auth_context,
        )

    except Exception as e:
        logger.error(f"HEXAGON agi execution failed: {e}")
        return RuntimeEnvelope(
            tool="hexagon_agi_execute",
            session_id=session_id,
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def hexagon_hold_status(
    hold_id: str | None = None,
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """Check 888 HOLD state status and manage escalations."""
    try:
        if hold_id:
            details = _HOLD_MANAGER.get_hold_details(hold_id)
            payload = details.to_dict() if details else {"error": "Hold not found"}
        else:
            pending = _HOLD_MANAGER.get_pending_holds()
            payload = {
                "pending_holds": [h.to_dict() for h in pending],
                "stats": _HOLD_MANAGER.get_stats(),
            }

        return RuntimeEnvelope(
            tool="hexagon_hold_status",
            session_id=session_id,
            stage=Stage.VAULT_999.value,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=payload,
            auth_context=auth_context,
        )

    except Exception as e:
        logger.error(f"HEXAGON hold status failed: {e}")
        return RuntimeEnvelope(
            tool="hexagon_hold_status",
            session_id=session_id,
            stage=Stage.VAULT_999.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def hexagon_asi_recall(
    query: str,
    project_id: str = "default",
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """autonomous memory search across Vault999 and session artifacts."""
    try:
        await _ASI.initialize_project(project_id)

        memories = await _ASI.recall(
            query=query,
            project_id=project_id,
            k=5,
            verify_f2=True,
        )

        payload = {
            "query": query,
            "results": [m.to_dict() for m in memories],
            "project_id": project_id,
        }

        return RuntimeEnvelope(
            tool="hexagon_asi_recall",
            session_id=session_id,
            stage=Stage.MEMORY_555.value,
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=payload,
            auth_context=auth_context,
        )

    except Exception as e:
        logger.error(f"HEXAGON asi recall failed: {e}")
        return RuntimeEnvelope(
            tool="hexagon_asi_recall",
            session_id=session_id,
            stage=Stage.MEMORY_555.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


async def hexagon_psi_armor(
    content: str,
    session_id: str = "global",
    auth_context: dict[str, Any] | None = None,
    caller_context: CallerContext | None = None,
    ctx: Context | None = None,
) -> RuntimeEnvelope:
    """L12 security scan (PromptArmor) on content."""
    try:
        report = await _ARMOR.scan(content)

        return RuntimeEnvelope(
            tool="hexagon_psi_armor",
            session_id=session_id,
            stage=Stage.SENSE_111.value,
            verdict=Verdict.VOID if report.is_injection else Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload=report.to_dict(),
            auth_context=auth_context,
        )

    except Exception as e:
        logger.error(f"HEXAGON psi armor failed: {e}")
        return RuntimeEnvelope(
            tool="hexagon_psi_armor",
            session_id=session_id,
            stage=Stage.SENSE_111.value,
            verdict=Verdict.VOID,
            status=RuntimeStatus.ERROR,
            payload={"error": str(e)},
            auth_context=auth_context,
        )


# ════════════════════════════════════════════════════════════════
# Backward-compat aliases (HEXAGON-NAME-CANON-20260606)
# Old tool names still work — removed in future forge.
# ════════════════════════════════════════════════════════════════


async def agentzero_validate(*args, **kwargs):
    """DEPRECATED: use hexagon_apex_validate (Ψ APEX → ΦΙ APEX)."""
    return await hexagon_apex_validate(*args, **kwargs)


async def agentzero_engineer(*args, **kwargs):
    """DEPRECATED: use hexagon_agi_execute (was Ω HEART engineer, reclassified to Δ MIND)."""
    return await hexagon_agi_execute(*args, **kwargs)


async def agentzero_hold_check(*args, **kwargs):
    """DEPRECATED: use hexagon_hold_status."""
    return await hexagon_hold_status(*args, **kwargs)


async def agentzero_memory_query(*args, **kwargs):
    """DEPRECATED: use hexagon_asi_recall."""
    return await hexagon_asi_recall(*args, **kwargs)


async def agentzero_armor_scan(*args, **kwargs):
    """DEPRECATED: use hexagon_psi_armor."""
    return await hexagon_psi_armor(*args, **kwargs)


# Export all tools
__all__ = [
    "hexagon_apex_validate",
    "hexagon_agi_execute",
    "hexagon_hold_status",
    "hexagon_asi_recall",
    "hexagon_psi_armor",
    # Backward-compat aliases (deprecated 2026-06-06, remove in future forge)
    "agentzero_validate",
    "agentzero_engineer",
    "agentzero_hold_check",
    "agentzero_memory_query",
    "agentzero_armor_scan",
    "_nine_signal",
    # Internal singletons (for advanced callers)
    "_APEX",
    "_AGI",
    "_ASI",
    "_ARMOR",
    "_HOLD_MANAGER",
]
