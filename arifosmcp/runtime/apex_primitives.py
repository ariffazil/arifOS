"""
apex_primitives.py — Derive APEX primitives from live tool call metrics
=========================================================================

Replaces system health proxy with actual tool call metrics:
  A = lease compliance rate (actions within authority)
  P = evidence floor compliance (claims with evidence)
  E = execution success rate (execution-classed 2026-10-06; the canon name
      "ENTROPY×ENERGY" is CANON_DERIVED, unimplemented — rename-before-rebuild,
      THERMO-INVARIANTS Th-2)
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
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Persistence ────────────────────────────────────────────────────────
_DB_DIR = Path("/var/lib/arifos")
_DB_PATH = _DB_DIR / "apex_metrics.db"

# Outcome semantics (2026-10-06, F13 SAH — verdict-pollution fix).
# `success` conflated execution outcomes with constitutional verdicts:
# a HOLD/SABAR is the brakes working, not a crash. Measured 2026-10-06:
# 1,292/1,292 evidence-bearing "failures" were verdicts, zero true errors.
OUTCOME_EXECUTION_SUCCESS = "execution_success"
OUTCOME_EXECUTION_FAILURE = "execution_failure"
OUTCOME_CONSTITUTIONAL_HOLD = "constitutional_hold"
OUTCOME_CONSTITUTIONAL_SABAR = "constitutional_sabar"


def derive_outcome(success: bool, failure_code: str) -> str:
    """Classify a tool-call outcome. Constitutional verdicts (HOLD/SABAR)
    are NOT execution failures. Verdict rows leave E's denominator."""
    fc = (failure_code or "").strip().upper()
    if fc == "HOLD":
        return OUTCOME_CONSTITUTIONAL_HOLD
    if fc == "SABAR":
        return OUTCOME_CONSTITUTIONAL_SABAR
    return OUTCOME_EXECUTION_SUCCESS if success else OUTCOME_EXECUTION_FAILURE


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
    # 2026-10-06 outcome-semantics migration (idempotent, additive, reversible)
    try:
        conn.execute("ALTER TABLE tool_calls ADD COLUMN outcome TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # column already exists
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
    outcome: str = "",
    metadata: dict[str, Any] | None = None,
) -> None:
    """Record a tool call for APEX primitive derivation.

    `outcome` (optional, 2026-10-06): explicit outcome class. When omitted it
    is derived from (success, failure_code) — HOLD/SABAR verdicts become
    constitutional_* classes instead of execution failures. Existing callers
    need no changes; their (success, failure_code) signals classify correctly.
    """
    try:
        conn = _get_db()
        _outcome = (outcome or "").strip() or derive_outcome(success, failure_code)
        conn.execute(
            """INSERT INTO tool_calls
               (tool_name, actor_id, session_id, timestamp, success, has_evidence,
                within_lease, dry_run_first, reversible, failure_code, outcome, metadata_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                _outcome,
                json.dumps(metadata or {}),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug("apex record_tool_call failed for %s: %s", tool_name, e)


def compute_apex_from_metrics(
    window_seconds: int = 604800,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Compute APEX primitives from recent tool call metrics.

    Returns dict with A, P, E, X, Φ, G, C_dark, W3, plus breakdown.

    Window defaults to 7 days (604800s). Previous 24h window produced
    UNMEASURED on cold start because only ~10 records existed in that window.
    7-day window captures ~6-7K records with meaningful signal.
    Adjusts for empty data (returns UNMEASURED defaults).

    P0.8 FIX (2026-08-15): actor_id filter. When provided, only tool calls
    from that actor are included. Returns actor-scoped G/C_dark/h instead
    of federation-wide population average. Without actor_id, returns global.
    """
    try:
        conn = _get_db()
        cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - window_seconds))
        query = """SELECT success, has_evidence, within_lease, dry_run_first,
                      reversible, failure_code, outcome
               FROM tool_calls WHERE timestamp >= ?"""
        params: list = [cutoff]
        if actor_id:
            query += " AND actor_id = ?"
            params.append(actor_id)
        rows = conn.execute(query, params).fetchall()
        # P1 residual accounting: fetch prior window BEFORE closing (same conn)
        _cutoff_prior = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 2 * window_seconds)
        )
        _rows_prior: list = []
        try:
            _qp = """SELECT success, has_evidence, within_lease, dry_run_first,
                      reversible, failure_code, outcome
               FROM tool_calls WHERE timestamp >= ? AND timestamp < ?"""
            _pp: list = [_cutoff_prior, cutoff]
            if actor_id:
                _qp += " AND actor_id = ?"
                _pp.append(actor_id)
            _rows_prior = conn.execute(_qp, _pp).fetchall()
        except Exception:
            _rows_prior = []
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

        # Outcome classification (2026-10-06 verdict-pollution fix).
        # Legacy rows (outcome='') are derived at read time — no backfill.
        classes = [
            (r[6] or "").strip() or derive_outcome(bool(r[0]), r[5] or "")
            for r in rows
        ]
        outcome_counts: dict[str, int] = {}
        outcome_evidence: dict[str, list[int]] = {}
        for cls, r in zip(classes, rows):
            outcome_counts[cls] = outcome_counts.get(cls, 0) + 1
            outcome_evidence.setdefault(cls, [0, 0])
            outcome_evidence[cls][0] += int(bool(r[1]))
            outcome_evidence[cls][1] += 1
        exec_success = outcome_counts.get(OUTCOME_EXECUTION_SUCCESS, 0)
        exec_failure = outcome_counts.get(OUTCOME_EXECUTION_FAILURE, 0)
        exec_total = exec_success + exec_failure

        # A = lease compliance rate
        A = round(in_lease / n, 4) if n > 0 else None
        # P = evidence floor compliance
        P = round(with_evidence / n, 4) if n > 0 else None
        # E = execution success rate — constitutional verdicts (HOLD/SABAR)
        # are excluded from BOTH numerator and denominator. A brake
        # activation is not an engine failure. If the window carries only
        # verdict traffic, E is UNMEASURED (nil propagates, never coerced).
        E = round(exec_success / exec_total, 4) if exec_total > 0 else None
        # X = reversibility rate (dry-run before execute)
        X = round(dry_runed / n, 4) if n > 0 else None
        # Φ = scar feedback (1 - repeated_failure_rate)
        repeated_rate = unique_failures / n if n > 0 else 0
        PHI = round(max(0.0, 1.0 - repeated_rate), 4) if n > 0 else None

        # 2026-08-04 333-AGI: UNMEASURED propagation.
        # When no data exists (n==0), factors are None → G is UNMEASURED.
        # Previously coerced None→0.5 producing G=0.0625 as a phantom number.
        # UNMEASURED must never coerce. Nil times anything is nil.
        #
        # 2026-08-05 W-09 FIX: Switch from Nash product to geometric mean.
        # Product formula A×P×E×X collapses when any factor ≈0
        # (X=0.0013 with product gives G≈0.0 even with 4,644 samples).
        # 2026-08-05 W-12 FIX: F8 GENIUS canonical is 4 factors (A,P,E,X).
        # Φ is scar pressure (separate gate per A2 canonic), NOT a 5th G dial.
        # G = (A×P×E×X)^(1/4). Adding Φ to the product changes Nash bargaining
        # geometry and would penalize every score for having a 5th factor.
        # Also apply a floor of 0.01 to each factor to prevent collapse.
        _factors = [A, P, E, X]
        if None in _factors:
            G = None
            C_dark = None
        else:
            import math as _math

            _floored = [max(0.01, f) for f in _factors]
            _product = 1.0
            for f in _floored:
                _product *= f
            G = round(_product ** (1.0 / len(_floored)), 4)
            C_dark = round(A * (1 - P) * (1 - X), 4)

        return {
            "A": A,
            "P": P,
            "E": E,
            "X": X,
            "Phi": PHI,
            "G": G,
            "C_dark": C_dark,
            # P0 2026-08-09: W3 + h wired from live metrics (was UNMEASURED).
            # h = humility/uncertainty mass = evidence gap (1 - P).
            #   High evidence compliance → low humility mass → G_seal un-damped.
            #   Low evidence compliance → high humility mass → G_seal damped.
            # W3 = tri-witness strength = scar feedback Φ (1 - repeated failure).
            #   Witness agreement measured as: failures don't repeat.
            # P0 2026-08-09 v2 (OPENCLAW): W3 must NOT be PHI.
            # PHI is scar pressure (repeated-failure feedback) — not tri-witness.
            # Canonical W3 = ∛(H×AI×Ext) needs live witness channels, which
            # tool-call metrics do not carry. Computed in rest_routes from
            # resolved_witness. Here: honest None, never an inflated proxy.
            "W3": None,
            "h": round(1.0 - P, 4) if P is not None else None,
            "window_seconds": window_seconds,
            "sample_size": n,
            "breakdown": {
                "successes": successes,
                "with_evidence": with_evidence,
                "in_lease": in_lease,
                "dry_run_first": dry_runed,
                "reversible": reversible_count,
                "unique_failure_codes": unique_failures,
                "execution_success": exec_success,
                "execution_failure": exec_failure,
            },
            "outcome_breakdown": {
                cls: {
                    "count": outcome_counts[cls],
                    "evidence_rate": round(
                        outcome_evidence[cls][0] / outcome_evidence[cls][1], 4
                    )
                    if outcome_evidence[cls][1]
                    else None,
                }
                for cls in sorted(outcome_counts)
            },
            "E_semantics": "execution-classed; constitutional verdicts excluded (energy/entropy components CANON_DERIVED, unimplemented)",
            "gram": _gram_block(rows, classes),
            "residual": _residual_block(_rows_prior, rows),
            "source": "apex_primitives.py",
            "version": "apex-v2-outcome-semantics",
        }
    except Exception as e:
        return _default_apex(f"error: {e}")


