"""
arifosmcp/runtime/witness_class.py — Positional Witness Taxonomy

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED — NOT DEPLOYED. Pure functions, isolated. Not wired into
the live runtime. Reversible-first per F1 AMANAH.

EUREKA: Tri-Witness only works if the three witnesses are *outside* the
thing they witness. The existing tri-witness taxonomy (human | ai | earth
from phoenix_72.py) names the *substantive* witness — the source of the
evidence. This module adds the *positional* witness — which loop the
receipt is standing in. The two are orthogonal.

  substantive: human | ai | earth
  positional:  SELF | INTERNAL | EXTERNAL | HUMAN

Substance answers: "what kind of evidence is this?"
Position answers: "where is the witness standing?"

A receipt that is `substantive=ai, position=SELF` means: an AI agent
attested to its own system. The Gödel lock is named, not papered over.

A receipt that is `substantive=ai, position=INTERNAL` means: an AI agent
that runs *inside* the federation (e.g. a long-running M3 session)
attested to a different part of the federation. Inside the loop, but
not the same loop.

A receipt that is `substantive=ai, position=EXTERNAL` means: an AI
agent that runs *outside* the federation (Perplexity, Fable, an external
auditor) attested to it. Outside the loop.

A receipt that is `substantive=human, position=HUMAN` means: you, Arif,
attested. The only witness outside every loop.

The current live kernel reports `tri_witness: [true, true, true]` when
all three substantive witnesses are present. It does not record
*position*. That is the gap. A system with substantive=ai, position=SELF
on every receipt is reporting "all witnesses present" while every receipt
is in fact self-attestation. The structural version of the same eureka.

This module provides:

  - `WitnessPosition` — the four-class enum
  - `classify_witness_position()` — pure function: takes a context dict
    and returns a position. Deterministic, no network calls.
  - `narrator_debt()` — counts how many receipts in a session came from
    SELF or INTERNAL positions. Returns a debt count.
  - `tri_witness_position_state()` — given substantive booleans AND a
    narrator debt, returns a tri-witness state that *honestly* reports
    position. A session with debt=0 returns 3/3_OK. A session with
    debt>0 returns 2/3_DEGRADED with `position_debt: N` exposed.
  - `reject_narrative_seal()` — the writer-side check. A `narrative_seal`
    (a string of the form `999 SEAL ALIVE` or any "SEAL" without a
    probe receipt hash) is rejected at the receipt boundary. The
    structural version of "the Fable 5 footer must not chain."

All functions are pure. None of them touch the live runtime. To wire
any of them into the receipt path, a separate, gated change is needed.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class WitnessPosition(str, Enum):
    """Positional witness taxonomy — orthogonal to substantive witness."""

    SELF = "SELF"  # the agent is attesting to itself
    INTERNAL = "INTERNAL"  # the agent is inside the federation but attesting to a different part
    EXTERNAL = "EXTERNAL"  # the agent is outside the federation
    HUMAN = "HUMAN"  # the human sovereign attested


@dataclass(frozen=True)
class ReceiptContext:
    """The minimum context needed to classify a receipt's position."""

    agent_id: str | None = None  # who is attesting
    tool_name: str | None = None  # which tool produced the receipt
    target_name: str | None = None  # what the receipt is about
    session_id: str | None = None  # which session
    actor_id: str | None = None  # the human actor (Arif) if present
    probe_receipt_hash: str | None = None  # bound receipt hash if available


def classify_witness_position(
    ctx: ReceiptContext,
    *,
    federation_agents: set[str] | None = None,
) -> WitnessPosition:
    """
    Classify the position of a receipt given its context. Pure function,
    deterministic, no network calls.

    Order of resolution:
      1. `actor_id` matches the human sovereign → HUMAN.
      2. `tool_name == target_name` → SELF.
      3. `agent_id` is in the known federation agent set → INTERNAL.
      4. Default → EXTERNAL.

    The `federation_agents` set is the canonical agent registry. If
    None, the function uses a conservative default containing the
    arifOS / federation / a-forge / aaa / geox / wealth / well / apex /
    hermes / openclaw / cn-organ identifiers. This is the safe default
    — a default that misclassifies an external agent as internal is
    safer than the reverse, because the SEALS chain will hold them
    to a higher standard.
    """
    if ctx.actor_id and ctx.actor_id.lower() in {"arif", "arif-fazil", "ariffazil", "888"}:
        return WitnessPosition.HUMAN

    if ctx.tool_name and ctx.target_name and ctx.tool_name == ctx.target_name:
        return WitnessPosition.SELF

    if federation_agents is None:
        federation_agents = {
            "arifos",
            "arifosd",
            "a-forge",
            "aforges",
            "aaa",
            "geox",
            "wealth",
            "well",
            "apex",
            "hermes",
            "hermes-asi",
            "openclaw",
            "cn-organ",
        }

    if ctx.agent_id and ctx.agent_id.lower() in {a.lower() for a in federation_agents}:
        return WitnessPosition.INTERNAL

    return WitnessPosition.EXTERNAL


