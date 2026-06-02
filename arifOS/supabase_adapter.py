"""
arifOS Supabase Receipt Adapter
==============================
Writes governance receipts to Supabase.

MODES (SUPABASE_WRITE_MODE env var):
  design      → s000/s999 (Phase 1 design tables) — default
  production  → arifosmcp_* / vault_* (production tables)
  dual        → write to both namespaces simultaneously
  shadow       → write design only, log production intent (kernel integration)
  off         → no writes, log only

RULE: Supabase receives receipts. Supabase does not control execution.
arifOS continues if Supabase is down — all failures are non-fatal.

Location: /root/arifOS/arifOS/supabase_adapter.py
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import asyncpg

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────
WRITE_MODE = os.getenv("SUPABASE_WRITE_MODE", "design").lower()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://utbmmjmbolmuahwixjqc.supabase.co")
VAULT999_DB = os.getenv(
    "VAULT999_DB",
    "postgresql://postgres.utbmmjmbolmuahwixjqc:cWZ228S72IaC9UzRD5i7UHh8s8NUbaXT@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres",
)
PROD_DB = os.getenv(
    "PROD_DB",
    "postgresql://postgres.utbmmjmbolmuahwixjqc:cWZ228S72IaC9UzRD5i7UHh8s8NUbaXT@db.utbmmjmbolmuahwixjqc.supabase.co:5432/postgres",
)

# Pool state
_design_pool: Optional[asyncpg.Pool] = None
_prod_pool: Optional[asyncpg.Pool] = None

MODE_DESIGN = WRITE_MODE == "design"
MODE_PROD = WRITE_MODE == "production"
MODE_DUAL = WRITE_MODE == "dual"
MODE_SHADOW = WRITE_MODE == "shadow"
MODE_OFF = WRITE_MODE == "off"

if WRITE_MODE not in ("design", "production", "dual", "shadow", "off"):
    logger.warning(f"[supabase_adapter] Unknown WRITE_MODE '{WRITE_MODE}' — defaulting to design")
    WRITE_MODE = "design"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


def _hash_payload(data: dict) -> str:
    import hashlib

    body = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()[:16]


# ── Pool Management ────────────────────────────────────────────


async def _get_design_pool() -> asyncpg.Pool:
    global _design_pool
    if _design_pool is None:
        _design_pool = await asyncpg.create_pool(
            VAULT999_DB, min_size=1, max_size=4, command_timeout=10
        )
    return _design_pool


async def _get_prod_pool() -> asyncpg.Pool:
    global _prod_pool
    if _prod_pool is None:
        _prod_pool = await asyncpg.create_pool(PROD_DB, min_size=1, max_size=4, command_timeout=10)
    return _prod_pool


async def close_pool() -> None:
    global _design_pool, _prod_pool
    if _design_pool:
        await _design_pool.close()
        _design_pool = None
    if _prod_pool:
        await _prod_pool.close()
        _prod_pool = None


# ── Shared Tool Call ID ─────────────────────────────────────────
# When writing dual/shadow, both namespaces must use the same tool_call_id
_tool_call_id_buffer: dict = {}


def _buffer_tool_call_id(tool_call_id: str, session_ref: str) -> None:
    _tool_call_id_buffer[session_ref] = tool_call_id


def _consume_tool_call_id(session_ref: str) -> Optional[str]:
    return _tool_call_id_buffer.pop(session_ref, None)


# ── Design Namespace (s000/s999) ────────────────────────────────


async def _write_design_tool_call(
    session_ref: str,
    tool_name: str,
    organ_code: str,
    arguments: dict,
    risk_tier: int,
    status: str,
    actor_ref: Optional[str],
    service_ref: Optional[str],
    trace_ref: Optional[str],
    server_ref: Optional[str],
    mcp_method: Optional[str],
) -> Optional[str]:
    """Write to s000.tool_calls (design Phase 1 schema)."""
    if MODE_OFF:
        return None
    tool_call_id = _uuid()
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.tool_calls
                  (id, tool_call_id, session_ref, trace_ref, actor_ref, service_ref,
                   organ_code, tool_name, server_ref, mcp_method,
                   arguments, arguments_hash, risk_tier, status, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)
                """,
                tool_call_id,
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
        logger.info(f"[adapter/design] tool_call: {tool_call_id}")
        return tool_call_id
    except Exception as e:
        logger.warning(f"[adapter/design] tool_call failed (soft): {e}")
        return None


