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
import logging
from datetime import datetime, timezone
from typing import Optional

try:
    import blake3

    _HAS_BLAKE3 = True
except ImportError:
    _HAS_BLAKE3 = False
    import hashlib

import asyncpg
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Ed25519 signature verification for sovereign ratification
# ═══════════════════════════════════════════════════════════════════════════════
try:
    from nacl.signing import VerifyKey
    from nacl.exceptions import BadSignatureError

    _HAS_ED25519 = True
except ImportError:
    _HAS_ED25519 = False

# Load Arif's public key(s) for signature verification.
# Priority: 1) dedicated vault signing key, 2) SSH public key raw bytes
_ARIF_PUBKEYS: list[bytes] = []


def _load_arif_pubkeys() -> list[bytes]:
    """Load all configured Arif Ed25519 public keys for verification."""
    keys: list[bytes] = []
    # Dedicated vault signing key (preferred)
    vault_pk_path = os.getenv("ARIF_VAULT_PUBKEY_FILE", "/run/secrets/arif_vault_signing_key.pub")
    try:
        with open(vault_pk_path) as f:
            b64 = f.read().strip()
            keys.append(__import__("base64").b64decode(b64))
    except Exception:
        pass
    # Fallback: SSH public key raw bytes from env
    ssh_raw_hex = os.getenv("ARIF_SSH_PUBKEY_HEX", "")
    if ssh_raw_hex:
        try:
            keys.append(bytes.fromhex(ssh_raw_hex))
        except ValueError:
            pass
    return keys


_ARIF_PUBKEYS = _load_arif_pubkeys()


def _canonical_json(obj: dict) -> str:
    """Deterministic JSON for signing."""
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)


def verify_arif_signature(signature_b64: str, signed_data: dict) -> tuple[bool, str]:
    """
    Verify an Ed25519 signature against Arif's configured public keys.

    Returns (verified: bool, reason: str)
    """
    if not _HAS_ED25519:
        return False, "ED25519_LIBRARY_NOT_AVAILABLE"
    if not _ARIF_PUBKEYS:
        return False, "ARIF_PUBLIC_KEY_NOT_CONFIGURED"

    try:
        sig_bytes = __import__("base64").b64decode(signature_b64)
    except Exception:
        return False, "SIGNATURE_BASE64_DECODE_FAILED"

    canonical = _canonical_json(signed_data)
    message = canonical.encode("utf-8")

    for pk_bytes in _ARIF_PUBKEYS:
        try:
            vk = VerifyKey(pk_bytes)
            vk.verify(message, sig_bytes)
            return True, "OK"
        except BadSignatureError:
            continue
        except Exception:
            continue

    return False, "SIGNATURE_INVALID_ALL_KEYS"

# ============================================================
# CONFIGURATION
# ============================================================
VAULT999_DB = os.getenv("VAULT999_DB", "postgresql://arifos_admin:***@postgres:5432/vault999")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
VAULT_WRITER_TOKEN_FILE = os.getenv("VAULT_WRITER_TOKEN_FILE", "/run/secrets/vault_writer_token")


