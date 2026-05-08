"""
VAULT999 append-only audit trail for WEALTH governance decisions.
Writes to Supabase PostgreSQL via HTTP REST API (no psycopg needed).

Uses Supabase REST API: https://utbmmjmbolmuahwixjqc.supabase.co
Tables: public.wealth_transactions, public.arifosmcp_vault_seals,
        public.arifosmcp_portfolio_snapshots, public.arifosmcp_sessions

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

import hashlib
import json
import os
import time
from datetime import datetime, date, timezone
from typing import Any, Dict, Optional, List

import httpx

DEFAULT_VAULT_PATH = os.path.join(os.getcwd(), "data", "vault999.jsonl")
INTEGRITY_SALT = "WEALTH-VAULT999-2026"
SUPABASE_URL = "https://utbmmjmbolmuahwixjqc.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV0Ym1tam1ib2xtdWFod2l4anFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY0MTQzMzEsImV4cCI6MjA5MTk5MDMzMX0.Nxg2Rkf-PyqnemVGz-_H1VW22jhNbmq67hH6EZ2EzEs"

_MIGRATED = False
_client: Optional[httpx.AsyncClient] = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=SUPABASE_URL,
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            timeout=10.0,
        )
    return _client


async def _close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


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

    entry = json.dumps(_sanitize(payload))
    try:
        path = os.path.join(os.getcwd(), "data", "vault999.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


async def _supabase_insert(
    table: str, record: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Insert record into Supabase table via REST API. Returns inserted row or None."""
    client = _get_client()
    try:
        response = await client.post(f"/rest/v1/{table}", json=record)
        if response.status_code in (200, 201):
            if response.headers.get("prefer") == "return=representation":
                return response.json()
            return {"status": "INSERTED", "table": table}
        else:
            return {
                "status": "ERROR",
                "table": table,
                "code": response.status_code,
                "body": response.text,
            }
    except Exception as e:
        return {"status": "ERROR", "table": table, "exception": str(e)}