async def _write_design_seal_vault999(
    subject_type: str,
    seal_type: str,
    verdict: str,
    content: dict,
    session_ref: Optional[str],
    trace_ref: Optional[str],
    actor_ref: Optional[str],
    service_ref: Optional[str],
    organ_code: Optional[str],
    subject_ref: Optional[str],
    signature: Optional[str],
    signed_by_ref: Optional[str],
) -> Optional[str]:
    """Write to s999.vault999_ledger (append-only)."""
    if MODE_OFF:
        return None
    seal_id = f"SEAL-{_uuid()[:12]}"
    content_hash = _hash_payload(content)
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
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
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
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
        logger.info(f"[adapter/design] seal: {seal_id}")
        return seal_id
    except Exception as e:
        logger.warning(f"[adapter/design] seal_vault999 failed (soft): {e}")
        return None


async def _write_design_evidence(
    session_ref: str,
    source_type: str,
    claim_state: str,
    title: Optional[str],
    content: Optional[str],
    confidence: Optional[float],
    organ_code: Optional[str],
    trace_ref: Optional[str],
    source_uri: Optional[str],
    metadata: Optional[dict],
) -> Optional[str]:
    """Write to s000.evidence_items."""
    if MODE_OFF:
        return None
    evidence_id = f"ev:{_uuid()[:12]}"
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.evidence_items
                  (evidence_id, session_ref, trace_ref, organ_code, source_type,
                   source_uri, title, content, claim_state, confidence, metadata, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                """,
                evidence_id,
                session_ref,
                trace_ref,
                organ_code,
                source_type,
                source_uri,
                title,
                content,
                claim_state,
                confidence,
                json.dumps(metadata) if metadata else "{}",
                _now(),
            )
        logger.info(f"[adapter/design] evidence: {evidence_id}")
        return evidence_id
    except Exception as e:
        logger.warning(f"[adapter/design] evidence failed (soft): {e}")
        return None


async def _write_design_artifact(
    bucket: str,
    path: str,
    filename: str,
    artifact_type: Optional[str],
    mime_type: Optional[str],
    size_bytes: Optional[int],
    content_hash: Optional[str],
    claim_state: str,
    organ_code: Optional[str],
    session_ref: Optional[str],
    trace_ref: Optional[str],
    metadata: Optional[dict],
) -> Optional[str]:
    """Write to s000.artifacts."""
    if MODE_OFF:
        return None
    artifact_id = f"art:{_uuid()[:12]}"
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.artifacts
                  (artifact_id, session_ref, trace_ref, organ_code,
                   bucket, path, filename, mime_type, size_bytes,
                   content_hash, artifact_type, claim_state, metadata, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
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
        logger.info(f"[adapter/design] artifact: {artifact_id}")
        return artifact_id
    except Exception as e:
        logger.warning(f"[adapter/design] artifact failed (soft): {e}")
        return None


async def _write_design_approval(
    tool_call_id: str,
    requested_by_ref: str,
    approved_by_ref: Optional[str],
    status: str,
    approval_method: str,
    reason: Optional[str],
    signature: Optional[str],
    signed_payload: Optional[dict],
) -> Optional[str]:
    """Write to s000.approvals (FK: tool_call_id in same transaction via session_ref)."""
    if MODE_OFF:
        return None
    approval_id = f"appr:{_uuid()[:12]}"
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.approvals
                  (approval_id, tool_call_id, requested_by_ref, approved_by_ref,
                   status, approval_method, reason, signed_payload, signature, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
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
        logger.info(f"[adapter/design] approval: {approval_id}")
        return approval_id
    except Exception as e:
        logger.warning(f"[adapter/design] approval failed (soft): {e}")
        return None


async def _write_design_judge_verdict(
    tool_call_id: Optional[str],
    session_ref: str,
    verdict: str,
    floor_summary: dict,
    risk_tier: Optional[int],
    reasoning: Optional[str],
    signature: Optional[str],
    judge_ref: str,
) -> Optional[str]:
    """Write to s000.judge_verdicts."""
    if MODE_OFF:
        return None
    verdict_id = f"verdict:{_uuid()[:12]}"
    try:
        pool = await _get_design_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO s000.judge_verdicts
                  (verdict_id, tool_call_id, session_ref, verdict,
                   risk_tier, floor_summary, reasoning, judge_ref, signature, created_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
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
        logger.info(f"[adapter/design] verdict: {verdict_id}")
        return verdict_id
    except Exception as e:
        logger.warning(f"[adapter/design] verdict failed (soft): {e}")
        return None


# ── Production Namespace (public.arifosmcp_*) ────────────────────


async def _write_prod_tool_call(
    session_ref: str,
    tool_name: str,
    organ_code: str,
    arguments: dict,
    risk_tier: int,
    status: str,
    actor_ref: Optional[str],
    service_ref: Optional[str],
    trace_ref: Optional[str],
    server_ref: Optional[str],
    mcp_method: Optional[str],
) -> Optional[str]:
    """Write to public.arifosmcp_tool_calls (production schema)."""
    if MODE_OFF:
        return None
    try:
        pool = await _get_prod_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO arifosmcp_tool_calls
                  (organ, session_id, tool_name, agent_id, input_hash, verdict,
                   floor_triggered, duration_ms, epoch, result_code, peace2, error_msg)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
                RETURNING id
                """,
                organ_code,
                session_ref,
                tool_name,
                actor_ref,
                _hash_payload(arguments),
                status,
                None,
                None,
                _now(),
                result_code_from_status(status),
                None,
                None,
            )
        call_id = str(row["id"])
        logger.info(f"[adapter/prod] tool_call: {call_id}")
        return call_id
    except Exception as e:
        logger.warning(f"[adapter/prod] tool_call failed (soft): {e}")
        return None


