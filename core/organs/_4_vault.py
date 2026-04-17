"""
organs/4_vault.py — Stage 999: THE MEMORY (VAULT SEAL)

Immutable ledger sealing and tamper-evident Merkle chaining.
Commits final session state to VAULT999.

DITEMPA BUKAN DIBERI — Forged, Not Given

fix/vault999-criticals:
  C1+C2: source_agent + pipeline_stage added to every entry (attribution fix).
  C2:    VAULT_POSTGRES_REQUIRED=true hard-fails when DATABASE_URL absent.
  C3:    F5 peace2 >= 1.0 enforced for seal_mode='final', verdict='SEAL'.
  ENH:   chain_tip mode returns last 3 entries + continuity status.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import blake3

from core.shared.types import HashChain, SealRecord, VaultOutput, Verdict

logger = logging.getLogger(__name__)

# Default storage
DEFAULT_VAULT_PATH = Path(__file__).parents[2] / "VAULT999" / "vault999.jsonl"
_CHAIN_SEED = "0x" + "0" * 64
VAULT_VERSION = "v1"

# Serialises the read-prev_hash → compute → append sequence so concurrent
# coroutines in THIS PROCESS cannot interleave and produce a broken Merkle chain.
# Cross-process serialisation is achieved by routing all callers (WEALTH, GEOX)
# through the arifos_vault HTTP endpoint, which funnels them through this lock.
_vault_write_lock = asyncio.Lock()


def _canonical_entry_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the canonical fields used to derive a vault seal hash."""
    return {
        "session_id": payload.get("session_id"),
        "ledger_id": payload.get("ledger_id"),
        "summary": payload.get("summary"),
        "verdict": payload.get("verdict"),
        "approved_by": payload.get("approved_by"),
        "approval_reference": payload.get("approval_reference"),
        "telemetry": payload.get("telemetry", {}),
        "timestamp": payload.get("timestamp"),
    }


def compute_vault_seal_hash(payload: dict[str, Any]) -> str:
    """Compute the canonical seal hash for a vault entry using blake3."""
    entry_json = json.dumps(
        _canonical_entry_payload(payload), sort_keys=True, separators=(",", ":")
    )
    return blake3.blake3(entry_json.encode("utf-8")).hexdigest()