def _gram_block(rows: list, classes: list[str]) -> dict[str, Any]:
    """Second-order observability: correlation structure of the observable
    columns (lease, evidence, execution-success, dry-run) + eigenvalues.

    Epistemic: this is OBSERVED covariance of observables. The 'scar
    covariance' reading is a separate H-class claim, not a theorem.
    numpy is optional (guarded import) — without it the block degrades to
    UNMEASURED, never to a fabricated proxy.
    """
    try:
        import numpy as _np
    except ImportError:
        return {"measurement_status": "UNMEASURED", "reason": "numpy unavailable"}
    if len(rows) < 30:
        return {"measurement_status": "UNMEASURED", "reason": "n<30"}
    obs = _np.array(
        [
            [
                float(r[2]),
                float(r[1]),
                1.0 if c == OUTCOME_EXECUTION_SUCCESS else 0.0,
                float(r[3]),
            ]
            for r, c in zip(rows, classes)
        ]
    )
    cols = ["A_within_lease", "P_has_evidence", "E_execution_success", "X_dry_run_first"]
    if float(obs.std(axis=0).min()) <= 0.0:
        return {"measurement_status": "UNMEASURED", "reason": "zero-variance column"}
    corr = _np.corrcoef(obs.T)
    eigs = _np.sort(_np.linalg.eigvalsh(corr))
    rank = int(_np.linalg.matrix_rank(corr, tol=1e-6))
    by_outcome: dict[str, float] = {}
    ev = obs[:, 1]
    for cls in sorted(set(classes)):
        ind = _np.array([1.0 if c == cls else 0.0 for c in classes])
        if ind.std() > 0 and ev.std() > 0:
            by_outcome[cls] = round(float(_np.corrcoef(ev, ind)[0, 1]), 4)
    return {
        "correlation": [[round(float(x), 4) for x in row] for row in corr],
        "columns": cols,
        "eigenvalues": [round(float(x), 4) for x in eigs],
        "rank": rank,
        "effective_dimension": rank,
        "rank_note": (
            "full rank"
            if rank == len(cols)
            else "collinear: effective dimension < columns (one voice counted twice)"
        ),
        "evidence_correlation_by_outcome": by_outcome,
        "epistemic": "OBSERVED covariance of observables; scar reading is H-class",
    }