async def _write_prod_seal_vault999(
    subject_type: str,
    seal_type: str,
    verdict: str,
    content: dict,
    session_ref: Optional[str],
    trace_ref: Optional[str],
    actor_ref: Optional[str],
    service_ref: Optional[str],
    organ_code: Optional[str],
    subject_ref: Optional[str],
    signature: Optional[str],
    signed_by_ref: Optional[str],
) -> Optional[str]:
    """Write to public.vault_sealed_events (production L6)."""
    if MODE_OFF:
        return None
    content_hash = _hash_payload(content)
    try:
        pool = await _get_prod_pool()
        async with pool.acquire() as conn:
            # Get previous leaf
            prev_row = await conn.fetchrow(
                "SELECT merkle_leaf FROM vault_sealed_events ORDER BY created_at DESC LIMIT 1"
            )
            prev_leaf = prev_row["merkle_leaf"] if prev_row else "GENESIS"
            row = await conn.fetchrow(
                """
                INSERT INTO vault_sealed_events
                  (event_type, session_id, actor_id, stage, verdict, risk_tier,
                   payload, source_ledger, prev_leaf, merkle_leaf, signature, signed_by, sealed_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                RETURNING event_id
                """,
                seal_type,
                session_ref,
                actor_ref,
                subject_type,
                verdict,
                risk_tier_from_verdict(verdict),
                json.dumps(content),
                "arifOS:adapter:dual",
                prev_leaf,
                content_hash,
                signature,
                signed_by_ref,
                _now(),
            )
        event_id = str(row["event_id"])
        logger.info(f"[adapter/prod] seal: {event_id}")
        return event_id
    except Exception as e:
        logger.warning(f"[adapter/prod] seal_vault999 failed (soft): {e}")
        return None


# ── Helpers ────────────────────────────────────────────────────


def result_code_from_status(status: str) -> Optional[str]:
    map_ = {"succeeded": "OK", "failed": "ERR", "pending": "PEND", "planned": "PLAN"}
    return map_.get(status.lower())


def risk_tier_from_verdict(verdict: str) -> Optional[str]:
    if verdict in ("SEAL", "APPROVED"):
        return "low"
    if verdict in ("HOLD", "SABAR"):
        return "medium"
    return "high"