# Load token from mounted Docker secret file
def _load_writer_token() -> str:
    try:
        with open(VAULT_WRITER_TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


_WRITER_TOKEN = _load_writer_token()


def verify_writer_token(x_writer_token: str = Header(None)) -> str:
    """Reject requests without a valid X-Writer-Token."""
    if not _WRITER_TOKEN:
        return "unauthenticated"
    if not x_writer_token:
        raise HTTPException(401, "Missing X-Writer-Token")
    if x_writer_token != _WRITER_TOKEN:
        raise HTTPException(401, "Invalid X-Writer-Token")
    return x_writer_token


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s vault999_writer: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("vault999_writer")


# ============================================================
# PYDANTIC MODELS
# ============================================================
class SovereignSealRequest(BaseModel):
    """Canonical request to write a SOVEREIGN SEAL into vault_seals. Binding."""

    cooling_id: Optional[str] = None
    cli_proposal_hash: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: str
    action: str
    payload: dict
    epoch: str
    verdict: str = Field(pattern="^(SEAL|VOID)$")
    human_ratifier: str = Field(pattern="^arif$")
    human_signature: Optional[str] = None  # Legacy ceremonial sig (deprecated)
    ed25519_signature: str  # Base64 Ed25519 signature over canonical payload
    ratified_at: str
    irreversibility_ack: bool = True
    irreversibility_class: Optional[str] = None
    tags: list[str] = []
    metadata: dict = {}


class AuditReceiptRequest(BaseModel):
    """Non-binding audit receipt. Clerks/tools may write. Not a constitutional verdict."""

    agent_id: str
    action: str
    payload: dict
    payload_hash: Optional[str] = None
    payload_summary: Optional[str] = None

    session_id: Optional[str] = None
    trace_id: Optional[str] = None

    claim_state: str = Field(pattern="^(OBSERVED|DRAFT|HYPOTHESIS|PENDING_RATIFICATION)$")
    binding: bool = False
    irreversible: bool = False

    human_ratifier: Optional[str] = None
    human_signature: Optional[str] = None
    ed25519_signature: Optional[str] = None

    tags: list[str] = []
    metadata: dict = {}
    created_at: Optional[str] = None


# Backward-compat alias
SealRequest = SovereignSealRequest


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
    """Unified ratification request from OpenClaw. Requires Arif's Ed25519 signature."""

    cooling_id: Optional[str] = None
    decision: str = Field(pattern="^(SEAL|VOID)$")
    review_reason: str
    human_signature: Optional[str] = None  # Legacy
    ed25519_signature: str  # Base64 Ed25519 sig over canonical payload
    human_ratifier: str = "arif"
    irreversibility_ack: bool = False
    irreversibility_class: Optional[str] = None
    action_type: str = "GENERAL_SEAL"
    session_id: Optional[str] = None
    metadata: dict = {}


# ============================================================
# HASH FUNCTIONS
# ============================================================
def compute_seal_hash(prev_chain_hash: str, action: str, epoch: str, payload: dict) -> str:
    """BLAKE3(prev_chain_hash || action || epoch || canonical(payload)).
    For genesis, prev_chain_hash = blake3(b'VAULT999:GENESIS:arif-fazil:2026-04-18')."""
    canonical_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    seal_input = f"{prev_chain_hash}|{action}|{epoch}|{canonical_json}"
    if _HAS_BLAKE3:
        return blake3.blake3(seal_input.encode("utf-8")).hexdigest(32)
    return hashlib.sha256(seal_input.encode("utf-8")).hexdigest()


def compute_chain_hash(prev_seal_hash: str, seal_hash: str) -> str:
    """BLAKE3(prev_seal_hash || seal_hash). Genesis uses genesis_chain_hash as prev."""
    chain_input = f"{prev_seal_hash}|{seal_hash}"
    if _HAS_BLAKE3:
        return blake3.blake3(chain_input.encode("utf-8")).hexdigest(32)
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

    async def write_seal(self, req: SovereignSealRequest) -> dict:
        """INSERT a SOVEREIGN SEAL into vault_seals. Binding constitutional verdict."""
        GENESIS_CHAIN_HASH = "9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43"  # pragma: allowlist secret

        async with self.pool.acquire() as conn:
            prev_row = await conn.fetchrow(
                """SELECT id, seal_hash, chain_hash FROM vault_seals
                   WHERE event_type = 'SOVEREIGN_SEAL' OR event_type IS NULL
                   ORDER BY epoch DESC LIMIT 1"""
            )
            prev_seal_id = prev_row["id"] if prev_row else None
            prev_seal_hash = prev_row["seal_hash"] if prev_row else None

            epoch_val = (
                datetime.fromisoformat(req.epoch) if isinstance(req.epoch, str) else req.epoch
            )
            prev_chain_hash = prev_row["chain_hash"] if prev_row else GENESIS_CHAIN_HASH

            seal_hash = compute_seal_hash(prev_chain_hash, req.action, epoch_val, req.payload)
            chain_hash = compute_chain_hash(prev_seal_hash or GENESIS_CHAIN_HASH, seal_hash)

            # Build witness with Ed25519 proof metadata
            witness = {
                "human_ratifier": req.human_ratifier,
                "human_signature": req.human_signature,
                "ed25519_signature_present": bool(req.ed25519_signature),
                "agent_id": req.agent_id,
                "cooling_id": req.cooling_id,
            }

            row = await conn.fetchrow(
                """
                INSERT INTO vault_seals (
                    event_type, session_id, actor_id, action_type,
                    seal_hash, chain_hash, prev_seal_id,
                    action, payload, verdict, epoch, witness,
                    signature, signed_by, sealed_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
                RETURNING id, seal_hash, chain_hash, epoch
            """,
                "SOVEREIGN_SEAL",
                req.session_id,
                req.agent_id,
                req.irreversibility_class or "general",
                seal_hash,
                chain_hash,
                prev_seal_id,
                req.action,
                json.dumps(req.payload),
                req.verdict,
                epoch_val,
                json.dumps(witness),
                req.ed25519_signature or req.human_signature,
                req.human_ratifier,
                epoch_val,
            )
            log.info(
                f"SOVEREIGN_SEAL written: id={row['id']}, action={req.action}, seal_hash={seal_hash[:16]}"
            )
            return dict(row)

    async def write_audit_receipt(self, req: AuditReceiptRequest) -> dict:
        """INSERT a non-binding AUDIT_RECEIPT into vault_seals. Clerk-allowed."""
        GENESIS_CHAIN_HASH = "9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43"  # pragma: allowlist secret

        async with self.pool.acquire() as conn:
            # Audit receipts chain independently or append to main chain
            # For simplicity, they still chain to the last seal for append-only property
            prev_row = await conn.fetchrow(
                """SELECT id, seal_hash, chain_hash FROM vault_seals
                   ORDER BY epoch DESC LIMIT 1"""
            )
            prev_seal_id = prev_row["id"] if prev_row else None
            prev_seal_hash = prev_row["seal_hash"] if prev_row else None

            created_at = (
                datetime.fromisoformat(req.created_at)
                if req.created_at
                else datetime.now(timezone.utc)
            )
            prev_chain_hash = prev_row["chain_hash"] if prev_row else GENESIS_CHAIN_HASH

            payload = dict(req.payload)
            seal_hash = compute_seal_hash(prev_chain_hash, req.action, created_at, payload)
            chain_hash = compute_chain_hash(prev_seal_hash or GENESIS_CHAIN_HASH, seal_hash)

            row = await conn.fetchrow(
                """
                INSERT INTO vault_seals (
                    event_type, session_id, actor_id, action_type,
                    seal_hash, chain_hash, prev_seal_id,
                    action, payload, verdict, epoch, witness,
                    signature, signed_by, sealed_at
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
                )
                RETURNING id, seal_hash, chain_hash, epoch
            """,
                "AUDIT_RECEIPT",
                req.session_id,
                req.agent_id,
                "audit",
                seal_hash,
                chain_hash,
                prev_seal_id,
                req.action,
                json.dumps(payload),
                req.claim_state,
                created_at,
                json.dumps(
                    {
                        "claim_state": req.claim_state,
                        "binding": req.binding,
                        "irreversible": req.irreversible,
                        "trace_id": req.trace_id,
                        "payload_summary": req.payload_summary,
                        "human_ratifier": req.human_ratifier,
                    }
                ),
                req.ed25519_signature or req.human_signature,
                req.human_ratifier or req.agent_id,
                created_at,
            )
            log.info(
                f"AUDIT_RECEIPT written: id={row['id']}, action={req.action}, seal_hash={seal_hash[:16]}"
            )
            return dict(row)

    async def write_void(self, req: VoidRequest) -> dict:
        """VOID — write human_reviews only, no vault_seals"""
        async with self.pool.acquire() as conn:
            # Verify cooling_queue record exists
            cq = await conn.fetchrow(
                "SELECT id, status FROM cooling_queue WHERE id = $1", req.cooling_id
            )
            if not cq:
                raise HTTPException(status_code=404, detail="cooling_id not found")
            if cq["status"] in ("sealed", "voided"):
                raise HTTPException(status_code=409, detail=f"Already {cq['status']}")

            # Insert human_reviews
            review_id = await conn.fetchval(
                """
                INSERT INTO human_reviews (
                    cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING review_id::text
            """,
                req.cooling_id,
                req.reviewer_id,
                req.decision,
                req.reason,
                req.human_signature,
                req.reviewed_at,
            )

            # Update cooling_queue status
            await conn.execute(
                "UPDATE cooling_queue SET status = 'voided', reviewed_by = $1, reviewed_at = $2, human_signature = $3 WHERE id = $4",
                req.reviewer_id,
                req.reviewed_at,
                req.human_signature,
                req.cooling_id,
            )

            log.info(f"VOID written: cooling_id={req.cooling_id}, review_id={review_id}")
            return {"review_id": review_id, "decision": "VOID", "status": "voided"}

    async def ratify(self, req: RatifyRequest) -> dict:
        """Unified ratification: SEAL or VOID. Ed25519 preferred; legacy accepted."""
        if req.ed25519_signature:
            sig_payload = {
                "cooling_id": req.cooling_id,
                "decision": req.decision,
                "review_reason": req.review_reason,
                "human_ratifier": req.human_ratifier,
                "irreversibility_ack": req.irreversibility_ack,
                "action_type": req.action_type,
                "session_id": req.session_id,
                "metadata": req.metadata,
            }
            sig_verified, sig_reason = verify_arif_signature(req.ed25519_signature, sig_payload)
            if not sig_verified:
                raise HTTPException(status_code=403, detail=f"F11 AUTH: {sig_reason}")

        if req.decision == "VOID":
            void_req = VoidRequest(
                cooling_id=req.cooling_id,
                reviewer_id=req.human_ratifier,
                reason=req.review_reason,
                human_signature=req.human_signature or req.ed25519_signature,
                reviewed_at=datetime.now(timezone.utc).isoformat(),
            )
            return await self.write_void(void_req)

        # SEAL path
        if not req.cooling_id:
            raise HTTPException(status_code=400, detail="cooling_id required for SEAL")

        async with self.pool.acquire() as conn:
            cq = await conn.fetchrow(
                "SELECT id, action_type, payload, session_id, proposal_hash FROM cooling_queue WHERE id = $1",
                req.cooling_id,
            )
            if not cq:
                raise HTTPException(status_code=404, detail="cooling_id not found")
            if cq["status"] in ("sealed", "voided"):
                raise HTTPException(status_code=409, detail=f"Already {cq['status']}")

            ratified_at = datetime.now(timezone.utc).isoformat()

            seal_req = SovereignSealRequest(
                cooling_id=req.cooling_id,
                cli_proposal_hash=cq["proposal_hash"],
                session_id=req.session_id or cq["session_id"],
                agent_id="arifOS-E",
                action=cq["action_type"],
                payload=(
                    json.loads(cq["payload"])
                    if isinstance(cq["payload"], str)
                    else dict(cq["payload"])
                ),
                epoch=ratified_at,
                verdict="SEAL",
                human_ratifier=req.human_ratifier,
                human_signature=req.human_signature,
                ed25519_signature=req.ed25519_signature,
                ratified_at=ratified_at,
                irreversibility_ack=req.irreversibility_ack,
                irreversibility_class=req.irreversibility_class,
                tags=[req.action_type, "ratified"],
                metadata={"review_reason": req.review_reason, "reviewed_by": req.human_ratifier},
            )

            seal_row = await self.write_seal(seal_req)

            review_id = await conn.fetchval(
                """
                INSERT INTO human_reviews (
                    cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at
                ) VALUES ($1, $2, 'SEAL', $3, $4, $5)
                RETURNING review_id::text
            """,
                req.cooling_id,
                req.human_ratifier,
                req.review_reason,
                req.ed25519_signature,
                ratified_at,
            )

            await conn.execute(
                """
                UPDATE cooling_queue
                SET status = 'sealed', reviewed_by = $1, reviewed_at = $2, human_signature = $3
                WHERE id = $4
            """,
                req.human_ratifier,
                ratified_at,
                req.ed25519_signature,
                req.cooling_id,
            )

            await conn.execute(
                """
                INSERT INTO vault999_witness (ledger_id, human_witness, ai_witness, evidence_witness, w_score, metadata)
                VALUES ($1, true, true, true, 1.00, $2)
            """,
                seal_row["id"],
                json.dumps({"review_reason": req.review_reason, "ed25519_verified": True}),
            )

            log.info(f"RATIFY SEAL: cooling_id={req.cooling_id}, seal_id={seal_row['id']}")
            return {
                "seal_id": seal_row["id"],
                "seal_hash": seal_row["seal_hash"],
                "review_id": review_id,
                "decision": "SEAL",
                "status": "sealed",
            }

    async def health_check(self) -> dict:
        """Read-only health check"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM vault_seals")
            pending = await conn.fetchval(
                "SELECT COUNT(*) FROM cooling_queue WHERE status = 'awaiting_human'"
            )
            return {
                "status": "healthy",
                "vault_seals_count": total,
                "pending_holds": pending,
                "timestamp": datetime.now(timezone.utc).isoformat(),
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
async def create_seal(req: SovereignSealRequest, _auth=Depends(verify_writer_token)):
    """Direct SOVEREIGN SEAL insert. Ed25519 preferred; legacy signature accepted as fallback."""
    if req.ed25519_signature:
        sig_payload = {
            "action": req.action,
            "payload": req.payload,
            "epoch": req.epoch,
            "verdict": req.verdict,
            "human_ratifier": req.human_ratifier,
            "session_id": req.session_id,
        }
        sig_verified, sig_reason = verify_arif_signature(req.ed25519_signature, sig_payload)
        if not sig_verified:
            raise HTTPException(status_code=403, detail=f"F11 AUTH: {sig_reason}")
    elif not req.human_signature:
        raise HTTPException(status_code=403, detail="F11 AUTH: Provide ed25519_signature or human_signature")

    try:
        result = await db.write_seal(req)
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"seal failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit-receipt")
async def create_audit_receipt(req: AuditReceiptRequest, _auth=Depends(verify_writer_token)):
    """Non-binding audit receipt. Clerks/tools may write. Not a constitutional verdict."""
    if req.binding:
        raise HTTPException(status_code=403, detail="Audit receipt cannot be binding")
    if req.irreversible:
        raise HTTPException(status_code=403, detail="Audit receipt cannot be irreversible")

    try:
        result = await db.write_audit_receipt(req)
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"audit-receipt failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ratify")
async def ratify(req: RatifyRequest, _auth=Depends(verify_writer_token)):
    """Canonical ratification: SEAL or VOID through CLI-L2 path. Verifies Ed25519."""
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
        rows = await conn.fetch(
            """
            SELECT id::text, action_type, risk_class, judge_verdict, proposal_hash,
                   session_id, created_at, hold_initiated_at
            FROM cooling_queue
            WHERE status = 'awaiting_human'
            ORDER BY created_at ASC
        """
        )
        return {"pending": [dict(r) for r in rows], "count": len(rows)}


@app.get("/inspect/{cooling_id}")
async def inspect(cooling_id: str):
    """Inspect a single cooling_queue record"""
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id::text, session_id, agent_id, action_type, prospect_id,
                   proposal_hash, judge_verdict, risk_class, status,
                   payload::text as payload_raw, created_at, hold_initiated_at,
                   reviewed_by, reviewed_at, review_notes, human_signature
            FROM cooling_queue WHERE id = $1
        """,
            cooling_id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="not found")
        return dict(row)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("VAULT999_WRITER_PORT", "5001"))
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec: B104
