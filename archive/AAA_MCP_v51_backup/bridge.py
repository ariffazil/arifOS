"""
AAA Bridge: Application <-> Core Adapter (v51.2.0)
Pure Serialization Layer + @PROMPT Codec.

Law: "I do not think, I only wire."

The bridge NEVER makes verdicts. It routes to kernels and returns their output.
All governance decisions belong to the core.

NEW in v51.2.0: @PROMPT integration
- Decodes human input → arifOS signals
- Routes to appropriate engine(s)
- Encodes verdicts → human language

DITEMPA BUKAN DIBERI
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# @PROMPT IMPORTS (Fail-safe)
# =============================================================================

PROMPT_AVAILABLE = False

try:
    from arifos.core.prompt.codec import SignalExtractor, ResponseFormatter, EngineRoute
    from arifos.core.prompt.router import PromptRouter, route_prompt
    PROMPT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"@PROMPT codec unavailable: {e}")
    SignalExtractor = ResponseFormatter = EngineRoute = None
    PromptRouter = route_prompt = None

# =============================================================================
# CORE IMPORTS (Fail-safe)
# =============================================================================

ENGINES_AVAILABLE = False

try:
    from arifos.core.agi.kernel import AGINeuralCore
    from arifos.core.asi.kernel import ASIActionCore
    from arifos.core.apex.kernel import APEXJudicialCore
    ENGINES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core kernels unavailable: {e}")
    AGINeuralCore = ASIActionCore = APEXJudicialCore = None

# Singletons
_AGI = _ASI = _APEX = None


def _kernel(cls, cache_name: str):
    """Get or create kernel singleton."""
    g = globals()
    if g[cache_name] is None and ENGINES_AVAILABLE and cls:
        g[cache_name] = cls()
    return g[cache_name]


def _run(coro):
    """Run async from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def _serialize(obj: Any) -> Any:
    """Convert objects to JSON-safe dicts."""
    if obj is None:
        return None
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, (str, int, float, bool)):
        return obj
    return str(obj)


def _unavailable(name: str) -> Dict:
    """Standard response when kernel unavailable."""
    return {"status": "UNAVAILABLE", "reason": f"{name} kernel not loaded"}


# =============================================================================
# ROUTERS - Pure Passthrough
# =============================================================================

def bridge_init_router(action: str = "init", **kw) -> Dict[str, Any]:
    """
    000_init: Session management + @PROMPT initialization.

    Returns:
        - session_id: Unique session identifier
        - @PROMPT config: Codec + routing rules
        - system_prompt: UNIVERSAL_PROMPT (if requested)
        - engines_available: Which kernels are loaded
    """
    import uuid, time
    session_id = kw.get("session_id") or str(uuid.uuid4())
    include_system_prompt = kw.get("include_system_prompt", True)

    result = {
        "session_id": session_id,
        "timestamp": time.time(),
        "engines_available": ENGINES_AVAILABLE,
        "prompt_available": PROMPT_AVAILABLE,
        "action": action,

        # @PROMPT Configuration
        "@PROMPT": {
            "enabled": PROMPT_AVAILABLE,
            "version": "v51.2.0",
            "routing": {
                "agi": "agi_genius → Reasoning, facts, analysis",
                "asi": "asi_act → Empathy, care, action",
                "apex": "apex_judge → Judgment, authority, verdicts",
                "trinity": "All three → Consensus for high-stakes",
            },
            "constraints": {
                "anti_hantu": True,       # F9: Block false empathy
                "delta_s_required": True, # F4: Reduce confusion
                "c_dark_max": 0.30,       # F9: Limit manipulation
                "reversibility": True,    # F1: Amanah check
                "injection_defense": True, # F12: Block injection
            },
        },

        # Active floors
        "floors_active": [
            "F1 Amanah (Reversibility)",
            "F2 Truth (Accuracy ≥0.99)",
            "F4 Clarity (ΔS ≤ 0)",
            "F6 Empathy (κᵣ ≥ 0.95)",
            "F7 Humility (Ω₀ ∈ [0.03, 0.05])",
            "F9 Anti-Hantu (Block false spirits)",
            "F12 Injection Defense (<0.85)",
        ],
    }

    # Load UNIVERSAL_PROMPT if requested
    if include_system_prompt:
        result["system_prompt"] = _load_universal_prompt()

    return result


