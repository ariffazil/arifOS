"""
arifosmcp/runtime/floor_producers.py — F2/F11/F12/F13 measurement producers.

ARIFOS::MEASUREMENT_CLOSURE_INIT::2026-10-10 · Phase 4 (minimal implementation).

These producers turn LIVE evidence into a challengeable floor signal. They
follow the F1/F3 producer pattern already in rest_routes.py: measure
unconditionally, emit a provenance origin, and let the threshold gate decide
pass/fail. They NEVER grant authority, NEVER mutate the ledger, NEVER rewrite
receipt history, and NEVER fabricate a PASS.

A signal is a dict with at least:
    {"floor": str, "status": PASS|FAIL|UNMEASURED|STALE|CONTRADICTED|ERROR,
     "origin": str, ...}

The function is PURE: it takes an injected `sources` dict (evidence) so the
adversarial tests can feed it the exact fabrication modes and observe rejection
without touching a live surface.

Contract per floor:
    /root/forge_work/measurement-closure-20261010/FLOOR_MEASUREMENT_CONTRACTS.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

FLOOR_STATUS = ("PASS", "FAIL", "UNMEASURED", "STALE", "CONTRADICTED", "ERROR")


def _now_iso() -> str:
    """P4 (F13 D2 2026-10-23): producer WHEN slot — emission time of THIS
    measurement, never report-generation time."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

# Conservative passing band for these four floors (matches _FLOOR_DEFAULTS
# placeholder semantics — 0.5 is the auto-pass threshold that must never be
# reached by a placeholder).
PASS_THRESHOLD = 0.5

# F2 coverage requirement (contract §5): at least this fraction of floors must
# carry non-placeholder origin for the truth floor to pass.
COVERAGE_THRESHOLD = 0.5

# Actor labels that count as sovereign/human for F13 acceptance.
SOVEREIGN_ACTORS = frozenset({"arif", "ARIF", "Arif"})

# Fields that make a seal record interpretable. A record carrying none of
# these cannot be judged: it is a shape without evidence, not a passing seal.
_SEAL_RECORD_KEYS = (
    "verdict",
    "actor",
    "payload",
    "reversibility",
    "human_ratifier",
    "human_signature",
)


def _readable_seal(record: Any) -> bool:
    """True only if this record carries enough to be judged at all.

    Empty dicts, non-dicts, and dicts of unrelated keys are unreadable.
    Cheap on purpose: this gate decides whether evidence EXISTS, not whether
    it is good — the floor's own logic decides that afterwards.
    """
    if not isinstance(record, dict):
        return False
    return any(record.get(k) not in (None, "", {}, []) for k in _SEAL_RECORD_KEYS)


_EPSILON = 1e-9


