"""
core/shared/paradox_ledger.py — ATLAS333 Paradox Activation Ledger

Append-only SQLite ledger for persistent paradox state over time.
Records every Φ() classification event so ATLAS333 can remember
the terrain it has traversed.

ARCHITECTURE:
    Φ() → resolve_paradox_axes() → record_paradox_event() → atlas_ledger.db
                                          │
                                          └─ try/except: NEVER blocks kernel (F1)

SCHEMA (paradox_events):
    id          INTEGER PRIMARY KEY AUTOINCREMENT
    timestamp   TEXT NOT NULL       — ISO 8601 UTC
    session_id  TEXT NOT NULL        — arifOS session identifier
    query_hash  TEXT                 — SHA-256 of input text (privacy-preserving)
    lane        TEXT NOT NULL        — Λ output: CRISIS|FACTUAL|SOCIAL|CARE|UNKNOWN
    tau         REAL NOT NULL        — Θ truth demand [0.0, 1.0]
    kappa       REAL NOT NULL        — Θ care demand [0.0, 1.0]
    rho         REAL NOT NULL        — Θ risk level [0.0, 1.0]
    paradox_id  TEXT NOT NULL        — canonical paradox ID (e.g. "P16")
    tension_score REAL NOT NULL      — GPV activation weight (rho for this activation)
    catalyst    TEXT                 — brief string or hash of trigger input
    zone        TEXT                 — derived zone I-VII
    verdict     TEXT                 — final verdict if known at write time

F1 FAIL-SAFE:
    All write operations are wrapped in try/except.
    If the ledger is locked, corrupt, or unavailable:
      → swallow exception
      → log warning via standard logging
      → release control to arifOS immediately
    The cognitive observer CANNOT crash the execution shell.

READ OPERATIONS (safe, never mutate):
    get_recent_events(n)     — last N paradox activations
    get_session_events(sid)  — all events for a session
    count_paradox_activations(pid, since) — recurrence count for EUREKA threshold
    get_zone_profile(sid)    — zone distribution for session

DITEMPA BUKAN DIBERI — Forged 2026-08-05 by 333-AGI Δ MIND
"""

from __future__ import annotations

import hashlib
import logging
import sqlite3
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("arifos.atlas.ledger")

# ── Storage location ──────────────────────────────────────────────────────
LEDGER_DIR = Path("/root/.local/share/arifos/atlas333")
LEDGER_PATH = LEDGER_DIR / "atlas_ledger.db"

# ── Zone mapping ──────────────────────────────────────────────────────────
# Maps paradox IDs to their ATLAS333 zone (I-VII)
# Reference: arifos://atlas333/zones
PARADOX_ZONE_MAP: dict[int, str] = {
    # Zone I — Truth Territory (euclidean, surface)
    1: "I",
    2: "I",
    3: "I",
    4: "I",
    # Zone I + Mind paradoxes
    12: "I",
    13: "I",
    14: "I",
    15: "I",
    16: "I",
    # Zone II — Risk Frontier (hyperbolic, deep)
    6: "II",
    7: "II",
    8: "II",
    9: "II",
    23: "II",
    24: "II",
    25: "II",
    26: "II",
    # Zone III — Care Basin (spherical, intimate)
    11: "III",
    15: "III",
    16: "III",
    17: "III",
    32: "III",
    # Zone IV — Meaning Meridian (toroidal, recursive)
    5: "IV",
    18: "IV",
    19: "IV",
    20: "IV",
    24: "IV",
    # Zone V — Discovery Ridge (fractal, emergent)
    3: "V",
    19: "V",
    21: "V",
    22: "V",
    25: "V",
    # Zone VI — Governance Spine (crystalline, constitutional)
    26: "VI",
    27: "VI",
    28: "VI",
    29: "VI",
    30: "VI",
    31: "VI",
    # Zone VII — Sovereign Apex (singular, absolute)
    29: "VII",
    31: "VII",
    33: "VII",
    34: "VII",
    35: "VII",
}


def _get_connection() -> sqlite3.Connection:
    """Get a thread-safe connection to the ledger database."""
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LEDGER_PATH), timeout=2.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrent access
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=2000")  # 2 second busy timeout
    conn.row_factory = sqlite3.Row
    return conn


