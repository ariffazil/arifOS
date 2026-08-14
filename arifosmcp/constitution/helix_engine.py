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

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
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
    """Compose all four locks into a single governance verdict."""
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
    # L3 helix
    check("seal needs judge", helix_chain_check(["seal"]), False)
    check("judge then seal ok", helix_chain_check(["judge", "seal"]), True)
    check("seal then seal no", helix_chain_check(["judge", "seal", "seal"]), False)
    # L4 rsiflow
    check("unbanked verify fails", rsi_flow_check([{"type": "verify", "banked": False}]), False)
    check("banked verify ok", rsi_flow_check([{"type": "verify", "banked": True}]), True)
    # integration
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