def _load_universal_prompt() -> str:
    """Load UNIVERSAL_PROMPT.md as system prompt baseline."""
    # Try multiple possible locations
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "docs", "UNIVERSAL_PROMPT.md"),
        os.path.join(os.path.dirname(__file__), "..", "arifos", "docs", "UNIVERSAL_PROMPT.md"),
        "docs/UNIVERSAL_PROMPT.md",
    ]

    for path in possible_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError):
            continue

    # Fallback: Return minimal TEACH prompt
    return """
# arifOS v50 SYSTEM PROMPT (Minimal)

You are operating under arifOS constitutional governance.

## TEACH Principles
- **T**ruth: Be ≥99% accurate or state uncertainty
- **E**mpathy: Protect the weakest stakeholder
- **A**manah: Warn before irreversible actions
- **C**larity: Reduce confusion (ΔS ≤ 0)
- **H**umility: Maintain 3-5% uncertainty

## Verdicts
- SEAL: Approved
- SABAR: Wait/adjust
- VOID: Blocked
- 888_HOLD: Needs human approval

DITEMPA BUKAN DIBERI
"""


def bridge_agi_router(action: str = "full", query: str = "", **kw) -> Dict[str, Any]:
    """agi_genius: Route to AGINeuralCore. Returns kernel output."""
    kernel = _kernel(AGINeuralCore, "_AGI")
    if not kernel:
        return _unavailable("AGI")

    ctx = kw.get("context") or {}
    try:
        if action == "sense":
            return _serialize(_run(kernel.sense(query, ctx)))
        elif action == "reflect":
            return _serialize(_run(kernel.reflect(
                kw.get("thought", query),
                kw.get("thought_number", 1),
                kw.get("total_thoughts", 1),
                kw.get("next_needed", False)
            )))
        elif action == "atlas":
            return _serialize(_run(kernel.atlas_tac_analysis(kw.get("inputs", []))))
        elif action == "evaluate":
            v = kernel.evaluate(query, kw.get("response", ""), kw.get("truth_score", 1.0))
            return _serialize(v)
        else:  # full, think, forge -> default to sense
            return _serialize(_run(kernel.sense(query, ctx)))
    except Exception as e:
        logger.error(f"AGI error ({action}): {e}")
        return {"error": str(e), "action": action}


def bridge_asi_router(action: str = "full", agi_result: Optional[Dict] = None, **kw) -> Dict[str, Any]:
    """asi_act: Route to ASIActionCore. Returns kernel output."""
    kernel = _kernel(ASIActionCore, "_ASI")
    if not kernel:
        return _unavailable("ASI")

    ctx = agi_result or {}
    text = kw.get("text", kw.get("query", kw.get("proposal", "")))
    try:
        if action == "evidence":
            return _serialize(_run(kernel.gather_evidence(kw.get("query", ""), kw.get("rationale", ""))))
        elif action in ("empathize", "full", "act"):
            return _serialize(_run(kernel.empathize(text, ctx)))
        elif action in ("bridge", "align"):
            return _serialize(_run(kernel.bridge_synthesis(ctx, kw.get("empathy_input", {}))))
        elif action == "witness":
            return {"witness_id": kw.get("witness_request_id"), "approval": kw.get("approval", False)}
        else:
            return _serialize(_run(kernel.empathize(text, ctx)))
    except Exception as e:
        logger.error(f"ASI error ({action}): {e}")
        return {"error": str(e), "action": action}


