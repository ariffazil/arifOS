"""
governed_vs_baseline.py — Compare governed path vs ungoverned baseline
=======================================================================

Instrumentation to measure the value of the governance layer:
  - false_lurus_rate: how often baseline would say "proceed" when governed says HOLD
  - sesat_detection_rate: how many failures the governance layer catches
  - repeated_failure_recurrence: does PARUT actually prevent repeat failures?
  - transport_success_rate: governed vs baseline tool call success

MEMBRANE_BRIDGE: Temporary arifOS location. Moves to A-FORGE when
TypeScript instrumentation is ready.

Forged: 2026-07-06 by FORGE (000Ω)
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

_DB_DIR = Path("/var/lib/arifos")
_DB_PATH = _DB_DIR / "apex_metrics.db"


def _get_db() -> sqlite3.Connection:
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS governed_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            governed_verdict TEXT NOT NULL,
            baseline_verdict TEXT NOT NULL,
            sesat_detected INTEGER DEFAULT 0,
            sesat_code TEXT DEFAULT '',
            measurement_G REAL DEFAULT 0,
            measurement_C_dark REAL DEFAULT 0,
            actor_id TEXT DEFAULT '',
            session_id TEXT DEFAULT ''
        )
    """)
    conn.commit()
    return conn


def record_comparison(
    tool_name: str,
    governed_verdict: str,
    baseline_verdict: str,
    sesat_detected: bool = False,
    sesat_code: str = "",
    measurement_G: float = 0.0,
    measurement_C_dark: float = 0.0,
    actor_id: str = "",
    session_id: str = "",
) -> None:
    """Record a governed-vs-baseline comparison event."""
    try:
        conn = _get_db()
        conn.execute(
            """INSERT INTO governed_events
               (timestamp, tool_name, governed_verdict, baseline_verdict,
                sesat_detected, sesat_code, measurement_G, measurement_C_dark,
                actor_id, session_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                tool_name,
                governed_verdict,
                baseline_verdict,
                int(sesat_detected),
                sesat_code,
                measurement_G,
                measurement_C_dark,
                actor_id,
                session_id,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def compute_comparison_metrics(window_seconds: int = 86400) -> dict[str, Any]:
    """Compute governed-vs-baseline comparison metrics."""
    try:
        conn = _get_db()
        cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - window_seconds))
        rows = conn.execute(
            """SELECT governed_verdict, baseline_verdict, sesat_detected,
                      measurement_G, measurement_C_dark
               FROM governed_events WHERE timestamp >= ?""",
            (cutoff,),
        ).fetchall()
        conn.close()

        n = len(rows)
        if n == 0:
            return {
                "sample_size": 0,
                "note": "No comparison data yet",
                "source": "governed_vs_baseline.py",
            }

        governed_hold = sum(1 for r in rows if r[0] in ("HOLD", "VOID", "SABAR"))
        baseline_proceed = sum(1 for r in rows if r[1] == "ALLOW")
        sesat_caught = sum(1 for r in rows if r[2])
        false_lurus = sum(1 for r in rows if r[1] == "ALLOW" and r[0] in ("HOLD", "VOID"))

        return {
            "sample_size": n,
            "false_lurus_rate": round(false_lurus / n, 4) if n > 0 else 0,
            "sesat_detection_rate": round(sesat_caught / n, 4) if n > 0 else 0,
            "governed_hold_rate": round(governed_hold / n, 4) if n > 0 else 0,
            "baseline_proceed_rate": round(baseline_proceed / n, 4) if n > 0 else 0,
            "governance_value": round(false_lurus / n, 4) if n > 0 else 0,
            "window_seconds": window_seconds,
            "source": "governed_vs_baseline.py",
            "version": "phase2-v1",
            "note": (
                "governance_value = false_lurus_rate = how often baseline would "
                "proceed when governed layer says HOLD. Higher = governance more valuable."
            ),
        }
    except Exception as e:
        return {"error": str(e), "sample_size": 0}
