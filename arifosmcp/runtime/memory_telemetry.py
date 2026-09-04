"""Retrieval telemetry — P1 (888 audit 2026-09-05).

Instrument-first doctrine: threshold/policy decisions need real score
distributions, not guesses. Baseline observed 2026-09-05: legit queries
score 0.45–0.53, gibberish ~0.49 → current threshold 0.1 is effectively
permissive for nomic cosine. This module records every recall so the
floor can be calibrated on evidence.

Design constraints:
- Telemetry must NEVER break recall (fire-and-forget, all exceptions swallowed).
- F4: store query_hash (16 hex) + preview truncated to 60 chars, not full raw text.
- Append-only jsonl, rotate at ~10 MB (rename .1, clobber old .1).
- Report computes p50/p95/top score, admitted rate, reason distribution,
  latency percentiles — the exact axes named in the audit.

Usage:
  from arifosmcp.runtime.memory_telemetry import record_recall, report
  python3 -m arifosmcp.runtime.memory_telemetry report
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_PATH = "/var/lib/arifos/telemetry/memory_retrieval.jsonl"
_MAX_BYTES = 10 * 1024 * 1024
_PREVIEW_CHARS = 60


def _telemetry_path() -> Path:
    return Path(os.getenv("ARIFOS_MEMORY_TELEMETRY_PATH", _DEFAULT_PATH))


def _query_hash(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]


def _percentile(sorted_vals: list[float], p: float) -> float | None:
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, max(0, int(round((p / 100.0) * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def record_recall(
    query: str,
    candidates: list[dict],
    admitted: list[dict],
    reason: str | None,
    backend: str = "qdrant",
    latency_ms: float | None = None,
    extra: dict[str, Any] | None = None,
) -> bool:
    """Append one retrieval telemetry record. Never raises."""
    try:
        scores = sorted(
            c.get("score") for c in candidates if isinstance(c.get("score"), (int, float))
        )
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "query_hash": _query_hash(query),
            "query_preview": query[:_PREVIEW_CHARS],
            "backend": backend,
            "candidate_count": len(candidates),
            "admitted_count": len(admitted),
            "top_score": scores[-1] if scores else None,
            "p50_score": _percentile(scores, 50),
            "p95_score": _percentile(scores, 95),
            "top_admitted_score": max(
                (a.get("score") for a in admitted if isinstance(a.get("score"), (int, float))),
                default=None,
            ),
            "content_coerced_count": sum(1 for c in candidates if c.get("content_coerced")),
            "reason": reason,  # None when found=True; taxonomy when not-found
            "latency_ms": latency_ms,
        }
        if extra:
            rec.update(extra)

        path = _telemetry_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > _MAX_BYTES:
            rotated = path.with_suffix(".jsonl.1")
            try:
                rotated.unlink()
            except FileNotFoundError:
                pass
            path.rename(rotated)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False  # telemetry is witness, never load-bearing


def report(limit: int = 2000) -> dict[str, Any]:
    """Aggregate the telemetry file. Never raises on missing file."""
    path = _telemetry_path()
    if not path.exists():
        return {"status": "NO_DATA", "path": str(path), "note": "no telemetry recorded yet"}

    records: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as exc:
        return {"status": "READ_ERROR", "error": str(exc)}

    records = records[-limit:]
    if not records:
        return {"status": "NO_DATA", "path": str(path)}

    admitted_scores = sorted(
        r.get("top_admitted_score")
        for r in records
        if isinstance(r.get("top_admitted_score"), (int, float))
    )
    latencies = sorted(
        r.get("latency_ms") for r in records if isinstance(r.get("latency_ms"), (int, float))
    )
    reasons: dict[str, int] = {}
    for r in records:
        reason = r.get("reason") or "FOUND"
        reasons[reason] = reasons.get(reason, 0) + 1

    n = len(records)
    n_admitted = sum(1 for r in records if (r.get("admitted_count") or 0) > 0)
    return {
        "status": "OK",
        "path": str(path),
        "n_records": n,
        "admitted_rate": round(n_admitted / n, 3) if n else None,
        "admitted_top_score": {
            "p50": _percentile(admitted_scores, 50),
            "p95": _percentile(admitted_scores, 95),
            "max": admitted_scores[-1] if admitted_scores else None,
            "min": admitted_scores[0] if admitted_scores else None,
        },
        "latency_ms": {
            "p50": _percentile(latencies, 50),
            "p95": _percentile(latencies, 95),
        },
        "reason_distribution": reasons,
        "content_coerced_total": sum(r.get("content_coerced_count") or 0 for r in records),
        "window_first_ts": records[0].get("ts"),
        "window_last_ts": records[-1].get("ts"),
        "threshold_calibration_note": (
            "Compare p50/p95 of FOUND vs permissive-floor concern: if gibberish-class "
            "queries cluster near legit p50, raise _MEMORY_MIN_SCORE above that cluster."
        ),
    }


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "report":
        print(json.dumps(report(), ensure_ascii=False, indent=1))
    else:
        print(f"usage: {sys.argv[0]} report", file=sys.stderr)
        raise SystemExit(2)
