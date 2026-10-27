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


# Epistemic keys a caller may use to declare an item unwitnessed (D2, 2026-10-28).
_EPISTEMIC_KEYS = (
    "tag",
    "claim_class",
    "truth_class",
    "label",
    "epistemic_tag",
    "epistemic",
    "epistemic_status",
    "status",
)
# Tokens that mean "nobody witnessed this" (D4: KX-007 names three; code matched one).
_UNWITNESSED_TOKENS = ("UNKNOWN", "UNK", "UNMEASURED", "UNVERIFIED", "UNWITNESSED")


def _coerce_evidence(evidence: Any, _depth: int = 0) -> Any:
    """Parse schema-legal transports: `evidence` may arrive as a JSON string (D1).

    Repeated encoding (a JSON string wrapping a JSON string) is unwrapped up to
    three times; beyond that the value is treated as opaque.
    """
    if _depth >= 3 or not isinstance(evidence, str):
        return evidence
    txt = evidence.strip()
    if txt.startswith("```"):  # fenced block from a chat client
        txt = txt.strip("`")
        if txt.lower().startswith("json"):
            txt = txt[4:]
    try:
        parsed = json.loads(txt)
    except (ValueError, TypeError):
        return None
    return _coerce_evidence(parsed, _depth + 1) if isinstance(parsed, str) else parsed


def _iter_evidence_items(evidence: Any, _depth: int = 0):
    """Yield candidate dicts from any depth of the caller's transport.

    D2 follow-up (2026-10-28, verifier red-team): an item may nest its own
    evidence list ("sources", "facts", "claims"), and an envelope may carry a
    top-level "fact" summary. Yielding the container AND recursing into every
    dict/list value means neither shape can hide a tagged child.
    """
    if _depth > 6:
        return
    data = _coerce_evidence(evidence)
    if isinstance(data, list):
        for entry in data:
            yield from _iter_evidence_items(entry, _depth + 1)
        return
    if not isinstance(data, dict):
        return
    yield data
    for value in data.values():
        if isinstance(value, (list, dict)):
            yield from _iter_evidence_items(value, _depth + 1)


def _witness_token(value: Any) -> str | None:
    """Normalise a declared epistemic status; tolerate case, spacing, trailing punctuation."""
    if not isinstance(value, str):
        return None
    token = value.strip().rstrip(".;,").strip().upper()
    return token if token in _UNWITNESSED_TOKENS else None


def _collect_unwitnessed(evidence: Any) -> list[dict[str, Any]]:
    """Items that self-declare an unwitnessed epistemic status, on any shape."""
    found: list[dict[str, Any]] = []
    for idx, item in enumerate(_iter_evidence_items(evidence)):
        field = value = None
        for key, candidate in item.items():
            if str(key).lower() in _EPISTEMIC_KEYS:
                value = _witness_token(candidate)
                if value:
                    field = str(key)
                    break
        if field is None and isinstance(item.get("meta"), dict):
            for key, candidate in item["meta"].items():
                if str(key).lower() in _EPISTEMIC_KEYS:
                    value = _witness_token(candidate)
                    if value:
                        field = f"meta.{key}"
                        break
        if field is not None:
            found.append(
                {
                    "index": idx,
                    "field": field,
                    "value": value,
                    "item": str(item.get("fact") or item)[:160],
                }
            )
    return found


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
    _coerced = _coerce_evidence(evidence)
    ev = (
        _coerced
        if isinstance(_coerced, dict)
        else ({} if _coerced is None else {"value": _coerced})
    )
    ev_ok = bool(ev) and any(_is_substantive(v) for v in ev.values())
    # An unparseable string transport is opaque evidence, not absent evidence:
    # disclose it so the caller is not left guessing why nothing was detected.
    evidence_opaque_string = isinstance(evidence, str) and _coerced is None and bool(evidence.strip())

    report: dict[str, Any] = {
        "spec": SPEC,
        "mode": mode_key or "judge",
        "candidate_hash": _sha256_text(cand_text or "") if cand_ok else None,
        "evidence_digest": _sha256_obj(ev) if ev_ok else None,
        "verdict_channel_integrity": (eff_key == verdict_key) if eff_key else None,
        "missing_evidence": [],
        "ledger_precheck": None,
        "enforce_ledger_gate": ENFORCE_LEDGER_GATE,
        "evidence_opaque_string": evidence_opaque_string,
    }

    # Unwitnessed evidence is disclosed on EVERY path, including advisory modes
    # (D3, 2026-10-28): mode=intercept is the pre-flight gate a caller uses to
    # decide whether to proceed, so it may not hide an UNKNOWN-tagged item.
    unwitnessed = _collect_unwitnessed(evidence)
    report["unwitnessed_evidence"] = unwitnessed

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

    # `unwitnessed` was computed once, before any early return (see above), so
    # every path — advisory, empty-evidence, candidate-missing, full — discloses
    # the same epistemic surface. The SEAL family additionally must not rest on
    # self-declared unknowns.

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
        if unwitnessed:
            # A seal may not rest on evidence that declares itself unwitnessed.
            report["missing_evidence"].append("unwitnessed_evidence_items")
        # S4 (F13 FIX-S4 2026-09-22): a stage-invalid integrity bit is
        # superseded by the rewrite below. Keeping False would re-fire at
        # reconcile time as a Point-#4 epistemic veto — HOLD became
        # self-perpetuating because a judge could never clear inherited
        # state. The conservative downgrade STILL fires for substantive
        # evidence gaps (provenance / ledger / empty evidence via Rule #1);
        # only the stale cross-stage comparison stops vetoing. Final
        # cross-key coherence remains reconcile_decision_contract's job.
        if report.get("verdict_channel_integrity") is False and report["missing_evidence"]:
            report["missing_evidence"] = [
                m for m in report["missing_evidence"] if m != "verdict_channel_integrity"
            ]
            report["verdict_channel_integrity"] = None
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
