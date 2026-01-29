"""
arifOS Pure Bridge (v52.0.0)
Authority: Muhammad Arif bin Fazil
Principle: Zero Logic Delegation (F1)

"I do not think, I only wire."

The bridge is a zero-logic adapter between the transport layer (SSE/STDIO)
and the arifOS cores (AGI/ASI/APEX).
"""

from __future__ import annotations
import logging
import time
from typing import Any, Optional

from codebase.mcp.constitutional_metrics import store_stage_result, get_stage_result
from codebase.mcp.tools.trinity_validator import validate_trinity_request
from codebase.mcp.tools import reality_grounding
from codebase.mcp.external_gateways.brave_client import BraveSearchClient

# Initialize logger
logger = logging.getLogger(__name__)

# --- CORE AVAILABILITY ---
try:
    from codebase.kernel import get_kernel_manager

    ENGINES_AVAILABLE = True
except ImportError:
    logger.warning("arifOS Cores unavailable - Bridge in degraded mode")

    def get_kernel_manager():
        return None

    ENGINES_AVAILABLE = False


# --- ERROR CATEGORIZATION ---
class BridgeError(Exception):
    """Base class for bridge errors."""

    def __init__(self, message: str, category: str = "FATAL", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.category = category
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            "status": "VOID",
            "verdict": "VOID",
            "error_category": self.category,
            "reason": self.message,
            "status_code": self.status_code,
        }


_FALLBACK_RESPONSE = BridgeError("arifOS Cores unavailable", "FATAL", 503).to_dict()


# --- UTILS ---
def _serialize(obj: Any) -> Any:
    """Zero-logic serialization for transport."""
    if obj is None:
        return None
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    # Handle dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(obj)
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "value") and not isinstance(obj, (int, float, str, bool)):
        return obj.value
    if isinstance(obj, (str, int, float, bool)):
        return obj
    # For objects without serialization, convert to dict if possible
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return str(obj)


# --- ROUTERS ---


