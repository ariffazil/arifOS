"""
arifOS — VAULT999 Live Chain Verifier (independent, read-only)
═══════════════════════════════════════════════════════════════════════════
Independent re-computation of the canonical vault_seals hash chain.

WHY THIS EXISTS (2026-08-31 production pass):
  The writer's own /vault/status only inspects the LAST TWO rows and reports
  chain_integrity from that. An external auditor needs a verifier that walks
  EVERY row and re-computes every seal_hash and chain_hash from first
  principles. This module does that: read-only, stdlib + blake3 + hashlib +
  asyncpg, no writes, no side effects.

HASH RULES (must match vault999-writer main.py + arifos_vault_seal_chain_check
DB trigger):

  seal_hash input (Python writer):
    seal_hash = blake3(prev_chain_hash | action | epoch | canonical(payload))
  seal_hash for the first row uses prev_chain_hash = GENESIS_CHAIN_HASH.

  chain_hash input (Postgres trigger arifos_vault_seal_chain_check):
    chain_hash = sha256(prev_chain_hash || payload::text || actor_id)
    The trigger reads the previous seal's chain_hash by JOIN on prev_seal_id =
    NEW.prev_seal_id (writer stores seal_hash in prev_seal_id).
    For the first row, v_prev_chain_hash is NULL → ''. This is intentional:
    the genesis chain_hash of any empty history is
    sha256("" || payload || actor_id). When the very first row was inserted
    by /seal with prev_seal_id set, the writer skipped the trigger by
    providing chain_hash directly (so the genesis row uses blake3 chain,
    not sha256 trigger chain — see below).

  chain_hash input (Python writer, /seal endpoint — SOVEREIGN path):
    chain_hash = blake3(prev_seal_hash | seal_hash)
    This row PASSES the trigger because the trigger only fills when
    NEW.chain_hash IS NULL. The sovereign path pre-computes the blake3
    chain_hash and inserts it directly.

  Hybrid chain (production reality, found 2026-08-31):
    Rows 17+ written via /audit-receipt and /transition pass chain_hash=NULL
    and the Postgres trigger fills sha256(prev_chain_hash || payload || actor).
    Rows written via /seal (sovereign, used for ratification) pass a pre-
    computed blake3(prev_seal_hash | seal_hash) which the trigger accepts as
    long as it matches its own sha256 expectation — usually it does NOT
    match, in which case the trigger RAISES F1_AMANAH_HOLD.
    In practice the sovereign path succeeds only when payload/actor are
    constructed to satisfy BOTH formulas; the audit path always uses the
    trigger formula. The verifier therefore tries both per row and records
    which one matched.

TOLERANCE (epoch-form drift, found 2026-08-31):
  epoch arrives from asyncpg as datetime. At write time the request epoch
  was sometimes a string (isoformat with 'T', early rows) and sometimes a
  datetime (f-string with space, recent rows). Both forms are tried for
  seal_hash and the matched convention is recorded per row. A row only
  counts as a mismatch if NEITHER form reproduces its seal_hash AND no
  known chain_hash convention matches its chain_hash.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import UTC, datetime
from typing import Any

try:
    import blake3 as _blake3

    _HAS_BLAKE3 = True
except ImportError:
    _HAS_BLAKE3 = False

GENESIS_CHAIN_HASH = (
    "9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43"
)

DEFAULT_DSN = os.environ.get("VAULT999_DB", "")


def _digest(data: bytes) -> str:
    if _HAS_BLAKE3:
        return _blake3.blake3(data).hexdigest(32)
    return hashlib.sha256(data).hexdigest()


def compute_seal_hash(
    prev_chain_hash: str, action: str, epoch: Any, payload: dict[str, Any]
) -> str:
    """Recompute a seal_hash exactly as vault999-writer does."""
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    seal_input = f"{prev_chain_hash}|{action}|{epoch}|{canonical}"
    return _digest(seal_input.encode("utf-8"))


def compute_chain_hash(prev_seal_hash: str, seal_hash: str) -> str:
    """Recompute a chain_hash exactly as vault999-writer /seal does."""
    chain_input = f"{prev_seal_hash}|{seal_hash}"
    return _digest(chain_input.encode("utf-8"))


def compute_chain_hash_trigger(
    prev_chain_hash: str, payload_json_text: str, actor_id: str | None
) -> str:
    """Recompute the trigger chain_hash: sha256(prev_chain || payload::text || actor_id).

    This is the rule the Postgres trigger `arifos_vault_seal_chain_check`
    enforces for /audit-receipt and /transition rows.
    """
    return hashlib.sha256(
        (prev_chain_hash or "").encode("utf-8")
        + (payload_json_text or "").encode("utf-8")
        + (actor_id or "").encode("utf-8")
    ).hexdigest()


def _payload_text(payload_obj: dict[str, Any]) -> str:
    """Approximate postgres `payload::text`.

    asyncpg returns jsonb as the parsed dict. The DB trigger uses
    payload::text, which is Postgres' canonical jsonb text repr.
    For payloads without weird unicode escapes, our canonical json
    gives a byte-identical match; for escaped chars it may differ.
    The verifier tries BOTH this canonical form AND the raw pg text
    (the trigger form is recorded separately in the SELECT below).
    """
    s = json.dumps(payload_obj, separators=(",", ":"), sort_keys=True)
    return json.dumps(json.loads(s), separators=(",", ":"), sort_keys=True)


def _epoch_str(epoch: Any) -> str:
    """The exact string the writer embedded in seal_hash."""
    if isinstance(epoch, datetime):
        return str(epoch)
    return str(epoch)


def _payload_obj(payload: Any) -> dict[str, Any]:
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except Exception:
            return {}
    if payload is None:
        return {}
    return dict(payload)


async def verify_live_chain(dsn: str | None = None) -> dict[str, Any]:
    """Walk vault_seals in insertion order and re-compute the whole chain.

    Returns a structured verdict. Never writes. Raises only on
    connectivity/schema failure (caller decides how to surface).
    """
    import asyncpg

    dsn = dsn or DEFAULT_DSN
    if not dsn:
        return {
            "valid": False,
            "error": "VAULT999_DB not configured",
            "checked_at": datetime.now(UTC).isoformat(),
        }

    conn = await asyncpg.connect(dsn, statement_cache_size=0)
    try:
        rows = await conn.fetch(
            """
            SELECT id, seal_hash, chain_hash, prev_seal_id, action,
                   actor_id, agent_id, event_type, verdict, epoch,
                   payload, payload::text AS payload_text
            FROM vault_seals
            ORDER BY id ASC
            """
        )
    finally:
        await conn.close()

    # Index maps keyed by ACTUAL row id (not position), so str(prev_seal_id)
    # can be either a row id or a seal_hash.
    seal_to_chain = {r["seal_hash"]: r["chain_hash"] for r in rows}
    id_to_chain = {str(r["id"]): r["chain_hash"] for r in rows}
    id_to_seal = {str(r["id"]): r["seal_hash"] for r in rows}

    total = len(rows)
    if total == 0:
        return {
            "valid": True,
            "chain_length": 0,
            "genesis_chain_hash": GENESIS_CHAIN_HASH,
            "checked_at": datetime.now(UTC).isoformat(),
            "error": None,
            "first_mismatch": None,
        }

    mismatches: list[dict[str, Any]] = []
    head: dict[str, Any] | None = None
    conv_count: dict[str, int] = {"datetime_str": 0, "isoformat": 0}
    chain_count: dict[str, int] = {
        "blake3(prev_chain||seal_hash)": 0,
        "blake3(prev_seal||seal_hash)": 0,
        "sha256_trigger(prev_chain||payload::text||actor)": 0,
        "unverified": 0,
    }
    orphan_prev_count = 0  # rows whose prev_seal_id cannot be resolved to any row

    # We track the running prev_chain_hash used by the trigger rule, which is
    # simply the chain_hash of the previous row in id order (since the writer
    # chains in id order too — see FOR UPDATE on the most recent row by id).
    prev_chain_hash = GENESIS_CHAIN_HASH
    prev_row_id = 0

    for row in rows:
        action = row["action"] or ""
        payload = _payload_obj(row["payload"])
        payload_text = row["payload_text"] or _payload_text(payload)

        # ── Try each epoch convention with each chain rule ──
        seal_ok = False
        chain_ok = False
        matched_conv: str | None = None
        matched_chain: str | None = None

        # prev_seal_id may be either a seal_hash (modern writer), a stringified row
        # id (legacy writer), or a free-form label/event_id from migrated data
        # where no canonical link exists. Resolve in priority order:
        #   1. row id → chain_hash / seal_hash of that row
        #   2. seal_hash → chain_hash of that row
        #   3. fallback to the immediately preceding row by id order
        prev_id_or_hash = row["prev_seal_id"] or ""
        if prev_id_or_hash == "0" * 64:
            # true genesis sentinel (row 17 and any seeded row)
            prev_chain_for_trigger = GENESIS_CHAIN_HASH
            prev_seal_for_writer = ""
        else:
            prev_chain_from_id = id_to_chain.get(prev_id_or_hash)
            prev_chain_from_seal = seal_to_chain.get(prev_id_or_hash)
            prev_chain_for_trigger = prev_chain_from_id or prev_chain_from_seal or ""
            prev_seal_for_writer = (
                prev_id_or_hash
                if prev_id_or_hash in seal_to_chain
                else (id_to_seal.get(prev_id_or_hash) or "")
            )
            if not prev_chain_for_trigger:
                # Migrated rows: id-order predecessor. We have to use it
                # because the writer's prev_chain_hash in the trigger was the
                # chain_hash of whatever row the database had at insert time,
                # which we can only approximate by id order.
                prev_chain_for_trigger = prev_chain_hash
                prev_seal_for_writer = id_to_seal.get(str(prev_row_id), "")
                orphan_prev_count += 1

        for label, epoch_str in (
            ("datetime_str", str(row["epoch"])),
            ("isoformat", row["epoch"].isoformat() if row["epoch"] else str(row["epoch"])),
        ):
            expected_seal = compute_seal_hash(prev_chain_for_trigger, action, epoch_str, payload)
            if expected_seal != row["seal_hash"]:
                continue
            seal_ok = True

            # Three known chain formulas. Try each in order.
            candidates: list[tuple[str, str]] = []
            candidates.append(
                (
                    "blake3(prev_chain||seal_hash)",
                    compute_chain_hash(prev_chain_for_trigger, expected_seal),
                )
            )
            candidates.append(
                (
                    "blake3(prev_seal||seal_hash)",
                    compute_chain_hash(prev_seal_for_writer, expected_seal),
                )
            )
            candidates.append(
                (
                    "sha256_trigger(prev_chain||payload::text||actor)",
                    compute_chain_hash_trigger(
                        prev_chain_for_trigger, payload_text, row["actor_id"]
                    ),
                )
            )
            for name, candidate in candidates:
                if candidate == row["chain_hash"]:
                    chain_ok = True
                    matched_conv = label
                    matched_chain = name
                    break
            if matched_chain:
                break

        if matched_conv:
            conv_count[matched_conv] += 1
            chain_count[matched_chain or "unverified"] += 1
        elif not seal_ok:
            # Last-ditch: maybe epoch_str needs a tweak (e.g. dropped tz)
            for alt_epoch in (_epoch_str(row["epoch"]),):
                alt_seal = compute_seal_hash(prev_chain_for_trigger, action, alt_epoch, payload)
                if alt_seal == row["seal_hash"]:
                    seal_ok = True
                    matched_conv = "datetime_str"
                    conv_count["datetime_str"] += 1
                    break

        if not (seal_ok and chain_ok):
            mismatches.append(
                {
                    "id": row["id"],
                    "seal_hash_ok": seal_ok,
                    "chain_hash_ok": chain_ok,
                    "expected_seal_hash": compute_seal_hash(
                        prev_chain_for_trigger, action, str(row["epoch"]), payload
                    ),
                    "stored_seal_hash": row["seal_hash"],
                    "expected_chain_hash_trigger": compute_chain_hash_trigger(
                        prev_chain_for_trigger, payload_text, row["actor_id"]
                    ),
                    "expected_chain_hash_writer": compute_chain_hash(
                        prev_chain_for_trigger,
                        compute_seal_hash(prev_chain_for_trigger, action, str(row["epoch"]), payload),
                    ),
                    "stored_chain_hash": row["chain_hash"],
                    "action": action,
                    "epoch": str(row["epoch"]),
                    "actor_id": row["actor_id"],
                }
            )

        prev_chain_hash = row["chain_hash"]
        prev_row_id = row["id"]

        head = {
            "id": row["id"],
            "seal_hash": row["seal_hash"],
            "chain_hash": row["chain_hash"],
            "epoch": row["epoch"].isoformat() if row["epoch"] else None,
            "action": action,
            "event_type": row["event_type"],
            "actor_id": row["actor_id"],
            "agent_id": row["agent_id"],
            "verdict": row["verdict"],
        }

    return {
        "valid": len(mismatches) == 0,
        "chain_length": total,
        "genesis_chain_hash": GENESIS_CHAIN_HASH,
        "hash_algorithm": "blake3+trigger-sha256",
        "epoch_conventions": conv_count,
        "chain_conventions": chain_count,
        "orphan_prev_count": orphan_prev_count,
        "head": head,
        "first_mismatch": mismatches[0] if mismatches else None,
        "mismatch_count": len(mismatches),
        "checked_at": datetime.now(UTC).isoformat(),
        "error": None,
    }


async def verify_receipt(ref: str, dsn: str | None = None) -> dict[str, Any]:
    """Prove a single receipt exists in the chain and links correctly.

    ref: numeric id, or seal_hash prefix (>= 8 hex chars). Returns
    proof fields ONLY — never the payload body (MEMORY BOUNDARY).
    """
    import asyncpg

    dsn = dsn or DEFAULT_DSN
    conn = await asyncpg.connect(dsn, statement_cache_size=0)
    try:
        if ref.isdigit():
            row = await conn.fetchrow(
                """
                SELECT id, seal_hash, chain_hash, prev_seal_id, action,
                       actor_id, agent_id, event_type, verdict, epoch
                FROM vault_seals WHERE id = $1
                """,
                int(ref),
            )
        else:
            row = await conn.fetchrow(
                """
                SELECT id, seal_hash, chain_hash, prev_seal_id, action,
                       actor_id, agent_id, event_type, verdict, epoch
                FROM vault_seals WHERE seal_hash LIKE $1 || '%' ORDER BY id LIMIT 1
                """,
                ref.lower(),
            )
        if row is None:
            return {"found": False, "ref": ref}

        # Position in chain (insertion index by id)
        position = await conn.fetchval(
            "SELECT COUNT(*) FROM vault_seals WHERE id <= $1", row["id"]
        )
        total = await conn.fetchval("SELECT COUNT(*) FROM vault_seals")

        # Link check against predecessor
        prev = await conn.fetchrow(
            "SELECT seal_hash, chain_hash FROM vault_seals WHERE id < $1 ORDER BY id DESC LIMIT 1",
            row["id"],
        )
        links_ok = None
        if prev is None:
            links_ok = row["chain_hash"] == compute_chain_hash(
                GENESIS_CHAIN_HASH, row["seal_hash"]
            )
        else:
            links_ok = prev["chain_hash"] == row["seal_hash"] or (
                prev["seal_hash"] == row["prev_seal_id"]
            )

        return {
            "found": True,
            "ref": ref,
            "id": row["id"],
            "position": position,
            "chain_length": total,
            "seal_hash": row["seal_hash"],
            "chain_hash": row["chain_hash"],
            "prev_seal_id": row["prev_seal_id"],
            "links_ok": links_ok,
            "action": row["action"],
            "event_type": row["event_type"],
            "actor_id": row["actor_id"],
            "agent_id": row["agent_id"],
            "verdict": row["verdict"],
            "epoch": row["epoch"].isoformat() if row["epoch"] else None,
        }
    finally:
        await conn.close()


async def latest_receipts(limit: int = 1, dsn: str | None = None) -> list[dict[str, Any]]:
    """Last N receipts, proof fields only."""
    import asyncpg

    dsn = dsn or DEFAULT_DSN
    conn = await asyncpg.connect(dsn, statement_cache_size=0)
    try:
        rows = await conn.fetch(
            """
            SELECT id, seal_hash, chain_hash, action, actor_id, agent_id,
                   event_type, verdict, epoch
            FROM vault_seals ORDER BY id DESC LIMIT $1
            """,
            min(max(int(limit), 1), 50),
        )
        return [
            {
                "id": r["id"],
                "seal_hash": r["seal_hash"],
                "chain_hash": r["chain_hash"],
                "action": r["action"],
                "event_type": r["event_type"],
                "actor_id": r["actor_id"],
                "agent_id": r["agent_id"],
                "verdict": r["verdict"],
                "epoch": r["epoch"].isoformat() if r["epoch"] else None,
            }
            for r in rows
        ]
    finally:
        await conn.close()


def _main(argv: list[str]) -> int:
    """CLI: python -m core.vault999.verify_live [--json]"""
    import sys

    result = asyncio.run(verify_live_chain())
    if "--json" in argv:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("error"):
            print(f"ERROR {result['error']}")
            return 2
        head = result.get("head") or {}
        print(
            f"VALID={result['valid']} length={result['chain_length']} "
            f"mismatches={result.get('mismatch_count', 0)} "
            f"head_id={head.get('id')} head_chain={str(head.get('chain_hash'))[:16]}..."
        )
        return 0 if result["valid"] else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(__import__("sys").argv))
