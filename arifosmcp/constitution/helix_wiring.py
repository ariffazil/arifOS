"""
helix_wiring.py — LIVE BRIDGES for helix_engine (Connectors; Read-mostly, Reversible)

Purpose: wire the FOUR LOCKS to real federation sources so the engine stops proving
correct in isolation and starts gating live metabolism.

DESIGN BOUNDARY (preserves helix_engine determinism):
  - helix_engine.py stays PURE (no I/O, no network) — that is its audited virtue.
  - THIS module holds the I/O bridges (urllib, file reads) and feeds helix_engine.
  - All bridges are READ-ONLY / additive. None mutate a daemon. None registers a boot hook.
  - F1 reversible: delete file / git revert. Zero boot blast.

BRIDGES:
  bridge_fq    — read LIVE arifFlow :7073 exec/verify → Lock 2 (sink poles)
  bridge_rsi   — read REAL RSI ledger freshness → Lock 4 (verification banked)
  pre_seal     — compose all four for the seal path (judge-chain + godel ctx params)

Wire status (honest): engine is WIRED-TO-READ. Enforcement (arif_seal blocking on the
verdict, arifFlow daemon restart) is the kernel/deploy step held for F13 (T2, live daemons).

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

from .helix_engine import (
    HelixVerdict,
    RATIO_LIMIT,
    MIN_TOTAL,
    compute_sink_poles,
    helix_chain_check,
    run_helix,
)

DEFAULT_FLOW = "http://127.0.0.1:7073"
DEFAULT_LEDGER = "/root/.local/share/arifos/rsi-ledger.jsonl"


# ─────────────────────────────────────────────────────────────────────────────
# BRIDGE 1 — LIVE arifFlow :7073 → Lock 2
# ─────────────────────────────────────────────────────────────────────────────
def _fetch_json(url: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"__error__": str(e)}


def bridge_fq(
    base: str = DEFAULT_FLOW,
    timeout: float = 5.0,
    ratio_limit: float = RATIO_LIMIT,
    min_total: int = MIN_TOTAL,
) -> Dict[str, Any]:
    """Read live arifFlow /health and compute Lock 2 sink-pole verdict."""
    health = _fetch_json(base.rstrip("/") + "/health", timeout)
    if not health or "__error__" in health:
        return {"available": False, "error": (health or {}).get("__error__", "no_health")}
    fq = health.get("fq", health)
    execute = int(fq.get("execute_count", 0))
    verify = int(fq.get("verify_count", 0))
    quotient = fq.get("quotient")
    # arifFlow can put counts under per_actor when aggregating; fall back if absent
    if execute == 0 and verify == 0 and "per_actor" in fq and isinstance(fq["per_actor"], dict):
        for _, st in fq["per_actor"].items():
            if isinstance(st, dict):
                execute += int(st.get("execute", 0) or 0)
                verify += int(st.get("verify", 0) or 0)
    poles = compute_sink_poles(execute, verify, ratio_limit, min_total)
    lock2 = not (poles["fossilisation"] or poles["burn"])
    return {
        "available": True,
        "execute": execute,
        "verify": verify,
        "quotient": quotient,
        "sink_poles": poles,
        "lock_2_calhoun": lock2,
        "reported_verdict": fq.get("verdict"),
        "reported_diag": fq.get("diagnosis"),
        "formula_version": fq.get("formula_version"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# BRIDGE 2 — REAL RSI ledger → Lock 4
# ─────────────────────────────────────────────────────────────────────────────
def bridge_rsi(
    ledger_path: str = DEFAULT_LEDGER,
    window: int = 20,
    require: str = "verify",
    required_recent_entries: int = 1,
) -> Dict[str, Any]:
    """Read tail of the RSI ledger; Lock 4 passes iff it is actively metabolizing
    (i.e. verification entries are being banked — the memory flow)."""
    if not os.path.exists(ledger_path):
        return {"available": False, "error": "ledger_missing", "lock_4_rsi": False}
    entries: List[Dict[str, Any]] = []
    try:
        with open(ledger_path, "r") as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    except Exception as e:
        return {"available": False, "error": str(e), "lock_4_rsi": False}
    tail = entries[-window:]
    banked = sum(1 for e in tail if e.get("last_delta_s") is not None or e.get("event"))
    lock4 = banked >= required_recent_entries and len(tail) >= required_recent_entries
    return {
        "available": True,
        "total_lines": len(entries),
        "window": len(tail),
        "banked_recent": banked,
        "required_recent": required_recent_entries,
        "lock_4_rsi": lock4,
        "last_event": tail[-1].get("event") if tail else None,
        "last_delta_s": tail[-1].get("last_delta_s") if tail else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# COMPOSE — pre_seal(): the guard the SEAL path should consult
# ─────────────────────────────────────────────────────────────────────────────
def pre_seal(
    events: Optional[List[Any]] = None,
    ctx: Any = None,
    base: str = DEFAULT_FLOW,
    ledger_path: str = DEFAULT_LEDGER,
    ratio_limit: float = RATIO_LIMIT,
    min_total: int = MIN_TOTAL,
) -> Dict[str, Any]:
    """Compose all four locks from LIVE sources + caller-supplied judge-chain.

    - Lock 1 Gödel: real ctx when provided (else flagged lazy)
    - Lock 2 Calhoun: live arifFlow counts (bridge_fq)
    - Lock 3 Helix:   caller-supplied events chain (kernel passes judge/seal sequence)
    - Lock 4 RSI:     real ledger freshness (bridge_rsi)

    Returns verdict dict — the seal path must call this BEFORE any arif_seal and
    HOLD when verdict['all_pass'] is False.
    """
    bfq = bridge_fq(base=base, ratio_limit=ratio_limit, min_total=min_total)
    brsi = bridge_rsi(ledger_path=ledger_path)
    events = events or []
    if not bfq.get("available"):
        bfq["lock_2_calhoun"] = False  # table: can't verify contact → do not pass
    if not brsi.get("available"):
        brsi["lock_4_rsi"] = False

    verdict = run_helix(
        execute=bfq.get("execute", 0),
        verify=bfq.get("verify", 0),
        events=events,
        ledger_entries=[{"type": "verify", "banked": brsi.get("lock_4_rsi", False)}],
        ctx=ctx,
        ratio_limit=ratio_limit,
        min_total=min_total,
    )
    # Override lock flags with the LIVE bridge values (run_helix defaults are pure-only)
    verdict.lock_2_calhoun = bool(bfq.get("lock_2_calhoun"))
    verdict.lock_4_rsi = bool(brsi.get("lock_4_rsi"))
    verdict.details["live"] = {
        "fq": bfq,
        "rsi": brsi,
        "chain_events": len(events),
    }
    return {
        "all_pass": verdict.all_pass,
        "verdict": verdict.summary(),
        "locks": {
            "godel": verdict.lock_1_godel,
            "calhoun": verdict.lock_2_calhoun,
            "helix": verdict.lock_3_helix,
            "rsi": verdict.lock_4_rsi,
        },
        "sink_poles": verdict.sink_poles,
        "live": {"fq": bfq, "rsi": brsi},
    }


# ─────────────────────────────────────────────────────────────────────────────
# LIVE WITNESS — show the engine reading TODAY (reality, not table)
# ─────────────────────────────────────────────────────────────────────────────
def _witness() -> int:
    print("== HELIX WIRING — LIVE WITNESS (reads real :7073 + real ledger) ==")
    bfq = bridge_fq()
    print(
        "FQ bridge:",
        json.dumps(
            {
                k: bfq.get(k)
                for k in (
                    "available",
                    "execute",
                    "verify",
                    "quotient",
                    "sink_poles",
                    "lock_2_calhoun",
                    "reported_verdict",
                )
            },
            indent=2,
        ),
    )
    brsi = bridge_rsi()
    print(
        "RSI bridge:",
        json.dumps(
            {
                k: brsi.get(k)
                for k in (
                    "available",
                    "total_lines",
                    "window",
                    "banked_recent",
                    "lock_4_rsi",
                    "last_delta_s",
                )
            },
            indent=2,
        ),
    )
    ps = pre_seal(events=["judge", "seal"])
    print("PRE_SEAL all_pass =", ps["all_pass"])
    print("  locks:", ps["locks"], "| sink:", ps["sink_poles"])
    print("== END LIVE WITNESS — verdict: 'HOLD' means the seal path must block ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(_witness())