def _reduce_letters(rows: list) -> dict[str, Any] | None:
    """Reduce a row-set to (A, P, E, X, G) with v2 outcome semantics.

    Shared by the residual block: prior-window letters serve as the naive
    persistence prediction for the current window (first honest residual
    accounting at the metric layer; DER-class, not a model).
    """
    import math as _math

    n = len(rows)
    if n == 0:
        return None
    classes = [
        (r[6] or "").strip() or derive_outcome(bool(r[0]), r[5] or "") for r in rows
    ]
    es = sum(1 for c in classes if c == OUTCOME_EXECUTION_SUCCESS)
    ef = sum(1 for c in classes if c == OUTCOME_EXECUTION_FAILURE)
    et = es + ef
    A = sum(1 for r in rows if r[2]) / n
    P = sum(1 for r in rows if r[1]) / n
    E = es / et if et > 0 else None
    X = sum(1 for r in rows if r[3]) / n
    G = None
    if E is not None:
        fs = [max(0.01, f) for f in (A, P, E, X)]
        G = float(_math.prod(fs) ** 0.25)
    return {
        "A": round(A, 4), "P": round(P, 4),
        "E": round(E, 4) if E is not None else None,
        "X": round(X, 4),
        "G": round(G, 4) if G is not None else None,
        "n": n,
    }


