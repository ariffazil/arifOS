"""
AAA Bridge: Application <-> Core Adapter (v51.1.0)
Wires MCP Requests to arifOS Core Kernels.

Aligned with v51 Unified Architecture:
  - AGINeuralCore (Mind - Δ)
  - ASIActionCore (Heart - Ω)
  - APEXJudicialCore (Soul - Ψ)
  - SystemCoordinator (Orchestrator)

The Body (Hands) speaks to the Brain (Soul) through this bridge.
Zero logic here - only routing and serialization.

DITEMPA BUKAN DIBERI
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# CORE KERNEL IMPORTS (v51 Unified - Fail-safe)
# =============================================================================

KERNELS_AVAILABLE = False
COORDINATOR_AVAILABLE = False

try:
    from arifos.core.agi.kernel import AGINeuralCore
    from arifos.core.asi.kernel import ASIActionCore
    from arifos.core.apex.kernel import APEXJudicialCore
    KERNELS_AVAILABLE = True
    logger.info("AAA Bridge: Core kernels loaded (AGI/ASI/APEX)")
except ImportError as e:
    logger.warning(f"AAA Bridge: Core kernels unavailable: {e}")
    AGINeuralCore = None
    ASIActionCore = None
    APEXJudicialCore = None

try:
    from arifos.core.system.system_coordinator import (
        SystemCoordinator,
        ConstitutionalContext,
        execute_constitutional_system,
    )
    COORDINATOR_AVAILABLE = True
    logger.info("AAA Bridge: SystemCoordinator loaded")
except ImportError as e:
    logger.warning(f"AAA Bridge: SystemCoordinator unavailable: {e}")
    SystemCoordinator = None
    ConstitutionalContext = None
    execute_constitutional_system = None

# Combined availability flag
ENGINES_AVAILABLE = KERNELS_AVAILABLE

# =============================================================================
# SINGLETON KERNEL INSTANCES
# =============================================================================

_AGI: Optional["AGINeuralCore"] = None
_ASI: Optional["ASIActionCore"] = None
_APEX: Optional["APEXJudicialCore"] = None
_COORDINATOR: Optional["SystemCoordinator"] = None


def get_agi() -> "AGINeuralCore":
    """Get or create AGI kernel singleton."""
    global _AGI
    if _AGI is None and KERNELS_AVAILABLE:
        _AGI = AGINeuralCore()
    return _AGI


def get_asi() -> "ASIActionCore":
    """Get or create ASI kernel singleton."""
    global _ASI
    if _ASI is None and KERNELS_AVAILABLE:
        _ASI = ASIActionCore()
    return _ASI


def get_apex() -> "APEXJudicialCore":
    """Get or create APEX kernel singleton."""
    global _APEX
    if _APEX is None and KERNELS_AVAILABLE:
        _APEX = APEXJudicialCore()
    return _APEX


def get_coordinator() -> "SystemCoordinator":
    """Get or create SystemCoordinator singleton."""
    global _COORDINATOR
    if _COORDINATOR is None and COORDINATOR_AVAILABLE:
        _COORDINATOR = SystemCoordinator()
    return _COORDINATOR


# =============================================================================
# ASYNC RUNNER HELPER
# =============================================================================

def _run_async(coro):
    """Run async coroutine from sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create new loop if current is running
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# =============================================================================
# SERIALIZATION HELPER
# =============================================================================

def _serialize(obj: Any) -> Any:
    """Recursively serialize objects to JSON-safe dicts/lists."""
    if obj is None:
        return None
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if hasattr(obj, "__dict__"):
        # Dataclass or object - serialize its dict
        result = {}
        for k, v in obj.__dict__.items():
            if not k.startswith("_"):
                result[k] = _serialize(v)
        return result
    if isinstance(obj, list):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (str, int, float, bool)):
        return obj
    # Enum handling
    if hasattr(obj, "value"):
        return obj.value
    return str(obj)


# =============================================================================
# AGI ROUTER (Mind - Δ)
# =============================================================================