async def bridge_init_router(action: str = "init", **kwargs) -> dict:
    """Pure bridge: Initialize session via kernel manager."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        manager = get_kernel_manager()
        if manager is None:
            raise BridgeError("Kernel manager not initialized.", "ENGINE_FAILURE", 500)
        result = await manager.init_session(action, kwargs)
        serialized = _serialize(result)
        session_id = (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
        if session_id:
            store_stage_result(str(session_id), "init", serialized)
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"Init Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_agi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route reasoning tasks to AGI Genius.
    Adapts Contrast Actions: predict, measure -> think, evaluate
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        kernel = get_kernel_manager().get_agi()
        if kernel is None:
            raise BridgeError("AGI Kernel not available.", "ENGINE_FAILURE", 500)

        # --- CONTRAST ADAPTERS ---
        if action in ["predict", "physics"]:
            # Transform "predict"/"physics" -> "think" (Reasoning/Modelling)
            kwargs["thought"] = (
                f"Reasoning Mode ({action}): Model reality for '{kwargs.get('query', '')}'"
            )
            action = "think"
        elif action in ["measure", "math"]:
            # Transform "measure"/"math" -> "evaluate" (Quantification)
            action = "evaluate"
        elif action == "language":
            # Transform "language" -> "forge" (Projection/Execution)
            action = "forge"

        serialized = _serialize(await kernel.execute(action, kwargs))
        session_id = (
            kwargs.get("session_id") or (serialized or {}).get("session_id")
            if isinstance(serialized, dict)
            else None
        )
        if session_id and isinstance(serialized, dict):
            store_stage_result(str(session_id), "agi", serialized)
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"AGI Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_atlas_router(**kwargs) -> dict:
    """Pure bridge: Route mapping tasks to Atlas tool."""
    try:
        from arifOS_Implementation.SKILL_2.mcp_tool_templates import _atlas_
        
        result = await _atlas_(**kwargs)
        serialized = _serialize(result)
        
        session_id = kwargs.get("session_id")
        if session_id and isinstance(serialized, dict):
            store_stage_result(str(session_id), "atlas", serialized)
            
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"Atlas Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()




async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route ethical tasks to ASI Heart Kernel."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        kernel = get_kernel_manager().get_asi()
        if kernel is None:
            raise BridgeError("ASI Kernel not available.", "ENGINE_FAILURE", 500)

        # --- CONTRAST ADAPTERS ---
        if action == "harmonize":
            action = "align"
            kwargs["proposal"] = "Harmonization: Seek win-win resolution."
        elif action == "physics":
            # Physics -> Empathize (Modelling Emotional Reality)
            action = "empathize"
        elif action in ["measure", "math"]:
            # Math -> Evaluate (Scoring Peace/Empathy)
            action = "evaluate"
        elif action == "language":
            # Language -> Act (Execution)
            action = "act"

        serialized = _serialize(await kernel.execute(action, kwargs))
        session_id = (
            kwargs.get("session_id") or (serialized or {}).get("session_id")
            if isinstance(serialized, dict)
            else None
        )
        if session_id and isinstance(serialized, dict):
            store_stage_result(str(session_id), "asi", serialized)
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"ASI Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


# --- v53 ASI COMPONENT ROUTERS ---
async def bridge_asi_stakeholder_router(**kwargs) -> dict:
    """Route A1 Semantic Stakeholder Reasoning."""
    try:
        return await bridge_asi_router(action="semantic_stakeholder_reasoning", **kwargs)
    except Exception as e:
        logger.error(f"ASI Stakeholder Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_asi_diffusion_router(**kwargs) -> dict:
    """Route A2 Impact Diffusion."""
    try:
        return await bridge_asi_router(action="impact_diffusion_peace_squared", **kwargs)
    except Exception as e:
        logger.error(f"ASI Diffusion Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_asi_audit_router(**kwargs) -> dict:
    """Route A3 Constitutional Audit."""
    try:
        return await bridge_asi_router(action="constitutional_audit_sink", **kwargs)
    except Exception as e:
        logger.error(f"ASI Audit Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_apex_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route judicial tasks to APEX Judge."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        kernel = get_kernel_manager().get_apex()
        if kernel is None:
            raise BridgeError("APEX Kernel not available.", "ENGINE_FAILURE", 500)

        # --- CONTRAST ADAPTERS ---
        if action == "redeem":
            action = "eureka"
        elif action == "physics":
            # Physics -> Judge (Reasoning about Law/Reality)
            action = "judge"
        elif action in ["measure", "math"]:
            # Math -> Entropy (Scoring Confidence)
            action = "entropy"
        elif action == "language":
            # Language -> Judge (Verdict Projection)
            action = "judge"

        serialized = _serialize(await kernel.execute(action, kwargs))
        session_id = (
            kwargs.get("session_id") or (serialized or {}).get("session_id")
            if isinstance(serialized, dict)
            else None
        )
        if session_id and isinstance(serialized, dict):
            store_stage_result(str(session_id), "apex", serialized)
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"APEX Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_vault_router(action: str = "seal", **kwargs) -> dict:
    """Pure bridge: Route archival tasks to VAULT-999."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        # Vault operations are part of the APEX Judicial Kernel in v52
        kernel = get_kernel_manager().get_apex()
        if kernel is None:
            raise BridgeError("APEX Kernel for Vault not available.", "ENGINE_FAILURE", 500)

        serialized = _serialize(await kernel.execute(action, kwargs))
        session_id = (
            kwargs.get("session_id") or (serialized or {}).get("session_id")
            if isinstance(serialized, dict)
            else None
        )
        if session_id and isinstance(serialized, dict):
            store_stage_result(str(session_id), "apex", serialized)
        return serialized if isinstance(serialized, dict) else {"result": serialized}
    except Exception as e:
        logger.error(f"Vault Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


# --- EXTERNAL GATEWAY ROUTING ---


class CircuitBreaker:
    """Simple circuit breaker for external gateways."""

    def __init__(self, failure_threshold: int = 3, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"⚠️ Circuit Breaker OPENED after {self.failures} failures.")

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF-OPEN"
                return True
            return False
        return True


class BridgeRouter:
    """Manages routing between MCP tools and external reality gateways."""

    def __init__(self, brave_key: Optional[str] = None):
        import os

        self.brave = BraveSearchClient(brave_key or os.environ.get("BRAVE_API_KEY"))
        self.brave_cb = CircuitBreaker(failure_threshold=3, reset_timeout=300)

    async def route_reality_check(
        self, query: str, session_id: Optional[str] = None, **kwargs
    ) -> dict:
        """Route reality-grounding queries to Brave Search."""
        if not self.brave_cb.can_execute():
            return BridgeError(
                "External Reality Gateway (Brave) is temporarily down (Circuit Open).",
                "TRANSIENT",
                503,
            ).to_dict()

        try:
            # Get authority and intent from init stage
            stage_result = get_stage_result(session_id, "init") if session_id else {}
            init_result = stage_result if stage_result is not None else {}
            lane = init_result.get("lane", "SOFT")
            intent = init_result.get("intent", "explain")
            scar_weight = init_result.get("scar_weight", 0.0)

            should_check, reason = reality_grounding.should_reality_check(
                query, lane, intent, scar_weight
            )

            if should_check is False:
                return {
                    "status": "SEAL",
                    "verdict": "SEAL",
                    "source": "local_memory",
                    "reason": reason,
                    "note": "Query handled by internal models/knowledge.",
                }

            # Call Brave
            result = await self.brave.search(query, intent, scar_weight)
            self.brave_cb.record_success()
            return _serialize(result)
        except Exception as e:
            self.brave_cb.record_failure()
            logger.error(f"Reality Check Error: {e}")
            return BridgeError(str(e), "EXTERNAL_GATEWAY_FAILURE", 502).to_dict()


# Singleton Bridge instance for external gateways
_ROUTER = None


def get_bridge_router():
    global _ROUTER
    if not _ROUTER:
        _ROUTER = BridgeRouter()
    return _ROUTER


async def bridge_reality_check_router(**kwargs) -> dict:
    """Gateway for reality_check tool."""
    return await get_bridge_router().route_reality_check(**kwargs)


async def bridge_trinity_loop_router(
    query: str, session_id: Optional[str] = None, **kwargs
) -> dict:
    """
    Trinity Metabolic Loop: Complete AGI→ASI→APEX pipeline.
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    try:
        import time

        start_time = time.time()

        # Step 1: Initialize session if needed
        if not session_id:
            init_result = await bridge_init_router(action="init", query=query)
            session_id = init_result.get("session_id", f"trinity_{int(time.time())}")
        else:
            init_result = get_stage_result(session_id, "init") or {}

        # NEW: Phase B Gating (v53.2.2)
        lane = init_result.get("lane", "SOFT")
        scar_weight = init_result.get("scar_weight", 0.0)

        allowed, reason = validate_trinity_request(query, lane, scar_weight)
        if not allowed:
            return {
                "verdict": "VOID" if lane != "CRISIS" else "888_HOLD",
                "status": "VOID" if lane != "CRISIS" else "888_HOLD",
                "reason": f"Validation Gate: {reason}",
                "session_id": session_id,
                "lane": lane,
                "scar_weight": scar_weight,
            }

        loop_results = []

        # Step 2: AGI Genius Pipeline
        agi_result = await bridge_agi_router(action="full", query=query, session_id=session_id)
        loop_results.append({"stage": "agi", "result": agi_result})

        if isinstance(agi_result, dict) and agi_result.get("verdict") == "VOID":
            return {
                "verdict": "VOID",
                "reason": f"AGI veto: {agi_result.get('reason', 'Unknown')}",
                "session_id": session_id,
                "stages": loop_results,
            }

        # Step 3: ASI Act Pipeline
        asi_result = await bridge_asi_router(
            action="full",
            text=agi_result.get("reasoning", str(agi_result)),
            query=query,
            session_id=session_id,
            agi_context=agi_result,
        )
        loop_results.append({"stage": "asi", "result": asi_result})

        if isinstance(asi_result, dict) and asi_result.get("verdict") == "VOID":
            return {
                "verdict": "VOID",
                "reason": f"ASI veto: {asi_result.get('reason', 'Ethical violation')}",
                "session_id": session_id,
                "stages": loop_results,
            }

        # Step 3b: 333 FORGE — Paradox Resolution (v53.5.0 — TrinitySyncHardened)
        try:
            from codebase.agi.trinity_sync_hardened import synthesize_paradox, compute_trinity_score

            agi_confidence = agi_result.get("truth_score", 0.9) if isinstance(agi_result, dict) else 0.9
            asi_empathy = asi_result.get("empathy_kappa", asi_result.get("empathy_kappa_r", 0.9)) if isinstance(asi_result, dict) else 0.9
            asi_peace = asi_result.get("peace_squared", 1.0) if isinstance(asi_result, dict) else 1.0

            paradox_scores = {
                "truth_care": synthesize_paradox(agi_confidence, asi_empathy),
                "clarity_peace": synthesize_paradox(1.0 - abs(agi_result.get("entropy_delta", 0.0)) if isinstance(agi_result, dict) else 0.9, asi_peace),
                "knowledge_wisdom": synthesize_paradox(agi_confidence, asi_empathy),
                "speed_safety": synthesize_paradox(0.9, asi_peace),
                "emotion_logic": synthesize_paradox(agi_confidence, asi_empathy),
                "openness_guard": synthesize_paradox(0.9, asi_empathy),
            }

            trinity_score = compute_trinity_score(list(paradox_scores.values()), method="geometric")
            min_paradox = min(paradox_scores.values()) if paradox_scores else 0.9

            loop_results.append({
                "stage": "333_forge",
                "result": {
                    "paradox_scores": paradox_scores,
                    "trinity_score": trinity_score,
                    "min_paradox_score": min_paradox,
                    "synthesis": "SEAL" if min_paradox >= 0.85 else "PARTIAL" if min_paradox >= 0.70 else "VOID",
                    "_source": "TrinitySyncHardened",
                },
            })

            if min_paradox < 0.70:
                return {
                    "verdict": "VOID",
                    "reason": f"333 FORGE: Paradox resolution failed (min={min_paradox:.3f}, trinity={trinity_score:.3f})",
                    "session_id": session_id,
                    "stages": loop_results,
                    "paradox_scores": paradox_scores,
                }
        except Exception as paradox_err:
            logger.warning(f"333 FORGE paradox resolution skipped: {paradox_err}")

        # Step 4: APEX Judge Pipeline
        apex_result = await bridge_apex_router(
            action="full",
            query=query,
            response=str(agi_result),
            session_id=session_id,
            reasoning=agi_result.get("reasoning", ""),
            safety_evaluation=asi_result,
        )
        loop_results.append({"stage": "apex", "result": apex_result})

        final_verdict = (
            apex_result.get("verdict", "SEAL") if isinstance(apex_result, dict) else "SEAL"
        )

        # Step 5: Vault Seal (only if SEAL verdict)
        if final_verdict == "SEAL":
            vault_result = await bridge_vault_router(
                action="seal",
                session_id=session_id,
                verdict=final_verdict,
                query=query,
                response=str(apex_result),
                decision_data={"agi": agi_result, "asi": asi_result, "apex": apex_result},
            )
            loop_results.append({"stage": "vault", "result": vault_result})

        duration = time.time() - start_time

        return {
            "verdict": final_verdict,
            "session_id": session_id,
            "query": query,
            "reasoning": apex_result.get("reasoning", "")
            if isinstance(apex_result, dict)
            else str(apex_result),
            "stages": loop_results,
            "duration_ms": duration * 1000,
            "loops_completed": len(loop_results),
        }
    except Exception as e:
        logger.error(f"Trinity Loop Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_context_docs_router(query: str, **kwargs) -> dict:
    """Pure bridge: Route documentation queries to 000_THEORY index."""
    try:
        from pathlib import Path

        theory_path = Path("c:/Users/ariff/arifOS/000_THEORY")
        if not theory_path.exists():
            theory_path = Path("./000_THEORY")

        docs = []
        if theory_path.exists():
            # Basic search for relevant files
            q = query.upper()
            for f in theory_path.glob("*.md"):
                if q in f.name.upper():
                    docs.append({"name": f.name, "path": str(f.absolute())})

        if docs:
            return {
                "status": "SEAL",
                "verdict": "SEAL",
                "docs_found": len(docs),
                "list": docs,
                "note": f"Found {len(docs)} matching documents in 000_THEORY.",
            }

        return {
            "status": "SEAL",
            "verdict": "SEAL",
            "query": query,
            "content": f"No specific documentation found for '{query}' in 000_THEORY index.",
            "source": "theory_bridge",
        }
    except Exception as e:
        logger.error(f"Context Docs Error: {e}")
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()


async def bridge_prompt_router(action: str, user_input: str, **kwargs) -> dict:
    """Pure bridge: Route prompt codec tasks via PromptCodec."""
    try:
        from codebase.prompt.codec import SignalExtractor, ResponseFormatter, EngineRoute

        if action == "route" or action == "decode":
            extractor = SignalExtractor()
            signal = extractor.extract(user_input)
            return {
                "status": "SEAL",
                "verdict": "SEAL",
                "signal": signal.to_dict(),
            }
        elif action == "encode":
            formatter = ResponseFormatter()
            # Expecting verdict, floor, reason, engine in kwargs
            verdict = kwargs.get("verdict", "SEAL")
            floor = kwargs.get("floor", "F1_Amanah")
            reason = kwargs.get("reason", "Standard alignment")
            engine_str = kwargs.get("engine", "agi")

            # Convert engine string to EngineRoute enum
            try:
                engine = EngineRoute(engine_str)
            except ValueError:
                engine = EngineRoute.AGI

            response = formatter.encode_response(verdict, floor, reason, engine)
            return {
                "status": "SEAL",
                "verdict": "SEAL",
                "response": response.to_dict(),
            }
        else:
            return BridgeError(f"Unknown prompt action: {action}", "INVALID_INPUT").to_dict()

    except Exception as e:
        logger.error(f"Prompt Router Error: {e}")
        if isinstance(e, BridgeError):
            return e.to_dict()
        return BridgeError(str(e), "ENGINE_FAILURE").to_dict()
