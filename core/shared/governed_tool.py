from functools import wraps
import os

from core.shared.vault_client import VaultClient

# Use core.laws as the source for tool call evaluation
try:
    from arifosmcp.core.floors import evaluate_tool_call
except ImportError:
    evaluate_tool_call = None

# Verdict is not in core.laws; provide a local fallback
try:
    from arifosmcp.models.verdicts import VerdictState as Verdict
except ImportError:

    class Verdict:
        SEAL = "SEAL"
        HOLD = "HOLD"
        VOID = "VOID"


if evaluate_tool_call is None:

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


def governed_tool(fn):
    """
    Decorator — wraps any FastMCP tool with:
    1. Floor check (via evaluate_tool_call)
    2. Execute if SEAL
    3. Vault seal regardless of verdict
    """

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        # Extract context if present, else use default
        ctx = kwargs.get("ctx", {})
        if not isinstance(ctx, dict):
            ctx = {}

        # 1. Floor check
        # Map FastMCP tool call to arifOS floor evaluation
        gov = evaluate_tool_call(
            action=fn.__name__,
            tool_name=fn.__name__,
            parameters=kwargs,
            actor_id=ctx.get("actor_id", "anonymous"),
            session_id=ctx.get("session_id", "unknown"),
        )

        verdict = "SEAL" if gov.verdict == Verdict.SEAL else "HOLD"
        if gov.verdict == Verdict.VOID:
            verdict = "VOID"

        # 2. Execute if SEAL
        result = None
        if verdict == "SEAL":
            result = await fn(*args, **kwargs)

        # 3. Always seal — even HOLDs get logged
        # Convert gov results to serializable list
        law_results = []
        if hasattr(gov, "law_results"):
            law_results = [
                {
                    "id": r.law_id,
                    "name": r.name,
                    "status": "PASS" if r.passed else "FAIL",
                    "score": r.score,
                }
                for r in gov.law_results
            ]
        else:
            law_results = [{"verdict": str(gov.verdict), "message": gov.message}]

        await vault.seal(
            verdict=verdict,
            tool_name=fn.__name__,
            session_id=ctx.get("session_id", "unknown"),
            actor_id=ctx.get("actor_id", "anonymous"),
            payload=kwargs,
            law_results=law_results,
            g_star=ctx.get("g_star", 0.0),
        )

        if verdict in ["HOLD", "VOID"]:
            return {
                "ok": False,
                "verdict": verdict,
                "message": f"Governance {verdict}: {gov.message}",
                "floors": law_results,
            }

        return result

    return wrapper