def init_ledger() -> None:
    """Initialize the ledger schema. Idempotent — safe to call on every import."""
    try:
        conn = _get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS paradox_events (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       TEXT    NOT NULL,
                session_id      TEXT    NOT NULL,
                query_hash      TEXT,
                lane            TEXT    NOT NULL,
                tau             REAL    NOT NULL,
                kappa           REAL    NOT NULL,
                rho             REAL    NOT NULL,
                paradox_id      TEXT    NOT NULL,
                tension_score   REAL    NOT NULL,
                catalyst        TEXT,
                zone            TEXT,
                verdict         TEXT
            )
        """)
        # Indexes for the read operations we'll need immediately
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_paradox_events_timestamp
            ON paradox_events(timestamp DESC)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_paradox_events_session
            ON paradox_events(session_id)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_paradox_events_paradox_id
            ON paradox_events(paradox_id)
        """)
        conn.commit()
        logger.info("ATLAS333 paradox ledger initialized at %s", LEDGER_PATH)
    except Exception as e:
        logger.warning("Failed to initialize paradox ledger: %s", e)
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
# WRITE OPERATIONS — F1 FAIL-SAFE
# ════════════════════════════════════════════════════════════════════════════


def record_paradox_event(
    session_id: str,
    paradox_id: str,
    tension_score: float,
    catalyst: str = "",
    lane: str = "UNKNOWN",
    tau: float = 0.5,
    kappa: float = 0.5,
    rho: float = 0.0,
    query_hash: str = "",
    verdict: str = "UNKNOWN",
) -> bool:
    """Record a single paradox activation event to the ledger.

    F1 FAIL-SAFE: If the ledger is locked/corrupt/unavailable, swallows
    the exception and returns False. NEVER raises. NEVER blocks the kernel.

    Args:
        session_id:   arifOS session identifier
        paradox_id:   canonical paradox ID (e.g. "P16")
        tension_score: GPV activation weight (typically rho)
        catalyst:     brief description or hash of what triggered activation
        lane:         Λ classification
        tau:          truth demand
        kappa:        care demand
        rho:          risk level
        query_hash:   SHA-256 prefix of input text
        verdict:      final verdict if known (SEAL|HOLD|SABAR|VOID|UNKNOWN)

    Returns:
        True if recorded successfully, False if swallowed (ledger failure)
    """
    try:
        timestamp = datetime.now(UTC).isoformat()
        # Parse paradox number for zone lookup
        try:
            paradox_num = int(paradox_id.replace("P", "").replace("p", ""))
        except (ValueError, AttributeError):
            paradox_num = 0
        zone = PARADOX_ZONE_MAP.get(paradox_num, "")

        conn = _get_connection()
        conn.execute(
            """
            INSERT INTO paradox_events
                (timestamp, session_id, query_hash, lane, tau, kappa, rho,
                 paradox_id, tension_score, catalyst, zone, verdict)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                session_id,
                query_hash,
                lane,
                tau,
                kappa,
                rho,
                paradox_id,
                tension_score,
                catalyst[:500] if catalyst else "",  # truncate for sanity
                zone,
                verdict,
            ),
        )
        conn.commit()
        logger.debug(
            "Paradox event recorded: %s | session=%s | lane=%s | τ=%.2f κ=%.2f ρ=%.2f",
            paradox_id,
            session_id[:12],
            lane,
            tau,
            kappa,
            rho,
        )
        return True

    except Exception as e:
        logger.warning(
            "Paradox ledger write FAILED (swallowed — F1 fail-safe): %s | paradox=%s session=%s",
            e,
            paradox_id,
            session_id[:12] if session_id else "?",
        )
        return False

    finally:
        try:
            conn.close()
        except Exception:
            pass


def record_paradox_batch(
    session_id: str,
    paradox_ids: list[int],
    lane: str = "UNKNOWN",
    tau: float = 0.5,
    kappa: float = 0.5,
    rho: float = 0.0,
    catalyst: str = "",
    query_hash: str = "",
    verdict: str = "UNKNOWN",
) -> int:
    """Record multiple paradox activations for a single Φ() classification.

    F1 FAIL-SAFE: wraps each insert. Returns count of successfully recorded events.
    Partial failures are logged but do not block remaining inserts.

    Returns:
        Number of events successfully recorded.
    """
    count = 0
    for pid in paradox_ids:
        if record_paradox_event(
            session_id=session_id,
            paradox_id=f"P{pid}",
            tension_score=rho,
            catalyst=catalyst,
            lane=lane,
            tau=tau,
            kappa=kappa,
            rho=rho,
            query_hash=query_hash,
            verdict=verdict,
        ):
            count += 1
    return count


# ════════════════════════════════════════════════════════════════════════════
# READ OPERATIONS — safe, never mutate
# ════════════════════════════════════════════════════════════════════════════


def get_recent_events(n: int = 100) -> list[dict]:
    """Return the N most recent paradox events.

    Read-only. Safe for any caller.
    """
    try:
        conn = _get_connection()
        rows = conn.execute(
            "SELECT * FROM paradox_events ORDER BY timestamp DESC LIMIT ?",
            (n,),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning("Paradox ledger read failed: %s", e)
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_session_events(session_id: str) -> list[dict]:
    """Return all paradox events for a given session.

    Read-only.
    """
    try:
        conn = _get_connection()
        rows = conn.execute(
            "SELECT * FROM paradox_events WHERE session_id = ? ORDER BY timestamp",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning("Session events read failed: %s", e)
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


def count_paradox_activations(
    paradox_id: str,
    since_timestamp: Optional[str] = None,
) -> int:
    """Count how many times a paradox has activated.

    Used for EUREKA threshold: paradox N in 3+ sessions = candidate.

    Args:
        paradox_id:      canonical ID like "P16"
        since_timestamp: ISO 8601 cutoff (optional)

    Returns:
        Activation count, or 0 on error.
    """
    try:
        conn = _get_connection()
        if since_timestamp:
            row = conn.execute(
                """
                SELECT COUNT(*) as cnt FROM paradox_events
                WHERE paradox_id = ? AND timestamp >= ?
                """,
                (paradox_id, since_timestamp),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM paradox_events WHERE paradox_id = ?",
                (paradox_id,),
            ).fetchone()
        return row["cnt"] if row else 0
    except Exception as e:
        logger.warning("Paradox count failed: %s", e)
        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


def count_distinct_sessions(paradox_id: str) -> int:
    """Count how many distinct sessions have activated a specific paradox.

    This is the EUREKA threshold metric: if paradox N appears in 3+ distinct
    sessions with unresolved tension, it matures into a EUREKA candidate.
    """
    try:
        conn = _get_connection()
        row = conn.execute(
            """
            SELECT COUNT(DISTINCT session_id) as cnt FROM paradox_events
            WHERE paradox_id = ?
            """,
            (paradox_id,),
        ).fetchone()
        return row["cnt"] if row else 0
    except Exception as e:
        logger.warning("Distinct session count failed: %s", e)
        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_zone_profile(session_id: Optional[str] = None) -> dict[str, float]:
    """Compute zone activation profile.

    If session_id provided, returns profile for that session only.
    Otherwise returns aggregate across all recorded events.

    Returns:
        Dict of zone_id → activation_count, e.g. {"I": 12, "VI": 5, "VII": 3}
    """
    try:
        conn = _get_connection()
        if session_id:
            rows = conn.execute(
                """
                SELECT zone, COUNT(*) as cnt FROM paradox_events
                WHERE session_id = ? AND zone != ''
                GROUP BY zone
                """,
                (session_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT zone, COUNT(*) as cnt FROM paradox_events
                WHERE zone != ''
                GROUP BY zone
                """
            ).fetchall()
        return {r["zone"]: r["cnt"] for r in rows}
    except Exception as e:
        logger.warning("Zone profile read failed: %s", e)
        return {}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_paradox_column(limit: int = 50) -> list[dict]:
    """Return events ordered by timestamp for stratigraphic rendering.

    This powers the Paradox Column visualizer — sessions as geological layers.
    """
    return get_recent_events(limit)


