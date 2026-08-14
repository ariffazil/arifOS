"""
completion_governor.py — TAMAT GOVERNOR · the Constitutional Completion Law as code.

Canon: F13 SOVEREIGN directive 2026-08-14 (sovereign's own analysis, verbatim):
    L5 (Completion, trilogi I): "If additional verification cannot change the
     decision, and execution is reversible, then execution is mandatory
     before session close. Deferral requires an explicit blocker, not mere
     uncertainty."
    L6 (Abandonment, trilogi II): "Stop executing when execution cannot
     change reality meaningfully. The most intelligent system does not
     complete all tasks — it aggressively abandons most. KILL must carry a
     reason receipt; without a receipt it is laziness, not judgment."

THE DUALITY (this module is the mirror of surface_breaker.py):

    SABAR-RETRY  (surface_breaker.py):  dVerdict/dRetry  = 0 on a FAILING surface
                                         → STOP retrying. Anti-persistence.
    TAMAT        (this module):         dVerdict/dVerify = 0 on an OPEN task
                                         → START executing. Anti-deferral.

    Same mathematical core: a window of k identical observations means the
    epistemic gradient is flat — more observations are entropy, not safety.
    One law stops pathological persistence; the other stops pathological
    deferral. Together they bracket the verify/execute axis completely.

v2 (trilogi II) — THE TWIN GOVERNOR. Anti-deferral (right side: invariant +
reversible + valuable → EXECUTE_NOW) is now paired with anti-completion-
addiction (left side: exists-but-worthless → KILL_NOW, receipt mandatory).
Completion addicts finish tasks BECAUSE the tasks exist; the left gate kills
the task BECAUSE it does not deserve to. The intelligence is in the
discarding; the receipt is the proof it was intelligence and not laziness.

DISCRIMINATOR PRINCIPLE (trilogi II): "unfinished" is observationally
identical from outside for laziness, over-verification, and rational
abandonment. ONLY receipts differentiate. Every non-DONE terminal requires:
    SEAL    → execution evidence  (Gate 3, no self-attestation)
    HOLD    → hold_reason         (what authority is it waiting for?)
    BLOCKED → blocker_id          (external cause, owned)
    VOID    → kill_reason         (rational abandonment, receipted)
No receipt = laziness. The receipt IS the intelligence.

EUREKA BASIS (sovereign's log, 2026-08-14):
    E1  Completion threshold > confidence threshold. Confidence asymptotes
        to 1 forever; decision invariance terminates. (Satisficing, Simon.)
    E2  The opposite of illusory completion is DEFERRAL BIAS: task is
        completable, agent refuses to finish it.
    E3  Every session boundary is entropy: context loss, state decay,
        environment drift, human reload. "Next session" is never free.
        A task deferred is a task made harder.

FLOORS SPANNED (no new floor — F4 given teeth at the session boundary):
  F4 CLARITY  — deferral IS ΔS > 0 across a session boundary; the law is
                F4's enforcement at closure time
  F1 AMANAH   — reversible + decision-invariant → execute NOW, not next epoch
  F11 AUDIT   — completion claims require execution evidence (200, service
                running, file exists, receipt hash). NO SELF-ATTESTATION.
  F13 SOVEREIGN — T3-class tasks terminate as explicit HOLD, never silently
                deferred; BLOCKED state requires a named blocker.

TERMINAL STATES (the only legal exits — "continue later" is NOT a state):
    SEAL    — done, WITH execution evidence
    HOLD    — explicit sovereign/authority gate (T3, irreversibility)
    VOID    — abandoned with reason
    BLOCKED — deferred WITH a named blocker_id (reversible deferral only)

DESIGN (mirrors F13 language ratification 2026-08-14 for surface_breaker):
  - Python. stdlib-only. Zero dependencies.
  - PURE core (no I/O, no clock) — deterministic, unit-testable, Calhoun-safe.
  - ADDITIVE module. Touches no boot hook, no seal path yet. The seal
    ceremony consults it (step 0: closure audit); the kernel may bind it
    to arif_seal(mode="session_close") when the deployment drift rebuild
    lands. Judgment stays here, Python.

WIRE STATUS (honest): WIRED-TO-CONSULT. Nothing imports this at boot yet.
The law binds the moment a seal ceremony or agent calls
`audit_session()` / `classify()` before closure.

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
INVARIANCE_WINDOW: int = 3  # k identical decision-verdicts → verification
# is no longer information-producing
TERMINAL_STATES = frozenset({"SEAL", "HOLD", "VOID", "BLOCKED"})


# ─────────────────────────────────────────────────────────────────────────────
# VERDICT EVENTS — the evidence stream of a single task
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class VerdictEvent:
    verdict: str  # decision-relevant verdict: PASS/SEAL/PROCEED/BLOCK...
    source: str = "unknown"  # which verifier produced it (F11 attribution)
    ts: str = ""  # optional timestamp (not used by pure core)
    evidence_hash: str = ""  # optional evidence binding

    def as_dict(self) -> Dict[str, str]:
        return {
            "verdict": self.verdict,
            "source": self.source,
            "ts": self.ts,
            "evidence_hash": self.evidence_hash,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "VerdictEvent":
        return VerdictEvent(
            verdict=str(d.get("verdict", "unknown")),
            source=str(d.get("source", "unknown")),
            ts=str(d.get("ts", "")),
            evidence_hash=str(d.get("evidence_hash", "")),
        )


# ─────────────────────────────────────────────────────────────────────────────
# PURE CORE — decision invariance (stateless replay, auditable arithmetic)
# ─────────────────────────────────────────────────────────────────────────────
def decision_invariance(
    verdicts: List[str],
    sources: Optional[List[str]] = None,
    window: int = INVARIANCE_WINDOW,
    require_distinct_sources: bool = True,
) -> Dict[str, Any]:
    """Stateless replay: given the ordered verdicts of past verification
    passes, can new verification still change the decision?

    Invariance condition: the LAST `window` verdicts are identical AND were
    produced by ≥2 distinct verifiers. (k identical verdicts from ONE
    verifier is a possibly-stuck verifier, not decision invariance —
    the mirror of surface_breaker's "new evidence class resets the climb".)

    Pure — agents can audit the arithmetic.
    """
    n = len(verdicts)
    if n < window:
        return {
            "invariant": False,
            "passes": n,
            "reason": "below_window_evidence_may_still_arrive",
        }
    tail_v = verdicts[-window:]
    tail_s = sources[-window:] if sources else ["single"] * window
    if len(set(tail_v)) != 1:
        return {
            "invariant": False,
            "passes": n,
            "reason": "verdicts_still_changing_evidence_is_informative",
        }
    if require_distinct_sources and len(set(tail_s)) < 2:
        return {
            "invariant": False,
            "passes": n,
            "reason": "single_verifier_repeat_not_invariance",
        }
    return {
        "invariant": True,
        "passes": n,
        "verdict": tail_v[-1],
        "reason": (
            f"{window} consecutive identical decision-verdicts across "
            f"{len(set(tail_s))} verifiers — dVerdict/dVerify = 0; "
            "additional verification is entropy, not safety"
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# TASK STATE — what the closure ledger tracks per task
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class TaskState:
    task_id: str
    description: str = ""
    state: str = "ACTIVE"  # ACTIVE | SEAL | HOLD | VOID | BLOCKED
    reversible: bool = True  # F1 axis
    requires_human_authority: bool = False  # T3 axis
    blocker_id: Optional[str] = None  # REQUIRED iff state == BLOCKED
    hold_reason: Optional[str] = None  # REQUIRED iff state == HOLD (v2) —
    # what authority is it waiting for?
    kill_reason: Optional[str] = None  # REQUIRED iff state == VOID — the KILL
    # receipt. "Tanpa resit = kemalasan."
    reality_value: str = "UNASSESSED"  # UNASSESSED | WORTH_EXECUTING |
    # NOT_WORTH_EXISTING — set by the ART
    # layer (selector), consumed at Gate 0
    verdicts: List[VerdictEvent] = field(default_factory=list)
    execution_evidence: List[str] = field(default_factory=list)  # Gate 3
    external_dependencies: bool = False  # deferral-cost axis (env drift)
    carried_sessions: int = 0  # deferral-cost axis (already deferred?)
    human_reload_needed: bool = False  # deferral-cost axis

    def invariance(self) -> Dict[str, Any]:
        return decision_invariance(
            [v.verdict for v in self.verdicts],
            [v.source for v in self.verdicts],
        )

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TaskState":
        return TaskState(
            task_id=str(d.get("task_id", d.get("id", "unknown"))),
            description=str(d.get("description", "")),
            state=str(d.get("state", "ACTIVE")).upper(),
            reversible=bool(d.get("reversible", True)),
            requires_human_authority=bool(d.get("requires_human_authority", False)),
            blocker_id=d.get("blocker_id"),
            hold_reason=d.get("hold_reason"),
            kill_reason=d.get("kill_reason"),
            reality_value=str(d.get("reality_value", "UNASSESSED")).upper(),
            verdicts=[VerdictEvent.from_dict(v) for v in d.get("verdicts", [])],
            execution_evidence=[str(e) for e in d.get("execution_evidence", [])],
            external_dependencies=bool(d.get("external_dependencies", False)),
            carried_sessions=int(d.get("carried_sessions", 0)),
            human_reload_needed=bool(d.get("human_reload_needed", False)),
        )


# ─────────────────────────────────────────────────────────────────────────────
# CLOSURE VERDICT — the governor's ruling on one task
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class ClosureVerdict:
    task_id: str
    action: str  # "TERMINAL" | "VERIFY" | "EXECUTE_NOW" | "HOLD_T3" |
    # "HOLD_F1_IRREVERSIBLE" | "SEAL_REJECTED_NO_EVIDENCE" |
    # "BLOCKER_REQUIRED"
    reason: str
    invariance: Dict[str, Any] = field(default_factory=dict)
    deferral_cost: str = "unknown"  # low | medium | high (entropy of deferring)

    def summary(self) -> str:
        return (
            f"TamatGovernor[{self.task_id}] {self.action} "
            f"(cost_of_deferral={self.deferral_cost}) — {self.reason}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# DEFERRAL COST — make session-boundary entropy visible and taxed (EUREKA-3)
# ─────────────────────────────────────────────────────────────────────────────
def deferral_cost(task: TaskState) -> str:
    """Heuristic estimate of the entropy injected by deferring this task
    across one more session boundary. DER label — heuristic, not measurement.
    """
    score = 0.0
    inv = task.invariance()
    if inv.get("invariant"):
        score += 0.35  # waiting produces nothing — pure loss now
    if task.external_dependencies:
        score += 0.25  # environment drift risk
    if task.carried_sessions >= 1:
        score += 0.20  # already deferred once — compounding
    if task.human_reload_needed:
        score += 0.20  # sovereign attention is the scarcest commodity
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


# ─────────────────────────────────────────────────────────────────────────────
# THE GOVERNOR — three gates, exactly as the sovereign specified
# ─────────────────────────────────────────────────────────────────────────────
class ClosureGovernor:
    def classify(self, task: TaskState) -> ClosureVerdict:
        cost = deferral_cost(task)

        # ── Gate 3 (checked first — no self-attestation, F11) ────────────
        # A claimed SEAL without execution evidence is illusory completion.
        if task.state == "SEAL" and not task.execution_evidence:
            return ClosureVerdict(
                task_id=task.task_id,
                action="SEAL_REJECTED_NO_EVIDENCE",
                reason=(
                    "state=SEAL but zero execution evidence (200/service/"
                    "file/receipt) — self-attestation prohibited, F11"
                ),
                invariance=task.invariance(),
                deferral_cost=cost,
            )
        if task.state == "SEAL":
            return ClosureVerdict(
                task_id=task.task_id,
                action="TERMINAL",
                reason=f"sealed with {len(task.execution_evidence)} evidence artifact(s)",
                invariance=task.invariance(),
                deferral_cost="none",
            )

        # ── Terminal states with structural requirements ─────────────────
        if task.state == "BLOCKED":
            if not task.blocker_id:
                return ClosureVerdict(
                    task_id=task.task_id,
                    action="BLOCKER_REQUIRED",
                    reason=(
                        "BLOCKED without named blocker_id — 'mere uncertainty' "
                        "is not a legal blocker (Completion Law)"
                    ),
                    invariance=task.invariance(),
                    deferral_cost=cost,
                )
            return ClosureVerdict(
                task_id=task.task_id,
                action="TERMINAL",
                reason=f"explicitly blocked by {task.blocker_id}",
                invariance=task.invariance(),
                deferral_cost=cost,
            )
        if task.state == "HOLD":
            if not task.hold_reason:
                return ClosureVerdict(
                    task_id=task.task_id,
                    action="HOLD_REASON_REQUIRED",
                    reason=(
                        "HOLD without hold_reason — an authority gate must "
                        "name what it is waiting for (discriminator: no "
                        "receipt = laziness, not judgment)"
                    ),
                    invariance=task.invariance(),
                    deferral_cost=cost,
                )
            return ClosureVerdict(
                task_id=task.task_id,
                action="TERMINAL",
                reason=f"hold: {task.hold_reason}",
                invariance=task.invariance(),
                deferral_cost="none",
            )
        if task.state == "VOID":
            if not task.kill_reason:
                return ClosureVerdict(
                    task_id=task.task_id,
                    action="KILL_RECEIPT_REQUIRED",
                    reason=(
                        "KILL without kill_reason — rational abandonment must "
                        "be receipted; an unreceipted kill is laziness "
                        "(Completion Law v2, L6)"
                    ),
                    invariance=task.invariance(),
                    deferral_cost=cost,
                )
            return ClosureVerdict(
                task_id=task.task_id,
                action="TERMINAL",
                reason=f"killed: {task.kill_reason}",
                invariance=task.invariance(),
                deferral_cost="none",
            )

        # ── ACTIVE tasks: the law lives here ──────────────────────────────

        # Gate 0 — existence (L6: does this work deserve reality at all?)
        # Precedes the invariance gate deliberately: no amount of verification
        # earns execution for work that does not deserve to exist. This is the
        # anti-completion-addiction gate — the left side of the twin governor.
        if task.reality_value == "NOT_WORTH_EXISTING":
            return ClosureVerdict(
                task_id=task.task_id,
                action="KILL_NOW",
                reason=(
                    "task judged not-worth-existing — execution cannot change "
                    "reality meaningfully; kill it NOW and file the "
                    "kill_reason receipt (L6: intelligence is in the "
                    "discarding, the receipt proves it wasn't laziness)"
                ),
                invariance=task.invariance(),
                deferral_cost=cost,
            )

        inv = task.invariance()

        # Gate 1 — can new evidence still change the decision?
        if not inv.get("invariant"):
            return ClosureVerdict(
                task_id=task.task_id,
                action="VERIFY",
                reason=(
                    "verdicts still moving — verification is information-"
                    f"producing ({inv.get('reason')})"
                ),
                invariance=inv,
                deferral_cost=cost,
            )

        # Decision is invariant. Now Gate 2 — reversibility decides the exit.
        if task.requires_human_authority:
            return ClosureVerdict(
                task_id=task.task_id,
                action="HOLD_T3",
                reason=(
                    "decision invariant but task is T3-class — explicit HOLD "
                    "with full diagnostic report; never silently deferred"
                ),
                invariance=inv,
                deferral_cost=cost,
            )
        if not task.reversible:
            return ClosureVerdict(
                task_id=task.task_id,
                action="HOLD_F1_IRREVERSIBLE",
                reason=(
                    "decision invariant but execution irreversible — F1 "
                    "AMANAH: 888_HOLD before crossing the point of no return"
                ),
                invariance=inv,
                deferral_cost=cost,
            )

        # Invariant + reversible + within authority → execution is MANDATORY.
        return ClosureVerdict(
            task_id=task.task_id,
            action="EXECUTE_NOW",
            reason=(
                "verification stopped being information-producing and "
                "execution is reversible — execution is mandatory before "
                "session close (Completion Law)"
            ),
            invariance=inv,
            deferral_cost=cost,
        )


# ─────────────────────────────────────────────────────────────────────────────
# SESSION CLOSURE AUDIT — no dangling work without explicit reason
# ─────────────────────────────────────────────────────────────────────────────
BLOCKING_ACTIONS = frozenset(
    {
        "EXECUTE_NOW",
        "KILL_NOW",
        "HOLD_T3",
        "HOLD_F1_IRREVERSIBLE",
        "SEAL_REJECTED_NO_EVIDENCE",
        "BLOCKER_REQUIRED",
        "KILL_RECEIPT_REQUIRED",
        "HOLD_REASON_REQUIRED",
    }
)


def audit_session(tasks: List[TaskState]) -> Dict[str, Any]:
    """Session may close ONLY if every task terminates cleanly.

    FAILS (may_close=False) when any task is:
      - EXECUTE_NOW                  → finish it NOW, then re-audit
      - HOLD_*                       → emit the explicit HOLD (with report)
      - SEAL_REJECTED_NO_EVIDENCE    → go get reality evidence or un-claim
      - BLOCKER_REQUIRED             → name the blocker or finish the task
      - VERIFY at session close      → verification that still informs may
                                       NOT be abandoned: either verify now,
                                       or file an explicit BLOCKED with
                                       blocker_id. "Continue later" is not
                                       a state.
    """
    gov = ClosureGovernor()
    rulings = [gov.classify(t) for t in tasks]
    dangling = []
    for task, ruling in zip(tasks, rulings):
        if ruling.action == "VERIFY":
            dangling.append(
                {
                    "task_id": task.task_id,
                    "action": "VERIFY_AT_CLOSE",
                    "reason": (
                        "verification still information-producing at session "
                        "close — finish verifying, or file BLOCKED with "
                        "blocker_id. Silence is not a legal exit."
                    ),
                    "deferral_cost": ruling.deferral_cost,
                }
            )
        elif ruling.action in BLOCKING_ACTIONS:
            dangling.append(
                {
                    "task_id": task.task_id,
                    "action": ruling.action,
                    "reason": ruling.reason,
                    "deferral_cost": ruling.deferral_cost,
                }
            )
    return {
        "may_close": len(dangling) == 0,
        "total_tasks": len(tasks),
        "terminal": sum(1 for r in rulings if r.action == "TERMINAL"),
        "dangling": dangling,
        "rulings": [r.summary() for r in rulings],
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI — audit a session-tasks JSON, or run self-test
# ─────────────────────────────────────────────────────────────────────────────
def _cli(argv: List[str]) -> int:
    if not argv or argv[0] in ("selftest", "--selftest"):
        return _selftest()
    if argv[0] == "audit" and len(argv) >= 2:
        with open(argv[1], "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        tasks = [TaskState.from_dict(t) for t in payload.get("tasks", [])]
        report = audit_session(tasks)
        print(json.dumps(report, indent=2))
        return 0 if report["may_close"] else 2
    print("usage: completion_governor.py [selftest | audit <session_tasks.json>]")
    return 64


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (run: python3 completion_governor.py) — Lock 4 discipline
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    failures = 0

    def check(name: str, got, want):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

    def task(
        task_id: str = "t",
        description: str = "t",
        state: str = "ACTIVE",
        reversible: bool = True,
        requires_human_authority: bool = False,
        blocker_id: Optional[str] = None,
        hold_reason: Optional[str] = None,
        kill_reason: Optional[str] = None,
        reality_value: str = "UNASSESSED",
        verdicts: Optional[List[VerdictEvent]] = None,
        execution_evidence: Optional[List[str]] = None,
        external_dependencies: bool = False,
        carried_sessions: int = 0,
        human_reload_needed: bool = False,
    ) -> TaskState:
        return TaskState(
            task_id=task_id,
            description=description,
            state=state,
            reversible=reversible,
            requires_human_authority=requires_human_authority,
            blocker_id=blocker_id,
            hold_reason=hold_reason,
            kill_reason=kill_reason,
            reality_value=reality_value,
            verdicts=verdicts if verdicts is not None else [],
            execution_evidence=(execution_evidence if execution_evidence is not None else []),
            external_dependencies=external_dependencies,
            carried_sessions=carried_sessions,
            human_reload_needed=human_reload_needed,
        )

    V = lambda v, s: VerdictEvent(verdict=v, source=s)  # noqa: E731

    # 1. invariance: k identical verdicts across 2 verifiers
    inv = decision_invariance(["PASS", "PASS", "PASS"], ["a", "b", "a"])
    check("3 identical verdicts invariant", inv["invariant"], True)

    # 2. verdicts still changing → not invariant (verification is informing)
    inv2 = decision_invariance(["FAIL", "PASS", "PASS"], ["a", "b", "a"])
    check("changing verdicts not invariant", inv2["invariant"], False)

    # 3. single-verifier repeats are NOT invariance (stuck verifier guard)
    inv3 = decision_invariance(["PASS", "PASS", "PASS"], ["a", "a", "a"])
    check("single verifier not invariant", inv3["invariant"], False)

    # 4. below window → evidence may still arrive
    check(
        "below window not invariant",
        decision_invariance(["PASS", "PASS"])["invariant"],
        False,
    )

    # 5. THE LAW: invariant + reversible + T1 → EXECUTE_NOW (mandatory)
    gov = ClosureGovernor()
    r5 = gov.classify(
        task(
            verdicts=[V("PASS", "linter"), V("PASS", "pytest"), V("PASS", "arif_judge")],
        )
    )
    check("invariant reversible executes", r5.action, "EXECUTE_NOW")

    # 6. invariant + T3 → explicit HOLD, never silent deferral
    r6 = gov.classify(
        task(
            requires_human_authority=True,
            verdicts=[V("PASS", "linter"), V("PASS", "pytest"), V("PASS", "arif_judge")],
        )
    )
    check("invariant t3 holds", r6.action, "HOLD_T3")

    # 7. invariant + irreversible → F1 HOLD
    r7 = gov.classify(
        task(
            reversible=False,
            verdicts=[V("PASS", "linter"), V("PASS", "pytest"), V("PASS", "arif_judge")],
        )
    )
    check("invariant irreversible holds f1", r7.action, "HOLD_F1_IRREVERSIBLE")

    # 8. verdicts still moving → VERIFY is legal (evidence still informing)
    r8 = gov.classify(
        task(
            verdicts=[V("FAIL", "pytest"), V("PASS", "pytest"), V("PASS", "linter")],
        )
    )
    check("informative verification continues", r8.action, "VERIFY")

    # 9. Gate 3: claimed SEAL without evidence → rejected (illusory completion)
    r9 = gov.classify(task(state="SEAL", execution_evidence=[]))
    check("seal without evidence rejected", r9.action, "SEAL_REJECTED_NO_EVIDENCE")

    # 10. claimed SEAL with evidence → terminal
    r10 = gov.classify(
        task(
            state="SEAL",
            execution_evidence=["curl :3001/health → 200"],
        )
    )
    check("sealed with evidence terminal", r10.action, "TERMINAL")

    # 11. BLOCKED without blocker_id → rejected ("mere uncertainty" illegal)
    r11 = gov.classify(task(state="BLOCKED", blocker_id=None))
    check("blocked without blocker rejected", r11.action, "BLOCKER_REQUIRED")

    # 12. BLOCKED with named blocker → terminal (legal deferral)
    r12 = gov.classify(task(state="BLOCKED", blocker_id="BLK-upstream-api-down"))
    check("blocked with blocker terminal", r12.action, "TERMINAL")

    # 13. closure audit blocks on dangling reversible invariant task
    rep13 = audit_session(
        [
            task(
                task_id="wiring",
                verdicts=[V("PASS", "a"), V("PASS", "b"), V("PASS", "a")],
            )
        ]
    )
    check("audit blocks dangling work", rep13["may_close"], False)

    # 14. closure audit passes when all terminal — v2: every non-DONE
    #     terminal carries its receipt (discriminator: no receipt = laziness)
    rep14 = audit_session(
        [
            task(task_id="done", state="SEAL", execution_evidence=["receipt#1"]),
            task(task_id="gated", state="HOLD", hold_reason="T3: sovereign ratification pending"),
            task(
                task_id="dropped",
                state="VOID",
                kill_reason="superseded by governor v2; value below threshold",
            ),
            task(task_id="waiting", state="BLOCKED", blocker_id="BLK-1"),
        ]
    )
    check("audit passes clean closure", rep14["may_close"], True)

    # 15. deferral cost: invariant + external deps + carried + human = high
    c15 = deferral_cost(
        task(
            verdicts=[V("PASS", "a"), V("PASS", "b"), V("PASS", "a")],
            external_dependencies=True,
            carried_sessions=1,
            human_reload_needed=True,
        )
    )
    check("deferral cost compounds to high", c15, "high")

    # 16. deferral cost: fresh reversible task = low
    check("fresh task deferral low", deferral_cost(task()), "low")

    # 17. VERIFY at close is dangling too — silence is not an exit
    rep17 = audit_session(
        [
            task(
                task_id="live-verify",
                verdicts=[V("FAIL", "pytest"), V("PASS", "pytest")],
            )
        ]
    )
    check(
        "verify at close is dangling",
        rep17["dangling"][0]["action"] if rep17["dangling"] else None,
        "VERIFY_AT_CLOSE",
    )

    # 18. the OODA asymmetry is encoded: no verdicts at all → VERIFY, not EXECUTE
    #     (an unobserved task has no invariance claim — observe first)
    r18 = gov.classify(task(verdicts=[]))
    check("no evidence no execution", r18.action, "VERIFY")

    # ── v2: twin governor + discriminator (trilogi II) ───────────────────

    # 19. VOID without kill_reason → rejected ("tanpa resit = kemalasan")
    r19 = gov.classify(task(state="VOID", kill_reason=None))
    check("kill without receipt rejected", r19.action, "KILL_RECEIPT_REQUIRED")

    # 20. VOID with kill_reason → terminal (rational abandonment, receipted)
    r20 = gov.classify(
        task(
            state="VOID",
            kill_reason="superseded by b909aa506; value below threshold",
        )
    )
    check("receipted kill terminal", r20.action, "TERMINAL")

    # 21. HOLD without hold_reason → rejected (authority gate must name its wait)
    r21 = gov.classify(task(state="HOLD", hold_reason=None))
    check("hold without reason rejected", r21.action, "HOLD_REASON_REQUIRED")

    # 22. Gate 0 precedes everything: worthless task → KILL_NOW even when it
    #     would otherwise be EXECUTE_NOW (invariant + reversible + valuable)
    r22 = gov.classify(
        task(
            reality_value="NOT_WORTH_EXISTING",
            verdicts=[V("PASS", "linter"), V("PASS", "pytest"), V("PASS", "arif_judge")],
        )
    )
    check("gate 0 kills before execute", r22.action, "KILL_NOW")

    # 23. KILL_NOW is dangling at close — abandonment must happen, not linger
    rep23 = audit_session([task(task_id="zombie", reality_value="NOT_WORTH_EXISTING")])
    check("kill-now blocks closure", rep23["may_close"], False)

    # 24. THE DISCRIMINATOR: two "unfinished" tasks, identical from outside.
    #     Only the receipt differentiates rational abandonment from laziness.
    rep24 = audit_session(
        [
            task(
                task_id="rational",
                state="VOID",
                kill_reason="scope cancelled by F13 directive 2026-08-14",
            ),
            task(task_id="lazy", state="VOID", kill_reason=None),
        ]
    )
    dangling24 = [d["task_id"] for d in rep24["dangling"]]
    check("discriminator catches only the receiptless", dangling24, ["lazy"])

    # 25. WORTH_EXECUTING flows through the normal gates (no regression)
    r25 = gov.classify(
        task(
            reality_value="WORTH_EXECUTING",
            verdicts=[V("PASS", "linter"), V("PASS", "pytest"), V("PASS", "arif_judge")],
        )
    )
    check("worth-executing still executes", r25.action, "EXECUTE_NOW")

    # 26. existence precedes epistemics: worthless task → KILL_NOW even when
    #     verdicts are NOT invariant (don't verify work that shouldn't exist)
    r26 = gov.classify(
        task(
            reality_value="NOT_WORTH_EXISTING",
            verdicts=[V("FAIL", "pytest"), V("PASS", "pytest")],
        )
    )
    check("worthless skips verification", r26.action, "KILL_NOW")

    print(
        f"\nCOMPLETION GOVERNOR SELF-TEST: "
        f"{'ALL PASS' if failures == 0 else str(failures) + ' FAILURES'}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
