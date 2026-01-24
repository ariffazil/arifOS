"""
AAA Bridge: Application <-> Core Adapter (v51.2.0)
Pure Serialization Layer - Zero Logic.

Law: "I do not think, I only wire."

The bridge NEVER makes verdicts. It routes to kernels and returns their output.
All governance decisions belong to the core.

DITEMPA BUKAN DIBERI
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

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
    """000_init: Session management. Returns kernel availability."""
    import uuid, time
    session_id = kw.get("session_id") or str(uuid.uuid4())
    return {
        "session_id": session_id,
        "timestamp": time.time(),
        "engines_available": ENGINES_AVAILABLE,
        "action": action,
    }


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
