"""
attention_gate.py — PERHATI GATE · the Attention/Admission Law as code.

Canon: F13 SOVEREIGN trilogi III 2026-08-14 (sovereign's own analysis, verbatim):
    "Attention is upstream of ART. Not every signal deserves classification.
     Not every classified intent deserves judgment. Not every judged action
     deserves execution. Reality contains infinite candidate tasks; no
     intelligence can process all of them. Humans fail at Attention, not
     intelligence — the scarce resource gets hijacked before judgment
     ever occurs."

THE LAW (L7, ADMISSION):
    No signal becomes a task without admission judgment.
    No signal is ignored without a receipt.
    Zero attention-gradient = noise.

THE DEFAULT FLIP (the industry gap the sovereign identified):
    Most agent systems DEFAULT-ADMIT: every signal becomes a task, every
    alert gets attention, every email gets answered. Labs build Gates 1-3
    (can evidence change decision / should execution happen / did reality
    change) because benchmarks quietly assume the task is already
    important — the dataset defines reality. Gate 0 (should this exist)
    has no benchmark because attention has no benchmark.
    This gate flips the default: unbound, novel-but-value-unknown signals
    DEFER to sweep (with receipt + TTL), they do NOT become tasks.
    Duty-bound and sovereign-bound signals always ADMIT — safety and the
    sovereign are never filtered.

THE GRADIENT TRILOGY (three flat-gradient detectors, one mathematical core):

    SABAR   (surface_breaker.py)     dVerdict/dRetry  = 0 → STOP retrying
    TAMAT   (completion_governor.py) dVerdict/dVerify = 0 → START executing
                                     worthless task         KILL with receipt
    PERHATI (this module)            dAttention/dSignal = 0 → IGNORE as noise

    Each detects a collapsed gradient — observation that has stopped
    producing information — at a different layer of the stack:

        PERHATI  → what gets noticed        (signal admission)
        ART      → what gets classified     (exists: apex_verdict_hold skill)
        Kernel   → what gets judged         (exists: F1-F13, :8088)
        TAMAT    → what gets finished/killed (exists: completion_governor)
        ACT      → what gets executed       (exists: A-FORGE)
        SABAR    → when retries stop        (exists: surface_breaker)

    The stack the sovereign described — Attention → ART → Kernel → ACT —
    now has code at every layer.

CONSUMER CONTRACT (closes the v2 stub — no abstract feature without consumer):
    completion_governor.TaskState.reality_value  ←  AttentionVerdict.reality_value
    PERHATI ADMIT(duty/sovereign) → reality_value=WORTH_EXECUTING
    PERHATI ADMIT(novel error)    → reality_value=UNASSESSED (judgment decides)
    Gate 0 of TAMAT consumes exactly this field. Producer meets consumer.

FLOORS SPANNED (no new floor):
  F4 CLARITY   — default-admit is attention entropy; the gate taxes it
  F6 MARUAH    — sovereign-bound signals are NEVER filtered (F13's voice
                 cannot become noise)
  F11 AUDIT    — IGNORE and DEFER require receipts; receiptless ignoring
                 is negligence, exactly as receiptless killing is laziness.
                 The discriminator principle extends upstream: bad attention
                 (ignoring a valuable signal) and good attention (ignoring
                 noise) are observationally identical from outside.
                 ONLY receipts differentiate.
  F13 SOVEREIGN — the sovereign's channel bypasses every filter

DESIGN (F13 language ratification 2026-08-14):
  Python. stdlib-only. PURE core (no I/O, no clock). Self-test. Honest
  wire status. Value estimation honesty: a pure function CANNOT compute
  importance — it computes novelty (gradient), duty-binding, severity
  escalation, and TTL expiry. Value beyond that stays UNASSESSED and is
  decided by the judgment layer (agent + kernel + sovereign). F7 humility
  is structural here.

WIRE STATUS (honest): WIRED-TO-CONSULT. Consumers: completion_governor
Gate 0 contract (today), signal intakes (drift detector, Hermes, cron
sweeps — when they adopt it). The law binds the moment any intake calls
`AttentionGate().observe()`.

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
GRADIENT_WINDOW: int = 3  # k identical signal signatures → dA = 0 → noise
DEFER_TTL_SWEEPS: int = 3  # deferrals expire — attention debt cannot hide
SEVERITIES = ("info", "warn", "error", "critical")
DUTY_BOUND_TAGS = ("floor", "scar", "incident", "drift", "security")


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL SIGNATURE — same normalization discipline as surface_breaker
# ─────────────────────────────────────────────────────────────────────────────
def signal_signature(text: str) -> str:
    """Stable signature of a signal's CLASS. The 100th 'disk 81% full' alert
    and the 1st differ only in run-length noise — same signature, same
    information class, zero new attention value."""
    if not text:
        return "EMPTY"
    head = text.strip().splitlines()[0]
    for marker in ("{", "("):
        idx = head.find(marker)
        if idx != -1:
            head = head[:idx]
    head = "".join(ch for ch in head if not ch.isdigit())
    return hashlib.sha256(head.encode("utf-8", "replace")).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
# PURE CORE — attention gradient (stateless replay, auditable arithmetic)
# ─────────────────────────────────────────────────────────────────────────────
def attention_gradient(
    signatures: List[str],
    window: int = GRADIENT_WINDOW,
) -> Dict[str, Any]:
    """Stateless replay: has the signal stream gone flat? The last `window`
    identical signatures means dAttention/dSignal = 0 — the stream has
    stopped producing new classes. Observation of it is now entropy."""
    n = len(signatures)
    if n < window:
        return {"flat": False, "count": n, "reason": "below_window"}
    tail = signatures[-window:]
    if len(set(tail)) == 1:
        return {
            "flat": True,
            "count": n,
            "signature": tail[-1],
            "reason": (
                f"{window} consecutive identical signal classes — "
                "dAttention/dSignal = 0; stream is noise"
            ),
        }
    return {"flat": False, "count": n, "reason": "new_classes_still_arriving"}


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL — what arrives at the membrane
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Signal:
    signal_id: str
    text: str
    source: str = "unknown"  # email / cron / drift-detector / telegram...
    severity: str = "info"  # info | warn | error | critical
    duty_bound: bool = False  # maps to floor/scar/incident/drift/security
    sovereign_bound: bool = False  # direct F13 channel — NEVER filtered
    defer_age: int = 0  # sweeps already survived while DEFERRED

    def signature(self) -> str:
        return signal_signature(self.text)


# ─────────────────────────────────────────────────────────────────────────────
# VERDICT — the admission ruling
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class AttentionVerdict:
    signal_id: str
    action: str  # ADMIT | IGNORE | DEFER | ADMIT_DEFER_EXPIRED |
    # ADMIT_ESCALATED
    reality_value: str  # WORTH_EXECUTING | UNASSESSED (never set here to
    # NOT_WORTH_EXISTING — that is a kill, TAMAT's job)
    receipt: str  # MANDATORY for every non-ADMIT (and recorded for
    # ADMITs too — F11)
    gradient: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        return (
            f"PerhatiGate[{self.signal_id}] {self.action} "
            f"(value={self.reality_value}) — {self.receipt}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# THE GATE — admission control
# ─────────────────────────────────────────────────────────────────────────────
class AttentionGate:
    """Stateful across a signal stream; the arithmetic inside is pure and
    replayable via `attention_gradient` on the recorded history."""

    def __init__(self, window: int = GRADIENT_WINDOW):
        self.window = window
        self.seen: List[str] = []  # signature history
        self.last_severity: Dict[str, str] = {}  # signature → last severity

    def observe(
        self,
        signal: Signal,
        defer_ttl: int = DEFER_TTL_SWEEPS,
    ) -> AttentionVerdict:
        sig = signal.signature()
        sev = signal.severity if signal.severity in SEVERITIES else "info"

        # ── Gate A: sovereign and duty channels bypass every filter ────────
        # F6 MARUAH / F13 SOVEREIGN: the sovereign's voice and constitutional
        # duties (floors, scars, incidents, security) can NEVER become noise.
        if signal.sovereign_bound:
            self.seen.append(sig)
            self.last_severity[sig] = sev
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="ADMIT",
                reality_value="WORTH_EXECUTING",
                receipt="sovereign-bound channel — bypasses all filtering (F13)",
                gradient={"flat": False, "reason": "sovereign_channel"},
            )
        if signal.duty_bound:
            self.seen.append(sig)
            self.last_severity[sig] = sev
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="ADMIT",
                reality_value="WORTH_EXECUTING",
                receipt="duty-bound signal (floor/scar/incident/drift/security)",
                gradient={"flat": False, "reason": "duty_channel"},
            )

        # ── Record and compute gradient ────────────────────────────────────
        self.seen.append(sig)
        grad = attention_gradient(self.seen, self.window)
        prev_sev = self.last_severity.get(sig)
        self.last_severity[sig] = sev

        # ── Gate B: severity escalation IS new information ─────────────────
        # Same class but climbing severity = the gradient is NOT flat even
        # if signatures repeat. 'disk 81%' → 'disk 97%' is escalation.
        if prev_sev is not None and SEVERITIES.index(sev) > SEVERITIES.index(prev_sev):
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="ADMIT_ESCALATED",
                reality_value="UNASSESSED",
                receipt=(
                    f"severity climbed {prev_sev}→{sev} on known class — "
                    "escalation is new information, gradient not flat"
                ),
                gradient=grad,
            )

        # ── Gate C: deferral debt expires — attention cannot hide ──────────
        if signal.defer_age >= defer_ttl:
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="ADMIT_DEFER_EXPIRED",
                reality_value="UNASSESSED",
                receipt=(
                    f"deferred for {signal.defer_age} sweeps (TTL {defer_ttl}) — "
                    "unjudged deferral escalates; attention debt cannot hide"
                ),
                gradient=grad,
            )

        # ── Gate D: novel hard failures admit (judgment layer will triage) ─
        seen_before = sum(1 for s in self.seen[:-1] if s == sig)
        if sev in ("error", "critical") and seen_before == 0:
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="ADMIT",
                reality_value="UNASSESSED",
                receipt="novel error-class signal — admits for judgment",
                gradient=grad,
            )

        # ── Gate E: flat gradient = noise. IGNORE, with receipt ────────────
        # The core law. Repeated identical classes carry zero new attention
        # value. The 100th identical email is noise regardless of urgency
        # theatre.
        if grad.get("flat"):
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="IGNORE",
                reality_value="UNASSESSED",
                receipt=(
                    "zero attention-gradient — signal class repeated "
                    f"{grad.get('count', '?')}x with no escalation; noise "
                    "(receipt filed: ignoring ≠ negligence)"
                ),
                gradient=grad,
            )

        # ── Gate F: THE DEFAULT FLIP — novel, unbound, value-unknown ───────
        # Industry default: admit as task. This law: DEFER to sweep with a
        # receipt and TTL. It may earn admission later (escalation, duty
        # binding, sovereign interest) but it does not preempt attention
        # merely by existing.
        if seen_before == 0:
            return AttentionVerdict(
                signal_id=signal.signal_id,
                action="DEFER",
                reality_value="UNASSESSED",
                receipt=(
                    "novel signal, no duty binding, value unknown — "
                    "deferred to sweep with TTL; existence alone does not "
                    "earn attention (L7 default flip)"
                ),
                gradient=grad,
            )

        # ── Otherwise: repeated non-flat, non-escalating, soft ─────────────
        return AttentionVerdict(
            signal_id=signal.signal_id,
            action="IGNORE",
            reality_value="UNASSESSED",
            receipt=(
                "repeated soft signal, no escalation, no duty binding — below admission threshold"
            ),
            gradient=grad,
        )


# ─────────────────────────────────────────────────────────────────────────────
# ATTENTION AUDIT — receipts both ways, the discriminator extends upstream
# ─────────────────────────────────────────────────────────────────────────────
def audit_attention(verdicts: List[AttentionVerdict]) -> Dict[str, Any]:
    """An attention session closes cleanly only if every IGNORE and DEFER
    carries a receipt, and no ADMIT lacks one either. Receiptless ignoring
    is negligence — the upstream twin of 'receiptless killing is laziness'.
    """
    problems = []
    for v in verdicts:
        if not v.receipt or not v.receipt.strip():
            problems.append(
                {
                    "signal_id": v.signal_id,
                    "action": v.action,
                    "problem": "receiptless non-admit = negligence",
                }
            )
    counts: Dict[str, int] = {}
    for v in verdicts:
        counts[v.action] = counts.get(v.action, 0) + 1
    return {
        "may_close": len(problems) == 0,
        "total": len(verdicts),
        "counts": counts,
        "problems": problems,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (run: python3 attention_gate.py)
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    failures = 0

    def check(name: str, got, want):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

    def sig(
        i: str,
        text: str = "newsletter: weekly digest",
        severity: str = "info",
        duty_bound: bool = False,
        sovereign_bound: bool = False,
        defer_age: int = 0,
    ) -> Signal:
        return Signal(
            signal_id=i,
            text=text,
            severity=severity,
            duty_bound=duty_bound,
            sovereign_bound=sovereign_bound,
            defer_age=defer_age,
        )

    # 1. sovereign-bound ALWAYS admits — F13's voice cannot become noise
    v1 = AttentionGate().observe(sig("s1", sovereign_bound=True))
    check("sovereign bypass admits", v1.action, "ADMIT")
    check("sovereign worth executing", v1.reality_value, "WORTH_EXECUTING")

    # 2. duty-bound admits (floor/scar/incident/drift/security)
    v2 = AttentionGate().observe(sig("s2", "drift detected: port 9443 unknown", duty_bound=True))
    check("duty-bound admits", v2.action, "ADMIT")

    # 3. novel error admits for judgment (UNASSESSED — value not invented)
    v3 = AttentionGate().observe(sig("s3", "kernel panic on organ boot", severity="error"))
    check("novel error admits", v3.action, "ADMIT")
    check("novel error unassessed", v3.reality_value, "UNASSESSED")

    # 4. THE SOVEREIGN'S EXAMPLE: 100 emails vs 1 existential problem
    gate = AttentionGate()
    email_verdicts = []
    for i in range(100):
        email_verdicts.append(gate.observe(sig(f"mail-{i}", "newsletter: weekly digest")))
    existential = gate.observe(
        sig(
            "the-one", "existential: kernel seal chain broken", severity="critical", duty_bound=True
        )
    )
    n_admitted_emails = sum(1 for v in email_verdicts if v.action.startswith("ADMIT"))
    n_ignored = sum(1 for v in email_verdicts if v.action == "IGNORE")
    n_deferred = sum(1 for v in email_verdicts if v.action == "DEFER")
    check("zero of 100 emails admitted as tasks", n_admitted_emails, 0)
    check("later emails ignored as noise", n_ignored >= 96, True)
    check("first emails deferred not admitted", n_deferred >= 1, True)
    check("existential problem admitted", existential.action, "ADMIT")

    # 5. attention gradient pure replay — flat tail detection
    flat = attention_gradient(["a", "a", "a"])
    check("flat gradient detected", flat["flat"], True)
    mixed = attention_gradient(["a", "b", "a"])
    check("mixed stream not flat", mixed["flat"], False)

    # 6. escalation admits even on a repeated class
    gate6 = AttentionGate()
    gate6.observe(sig("d1", "disk usage at 81 percent", severity="warn"))
    v6 = gate6.observe(sig("d2", "disk usage at 97 percent", severity="critical"))
    check("severity escalation admits", v6.action, "ADMIT_ESCALATED")

    # 7. alert storm of identical errors → noise (after first admit)
    gate7 = AttentionGate()
    storm = [
        gate7.observe(sig(f"e{i}", "timeout calling provider xyz", severity="error"))
        for i in range(6)
    ]
    check("first error admitted", storm[0].action, "ADMIT")
    check("storm tail ignored", [v.action for v in storm[3:]], ["IGNORE"] * 3)

    # 8. deferral TTL — attention debt cannot hide forever
    v8 = AttentionGate().observe(sig("old-curiosity", defer_age=3))
    check("defer expiry admits", v8.action, "ADMIT_DEFER_EXPIRED")

    # 9. default flip: novel unbound info DEFERS, never admits directly
    v9 = AttentionGate().observe(sig("new-idea", "interesting new rss feed appeared"))
    check("novel unbound defers", v9.action, "DEFER")

    # 10. audit: receiptless ignoring is flagged (negligence discriminator)
    bad = AttentionVerdict(signal_id="x", action="IGNORE", reality_value="UNASSESSED", receipt="")
    good = AttentionVerdict(
        signal_id="y", action="IGNORE", reality_value="UNASSESSED", receipt="noise class, dA=0"
    )
    rep = audit_attention([bad, good])
    check("receiptless ignore flagged", [p["signal_id"] for p in rep["problems"]], ["x"])

    # 11. audit clean when all receipted
    rep11 = audit_attention([good])
    check("receipted attention closes", rep11["may_close"], True)

    # 12. PERHATI never sets NOT_WORTH_EXISTING — killing is TAMAT's job,
    #     separation of powers between the two gates
    gate12 = AttentionGate()
    vs = [gate12.observe(sig(f"n{i}", "spam advertisement")) for i in range(5)]
    check(
        "gate never kills (separation of powers)",
        all(v.reality_value != "NOT_WORTH_EXISTING" for v in vs),
        True,
    )

    print(
        f"\nATTENTION GATE SELF-TEST: "
        f"{'ALL PASS' if failures == 0 else str(failures) + ' FAILURES'}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_selftest() or 0)
