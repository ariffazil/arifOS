#!/usr/bin/env python3
"""STAB-2026-08-07 Rule #4: daily liveness probe for all 8 canonical arifOS tools.

Runs each tool with a minimal payload, records pass/fail/expected-hold.
Exit 0 = all healthy, 1 = dead tool found. Intended for cron/systemd-timer.
Rule #8: this is a probe runner, not a predictor — it reports what the
kernel actually returned.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

BASE = "http://127.0.0.1:8088/mcp"

TOOLS = [
    ("arif_init", {"mode": "init", "actor_id": "liveness_probe", "ack_irreversible": False}),
    ("arif_observe", {"subject": "liveness_check", "frame": "ok", "session_id": "liveness_probe"}),
    ("arif_think", {"question": "liveness ping", "session_id": "liveness_probe"}),
    ("arif_route", {"intent": "liveness_check", "session_id": "liveness_probe"}),
    ("arif_memory", {"query": "liveness", "mode": "recall", "session_id": "liveness_probe"}),
    ("arif_judge", {"candidate": "liveness_check", "evidence": {"in_band": True}, "session_id": "liveness_probe"}),
    ("arif_forge", {"action": "liveness_ping", "dry_run": True, "session_id": "liveness_probe"}),
    ("arif_seal", {"receipt": "liveness_check", "session_id": "liveness_probe"}),
]

# Tools expected to HOLD for an anonymous probe — HOLD here means the gate works, not dead.
EXPECTED_HOLD = {"arif_forge", "arif_seal"}


def call(name: str, args: dict, req_id: int = 1) -> dict:
    body = {
        "jsonrpc": "2.0", "id": req_id, "method": "tools/call",
        "params": {"name": name, "arguments": args},
    }
    req = urllib.request.Request(
        BASE, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode()
        try:
            return json.loads(raw)
        except Exception:
            for line in raw.splitlines():
                if line.startswith("data:"):
                    return json.loads(line[5:].strip())
            return {"error": "unparseable response"}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    results: list[dict] = []
    dead: list[str] = []

    for name, args in TOOLS:
        t0 = time.monotonic()
        out = call(name, args)
        elapsed_ms = round((time.monotonic() - t0) * 1000, 1)

        verdict = "UNKNOWN"
        err = out.get("error")
        if err:
            verdict = f"DEAD:{err[:60]}"
        else:
            try:
                txt = (out.get("result", {}).get("content") or [{}])[0].get("text", "")
                p = json.loads(txt)
                verdict = str(p.get("effective_verdict") or p.get("verdict") or "UNKNOWN")
            except Exception:
                verdict = "DEAD:no_verdict_field"

        status = "ok"
        if "DEAD" in verdict:
            status = "dead"
            dead.append(name)
        elif verdict.upper() in ("HOLD", "888_HOLD", "VOID"):
            if name in EXPECTED_HOLD:
                verdict = "EXPECTED_HOLD"
            else:
                # HOLD on a read tool could be a genuine gate — not dead, but flag it
                status = "hold"

        results.append({"tool": name, "verdict": verdict, "latency_ms": elapsed_ms, "status": status})

    report = {
        "ts": now,
        "kernel": BASE,
        "tools_probed": len(TOOLS),
        "dead": dead,
        "results": results,
        "healthy": not dead,
    }
    print(json.dumps(report, indent=1))
    return 0 if report["healthy"] else 1


if __name__ == "__main__":
    sys.exit(main())
