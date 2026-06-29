"""
cooling_ledger.py — Kernel-side Cooling Ledger API for arifOS.

Substrate: Supabase Postgres (utbmmjmbolmuahwixjqc).
Tables: cooling_ledger_entries, cooling_decay_events, cooling_overrides,
        cooling_queue, vault999_witness.
Functions: apply_decay, apply_override, promote_to_vault,
           kernel_check_budget, kernel_consume_budget.

RLS policy requires app.role = 'kernel' for writes — enforced via
SET LOCAL in CoolingLedgerSession.

Doctrine: DITEMPA BUKAN DIBERI.
"""

import os
import uuid as _uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras
import psycopg2.sql

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

ORGAN_DECAY_COEFFICIENT: Dict[str, float] = {
    "GEOX": 0.05,
    "A-FORGE": 0.02,
    "arifOS": 0.01,
    "WEALTH": 0.04,
    "WELL": 0.03,
    "AAA": 0.02,
}

_DEFAULT_DECAY = 0.05

_VALID_ENTRY_TYPES = frozenset(
    {"evidence", "reasoning", "verdict_pending", "override", "failure", "witness"}
)

_POSTGRES_URL_ENV = "POSTGRES_URL"


# ---------------------------------------------------------------------------
# Domain exception
# ---------------------------------------------------------------------------


