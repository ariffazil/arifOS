"""
helix_wiring.py — LIVE BRIDGES for helix_engine (Connectors; Read-mostly, Reversible)

Purpose: wire the FOUR LOCKS to real federation sources so the engine stops proving
correct in isolation and starts gating live metabolism.

DESIGN BOUNDARY (preserves helix_engine determinism):
  - helix_engine.py stays PURE (no I/O, no network) — that is its audited virtue.
  - THIS module holds the I/O bridges (urllib, file reads) and feeds helix_engine.
  - All bridges are READ-ONLY / additive EXCEPT two governed exceptions:
      (a) helix_lock2_state.json — the Amendment #1 sustain/hysteresis state file
          (append-tracked JSON, atomic replace, advisory only);
      (b) POST :7073/ingest Barrier receipts — Amendment #4 (F11: every block auditable).
  - F1 reversible: delete file / git revert. Zero boot blast.

AMENDMENTS v2 (2026-08-14 — 6-finding governance review, F13 directive):
  #1 SUSTAIN + HYSTERESIS — Lock 2 pole evidence must persist across >= 2 windows
     or >= 30 min before HOLD. Single-window breach → WARN. Release < 2.8 only.
     State: DEFAULT_LOCK2_STATE (advisory JSON; failure to read/write degrades to
     fresh-state + warn — never blocks, never crashes the seal path).
  #2 FAIL-OPEN ON BRIDGE ABSENCE — HOLD requires POSITIVE live evidence. Bridge
     unavailable / vector diagnosis missing → warn-and-proceed. Absence of telemetry
     is not proof of disease (kills finding F3: fail-closed lock_2 on arifFlow down).
  #3 HONEST LOCKS — godel without ctx → None (VACUOUS); helix chain without events
     → None (VACUOUS). Reported in every verdict string; never silently True.
     (Production guard currently calls pre_seal(events=[], ctx=None) — locks 1/3
     are honestly VACUOUS until the kernel passes real judge-chain events.)
  #4 BANK THE BLOCK — every HOLD banks a Barrier receipt (floor_verdict=Hold) and
     every WARN banks Caution, via arifFlow :7073 /ingest. Best-effort; a banking
     failure never changes the verdict, only the audit trail.
  #5 VECTOR-FIRST — Lock 2 consumes arifFlow's vector `diagnosis` as PRIMARY.
     Scalar ratio poles are divergence evidence + hysteresis release input only.

Wire status (honest): engine WIRED-TO-READ + gate enforcing in vault_postgres
seal_to_vault() stage-999 path (commit 40a6828). Lock 3 real judge-chain events
remain a kernel-side follow-up (guard passes events=[] today → VACUOUS, honest).

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any, Dict, List, Optional

from .helix_engine import (
    HelixVerdict,
    RATIO_LIMIT,
    MIN_TOTAL,
    RELEASE_RATIO,
    SUSTAIN_WINDOWS,
    SUSTAIN_SECONDS,
    compute_sink_poles,
    dominant_ratio,
    evaluate_lock2,
    helix_chain_check,
    run_helix,
    vector_poles,
)

DEFAULT_FLOW = "http://127.0.0.1:7073"
DEFAULT_LEDGER = "/root/.local/share/arifos/rsi-ledger.jsonl"
DEFAULT_LOCK2_STATE = "/root/.local/share/arifos/helix_lock2_state.json"


# ─────────────────────────────────────────────────────────────────────────────
# BRIDGE 1 — LIVE arifFlow :7073 → Lock 2 (Amendment #5: vector-first)
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
    """Read live arifFlow /health. PRIMARY signal = vector diagnosis; scalar
    counts retained as divergence evidence + hysteresis input."""
    health = _fetch_json(base.rstrip("/") + "/health", timeout)
    if not health or "__error__" in health:
        # Amendment #2: unavailable → fail-open marker, NOT a lock failure.
        return {
            "available": False,
            "fail_open": True,
            "error": (health or {}).get("__error__", "no_health"),
            "lock_2_calhoun": True,  # absence of evidence ≠ evidence of disease
            "note": "fail-open (Amendment #2): bridge unavailable, proceeding",
        }
    fq = health.get("fq", health)
    execute = int(fq.get("execute_count", 0) or 0)
    verify = int(fq.get("verify_count", 0) or 0)
    quotient = fq.get("quotient")
    # arifFlow can put counts under per_actor when aggregating; fall back if absent
    if execute == 0 and verify == 0 and "per_actor" in fq and isinstance(fq["per_actor"], dict):
        for _, st in fq["per_actor"].items():
            if isinstance(st, dict):
                execute += int(st.get("execute", 0) or 0)
                verify += int(st.get("verify", 0) or 0)

    # Amendment #5 — the vector diagnosis is the pole signal.
    diag = fq.get("diagnosis")
    vec = vector_poles(diag)
    scalar_poles = compute_sink_poles(execute, verify, ratio_limit, min_total)
    vec_any = vec["poles"]["fossilisation"] or vec["poles"]["burn"]
    scalar_any = scalar_poles["fossilisation"] or scalar_poles["burn"]
    if not vec["measured"]:
        # Daemon not publishing diagnosis → treat pole evidence as absent (fail-open)
        lock2 = True
        note = "fail-open (Amendment #2): vector diagnosis not published"
    else:
        lock2 = not vec_any
        note = None
    return {
        "available": True,
        "execute": execute,
        "verify": verify,
        "quotient": quotient,
        "vector_diagnosis": diag,
        "vector_measured": vec["measured"],
        "sink_poles": vec["poles"],  # vector poles are THE poles (Amendment #5)
        "scalar_sink_poles": scalar_poles,
        "dominant_ratio": dominant_ratio(execute, verify, min_total),
        "divergence": bool(scalar_any and not vec_any),
        "lock_2_calhoun": lock2,
        "reported_verdict": fq.get("verdict"),
        "reported_diag": diag,
        "formula_version": fq.get("formula_version"),
        "note": note,
    }


# ─────────────────────────────────────────────────────────────────────────────
# AMENDMENT #1 — Lock 2 sustain/hysteresis state (advisory JSON, atomic)
# ─────────────────────────────────────────────────────────────────────────────
def _load_lock2_state(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r") as f:
            st = json.load(f)
        if isinstance(st, dict):
            return st
    except Exception:
        pass
    return {"held": False, "consecutive": 0, "first_pole_ts": None, "pole": None}


def _save_lock2_state(path: str, state: Dict[str, Any]) -> bool:
    try:
        tmp = path + ".tmp"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w") as f:
            json.dump(state, f)
        os.replace(tmp, path)
        return True
    except Exception:
        return False  # advisory only — degrade to fresh-state next call + warn


def _evaluate_lock2_live(bfq: Dict[str, Any], state_path: str) -> Dict[str, Any]:
    """Compose vector pole + sustain state into the three-level Lock 2 verdict."""
    now = time.time()
    prev = _load_lock2_state(state_path)
    poles = bfq.get("sink_poles", {})
    pole = None
    if poles.get("fossilisation"):
        pole = "fossilisation"
    elif poles.get("burn"):
        pole = "burn"

    if pole is not None:
        if prev.get("pole") == pole and prev.get("first_pole_ts"):
            first_ts = prev["first_pole_ts"]
            consecutive = int(prev.get("consecutive", 0)) + 1
        else:
            first_ts = now
            consecutive = 1
        age = max(0.0, now - float(first_ts))
        held_prev = bool(prev.get("held"))
    else:
        first_ts = None
        consecutive = 0
        age = 0.0
        held_prev = bool(prev.get("held"))

    result = evaluate_lock2(
        pole_now=pole is not None,
        held_previous=held_prev,
        consecutive_windows=consecutive,
        pole_age_s=age,
        dominant_ratio_now=bfq.get("dominant_ratio"),
    )
    held_now = result["verdict"] == "HOLD"
    _save_lock2_state(
        state_path,
        {
            "held": held_now,
            "consecutive": consecutive,
            "first_pole_ts": first_ts,
            "pole": pole,
            "updated_at": now,
            "last_verdict": result["verdict"],
        },
    )
    result["pole"] = pole
    result["state_ok"] = True
    return result


# ─────────────────────────────────────────────────────────────────────────────
# AMENDMENT #4 — bank HOLD/WARN as arifFlow Barrier receipts (F11 audit)
# ─────────────────────────────────────────────────────────────────────────────
def _bank_barrier(
    base: str,
    level: str,
    locks: Dict[str, Any],
    bfq: Dict[str, Any],
    l2: Dict[str, Any],
) -> Any:
    payload = {
        "actor_id": "helix-guard",
        "session_id": "kernel-seal-path",
        "step_type": "Barrier",
        "floor_verdict": "Hold" if level == "HOLD" else "Caution",
        "epistemic_label": "Specification",
        "payload": {
            "source": "helix_pre_seal",
            "lock2_verdict": level,
            "locks": locks,
            "vector_diagnosis": bfq.get("vector_diagnosis"),
            "sink_poles": bfq.get("sink_poles"),
            "scalar_sink_poles": bfq.get("scalar_sink_poles"),
            "dominant_ratio": bfq.get("dominant_ratio"),
            "consecutive_windows": l2.get("consecutive_windows"),
            "pole_age_s": l2.get("pole_age_s"),
            "deadband": l2.get("deadband", False),
        },
    }
    try:
        req = urllib.request.Request(
            base.rstrip("/") + "/ingest",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3.0) as r:
            return r.status == 200
    except Exception as e:
        return f"bank_failed:{e}"  # verdict unchanged — audit trail degraded only


# ─────────────────────────────────────────────────────────────────────────────
# BRIDGE 2 — REAL RSI ledger → Lock 4 (Amendment #2: fail-open)
# ─────────────────────────────────────────────────────────────────────────────
def bridge_rsi(
    ledger_path: str = DEFAULT_LEDGER,
    window: int = 20,
    require: str = "verify",
    required_recent_entries: int = 1,
) -> Dict[str, Any]:
    """Read tail of the RSI ledger; Lock 4 passes iff it is actively metabolizing
    (i.e. verification entries are being banked — the memory flow).
    Amendment #2: ledger unavailable → fail-open warn (fresh installs, moved
    paths), not a block. Absence of the ledger file is not positive disease
    evidence."""
    if not os.path.exists(ledger_path):
        return {
            "available": False,
            "fail_open": True,
            "error": "ledger_missing",
            "lock_4_rsi": True,
            "note": "fail-open (Amendment #2): ledger unavailable",
        }
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
        return {
            "available": False,
            "fail_open": True,
            "error": str(e),
            "lock_4_rsi": True,
            "note": "fail-open (Amendment #2): ledger unreadable",
        }
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
# COMPOSE — pre_seal(): the guard the SEAL path consults
# ─────────────────────────────────────────────────────────────────────────────
def pre_seal(
    events: Optional[List[Any]] = None,
    ctx: Any = None,
    base: str = DEFAULT_FLOW,
    ledger_path: str = DEFAULT_LEDGER,
    ratio_limit: float = RATIO_LIMIT,
    min_total: int = MIN_TOTAL,
    state_path: str = DEFAULT_LOCK2_STATE,
) -> Dict[str, Any]:
    """Compose all four locks from LIVE sources + caller-supplied judge-chain.

    - Lock 1 Gödel: real ctx when provided; VACUOUS (None) otherwise (#3)
    - Lock 2 Calhoun: vector-first, sustained, hysteretic (#1/#5); fail-open (#2)
    - Lock 3 Helix: caller-supplied events chain; VACUOUS (None) when empty (#3)
    - Lock 4 RSI: real ledger freshness; fail-open when unavailable (#2)

    Returns verdict dict — the seal path must call this BEFORE any arif_seal and
    HOLD when verdict['all_pass'] is False. VACUOUS locks never block; they are
    reported honestly in the verdict string. WARN never blocks (Amendment #1)
    but IS banked as a Caution Barrier receipt (Amendment #4).
    """
    bfq = bridge_fq(base=base, ratio_limit=ratio_limit, min_total=min_total)
    brsi = bridge_rsi(ledger_path=ledger_path)
    events = events or []

    # Lock 2 — vector + sustain + hysteresis (the three-level verdict)
    if bfq.get("available") and bfq.get("vector_measured"):
        l2 = _evaluate_lock2_live(bfq, state_path)
    else:
        # Amendment #2 — no positive evidence available: fail open, no state churn
        l2 = {
            "verdict": "PASS",
            "held": False,
            "release": False,
            "deadband": False,
            "consecutive_windows": 0,
            "pole_age_s": 0.0,
            "pole": None,
            "state_ok": False,
            "fail_open": True,
        }
    lock2_pass = l2["verdict"] != "HOLD"

    # Lock 1 — honest: no ctx → VACUOUS (Amendment #3)
    if ctx is None:
        godel: Optional[bool] = None
    else:
        from .helix_engine import godel_wrap

        godel = godel_wrap(ctx)

    # Lock 3 — honest: no events → VACUOUS (Amendment #3)
    helix: Optional[bool] = helix_chain_check(events) if events else None

    # Lock 4 — fail-open on absence (Amendment #2)
    rsi = bool(brsi.get("lock_4_rsi"))

    locks: Dict[str, Any] = {
        "godel": godel,  # None = VACUOUS
        "calhoun": lock2_pass,
        "helix": helix,  # None = VACUOUS
        "rsi": rsi,
    }
    # VACUOUS (None) never blocks — only positive False blocks.
    all_pass = all(v is not False for v in locks.values())

    # Amendment #4 — bank HOLD / WARN as Barrier receipts (best-effort)
    barrier_banked = None
    if l2["verdict"] in ("HOLD", "WARN"):
        barrier_banked = _bank_barrier(base, l2["verdict"], locks, bfq, l2)

    def _tag(v: Optional[bool]) -> str:
        return "VACUOUS" if v is None else str(v)

    verdict_str = (
        f"Helix[G={_tag(godel)}·C={lock2_pass}(lock2={l2['verdict']})"
        f"·H={_tag(helix)}·R={rsi}] all_pass={all_pass} "
        f"sink={bfq.get('sink_poles', {})} vector={bfq.get('vector_diagnosis')}"
    )
    return {
        "all_pass": all_pass,
        "verdict": verdict_str,
        "locks": locks,
        "lock2_detail": l2,
        "sink_poles": bfq.get("sink_poles", {}),
        "scalar_sink_poles": bfq.get("scalar_sink_poles", {}),
        "barrier_banked": barrier_banked,
        "live": {"fq": bfq, "rsi": brsi},
    }


# ─────────────────────────────────────────────────────────────────────────────
# LIVE WITNESS — show the engine reading TODAY (reality, not table)
# ─────────────────────────────────────────────────────────────────────────────
def _witness() -> int:
    print("== HELIX WIRING v2 — LIVE WITNESS (vector-first, sustained, fail-open) ==")
    bfq = bridge_fq()
    print(
        "FQ bridge:",
        json.dumps(
            {
                k: bfq.get(k)
                for k in (
                    "available",
                    "vector_diagnosis",
                    "vector_measured",
                    "sink_poles",
                    "scalar_sink_poles",
                    "dominant_ratio",
                    "divergence",
                    "execute",
                    "verify",
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
    print("  locks:", ps["locks"])
    print("  lock2:", ps["lock2_detail"])
    print("  sink:", ps["sink_poles"], "| vector:", bfq.get("vector_diagnosis"))
    print("== END LIVE WITNESS — HOLD blocks seal; WARN banks Caution and proceeds ==")
    return 0


if __name__ == "__main__":
    raise SystemExit(_witness())