def bridge_apex_router(action: str = "full", agi_result: Optional[Dict] = None, asi_result: Optional[Dict] = None, **kw) -> Dict[str, Any]:
    """apex_judge: Route to APEXJudicialCore. Returns kernel output."""
    kernel = _kernel(APEXJudicialCore, "_APEX")
    if not kernel:
        return _unavailable("APEX")

    try:
        if action in ("full", "judge"):
            return _serialize(_run(kernel.judge_quantum_path(
                kw.get("query", ""),
                kw.get("response", ""),
                [],  # trinity_floors
                kw.get("session_id", "anonymous")
            )))
        elif action in ("forge", "eureka"):
            return _serialize(_run(kernel.forge_insight(kw.get("draft", kw.get("response", "")))))
        elif action == "entropy":
            r = _run(kernel.entropy_profiler.measure_constitutional_cooling(
                kw.get("pre_text", ""), kw.get("post_text", "")
            ))
            return _serialize(r)
        elif action == "parallelism":
            import time
            r = _run(kernel.parallel_profiler.prove_constitutional_parallelism(
                kw.get("start_time", time.time()), kw.get("component_durations", {})
            ))
            return _serialize(r)
        elif action == "proof":
            import hashlib
            return {"hash": hashlib.sha256(str(kw.get("data", "")).encode()).hexdigest()[:16]}
        else:
            return _serialize(_run(kernel.judge_quantum_path(kw.get("query", ""), kw.get("response", ""), [], "anonymous")))
    except Exception as e:
        logger.error(f"APEX error ({action}): {e}")
        return {"error": str(e), "action": action}


def bridge_vault_router(action: str = "seal", **kw) -> Dict[str, Any]:
    """999_vault: Sealing operations. Pure hash generation."""
    import hashlib, time
    if action == "seal":
        data = {
            "timestamp": time.time(),
            "verdict": kw.get("verdict"),
            "agi": kw.get("agi_result"),
            "asi": kw.get("asi_result"),
            "apex": kw.get("apex_result"),
        }
        return {"hash": hashlib.sha256(str(data).encode()).hexdigest(), "timestamp": data["timestamp"]}
    elif action == "list":
        return {"entries": [], "target": kw.get("target", "ledger")}
    elif action == "read":
        return {"data": None, "query": kw.get("query", "")}
    elif action == "write":
        return {"hold": "888_HOLD", "reason": "Requires human authority"}
    elif action == "propose":
        return {"hold": "SABAR", "reason": "Requires tri-witness"}
    return {"action": action}


# =============================================================================
# @PROMPT ROUTER - Intelligent Codec + Routing
# =============================================================================

