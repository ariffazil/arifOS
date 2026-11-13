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


def wrap_mutate_verbs(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        result = await fn(*args, **kwargs)
        try:
            verdict = None
            actor_id = kwargs.get("actor_id")
            session_id = kwargs.get("session_id")
            if isinstance(result, dict):
                verdict = (
                    result.get("effective_verdict")
                    or result.get("verdict")
                    or (result.get("actor") or {}).get("verdict")
                    or result.get("status")
                )
                # resolved identity (result) outranks the claimed kwargs alias
                actor_id = (result.get("actor") or {}).get("actor_id") or actor_id
                session_id = result.get("session_id") or session_id
            emit_dry_run(
                tool=getattr(fn, "__name__", "unknown"),
                actor_id=actor_id,
                session_id=session_id,
                verdict=verdict,
                mode_param=kwargs.get("mode"),
                trace_id=kwargs.get("trace_id") or (result.get("trace_id") if isinstance(result, dict) else None),
            )
        except Exception as exc:
            print(f"[os1-canary] wrap failed: {exc}", file=sys.stderr)
        return result

    return wrapper