def narrator_debt(
    receipts: Iterable[tuple[ReceiptContext, WitnessPosition]],
) -> int:
    """
    Count receipts whose position is SELF or INTERNAL. The higher this
    count, the more the session has been narrated by witnesses inside
    the loop rather than outside it. A session with debt > 0 cannot
    honestly report `tri_witness: 3/3_OK` — at least one of the receipts
    is structurally the wrong kind.
    """
    debt = 0
    for _, position in receipts:
        if position in (WitnessPosition.SELF, WitnessPosition.INTERNAL):
            debt += 1
    return debt


@dataclass(frozen=True)
class TriWitnessPositionState:
    """The honest tri-witness state, including positional debt."""

    state: str  # 3/3_OK | 2/3_DEGRADED | 1/3_DEGRADED | 0/3_DEGRADED
    substantive: dict[str, bool]
    position_debt: int
    notes: tuple[str, ...]


def tri_witness_position_state(
    substantive: dict[str, bool],
    receipts: Iterable[tuple[ReceiptContext, WitnessPosition]],
) -> TriWitnessPositionState:
    """
    Compute the honest tri-witness state. Combines substantive booleans
    (human/ai/earth — from the existing Phoenix-72 path) with positional
    debt (from this module).

    Rules:
      - 0 substantive = 0/3_DEGRADED
      - 1 substantive, debt > 0 = 1/3_DEGRADED with the one being INTERNAL or SELF
      - 2 substantive, debt > 0 = 2/3_DEGRADED
      - 3 substantive, debt = 0 = 3/3_OK
      - 3 substantive, debt > 0 = 2/3_DEGRADED (because at least one of
        the three receipts is from inside the loop)

    A 3/3_OK report is *only* honest when every substantive witness
    came from a non-self, non-internal position. Otherwise the session
    is degraded by the position, even if all three substantive booleans
    are true.
    """
    n_substantive = sum(1 for v in substantive.values() if v)
    debt = narrator_debt(receipts)

    if n_substantive == 0:
        return TriWitnessPositionState(
            state="0/3_DEGRADED",
            substantive=substantive,
            position_debt=debt,
            notes=("no substantive witness present",),
        )
    if n_substantive == 1:
        return TriWitnessPositionState(
            state="1/3_DEGRADED",
            substantive=substantive,
            position_debt=debt,
            notes=("only one substantive witness",),
        )
    if n_substantive == 2:
        return TriWitnessPositionState(
            state="2/3_DEGRADED",
            substantive=substantive,
            position_debt=debt,
            notes=("two substantive witnesses, third missing",),
        )
    # n_substantive == 3
    if debt == 0:
        return TriWitnessPositionState(
            state="3/3_OK",
            substantive=substantive,
            position_debt=0,
            notes=(),
        )
    return TriWitnessPositionState(
        state="2/3_DEGRADED",
        substantive=substantive,
        position_debt=debt,
        notes=(f"{debt} receipt(s) from SELF or INTERNAL position",),
    )


# ──────────────────────────────────────────────────────────────────────
# Narrative-seal rejection — the structural block on the Fable 5 footer
# ──────────────────────────────────────────────────────────────────────

# Patterns that look like a SEAL but carry no receipt hash. These are
# the exact phrases that have appeared at the end of briefs in this
# session. A receipt with one of these strings as its `sealed` field
# and no `probe_receipt_hash` is a narrative seal, not a real seal.
NARRATIVE_SEAL_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^\s*999\s*SEAL\s*ALIVE\s*$", re.IGNORECASE),
    re.compile(r"^\s*SEAL\s*$", re.IGNORECASE),
    re.compile(r"^\s*999\s*SEAL\s*$", re.IGNORECASE),
    re.compile(r"^\s*FORGED_NOT_GIVEN\s*$", re.IGNORECASE),
    re.compile(r"^\s*DITEMPA\s*BUKAN\s*DIBERI\s*$", re.IGNORECASE),
)


@dataclass(frozen=True)
class NarrativeSealRejection:
    """The result of a narrative-seal check."""

    accepted: bool
    reason: str
    pattern_matched: str | None = None
    suggestion: str | None = None