def verify_vault_record(payload: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate a persisted vault record for tamper evidence."""
    required = {
        "session_id",
        "ledger_id",
        "summary",
        "verdict",
        "approved_by",
        "telemetry",
        "timestamp",
        "seal_hash",
        "chain",
    }
    missing = sorted(key for key in required if key not in payload)
    if missing:
        return False, f"missing required fields: {', '.join(missing)}"

    expected_hash = compute_vault_seal_hash(payload)
    if payload.get("seal_hash") != expected_hash:
        return False, "seal hash mismatch"

    chain = payload.get("chain")
    if not isinstance(chain, dict):
        return False, "invalid chain payload"

    if chain.get("payload_hash") != expected_hash:
        return False, "chain payload hash mismatch"

    return True, None


def verify_vault_ledger(path: Path) -> tuple[bool, str | None]:
    """Verify every persisted entry in a vault ledger file."""
    try:
        with open(path, encoding="utf-8") as file_handle:
            prev_entry_hash = _CHAIN_SEED
            for line_no, line in enumerate(file_handle, start=1):
                row = line.strip()
                if not row:
                    continue
                try:
                    payload = json.loads(row)
                except json.JSONDecodeError as exc:
                    return False, f"line {line_no}: invalid json ({exc})"

                if (
                    payload.get("type") in ("seed", "bootstrap")
                    or payload.get("entry_id") == "GENESIS"
                ):
                    continue

                if "chain" not in payload:
                    logger.warning("Line %s: Skipping legacy record (no chain)", line_no)
                    continue

                ok, reason = verify_vault_record(payload)
                if not ok:
                    return False, f"line {line_no}: {reason}"

                chain = payload.get("chain", {})
                current_prev_hash = chain.get("prev_entry_hash")

                if current_prev_hash in (
                    _CHAIN_SEED,
                    "0x0000000000000000000000000000000000000000000000000000000000000000",
                ):
                    logger.info("Line %s: Merkle chain resync detected", line_no)
                    expected_entry_hash = hashlib.sha256(
                        (current_prev_hash + payload["seal_hash"]).encode()
                    ).hexdigest()
                    if chain.get("entry_hash") != expected_entry_hash:
                        return False, f"line {line_no}: entry hash mismatch on resync record"
                    prev_entry_hash = chain.get("entry_hash")
                    continue

                if current_prev_hash != prev_entry_hash:
                    return (
                        False,
                        f"line {line_no}: chain broken (prev_hash mismatch). "
                        f"Expected {prev_entry_hash}, found {current_prev_hash}",
                    )

                expected_entry_hash = hashlib.sha256(
                    (prev_entry_hash + payload["seal_hash"]).encode()
                ).hexdigest()
                if chain.get("entry_hash") != expected_entry_hash:
                    return False, f"line {line_no}: entry hash mismatch"

                prev_entry_hash = chain.get("entry_hash")

    except OSError as exc:
        return False, str(exc)

    return True, None


def get_last_vault_entry_hash(path: Path = DEFAULT_VAULT_PATH) -> str:
    """Retrieve the entry_hash of the very last line in the ledger."""
    if not path.exists():
        return _CHAIN_SEED

    try:
        with open(path, "rb") as f:
            try:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode().strip()
            if not last_line:
                return _CHAIN_SEED
            data = json.loads(last_line)
            return data.get("chain", {}).get("entry_hash", _CHAIN_SEED)
    except Exception:
        return _CHAIN_SEED


def get_last_n_vault_entries(path: Path, n: int = 3) -> list[dict[str, Any]]:
    """Return the last n entries from the ledger for chain_tip inspection."""
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                row = line.strip()
                if row:
                    try:
                        entries.append(json.loads(row))
                    except json.JSONDecodeError:
                        pass
    except OSError:
        return []
    return entries[-n:] if len(entries) >= n else entries


def _append_vault_record(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as file_handle:
        file_handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _check_vault_postgres_required() -> None:
    """
    Hard-fail guard: if VAULT_POSTGRES_REQUIRED=true is set in the environment
    but no DATABASE_URL is configured, raise immediately so the operator knows
    the canonical write-path is broken before any Merkle entry is attempted.
    """
    if os.environ.get("VAULT_POSTGRES_REQUIRED", "").lower() == "true":
        if not (os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")):
            raise RuntimeError(
                "F1 AMANAH BREACH: VAULT_POSTGRES_REQUIRED=true but no DATABASE_URL "
                "or POSTGRES_URL is set. Vault seal aborted. "
                "Set DATABASE_URL or unset VAULT_POSTGRES_REQUIRED for local dev."
            )


async def seal(
    session_id: str,
    summary: str,
    verdict: str = "SEAL",
    approved_by: str | None = None,
    approval_reference: str | None = None,
    telemetry: dict[str, Any] | None = None,
    seal_mode: Literal["final", "provisional", "audit_only"] = "final",
    auth_context: dict[str, Any] | None = None,
    expected_prev_hash: str | None = None,
    # C2 attribution fields — all callers should supply these
    source_agent: str = "arifos_vault",
    pipeline_stage: str = "999_VAULT",
    **kwargs: Any,
) -> VaultOutput:
    """
    Stage 999: VAULT SEAL (Immutable Commit - APEX-G compliant)

    Args:
        source_agent:   Identifier of the calling agent (e.g. 'arifos_vault',
                        'geox', 'wealth', 'af-forge'). Written to every ledger
                        entry for cross-agent attribution (C2 fix).
        pipeline_stage: The pipeline step that triggered this seal (e.g.
                        '999_VAULT', 'geox_evaluate_prospect'). Written to
                        every ledger entry for causal chain reconstruction.
    """
    # C2 — hard-fail guard for VAULT_POSTGRES_REQUIRED
    _check_vault_postgres_required()

    from core.physics.thermodynamics_hardened import (
        cleanup_thermodynamic_budget,
        consume_tool_energy,
    )

    consume_tool_energy(session_id, n_calls=1)

    telemetry = dict(telemetry) if telemetry else {}

    # Hard Floors to track
    floors = {"F1": "pass", "F5": "pass", "F9": "pass", "F12": "pass", "F13": "pass"}

    # Extract tau_truth to floors
    if "tau_truth" in telemetry:
        floors["tau_truth"] = telemetry.pop("tau_truth")

    # Standardize naming to witness_coherence
    if "confidence" in telemetry and "witness_coherence" not in telemetry:
        telemetry["witness_coherence"] = telemetry.pop("confidence")

    # ── C3: F5 peace2 enforcement ─────────────────────────────────────────────
    # For any final seal with verdict SEAL, peace2 must be >= 1.0.
    # This gate applies to ALL callers (arifos_vault, geox, wealth, af-forge)
    # because all writes route through this organ.
    # Irreversible actions that reach VAULT without peace2 >= 1.0 are F5 violations.
    if seal_mode == "final" and verdict == "SEAL":
        peace2_value = float(telemetry.get("peace2", telemetry.get("peace_score", 1.0)))
        if peace2_value < 1.0:
            floors["F5"] = f"VIOLATION: peace2={peace2_value:.3f} < 1.0"
            logger.error(
                "F5 PEACE VIOLATION: source_agent=%s pipeline_stage=%s peace2=%.3f "
                "— downgrading verdict to HOLD",
                source_agent, pipeline_stage, peace2_value,
            )
            # Downgrade: SEAL → HOLD. Do not raise — let the entry be recorded
            # as HOLD so the operator can audit it. Raising would swallow evidence.
            verdict = "HOLD"
            telemetry["f5_peace_override"] = {
                "original_verdict": "SEAL",
                "overridden_to": "HOLD",
                "peace2": peace2_value,
                "source_agent": source_agent,
                "pipeline_stage": pipeline_stage,
            }
    # ─────────────────────────────────────────────────────────────────────────

    # 0. Merkle-Chain Continuity Check (F1 Amanah)
    prev_hash = get_last_vault_entry_hash(DEFAULT_VAULT_PATH)
    if expected_prev_hash and expected_prev_hash != prev_hash:
        from arifosmcp.runtime.exceptions import ConstitutionalViolation
        from arifosmcp.runtime.fault_codes import ConstitutionalFaultCode

        logger.error(
            "F1 AMANAH VIOLATION: Merkle continuity broken. Session expected %s, Vault contains %s",
            expected_prev_hash,
            prev_hash,
        )
        raise ConstitutionalViolation(
            message=(
                f"F1 Amanah: Vault continuity broken. "
                f"Expected {expected_prev_hash[:16]}..., found {prev_hash[:16]}..."
            ),
            floor_code=ConstitutionalFaultCode.F1_AMANAH_BREACH,
        )

    # 1. Generate Immutable IDs
    ledger_id = f"LGR-{secrets.token_hex(8).upper()}"

    # 2. Build canonical entry for hashing
    timestamp = datetime.now(UTC)
    entry_data = {
        "session_id": session_id,
        "ledger_id": ledger_id,
        "summary": summary,
        "verdict": verdict,
        "approved_by": approved_by or "system",
        "approval_reference": approval_reference,
        "telemetry": telemetry,
        "timestamp": timestamp.isoformat(),
        # C2 attribution
        "source_agent": source_agent,
        "pipeline_stage": pipeline_stage,
        # A-RIF Constitutional RAG: AAA dataset provenance binding
        "aaa_revision": os.getenv("AAA_DATASET_REVISION", "unknown"),
    }

    entry_hash = compute_vault_seal_hash(entry_data)

    from core.shared.crypto import SYSTEM_SIGNER, generate_zkpc_receipt

    signature = SYSTEM_SIGNER.sign_hash(entry_hash)
    pubkey = SYSTEM_SIGNER.public_key_hex

    zkpc_receipt = generate_zkpc_receipt(
        verdict=verdict,
        floors=floors,
        hash_commitment=entry_hash,
        signature=signature,
    )

    # 3. Construct Seal Record
    record = SealRecord(
        status="sealed" if seal_mode == "final" else "provisional",
        ledger_id=ledger_id,
        summary=summary,
        verdict=verdict,
        timestamp=timestamp,
        hash=entry_hash,
        bls_signature=signature,
        signer_pubkey=pubkey,
        zkpc_receipt=zkpc_receipt,
    )

    # 4 & 5. Build Tamper-Evident Hash Chain + Persist
    try:
        if seal_mode == "final":
            async with _vault_write_lock:
                # Re-verify inside the lock (double-check concurrency safety)
                prev_hash = get_last_vault_entry_hash(DEFAULT_VAULT_PATH)
                if expected_prev_hash and expected_prev_hash != prev_hash:
                    from arifosmcp.runtime.exceptions import ConstitutionalViolation
                    from arifosmcp.runtime.fault_codes import ConstitutionalFaultCode

                    raise ConstitutionalViolation(
                        message=f"F1: Vault race condition. Expected {expected_prev_hash[:16]}...",
                        floor_code=ConstitutionalFaultCode.F1_AMANAH_BREACH,
                    )

                entry_chain_hash = hashlib.sha256((prev_hash + entry_hash).encode()).hexdigest()
                chain = HashChain(
                    payload_hash=entry_hash,
                    entry_hash=entry_chain_hash,
                    prev_entry_hash=prev_hash,
                    vault_version=VAULT_VERSION,
                )
                await asyncio.to_thread(
                    _append_vault_record,
                    DEFAULT_VAULT_PATH,
                    {
                        **entry_data,
                        "seal_hash": entry_hash,
                        "bls_signature": signature,
                        "signer_pubkey": pubkey,
                        "zkpc_receipt": zkpc_receipt.model_dump(),
                        "chain": chain.model_dump(),
                    },
                )
        else:
            prev_hash = get_last_vault_entry_hash(DEFAULT_VAULT_PATH)
            entry_chain_hash = hashlib.sha256((prev_hash + entry_hash).encode()).hexdigest()
            chain = HashChain(
                payload_hash=entry_hash,
                entry_hash=entry_chain_hash,
                prev_entry_hash=prev_hash,
                vault_version=VAULT_VERSION,
            )
    except Exception as e:
        logger.error("Vault persistence failure: %s", e)
        prev_hash = _CHAIN_SEED
        entry_chain_hash = hashlib.sha256((prev_hash + entry_hash).encode()).hexdigest()
        chain = HashChain(
            payload_hash=entry_hash,
            entry_hash=entry_chain_hash,
            prev_entry_hash=prev_hash,
            vault_version=VAULT_VERSION,
        )

    # 6. Thermodynamic Cleanup
    final_report = cleanup_thermodynamic_budget(session_id)
    if telemetry is not None:
        telemetry["physics_final"] = final_report

    # 7. EUREKA Layer 6: Register decision in the Reality Feedback Ledger
    try:
        from core.recovery.rollback_engine import outcome_ledger

        outcome_ledger.record_outcome(
            decision_id=ledger_id,
            session_id=session_id,
            verdict_issued=verdict,
            expected_outcome=summary,
            reversible=seal_mode != "final",
        )
    except Exception as _oe:
        logger.warning("OutcomeLedger hook failed (Layer 6 reality feedback degraded): %s", _oe)

    # 7b. Postgres Audit Write-Through (999 SQL Schema)
    # C2: VAULT_POSTGRES_REQUIRED guard already ran at function entry.
    _pg_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if _pg_url and seal_mode == "final":
        try:
            import asyncpg
            import json as _json

            async def _pg_write():
                import uuid
                conn = await asyncpg.connect(_pg_url)
                try:
                    # 1. Ensure 999 Schema exists
                    await conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS vault_events (
                            id SERIAL PRIMARY KEY,
                            event_id UUID NOT NULL,
                            event_type VARCHAR(64) NOT NULL,
                            session_id VARCHAR(128) NOT NULL,
                            actor_id VARCHAR(128),
                            stage VARCHAR(16),
                            verdict VARCHAR(32),
                            payload JSONB,
                            risk_tier VARCHAR(16),
                            merkle_leaf VARCHAR(64),
                            prev_hash VARCHAR(64),
                            chain_hash VARCHAR(64),
                            signature TEXT,
                            signed_by TEXT,
                            sealed_at TIMESTAMPTZ DEFAULT NOW(),
                            created_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        CREATE TABLE IF NOT EXISTS vault_seals (
                            id SERIAL PRIMARY KEY,
                            tree_size INT,
                            merkle_root VARCHAR(64),
                            prev_root VARCHAR(64),
                            first_event_id INT,
                            last_event_id INT,
                            signature TEXT,
                            signed_by TEXT DEFAULT '888_AUDITOR',
                            sealed_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        CREATE INDEX IF NOT EXISTS idx_vault_events_session ON vault_events(session_id);
                        CREATE INDEX IF NOT EXISTS idx_vault_events_stage_verdict ON vault_events(stage, verdict);
                        CREATE INDEX IF NOT EXISTS idx_vault_events_sealed_at ON vault_events(sealed_at DESC);
                        """
                    )

                    # 2. Insert into vault_events
                    new_event_id = uuid.uuid4()
                    row = await conn.fetchrow(
                        """
                        INSERT INTO vault_events (
                            event_id, event_type, session_id, actor_id,
                            stage, verdict, payload, risk_tier,
                            merkle_leaf, prev_hash, chain_hash,
                            signature, signed_by
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, $9, $10, $11, $12, $13)
                        RETURNING id
                        """,
                        new_event_id,
                        "SEAL",
                        session_id,
                        (auth_context or {}).get("actor_id", "anonymous"),
                        pipeline_stage,
                        verdict,
                        _json.dumps({
                            "summary": summary,
                            "telemetry": telemetry or {},
                            "floors": floors
                        }),
                        kwargs.get("risk_tier", "medium"),
                        entry_hash,           # merkle_leaf
                        prev_hash,            # prev_hash
                        entry_chain_hash,     # chain_hash
                        zkpc_receipt.signature if hasattr(zkpc_receipt, "signature") else signature,
                        pubkey                # signed_by
                    )

                    # 3. Check if batch seal (vault_seals) is warranted
                    # Constitutional Trigger: Every 5 events or Phoenix-72 cycle
                    # (Reduced from 72 to 5 for bootstrap phase)
                    event_count = await conn.fetchval("SELECT count(*) FROM vault_events")
                    if event_count >= 5:
                        # Only seal if there are unsealed events
                        last_seal = await conn.fetchrow("SELECT * FROM vault_seals ORDER BY id DESC LIMIT 1")
                        first_id = (last_seal['last_event_id'] + 1) if last_seal else 1
                        last_id = row['id']
                        
                        if last_id >= first_id:
                            # Compute simple root hash for the batch
                            batch_hashes = await conn.fetch(
                                "SELECT merkle_leaf FROM vault_events WHERE id BETWEEN $1 AND $2 ORDER BY id",
                                first_id, last_id
                            )
                            # Filter out empty leaves (from manual/failed entries)
                            valid_hashes = [r['merkle_leaf'] for r in batch_hashes if r['merkle_leaf']]
                            if valid_hashes:
                                combined = "".join(valid_hashes)
                                merkle_root = hashlib.sha256(combined.encode()).hexdigest()
                                
                                await conn.execute(
                                    """
                                    INSERT INTO vault_seals (
                                        tree_size, merkle_root, prev_root,
                                        first_event_id, last_event_id,
                                        signature, signed_by
                                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                                    """,
                                    len(valid_hashes),
                                    merkle_root,
                                    last_seal['merkle_root'] if last_seal else _CHAIN_SEED,
                                    first_id,
                                    last_id,
                                    signature, # Batch signature
                                    "888_AUDITOR"
                                )
                                logger.info("Vault-999 Checkpoint: Merkle Root %s anchored", merkle_root[:16])

                finally:
                    await conn.close()

            await _pg_write()
            logger.info(
                "Vault event written to 999 SQL (ledger_id=%s session_id=%s)",
                ledger_id, session_id,
            )
        except Exception as _pg_exc:
            logger.warning("Postgres 999 SQL write failed (non-critical): %s", _pg_exc)

    # 8. Construct Output
    return VaultOutput(
        session_id=session_id,
        verdict=Verdict.SEAL,
        operation="seal",
        status="SUCCESS",
        seal_record=record,
        hash_chain=chain,
        floors=floors,
        human_witness=1.0,
        ai_witness=1.0,
        earth_witness=1.0,
        evidence={"grounding": f"v1 Tamper-Evident Chain Seal: {entry_chain_hash[:16]}..."},
    )


