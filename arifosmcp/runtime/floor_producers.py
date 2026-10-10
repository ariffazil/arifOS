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

from typing import Any

FLOOR_STATUS = ("PASS", "FAIL", "UNMEASURED", "STALE", "CONTRADICTED", "ERROR")

# Conservative passing band for these four floors (matches _FLOOR_DEFAULTS
# placeholder semantics — 0.5 is the auto-pass threshold that must never be
# reached by a placeholder).
PASS_THRESHOLD = 0.5

# F2 coverage requirement (contract §5): at least this fraction of floors must
# carry non-placeholder origin for the truth floor to pass.
COVERAGE_THRESHOLD = 0.5

# Actor labels that count as sovereign/human for F13 acceptance.
SOVEREIGN_ACTORS = frozenset({"arif", "ARIF", "Arif"})

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
        }
    return handler(sources)


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

    # 2. greenwash: placeholder origin that would render a passing value.
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
                "origin": "seal_chain",
                "reason": "machine_self_acceptance",
                "actor": actor,
            }
    return {"floor": "F13", "status": "PASS", "origin": "seal_chain"}


_PRODUCERS = {
    "F2": _f2_truth,
    "F11": _f11_audit,
    "F12": _f12_injection,
    "F13": _f13_sovereign,
}
