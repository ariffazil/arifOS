"""
FQ Metabolic Cap — fq_policy.yaml enforcement plane "arifOS kernel"
(F13_RATIFIED_CHAT 2026-09-12, directive "ratify + wire").

Mirrors A-FORGE gateToolByFq semantics at session birth: an actor whose
scalar FQ sits below the observe_only_below floor (0.5) with a verdict of
STUCK or BURNING has execution outrunning verification — the kernel caps
the session at OBSERVE_ONLY until receipts rebalance.

Rules (ratified contract + live ledger semantics):

- Sovereign principals are never metabolically downgraded.
- Cap applies only when the derived authority exceeds OBSERVE_ONLY.
- Unknown actor (no receipts) → no cap. Absence of receipts is not guilt (F9).
- FOSSILIZED (verification dominance) → no cap — the harmful direction is
  under-verification, not over-verification.
- arifFlow unreachable → no cap at session level; metabolic_state recorded
  as UNREACHABLE. The executor-level gate (A-FORGE gateToolByFq) stays
  fail-closed per-tool; bricking every kernel session on a daemon outage
  would trade one failure mode for a worse one.
"""

from __future__ import annotations

import json
import logging
import urllib.request

logger = logging.getLogger(__name__)

ARIFFLOW_HEALTH_URL = "http://127.0.0.1:7073/health"
FQ_OBSERVE_ONLY_BELOW = 0.5          # fq_policy.yaml policy.thresholds.observe_only_below
CAP_VERDICTS = ("STUCK", "BURNING")  # execute outruns verify


def _candidate_lanes(per_actor: dict, actor_id: str) -> list:
    """Match kernel-canonical actor ids against arifFlow receipt lane ids.

    The kernel canonicalizes e.g. 'hermes-asi' → 'HERMES' while the ledger
    carries per-lane keys ('hermes-asi', 'hermes-cron'). Match exact, then
    case-insensitive containment both directions, so an umbrella actor maps
    to all of its receipt lanes.
    """
    exact = per_actor.get(actor_id)
    if isinstance(exact, dict):
        return [(actor_id, exact)]
    lowered = (actor_id or "").lower()
    if not lowered:
        return []
    candidates = []
    for key, val in per_actor.items():
        if not isinstance(val, dict):
            continue
        k = str(key).lower()
        if k == lowered or lowered in k or k in lowered:
            candidates.append((str(key), val))
    return candidates


def metabolic_cap(
    actor_id: str | None,
    authority: str,
    *,
    is_sovereign_principal: bool = False,
    timeout: float = 2.0,
) -> tuple[str, dict]:
    """Return (possibly-capped authority, metabolic_state dict)."""
    state = {
        "actor_id": actor_id,
        "quotient": None,
        "verdict": None,
        "capped": False,
        "reason": None,
        "source": "arifFlow :7073/health",
        "policy": f"fq_policy.yaml F13_RATIFIED 2026-09-12 floor={FQ_OBSERVE_ONLY_BELOW}",
    }
    if not actor_id or is_sovereign_principal:
        state["verdict"] = "SOVEREIGN_EXEMPT" if is_sovereign_principal else "NO_ACTOR"
        return authority, state
    if authority not in ("FULL", "LIMITED_MUTATE", "SOVEREIGN"):
        # Already OBSERVE_ONLY or unknown shape — nothing to cap.
        state["verdict"] = "ALREADY_CAPPED"
        return authority, state
    try:
        with urllib.request.urlopen(ARIFFLOW_HEALTH_URL, timeout=timeout) as resp:
            health = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 — session-level gate must fail-open
        state["verdict"] = "UNREACHABLE"
        state["reason"] = f"arifFlow health probe failed: {exc}"
        logger.warning("fq_gate: arifFlow unreachable (%s) — session cap skipped", exc)
        return authority, state
    per_actor = (health.get("fq") or {}).get("per_actor") or {}
    candidates = _candidate_lanes(per_actor, actor_id)
    if not candidates:
        state["verdict"] = "UNKNOWN_ACTOR"
        state["reason"] = "no receipts for this actor — absence of data is not guilt"
        return authority, state
    qualifying = []
    for lane, entry in candidates:
        q = entry.get("quotient")
        v = entry.get("verdict")
        if v in CAP_VERDICTS and isinstance(q, (int, float)) and q < FQ_OBSERVE_ONLY_BELOW:
            qualifying.append((lane, v, float(q)))
    state["matched_lanes"] = {lane: {"verdict": e.get("verdict"), "quotient": e.get("quotient")} for lane, e in candidates}
    if qualifying:
        worst = min(qualifying, key=lambda t: t[2])
        state["quotient"] = worst[2]
        state["verdict"] = worst[1]
        state["capped"] = True
        lanes_txt = ", ".join(f"{lane} ({v}, FQ={round(q, 3)})" for lane, v, q in qualifying)
        state["reason"] = (
            f"FQ_GATE: actor {actor_id} lane(s) [{lanes_txt}] below {FQ_OBSERVE_ONLY_BELOW} floor "
            f"with verdict in {CAP_VERDICTS} — session capped at OBSERVE_ONLY until "
            "verify receipts rebalance (fq_policy.yaml, F13-ratified 2026-09-12)"
        )
        logger.info("fq_gate: capped %s via lane(s) %s -> OBSERVE_ONLY", actor_id, lanes_txt)
        return "OBSERVE_ONLY", state
    best = candidates[0]
    state["quotient"] = best[1].get("quotient")
    state["verdict"] = best[1].get("verdict")
    return authority, state