def reject_narrative_seal(
    sealed_field: str | None,
    probe_receipt_hash: str | None,
) -> NarrativeSealRejection:
    """
    Reject any SEAL that is not bound to a probe receipt hash. The
    structural block on the Fable 5 footer — a string at the bottom
    of a brief that *looks* like a seal but is just prose.

    Acceptance conditions:
      - `sealed_field` is None or empty (no claim made) — accepted.
      - `sealed_field` does not match a narrative-seal pattern — accepted.
      - `sealed_field` matches a narrative-seal pattern AND
        `probe_receipt_hash` is provided and is a non-empty hex string
        (≥16 chars) — accepted (the seal is bound to a real probe).
      - Otherwise — rejected with reason.

    This function does not write anything. It only decides. The writer
    is the one that must call this before chain insertion.
    """
    if not sealed_field or not sealed_field.strip():
        return NarrativeSealRejection(accepted=True, reason="no seal claimed")

    matched = None
    for pat in NARRATIVE_SEAL_PATTERNS:
        if pat.match(sealed_field):
            matched = pat.pattern
            break

    if matched is None:
        return NarrativeSealRejection(
            accepted=True,
            reason="not a recognized narrative-seal pattern",
        )

    if (
        probe_receipt_hash
        and len(probe_receipt_hash) >= 16
        and all(c in "0123456789abcdefABCDEF" for c in probe_receipt_hash)
    ):
        return NarrativeSealRejection(
            accepted=True,
            reason="narrative-seal pattern matched but bound to a probe receipt hash",
            pattern_matched=matched,
        )

    return NarrativeSealRejection(
        accepted=False,
        reason=(
            f"narrative-seal pattern matched ({matched!r}) "
            f"but no probe_receipt_hash was provided; refusing to chain"
        ),
        pattern_matched=matched,
        suggestion=(
            "Provide a real probe receipt hash from arif_session_init, "
            "arif_sense_observe, arif_ops_measure, or arif_evidence_fetch "
            "to bind the seal to a verifiable probe."
        ),
    )


# ──────────────────────────────────────────────────────────────────────
# W₄ Quad-Witness — 4th witness: system/machine state
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class QuadWitnessState:
    """W₄ state: human · ai · earth · system (H·A·E·S)."""

    human_ok: bool
    ai_ok: bool
    earth_ok: bool
    system_ok: bool
    position_debt: int
    w4_score: float  # 0.0-1.0 — fraction of witnesses present
    w4_verdict: str  # W4_OK | W4_DEGRADED | W4_FAILED
    notes: tuple[str, ...]


# System witness — the 4th witness: machine state self-attestation
# Always present when the kernel is alive. The system is always watching,
# always attesting. This is the "silent witness" that makes W₄ fundamentally
# different from W₃: the system cannot be silenced by a lack of human/earth input.
SYSTEM_WITNESS_ALIVE = True  # constant — system is always self-aware


def compute_quad_witness(
    human_ok: bool,
    ai_ok: bool,
    earth_ok: bool,
    receipts: Iterable[tuple[ReceiptContext, WitnessPosition]],
) -> QuadWitnessState:
    """
    Compute W₄ Quad-Witness state. The 4th witness (system) is always
    present when the kernel is alive. Positional debt reduces the
    effective witness count the same way as W₃.

    W₄ score = (human + ai + earth + system) / 4
    Positional debt subtracts from the denominator: effective_w4 = (present - debt) / max(1, 4 - debt)
    """
    n_substantive = sum([human_ok, ai_ok, earth_ok, SYSTEM_WITNESS_ALIVE])
    debt = narrator_debt(receipts)

    effective_n = max(0, n_substantive - debt)
    effective_max = max(1, 4 - debt)
    w4_score = effective_n / effective_max

    if w4_score >= 0.75:
        w4_verdict = "W4_OK"
    elif w4_score >= 0.40:
        w4_verdict = "W4_DEGRADED"
    else:
        w4_verdict = "W4_FAILED"

    notes: list[str] = []
    if not human_ok:
        notes.append("human witness missing")
    if not ai_ok:
        notes.append("ai witness missing")
    if not earth_ok:
        notes.append("earth witness missing")
    if debt > 0:
        notes.append(f"{debt} receipt(s) from SELF or INTERNAL position")

    return QuadWitnessState(
        human_ok=human_ok,
        ai_ok=ai_ok,
        earth_ok=earth_ok,
        system_ok=SYSTEM_WITNESS_ALIVE,
        position_debt=debt,
        w4_score=round(w4_score, 3),
        w4_verdict=w4_verdict,
        notes=tuple(notes),
    )


__all__ = [
    "WitnessPosition",
    "ReceiptContext",
    "classify_witness_position",
    "narrator_debt",
    "TriWitnessPositionState",
    "tri_witness_position_state",
    "QuadWitnessState",
    "compute_quad_witness",
    "NarrativeSealRejection",
    "reject_narrative_seal",
    "NARRATIVE_SEAL_PATTERNS",
]
