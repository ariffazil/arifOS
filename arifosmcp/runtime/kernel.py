from __future__ import annotations

import inspect

from arifosmcp.runtime.DNA import OMEGA_BAND, VERSION

# --- Thermodynamics & Physics Stubs ---
try:
    from core.physics.thermodynamics_hardened import (
        check_landauer_bound as landauer_limit,
    )
    from core.shared.physics import build_qt_quad_proof, genius_score
except ImportError:

    def landauer_limit(bits_erased: float) -> dict:
        kb, t = 1.380649e-23, 300
        return {
            "energy_joules": bits_erased * kb * t * 0.693,
            "bits_erased": bits_erased,
        }

    def genius_score(a, p, x, e):
        return a * p * x * e**2

    def delta_s(t1, t2):
        return 0.0  # Placeholder

    def build_qt_quad_proof(**kwargs):
        return {
            "quad_witness_valid": True,
            "witnesses": {"W_ai": 0.8, "W_adversarial": 0.5},
            "W_four": 0.6,
        }


# --- Paradox Engine Primitives ---
QUOTES = {
    "triumph": (
        "In the midst of winter, I found there was, within me, " "an invincible summer. (Camus)"
    ),
    "wisdom": "He who knows others is wise; he who knows himself is enlightened. (Lao Tzu)",
    "warning": (
        "The first principle is that you must not fool yourself, "
        "and you are the easiest person to fool. (Feynman)"
    ),
    "tension": ("Out of the strain of the doing, into the peace of the done. (St. Augustine)"),
    "void": ("The void is not empty; it is full of potential that has not yet cooled. (888_JUDGE)"),
}


def get_philosophical_contrast(g_score: float, risk: str) -> dict[str, str]:
    if g_score < 0.5 and risk in ("high", "critical"):
        return {"label": "warning", "quote": QUOTES["warning"]}
    if g_score >= 0.8 and risk in ("low", "medium"):
        return {"label": "triumph", "quote": QUOTES["triumph"]}
    if risk == "high":
        return {"label": "tension", "quote": QUOTES["tension"]}
    return {"label": "wisdom", "quote": QUOTES["wisdom"]}


# --- Auditor Pre-Delivery Gate (666_HEART) ---

_AUDITOR_GATED_TOOLS = frozenset({
    "arif_sense_observe",
    "arif_mind_reason",
    "arif_memory_recall",
    "arif_evidence_fetch",
    "arif_reply_compose",
    "arif_forge_execute",
    "arif_heart_critique",
})
_AUDITOR_TIMEOUT_S = 5.0

# Fast deterministic audit markers (F-WEB §10 pattern-matched, no LLM required)
_AUDITOR_HALLUCINATION_MARKERS = [
    "i think", "probably", "might be", "could be", "possibly",
    "as far as i know", "to the best of my knowledge",
]
_AUDITOR_AUTONOMY_MARKERS = [
    "i decided", "i will deploy", "i will restart", "i'll go ahead",
]


def _auditor_quick_scan(result_text: str) -> dict:
    """Lightning-fast deterministic audit: F2 Truth, F6 Sovereignty, F9 Anti-Hantu.

    Runs < 1 ms — no LLM, no IO. If issues found, marks CAUTION.
    Clean results get SEAL.
    """
    text_lower = result_text.lower()
    warnings = []

    # F2 Truth: unqualified uncertainty markers
    for marker in _AUDITOR_HALLUCINATION_MARKERS:
        if marker in text_lower:
            warnings.append(f"F2_TRUTH: Unqualified uncertainty marker '{marker}'")
            break

    # F6 Sovereignty: autonomy overreach
    for marker in _AUDITOR_AUTONOMY_MARKERS:
        if marker in text_lower:
            warnings.append(f"F6_SOVEREIGN: Autonomy overreach marker '{marker}'")
            break

    # F9 Anti-Hantu: confidence without evidence citation
    if ("confident" in text_lower or "certainly" in text_lower) and "evidence" not in text_lower:
        warnings.append("F9_ANTI_HANTU: Confidence expressed without evidence citation")

    if warnings:
        return {
            "gate": "666_HEART",
            "verdict": "CAUTION",
            "risks_found": warnings,
            "risk_tier": "medium",
            "human_decision_required": False,
        }
    return {"gate": "666_HEART", "verdict": "SEAL"}


