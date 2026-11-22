"""OS-1 canary (PLAN-2026-11-10-Q1 S3c) — dry-run receipt emission.

Env-gated, default OFF. When ARIFOS_OS1_CANARY=1, every arif_judge /
arif_seal outcome appends ONE arifFlow-receipt-shaped line to the canary
log (ARIFOS_OS1_CANARY_PATH, default /var/lib/arifos/os1_canary.jsonl).
Zero network ingest — the 48h shape/count window runs before live ingest
is ever enabled (S3 spec section 4). Fail-open by design: a canary log
failure must never break the verb it observes (errors go to stderr).
"""
import json
import os
import sys
import time
from functools import wraps

CANARY_ENV = "ARIFOS_OS1_CANARY"
CANARY_PATH_ENV = "ARIFOS_OS1_CANARY_PATH"
DEFAULT_PATH = "/var/lib/arifos/os1_canary.jsonl"

_FLOOR_MAP = {
    "SEAL": "Pass",
    "SABAR": "Caution",
    "HOLD": "Hold",
    "VOID": "Void",
    "PASS": "Pass",
    "CAUTION": "Caution",
}


def emit_dry_run(tool, actor_id, session_id, verdict, mode_param=None, trace_id=None):
    if os.environ.get(CANARY_ENV) != "1":
        return False
    raw = verdict if verdict is not None else "Unknown"
    line = {
        "schema": "arifos.os1-canary/v1",
        "mode": "dry_run",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tool": tool,
        "actor_id": actor_id,
        "session_id": session_id,
        "step_type": "Execute",
        "floor_verdict": _FLOOR_MAP.get(str(raw).upper(), str(raw)),
        "raw_verdict": raw,
        "mode_param": mode_param,
        "trace_id": trace_id,
    }
    try:
        path = os.environ.get(CANARY_PATH_ENV, DEFAULT_PATH)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
        return True
    except Exception as exc:  # canary must never break the verb
        print(f"[os1-canary] emit failed: {exc}", file=sys.stderr)
        return False


def _result_payload(result):
    # 2026-11-18 shape fix: arif_judge/arif_seal handler paths return pydantic
    # models (VerdictOutput / SealOutput via _echo_standing), not dicts — the
    # dict-only ladder never saw their verdict, so 57% of canary rows read
    # Unknown. Normalize pydantic results to a dict once; keep one ladder.
    if isinstance(result, dict):
        return result
    model_dump = getattr(result, "model_dump", None)
    if callable(model_dump):
        try:
            payload = model_dump(mode="json")
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None
    return None


def wrap_mutate_verbs(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        result = await fn(*args, **kwargs)
        try:
            verdict = None
            actor_id = kwargs.get("actor_id")
            session_id = kwargs.get("session_id")
            trace_id = kwargs.get("trace_id")
            payload = _result_payload(result)
            if isinstance(payload, dict):
                verdict = (
                    payload.get("effective_verdict")
                    or payload.get("verdict")
                    or (payload.get("actor") or {}).get("verdict")
                    or payload.get("status")
                )
                # resolved identity (result) outranks the claimed kwargs alias;
                # nested actor{} (judge dict path) or flat actor_id (VerdictOutput)
                actor_id = (
                    (payload.get("actor") or {}).get("actor_id")
                    or payload.get("actor_id")
                    or actor_id
                )
                session_id = payload.get("session_id") or session_id
                trace_id = trace_id or payload.get("trace_id")
            emit_dry_run(
                tool=getattr(fn, "__name__", "unknown"),
                actor_id=actor_id,
                session_id=session_id,
                verdict=verdict,
                mode_param=kwargs.get("mode"),
                trace_id=trace_id,
            )
        except Exception as exc:
            print(f"[os1-canary] wrap failed: {exc}", file=sys.stderr)
        return result

    return wrapper
