"""
VAULT999 Unified Service
WELD-003: Merkle-chained vault ledger for arifOS federation
DITEMPA BUKAN DIBERI

Endpoints:
  POST /vault/seal              — Write a governed action to the ledger
  GET  /vault/session/{id}      — Get full chain for a session
  GET  /health                 — Service health check
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import asyncpg
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import VaultEntry, ChainedEntry, SessionChain


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://arifos_admin:password@postgres:5432/arifos_vault"
)

POOL: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global POOL
    if POOL is None:
        POOL = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
    return POOL


async def close_pool():
    global POOL
    if POOL:
        await POOL.close()
        POOL = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(
    title="VAULT999 — Unified Merkle Ledger",
    description="Constitutional seal ledger for arifOS federation. Append-only, Merkle-chained.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def compute_chain_hash(prev_hash: str, payload_hash: str) -> str:
    """Merkle chain link: SHA-256(prev_hash + payload_hash)."""
    return hashlib.sha256(f"{prev_hash}{payload_hash}".encode()).hexdigest()


def compute_payload_hash(data: dict) -> str:
    """SHA-256 of canonical JSON serialization."""
    import json
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


async def get_last_hash(pool: asyncpg.Pool) -> str:
    """Fetch the most recent chain_hash from the vault."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT chain_hash
            FROM arifosmcp_vault_seals
            ORDER BY id DESC
            LIMIT 1
            """
        )
    if row is None:
        return "GENESIS"
    return row["chain_hash"]


@app.post("/vault/seal", response_model=ChainedEntry)
async def seal(entry: VaultEntry):
    """
    Write a governed action to the unified ledger.

    NOT called on HOLD or VOID — ungoverned states do not enter the chain.
    Only PROCEED and SEAL verdicts are sealed.

    Chain invariant:
      entry_n.chain_hash = SHA-256(entry_(n-1).chain_hash + entry_n.payload_hash)
    """
    if entry.verdict not in ("PROCEED", "SEAL"):
        raise HTTPException(
            status_code=400,
            detail=f"Only PROCEED or SEAL may be sealed. Got: {entry.verdict}"
        )

    pool = await get_pool()

    prev_hash = await get_last_hash(pool)
    payload_for_hash = {
        "session_id": entry.session_id,
        "domain": entry.domain,
        "tool": entry.tool,
        "verdict": entry.verdict,
        "ac_risk": entry.ac_risk,
        "claim_tag": entry.claim_tag,
        "floor_violations": entry.floor_violations,
        "epistemic": entry.epistemic,
        "witness": {
            "human": entry.witness_human,
            "ai": entry.witness_ai,
            "earth": entry.witness_earth,
        },
    }
    payload_hash = compute_payload_hash(payload_for_hash)
    chain_hash = compute_chain_hash(prev_hash, payload_hash)
    seal_id = f"SEAL-{uuid.uuid4().hex[:12].upper()}"
    epoch = datetime.now(timezone.utc).isoformat()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO arifosmcp_vault_seals
              (seal_id, prev_hash, agent_id, action, payload, confidence, epoch,
               session_id, domain, tool, verdict, ac_risk, claim_tag,
               payload_hash, chain_hash, floor_violations, epistemic,
               witness_human, witness_ai, witness_earth)
            VALUES
              ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
            """,
            seal_id,
            prev_hash,
            f"{entry.domain}/{entry.witness_ai}",
            f"{entry.tool}:{entry.verdict}",
            json.dumps(payload_for_hash),
            1.0 - entry.ac_risk,
            epoch,
            entry.session_id,
            entry.domain,
            entry.tool,
            entry.verdict,
            entry.ac_risk,
            entry.claim_tag,
            compute_payload_hash(payload_for_hash),
            chain_hash,
            entry.floor_violations or [],
            entry.epistemic,
            entry.witness_human,
            entry.witness_ai,
            entry.witness_earth,
        )

    return ChainedEntry(
        session_id=entry.session_id,
        epoch=epoch,
        domain=entry.domain,
        tool=entry.tool,
        verdict=entry.verdict,
        ac_risk=entry.ac_risk,
        claim_tag=entry.claim_tag,
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        chain_hash=chain_hash,
        timestamp=datetime.now(timezone.utc),
        floor_violations=entry.floor_violations,
        seal_id=seal_id,
    )


@app.get("/vault/session/{session_id}", response_model=SessionChain)
async def get_session(session_id: str):
    """
    Return full chain for a session — GEOX entry + WEALTH entry linked.

    This is the cross-domain audit trace.
    """
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
              agent_id, action, payload, confidence, epoch, prev_hash, seal_id
            FROM arifosmcp_vault_seals
            WHERE session_id = $1
            ORDER BY id ASC
            """,
            session_id,
        )

    if not rows:
        raise HTTPException(status_code=404, detail=f"No chain found for session: {session_id}")

    entries = []
    prev_expected = None
    chain_integrity = True

    for row in rows:
        payload = json.loads(row["payload"])
        payload_hash = compute_payload_hash(payload)
        chain_hash = compute_chain_hash(row["prev_hash"], payload_hash)

        if prev_expected is not None and row["prev_hash"] != prev_expected:
            chain_integrity = False

        if chain_hash != compute_chain_hash(row["prev_hash"], payload_hash):
            chain_integrity = False

        prev_expected = chain_hash

        entries.append(ChainedEntry(
            session_id=session_id,
            epoch=row["epoch"],
            domain=payload.get("domain", "UNKNOWN"),
            tool=row["action"],
            verdict=payload.get("verdict", "UNKNOWN"),
            ac_risk=payload.get("ac_risk", 0.0),
            claim_tag=payload.get("claim_tag", "UNKNOWN"),
            payload_hash=payload_hash,
            prev_hash=row["prev_hash"],
            chain_hash=chain_hash,
            timestamp=row["epoch"],
            floor_violations=payload.get("floor_violations", []),
            seal_id=row["seal_id"],
        ))

    return SessionChain(
        session_id=session_id,
        entries=entries,
        chain_integrity=chain_integrity,
    )


@app.get("/health")
async def health():
    """Service health check."""
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "healthy", "vault": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "vault": "disconnected", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8100))
    uvicorn.run(app, host="0.0.0.0", port=port)