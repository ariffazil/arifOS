"""
judge_postcondition — P0-1 evidence postcondition for 888 (2026-08-15).

Mirrors the GEOX Stage-1 outputSchema enforcement (commit 80fc80fd pattern,
src/geox_mcp/evidence_postcondition.py): a verdict that claims SEAL without
substantive evidence is a FALSE SUCCESS and is downgraded.

Root cause this closes (KRT-JOHOR-2026-08-15, tri-session A/B/C):
    judge.py main path decided verdicts from session state only
    (standing/floors/grant/expiry); evidence never entered the predicate,
    so the same kernel returned HOLD, HOLD, or SEAL for the same question
    depending on which session asked. Spec:
    /root/forge_work/P0-1-JUDGE-EVIDENCE-POSTCONDITION-spec-20260815.md

Contract families (per-mode; lesson from geox_evidence 2026-08-06 — never
guess a single flat key list for a multi-mode tool):
    judge      → candidate + substantive evidence required; SEAL additionally
                 requires provenance-bearing evidence and channel integrity.
    hold/escalate → candidate required; evidence advisory.
    validate/intercept → validated elsewhere; postcondition advisory only.

Enforcement:
    EVIDENCE_EMPTY_RULE1      evidence {} / None / insubstantive  → HOLD
    EVIDENCE_POSTCONDITION_VIOLATION  SEAL w/o provenance keys   → SABAR
    CANDIDATE_MISSING         no candidate text                  → HOLD
    verdict_channel_integrity effective_verdict must track verdict

Ledger precheck (R4): reported as an advisory flag. Full blocking
enforcement flips on only when the P1 ledger truth-function lands
(ENFORCE_LEDGER_GATE) — blocking every 888 SEAL on a ledger that is a
known-open P1 surface would brick the lane rather than protect it.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger("arifosmcp.runtime.judge_postcondition")

SPEC = "judge-evidence-postcondition-v1"

# Provenance-bearing keys: SEAL requires at least one substantive entry.
_PROVENANCE_KEYS = (
    "provenance_source",
    "provenance",
    "sources",
    "source",
    "evidence_refs",
    "witness_refs",
    "citations",
    "artifacts",
    "observations",
    "facts",
    "receipts",
    "primary_sources",
)

# Modes where evidence is load-bearing for the verdict predicate.
_EVIDENCE_REQUIRED_MODES = {"judge", "jurisdiction", ""}
# Modes where the postcondition is advisory only (validated elsewhere).
_ADVISORY_MODES = {"validate", "intercept", "diagnostic"}

# R4 switch — deliberately OFF until the P1 ledger truth function lands.
ENFORCE_LEDGER_GATE = False

_SEAL_FAMILY = {"SEAL", "PARTIAL", "PROVISIONAL"}


def _is_substantive(val: Any) -> bool:
    """GEOX parity: non-null, non-empty, and not a bare falsy placeholder."""
    if val is None:
        return False
    if isinstance(val, (str, list, dict, tuple, set)):
        return len(val) > 0
    return True


def _evidence_has_provenance(evidence: dict[str, Any]) -> bool:
    for key in _PROVENANCE_KEYS:
        if _is_substantive(evidence.get(key)):
            return True
    # Any nested non-scalar structure also counts as substantive evidence.
    for val in evidence.values():
        if isinstance(val, (dict, list)) and len(val) > 0:
            return True
    return False


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()


def _sha256_obj(obj: Any) -> str:
    try:
        blob = json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))
    except Exception:
        blob = repr(obj)
    return "sha256:" + hashlib.sha256(blob.encode("utf-8", "replace")).hexdigest()


def ledger_precheck() -> dict[str, Any]:
    """Advisory R4 flag: current seal-chain head health, never blocking here."""
    try:
        from arifosmcp.runtime.seal_chain import validate_seal_chain

        try:
            report = validate_seal_chain(seal_id="head")
        except TypeError:
            report = validate_seal_chain("head")
        if isinstance(report, dict):
            return {
                "available": True,
                "verified": report.get("verified", report.get("integrity") == "OK"),
                "chain_status": report.get("chain_status"),
                "gap_count": report.get("gap_count"),
            }
        return {"available": True, "verified": None}
    except Exception as exc:  # noqa: BLE001 — advisory path must never throw
        return {"available": False, "error": str(exc)[:200]}


def check_judge_postcondition(
    *,
    mode: str | None,
    candidate: Any,
    evidence: Any,
    verdict_str: str,
    effective_verdict: str | None = None,
) -> dict[str, Any]:
    """Evaluate the 888 evidence contract. Pure function, never raises.

    Returns a report dict; ``applied`` is True when the postcondition
    actively rewrote the verdict (downgrade), False when it only annotated.
    """
    mode_key = (mode or "").strip().lower()
    verdict_key = (verdict_str or "").strip().upper()
    eff_key = (effective_verdict or "").strip().upper()
    cand_text = candidate if isinstance(candidate, str) else json.dumps(candidate, default=str)
    cand_ok = _is_substantive(cand_text)
    ev = evidence if isinstance(evidence, dict) else ({} if evidence is None else {"value": evidence})
    ev_ok = bool(ev) and any(_is_substantive(v) for v in ev.values())

    report: dict[str, Any] = {
        "spec": SPEC,
        "mode": mode_key or "judge",
        "candidate_hash": _sha256_text(cand_text or "") if cand_ok else None,
        "evidence_digest": _sha256_obj(ev) if ev_ok else None,
        "verdict_channel_integrity": (eff_key == verdict_key) if eff_key else None,
        "missing_evidence": [],
        "ledger_precheck": None,
        "enforce_ledger_gate": ENFORCE_LEDGER_GATE,
    }

    # Advisory modes: annotate and leave the verdict untouched.
    if mode_key in _ADVISORY_MODES:
        report.update({"applied": False, "verdict": verdict_key or None, "reason_code": None})
        return report

    missing: list[str] = []

    if not cand_ok:
        missing.append("candidate")
    if not ev_ok:
        missing.append("evidence")

    # Rule #1 — empty evidence may never pass as a verdict of record.
    if (mode_key in _EVIDENCE_REQUIRED_MODES or mode_key in _ADVISORY_MODES) and not ev_ok:
        report.update(
            {
                "applied": True,
                "verdict": "HOLD",
                "reason_code": "EVIDENCE_EMPTY_RULE1",
                "missing_evidence": missing or ["evidence"],
            }
        )
        return report

    if not cand_ok:
        report.update(
            {
                "applied": True,
                "verdict": "HOLD",
                "reason_code": "CANDIDATE_MISSING",
                "missing_evidence": missing,
            }
        )
        return report

    # SEAL family requires provenance-bearing evidence + channel integrity.
    if verdict_key in _SEAL_FAMILY:
        if not _evidence_has_provenance(ev):
            report["missing_evidence"].append("provenance")
        if report["verdict_channel_integrity"] is False:
            report["missing_evidence"].append("verdict_channel_integrity")
        ledger = ledger_precheck()
        report["ledger_precheck"] = ledger
        if ENFORCE_LEDGER_GATE and ledger.get("verified") is False:
            report["missing_evidence"].append("ledger_verified")
        if report["missing_evidence"]:
            report.update(
                {
                    "applied": True,
                    "verdict": "SABAR",
                    "reason_code": "EVIDENCE_POSTCONDITION_VIOLATION",
                }
            )
            return report

    report.update({"applied": False, "verdict": verdict_key or None, "reason_code": None})
    return report
