"""
arifosmcp/runtime/evidence_admission.py — D2 typed evidence admission.

F13 D1 ratified 2026-10-23 (QWENCODE_FEDERATION_INIT decision sheet).
Evidence enters reasoning ONLY through this gate:

    arif_think(evidence=[EvidenceObject, ...])

Contract (forge_work/2026-10-23-qwen-federation-init/08-D2-EVIDENCE-AUDIT.md):
  - Expired evidence (expires_at <= now) is omitted from the prompt and
    listed in expired_omitted — it may not silently support a live claim.
  - UNKNOWN and CONTRADICTED entries render under an explicit GATE banner
    barring them from supporting PASS/SEAL-shaped conclusions;
    CONTRADICTED entries remain visible — preserved, never averaged away.
  - Malformed entries are rejected with a reason — never crash the call.
  - The response echoes consumed ids so downstream consumers can audit what
    the reasoning actually admitted.

Pure functions, no I/O. DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

CLASSIFICATIONS = ("VERIFIED", "DERIVED", "REPORTED", "UNKNOWN", "CONTRADICTED")
GATED_CLASSIFICATIONS = ("UNKNOWN", "CONTRADICTED")
MAX_EVIDENCE = 32
MAX_FIELD_CHARS = 400

_GATE_BANNER = (
    "\nEVIDENCE GATE: entries classified UNKNOWN or CONTRADICTED may NOT be "
    "used to support PASS/SEAL-shaped conclusions. Treat UNKNOWN as an open "
    "question; preserve CONTRADICTED entries as contradictions — never "
    "average them away. Expired entries are absent by policy."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _clip(value: Any) -> str:
    text = str(value) if value is not None else ""
    return text if len(text) <= MAX_FIELD_CHARS else text[: MAX_FIELD_CHARS - 1] + "…"


def admit_evidence(
    evidence: list[dict[str, Any]] | None, now: datetime | None = None
) -> dict[str, Any]:
    """Validate and render typed evidence for one reasoning pass."""
    now = now or _now()
    summary: dict[str, Any] = {
        "prompt_block": None,
        "consumed": [],
        "admitted_items": [],
        "expired_omitted": [],
        "rejected": [],
        "counts": {"admitted": 0, "expired": 0, "rejected": 0, "gated": 0},
    }
    if not evidence:
        return summary
    if not isinstance(evidence, list):
        summary["rejected"].append({"index": 0, "reason": "evidence must be a list of objects"})
        summary["counts"]["rejected"] = 1
        return summary

    lines: list[str] = []
    for idx, item in enumerate(evidence[:MAX_EVIDENCE], start=1):
        if not isinstance(item, dict):
            summary["rejected"].append({"index": idx, "reason": "not an object"})
            summary["counts"]["rejected"] += 1
            continue
        claim = item.get("claim")
        classification = str(item.get("classification", "")).strip().upper()
        if not claim or not isinstance(claim, str):
            summary["rejected"].append({"index": idx, "reason": "missing claim"})
            summary["counts"]["rejected"] += 1
            continue
        if classification not in CLASSIFICATIONS:
            summary["rejected"].append(
                {"index": idx, "reason": f"classification must be one of {CLASSIFICATIONS}"}
            )
            summary["counts"]["rejected"] += 1
            continue

        expires_at = _parse_iso(item.get("expires_at"))
        eid = str(item.get("source_id") or f"E{idx}")
        if expires_at is not None and expires_at <= now:
            summary["expired_omitted"].append(eid)
            summary["counts"]["expired"] += 1
            continue

        subject = _clip(item.get("subject") or eid)
        observed_at = _clip(item.get("observed_at") or "unknown")
        source_uri = _clip(item.get("source_uri") or item.get("source_id") or "none")
        falsifier = _clip(item.get("falsifier") or "not-stated")
        observer = _clip(item.get("observer_actor") or "not-stated")
        lines.append(
            f"\n[{eid}] subject={subject} | {classification} | observed_at={observed_at}"
            f" | expires_at={_clip(item.get('expires_at') or 'none')}"
            f" | source={source_uri} | observer={observer}"
            f" (verified={bool(item.get('observer_verified'))})"
            f" | falsifier={falsifier}"
            f"\n    claim: {_clip(claim)}"
        )
        contradictions = item.get("contradictions") or []
        if contradictions:
            lines.append(f"    contradictions: {_clip('; '.join(map(str, list(contradictions)[:4])))}")
        summary["consumed"].append(eid)
        summary["admitted_items"].append({"eid": eid, "evidence": item})
        summary["counts"]["admitted"] += 1
        if classification in GATED_CLASSIFICATIONS:
            summary["counts"]["gated"] += 1

    if not lines:
        return summary

    header = (
        f"\n\nADMITTED EVIDENCE ({summary['counts']['admitted']} objects, "
        f"{summary['counts']['gated']} gated, {summary['counts']['expired']} expired-omitted):"
    )
    summary["prompt_block"] = header + "".join(lines)
    if summary["counts"]["gated"]:
        summary["prompt_block"] += _GATE_BANNER
    return summary