class CoolingLedgerError(Exception):
    """Raised when a cooling-ledger Postgres operation fails."""

    def __init__(self, message: str, original: Optional[Exception] = None) -> None:
        self.original = original
        detail = f"{message}"
        if original:
            detail += f"  [{original}]"
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class CoolingLedgerClient:
    """Stateless client bound to an open psycopg2 connection.

    All queries use parameterised ``%s`` placeholders.  The caller (usually
    ``CoolingLedgerSession``) is responsible for setting session-local
    GUCs (``app.role``, ``app.current_principal``, etc.) before the client
    runs any DML.
    """

    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # 1. write
    # ------------------------------------------------------------------

    def write(
        self,
        event: Dict[str, Any],
        organ: str,
        entry_type: str,
        principal_id: str,
        agent_role: str,
        lease_id: Optional[str] = None,
        epoch_id: Optional[str] = None,
    ) -> str:
        """Insert a new cooling-ledger entry and return its ``entry_id``.

        Parameters
        ----------
        event:
            JSON-serialisable payload stored in the ``payload`` column.
        organ:
            Federation organ that owns the entry (e.g. ``"GEOX"``).
        entry_type:
            One of ``evidence``, ``reasoning``, ``verdict_pending``,
            ``override``, ``failure``, ``witness``.
        principal_id:
            Human or sovereign principal identifier (text).
        agent_role:
            Role label for the calling agent.
        lease_id:
            Optional forge-lease identifier.
        epoch_id:
            Session epoch UUID.  Falls back to ``app.current_epoch`` GUC
            if not provided.

        Returns
        -------
        The UUID of the newly created entry (as a hex string).
        """
        if entry_type not in _VALID_ENTRY_TYPES:
            raise CoolingLedgerError(
                f"Invalid entry_type {entry_type!r}. Must be one of {sorted(_VALID_ENTRY_TYPES)}"
            )

        coeff = ORGAN_DECAY_COEFFICIENT.get(organ, _DEFAULT_DECAY)

        # epoch_id may be passed explicitly, otherwise rely on session GUC
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO cooling_ledger_entries
                        (epoch_id, organ, entry_type, payload, verdict_state,
                         temperature, heat_decay_coefficient,
                         principal_id, agent_role, lease_id)
                    VALUES
                        (COALESCE(%s::uuid, current_setting('app.current_epoch', true)::uuid),
                         %s, %s, %s::jsonb, 'PENDING',
                         1.0, %s,
                         %s, %s, %s)
                    RETURNING entry_id
                    """,
                    (
                        epoch_id,
                        organ,
                        entry_type,
                        psycopg2.extras.Json(event),
                        coeff,
                        principal_id,
                        agent_role,
                        lease_id,
                    ),
                )
                row = cur.fetchone()
                if row is None:
                    raise CoolingLedgerError(
                        "INSERT returned no row (RLS policy may have blocked it)."
                    )
                return str(row["entry_id"])
            except psycopg2.Error as exc:
                raise CoolingLedgerError("write() failed", original=exc) from exc

    # ------------------------------------------------------------------
    # 2. decay_tick
    # ------------------------------------------------------------------

    def decay_tick(self, entry_id: str) -> Dict[str, Any]:
        """Apply one decay cycle to a single entry.

        Calls the server-side ``apply_decay`` function which computes
        ``new_temp = temp * exp(-lambda * age_hours)`` and inserts a
        ``cooling_decay_events`` row.

        Returns
        -------
        ``{"old_temp": …, "new_temp": …, "decay_reason": "age"}``
        or an empty dict if the entry does not exist.
        """
        try:
            # apply_decay is a void function, so we read the decay event
            # that it just inserted.
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT apply_decay(%s::uuid)", (entry_id,))

            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT old_temperature, new_temperature, decay_reason
                    FROM cooling_decay_events
                    WHERE entry_id = %s::uuid
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (entry_id,),
                )
                row = cur.fetchone()
                if row is None:
                    # Entry may not exist or decay was a no-op
                    return {}
                return dict(row)
        except psycopg2.Error as exc:
            raise CoolingLedgerError(f"decay_tick({entry_id}) failed", original=exc) from exc

    # ------------------------------------------------------------------
    # 3. decay_sweep
    # ------------------------------------------------------------------

    def decay_sweep(self, organ: Optional[str] = None, min_temp: float = 0.0) -> int:
        """Apply ``apply_decay`` to every entry that matches the filter.

        Parameters
        ----------
        organ:
            If provided, only entries for this organ are decayed.
        min_temp:
            Only decay entries whose current temperature is **above** this
            threshold (strict inequality: ``temperature > min_temp``).

        Returns
        -------
        Number of entries that were decayed.
        """
        clauses: list[str] = []
        params: list[Any] = []

        if organ is not None:
            clauses.append("organ = %s")
            params.append(organ)
        if min_temp > 0.0:
            clauses.append("temperature > %s")
            params.append(min_temp)

        where = " AND ".join(clauses) if clauses else "TRUE"

        try:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                query = f"SELECT entry_id FROM cooling_ledger_entries WHERE {where}"
                cur.execute(query, params)
                rows = cur.fetchall()

            count = 0
            for row in rows:
                with self._conn.cursor() as cur:
                    cur.execute("SELECT apply_decay(%s::uuid)", (row["entry_id"],))
                count += 1
            return count
        except psycopg2.Error as exc:
            raise CoolingLedgerError("decay_sweep() failed", original=exc) from exc

    # ------------------------------------------------------------------
    # 4. override
    # ------------------------------------------------------------------

    def override(self, entry_id: str, action: str) -> str:
        """Call ``apply_override`` on an entry.

        Returns the result string (e.g. ``OK_FROZEN``, ``BLOCKED_…``).
        """
        try:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT apply_override(%s::uuid, %s) AS result",
                    (entry_id, action),
                )
                row = cur.fetchone()
                return row["result"] if row else "UNKNOWN"
        except psycopg2.Error as exc:
            raise CoolingLedgerError(
                f"override({entry_id}, {action!r}) failed", original=exc
            ) from exc

    # ------------------------------------------------------------------
    # 5. promote
    # ------------------------------------------------------------------

    def promote(self, entry_id: str) -> str:
        """Call ``promote_to_vault`` on an entry.

        Returns the vault seal identifier.
        """
        try:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT promote_to_vault(%s::uuid) AS result",
                    (entry_id,),
                )
                row = cur.fetchone()
                return row["result"] if row else "UNKNOWN"
        except psycopg2.Error as exc:
            raise CoolingLedgerError(f"promote({entry_id}) failed", original=exc) from exc

    # ------------------------------------------------------------------
    # 6–9. Query helpers
    # ------------------------------------------------------------------

    def _query(
        self,
        *,
        organ: Optional[str] = None,
        limit: int,
        where_clause: str,
        params: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generic query helper used by all ``query_*`` methods."""
        query_parts = ["SELECT * FROM cooling_ledger_entries WHERE"]
        query_params: list[Any] = []

        if params is None:
            params = []

        query_parts.append(where_clause)
        query_params.extend(params)

        if organ is not None:
            query_parts.append("AND organ = %s")
            query_params.append(organ)

        query_parts.append("ORDER BY created_at DESC LIMIT %s")
        query_params.append(limit)

        try:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(" ".join(query_parts), query_params)
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except psycopg2.Error as exc:
            raise CoolingLedgerError("query failed", original=exc) from exc

    def query_hot(self, organ: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Entries with ``temperature >= 0.5`` (still hot / unmodified)."""
        return self._query(
            organ=organ,
            limit=limit,
            where_clause="temperature >= 0.5",
        )

    def query_cool(self, organ: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Entries with ``temperature < 0.5`` (substantially cooled)."""
        return self._query(
            organ=organ,
            limit=limit,
            where_clause="temperature < 0.5",
        )

    def query_pending(self, organ: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Entries still in ``PENDING`` verdict state."""
        return self._query(
            organ=organ,
            limit=limit,
            where_clause="verdict_state = 'PENDING'",
        )

    def query_seal_ready(
        self, organ: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Entries that have graduated to ``SEAL_READY``."""
        return self._query(
            organ=organ,
            limit=limit,
            where_clause="verdict_state = 'SEAL_READY'",
        )

    # ------------------------------------------------------------------
    # Budget helpers (convenience wrappers around PG functions)
    # ------------------------------------------------------------------

    def check_budget(self, principal_id: str, epoch_id: str, action: str) -> str:
        """Call ``kernel_check_budget`` and return its verdict text."""
        try:
            with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT kernel_check_budget(%s::uuid, %s::uuid, %s) AS result",
                    (principal_id, epoch_id, action),
                )
                row = cur.fetchone()
                return row["result"] if row else "UNKNOWN"
        except psycopg2.Error as exc:
            raise CoolingLedgerError("check_budget() failed", original=exc) from exc

    def consume_budget(self, principal_id: str, epoch_id: str, action: str) -> None:
        """Call ``kernel_consume_budget`` to deduct from the principal's budget."""
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT kernel_consume_budget(%s::uuid, %s::uuid, %s)",
                    (principal_id, epoch_id, action),
                )
        except psycopg2.Error as exc:
            raise CoolingLedgerError("consume_budget() failed", original=exc) from exc


