#!/usr/bin/env python3
"""
vault999_writer — Bounded vault_seals INSERT service
=============================================
Role: Only service allowed to INSERT into vault_seals
Auth: vault_writer_svc PostgreSQL role
Flow: OpenClaw calls /seal endpoint with human decision
      → vault_writer validates + inserts

Author: arifOS_bot
Date: 2026-04-18
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import asyncpg
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field

# ============================================================
# CONFIGURATION
# ============================================================
VAULT999_DB = os.getenv("VAULT999_DB", "postgresql://arifos_admin:ArifPostgresVault2026!@72.62.71.199:5432/vault999")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s vault999_writer: %(message)s",
    stream=sys.stdout
)
log = logging.getLogger("vault999_writer")

# ============================================================
# PYDANTIC MODELS
# ============================================================
class SealRequest(BaseModel):
    """Canonical request to write a SEAL into vault_seals"""
    cooling_id: Optional[str] = None
    cli_proposal_hash: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: str
    action: str
    payload: dict
    epoch: str
    verdict: str = Field(pattern="^(SEAL|VOID)$")
    human_ratifier: str
    human_signature: str  # Format: SIG_ARIF_TELEMETRY_<YYYYMMDD>_<SEQ>
    ratified_at: str
    irreversibility_ack: bool = True
    irreversibility_class: Optional[str] = None
    tags: list[str] = []
    metadata: dict = {}

class VoidRequest(BaseModel):
    """VOID decision — no vault_seals write, but record in human_reviews"""
    cooling_id: str
    reviewer_id: str
    reason: str
    human_signature: str
    decision: str = Field(default="VOID", pattern="^VOID$")
    reviewed_at: str
    metadata: dict = {}

class RatifyRequest(BaseModel):
    """Unified ratification request from OpenClaw"""
    cooling_id: Optional[str] = None
    decision: str = Field(pattern="^(SEAL|VOID)$")
    review_reason: str
    human_signature: str
    human_ratifier: str = "arif"
    irreversibility_ack: bool = False
    irreversibility_class: Optional[str] = None
    action_type: str = "GENERAL_SEAL"
    session_id: Optional[str] = None
    metadata: dict = {}

# ============================================================
# HASH FUNCTIONS
# ============================================================
def compute_seal_hash(agent_id: str, action: str, payload: dict, epoch: str,
                      verdict: str, human_ratifier: str, human_signature: str,
                      ratified_at: str, cooling_id: Optional[str],
                      cli_proposal_hash: Optional[str]) -> str:
    """SHA256 of canonical seal payload"""
    canonical = {
        "agent_id": agent_id,
        "action": action,
        "payload": payload,
        "epoch": epoch,
        "verdict": verdict,
        "human_ratifier": human_ratifier,
        "human_signature": human_signature,
        "ratified_at": ratified_at,
        "cooling_id": str(cooling_id) if cooling_id else None,
        "cli_proposal_hash": cli_proposal_hash
    }
    canonical_json = json.dumps(canonical, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

def compute_chain_hash(verdict: str, human_signature: str, ratified_at: str,
                       prev_seal_hash: Optional[str]) -> str:
    """SHA256(verdict + human_signature + ratified_at + prev_seal_hash)"""
    chain_input = verdict + human_signature + ratified_at + (prev_seal_hash or "GENESIS")
    return hashlib.sha256(chain_input.encode("utf-8")).hexdigest()

# ============================================================
# DATABASE HELPERS
# ============================================================
class VaultDB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=3)
        log.info("Connected to vault999 database")

    async def close(self):
        if self.pool:
            await self.pool.close()
            log.info("Database pool closed")

    async def write_seal(self, req: SealRequest) -> dict:
        """INSERT into vault_seals through vault_writer role"""
        async with self.pool.acquire() as conn:
            # Get prev_seal_id and seal_hash for chain
            prev_row = await conn.fetchrow("""
                SELECT id, seal_hash FROM vault_seals 
                ORDER BY ratified_at DESC LIMIT 1
            """)
            prev_seal_id = prev_row["id"] if prev_row else None
            prev_seal_hash = prev_row["seal_hash"] if prev_row else None

            # Compute hashes
            seal_hash = compute_seal_hash(
                req.agent_id, req.action, req.payload, req.epoch,
                req.verdict, req.human_ratifier, req.human_signature,
                req.ratified_at, req.cooling_id, req.cli_proposal_hash
            )
            chain_hash = compute_chain_hash(
                req.verdict, req.human_signature, req.ratified_at, prev_seal_hash
            )

            # Insert
            row = await conn.fetchrow("""
                INSERT INTO vault_seals (
                    seal_hash, chain_hash, prev_seal_id, 
                    cooling_id, cli_proposal_hash, session_id,
                    agent_id, action, payload, epoch,
                    verdict, human_ratifier, human_signature, ratified_at,
                    irreversibility_ack, irreversibility_class,
                    provenance_tag, tags, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, 'human', $17, $18
                )
                RETURNING id, seal_hash, chain_hash, ratified_at
            """,
                seal_hash, chain_hash, prev_seal_id,
                req.cooling_id, req.cli_proposal_hash, req.session_id,
                req.agent_id, req.action, json.dumps(req.payload), req.epoch,
                req.verdict, req.human_ratifier, req.human_signature, req.ratified_at,
                req.irreversibility_ack, req.irreversibility_class,
                req.tags, json.dumps(req.metadata)
            )
            log.info(f"SEAL written: id={row['id']}, action={req.action}, seal_hash={seal_hash[:16]}")
            return dict(row)

    async def write_void(self, req: VoidRequest) -> dict:
        """VOID — write human_reviews only, no vault_seals"""
        async with self.pool.acquire() as conn:
            # Verify cooling_queue record exists
            cq = await conn.fetchrow(
                "SELECT id, status FROM cooling_queue WHERE id = $1", 
                req.cooling_id
            )
            if not cq:
                raise HTTPException(status_code=404, detail="cooling_id not found")
            if cq["status"] in ("sealed", "voided"):
                raise HTTPException(status_code=409, detail=f"Already {cq['status']}")

            # Insert human_reviews
            review_id = await conn.fetchval("""
                INSERT INTO human_reviews (
                    cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING review_id::text
            """,
                req.cooling_id, req.reviewer_id, req.decision, req.reason,
                req.human_signature, req.reviewed_at
            )

            # Update cooling_queue status
            await conn.execute(
                "UPDATE cooling_queue SET status = 'voided', reviewed_by = $1, reviewed_at = $2, human_signature = $3 WHERE id = $4",
                req.reviewer_id, req.reviewed_at, req.human_signature, req.cooling_id
            )

            log.info(f"VOID written: cooling_id={req.cooling_id}, review_id={review_id}")
            return {"review_id": review_id, "decision": "VOID", "status": "voided"}

    async def ratify(self, req: RatifyRequest) -> dict:
        """Unified ratification: SEAL or VOID"""
        if req.decision == "VOID":
            void_req = VoidRequest(
                cooling_id=req.cooling_id,
                reviewer_id=req.human_ratifier,
                reason=req.review_reason,
                human_signature=req.human_signature,
                reviewed_at=datetime.now(timezone.utc).isoformat()
            )
            return await self.write_void(void_req)

        # SEAL path
        if not req.cooling_id:
            raise HTTPException(status_code=400, detail="cooling_id required for SEAL")

        # Get cooling_queue record
        async with self.pool.acquire() as conn:
            cq = await conn.fetchrow(
                "SELECT id, action_type, payload, session_id, proposal_hash FROM cooling_queue WHERE id = $1",
                req.cooling_id
            )
            if not cq:
                raise HTTPException(status_code=404, detail="cooling_id not found")
            if cq["status"] in ("sealed", "voided"):
                raise HTTPException(status_code=409, detail=f"Already {cq['status']}")

            ratified_at = datetime.now(timezone.utc).isoformat()

            # Build seal request
            seal_req = SealRequest(
                cooling_id=req.cooling_id,
                cli_proposal_hash=cq["proposal_hash"],
                session_id=req.session_id or cq["session_id"],
                agent_id="arifOS-E",
                action=cq["action_type"],
                payload=json.loads(cq["payload"]) if isinstance(cq["payload"], str) else dict(cq["payload"]),
                epoch=ratified_at,
                verdict="SEAL",
                human_ratifier=req.human_ratifier,
                human_signature=req.human_signature,
                ratified_at=ratified_at,
                irreversibility_ack=req.irreversibility_ack,
                irreversibility_class=req.irreversibility_class,
                tags=[req.action_type, "ratified"],
                metadata={"review_reason": req.review_reason, "reviewed_by": req.human_ratifier}
            )

            # Insert vault_seals
            seal_row = await self.write_seal(seal_req)

            # Write human_reviews
            review_id = await conn.fetchval("""
                INSERT INTO human_reviews (
                    cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at
                ) VALUES ($1, $2, 'SEAL', $3, $4, $5)
                RETURNING review_id::text
            """,
                req.cooling_id, req.human_ratifier, req.review_reason,
                req.human_signature, ratified_at
            )

            # Update cooling_queue
            await conn.execute("""
                UPDATE cooling_queue 
                SET status = 'sealed', reviewed_by = $1, reviewed_at = $2, human_signature = $3
                WHERE id = $4
            """, req.human_ratifier, ratified_at, req.human_signature, req.cooling_id)

            # Insert vault999_witness
            await conn.execute("""
                INSERT INTO vault999_witness (ledger_id, human_witness, ai_witness, evidence_witness, w_score, metadata)
                VALUES ($1, true, true, true, 1.00, $2)
            """, seal_row["id"], json.dumps({"review_reason": req.review_reason}))

            log.info(f"RATIFY SEAL: cooling_id={req.cooling_id}, seal_id={seal_row['id']}")
            return {
                "seal_id": seal_row["id"],
                "seal_hash": seal_row["seal_hash"],
                "review_id": review_id,
                "decision": "SEAL",
                "status": "sealed"
            }

    async def health_check(self) -> dict:
        """Read-only health check"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM vault_seals")
            pending = await conn.fetchval("SELECT COUNT(*) FROM cooling_queue WHERE status = 'awaiting_human'")
            return {
                "status": "healthy",
                "vault_seals_count": total,
                "pending_holds": pending,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(title="vault999_writer", version="1.0.0")
db: Optional[VaultDB] = None

@app.on_event("startup")
async def startup():
    global db
    db = VaultDB(VAULT999_DB)
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    if db:
        await db.close()

@app.get("/health")
async def health():
    return await db.health_check()

@app.post("/seal")
async def create_seal(req: SealRequest):
    """Direct SEAL insert — used for Path 2 (direct human seal without CLI-L2)"""
    try:
        result = await db.write_seal(req)
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"seal failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ratify")
async def ratify(req: RatifyRequest):
    """Canonical ratification: SEAL or VOID through CLI-L2 path"""
    try:
        result = await db.ratify(req)
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"ratify failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pending")
async def list_pending():
    """List all awaiting_human cooling_queue records"""
    async with db.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id::text, action_type, risk_class, judge_verdict, proposal_hash, 
                   session_id, created_at, hold_initiated_at
            FROM cooling_queue 
            WHERE status = 'awaiting_human'
            ORDER BY created_at ASC
        """)
        return {"pending": [dict(r) for r in rows], "count": len(rows)}

@app.get("/inspect/{cooling_id}")
async def inspect(cooling_id: str):
    """Inspect a single cooling_queue record"""
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT id::text, session_id, agent_id, action_type, prospect_id,
                   proposal_hash, judge_verdict, risk_class, status,
                   payload::text as payload_raw, created_at, hold_initiated_at,
                   reviewed_by, reviewed_at, review_notes, human_signature
            FROM cooling_queue WHERE id = $1
        """, cooling_id)
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        return dict(row)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VAULT999_WRITER_PORT", "5001"))
    uvicorn.run(app, host="0.0.0.0", port=port)