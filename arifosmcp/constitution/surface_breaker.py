"""
surface_breaker.py — TRANSPORT CIRCUIT BREAKER · the SABAR-RETRY invariant as code.

Canon: F13 SOVEREIGN doctrine 2026-08-14 (transport-corruption diagnosis):
    "If N consecutive failures produce no new verdict-changing evidence,
     the execution surface is declared contaminated.
     Retry prohibited. Switch transport or HOLD."

Scar origin: 2026-08-14 helix session — opencode bash tool-call serialization
corrupted by invocation-envelope bleed (output/param echo fed back into the next
call, duplicating `"timeout":15000,"workdir":"/root"` segments exponentially).
5 retries produced zero new verdict-changing evidence; the verdict
(TOOL_SERIALIZATION_CORRUPTED) existed by failure #1. Every retry after that was
maintenance entropy — gain > 1 positive feedback: bigger error → bigger echo.

FLOORS SPANNED (no new floor — this is SABAR extended to the transport layer):
  F12 RESILIENCE — envelope bleed IS injection across time/transport
  F11 AUDIT     — every trip banks a receipt signature
  F4 CLARITY    — stops entropy amplification at the trip point

DESIGN (per F13 language ratification 2026-08-14):
  - Python. stdlib-only. hashlib is the only non-trivial import. Zero dependencies.
  - PURE core (no I/O, no clock) — deterministic, unit-testable, Calhoun-safe.
  - ADDITIVE module. Touches no boot hook, no seal path. Enforcement points
    consume it as consultation (agent doctrine now; A-FORGE forge_shell retry
    loop can wrap it as its TS reflex later — judgment stays here, Python).

WIRE STATUS (honest): WIRED-TO-CONSULT. Nothing imports this at boot yet.
The invariant is law the moment an agent or actuator calls `observe()`/`should_sabar()`.

DITEMPA BUKAN DIBERI · forged in flow, not in drift.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
TRIP_THRESHOLD: int = 3  # N consecutive no-new-evidence failures → trip
SIGNATURE_HEAD_BYTES: int = 64  # stable head of error class used for evidence


# ─────────────────────────────────────────────────────────────────────────────
# VERDICT
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class BreakerVerdict:
    action: str  # "ALLOW" | "SABAR_SWITCH_SURFACE" | "SABAR_HOLD"
    contaminated: bool
    consecutive_failures: int
    last_signature: Optional[str]
    detail: str

    @property
    def is_sabar(self) -> bool:
        return self.action.startswith("SABAR")

    def summary(self) -> str:
        return (
            f"SurfaceBreaker[{self.action} contaminated={self.contaminated} "
            f"consec={self.consecutive_failures} sig={self.last_signature}] "
            f"— {self.detail}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# ERROR SIGNATURE — what counts as NEW evidence vs transport echo
# ─────────────────────────────────────────────────────────────────────────────
def error_signature(error_text: str) -> str:
    """Stable signature of an error's CLASS, immune to payload-length noise.

    The envelope-bleed failure mode duplicates param-echo segments; two errors
    that differ only by how many times `"timeout":15000` was repeated are the
    SAME failure (same evidence), not new evidence. Normalization, in order:
      1. first line only (stack tails are echo volume)
      2. cut at first payload marker '{' or '(' — the class is what precedes
         structured payload, and payload growth is the amplifier
      3. strip digits — incrementing counters/run-lengths are noise, not
         evidence (documented tradeoff: classes differing ONLY by number,
         e.g. 'billing 402' vs 'billing 429', collapse to one class)
    """
    if not error_text:
        return "EMPTY"
    head = error_text.strip().splitlines()[0]
    for marker in ("{", "("):
        idx = head.find(marker)
        if idx != -1:
            head = head[:idx]
    head = "".join(ch for ch in head if not ch.isdigit())
    return hashlib.sha256(head.encode("utf-8", "replace")).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────────
# PURE CORE — stateless doctrine check
# ─────────────────────────────────────────────────────────────────────────────
def should_sabar(
    failure_signatures: List[str],
    trip_threshold: int = TRIP_THRESHOLD,
) -> Dict[str, Any]:
    """Stateless replay: given the ordered signatures of past failures, is the
    surface contaminated? Pure — agents can audit the arithmetic.

    Trip condition: the LAST `trip_threshold` failures all share one signature
    (zero new evidence across N consecutive failures).
    """
    n = len(failure_signatures)
    if n < trip_threshold:
        return {"sabar": False, "consecutive": n, "reason": "below_threshold"}
    tail = failure_signatures[-trip_threshold:]
    if len(set(tail)) == 1:
        return {
            "sabar": True,
            "consecutive": n,
            "signature": tail[-1],
            "reason": (
                f"{trip_threshold} consecutive failures, one signature, "
                "zero verdict-changing evidence — dVerdict/dRetry = 0"
            ),
        }
    return {"sabar": False, "consecutive": n, "reason": "evidence_still_arriving"}


# ─────────────────────────────────────────────────────────────────────────────
# STATEFUL OBSERVER — what a retry loop consults before each retry
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class SurfaceState:
    surface: str = "default"
    consecutive_failures: int = 0
    last_signature: Optional[str] = None
    contaminated: bool = False
    trip_count: int = 0
    signature_history: List[str] = field(default_factory=list)

    def observe(
        self,
        success: bool,
        error_text: str = "",
        trip_threshold: int = TRIP_THRESHOLD,
    ) -> BreakerVerdict:
        """Feed one outcome; get the verdict for the NEXT attempt.

        - success            → reset (surface works; contamination cleared)
        - new signature      → reset counter to 1 (NEW evidence — retry legal)
        - same signature     → climb; at threshold → SABAR, retry prohibited
        - already tripped    → SABAR persists until success or surface switch
        """
        if success:
            self.consecutive_failures = 0
            self.last_signature = None
            self.contaminated = False
            return BreakerVerdict(
                action="ALLOW",
                contaminated=False,
                consecutive_failures=0,
                last_signature=None,
                detail="surface recovered — counter reset",
            )

        sig = error_signature(error_text)
        self.signature_history.append(sig)

        if self.contaminated:
            # Trip state is sticky: retries on a contaminated surface are
            # prohibited regardless of what the new error says.
            self.trip_count += 1
            return BreakerVerdict(
                action="SABAR_HOLD",
                contaminated=True,
                consecutive_failures=self.consecutive_failures,
                last_signature=sig,
                detail=(
                    f"surface '{self.surface}' already contaminated — "
                    f"retry #{self.trip_count} since trip; switch transport or HOLD"
                ),
            )

        if self.last_signature is not None and sig != self.last_signature:
            # New error class = new verdict-changing evidence. Retry is legal;
            # the failure was informative, not transport echo.
            self.consecutive_failures = 1
            self.last_signature = sig
            return BreakerVerdict(
                action="ALLOW",
                contaminated=False,
                consecutive_failures=1,
                last_signature=sig,
                detail="new evidence class — retry legal, counter reset to 1",
            )

        self.consecutive_failures += 1
        self.last_signature = sig
        if self.consecutive_failures >= trip_threshold:
            self.contaminated = True
            self.trip_count = 0
            return BreakerVerdict(
                action="SABAR_SWITCH_SURFACE",
                contaminated=True,
                consecutive_failures=self.consecutive_failures,
                last_signature=sig,
                detail=(
                    f"{self.consecutive_failures} consecutive same-signature "
                    f"failures on '{self.surface}' — dVerdict/dRetry=0; "
                    "surface contaminated, retry PROHIBITED"
                ),
            )
        return BreakerVerdict(
            action="ALLOW",
            contaminated=False,
            consecutive_failures=self.consecutive_failures,
            last_signature=sig,
            detail=(
                f"failure {self.consecutive_failures}/{trip_threshold} "
                "same-signature — evidence budget draining"
            ),
        )


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (run: python3 surface_breaker.py) — Lock 4 discipline
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    failures = 0

    def check(name: str, got, want):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

    # 1. signature stability across echo growth (the exact scar replay)
    s_small = error_signature('JSON parsing failed: Text: {"command":"ls"}')
    s_bloat = error_signature(
        'JSON parsing failed: Text: {"command":"ls","timeout":15000,'
        '"workdir":"/root","timeout":15000,"workdir":"/root"'
    )
    check("echo-bloat same signature", s_small == s_bloat, True)

    # 2. different error class → different signature
    check(
        "different class different sig",
        error_signature("NotFound: FileSystem.access (/bad/path)")
        != error_signature("JSON parsing failed: ..."),
        True,
    )

    # 3. success resets
    st = SurfaceState(surface="bash")
    st.observe(False, "JSON parsing failed: A")
    st.observe(False, "JSON parsing failed: A")
    v = st.observe(True)
    check("success resets contaminated", v.contaminated, False)

    # 4. trip at exactly threshold, not before
    st = SurfaceState(surface="bash")
    v2 = st.observe(False, "JSON parsing failed: A")
    v3 = st.observe(False, "JSON parsing failed: A")
    v4 = st.observe(False, "JSON parsing failed: A")
    check("below threshold allows", v3.action, "ALLOW")
    check("at threshold trips", v4.action, "SABAR_SWITCH_SURFACE")

    # 5. new evidence class resets the climb
    st = SurfaceState(surface="bash")
    st.observe(False, "JSON parsing failed: A")
    st.observe(False, "JSON parsing failed: A")
    v_new = st.observe(False, "NotFound: FileSystem.access (/typo)")
    check("new evidence resets to 1", v_new.consecutive_failures, 1)
    check("new evidence allows retry", v_new.action, "ALLOW")

    # 6. contaminated is sticky — later retries prohibited even with new text
    st = SurfaceState(surface="bash")
    for _ in range(3):
        st.observe(False, "JSON parsing failed: A")
    v_sticky = st.observe(False, "completely different error now")
    check("trip sticky on retry", v_sticky.action, "SABAR_HOLD")

    # 7. stateless replay of the actual 2026-08-14 session
    replay = should_sabar([error_signature(f"JSON parsing failed: {i}") for i in range(3)])
    check("session replay trips", replay["sabar"], True)

    # 8. two failures do not trip (evidence may still arrive)
    check("two failures no trip", should_sabar(["a", "a"])["sabar"], False)

    # 9. mixed evidence never trips
    check(
        "mixed evidence no trip",
        should_sabar(["a", "a", "b", "a"])["sabar"],
        False,
    )

    # 10. success after trip clears contamination
    st = SurfaceState(surface="bash")
    for _ in range(3):
        st.observe(False, "JSON parsing failed: A")
    v_recover = st.observe(True)
    check("recovery clears", v_recover.contaminated, False)

    print(
        f"\nSURFACE BREAKER SELF-TEST: {'ALL PASS' if failures == 0 else str(failures) + ' FAILURES'}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