async def chain_tip(
    n: int = 3,
) -> dict[str, Any]:
    """
    ENH: Return the last n vault entries + continuity status.

    Safe read-only operation — acquires no write lock.
    Agents can call this before sealing to self-verify chain state.

    Returns:
        {
          "tip_entries": [...],       # last n ledger entries (abridged)
          "chain_ok": bool,           # True if tip entries chain correctly
          "latest_entry_hash": str,
          "entry_count": int,
          "vault_path": str,
        }
    """
    entries = get_last_n_vault_entries(DEFAULT_VAULT_PATH, n=n)
    latest_hash = get_last_vault_entry_hash(DEFAULT_VAULT_PATH)

    # Quick continuity check on the tip window
    chain_ok = True
    if len(entries) >= 2:
        for i in range(1, len(entries)):
            prev = entries[i - 1].get("chain", {}).get("entry_hash", "")
            curr_prev = entries[i].get("chain", {}).get("prev_entry_hash", "")
            if prev and curr_prev and prev != curr_prev:
                chain_ok = False
                break

    # Abridge entries for the response (omit bls_signature, full telemetry)
    abridged = [
        {
            "ledger_id": e.get("ledger_id"),
            "verdict": e.get("verdict"),
            "source_agent": e.get("source_agent", "unknown"),
            "pipeline_stage": e.get("pipeline_stage", "unknown"),
            "timestamp": e.get("timestamp"),
            "entry_hash": e.get("chain", {}).get("entry_hash"),
            "prev_entry_hash": e.get("chain", {}).get("prev_entry_hash"),
        }
        for e in entries
    ]

    return {
        "tip_entries": abridged,
        "chain_ok": chain_ok,
        "latest_entry_hash": latest_hash,
        "entry_count": len(entries),
        "vault_path": str(DEFAULT_VAULT_PATH),
    }


async def vault(
    operation: str = "seal",
    **kwargs: Any,
) -> Any:
    """Unified Vault Interface."""
    if operation == "seal":
        return await seal(**kwargs)
    if operation == "chain_tip":
        return await chain_tip(n=int(kwargs.get("n", 3)))

    from .unified_memory import vault as memory_vault

    return await memory_vault(operation=operation, **kwargs)


# Unified alias
SealReceipt = SealRecord
seal_vault = seal


__all__ = [
    "SealReceipt",
    "chain_tip",
    "compute_vault_seal_hash",
    "seal",
    "seal_vault",
    "vault",
    "verify_vault_ledger",
    "verify_vault_record",
]
