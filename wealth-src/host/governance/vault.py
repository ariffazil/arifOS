"""
VAULT999 append-only audit trail for WEALTH governance decisions.
Writes to PostgreSQL arifos_vault.wealth.{transactions,portfolio_snapshots,fx_rates,watchlist}
via DATABASE_URL environment variable.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import hashlib
import json
import os
from datetime import datetime, date, timezone
from typing import Any, Dict, Optional
from contextlib import contextmanager

try:
    import psycopg

    PSYCOPG_AVAILABLE = True
except Exception:
    psycopg = None
    PSYCOPG_AVAILABLE = False

try:
    from .vault_supabase import append_vault999 as _vault_append

    SUPABASE_VAULT = True
except Exception:
    _vault_append = None
    SUPABASE_VAULT = False

DEFAULT_VAULT_PATH = os.path.join(os.getcwd(), "data", "vault999.jsonl")
INTEGRITY_SALT = "WEALTH-VAULT999-2026"

_MIGRATED = False


def _ensure_tables(cur) -> None:
    global _MIGRATED
    if _MIGRATED:
        return
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wealth.transactions (
            id              BIGSERIAL PRIMARY KEY,
            asset_id        TEXT        NOT NULL DEFAULT '',
            tx_type         VARCHAR(50) NOT NULL,
            quantity        NUMERIC,
            price           NUMERIC,
            fx_rate         NUMERIC,
            currency        VARCHAR(10),
            fees            NUMERIC,
            broker          TEXT,
            tx_date         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            notes           TEXT,
            source          TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW(),
            integrity       TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wealth.portfolio_snapshots (
            id              BIGSERIAL PRIMARY KEY,
            snapshot_date   DATE        NOT NULL DEFAULT CURRENT_DATE,
            asset_id        TEXT        NOT NULL DEFAULT '',
            quantity_held   NUMERIC,
            price_close     NUMERIC,
            nav_myr         NUMERIC,
            currency        VARCHAR(10),
            created_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    _MIGRATED = True


def _pg_connection():
    if not PSYCOPG_AVAILABLE:
        import sys

        sys.stderr.write(f"VAULT999_PG: psycopg not available\n")
        return None
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not url:
        import sys

        sys.stderr.write(f"VAULT999_PG: DATABASE_URL/POSTGRES_URL not set in env\n")
        return None
    try:
        conn = psycopg.connect(url, autocommit=True, connect_timeout=5)
        return conn
    except Exception as e:
        import sys

        sys.stderr.write(f"VAULT999_PG_CONNECT_FAILED:{type(e).__name__}:{e}\n")
        return None


@contextmanager
def _get_cursor():
    conn = _pg_connection()
    if conn is None:
        yield None
        return
    try:
        with conn.cursor() as cur:
            yield cur
    finally:
        conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _compute_integrity(payload: Dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True) + INTEGRITY_SALT
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def _safe_arg(arg: Any) -> Any:
    if isinstance(arg, dict):
        return {
            k: v
            for k, v in arg.items()
            if k.lower() not in ("password", "token", "key", "secret", "bearer")
        }
    return arg


def _fallback_jsonl(payload: Dict[str, Any]) -> None:
    def _sanitize(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, (dict, list)):
            return (
                {k: _sanitize(v) for k, v in obj.items()}
                if isinstance(obj, dict)
                else [_sanitize(x) for x in obj]
            )
        return obj

    import sys

    entry = json.dumps(_sanitize(payload))
    try:
        path = os.path.join(os.getcwd(), "data", "vault999.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        sys.stderr.write(f"VAULT999_FALLBACK:{entry}\n")


def record_transaction(
    tx_type: str,
    amount: float,
    currency: str,
    description: str,
    quantity: Optional[float] = None,
    price: Optional[float] = None,
    fees: Optional[float] = None,
    broker: Optional[str] = None,
    asset_id: Optional[str] = None,
    category: Optional[str] = None,
    source_tool: Optional[str] = None,
    notes: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record a financial transaction to arifos_vault.wealth.transactions.

    Args:
        tx_type:        income | expense | investment | dividend | fee | other
        amount:         Positive for inflow, negative for outflow
        currency:       ISO 4217 code (e.g. MYR, USD)
        description:    Human-readable transaction description
        quantity:       Number of units (optional)
        price:          Price per unit (optional)
        fees:           Transaction fees (optional)
        broker:         Broker/exchange name (optional)
        asset_id:       Asset identifier (optional, links to wealth.assets)
        category:       Internal category tag (optional)
        source_tool:    Name of tool that triggered this record
        notes:          Free-text notes (optional)
        metadata:       Additional structured data (optional)

    Returns:
        dict with tx_id, integrity, and status
    """
    epoch = _now_iso()
    integrity = _compute_integrity(
        {
            "tx_type": tx_type,
            "amount": amount,
            "currency": currency,
            "epoch": epoch,
            "vault_seal": "VAULT999",
        }
    )

    record = {
        "tx_type": tx_type,
        "amount": amount,
        "quantity": quantity,
        "price": price,
        "currency": currency,
        "fees": fees,
        "broker": broker,
        "asset_id": asset_id or "",
        "tx_date": datetime.now(timezone.utc),
        "notes": notes or (json.dumps(metadata) if metadata else None),
        "source": source_tool or "wealth_record_transaction",
        "created_at": datetime.now(timezone.utc),
        "integrity": integrity,
        "epoch": epoch,
        "vault_seal": "VAULT999",
    }

    with _get_cursor() as cur:
        if cur is not None:
            try:
                _ensure_tables(cur)
                cur.execute(
                    """
                    INSERT INTO wealth.transactions
                    (asset_id, tx_type, quantity, price, currency, fees, broker, tx_date, notes, source, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        record["asset_id"],
                        record["tx_type"],
                        record["quantity"],
                        record["price"],
                        record["currency"],
                        record["fees"],
                        record["broker"],
                        record["tx_date"],
                        record["notes"],
                        record["source"],
                        record["created_at"],
                    ),
                )
                row = cur.fetchone()
                record["tx_id"] = row[0] if row else None
                record["status"] = "INSERTED"
            except Exception as e:
                record["status"] = "ERROR"
                record["pg_error"] = str(e)
                _fallback_jsonl(record)
        else:
            record["status"] = "NO_PG_CONNECTION"
            _fallback_jsonl(record)

    return record


def snapshot_portfolio(
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
    scale_mode: str = "enterprise",
    asset_id: Optional[str] = None,
    nav_myr: Optional[float] = None,
    quantity_held: Optional[float] = None,
    price_close: Optional[float] = None,
    currency: str = "MYR",
) -> Dict[str, Any]:
    """
    Snapshot a tool computation result to arifos_vault.wealth.portfolio_snapshots.

    Args:
        tool_name:   Name of the WEALTH tool called
        arguments:  Arguments passed to the tool
        result:     Full result dict from the tool
        scale_mode: enterprise|personal|civilization|agentic|crisis
        asset_id:   Asset identifier (optional)
        nav_myr:    Net asset value in MYR (optional)
        quantity_held: Units held (optional)
        price_close: Closing price (optional)
        currency:   Currency code (default MYR)

    Returns:
        dict with snapshot_id, integrity, and status
    """
    epoch = _now_iso()
    integrity = _compute_integrity(
        {
            "tool_name": tool_name,
            "scale_mode": scale_mode,
            "epoch": epoch,
            "vault_seal": "VAULT999",
        }
    )

    record = {
        "snapshot_date": datetime.now(timezone.utc).date(),
        "asset_id": asset_id or "",
        "quantity_held": quantity_held,
        "price_close": price_close,
        "nav_myr": nav_myr,
        "currency": currency,
        "tool_called": tool_name,
        "args_json": json.dumps(_safe_arg(arguments)),
        "result_json": json.dumps(_safe_arg(result)),
        "scale_mode": scale_mode,
        "verdict": result.get("governance_verdict", result.get("verdict", "SEAL")),
        "computed_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "integrity": integrity,
        "epoch": epoch,
        "vault_seal": "VAULT999",
    }

    with _get_cursor() as cur:
        if cur is not None:
            try:
                _ensure_tables(cur)
                cur.execute(
                    """
                    INSERT INTO wealth.portfolio_snapshots
                    (snapshot_date, asset_id, quantity_held, price_close, nav_myr, currency, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        record["snapshot_date"],
                        record["asset_id"],
                        record["quantity_held"],
                        record["price_close"],
                        record["nav_myr"],
                        record["currency"],
                        record["created_at"],
                    ),
                )
                row = cur.fetchone()
                record["snapshot_id"] = row[0] if row else None
                record["status"] = "INSERTED"
            except Exception as e:
                record["status"] = "ERROR"
                record["pg_error"] = str(e)
                _fallback_jsonl(record)
        else:
            record["status"] = "NO_PG_CONNECTION"
            _fallback_jsonl(record)

    return record