def w3_rank_check(*channels: list | None) -> dict[str, Any]:
    """Independence gate for W³ = ∛(H×AI×Ext).

    Cardinality is not independence (APEX GEOMETRY SUBSTRATE canon): k
    witnesses are k independent voices only if their sample vectors are not
    collinear. Returns declared vs effective witness count. Advisory until
    witness sample streams are wired; scalar channels cannot rank-check.
    """
    try:
        import numpy as _np
    except ImportError:
        return {"independence": "UNMEASURED", "reason": "numpy unavailable"}
    chs = [list(c) for c in channels if c is not None and len(c) > 0]
    k = len(chs)
    if k < 2:
        return {"independence": "UNMEASURED", "reason": "fewer than 2 witness streams"}
    M = _np.vstack([_np.asarray(c, dtype=float) for c in chs])
    if float(_np.abs(M.std(axis=1)).min()) <= 0.0:
        return {
            "witnesses_declared": k,
            "witnesses_effective": 0,
            "independence": "FAIL",
            "reason": "constant witness stream",
        }
    k_eff = int(_np.linalg.matrix_rank(M, tol=1e-6))
    return {
        "witnesses_declared": k,
        "witnesses_effective": k_eff,
        "independence": "PASS" if k_eff == k else "FAIL",
        "note": "independent" if k_eff == k else "cardinality is not independence",
    }


def _residual_block(rows_prior: list, rows_current: list) -> dict[str, Any]:
    """Persistence-basis residual: prior-window letters as the naive
    prediction for the current window. r = observed − predicted — the
    metric layer's first honest residual accounting (DER-class: naive
    persistence baseline, not a model; models arrive with J-calibration)."""
    prior = _reduce_letters(rows_prior)
    current = _reduce_letters(rows_current)
    if prior is None or current is None:
        return {
            "measurement_status": "UNMEASURED",
            "reason": "empty prior or current window",
            "prior_n": 0 if prior is None else prior["n"],
            "current_n": 0 if current is None else current["n"],
        }
    delta: dict[str, Any] = {}
    for k in ("A", "P", "E", "X", "G"):
        p, c = prior.get(k), current.get(k)
        delta[k] = None if (p is None or c is None) else round(c - p, 4)
    return {
        "basis": "persistence: prior-window letters as naive prediction",
        "prior": prior,
        "current": current,
        "delta": delta,
        "epistemic": "DER — naive persistence baseline, not a model",
    }


def _default_apex(reason: str) -> dict[str, Any]:
    """Return UNMEASURED defaults when no data available.

    2026-08-04 333-AGI: UNMEASURED propagation fix.
    G=0.0625 (product of five faked 0.5 priors) was a phantom number encoding
    "no data = maximum restriction." Replaced with None/UNMEASURED sentinel.
    Cold start = UNMEASURED, not 0.0625, not 0.80. Measure first, gate second.
    """
    return {
        "A": None,
        "P": None,
        "E": None,
        "X": None,
        "Phi": None,
        "G": None,
        "C_dark": None,
        "window_seconds": 0,
        "sample_size": 0,
        "source": "apex_primitives.py",
        "version": "apex-v2-outcome-semantics",
        "note": f"UNMEASURED — no APEX sample yet ({reason}). Not a G score.",
        "measurement_status": "UNMEASURED",
        "outcome_breakdown": {},
        "E_semantics": "execution-classed; constitutional verdicts excluded",
        "gram": {"measurement_status": "UNMEASURED", "reason": reason},
    }