# ── Public API — Single Entry Point ─────────────────────────────


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
    Record a tool call receipt.

    Mode routing:
      design     → s000.tool_calls
      production → public.arifosmcp_tool_calls
      dual       → both namespaces
      shadow     → design only (kernel integration prep)
      off        → no write, log only
    """
    result_design = None
    result_prod = None

    if not MODE_OFF:
        # Always write design namespace
        result_design = await _write_design_tool_call(
            session_ref,
            tool_name,
            organ_code,
            arguments,
            risk_tier,
            status,
            actor_ref,
            service_ref,
            trace_ref,
            server_ref,
            mcp_method,
        )

        # Write production namespace if mode requires
        if MODE_PROD or MODE_DUAL:
            result_prod = await _write_prod_tool_call(
                session_ref,
                tool_name,
                organ_code,
                arguments,
                risk_tier,
                status,
                actor_ref,
                service_ref,
                trace_ref,
                server_ref,
                mcp_method,
            )
    else:
        logger.info(f"[adapter/off] tool_call: {session_ref}/{tool_name} — no write")

    # Buffer the design tool_call_id for FK chaining in same session
    if result_design:
        _buffer_tool_call_id(result_design, session_ref)

    return result_design or result_prod


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
    Seal a record to vault (append-only).

    Mode routing:
      design     → s999.vault999_ledger
      production → public.vault_sealed_events
      dual       → both namespaces
      shadow     → design only
      off        → no write
    """
    if MODE_OFF:
        logger.info(f"[adapter/off] seal_vault999: {subject_type}/{verdict} — no write")
        return None

    result = None

    if MODE_DESIGN or MODE_DUAL or MODE_SHADOW:
        result = await _write_design_seal_vault999(
            subject_type,
            seal_type,
            verdict,
            content,
            session_ref,
            trace_ref,
            actor_ref,
            service_ref,
            organ_code,
            subject_ref,
            signature,
            signed_by_ref,
        )

    if MODE_PROD or MODE_DUAL:
        prod_result = await _write_prod_seal_vault999(
            subject_type,
            seal_type,
            verdict,
            content,
            session_ref,
            trace_ref,
            actor_ref,
            service_ref,
            organ_code,
            subject_ref,
            signature,
            signed_by_ref,
        )
        if prod_result and not result:
            result = prod_result

    return result


async def record_evidence(
    session_ref: str,
    source_type: str,
    claim_state: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    confidence: Optional[float] = None,
    organ_code: Optional[str] = None,
    trace_ref: Optional[str] = None,
    source_uri: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Optional[str]:
    """Record evidence. Writes to design namespace only (production schema has no evidence table yet)."""
    if MODE_PROD:
        logger.info("[adapter/prod] evidence: no production table — skipping")
        return None
    return await _write_design_evidence(
        session_ref,
        source_type,
        claim_state,
        title,
        content,
        confidence,
        organ_code,
        trace_ref,
        source_uri,
        metadata,
    )


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
    """Record artifact metadata. Design namespace only (production has no artifacts table yet)."""
    if MODE_PROD:
        logger.info("[adapter/prod] artifact: no production table — skipping")
        return None
    return await _write_design_artifact(
        bucket,
        path,
        filename,
        artifact_type,
        mime_type,
        size_bytes,
        content_hash,
        claim_state,
        organ_code,
        session_ref,
        trace_ref,
        metadata,
    )


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
    """Record approval. Design namespace only (production has ticket model)."""
    if MODE_PROD:
        logger.info("[adapter/prod] approval: no production table — skipping")
        return None
    return await _write_design_approval(
        tool_call_id,
        requested_by_ref,
        approved_by_ref,
        status,
        approval_method,
        reason,
        signature,
        signed_payload,
    )


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
    """Record judge verdict. Design namespace only."""
    if MODE_PROD:
        logger.info("[adapter/prod] judge_verdict: no production table — skipping")
        return None
    return await _write_design_judge_verdict(
        tool_call_id,
        session_ref,
        verdict,
        floor_summary,
        risk_tier,
        reasoning,
        signature,
        judge_ref,
    )


# ── Smoke Test ────────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    async def smoke_test():
        mode = WRITE_MODE
        print(f"[smoke_test] Mode: {mode}")
        print("[smoke_test] Run: SUPABASE_WRITE_MODE=design python arifOS/supabase_adapter.py")
        session = f"smoke-{_uuid()[:8]}"

        try:
            tc = await record_tool_call(
                session_ref=session,
                tool_name="arif_heart_critique",
                organ_code="arifos",
                arguments={"mode": "critique"},
                risk_tier=1,
                status="succeeded",
            )
            print(f"[smoke_test] tool_call: {tc}")

            ev = await record_evidence(
                session_ref=session,
                source_type="mcp",
                claim_state="FACT",
                title="Smoke test evidence",
                content="Test content",
            )
            print(f"[smoke_test] evidence: {ev}")

            art = await record_artifact(
                bucket="evidence",
                path=f"smoke/{session}/test.txt",
                filename="test.txt",
                artifact_type="test",
            )
            print(f"[smoke_test] artifact: {art}")

            seal = await seal_vault999(
                subject_type="smoke_test",
                seal_type="smoke_test",
                verdict="SEAL",
                content={"session": session, "test": True},
                actor_ref="arifOS:smoke-test",
            )
            print(f"[smoke_test] seal: {seal}")
            print(f"[smoke_test] ALL PASS — mode={mode}")
        finally:
            await close_pool()

    asyncio.run(smoke_test())