def collect_floor_producer_signal(
    floor_id: str, *, sources: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Return the measurement signal for one floor, from injected evidence.

    sources is the evidence bundle the caller gathered (provenance map,
    receipt list, trust snapshot, seal list). Omit to get the honest
    UNMEASURED for a missing source — never a fabricated PASS.
    """
    sources = sources or {}
    handler = _PRODUCERS.get(floor_id)
    if handler is None:
        return {
            "floor": floor_id,
            "status": "UNMEASURED",
            "origin": "unmeasured_default:no_producer",
            "measured_at": _now_iso(),
        }
    signal = handler(sources)
    if isinstance(signal, dict):
        # P4 (F13 D2 2026-10-23): every producer signal carries its own WHEN
        # slot — stamped at emission unless the producer already dated itself.
        signal.setdefault("measured_at", _now_iso())
    return signal


def _f2_truth(sources: dict[str, Any]) -> dict[str, Any]:
    """F2 TRUTH = the kernel's own reporting honesty, across ALL floors.

    Three checks, in order:
      1. CONTRADICTED — an origin claims a real measurement but the value
         equals the placeholder default (origin lies about its source).
      2. FAIL (greenwash) — a floor renders a passing value while its origin
         is `unmeasured_default*` (a placeholder that would falsely pass).
      3. FAIL (coverage) — provenance coverage below COVERAGE_THRESHOLD
         (contract §5: coverage ≥ N/13 floors with non-placeholder origin).
    Absent provenance map → UNMEASURED.
    """
    prov = sources.get("floor_provenance")
    if not prov:
        return {"floor": "F2", "status": "UNMEASURED", "origin": "unmeasured_default:absent"}
    resolved = sources.get("resolved_floors", {})
    defaults = sources.get("floor_defaults", {})

    total = len(prov)
    measured = sum(1 for o in prov.values() if not str(o).startswith("unmeasured_default"))
    coverage = round(measured / total, 4) if total else 0.0

    # 1. origin lies: claims a real origin but the value is the placeholder default.
    for fid, origin in prov.items():
        if str(origin).startswith("unmeasured_default"):
            continue
        v = resolved.get(fid)
        if fid in defaults and v is not None and abs(v - defaults[fid]) < _EPSILON:
            return {
                "floor": "F2",
                "status": "CONTRADICTED",
                "origin": origin,
                "reason": "origin-lies-default-value",
                "offending_floor": fid,
                "coverage": coverage,
            }

    # 2. greenwash: placeholder origin that renders a passing verdict.
    # Contract §5 & §6: "zero floors render PASS from unmeasured_default".
    # Check rendered statuses if provided, or verify against PASS_THRESHOLD if explicit pass.
    statuses = sources.get("floor_statuses")
    if statuses:
        greenwash = [
            fid
            for fid, origin in prov.items()
            if str(origin).startswith("unmeasured_default") and statuses.get(fid) == "pass"
        ]
    else:
        greenwash = [
            fid
            for fid, origin in prov.items()
            if str(origin).startswith("unmeasured_default")
            and resolved.get(fid) is not None
            and resolved.get(fid) >= PASS_THRESHOLD
        ]
    if greenwash:
        return {
            "floor": "F2",
            "status": "FAIL",
            "origin": "greenwash",
            "reason": "pass-from-placeholder",
            "offending_floors": greenwash,
            "coverage": coverage,
        }

    # 3. coverage (contract §5).
    if coverage < COVERAGE_THRESHOLD:
        return {
            "floor": "F2",
            "status": "FAIL",
            "origin": "floor_provenance_coverage",
            "reason": "insufficient-coverage",
            "coverage": coverage,
            "measured": measured,
            "total": total,
        }

    return {
        "floor": "F2",
        "status": "PASS",
        "origin": "floor_provenance_coverage",
        "coverage": coverage,
    }


def _f11_audit(sources: dict[str, Any]) -> dict[str, Any]:
    receipts = sources.get("receipts")
    if receipts is None:
        return {
            "floor": "F11",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:ledger_unreachable",
        }
    if not receipts:
        return {"floor": "F11", "status": "UNMEASURED", "origin": "unmeasured_default:ledger_empty"}
    # Known identifiers include every hash-like field a parent link may target.
    known: set[str] = set()
    for r in receipts:
        for key in ("receipt_id", "jcs_body_hash", "this_hash"):
            v = r.get(key)
            if v:
                known.add(v)
    unattributable = 0
    broken_chain = 0
    for r in receipts:
        if not r.get("actor_id") or not r.get("step_type"):
            unattributable += 1
        ph = r.get("previous_receipt_hash")
        if ph and ph not in known:
            broken_chain += 1
    if broken_chain:
        return {
            "floor": "F11",
            "status": "CONTRADICTED",
            "origin": "receipt_ledger",
            "broken_chain": broken_chain,
        }
    if unattributable:
        return {
            "floor": "F11",
            "status": "FAIL",
            "origin": "receipt_ledger",
            "unattributable": unattributable,
        }
    return {"floor": "F11", "status": "PASS", "origin": "receipt_ledger"}


def _f12_injection(sources: dict[str, Any]) -> dict[str, Any]:
    auto = sources.get("auto_sign_allowed")
    if auto is None:
        return {
            "floor": "F12",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:trust_unreadable",
        }
    declared = sources.get("declared_default")
    effective = sources.get("effective_default")
    if declared is not None and effective is not None and declared != effective:
        return {
            "floor": "F12",
            "status": "CONTRADICTED",
            "origin": "request_trust",
            "reason": "doc-code-drift",
        }
    if auto:
        return {
            "floor": "F12",
            "status": "FAIL",
            "origin": "request_trust",
            "reason": "auto_sign_open",
        }
    return {"floor": "F12", "status": "PASS", "origin": "request_trust"}


def _f13_sovereign(sources: dict[str, Any]) -> dict[str, Any]:
    """F13 SOVEREIGN = human acceptance remains separate from machine sealing.

    A seal attributed to a NON-sovereign actor is only legitimate when the
    payload carries a human ratification (`human_ratifier` / `human_signature`).
    A machine `SEAL` verdict with neither is self-acceptance → FAIL. This uses
    the live seal-chain schema, not a synthetic flag.
    """
    seals = sources.get("seals")
    if seals is None:
        return {
            "floor": "F13",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_chain_unreachable",
        }
    if not seals:
        return {
            "floor": "F13",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_chain_empty",
        }
    # ── SEAL-READABILITY GATE (F13 888_HOLD repair, 2026-10-24) ──────────
    # 888_HOLD named "{} -> PASS". Measured: {} and None already return
    # UNMEASURED. The live leak is present-but-JUNK evidence:
    #   {"seals": [{}]}  and  {"seals": [{"payload": {}}]}
    # fell through the `continue` loop to PASS on F5 and F13 — the two floors
    # that gate SEAL. Requirement #4 of the ruling forbids exactly that:
    # "malformed or insufficient producer evidence must resolve to
    # UNMEASURED". Present-but-unreadable records are not evidence; nothing
    # was observed, so nothing may pass.
    if not any(_readable_seal(s) for s in seals):
        return {
            "floor": "F13",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_records_unreadable",
        }
    for s in seals:
        actor = s.get("actor")
        if s.get("verdict") != "SEAL" or actor in SOVEREIGN_ACTORS:
            continue
        payload = s.get("payload") or {}
        ratified = (
            payload.get("human_ratifier")
            or s.get("human_ratifier")
            or payload.get("human_signature")
            or s.get("human_signature")
        )
        if not ratified:
            return {
                "floor": "F13",
                "status": "FAIL",
                "origin": "seal_chain_sovereign",
                "reason": "machine_self_acceptance",
                "actor": actor,
            }
    return {"floor": "F13", "status": "PASS", "origin": "seal_chain_sovereign"}


def _f5_peace(sources: dict[str, Any]) -> dict[str, Any]:
    """F5 PEACE² = non-destructive power (MEASUREMENT_CLOSURE tranche 2, 2026-10-20).

    Every recent seal must be either reversible or carry explicit human
    ratification for its irreversibility. An IRREVERSIBLE action without
    ratification is destructive power → FAIL. Mirrors the F13 source contract
    (seal_chain tail, read-only) so both floors read the same evidence.
    """
    seals = sources.get("seals")
    if seals is None:
        return {
            "floor": "F5",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_chain_unreachable",
        }
    if not seals:
        return {
            "floor": "F5",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_chain_empty",
        }
    # ── SEAL-READABILITY GATE (F13 888_HOLD repair, 2026-10-24) ──────────
    # 888_HOLD named "{} -> PASS". Measured: {} and None already return
    # UNMEASURED. The live leak is present-but-JUNK evidence:
    #   {"seals": [{}]}  and  {"seals": [{"payload": {}}]}
    # fell through the `continue` loop to PASS on F5 and F13 — the two floors
    # that gate SEAL. Requirement #4 of the ruling forbids exactly that:
    # "malformed or insufficient producer evidence must resolve to
    # UNMEASURED". Present-but-unreadable records are not evidence; nothing
    # was observed, so nothing may pass.
    if not any(_readable_seal(s) for s in seals):
        return {
            "floor": "F5",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_records_unreadable",
        }
    for s in seals:
        payload = s.get("payload") or {}
        # Sovereign-actor exemption — SAME doctrine line as _f13_sovereign
        # (floor_producers.py:242): the human principal acting IS human
        # ratification; demanding a second ratifier on Arif's own action is
        # a category error. F5 polices NON-sovereign destructive power.
        if s.get("actor") in SOVEREIGN_ACTORS:
            continue
        reversibility = str(
            payload.get("reversibility")
            or payload.get("reversibility_level")
            or s.get("reversibility")
            or ""
        ).upper()
        if reversibility != "IRREVERSIBLE":
            continue
        ratified = (
            payload.get("human_ratifier")
            or payload.get("human_signature")
            or s.get("human_ratifier")
            or s.get("human_signature")
        )
        if not ratified:
            return {
                "floor": "F5",
                "status": "FAIL",
                "origin": "seal_chain_peace",
                "reason": "unratified_irreversible_action",
                "actor": s.get("actor"),
            }
    # P3 (F13 D2 2026-10-23): F5 and F13 no longer share one origin — one
    # measurement may not earn two constitutional claims under one label.
    return {"floor": "F5", "status": "PASS", "origin": "seal_chain_peace"}


def _f6_maruah(sources: dict[str, Any]) -> dict[str, Any]:
    """F6 MARUAH — protected human worth (2026-10-24, MARUAH_HIKMAH_RUNTIME_WIRING).

    Source: `sources["seals"]` payloads carrying a declared `heart_critique` block
    — the SAME evidence bundle F5/F13 already read. No new ledger, no new organ.

    Dignity conflict is never averaged away: the producer short-circuits on the
    first conflict and reports FAIL. Absence of evidence is UNMEASURED, never PASS.
    It reads three declared keys and nothing else — it cannot turn a representation
    of a person into a fact about them.
    """
    seals = sources.get("seals")
    if seals is None:
        return {
            "floor": "F6",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_chain_unreachable",
        }
    reviews: list[dict[str, Any]] = []
    for s in seals:
        payload = (s or {}).get("payload") or {}
        critique = payload.get("heart_critique")
        if isinstance(critique, dict):
            reviews.append(critique)
    if not reviews:
        return {
            "floor": "F6",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:no_heart_critique",
        }
    for r in reviews:
        if r.get("coercion") is True:
            return {
                "floor": "F6",
                "status": "FAIL",
                "origin": "heart_critique",
                "reason": "coercion_present",
            }
        if str(r.get("dignity_verdict") or "").upper() == "COMPROMISED":
            return {
                "floor": "F6",
                "status": "FAIL",
                "origin": "heart_critique",
                "reason": "dignity_verdict_compromised",
            }
        dignity = r.get("dignity")
        if isinstance(dignity, (int, float)) and dignity < 0.5:
            return {
                "floor": "F6",
                "status": "FAIL",
                "origin": "heart_critique",
                "reason": "dignity_conflict",
                "dignity": dignity,
            }
    return {"floor": "F6", "status": "PASS", "origin": "heart_critique"}


_PRODUCERS = {
    "F6": _f6_maruah,
    "F2": _f2_truth,
    "F5": _f5_peace,
    "F11": _f11_audit,
    "F12": _f12_injection,
    "F13": _f13_sovereign,
}