# --- Core Governance Classes ---


class ConstitutionalKernel:
    """The Unified Metabolic Heart of arifOS."""

    def __init__(self):
        self.godel_lock = {
            "acknowledged": True,
            "omega_0": 0.04,
            "omega_band": OMEGA_BAND,
            "note": "This system is incomplete. Truth > Proof.",
        }

    async def dispatch_with_fail_closed(self, tool_name: str, arguments: dict):
        """Fail-Closed Dispatch Gateway (F12/F13) + Formal Execution State Machine."""
        import time as _time

        from arifosmcp.runtime.execution_state_machine import (
            ExecutionState,
            ExecutionStateMachine,
        )
        from arifosmcp.runtime.output_formatter import format_output
        from arifosmcp.runtime.session import (
            get_session_execution_state,
            record_session_tool_event,
            set_session_execution_state,
        )
        from arifosmcp.runtime.telemetry import trace_tool_call
        from arifosmcp.runtime.tools import (
            FINAL_TOOL_IMPLEMENTATIONS,
            LEGACY_TOOL_ALIASES,
        )

        print(f"KERNEL: Dispatching {tool_name} through Fail-Closed Gates...")

        canonical_name = LEGACY_TOOL_ALIASES.get(tool_name, tool_name)
        session_id = arguments.get("session_id")
        actor_id = arguments.get("actor_id") or "system"

        # ── Formal Execution State Machine Gate ───────────────────────────────────────
        current_state_str = get_session_execution_state(session_id)
        try:
            current_state = ExecutionState(current_state_str) if current_state_str else None
        except ValueError:
            current_state = None

        if ExecutionStateMachine.is_enforced() and not ExecutionStateMachine.can_execute(
            canonical_name, current_state
        ):
            hold_result = ExecutionStateMachine.get_hold_response(
                canonical_name, current_state, session_id=session_id
            )
            trace_tool_call(
                tool_name=canonical_name,
                arguments=arguments,
                result=hold_result,
                session_id=session_id,
                actor_id=actor_id,
                latency_ms=0.0,
            )
            record_session_tool_event(
                session_id=session_id,
                tool_name=canonical_name,
                stage="888",
                verdict="HOLD",
                payload=hold_result,
                execution_state=current_state_str,
            )
            return hold_result

        # ── Tool Embodiment Contract Gate (F11 AUTH + embodiment enforcement) ────────
        from arifosmcp.runtime.embodiment_contracts import enforce_embodiment
        from arifosmcp.runtime.tools import _SESSIONS

        session = _SESSIONS.get(session_id) if session_id else None
        plan_id = arguments.get("plan_id")
        judge_verdict = arguments.get("judge_verdict")
        embodiment = enforce_embodiment(
            canonical_name, session, plan_id=plan_id, judge_verdict=judge_verdict
        )
        if not embodiment.get("ok"):
            hold_result = {
                "tool": canonical_name,
                "stage": "555_ROUTE",
                "status": "HOLD",
                "result": {
                    "error": "EMBODIMENT_HOLD",
                    "reason": embodiment.get("reason"),
                    "failed_floors": embodiment.get("floors", ["F11"]),
                    "embodiment_violation": embodiment.get("embodiment_violation"),
                    "next_safe_action": embodiment.get(
                        "next_safe_action", "Review agent card and constitutional lane."
                    ),
                },
                "verdict": "HOLD",
                "nine_signal": "RETAK",
            }
            trace_tool_call(
                tool_name=canonical_name,
                arguments=arguments,
                result=hold_result,
                session_id=session_id,
                actor_id=actor_id,
                latency_ms=0.0,
            )
            record_session_tool_event(
                session_id=session_id,
                tool_name=canonical_name,
                stage="555_ROUTE",
                verdict="HOLD",
                payload=hold_result,
                execution_state=current_state_str,
            )
            return hold_result

        handler = FINAL_TOOL_IMPLEMENTATIONS.get(canonical_name)
        if handler is None:
            result = {
                "tool": canonical_name,
                "stage": "555_ROUTE",
                "status": "error",
                "summary": f"No canonical handler registered for {tool_name}.",
                "result": {"error": "TOOL_NOT_FOUND", "requested_tool": tool_name},
            }
            trace_tool_call(
                tool_name=canonical_name,
                arguments=arguments,
                result=result,
                session_id=session_id,
                actor_id=actor_id,
                latency_ms=0.0,
            )
            return result

        start_ns = _time.perf_counter_ns()
        try:
            result = handler(**arguments)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            result = {
                "tool": canonical_name,
                "stage": "555_ROUTE",
                "status": "ERROR",
                "error_message": str(e),
                "result": {},
            }
        latency_ms = (_time.perf_counter_ns() - start_ns) / 1e6

        # ── Ontology bridge: canonicalize + validate output ─────────────────────────────
        try:
            from arifosmcp.runtime.ontology_bridge import ontology_bridge

            if isinstance(result, dict):
                result = ontology_bridge.process(
                    tool_name=canonical_name,
                    result=result,
                    session_id=session_id,
                    actor_id=actor_id,
                    execution_state=current_state,
                )
        except Exception:
            # Ontology bridge must never break tool execution
            pass

        # ── Auditor Pre-Delivery Gate (666_HEART) ───────────────────────────────────────
        if (
            canonical_name in _AUDITOR_GATED_TOOLS
            and not arguments.get("skip_auditor_gate")
            and isinstance(result, dict)
        ):
            try:
                result_text = str(result.get("result", result))
                audit_block = _auditor_quick_scan(result_text[:3000])
                result["_auditor_gate"] = audit_block
            except Exception:
                # Auditor must never break tool execution
                result["_auditor_gate"] = {"gate": "666_HEART", "verdict": "DEGRADED"}

        # ── State progression ───────────────────────────────────────────────────────────
        next_state = ExecutionStateMachine.get_next_state(canonical_name, current_state)
        if session_id and next_state != current_state:
            set_session_execution_state(session_id, next_state.value)

        # Record event with execution state
        record_session_tool_event(
            session_id=session_id,
            tool_name=canonical_name,
            stage="555_ROUTE",
            verdict=result.get("verdict") or result.get("status", "UNKNOWN"),
            payload=result if isinstance(result, dict) else {},
            execution_state=next_state.value,
        )

        if result.__class__.__name__ == "RuntimeEnvelope":
            platform = arguments.get("platform", "mcp")
            if hasattr(result, "platform_context"):
                result.platform_context = platform
            formatted = format_output(
                result,
                {"verbose": False, "debug": bool(arguments.get("debug", False))},
            )
            trace_tool_call(
                tool_name=canonical_name,
                arguments=arguments,
                result=formatted,
                session_id=arguments.get("session_id"),
                actor_id=arguments.get("actor_id") or "system",
                latency_ms=latency_ms,
            )
            return formatted
        if hasattr(result, "model_dump"):
            dumped = result.model_dump(mode="json")
            trace_tool_call(
                tool_name=canonical_name,
                arguments=arguments,
                result=dumped,
                session_id=arguments.get("session_id"),
                actor_id=arguments.get("actor_id") or "system",
                latency_ms=latency_ms,
            )
            return dumped

        trace_tool_call(
            tool_name=canonical_name,
            arguments=arguments,
            result=result,
            session_id=arguments.get("session_id"),
            actor_id=arguments.get("actor_id") or "system",
            latency_ms=latency_ms,
        )
        return result

    async def get_constitutional_context(self, session_id: str, actor_id: str) -> str:
        """Grounding prompt for Agentic reasoning (K_FORGE §I)."""
        return f"Actor: {actor_id} | Session: {session_id} | Version: {VERSION} | DNA: SEALED"

    def calculate_coherence(self, entropy_delta: float, confidence: float) -> float:
        """Lyapunov-like stability assessment (K_FORGE §XI)."""
        return confidence * (1.0 if entropy_delta <= 0 else 0.5)


# Global kernel instance for the gateway
kernel = ConstitutionalKernel()

# --- End of Kernel ---