# ---------------------------------------------------------------------------
# Session context manager
# ---------------------------------------------------------------------------


@contextmanager
def CoolingLedgerSession(
    principal_id: str,
    actor: str,
    epoch_id: str,
    *,
    dsn: Optional[str] = None,
    autocommit: bool = False,
):
    """Context manager that opens a Postgres connection, sets session-local
    GUCs required by RLS, and yields a :class:`CoolingLedgerClient`.

    The GUCs set via ``SET LOCAL``:

    - ``app.role = 'kernel'``          (RLS write policy)
    - ``app.current_principal``        (audit traceability)
    - ``app.current_actor``            (agent identity)
    - ``app.current_epoch``            (session epoch)

    On success the transaction is committed; on any exception it is
    rolled back and re-raised as ``CoolingLedgerError``.

    Parameters
    ----------
    principal_id:
        UUID (or text) identifying the sovereign / human principal.
    actor:
        Agent role label (e.g. ``"test-kernel"``, ``"forge-worker"``).
    epoch_id:
        Session epoch UUID.
    dsn:
        Postgres connection string.  Defaults to the ``POSTGRES_URL``
        environment variable.
    autocommit:
        If ``True``, run in autocommit mode (useful for read-only probes).
    """
    if dsn is None:
        dsn = os.environ.get(_POSTGRES_URL_ENV)
    if not dsn:
        raise CoolingLedgerError(f"{_POSTGRES_URL_ENV} is not set and no dsn= was provided.")

    conn: Optional[psycopg2.extensions.connection] = None
    try:
        conn = psycopg2.connect(dsn)
        if autocommit:
            conn.set_session(autocommit=True)

        with conn.cursor() as cur:
            cur.execute("SET LOCAL app.role = 'kernel'")
            cur.execute("SET LOCAL app.current_principal = %s", (principal_id,))
            cur.execute("SET LOCAL app.current_actor = %s", (actor,))
            cur.execute("SET LOCAL app.current_epoch = %s", (epoch_id,))

        client = CoolingLedgerClient(conn)
        yield client
        if not autocommit:
            conn.commit()
    except Exception:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