def append_vault999(
    record: Dict[str, Any], path: str = DEFAULT_VAULT_PATH
) -> Dict[str, Any]:
    """
    Legacy VAULT999 append — auto-snapshots to portfolio_snapshots on scale_mode
    triggers (national/civilization/agentic/crisis), and records as transaction
    if the governance verdict is SEAL and scale is high.

    Tries psycopg (native Postgres) first, falls back to Supabase REST API,
    then falls back to no-op with jsonl dump.
    """
    if SUPABASE_VAULT and _vault_append is not None:
        try:
            return _vault_append(record, path)
        except Exception:
            pass

    tool = record.get("tool", "unknown")
    scale_mode = record.get("scale_mode", "enterprise")
    verdict = record.get("governance_verdict", record.get("verdict", "SEAL"))
    args = record.get("args", record.get("arguments", {}))

    epoch = record.get("epoch") or _now_iso()
    integrity = _compute_integrity(
        {
            "tool": tool,
            "scale_mode": scale_mode,
            "verdict": verdict,
            "epoch": epoch,
            "vault_seal": "VAULT999",
        }
    )
    entry = {
        **record,
        "epoch": epoch,
        "vault_seal": "VAULT999",
        "integrity": integrity,
    }

    snap_result = snapshot_portfolio(
        tool_name=tool,
        arguments=_safe_arg(args),
        result=record,
        scale_mode=scale_mode,
    )
    entry["snapshot_result"] = snap_result

    if verdict == "SEAL" and scale_mode in (
        "national",
        "crisis",
        "civilization",
        "agentic",
    ):
        tx_result = record_transaction(
            tx_type="allocation",
            amount=record.get("amount", 0),
            currency="MYR",
            description=f"[{scale_mode.upper()}] {tool} → {verdict}",
            source_tool=tool,
            notes=f"Scale: {scale_mode}, Integrity: {integrity[:16]}",
        )
        entry["transaction_result"] = tx_result

    return entry


def health_check() -> Dict[str, Any]:
    """Check vault DB connectivity and table readiness."""
    with _get_cursor() as cur:
        if cur is None:
            return {
                "status": "NO_PG_CONNECTION",
                "pg_available": False,
                "fallback": "jsonl",
                "wealth_tables_exist": False,
            }
        try:
            _ensure_tables(cur)
            cur.execute("SELECT COUNT(*) FROM wealth.transactions")
            tx_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM wealth.portfolio_snapshots")
            snap_count = cur.fetchone()[0]
            return {
                "status": "CONNECTED",
                "pg_available": True,
                "transactions_count": tx_count,
                "snapshots_count": snap_count,
                "wealth_tables_exist": True,
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "pg_available": True,
                "error": str(e),
                "wealth_tables_exist": False,
            }