async def _supabase_rpc(fn: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Call a Supabase RPC function."""
    client = _get_client()
    try:
        response = await client.post(f"/rest/v1/rpc/{fn}", json=params)
        if response.status_code in (200, 201):
            return response.json()
        return {
            "status": "ERROR",
            "rpc": fn,
            "code": response.status_code,
            "body": response.text,
        }
    except Exception as e:
        return {"status": "ERROR", "rpc": fn, "exception": str(e)}


async def _supabase_select(
    table: str,
    params: Dict[str, Any],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Select rows from Supabase table via REST API. Returns list of rows."""
    client = _get_client()
    try:
        query_params = "&".join(f"{k}={v}" for k, v in params.items())
        response = await client.get(
            f"/rest/v1/{table}?{query_params}&limit={limit}",
            headers={"Prefer": "count=none"},
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def query_vault999(
    query: str,
    limit: int = 10,
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query the VAULT999 ledger via Supabase REST API.

    Args:
        query:       Search text (matches tool name or action)
        limit:       Max rows to return (default 10)
        session_id:  Optional session filter

    Returns:
        dict with records list, earth_refs, and count
    """
    loop = __import__("asyncio").get_event_loop()
    filters = {"order": "epoch.desc", "limit": str(limit)}
    if session_id:
        filters["session_id"] = f"eq.{session_id}"
    if query:
        filters["action"] = f"ilike.%{query}%"

    rows = loop.run_until_complete(_supabase_select("wealth_transactions", filters, limit))

    earth_refs = []
    for row in rows:
        earth_refs.append(
            {
                "tx_id": row.get("id"),
                "tool": row.get("tool"),
                "action": row.get("action"),
                "epoch": row.get("epoch"),
                "integrity": row.get("integrity", "")[:16],
            }
        )

    return {
        "query": query,
        "records": rows,
        "earth_refs": earth_refs,
        "count": len(rows),
        "vault_seal": "VAULT999",
    }


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
    Record a financial transaction to public.wealth_transactions via Supabase REST API.

    Args:
        tx_type:        income | expense | investment | dividend | fee | other
        amount:         Positive for inflow, negative for outflow
        currency:       ISO 4217 code (e.g. MYR, USD)
        description:    Human-readable transaction description
        quantity:       Number of units (optional)
        price:          Price per unit (optional)
        fees:           Transaction fees (optional)
        broker:         Broker/exchange name (optional)
        asset_id:       Asset identifier (optional)
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
        "asset": asset_id or "",
        "amount": amount,
        "currency": currency,
        "metadata": metadata or {},
        "epoch": datetime.now(timezone.utc).isoformat(),
        "integrity": integrity,
    }

    result = {}
    try:
        loop = __import__("asyncio").get_event_loop()
        if loop.is_running():
            import asyncio

            result = asyncio.run(_supabase_insert("wealth_transactions", record))
        else:
            result = loop.run_until_complete(
                _supabase_insert("wealth_transactions", record)
            )
    except Exception:
        _fallback_jsonl({**record, "source_tool": source_tool, "verdict": "VAULT999"})
        return {"status": "NO_ASYNC", "integrity": integrity}

    if result and result.get("status") == "INSERTED":
        return {"integrity": integrity, "status": "INSERTED"}
    _fallback_jsonl({**record, "source_tool": source_tool, "verdict": "VAULT999"})
    return {"integrity": integrity, "status": (result or {}).get("status", "ERROR")}


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
    Snapshot a tool computation result to public.arifosmcp_portfolio_snapshots.

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
        "snapshot_ts": datetime.now(timezone.utc).isoformat(),
        "holdings": _safe_arg(arguments),
        "total_value": nav_myr,
        "currency": currency,
        "integrity": integrity,
    }

    try:
        loop = __import__("asyncio").get_event_loop()
        if loop.is_running():
            import asyncio

            result_obj = asyncio.run(
                _supabase_insert("arifosmcp_portfolio_snapshots", record)
            )
        else:
            result_obj = loop.run_until_complete(
                _supabase_insert("arifosmcp_portfolio_snapshots", record)
            )
    except Exception:
        _fallback_jsonl({"tool": tool_name, "scale_mode": scale_mode, "epoch": epoch})
        return {"status": "NO_ASYNC", "integrity": integrity}

    if result_obj and result_obj.get("status") == "INSERTED":
        return {"integrity": integrity, "status": "INSERTED"}
    return {
        "integrity": integrity,
        "status": (result_obj or {}).get("status", "ERROR"),
    }


def append_vault999(
    record: Dict[str, Any], path: str = DEFAULT_VAULT_PATH
) -> Dict[str, Any]:
    """
    Legacy VAULT999 append — auto-snapshots to portfolio_snapshots on scale_mode
    triggers (national/civilization/agentic/crisis), and records as transaction
    if the governance verdict is SEAL and scale is high.
    """
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

    # Always mirror to local append-only ledger
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass

    return entry


def health_check() -> Dict[str, Any]:
    """Check vault Supabase connectivity and table readiness."""
    try:
        client = _get_client()
        loop = __import__("asyncio").get_event_loop()
        if loop.is_running():
            import asyncio

            response = asyncio.run(
                client.get("/rest/v1/wealth_transactions?select=id&limit=1")
            )
        else:
            response = loop.run_until_complete(
                client.get("/rest/v1/wealth_transactions?select=id&limit=1")
            )

        if response.status_code == 200:
            return {
                "status": "CONNECTED",
                "supabase_url": SUPABASE_URL,
                "pg_available": True,
                "wealth_tables_exist": True,
            }
        return {
            "status": f"ERROR_{response.status_code}",
            "pg_available": True,
            "wealth_tables_exist": False,
        }
    except Exception as e:
        return {
            "status": "NO_CONNECTION",
            "pg_available": False,
            "fallback": "jsonl",
            "error": str(e),
        }
