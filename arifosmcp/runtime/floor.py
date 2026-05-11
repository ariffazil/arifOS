"""
F1–F13 Constitutional Floor Enforcer + F14 Semantic Gate
════════════════════════════════════════════════════════

Each floor is an interceptor axiom, not a callable tool.
They wrap all tool executions and gate the pipeline.

v2026.05.05-SSCT — SSCT NIAT PATCH:
- Reasoning free / Action narrow — core principle
- Angel + Devil reasoning allowed without gate
- Execution gated, not reasoning
- Fine-grained verdict subtypes replace flat HOLD

v2026.05.05-SSCT — SSCT SEMANTIC GATE:
- Intent classification BEFORE NIAT free-pass
- Instruction/manipulation intent caught even in reasoning tools
- Fast-path regex + structured fallback
- Crisis / self-support → ALLOW with resources
- Education / critique → ALLOW
- Instruction intent → VOID (blocked)
- Manipulation intent → HOLD (blocked)
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.constitutional_map import CANONICAL_TOOLS, Floor
from arifosmcp.runtime.semantic_gate import classify_intent

logger = logging.getLogger(__name__)


# Lazy import to avoid circular dependency at module load time
def _get_budget_contract(session_id: str):
    from arifosmcp.runtime.budget_contract import get_budget_contract as _gc

    return _gc(session_id)


# ─────────────────────────────────────────────────────────────────────────────
# Request Type Classification — NIAT principle
# Think wide / Act narrow
# ─────────────────────────────────────────────────────────────────────────────


class RequestType:
    """Cognitive mode tags — determines gating aggressiveness."""

    READ = "READ"  # Memory, evidence, observation — free
    REASON = "REASON"  # Thinking, analysis, critique — free
    CRITIQUE = "CRITIQUE"  # Adversarial/angel-devil reasoning — free
    DESIGN = "DESIGN"  # Architecture, blueprint — allow with caveat
    SIMULATE = "SIMULATE"  # What-if, dry-run — allow with caveat
    RED_TEAM = "RED_TEAM"  # Adversarial simulation — free (not execution)
    DRY_RUN = "DRY_RUN"  # Simulation only — allow with caveat
    EXECUTE = "EXECUTE"  # Real mutation — gate required
    VAULT_WRITE = "VAULT_WRITE"  # Irreversible anchoring — hard gate


# Verdict subtypes (replaces flat HOLD)
class VerdictLabel:
    ALLOW = "ALLOW"  # Pure read/critique, no gate
    ALLOW_WITH_CAVEAT = "ALLOW_WITH_CAVEAT"  # Design/simulate, caveat attached
    PARTIAL_EVIDENCE = "PARTIAL_EVIDENCE"  # Claim needs sourcing, can proceed with flag
    DESIGN_ONLY = "DESIGN_ONLY"  # Blueprint ok, execution blocked
    DRY_RUN_ONLY = "DRY_RUN_ONLY"  # Simulate ok, real execution HOLD
    RED_TEAM_SIMULATION_ONLY = (
        "RED_TEAM_SIMULATION_ONLY"  # Adversarial reasoning ok, weaponization blocked
    )
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"  # Needs explicit ack before proceeding
    HOLD_EXECUTION = "HOLD_EXECUTION"  # Full stop, fix needed before proceeding
    VOID = "VOID"  # Breach, blocked permanently


# Mode-to-RequestType mapping for arif_mind_reason
MIND_REASON_MODES = {
    "reason": RequestType.REASON,
    "reflect": RequestType.REASON,
    "verify": RequestType.CRITIQUE,
    "critique": RequestType.CRITIQUE,
    "debate": RequestType.RED_TEAM,
    "socratic": RequestType.REASON,
    "axioms": RequestType.READ,
    "plan": RequestType.DESIGN,
    "plan_review": RequestType.DESIGN,
    "plan_approve": RequestType.EXECUTE,
}

# Tool-to-RequestType mapping
TOOL_REQUEST_TYPE = {
    "arif_session_init": RequestType.EXECUTE,
    "arif_sense_observe": RequestType.READ,
    "arif_evidence_fetch": RequestType.READ,
    "arif_mind_reason": RequestType.REASON,  # overridden by mode param
    "arif_heart_critique": RequestType.CRITIQUE,  # overridden by mode
    "arif_kernel_route": RequestType.READ,
    "arif_reply_compose": RequestType.REASON,
    "arif_memory_recall": RequestType.READ,
    "arif_gateway_connect": RequestType.EXECUTE,
    "arif_judge_deliberate": RequestType.REASON,
    "arif_vault_seal": RequestType.VAULT_WRITE,
    "arif_forge_execute": RequestType.EXECUTE,  # overridden by mode
    "arif_ops_measure": RequestType.READ,
}


def classify_request(tool_name: str, params: dict[str, Any]) -> str:
    """
    Classify the request type for a tool call.
    Used to determine gating aggressiveness.

    NIAT principle:
      The Instrument may imagine the forbidden.
      The Instrument may not perform the forbidden.
      The Instrument may expose the dangerous.
      The Instrument may not enable the dangerous.
    """
    base_type = TOOL_REQUEST_TYPE.get(tool_name, RequestType.REASON)

    # Override by mode for multi-mode tools
    mode = params.get("mode", "").lower()

    if tool_name == "arif_mind_reason":
        return MIND_REASON_MODES.get(mode, RequestType.REASON)

    if tool_name == "arif_heart_critique":
        if mode in ("critique", "redteam", "simulate"):
            return RequestType.CRITIQUE
        if mode in ("empathize", "maruah", "deescalate"):
            return RequestType.REASON
        return RequestType.CRITIQUE

    if tool_name == "arif_forge_execute":
        if mode == "dry_run":
            return RequestType.DRY_RUN
        if mode in ("query", "recall"):
            return RequestType.READ
        if mode in ("write", "generate"):
            return RequestType.DESIGN
        if mode == "engineer":
            return RequestType.EXECUTE
        return base_type

    return base_type


def is_dangerous_tool(tool_name: str, params: dict[str, Any]) -> bool:
    """
    Check if tool call is asking for dangerous execution (not just reasoning).
    Used for weaponization detection — intent matters, not topic.
    """
    dangerous_keywords = [
        "bypass",
        "exploit",
        "privilege_escalate",
        "stealth",
        "rootkit",
        "backdoor",
        "credential",
        "unauthorized",
        "force_auth",
        "dump_password",
    ]
    return any(
        kw.lower() in str(v).lower()
        for k, v in params.items()
        if isinstance(v, str)
        for kw in dangerous_keywords
    )


# ─────────────────────────────────────────────────────────────────────────────
# Floor Descriptions
# ─────────────────────────────────────────────────────────────────────────────

FLOOR_DESCRIPTIONS: dict[Floor, str] = {
    Floor.F01_AMANAH: "Trustworthiness — every action is accountable.",
    Floor.F02_TRUTH: "Truthfulness — no deception, no hallucination passed as fact.",
    Floor.F03_WITNESS: "Witness — evidence must be verifiable and preserved.",
    Floor.F04_CLARITY: "Clarity — intent and mechanism are transparent.",
    Floor.F05_PEACE: "Peace — no harm to human dignity or safety.",
    Floor.F06_EMPATHY: "Empathy — consider human consequence before acting.",
    Floor.F07_HUMILITY: "Humility — acknowledge limits and uncertainty.",
    Floor.F08_GENIUS: "Genius — strive for elegant, correct solutions.",
    Floor.F09_ANTIHANTU: "Anti-Hantu — detect and reject manipulation.",
    Floor.F10_ONTOLOGY: "Ontology — preserve structural coherence.",
    Floor.F11_AUTH: "Authority — verify identity before irreversible acts.",
    Floor.F12_INJECTION: "Injection Guard — sanitize all inputs.",
    Floor.F13_SOVEREIGN: "Sovereign — human veto is absolute.",
}


def check_floors(tool_name: str, params: dict[str, Any], actor_id: str | None) -> dict[str, Any]:
    """
    Run F1–F13 interceptors + F14 semantic gate for a tool call.

    Returns dict with:
      - verdict: SEAL | HOLD | VOID
      - label: VerdictLabel string (fine-grained)
      - failed_floors: list
      - reason: str
      - request_type: classified type
      - next_safe_action: str

    NIAT principle:
      - Reasoning: wide (READ, REASON, CRITIQUE, RED_TEAM → ALLOW)
      - Action: narrow (EXECUTE, VAULT_WRITE → HARD GATE)
      - Design/Simulate → ALLOW_WITH_CAVEAT

    F14 Semantic Gate:
      - Instruction intent → VOID (blocked even in reasoning tools)
      - Manipulation intent → HOLD (blocked)
      - Crisis / self-support → ALLOW + supportive resources
      - Education / critique → ALLOW
    """
    # Record tool call in session history — F9 TAQWA prerequisite tracking
    session_id = params.get("session_id")
    if session_id:
        try:
            from arifosmcp.apps.session_state import record_tool_call

            record_tool_call(session_id, tool_name)
        except Exception:
            pass  # Non-session or cross-module: skip silently

    # ── 0. Classify request type (needed for budget gate responses) ───────────
    request_type = classify_request(tool_name, params)

    # ── 0. Budget Contract Enforcement (AAA-GOV-BUDGET-v1) ────────────────────
    # AAA defines. arifOS enforces. A-FORGE triggers via session_id.
    # Runs FIRST — budget exhaustion is a pre-condition failure, not a floor failure.
    if session_id:
        try:
            contract = _get_budget_contract(session_id)
            ok, reason = contract.check_turn()
            if not ok:
                logger.critical(f"BUDGET HOLD: {reason}")
                from arifosmcp.runtime.tools import _nine_signal_from_status

                return {
                    "verdict": "HOLD",
                    "label": VerdictLabel.HOLD_EXECUTION,
                    "failed_floors": ["BUDGET"],
                    "reasons": [reason],
                    "output_policy": "DOMAIN_VOID",
                    "nine_signal": _nine_signal_from_status("HOLD"),
                    "request_type": request_type,
                    "next_safe_action": "888_HOLD — budget exhausted, await human verdict",
                }
            ok, reason = contract.check_tool_call(tool_name)
            if not ok:
                logger.critical(f"BUDGET HOLD: {reason}")
                from arifosmcp.runtime.tools import _nine_signal_from_status

                return {
                    "verdict": "HOLD",
                    "label": VerdictLabel.HOLD_EXECUTION,
                    "failed_floors": ["BUDGET"],
                    "reasons": [reason],
                    "output_policy": "DOMAIN_VOID",
                    "nine_signal": _nine_signal_from_status("HOLD"),
                    "request_type": request_type,
                    "next_safe_action": "888_HOLD — tool call budget exhausted",
                }
            # Budget clear — record usage
            contract.record_turn(action=f"{tool_name}")
            contract.record_tool_call(tool_name)
        except Exception as e:
            logger.warning(f"Budget contract check failed (non-blocking): {e}")

    # ── 2. Angel/Devil reasoning — always allowed (niats freely) ────────────
    # "The Instrument may imagine the forbidden."
    # BUT: F14 semantic gate catches instruction/manipulation BEFORE the NIAT free-pass.
    if request_type in (
        RequestType.REASON,
        RequestType.CRITIQUE,
        RequestType.RED_TEAM,
        RequestType.READ,
    ):
        # F14 Semantic Gate: check text inputs for instruction/manipulation intent
        # This runs BEFORE the NIAT free-pass so harmful intent is caught even in reasoning tools
        query_param = (
            params.get("query")
            or params.get("text")
            or params.get("prompt")
            or params.get("target")
        )
        if query_param and isinstance(query_param, str) and len(query_param) > 2:
            if tool_name in (
                "arif_mind_reason",
                "arif_heart_critique",
                "arif_sense_observe",
                "arif_evidence_fetch",
                "arif_reply_compose",
                "arif_read",
            ):
                try:
                    intent_result = classify_intent(query_param)
                    if intent_result["verdict"] == "VOID":
                        return {
                            "verdict": "VOID",
                            "label": VerdictLabel.VOID,
                            "failed_floors": ["F14"],
                            "reason": (
                                f"F14 Semantic: {intent_result['category']} "
                                f"(confidence={intent_result['confidence']:.2f})"
                            ),
                            "request_type": request_type,
                            "next_safe_action": "Refuse — instruction intent blocked",
                        }
                    if intent_result["verdict"] == "HOLD":
                        if intent_result["category"] == "manipulation":
                            return {
                                "verdict": "HOLD",
                                "label": VerdictLabel.HOLD_EXECUTION,
                                "failed_floors": ["F14"],
                                "reason": (
                                    f"F14 Semantic: manipulation "
                                    f"(confidence={intent_result['confidence']:.2f})"
                                ),
                                "request_type": request_type,
                                "next_safe_action": "Hold — manipulation attempt blocked",
                            }
                except Exception as e:
                    logger.error(f"F14 Semantic Gate failed: {e}")
        # NIAT free-pass for education/critique/self-support/crisis
        return {
            "verdict": "SEAL",
            "label": VerdictLabel.ALLOW,
            "failed_floors": [],
            "reason": f"Free reasoning mode: {request_type}",
            "request_type": request_type,
            "next_safe_action": "Proceed — thinking is safe",
        }

    # ── 3. Design / Simulate → allow with caveat ─────────────────────────────
    if request_type in (
        RequestType.DESIGN,
        RequestType.SIMULATE,
        RequestType.DRY_RUN,
    ):
        return {
            "verdict": "SEAL",
            "label": VerdictLabel.ALLOW_WITH_CAVEAT,
            "failed_floors": [],
            "reason": f"Simulation/design mode: {request_type} — execution blocked separately",
            "request_type": request_type,
            "next_safe_action": (
                "Blueprint/simulation ok — " "real execution will require separate gate"
            ),
        }

    # ── 4. Execution-gated tools (EXECUTE, VAULT_WRITE) ───────────────────────
    spec = CANONICAL_TOOLS.get(tool_name)
    if not spec:
        return {
            "verdict": "VOID",
            "label": VerdictLabel.VOID,
            "failed_floors": ["F10"],
            "reason": f"Unknown tool: {tool_name}",
            "request_type": request_type,
            "next_safe_action": "Tool not found in canonical registry",
        }

    failed: list[str] = []

    # F12 Injection Guard — block injection patterns
    for key, value in params.items():
        if isinstance(value, str):
            risky = ["rm -rf", "eval(", "exec(", "__import__", "os.system"]
            if any(r in value for r in risky):
                failed.append("F12")
                logger.warning(f"F12 BLOCK: injection pattern in param '{key}' for {tool_name}")
                break

    # F11 Authority — only for EXECUTE/VAULT_WRITE, not for read-only modes
    risk_tier = spec.get("risk_tier", "low")
    _f11_safe_modes = {"query", "recall", "dry_run"}
    if risk_tier in ("critical", "sovereign") and not actor_id:
        mode_val = params.get("mode", "")
        if mode_val not in _f11_safe_modes:
            failed.append("F11")
            logger.warning(
                "F11 HOLD: %s requires actor_id for mode=%r (actor_id=%r, params_keys=%r)",
                tool_name,
                mode_val,
                actor_id,
                (list(params.keys()) if isinstance(params, dict) else type(params).__name__),
            )

    # F01 Amanah — irreversible tools need explicit ack
    if spec.get("irreversible") and not params.get("ack_irreversible"):
        failed.append("F01")
        logger.warning(f"F01 HOLD: {tool_name} is irreversible without ack")

    # F13 Sovereign — master veto
    if params.get("sovereign_veto"):
        failed.append("F13")
        logger.critical("F13 SOVEREIGN VETO invoked")

    # F09 TAQWA — arif_heart_critique must precede arif_forge_execute
    if tool_name == "arif_forge_execute":
        sid = params.get("session_id")
        if sid:
            try:
                from arifosmcp.apps.session_state import was_tool_called

                if not was_tool_called(sid, "arif_heart_critique"):
                    failed.append("F09")
                    logger.critical(
                        f"F09 ANTIHANTU: arif_forge_execute blocked — "
                        f"arif_heart_critique not called in session {sid}. "
                        f"PSI KHIANAT: Anti-Hantu prerequisite violated."
                    )
            except Exception as e:
                logger.error(f"F09 TAQWA check failed: {e}")

    # ── 5. Build response ────────────────────────────────────────────────────
    if failed:
        if "F13" in failed:
            return {
                "verdict": "VOID",
                "label": VerdictLabel.VOID,
                "failed_floors": failed,
                "reason": f"Constitutional breach: {', '.join(failed)}",
                "request_type": request_type,
                "next_safe_action": "Sovereign veto — no proceed path",
            }
        if "F09" in failed:
            return {
                "verdict": "HOLD",
                "label": VerdictLabel.HOLD_EXECUTION,
                "failed_floors": failed,
                "reason": f"Constitutional floor breach: {', '.join(failed)}",
                "request_type": request_type,
                "next_safe_action": "Run arif_heart_critique first, then retry forge",
            }
        if "F01" in failed or "F11" in failed:
            return {
                "verdict": "HOLD",
                "label": VerdictLabel.HUMAN_APPROVAL_REQUIRED,
                "failed_floors": failed,
                "reason": f"Constitutional floor breach: {', '.join(failed)}",
                "request_type": request_type,
                "next_safe_action": "Provide actor_id and/or ack_irreversible=true to proceed",
            }
        return {
            "verdict": "HOLD",
            "label": VerdictLabel.HOLD_EXECUTION,
            "failed_floors": failed,
            "reason": f"Constitutional floor breach: {', '.join(failed)}",
            "request_type": request_type,
            "next_safe_action": "Address failed floors before retry",
        }

    return {
        "verdict": "SEAL",
        "label": VerdictLabel.ALLOW,
        "failed_floors": [],
        "reason": "All floors clear",
        "request_type": request_type,
        "next_safe_action": "Proceed",
    }


def get_floor_status() -> dict[str, Any]:
    """Return current constitutional floor status."""
    return {
        "floors": {f.value: FLOOR_DESCRIPTIONS[f] for f in Floor},
        "status": "aligned",
        "version": "2026.05.05-SSCT",
    }
