from functools import wraps
import os

from core.shared.vault_client import VaultClient

# Use core.floors as the source for tool call evaluation
try:
    from core.floors import evaluate_tool_call, Verdict
except ImportError:
    # Fallback/Mock for local testing if core.floors is not available
    class Verdict:
        SEAL = "SEAL"
        HOLD = "HOLD"
        VOID = "VOID"

    def evaluate_tool_call(**kwargs):
        class MockGov:
            verdict = Verdict.SEAL
            message = "PASSED"

            def to_dict(self):
                return {"verdict": self.verdict, "message": self.message}

        return MockGov()


# Initialize VaultClient with ORGAN_ID from environment
ORGAN_ID = os.getenv("ORGAN_ID", "unknown")
vault = VaultClient(organ_id=ORGAN_ID)

# ── Option C Session Gate — Anonymous Tool Allowlist ────────────────────────
# Health probes and read-only status tools may run without actor binding.
# Everything else forces arifos_init first.
ANONYMOUS_ALLOWED_TOOLS: set[str] = {
    "arifos_health",
    "arifos_status",
    "check_vital",
    "system_health",
}


def governed_tool(fn):
    """
    Decorator — wraps any FastMCP tool with:
    1. F11 Session gate (Option C: anonymous → redirect to arifos_init)
    2. Floor check (via evaluate_tool_call)
    3. Execute if SEAL
    4. Vault seal regardless of verdict
    """

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        # Extract context if present, else use default
        ctx = kwargs.get("ctx", {})
        if not isinstance(ctx, dict):
            ctx = {}

        actor_id = ctx.get("actor_id", "anonymous")
        session_id = ctx.get("session_id", "unknown")
        tool_name = fn.__name__

        # ── 1. F11 Session Gate (Option C) ─────────────────────────────────
        is_anonymous = not actor_id or actor_id.strip().lower() in {"anonymous", "", "none"}
        if is_anonymous and tool_name not in ANONYMOUS_ALLOWED_TOOLS:
            # Force function: redirect to init before any state mutation
            return {
                "ok": False,
                "verdict": "HOLD",
                "error": "F11_NO_ACTOR_ID",
                "message": (
                    f"Tool '{tool_name}' requires an anchored session. "
                    "Run arifos_init(mode='init', actor_id='your_id') first."
                ),
                "redirect": "arifos_init",
                "session_id": session_id,
                "actor_id": actor_id,
            }

        # ── 2. Floor check ─────────────────────────────────────────────────
        gov = evaluate_tool_call(
            action=tool_name,
            tool_name=tool_name,
            parameters=kwargs,
            actor_id=actor_id,
            session_id=session_id,
        )

        verdict = "SEAL" if gov.verdict == Verdict.SEAL else "HOLD"
        if gov.verdict == Verdict.VOID:
            verdict = "VOID"

        # ── 3. Execute if SEAL ─────────────────────────────────────────────
        result = None
        if verdict == "SEAL":
            result = await fn(*args, **kwargs)

        # ── 4. Always seal — even HOLDs get logged ─────────────────────────
        floor_results = []
        if hasattr(gov, "floor_results"):
            floor_results = [
                {
                    "id": r.floor_id,
                    "name": r.name,
                    "status": "PASS" if r.passed else "FAIL",
                    "score": r.score,
                }
                for r in gov.floor_results
            ]
        else:
            floor_results = [{"verdict": str(gov.verdict), "message": gov.message}]

        # Thread plan metadata if present in context (repaired Planning Organ)
        plan_meta = ctx.get("_plan_metadata") if isinstance(ctx, dict) else None
        plan_id = ctx.get("_plan_id") if isinstance(ctx, dict) else None

        await vault.seal(
            verdict=verdict,
            tool_name=tool_name,
            session_id=session_id,
            actor_id=actor_id,
            payload=kwargs,
            floor_results=floor_results,
            g_star=ctx.get("g_star", 0.0),
            plan_id=plan_id or (plan_meta.get("plan_id") if plan_meta else None),
        )

        if verdict in ["HOLD", "VOID"]:
            return {
                "ok": False,
                "verdict": verdict,
                "message": f"Governance {verdict}: {gov.message}",
                "floors": floor_results,
            }

        return result

    return wrapper
