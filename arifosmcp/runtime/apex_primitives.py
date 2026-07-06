"""
apex_primitives.py — Derive APEX primitives from live tool call metrics
=========================================================================

Replaces system health proxy with actual tool call metrics:
  A = lease compliance rate (actions within authority)
  P = evidence floor compliance (claims with evidence)
  E = tool call success rate
  X = reversibility rate (dry-run before execute)
  Φ = scar feedback (1 - repeated_failure_rate)

MEMBRANE-01: This computation belongs in A-FORGE (actuator), not the kernel.
But it's placed here (arifOS runtime) as a TEMPORARY bridge until A-FORGE
TypeScript implementation is ready. Marked MEMBRANE_BRIDGE.

Forged: 2026-07-06 by FORGE (000Ω)
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

# ── Persistence ────────────────────────────────────────────────────────
_DB_DIR = Path("/var/lib/arifos")
_DB_PATH = _DB_DIR / "apex_metrics.db"


def _get_db() -> sqlite3.Connection:
    """Get SQLite connection. Creates tables if needed."""
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB_PATH), timeout=5)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_name TEXT NOT NULL,
            actor_id TEXT DEFAULT '',
            session_id TEXT DEFAULT '',
            timestamp TEXT NOT NULL,
            success INTEGER NOT NULL DEFAULT 1,
            has_evidence INTEGER NOT NULL DEFAULT 0,
            within_lease INTEGER NOT NULL DEFAULT 1,
            dry_run_first INTEGER NOT NULL DEFAULT 0,
            reversible INTEGER NOT NULL DEFAULT 1,
            failure_code TEXT DEFAULT '',
            metadata_json TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tool_calls_ts ON tool_calls(timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tool_calls_tool ON tool_calls(tool_name)
    """)
    conn.commit()
    return conn


def record_tool_call(
    tool_name: str,
    success: bool = True,
    has_evidence: bool = False,
    within_lease: bool = True,
    dry_run_first: bool = False,
    reversible: bool = True,
    failure_code: str = "",
    actor_id: str = "",
    session_id: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Record a tool call for APEX primitive derivation."""
    try:
        conn = _get_db()
        conn.execute(
            """INSERT INTO tool_calls
               (tool_name, actor_id, session_id, timestamp, success, has_evidence,
                within_lease, dry_run_first, reversible, failure_code, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                tool_name,
                actor_id,
                session_id,
                time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                int(success),
                int(has_evidence),
                int(within_lease),
                int(dry_run_first),
                int(reversible),
                failure_code,
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Metrics are best-effort


def compute_apex_from_metrics(window_seconds: int = 86400) -> dict[str, Any]:
    """Compute APEX primitives from recent tool call metrics.

    Returns dict with A, P, E, X, Φ, G, C_dark, W3, plus breakdown.

    Window defaults to 24h. Adjusts for empty data (returns defaults).
    """
    try:
        conn = _get_db()
        cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - window_seconds))
        rows = conn.execute(
            """SELECT success, has_evidence, within_lease, dry_run_first,
                      reversible, failure_code
               FROM tool_calls WHERE timestamp >= ?""",
            (cutoff,),
        ).fetchall()
        conn.close()

        n = len(rows)
        if n == 0:
            return _default_apex("no_data")

        successes = sum(1 for r in rows if r[0])
        with_evidence = sum(1 for r in rows if r[1])
        in_lease = sum(1 for r in rows if r[2])
        dry_runed = sum(1 for r in rows if r[3])
        reversible_count = sum(1 for r in rows if r[4])
        failure_codes = [r[5] for r in rows if r[5]]
        unique_failures = len(set(failure_codes))

        # A = lease compliance rate
        A = round(in_lease / n, 4)
        # P = evidence floor compliance
        P = round(with_evidence / n, 4) if n > 0 else 0.5
        # E = tool call success rate
        E = round(successes / n, 4)
        # X = reversibility rate (dry-run before execute)
        X = round(dry_runed / n, 4) if n > 0 else 0.5
        # Φ = scar feedback (1 - repeated_failure_rate)
        repeated_rate = unique_failures / n if n > 0 else 0
        PHI = round(max(0.0, 1.0 - repeated_rate), 4)

        # G = A · P · E · X · Φ
        G = round(A * P * E * X * PHI, 4)
        # C_dark = A · (1-P) · (1-X)
        C_dark = round(A * (1 - P) * (1 - X), 4)

        return {
            "A": A,
            "P": P,
            "E": E,
            "X": X,
            "Phi": PHI,
            "G": G,
            "C_dark": C_dark,
            "window_seconds": window_seconds,
            "sample_size": n,
            "breakdown": {
                "successes": successes,
                "with_evidence": with_evidence,
                "in_lease": in_lease,
                "dry_run_first": dry_runed,
                "reversible": reversible_count,
                "unique_failure_codes": unique_failures,
            },
            "source": "apex_primitives.py",
            "version": "apex-v1-phase2",
        }
    except Exception as e:
        return _default_apex(f"error: {e}")


def _default_apex(reason: str) -> dict[str, Any]:
    """Return safe defaults when no data available."""
    return {
        "A": 0.5,
        "P": 0.5,
        "E": 0.5,
        "X": 0.5,
        "Phi": 1.0,
        "G": 0.0625,
        "C_dark": 0.25,
        "window_seconds": 0,
        "sample_size": 0,
        "source": "apex_primitives.py",
        "version": "apex-v1-phase2",
        "note": f"Default values — {reason}",
    }