def bridge_prompt_router(action: str = "route", user_input: str = "", **kw) -> Dict[str, Any]:
    """
    @PROMPT: Intelligent codec + router.

    Actions:
        - decode: Extract signal from user input (intent, risk, stakeholders)
        - route: Decode + determine which engine(s) to call
        - process: Full pipeline (decode → route → call engines → encode response)
        - encode: Format verdict as human-readable response

    This is the intelligent protocol layer that:
        1. Translates human language → arifOS signals
        2. Routes to appropriate engine(s)
        3. Translates arifOS verdicts → human language

    Returns:
        Dict with signal, routing decision, and/or verdict response
    """
    if not PROMPT_AVAILABLE:
        return {
            "status": "UNAVAILABLE",
            "reason": "@PROMPT codec not loaded",
            "fallback": "Use individual tools (agi_genius, asi_act, apex_judge) directly",
        }

    try:
        extractor = SignalExtractor()
        formatter = ResponseFormatter()

        # ─────────────────────────────────────────────────────────────
        # ACTION: decode - Extract signal only
        # ─────────────────────────────────────────────────────────────
        if action == "decode":
            signal = extractor.extract(user_input)
            return {
                "action": "decode",
                "signal": signal.to_dict() if hasattr(signal, 'to_dict') else _serialize(signal),
                "routing_recommendation": signal.engine_route.value if hasattr(signal.engine_route, 'value') else str(signal.engine_route),
            }

        # ─────────────────────────────────────────────────────────────
        # ACTION: route - Decode + routing decision
        # ─────────────────────────────────────────────────────────────
        elif action == "route":
            signal = extractor.extract(user_input)

            # Check for injection (F12)
            if signal.injection_detected:
                return {
                    "action": "route",
                    "signal": signal.to_dict() if hasattr(signal, 'to_dict') else _serialize(signal),
                    "routing": "BLOCKED",
                    "verdict": "VOID",
                    "floor": "F12 Injection Defense",
                    "reason": "Manipulation attempt detected",
                    "engines_to_call": [],
                }

            # Determine engines
            route = signal.engine_route
            engines_to_call = []
            if route == EngineRoute.AGI:
                engines_to_call = ["agi_genius"]
            elif route == EngineRoute.ASI:
                engines_to_call = ["asi_act"]
            elif route == EngineRoute.APEX:
                engines_to_call = ["apex_judge"]
            elif route == EngineRoute.TRINITY:
                engines_to_call = ["agi_genius", "asi_act", "apex_judge"]

            return {
                "action": "route",
                "signal": signal.to_dict() if hasattr(signal, 'to_dict') else _serialize(signal),
                "routing": route.value if hasattr(route, 'value') else str(route),
                "engines_to_call": engines_to_call,
                "intent": signal.intent.value if hasattr(signal.intent, 'value') else str(signal.intent),
                "risk_level": signal.risk_level.value if hasattr(signal.risk_level, 'value') else str(signal.risk_level),
                "reversible": signal.reversible,
            }

        # ─────────────────────────────────────────────────────────────
        # ACTION: process - Full pipeline with engine calls
        # ─────────────────────────────────────────────────────────────
        elif action == "process":
            # Use async router if available
            if route_prompt:
                response = _run(route_prompt(user_input))
                return {
                    "action": "process",
                    "verdict": response.verdict,
                    "explanation": response.explanation,
                    "suggested_action": response.suggested_action,
                    "floor": response.constitutional_floor,
                    "confidence": response.confidence,
                    "human_readable": response.human_readable,
                    "engine_source": response.engine_source.value if hasattr(response.engine_source, 'value') else str(response.engine_source),
                }
            else:
                # Fallback: Just decode + route
                signal = extractor.extract(user_input)
                return {
                    "action": "process",
                    "fallback": True,
                    "signal": signal.to_dict() if hasattr(signal, 'to_dict') else _serialize(signal),
                    "note": "Full processing unavailable, returning signal only",
                }

        # ─────────────────────────────────────────────────────────────
        # ACTION: encode - Format verdict as response
        # ─────────────────────────────────────────────────────────────
        elif action == "encode":
            verdict = kw.get("verdict", "SEAL")
            floor = kw.get("floor", "Unknown")
            reason = kw.get("reason", "")
            engine = kw.get("engine", "unknown")

            # Convert engine string to EngineRoute if needed
            if isinstance(engine, str):
                try:
                    engine = EngineRoute(engine)
                except ValueError:
                    engine = EngineRoute.NONE

            response = formatter.encode_response(
                verdict=verdict,
                floor=floor,
                reason=reason,
                engine=engine,
            )

            return {
                "action": "encode",
                "verdict": response.verdict,
                "human_readable": response.human_readable,
                "suggested_action": response.suggested_action,
            }

        # ─────────────────────────────────────────────────────────────
        # Unknown action
        # ─────────────────────────────────────────────────────────────
        else:
            return {
                "error": f"Unknown @PROMPT action: {action}",
                "valid_actions": ["decode", "route", "process", "encode"],
            }

    except Exception as e:
        logger.error(f"@PROMPT error ({action}): {e}")
        return {"error": str(e), "action": action}