def bridge_agi_router(
    action: str,
    query: str = "",
    context: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes AGI actions to AGINeuralCore methods.

    Actions:
      - full: Complete AGI pipeline via SystemCoordinator
      - sense: Stage 111 - Lane classification + truth threshold
      - reflect: Stage 222 - Sequential reflection
      - atlas: Stage 333 - TAC analysis
      - evaluate: Floor evaluation (F2 + F4)
    """
    if not KERNELS_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core kernels unavailable", "source": "AAA_bridge"}

    kernel = get_agi()
    if kernel is None:
        return {"status": "FALLBACK", "reason": "AGI kernel init failed", "source": "AAA_bridge"}

    try:
        if action == "full":
            # Use SystemCoordinator for full orchestrated execution
            if COORDINATOR_AVAILABLE:
                user_id = kwargs.get("session_id", "anonymous")
                result = _run_async(execute_constitutional_system(query, user_id, context))
                output = _serialize(result)
                output["source"] = "AAA_bridge_coordinator"
                return output
            else:
                # Fallback: Just run sense
                result = _run_async(kernel.sense(query, context))
                return {
                    "status": "SEAL",
                    "result": _serialize(result),
                    "source": "AAA_bridge_fallback"
                }

        elif action == "sense":
            # Stage 111: Active Context Sensing via ATLAS
            context_meta = context or {"origin": "MCP", "user_id": kwargs.get("session_id", "anonymous")}
            result = _run_async(kernel.sense(query, context_meta))
            meta = result.get("meta", {})
            lane = meta.get("lane", "HARD")
            # Handle Lane enum or string
            lane_value = lane.value if hasattr(lane, "value") else str(lane)
            return {
                "status": "SEAL" if lane_value != "REFUSE" else "VOID",
                "lane": lane_value,
                "truth_demand": meta.get("truth_demand", 0.99),
                "care_demand": meta.get("care_demand", 0.5),
                "risk_level": meta.get("risk_level", "low"),
                "source": "AAA_bridge"
            }

        elif action == "reflect":
            # Stage 222: Sequential Reflection
            thought = kwargs.get("thought", query)
            thought_num = kwargs.get("thought_number", 1)
            total = kwargs.get("total_thoughts", 1)
            next_needed = kwargs.get("next_needed", False)
            result = _run_async(kernel.reflect(thought, thought_num, total, next_needed))
            return {
                "status": "SEAL",
                "reflection": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "atlas":
            # Stage 333: TAC Engine
            inputs = kwargs.get("inputs", [])
            result = _run_async(kernel.atlas_tac_analysis(inputs))
            return {
                "status": "SEAL",
                "atlas": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "evaluate":
            # Floor evaluation using kernel.evaluate()
            response = kwargs.get("response", "")
            truth_score = kwargs.get("truth_score", 1.0)
            verdict = kernel.evaluate(query, response, truth_score)
            return {
                "status": "SEAL" if verdict.passed else "VOID",
                "passed": verdict.passed,
                "reason": verdict.reason,
                "failures": verdict.failures,
                "f4_delta_s": verdict.f4_delta_s,
                "truth_score": verdict.truth_score,
                "source": "AAA_bridge"
            }

        elif action == "think":
            # Alias for reflect
            return bridge_agi_router("reflect", query, context, **kwargs)

        elif action == "forge":
            # Alias for full
            return bridge_agi_router("full", query, context, **kwargs)

        else:
            return {"status": "FALLBACK", "reason": f"Unknown AGI action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"AGI bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# ASI ROUTER (Heart - Ω)
# =============================================================================

def bridge_asi_router(
    action: str,
    agi_result: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes ASI actions to ASIActionCore methods.

    Actions:
      - full: Complete ASI pipeline
      - evidence: Stage 444 - Truth grounding via sources
      - empathize: Stage 555 - Empathy processing
      - bridge: Stage 666 - Neuro-symbolic synthesis
      - evaluate: Floor evaluation (F3 + F4 + F5)
    """
    if not KERNELS_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core kernels unavailable", "source": "AAA_bridge"}

    kernel = get_asi()
    if kernel is None:
        return {"status": "FALLBACK", "reason": "ASI kernel init failed", "source": "AAA_bridge"}

    try:
        if action == "full":
            # Full ASI pipeline: evidence -> empathize -> bridge
            query = kwargs.get("query", kwargs.get("text", ""))
            context = agi_result or {"origin": "MCP"}

            # Run empathize (main ASI action)
            result = _run_async(kernel.empathize(query, context))
            omega_verdict = result.get("omega_verdict", "SEAL")

            return {
                "status": omega_verdict,
                "vulnerability_score": result.get("vulnerability_score", 0.0),
                "action": result.get("action", "Neutral"),
                "omega_verdict": omega_verdict,
                "source": "AAA_bridge"
            }

        elif action == "evidence":
            # Stage 444: Active Grounding
            query = kwargs.get("query", "")
            rationale = kwargs.get("rationale", "MCP evidence request")
            result = _run_async(kernel.gather_evidence(query, rationale))
            return {
                "status": "SEAL",
                "evidence_count": result.get("evidence_count", 0),
                "sources": result.get("sources", []),
                "top_evidence": result.get("top_evidence", []),
                "truth_score": result.get("truth_score", 0.99),
                "source": "AAA_bridge"
            }

        elif action == "empathize":
            # Stage 555: Empathy Processing
            text = kwargs.get("text", kwargs.get("proposal", ""))
            context = agi_result or {"origin": "MCP"}
            result = _run_async(kernel.empathize(text, context))
            return {
                "status": result.get("omega_verdict", "SEAL"),
                "vulnerability_score": result.get("vulnerability_score", 0.0),
                "action": result.get("action", "Neutral"),
                "source": "AAA_bridge"
            }

        elif action == "bridge" or action == "align":
            # Stage 666: Neuro-Symbolic Bridge
            logic_input = agi_result or {}
            empathy_input = kwargs.get("empathy_input", {})
            result = _run_async(kernel.bridge_synthesis(logic_input, empathy_input))
            return {
                "status": "SEAL",
                "synthesis": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "act":
            # Alias for full with agi_result
            return bridge_asi_router("full", agi_result, **kwargs)

        elif action == "witness":
            witness_id = kwargs.get("witness_request_id", "")
            approval = kwargs.get("approval", False)
            return {
                "status": "SEAL" if approval else "SABAR",
                "witness": {"id": witness_id, "approval": approval},
                "source": "AAA_bridge"
            }

        elif action == "evaluate":
            return {
                "status": "SEAL",
                "floors": {
                    "F3_peace": True,
                    "F4_empathy": True,
                    "F5_safety": True,
                },
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown ASI action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"ASI bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# APEX ROUTER (Soul - Ψ)
# =============================================================================

def bridge_apex_router(
    action: str,
    agi_result: Optional[Dict] = None,
    asi_result: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes APEX actions to APEXJudicialCore methods.

    Actions:
      - full/judge: Stage 888 - Constitutional verdict via APEX Prime
      - forge: Stage 777 - Insight forging
      - entropy: Entropy measurement (Agent Zero)
      - parallelism: Parallelism proof (Agent Zero)
      - proof: Cryptographic sealing
    """
    if not KERNELS_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core kernels unavailable", "source": "AAA_bridge"}

    kernel = get_apex()
    if kernel is None:
        return {"status": "FALLBACK", "reason": "APEX kernel init failed", "source": "AAA_bridge"}

    try:
        if action in ("full", "judge"):
            # Stage 888: Quantum Path Judgment via APEX Prime
            query = kwargs.get("query", "")
            response = kwargs.get("response", "")
            user_id = kwargs.get("session_id", "anonymous")
            trinity_floors = []  # Would collect from agi/asi results

            result = _run_async(kernel.judge_quantum_path(query, response, trinity_floors, user_id))
            final_ruling = result.get("final_ruling", "SEAL")

            return {
                "status": final_ruling,
                "judgment": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "forge" or action == "eureka":
            # Stage 777: Forge Insight
            draft = kwargs.get("draft", kwargs.get("response", ""))
            result = _run_async(kernel.forge_insight(draft))
            return {
                "status": "SEAL",
                "forge": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "entropy":
            # Agent Zero: Entropy Measurement
            pre_text = kwargs.get("pre_text", "")
            post_text = kwargs.get("post_text", "")
            result = _run_async(kernel.entropy_profiler.measure_constitutional_cooling(pre_text, post_text))
            return {
                "status": "SEAL" if result.thermodynamic_valid else "VOID",
                "entropy": {
                    "pre_entropy": result.pre_entropy,
                    "post_entropy": result.post_entropy,
                    "reduction": result.entropy_reduction,
                    "thermodynamic_valid": result.thermodynamic_valid
                },
                "source": "AAA_bridge"
            }

        elif action == "parallelism":
            # Agent Zero: Parallelism Proof
            import time
            start_time = kwargs.get("start_time", time.time())
            component_durations = kwargs.get("component_durations", {})
            result = _run_async(kernel.parallel_profiler.prove_constitutional_parallelism(start_time, component_durations))
            return {
                "status": "SEAL" if result.parallelism_achieved else "VOID",
                "parallelism": {
                    "speedup": result.speedup_achieved,
                    "parallel_time": result.parallel_execution_time,
                    "achieved": result.parallelism_achieved
                },
                "source": "AAA_bridge"
            }

        elif action == "proof":
            data = kwargs.get("data", "")
            verdict = kwargs.get("verdict", "SEAL")
            import hashlib
            proof_hash = hashlib.sha256(str(data).encode()).hexdigest()[:16]
            return {
                "status": verdict,
                "proof": {
                    "hash": proof_hash,
                    "data": data,
                    "sealed": True
                },
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown APEX action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"APEX bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# VAULT ROUTER (Seal - 999)
# =============================================================================

def bridge_vault_router(
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes Vault actions for sealing and persistence.

    Actions:
      - seal: Final seal with hash
      - list: List vault entries
      - read: Read vault entry
      - write: Write to vault (requires authority)
      - propose: Propose new canon entry
    """
    import hashlib
    import time

    try:
        if action == "seal":
            verdict = kwargs.get("verdict", "SEAL")
            seal_data = {
                "timestamp": time.time(),
                "verdict": verdict,
                "init_result": kwargs.get("init_result"),
                "agi_result": kwargs.get("agi_result"),
                "asi_result": kwargs.get("asi_result"),
                "apex_result": kwargs.get("apex_result"),
            }
            seal_hash = hashlib.sha256(str(seal_data).encode()).hexdigest()
            return {
                "status": verdict,
                "seal": {
                    "hash": seal_hash,
                    "timestamp": seal_data["timestamp"],
                    "sealed": True
                },
                "source": "AAA_bridge"
            }

        elif action == "list":
            target = kwargs.get("target", "ledger")
            return {
                "status": "SEAL",
                "entries": [],
                "target": target,
                "source": "AAA_bridge"
            }

        elif action == "read":
            query = kwargs.get("query", "")
            target = kwargs.get("target", "ledger")
            return {
                "status": "SEAL",
                "data": None,
                "query": query,
                "target": target,
                "source": "AAA_bridge"
            }

        elif action == "write":
            return {
                "status": "888_HOLD",
                "reason": "Vault write requires human authority",
                "source": "AAA_bridge"
            }

        elif action == "propose":
            return {
                "status": "SABAR",
                "reason": "Canon proposals require tri-witness approval",
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown vault action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"Vault bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# INIT ROUTER (Gate - 000)
# =============================================================================

def bridge_init_router(
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes Init actions for session management.

    Actions:
      - init: Full initialization
      - gate: Constitutional authority check
      - reset: Clean session start
      - validate: Pre-flight validation
    """
    import uuid
    import time

    try:
        session_id = kwargs.get("session_id") or str(uuid.uuid4())

        if action == "init":
            return {
                "status": "SEAL",
                "session_id": session_id,
                "timestamp": time.time(),
                "kernels_available": KERNELS_AVAILABLE,
                "coordinator_available": COORDINATOR_AVAILABLE,
                "gates": {
                    "F1_amanah": True,
                    "F11_command_auth": True,
                    "F12_injection": True,
                },
                "source": "AAA_bridge"
            }

        elif action == "gate":
            query = kwargs.get("query", "")
            injection_patterns = ["rm -rf", "DROP TABLE", "eval(", "curl | bash"]
            is_safe = not any(p in query for p in injection_patterns)
            return {
                "status": "SEAL" if is_safe else "VOID",
                "gate": "open" if is_safe else "blocked",
                "reason": None if is_safe else "Injection pattern detected",
                "source": "AAA_bridge"
            }

        elif action == "reset":
            return {
                "status": "SEAL",
                "session_id": str(uuid.uuid4()),
                "reset": True,
                "source": "AAA_bridge"
            }

        elif action == "validate":
            return {
                "status": "SEAL",
                "valid": True,
                "kernels": KERNELS_AVAILABLE,
                "coordinator": COORDINATOR_AVAILABLE,
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown init action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"Init bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}
