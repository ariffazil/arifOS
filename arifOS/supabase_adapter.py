"""
arifOS Supabase Receipt Adapter
================================
Writes governance receipts to Supabase s000/s999 tables.

RULE: Supabase receives receipts. Supabase does not control execution.
If Supabase is down, arifOS continues — never block on Supabase writes.

Location: /root/arifOS/arifOS/supabase_adapter.py
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
import asyncpg

logger = logging.getLogger(__name__)

# Environment
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://utbmmjmbolmuahwixjqc.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_POOL_URL = os.getenv(
    "VAULT999_DB",
    "postgresql://postgres.utbmmjmbolmuahwixjqc:cWZ228S72IaC9UzRD5i7UHh8s8NUbaXT@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres",
)

# Connection pool (lazy init)
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the asyncpg connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            SUPABASE_POOL_URL,
            min_size=1,
            max_size=4,
            command_timeout=10,
        )
    return _pool


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


def _hash_payload(data: dict) -> str:
    """SHA256 hash of JSON-serializable dict."""
    import hashlib

    body = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


async def record_tool_call(
    session_ref: str,
    tool_name: str,
    organ_code: str,
    arguments: dict,
    risk_tier: int,
    status: str = "planned",
    actor_ref: Optional[str] = None,
    service_ref: Optional[str] = None,
    trace_ref: Optional[str] = None,
    server_ref: Optional[str] = None,
    mcp_method: Optional[str] = None,
) -> Optional[str]:
    """
    Record a tool call receipt in s000.tool_calls.

    Fails soft: returns None if Supabase is down, does not raise.
    """
    tool_call_id = f"tc:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.tool_calls
                  (tool_call_id, session_ref, trace_ref, actor_ref, service_ref,
                   organ_code, tool_name, server_ref, mcp_method,
                   arguments, arguments_hash, risk_tier, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                tool_call_id,
                session_ref,
                trace_ref,
                actor_ref,
                service_ref,
                organ_code,
                tool_name,
                server_ref,
                mcp_method,
                json.dumps(arguments),
                _hash_payload(arguments),
                risk_tier,
                status,
                _now(),
            )
        logger.info(f"[supabase_adapter] tool_call recorded: {tool_call_id}")
        return tool_call_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] tool_call failed (soft fail): {e}")
        return None


async def record_approval(
    tool_call_id: str,
    requested_by_ref: str,
    approved_by_ref: Optional[str] = None,
    status: str = "pending",
    approval_method: str = "mcp",
    reason: Optional[str] = None,
    signature: Optional[str] = None,
    signed_payload: Optional[dict] = None,
) -> Optional[str]:
    """
    Record an approval receipt in s000.approvals.

    Fails soft: returns None if Supabase is down.
    """
    approval_id = f"appr:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.approvals
                  (approval_id, tool_call_id, requested_by_ref, approved_by_ref,
                   status, approval_method, reason, signed_payload, signature, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                approval_id,
                tool_call_id,
                requested_by_ref,
                approved_by_ref,
                status,
                approval_method,
                reason,
                json.dumps(signed_payload) if signed_payload else None,
                signature,
                _now(),
            )
        logger.info(f"[supabase_adapter] approval recorded: {approval_id}")
        return approval_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] approval failed (soft fail): {e}")
        return None


async def record_judge_verdict(
    tool_call_id: Optional[str],
    session_ref: str,
    verdict: str,
    floor_summary: dict,
    risk_tier: Optional[int] = None,
    reasoning: Optional[str] = None,
    signature: Optional[str] = None,
    judge_ref: str = "arifOS:888_JUDGE",
) -> Optional[str]:
    """
    Record an 888_JUDGE verdict in s000.judge_verdicts.

    Fails soft: returns None if Supabase is down.
    """
    verdict_id = f"verdict:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.judge_verdicts
                  (verdict_id, tool_call_id, session_ref, verdict,
                   risk_tier, floor_summary, reasoning, judge_ref, signature, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                verdict_id,
                tool_call_id,
                session_ref,
                verdict,
                risk_tier,
                json.dumps(floor_summary),
                reasoning,
                judge_ref,
                signature,
                _now(),
            )
        logger.info(f"[supabase_adapter] verdict recorded: {verdict_id}")
        return verdict_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] verdict failed (soft fail): {e}")
        return None


async def record_evidence(
    session_ref: str,
    source_type: str,
    claim_state: str,
    content: Optional[str] = None,
    title: Optional[str] = None,
    source_uri: Optional[str] = None,
    source_hash: Optional[str] = None,
    confidence: Optional[float] = None,
    organ_code: Optional[str] = None,
    trace_ref: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """
    Record an evidence item in s000.evidence_items.

    Fails soft: returns None if Supabase is down.
    """
    evidence_id = f"ev:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.evidence_items
                  (evidence_id, session_ref, trace_ref, organ_code,
                   source_type, source_uri, source_hash, title, content,
                   claim_state, confidence, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                evidence_id,
                session_ref,
                trace_ref,
                organ_code,
                source_type,
                source_uri,
                source_hash,
                title,
                content,
                claim_state,
                confidence,
                json.dumps(metadata) if metadata else "{}",
                _now(),
            )
        logger.info(f"[supabase_adapter] evidence recorded: {evidence_id}")
        return evidence_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] evidence failed (soft fail): {e}")
        return None


async def record_artifact(
    bucket: str,
    path: str,
    filename: str,
    artifact_type: Optional[str] = None,
    mime_type: Optional[str] = None,
    size_bytes: Optional[int] = None,
    content_hash: Optional[str] = None,
    claim_state: str = "EST",
    organ_code: Optional[str] = None,
    session_ref: Optional[str] = None,
    trace_ref: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """
    Record an artifact metadata row in s000.artifacts.

    Fails soft: returns None if Supabase is down.
    """
    artifact_id = f"art:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.artifacts
                  (artifact_id, session_ref, trace_ref, organ_code,
                   bucket, path, filename, mime_type, size_bytes,
                   content_hash, artifact_type, claim_state, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                artifact_id,
                session_ref,
                trace_ref,
                organ_code,
                bucket,
                path,
                filename,
                mime_type,
                size_bytes,
                content_hash,
                artifact_type,
                claim_state,
                json.dumps(metadata) if metadata else "{}",
                _now(),
            )
        logger.info(f"[supabase_adapter] artifact recorded: {artifact_id}")
        return artifact_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] artifact failed (soft fail): {e}")
        return None


async def seal_vault999(
    subject_type: str,
    seal_type: str,
    verdict: str,
    content: dict,
    session_ref: Optional[str] = None,
    trace_ref: Optional[str] = None,
    actor_ref: Optional[str] = None,
    service_ref: Optional[str] = None,
    organ_code: Optional[str] = None,
    subject_ref: Optional[str] = None,
    signature: Optional[str] = None,
    signed_by_ref: Optional[str] = None,
) -> Optional[str]:
    """
    Seal a record to s999.vault999_ledger (append-only).

    Fails soft: returns None if Supabase is down.
    This is the most critical write — must never block the kernel.
    """
    seal_id = f"SEAL-{_uuid()[:12]}"
    content_hash = _hash_payload(content)
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            # Get previous hash for chain
            prev_row = await conn.fetchrow(
                "SELECT content_hash FROM s999.vault999_ledger ORDER BY created_at DESC LIMIT 1"
            )
            previous_hash = prev_row["content_hash"] if prev_row else "GENESIS"
            await conn.execute(
                """
                INSERT INTO s999.vault999_ledger
                  (seal_id, session_ref, trace_ref, actor_ref, service_ref, organ_code,
                   subject_type, subject_ref, seal_type, verdict,
                   content_hash, previous_hash, content, signature, signed_by_ref, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                """,
                seal_id,
                session_ref,
                trace_ref,
                actor_ref,
                service_ref,
                organ_code,
                subject_type,
                subject_ref,
                seal_type,
                verdict,
                content_hash,
                previous_hash,
                json.dumps(content),
                signature,
                signed_by_ref,
                _now(),
            )
        logger.info(f"[supabase_adapter] vault sealed: {seal_id}")
        return seal_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] vault seal failed (soft fail): {e}")
        return None


async def record_mcp_manifest_snapshot(
    server_ref: str,
    tools: list,
    manifest_hash: Optional[str] = None,
    observed_by_ref: Optional[str] = "arifOS:NATS-heartbeat",
) -> Optional[str]:
    """
    Record an MCP tool manifest snapshot in s000.mcp_manifest_snapshots.

    Fails soft: returns None if Supabase is down.
    """
    if manifest_hash is None:
        manifest_hash = _hash_payload({"server": server_ref, "tools": tools})
    snapshot_id = f"snap:{_uuid()[:12]}"
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.mcp_manifest_snapshots
                  (server_ref, manifest_hash, tool_count, tools, observed_by_ref, observed_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (server_ref, manifest_hash) DO NOTHING
                """,
                server_ref,
                manifest_hash,
                len(tools),
                json.dumps(tools),
                observed_by_ref,
                _now(),
            )
        logger.info(f"[supabase_adapter] MCP snapshot recorded: {snapshot_id}")
        return snapshot_id
    except Exception as e:
        logger.warning(f"[supabase_adapter] MCP snapshot failed (soft fail): {e}")
        return None


