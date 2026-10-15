"""QRL increment 1 — deterministic judge modes: score + collapse.

SPEC of record: F13 QRL increment-1 directive 2026-10-14.

Scope:
  - arif_judge mode=score    → hard-floor veto (deterministic rules, NO LLM
    in the veto path) then soft score S = P(success) − irreversibility −
    blast_radius − cost + info_gain. ADVISORY scoring output; the veto is
    binding (floor violation), the soft score is not.
  - arif_judge mode=collapse → exactly one canonical QRL-4 verdict
    (SEAL / SABAR / HOLD / VOID) with reason_code + floor_ids, derived by
    calling the deterministic veto first, then the existing kernel judge
    facade; emits exactly one prediction record (test sink in this
    increment — live CHRON write only after deploy).

State honesty: PRODUCED/TESTED-LOCAL. Not WIRED until dispatch lands in
tools.py arif_judge facade; not DEPLOYED until the deploy drift resolves.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

QRL4 = ("SEAL", "SABAR", "HOLD", "VOID")

# Test sink for prediction records (increment 1). Live CHRON (:18102) is
# deliberately NOT written here — that wiring happens only after deploy.
DEFAULT_PREDICTION_SINK = os.path.join(
    os.path.expanduser("~"), ".local", "share", "arifos", "qrl", "predictions.jsonl"
)

# ── Deterministic hard-floor veto ───────────────────────────────────────
# Compiled rules. Each rule: (floor_id, predicate(kwargs)->bool, reason).
# A fired veto is BINDING: score/collapse must return HOLD or VOID.
# Order matters only for reason reporting; all fired rules are reported.


def _norm(v: Any) -> str:
    return str(v or "").strip().upper()


def hard_floor_veto(
    *,
    candidate: str | None = None,
    action_class: str | None = None,
    reversibility_level: str | None = None,
    blast_radius: str | None = None,
    action_tier: str | None = None,
    sovereign_receipt: str | None = None,
    actor_verified: bool = False,
    requested_capability: str | None = None,
    claim_class: str | None = None,
) -> list[dict[str, str]]:
    """Return fired veto rules. Empty list = no floor violation."""
    fired: list[dict[str, str]] = []
    ac = _norm(action_class)
    rev = _norm(reversibility_level)
    br = _norm(blast_radius)
    tier = _norm(action_tier)

    # F1 AMANAH — irreversible without a sovereign receipt is a hard stop.
    if ac == "IRREVERSIBLE" or rev == "IRREVERSIBLE":
        fired.append(
            {
                "floor": "F1",
                "rule": "irreversible_action",
                "reason": (
                    "action_class/reversibility_level=IRREVERSIBLE — "
                    "F1 AMANAH veto: irreversible actions require F13 "
                    "sovereign decision, never an autonomous verdict."
                ),
            }
        )
    # F1: even WITH a sovereign receipt the judge never auto-SEALs — escalate.
    if (ac == "IRREVERSIBLE" or rev == "IRREVERSIBLE") and not sovereign_receipt:
        fired.append(
            {
                "floor": "F13",
                "rule": "irreversible_without_sovereign",
                "reason": "no sovereign_receipt on an irreversible action — F13 SOVEREIGN veto.",
            }
        )
    # F1/F13 — federation blast radius mutation.
    if br == "FEDERATION" and ac == "MUTATE":
        fired.append(
            {
                "floor": "F1",
                "rule": "federation_mutation",
                "reason": "blast_radius=FEDERATION with action_class=MUTATE — hard veto.",
            }
        )
    # F11 AUDIT — unverified actor requesting mutation/critical tier.
    if (ac == "MUTATE" or tier == "CRITICAL") and not actor_verified:
        fired.append(
            {
                "floor": "F11",
                "rule": "unverified_actor_mutation",
                "reason": "actor_verified=false on MUTATE/critical action — F11 AUDIT veto.",
            }
        )
    # F2 TRUTH — SPEC-only claims can never authorize anything.
    if _norm(claim_class) == "SPEC":
        fired.append(
            {
                "floor": "F2",
                "rule": "spec_class_claim",
                "reason": "claim_class=SPEC — speculative claims carry no authorizing weight (F2).",
            }
        )
    # capability unknown → fail closed (never invent).
    if requested_capability and _norm(requested_capability) not in (
        "",
        "FORGE.DRY_RUN",
        "OBSERVE.READ",
    ) and not actor_verified:
        fired.append(
            {
                "floor": "F11",
                "rule": "capability_without_identity",
                "reason": (
                    f"requested_capability={requested_capability} with unverified "
                    "identity — fail closed (F11)."
                ),
            }
        )
    return fired


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


_REV_WEIGHT = {"reversible": 0.0, "read_only": 0.0, "hard": 0.5, "irreversible": 1.0}
_BR_WEIGHT = {"self": 0.0, "session": 0.1, "organ": 0.3, "federation": 0.8, "external": 1.0}
_TIER_WEIGHT = {"standard": 0.0, "high": 0.3, "critical": 0.6}


def soft_score(
    *,
    p_success: float = 0.5,
    action_class: str | None = None,
    reversibility_level: str | None = None,
    blast_radius: str | None = None,
    action_tier: str | None = None,
    est_cost: float = 0.0,
    info_gain: float = 0.0,
) -> dict[str, Any]:
    """S = P(success) − irreversibility − blast_radius − cost + info_gain.

    Heuristic ranking signal labeled INT — never a kernel verdict.
    """
    rev = _norm(reversibility_level).lower()
    br = _norm(blast_radius).lower()
    irr = _REV_WEIGHT.get(rev, 0.5 if rev else 0.0)
    blast = _BR_WEIGHT.get(br, 0.3 if br else 0.0)
    cost = _clamp01(est_cost)
    s = (
        _clamp01(p_success)
        - irr
        - blast
        - cost
        + _clamp01(info_gain)
    )
    return {
        "S": round(s, 4),
        "terms": {
            "p_success": _clamp01(p_success),
            "irreversibility": irr,
            "blast_radius": blast,
            "cost": cost,
            "info_gain": _clamp01(info_gain),
        },
        "label": "INT",
        "note": "heuristic ranking signal — not a measurement, not a verdict",
    }


def score_candidate(kwargs: dict[str, Any]) -> dict[str, Any]:
    """mode=score entry: deterministic veto first, soft score for survivors."""
    veto = hard_floor_veto(**{k: v for k, v in kwargs.items() if k in {
        "candidate", "action_class", "reversibility_level", "blast_radius",
        "action_tier", "sovereign_receipt", "actor_verified",
        "requested_capability", "claim_class",
    }})
    body: dict[str, Any] = {
        "mode": "score",
        "authority": "ADVISORY",
        "sealable": False,
        "vetoed": veto,
        "verdict": None,  # only collapse may set
    }
    if veto:
        # Binding floor failure → S is not meaningful; report the veto.
        body["S"] = None
        body["qrl_hint"] = "HOLD"
        body["reason_code"] = "HARD_FLOOR_VETO"
        body["floor_ids"] = sorted({v["floor"] for v in veto})
    else:
        score = soft_score(**{k: v for k, v in kwargs.items() if k in {
            "p_success", "action_class", "reversibility_level", "blast_radius",
            "action_tier", "est_cost", "info_gain",
        }})
        body["S"] = score["S"]
        body["terms"] = score["terms"]
        body["score_label"] = score["label"]
        body["qrl_hint"] = "SEAL" if score["S"] >= 0.3 else ("SABAR" if score["S"] >= 0 else "HOLD")
        body["reason_code"] = "SOFT_SCORE_ADVISORY"
        body["floor_ids"] = []
    return body


# ── Prediction record (scope 5) ─────────────────────────────────────────


def write_prediction_record(
    record: dict[str, Any], sink: str | None = None
) -> dict[str, Any]:
    """Append exactly one prediction record to the local test sink.

    Returns {path, written, error?}. Missing/malformed input → written=False
    (never fabricate a sink write).
    """
    try:
        p_raw = float(record.get("p"))
    except (TypeError, ValueError):
        return {"written": False, "error": f"p not numeric: {record.get('p')!r}"}
    # validate BEFORE clamping — a clamped 1.5 must never masquerade as 1.0
    if not (0.0 <= p_raw <= 1.0):
        return {"written": False, "error": f"p out of [0,1]: {record.get('p')!r}"}
    p = p_raw
    if not record.get("node") or not record.get("expected"):
        return {"written": False, "error": "prediction record missing node/expected"}
    path = sink or DEFAULT_PREDICTION_SINK
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "node": str(record["node"]),
        "expected": str(record["expected"])[:300],
        "p": p,
        "sealed": False,
        "lane": "qrl-incr1-test-sink",
        "live_chron": False,
    }
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError as e:
        return {"written": False, "error": str(e)}
    return {"written": True, "path": path, "entry": entry}


def collapse_verdict(
    kernel_verdict: str | None,
    *,
    veto_floors: list[str] | None = None,
    reason_code: str = "",
) -> dict[str, Any]:
    """Map a raw kernel verdict to the canonical QRL-4, never upward.

    VOID > HOLD > SABAR > SEAL. Unknown/empty → HOLD (unknown_verdict_token).
    A fired hard-floor veto forces ≥ HOLD regardless of kernel verdict.
    """
    veto_floors = veto_floors or []
    # Strict token matching: verdict tokens on the wire are EXACT uppercase
    # strings. Lowercase/whitespace variants (e.g. "seal ") are NOT known
    # tokens — they fall to HOLD/unknown_verdict_token (fail closed).
    raw = str(kernel_verdict) if kernel_verdict is not None else ""
    alias = {
        "SEAL": "SEAL",
        "PARTIAL": "SABAR",
        "PROVISIONAL": "SABAR",
        "SABAR": "SABAR",
        "HOLD": "HOLD",
        "HOLD_888": "HOLD",
        "888_HOLD": "HOLD",
        "VOID": "VOID",
        "DENY": "VOID",
        "DEGRADED": "SABAR",
        "OBSERVE_ONLY": "HOLD",
    }
    mapped = alias.get(raw)
    if mapped is None:
        return {
            "verdict": "HOLD",
            "raw": kernel_verdict,
            "reason_code": reason_code or "unknown_verdict_token",
            "floor_ids": veto_floors,
        }
    if veto_floors and mapped == "SEAL":
        mapped = "HOLD"
    return {
        "verdict": mapped,
        "raw": kernel_verdict,
        "reason_code": reason_code or ("hard_floor_veto" if veto_floors else "kernel_verdict"),
        "floor_ids": veto_floors,
    }


__all__ = [
    "QRL4",
    "DEFAULT_PREDICTION_SINK",
    "hard_floor_veto",
    "soft_score",
    "score_candidate",
    "write_prediction_record",
    "collapse_verdict",
]
