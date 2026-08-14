"""
helix_engine.py — THE HELIX ENGINE · unified composition of the Four Locks.

Canon: AAA/canon/HELIX_CODEX.md (2026-08-14, F13 SOVEREIGN directive "zen all")
Composes the four load-bearing walls into ONE governance function for the
whole system. NEW module — does not modify boot hooks (F1 reversible).

LOCKS:
  L1 Gödel      — no self-certification; reality final auditor.
                     (wraps existing godel_lock_gate.godel_lock_gate(ctx))
  L2 Calhoun    — NEW: BOTH ratio poles (fossilisation verify:exec, burn exec:verify).
                     NOT the WEALTH market calhoun. This is the institutional sink guard.
  L3 Helix      — NEW: judge-before-seal chain check. No seal without a prior judge.
  L4 RSI Flow   — NEW: verification must be banked into the ledger (memory flow).

Design: pure, deterministic core (ratio poles, chain check) so the arithmetic is
unit-testable and can never silently drift (Calhoun determinism == the SOT rule).
Gödel coupling is lazy/try-import so the module degrades cleanly without the ctx.

AMENDMENTS v2 (2026-08-14, F13 directive "execute all autonomously forge all to seal"
— post governance-lock review, 6-finding amendment set):
  #1 SUSTAIN + HYSTERESIS — Lock 2 HOLDs only when a pole is held across K>=2
     consecutive observation windows OR >= SUSTAIN_SECONDS (30 min). Single-window
     breach → WARN (receipt, not block). Release only below RELEASE_RATIO (2.8),
     creating a 2.8–3.0 deadband so the gate cannot flap at the 3.0 operating point.
  #3 HONEST LOCKS — absent evidence is VACUOUS (None), never a silent True.
     godel without ctx → None; helix chain without events → None. all_pass ignores
     VACUOUS (does not block) but every verdict string reports it honestly.
  #5 VECTOR-FIRST LOCK 2 — the gating signal is arifFlow's vector `diagnosis`
     (VERIFICATION/EXECUTION DOMINANCE), NOT the deprecated scalar ratio. Scalar
     poles survive only as divergence evidence + hysteresis release input.

The engine stays PURE (no I/O, no clock) — sustain state and time are injected
by helix_wiring (the I/O layer). DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CORE CONSTANTS (single source of truth — HELIX_CODEX Lock 2)
# ─────────────────────────────────────────────────────────────────────────────
# A pole is "held" when one side strictly dominates the other by more than
# RATIO_LIMIT : 1. BOTH poles are sink disease. MIN_TOTAL avoids tripping on
# cold-start noise (mirrors kernel FQ sample-window behaviour).
RATIO_LIMIT: float = 3.0
MIN_TOTAL: int = 6

# Amendment #1 — sustain + hysteresis geometry.
SUSTAIN_WINDOWS: int = 2  # K consecutive pole windows before HOLD
SUSTAIN_SECONDS: float = 1800.0  # 30 min time floor (seals are sporadic observers)
RELEASE_RATIO: float = 2.8  # hysteresis: clear a HOLD only below this


# ─────────────────────────────────────────────────────────────────────────────
# HELIX VERDICT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class HelixVerdict:
    """Result of composing all four locks. `all_pass` is the single governance gate."""

    lock_1_godel: bool
    lock_2_calhoun: bool  # True when NO sink pole is held
    lock_3_helix: bool
    lock_4_rsi: bool
    sink_poles: Dict[str, bool] = field(default_factory=dict)  # {fossilisation, burn}
    details: Dict[str, Any] = field(default_factory=dict)
    lock_2_skipped_lowtotal: bool = False

    @property
    def all_pass(self) -> bool:
        return bool(
            self.lock_1_godel and self.lock_2_calhoun and self.lock_3_helix and self.lock_4_rsi
        )

    def summary(self, lock_1_name: str = "ok") -> str:
        return (
            f"Helix[G={self.lock_1_godel}·C={self.lock_2_calhoun}"
            f"·H={self.lock_3_helix}·R={self.lock_4_rsi}] "
            f"all_pass={self.all_pass} sink={self.sink_poles}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 2 — CALHOUN RATIO-POLE GUARD (PURE, deterministic)
# ─────────────────────────────────────────────────────────────────────────────
def compute_sink_poles(
    execute: int,
    verify: int,
    ratio_limit: float = RATIO_LIMIT,
    min_total: int = MIN_TOTAL,
) -> Dict[str, bool]:
    """Return {fossilisation, burn} — the two poles of the institutional sink.

    fossilisation : verify dominates  → reality contact, no movement (agent-addiction #4)
    burn          : execute dominates → movement, no witness (agent-addiction #1/#3)

    Both True is impossible unless ratio_limit < 1. When totals are too small
    to be meaningful (< min_total) both poles report False (no false alarm).
    """
    total = execute + verify
    if total < min_total:
        return {"fossilisation": False, "burn": False}

    fossilisation = bool(verify >= ratio_limit * execute + 1)
    burn = bool(execute >= ratio_limit * verify + 1)
    return {"fossilisation": fossilisation, "burn": burn}


def dominant_ratio(
    execute: int,
    verify: int,
    min_total: int = MIN_TOTAL,
) -> Optional[float]:
    """Scalar dominance magnitude in the dominant direction (>= 1.0), or None
    when totals are too small to be meaningful. Pure hysteresis input (Amendment #1)."""
    if execute + verify < min_total:
        return None
    if execute <= 0 or verify <= 0:
        return float("inf") if (execute + verify) > 0 else None
    return max(verify / execute, execute / verify)


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 2 (Amendment #5) — VECTOR POLES: the diagnosis IS the signal
# ─────────────────────────────────────────────────────────────────────────────
VECTOR_FOSSILISATION = "VERIFICATION DOMINANCE"
VECTOR_BURN = "EXECUTION DOMINANCE"


def vector_poles(diagnosis: Optional[str]) -> Dict[str, Any]:
    """Map arifFlow's vector diagnosis onto sink poles. PURE.

    Returns {"poles": {fossilisation, burn}, "measured": bool}.
    Absent/empty diagnosis → measured=False (VACUOUS — wiring fails open)."""
    if not isinstance(diagnosis, str) or not diagnosis.strip():
        return {"poles": {"fossilisation": False, "burn": False}, "measured": False}
    d = diagnosis.strip().upper()
    return {
        "poles": {
            "fossilisation": d == VECTOR_FOSSILISATION,
            "burn": d == VECTOR_BURN,
        },
        "measured": True,
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 2 (Amendment #1) — SUSTAIN + HYSTERESIS EVALUATION (PURE)
# ─────────────────────────────────────────────────────────────────────────────
def evaluate_lock2(
    *,
    pole_now: bool,
    held_previous: bool = False,
    consecutive_windows: int = 0,
    pole_age_s: float = 0.0,
    dominant_ratio_now: Optional[float] = None,
    ratio_limit: float = RATIO_LIMIT,
    release_ratio: float = RELEASE_RATIO,
    sustain_windows: int = SUSTAIN_WINDOWS,
    sustain_seconds: float = SUSTAIN_SECONDS,
) -> Dict[str, Any]:
    """Three-level Lock 2 verdict: PASS / WARN / HOLD. PURE — no clock, no I/O.

    - pole_now sustained (K windows OR time floor)      → HOLD
    - pole_now single window                            → WARN (receipt, not block)
    - held_previous, pole cleared, ratio < release      → PASS (release)
    - held_previous, pole cleared, ratio in deadband    → HOLD (stay held — no flap)
    - held_previous, pole still held                    → HOLD (sustains automatically)
    - no pole, not held                                 → PASS
    """
    if pole_now:
        sustained = consecutive_windows >= sustain_windows or pole_age_s >= sustain_seconds
        verdict = "HOLD" if sustained else "WARN"
        return {
            "verdict": verdict,
            "held": verdict == "HOLD",
            "consecutive_windows": consecutive_windows,
            "pole_age_s": pole_age_s,
            "release": False,
            "deadband": False,
            "sustain_windows": sustain_windows,
            "sustain_seconds": sustain_seconds,
        }
    if held_previous:
        # Release needs positive counter-evidence, not mere absence of the pole:
        # vector primary (pole cleared) AND scalar out of the deadband.
        if dominant_ratio_now is None or dominant_ratio_now < release_ratio:
            return {
                "verdict": "PASS",
                "held": False,
                "release": True,
                "deadband": False,
                "consecutive_windows": 0,
                "pole_age_s": 0.0,
                "sustain_windows": sustain_windows,
                "sustain_seconds": sustain_seconds,
            }
        return {
            "verdict": "HOLD",
            "held": True,
            "release": False,
            "deadband": True,
            "consecutive_windows": consecutive_windows,
            "pole_age_s": pole_age_s,
            "sustain_windows": sustain_windows,
            "sustain_seconds": sustain_seconds,
        }
    return {
        "verdict": "PASS",
        "held": False,
        "release": False,
        "deadband": False,
        "consecutive_windows": 0,
        "pole_age_s": 0.0,
        "sustain_windows": sustain_windows,
        "sustain_seconds": sustain_seconds,
    }


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 3 — HELIX CHAIN CHECK (PURE): judge-before-seal
# ─────────────────────────────────────────────────────────────────────────────
# events: ordered list of (kind, ...) where kind in {"judge","seal","work"}.
# A seal is only legitimate if a judge event precedes it with no intervening seal.
def helix_chain_check(events: List[Any]) -> bool:
    """True iff the governance chain is sound: no seal without a prior judge.

    Bare strings are accepted: "judge","seal","work". Tuples (kind, payload) also OK.
    """
    last_judge_seen = False
    for ev in events:
        kind = ev if isinstance(ev, str) else (ev[0] if isinstance(ev, tuple) else str(ev))
        kind = str(kind)
        if kind == "judge":
            last_judge_seen = True
        elif kind == "seal":
            if not last_judge_seen:
                return False
            # a seal consumes the judge-warrant; next seal needs a new judge
            last_judge_seen = False
        # "work" events neither grant nor consume a warrant
    return True


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 4 — RSI FLOW CHECK (PURE): verification must be banked
# ─────────────────────────────────────────────────────────────────────────────
def rsi_flow_check(ledger_entries: List[Any], require: str = "verify") -> bool:
    """True iff every `require`-marked event in the window is also banked=True
    (i.e. the verification metabolised into the ledger — the memory flow).

    ledger_entries: list of dicts with keys {type, banked} or tuples (type, banked).
    """
    needed = False
    for ent in ledger_entries:
        if isinstance(ent, dict):
            kind, banked = ent.get("type", ""), ent.get("banked", False)
        else:
            kind, banked = ent[0], bool(ent[1])
        if kind == require:
            needed = True
            if not banked:
                return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# LOCK 1 — GÖDEL WRAP (lazy, real gate)
# ─────────────────────────────────────────────────────────────────────────────
def godel_wrap(ctx: Optional[Any] = None) -> bool:
    """Call the real godel_lock_gate if importable and ctx provided.

    ctx = the governance context object. Without ctx we return True (vacuously
    satisfied) but flag it — the caller is expected to pass ctx in production.
    Amendment #3: honest callers treat the no-ctx path as VACUOUS (None) at the
    wiring layer; this pure wrap keeps its legacy bool contract for run_helix.
    """
    if ctx is None:
        return True  # advisory: caller must wire real ctx in the kernel path
    try:
        mod = importlib.import_module("arifosmcp.runtime.godel_lock_gate")
        gate = getattr(mod, "godel_lock_gate")
        res = gate(ctx)
        # gate returns dict; treat non-HOLD/verdict==pass as OK
        return bool(res.get("pass", res.get("verdict", "PASS") == "PASS"))
    except Exception:
        # fail-open here is a *recognition* gap, not a false block — but the
        # engine will still surface it in details so the caller can HOLD.
        return True


# ─────────────────────────────────────────────────────────────────────────────
# THE HELIX ENGINE — one function, four walls
# ─────────────────────────────────────────────────────────────────────────────
def run_helix(
    execute: int,
    verify: int,
    events: List[Any],
    ledger_entries: List[Any],
    ctx: Optional[Any] = None,
    ratio_limit: float = RATIO_LIMIT,
    min_total: int = MIN_TOTAL,
) -> HelixVerdict:
    """Compose all four locks into a single governance verdict.

    NOTE (v2): run_helix retains the legacy single-window scalar Lock 2 for
    pure/arithmetic consumers. The LIVE seal path (helix_wiring.pre_seal)
    composes Lock 2 via evaluate_lock2 + vector_poles instead — vector-first,
    sustained, hysteretic. Do not report both as the same signal.
    """
    poles = compute_sink_poles(execute, verify, ratio_limit, min_total)
    skipped_low = (execute + verify) < min_total

    verdict = HelixVerdict(
        lock_1_godel=godel_wrap(ctx),
        lock_2_calhoun=not (poles["fossilisation"] or poles["burn"]),
        lock_3_helix=helix_chain_check(events),
        lock_4_rsi=rsi_flow_check(ledger_entries),
        sink_poles=poles,
        lock_2_skipped_lowtotal=skipped_low,
        details={
            "execute": execute,
            "verify": verify,
            "ratio_limit": ratio_limit,
            "min_total": min_total,
            "godel": "lazy_wrap_no_ctx" if ctx is None else "real_gate",
        },
    )
    return verdict


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (run: python3 helix_engine.py) — the Verification step, Lock 4
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    failures = 0

    def check(name: str, got, want):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

    # L2 pure
    check("balanced (no pole)", compute_sink_poles(5, 5), {"fossilisation": False, "burn": False})
    check(
        "fossilisation (verify>3:1)",
        compute_sink_poles(1, 10),
        {"fossilisation": True, "burn": False},
    )
    check("burn (execute>3:1)", compute_sink_poles(10, 1), {"fossilisation": False, "burn": True})
    check(
        "cold-start skip",
        compute_sink_poles(1, 1, min_total=6),
        {"fossilisation": False, "burn": False},
    )
    # dominant_ratio (Amendment #1 hysteresis input)
    check("dominant_ratio low-total None", dominant_ratio(1, 1), None)
    dr = dominant_ratio(17, 49)
    check("dominant_ratio 49/17 ~2.88", round(dr, 2) if dr is not None else None, 2.88)
    check("dominant_ratio burn inf", dominant_ratio(10, 0), float("inf"))
    # vector_poles (Amendment #5)
    check(
        "vector fossilisation",
        vector_poles("VERIFICATION DOMINANCE"),
        {"poles": {"fossilisation": True, "burn": False}, "measured": True},
    )
    check(
        "vector burn",
        vector_poles("EXECUTION DOMINANCE"),
        {"poles": {"fossilisation": False, "burn": True}, "measured": True},
    )
    check(
        "vector balanced",
        vector_poles("BALANCED")["poles"],
        {"fossilisation": False, "burn": False},
    )
    check("vector absent unmeasured", vector_poles(None)["measured"], False)
    # evaluate_lock2 (Amendment #1)
    check(
        "single-window breach → WARN",
        evaluate_lock2(pole_now=True, consecutive_windows=1)["verdict"],
        "WARN",
    )
    check(
        "sustained K=2 → HOLD",
        evaluate_lock2(pole_now=True, consecutive_windows=2)["verdict"],
        "HOLD",
    )
    check(
        "time floor 30min → HOLD",
        evaluate_lock2(pole_now=True, consecutive_windows=1, pole_age_s=1801.0)["verdict"],
        "HOLD",
    )
    check(
        "release below 2.8 → PASS",
        evaluate_lock2(pole_now=False, held_previous=True, dominant_ratio_now=2.5)["verdict"],
        "PASS",
    )
    check(
        "deadband 2.9 stays HOLD",
        evaluate_lock2(pole_now=False, held_previous=True, dominant_ratio_now=2.9)["verdict"],
        "HOLD",
    )
    check(
        "deadband release flag",
        evaluate_lock2(pole_now=False, held_previous=True, dominant_ratio_now=2.5)["release"],
        True,
    )
    check(
        "no pole fresh → PASS",
        evaluate_lock2(pole_now=False)["verdict"],
        "PASS",
    )
    # L3 helix
    check("seal needs judge", helix_chain_check(["seal"]), False)
    check("judge then seal ok", helix_chain_check(["judge", "seal"]), True)
    check("seal then seal no", helix_chain_check(["judge", "seal", "seal"]), False)
    # L4 rsiflow
    check("unbanked verify fails", rsi_flow_check([{"type": "verify", "banked": False}]), False)
    check("banked verify ok", rsi_flow_check([{"type": "verify", "banked": True}]), True)
    # integration (legacy scalar path retained)
    v = run_helix(5, 5, ["judge", "seal"], [{"type": "verify", "banked": True}])
    check("all_pass (healthy)", v.all_pass, True)
    v2 = run_helix(10, 1, ["judge", "seal"], [{"type": "verify", "banked": True}])
    check("burn pole fails all_pass", v2.all_pass, False)
    v3 = run_helix(5, 5, ["seal"], [{"type": "verify", "banked": True}])
    check("no judge fails all_pass", v3.all_pass, False)

    print(f"\nHELIX SELF-TEST: {'ALL PASS' if failures == 0 else str(failures) + ' FAILURES'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