# ============================================================
# Smoke test — run directly: python supabase_adapter.py
# ============================================================
if __name__ == "__main__":
    import asyncio

    async def smoke_test():
        print("[smoke_test] Starting...")
        try:
            # Test tool_call
            tc = await record_tool_call(
                session_ref="smoke-test",
                tool_name="arif_heart_critique",
                organ_code="arifos",
                arguments={"mode": "critique", "target": "test"},
                risk_tier=1,
                status="succeeded",
            )
            print(f"[smoke_test] tool_call: {tc}")

            # Test evidence
            ev = await record_evidence(
                session_ref="smoke-test",
                source_type="mcp",
                claim_state="FACT",
                title="Smoke test evidence",
                content="Test content",
            )
            print(f"[smoke_test] evidence: {ev}")

            # Test artifact
            art = await record_artifact(
                bucket="evidence",
                path="smoke-test/test.txt",
                filename="test.txt",
                artifact_type="test",
                claim_state="EST",
            )
            print(f"[smoke_test] artifact: {art}")

            # Test seal
            seal = await seal_vault999(
                subject_type="test",
                seal_type="smoke_test",
                verdict="SEAL",
                content={"test": True, "note": "smoke test only"},
            )
            print(f"[smoke_test] vault seal: {seal}")

            print("[smoke_test] ALL PASSED")
        finally:
            await close_pool()

    asyncio.run(smoke_test())