def get_ledger_stats() -> dict:
    """Return summary statistics about the ledger."""
    try:
        conn = _get_connection()
        total = conn.execute("SELECT COUNT(*) as cnt FROM paradox_events").fetchone()
        sessions = conn.execute(
            "SELECT COUNT(DISTINCT session_id) as cnt FROM paradox_events"
        ).fetchone()
        top_paradoxes = conn.execute(
            """
            SELECT paradox_id, COUNT(*) as cnt FROM paradox_events
            GROUP BY paradox_id ORDER BY cnt DESC LIMIT 10
            """
        ).fetchall()
        return {
            "total_events": total["cnt"] if total else 0,
            "distinct_sessions": sessions["cnt"] if sessions else 0,
            "top_paradoxes": [
                {"paradox_id": r["paradox_id"], "count": r["cnt"]} for r in top_paradoxes
            ],
            "ledger_path": str(LEDGER_PATH),
        }
    except Exception as e:
        logger.warning("Ledger stats failed: %s", e)
        return {"error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
# EUREKA DETECTOR — Cross-Session Paradox Maturity
# ════════════════════════════════════════════════════════════════════════════
# PURE READ OPERATIONS — never mutate, never auto-resolve.
#
# When a paradox appears in 3+ distinct sessions without resolution,
# it matures into a EUREKA_CANDIDATE — a structural insight that
# must be routed to 888-APEX for sovereign review.
#
# This is the thermodynamic engine: paradox tension → repeat activation
# → maturity → EUREKA_CANDIDATE → F13 ratification → SCAR or RESOLUTION.
#
# The detector NEVER self-seals. It emits CANDIDATE only.
# The verdict belongs to 888-APEX. The seal belongs to F13.

EUREKA_SESSION_THRESHOLD = 3  # Paradox must appear in 3+ distinct sessions


def check_eureka_threshold(paradox_id: str, min_sessions: int = EUREKA_SESSION_THRESHOLD) -> dict:
    """Check whether a specific paradox has matured into a EUREKA candidate.

    PURE READ. Never mutates. Emits CANDIDATE — never SEAL.

    Args:
        paradox_id:  canonical ID like "P16" or "P26"
        min_sessions: threshold for distinct sessions (default: 3)

    Returns:
        Dict with verdict, paradox_id, session_count, and action.
        If threshold not met, verdict is "IMMATURE".
        If threshold met, verdict is "EUREKA_CANDIDATE" with routing instruction.
    """
    session_count = count_distinct_sessions(paradox_id)
    total_activations = count_paradox_activations(paradox_id)

    if session_count >= min_sessions:
        return {
            "verdict": "EUREKA_CANDIDATE",
            "paradox_id": paradox_id,
            "distinct_sessions": session_count,
            "total_activations": total_activations,
            "threshold": min_sessions,
            "action": (
                f"Paradox {paradox_id} has activated in {session_count} distinct sessions. "
                "Route to 888-APEX for constitutional review. "
                "DO NOT auto-resolve. DO NOT auto-seal. "
                "This is a CANDIDATE — the verdict belongs to the Sovereign."
            ),
            "recommended_route": "888-APEX",
            "state": "PENDING_REVIEW",
        }

    return {
        "verdict": "IMMATURE",
        "paradox_id": paradox_id,
        "distinct_sessions": session_count,
        "total_activations": total_activations,
        "threshold": min_sessions,
        "sessions_remaining": min_sessions - session_count,
        "state": "ACCUMULATING",
    }


def scan_eureka_candidates(
    min_sessions: int = EUREKA_SESSION_THRESHOLD,
    paradox_ids: Optional[list[int]] = None,
) -> list[dict]:
    """Scan all (or specified) paradoxes for EUREKA maturity.

    PURE READ. Returns list of candidates meeting the threshold,
    ordered by session_count descending (most mature first).

    Args:
        min_sessions: threshold for distinct sessions (default: 3)
        paradox_ids:  specific paradox IDs to check (default: all 1-35)

    Returns:
        List of candidate dicts, each with verdict, paradox_id, session_count.
        Empty list if no paradoxes meet the threshold.
    """
    if paradox_ids is None:
        paradox_ids = list(range(1, 36))

    candidates = []
    for pid in paradox_ids:
        result = check_eureka_threshold(f"P{pid}", min_sessions=min_sessions)
        if result["verdict"] == "EUREKA_CANDIDATE":
            candidates.append(result)

    # Sort by session count descending — most mature first
    candidates.sort(key=lambda c: c["distinct_sessions"], reverse=True)
    return candidates


def get_eureka_report(min_sessions: int = EUREKA_SESSION_THRESHOLD) -> dict:
    """Generate a comprehensive EUREKA report for 888-APEX review.

    PURE READ. Includes:
    - Active candidates (meeting threshold)
    - Approaching candidates (1-2 sessions away)
    - Ledger summary statistics
    - Recommended sovereign actions

    Returns:
        Dict with full report suitable for constitutional review.
    """
    candidates = scan_eureka_candidates(min_sessions=min_sessions)

    # Also find paradoxes that are close to threshold
    approaching = []
    for pid in range(1, 36):
        result = check_eureka_threshold(f"P{pid}", min_sessions=min_sessions)
        remaining = result.get("sessions_remaining", 999)
        if 1 <= remaining <= 2:
            approaching.append(result)

    approaching.sort(key=lambda c: c.get("sessions_remaining", 999))

    stats = get_ledger_stats()

    return {
        "report_type": "EUREKA_DETECTOR_SCAN",
        "generated_at": datetime.now(UTC).isoformat(),
        "threshold": {"min_distinct_sessions": min_sessions},
        "candidates": candidates,
        "candidate_count": len(candidates),
        "approaching": approaching,
        "approaching_count": len(approaching),
        "ledger_summary": stats,
        "sovereign_action_required": len(candidates) > 0,
        "recommended_next": (
            "Route EUREKA_CANDIDATES to 888-APEX for constitutional review. "
            "Each candidate must be individually judged: SEAL (ratify as scar), "
            "HOLD (more evidence needed), or VOID (dismiss). "
            "The detector DOES NOT decide — it only detects."
        ),
    }


# ── Initialize on import ───────────────────────────────────────────────────
# The ledger schema is created idempotently on first import.
# Safe to call — CREATE TABLE IF NOT EXISTS.
init_ledger()

__all__ = [
    "record_paradox_event",
    "record_paradox_batch",
    "get_recent_events",
    "get_session_events",
    "count_paradox_activations",
    "count_distinct_sessions",
    "get_zone_profile",
    "get_paradox_column",
    "get_ledger_stats",
    "check_eureka_threshold",
    "scan_eureka_candidates",
    "get_eureka_report",
    "EUREKA_SESSION_THRESHOLD",
    "LEDGER_PATH",
    "PARADOX_ZONE_MAP",
]
