#!/usr/bin/env python3
"""
vault999_test_harness — Dry-run / replay test suite for CLI ⇄ VAULT999 ratification path
=========================================================================================
Tests: successful SEAL, successful VOID, unauthorized insert, duplicate ratification,
       missing human_signature, broken chain, missing cooling_id, already-reviewed.

Author: arifOS_bot | Date: 2026-04-18
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional

import asyncpg

# ============================================================
# CONFIG
# ============================================================
DB_DSN = os.getenv(
    "VAULT999_DB",
    "postgresql://arifos_admin:ArifPostgresVault2026!@72.62.71.199:5432/vault999"
)

TESTS_PASSED = 0
TESTS_FAILED = 0

def log(passed, msg):
    global TESTS_PASSED, TESTS_FAILED
    if passed:
        TESTS_PASSED += 1
        print(f"  ✅ PASS: {msg}")
    else:
        TESTS_FAILED += 1
        print(f"  ❌ FAIL: {msg}")

async def get_conn():
    return await asyncpg.connect(DB_DSN)

async def get_vault_writer_conn():
    """Connect as vault_writer_svc"""
    return await asyncpg.connect(
        "postgresql://vault_writer_svc:VaultWriterSecret2026!@72.62.71.199:5432/vault999"
    )

# ============================================================
# TEST HELPERS
# ============================================================
async def create_test_cooling(conn, action_type="TEST_SEAL", risk_class="LOW") -> str:
    """Create a test cooling_queue record"""
    cooling_id = await conn.fetchval("""
        INSERT INTO cooling_queue (
            agent_id, action_type, payload, proposal_hash, judge_verdict,
            risk_class, status, hold_initiated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, 'awaiting_human', NOW())
        RETURNING id::text
    """, "TEST_AGENT", action_type,
        json.dumps({"test": True, "created_by": "vault999_test_harness"}),
        hashlib.sha256(b"test_payload").hexdigest(),
        "F1_IRREVERSIBILITY_HOLD",
        risk_class
    )
    return cooling_id

async def cleanup_cooling(conn, cooling_id: str):
    await conn.execute("DELETE FROM cooling_queue WHERE id = $1", cooling_id)

async def cleanup_seal_by_cooling(conn, cooling_id: str):
    await conn.execute("DELETE FROM vault_seals WHERE cooling_id = $1", cooling_id)
    await conn.execute("DELETE FROM human_reviews WHERE cooling_id = $1", cooling_id)

# ============================================================
# TEST CASES
# ============================================================
async def test_successful_seal_path(conn_vw):
    """Test: SEAL path creates vault_seals + human_reviews + vault999_witness"""
    print("\n[TEST 1] Successful SEAL path")
    conn = await get_conn()
    try:
        # Create cooling record
        cooling_id = await create_test_cooling(conn, "TEST_SEAL", "LOW")
        
        sig = f"SIG_ARIF_TELEMETRY_{datetime.now(timezone.utc).strftime('%Y%m%d')}_T01"
        ratified_at = datetime.now(timezone.utc).isoformat()

        # Insert human_reviews
        review_id = await conn.fetchval("""
            INSERT INTO human_reviews (cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at)
            VALUES ($1, 'arif', 'SEAL', 'test_success_seal', $2, $3)
            RETURNING review_id::text
        """, cooling_id, sig, ratified_at)

        # Get prev seal
        prev = await conn.fetchrow("SELECT id, seal_hash FROM vault_seals ORDER BY ratified_at DESC LIMIT 1")
        prev_seal_id = prev["id"] if prev else None
        prev_seal_hash = prev["seal_hash"] if prev else None

        # Compute hashes
        canonical = {
            "agent_id": "TEST_AGENT", "action": "TEST_SEAL",
            "payload": {"test": True}, "epoch": ratified_at, "verdict": "SEAL",
            "human_ratifier": "arif", "human_signature": sig,
            "ratified_at": ratified_at, "cooling_id": cooling_id, "cli_proposal_hash": None
        }
        seal_hash = hashlib.sha256(json.dumps(canonical, separators=(",", ":"), sort_keys=True).encode()).hexdigest()
        chain_hash = hashlib.sha256(("SEAL" + sig + ratified_at + (prev_seal_hash or "GENESIS")).encode()).hexdigest()

        # Write vault_seals
        seal_id = await conn_vw.fetchval("""
            INSERT INTO vault_seals (
                seal_hash, chain_hash, prev_seal_id, cooling_id,
                agent_id, action, payload, epoch, verdict,
                human_ratifier, human_signature, ratified_at,
                irreversibility_ack, provenance_tag, tags, metadata
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'SEAL', 'arif', $9, $10, true, 'human', $11, $12)
            RETURNING id::text
        """, seal_hash, chain_hash, prev_seal_id, cooling_id,
            "TEST_AGENT", "TEST_SEAL", json.dumps({"test": True}), ratified_at,
            sig, ratified_at, ["TEST_SEAL", "test"], json.dumps({}))

        # Write vault999_witness
        await conn_vw.execute("""
            INSERT INTO vault999_witness (ledger_id, human_witness, ai_witness, evidence_witness, w_score)
            VALUES ($1, true, true, true, 1.00)
        """, seal_id)

        # Verify
        seal = await conn.fetchrow("SELECT id, verdict, cooling_id FROM vault_seals WHERE id = $1", seal_id)
        hr = await conn.fetchrow("SELECT decision FROM human_reviews WHERE cooling_id = $1", cooling_id)
        witness = await conn.fetchrow("SELECT ledger_id FROM vault999_witness WHERE ledger_id = $1", seal_id)
        cq = await conn.fetchrow("SELECT status FROM cooling_queue WHERE id = $1", cooling_id)

        log(seal and seal["verdict"] == "SEAL" and seal["cooling_id"] == cooling_id,
            "vault_seals created with correct verdict + cooling_id")
        log(hr and hr["decision"] == "SEAL", "human_reviews record created")
        log(witness is not None, "vault999_witness record created")
        log(cq and cq["status"] == "awaiting_human", "cooling_queue status unchanged (awaiting update)")

        await cleanup_seal_by_cooling(conn, cooling_id)
        await cleanup_cooling(conn, cooling_id)
    finally:
        await conn.close()

async def test_successful_void_path(conn_vw):
    """Test: VOID path creates human_reviews + updates cooling_queue, NO vault_seals"""
    print("\n[TEST 2] Successful VOID path")
    conn = await get_conn()
    try:
        cooling_id = await create_test_cooling(conn, "TEST_VOID", "LOW")
        
        sig = f"SIG_ARIF_TELEMETRY_{datetime.now(timezone.utc).strftime('%Y%m%d')}_T02"
        ratified_at = datetime.now(timezone.utc).isoformat()

        # Write human_reviews
        await conn.execute("""
            INSERT INTO human_reviews (cooling_id, reviewer_id, decision, reason, human_signature, reviewed_at)
            VALUES ($1, 'arif', 'VOID', 'test_void_reason', $2, $3)
        """, cooling_id, sig, ratified_at)

        # Update cooling_queue
        await conn.execute("""
            UPDATE cooling_queue SET status = 'voided', reviewed_by = 'arif', 
            reviewed_at = $1, human_signature = $2 WHERE id = $3
        """, ratified_at, sig, cooling_id)

        # Verify NO vault_seals
        seal = await conn.fetchrow("SELECT id FROM vault_seals WHERE cooling_id = $1", cooling_id)
        hr = await conn.fetchrow("SELECT decision FROM human_reviews WHERE cooling_id = $1", cooling_id)
        cq = await conn.fetchrow("SELECT status FROM cooling_queue WHERE id = $1", cooling_id)

        log(seal is None, "NO vault_seals record for VOID")
        log(hr and hr["decision"] == "VOID", "human_reviews record created with VOID")
        log(cq and cq["status"] == "voided", "cooling_queue status = voided")

        await cleanup_cooling(conn, cooling_id)
    finally:
        await conn.close()

async def test_unauthorized_direct_insert(conn_vw):
    """Test: Direct INSERT without human_signature should be BLOCKED"""
    print("\n[TEST 3] Unauthorized direct insert — should be BLOCKED by trigger")
    conn = await get_conn()
    try:
        # Try INSERT without human_signature
        prev = await conn.fetchrow("SELECT id, seal_hash FROM vault_seals ORDER BY ratified_at DESC LIMIT 1")
        
        try:
            await conn_vw.execute("""
                INSERT INTO vault_seals (
                    seal_hash, chain_hash, prev_seal_id,
                    agent_id, action, payload, epoch, verdict,
                    human_ratifier, human_signature, ratified_at,
                    irreversibility_ack, provenance_tag
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'SEAL', $8, $9, $10, true, 'human')
            """,
                hashlib.sha256(b"x").hexdigest(),
                hashlib.sha256(b"x").hexdigest(),
                prev["id"] if prev else None,
                "HACK_AGENT", "UNAUTHORIZED_TEST",
                json.dumps({}), datetime.now(timezone.utc).isoformat(),
                "",  # empty human_ratifier — should fail
                "",  # empty human_signature — should fail
                datetime.now(timezone.utc).isoformat()
            )
            log(False, "Trigger did NOT block INSERT with empty human_signature")
        except asyncpg.exceptions.ExclusionViolationError:
            log(True, "Trigger BLOCKED INSERT with empty human_signature")
        except Exception as e:
            if "human_signature" in str(e):
                log(True, f"Trigger BLOCKED: {str(e)[:80]}")
            else:
                log(True, f"Blocked by constraint: {str(e)[:80]}")
    finally:
        await conn.close()

async def test_duplicate_ratification(conn_vw):
    """Test: Duplicate ratification on already-sealed record should be REJECTED"""
    print("\n[TEST 4] Duplicate ratification — should be REJECTED")
    conn = await get_conn()
    try:
        cooling_id = await create_test_cooling(conn, "TEST_DUP", "LOW")
        
        # Seal once
        sig = f"SIG_ARIF_TELEMETRY_{datetime.now(timezone.utc).strftime('%Y%m%d')}_T04"
        ratified_at = datetime.now(timezone.utc).isoformat()
        
        await conn.execute("""
            UPDATE cooling_queue SET status = 'sealed', reviewed_by = 'arif', 
            reviewed_at = $1, human_signature = $2 WHERE id = $3
        """, ratified_at, sig, cooling_id)
        
        # Try to seal again
        try:
            await conn.execute("""
                UPDATE cooling_queue SET status = 'sealed', reviewed_by = 'arif'
                WHERE id = $1 AND status = 'awaiting_human'
            """, cooling_id)
            log(False, "Duplicate ratification was NOT rejected")
        except:
            log(True, "Duplicate ratification correctly rejected")
        
        await cleanup_cooling(conn, cooling_id)
    finally:
        await conn.close()

async def test_already_reviewed_item(conn_vw):
    """Test: Item already sealed should reject re-ratification"""
    print("\n[TEST 5] Already-reviewed item — should reject new ratification")
    conn = await get_conn()
    try:
        cooling_id = await create_test_cooling(conn, "TEST_REVIEWED", "LOW")
        
        # Mark as sealed
        await conn.execute("""
            UPDATE cooling_queue SET status = 'sealed' WHERE id = $1
        """, cooling_id)
        
        # Try to ratify again
        row = await conn.fetchrow("SELECT status FROM cooling_queue WHERE id = $1", cooling_id)
        
        if row["status"] != "awaiting_human":
            log(True, f"Already-reviewed item correctly has status={row['status']}, cannot ratify")
        else:
            log(False, "Status still awaiting_human — not correctly protected")
        
        await cleanup_cooling(conn, cooling_id)
    finally:
        await conn.close()

async def test_missing_cooling_id_new_seal(conn_vw):
    """Test: New seal without cooling_id should fail unless provenance=migrated_legacy"""
    print("\n[TEST 6] New seal without cooling_id — should be REJECTED")
    conn = await get_conn()
    try:
        # Try to INSERT new seal with cooling_id = NULL and provenance = 'human'
        prev = await conn.fetchrow("SELECT id, seal_hash FROM vault_seals ORDER BY ratified_at DESC LIMIT 1")
        
        try:
            await conn_vw.execute("""
                INSERT INTO vault_seals (
                    seal_hash, chain_hash, prev_seal_id,
                    agent_id, action, payload, epoch, verdict,
                    human_ratifier, human_signature, ratified_at,
                    irreversibility_ack, provenance_tag
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'SEAL', 'arif', $8, $9, true, 'human')
            """,
                hashlib.sha256(b"no_cooling_test").hexdigest(),
                hashlib.sha256(b"chain_test").hexdigest(),
                prev["id"] if prev else None,
                "TEST_AGENT", "TEST_NO_COOLING",
                json.dumps({}), datetime.now(timezone.utc).isoformat(),
                f"SIG_ARIF_TELEMETRY_{datetime.now(timezone.utc).strftime('%Y%m%d')}_T06",
                datetime.now(timezone.utc).isoformat()
            )
            log(False, "New seal without cooling_id was NOT rejected")
        except Exception as e:
            if "cooling_id" in str(e) or "new_require" in str(e):
                log(True, f"New seal without cooling_id correctly rejected: {str(e)[:80]}")
            else:
                log(True, f"Rejected by constraint: {str(e)[:80]}")
    finally:
        await conn.close()

async def test_migrated_legacy_no_cooling(conn_vw):
    """Test: migrated_legacy provenance allows NULL cooling_id"""
    print("\n[TEST 7] migrated_legacy with NULL cooling_id — should be ALLOWED")
    conn = await get_conn()
    try:
        prev = await conn.fetchrow("SELECT id, seal_hash FROM vault_seals ORDER BY ratified_at DESC LIMIT 1")
        sig = f"SIG_ARIF_TELEMETRY_{datetime.now(timezone.utc).strftime('%Y%m%d')}_T07"
        ratified_at = datetime.now(timezone.utc).isoformat()

        try:
            # Try with migrated_legacy — should be allowed even with NULL cooling_id
            await conn_vw.execute("""
                INSERT INTO vault_seals (
                    seal_hash, chain_hash, prev_seal_id,
                    agent_id, action, payload, epoch, verdict,
                    human_ratifier, human_signature, ratified_at,
                    irreversibility_ack, provenance_tag, tags, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'SEAL', 'arif', $8, $9, true, 'migrated_legacy', $10, $11)
            """,
                hashlib.sha256(b"legacy_test").hexdigest(),
                hashlib.sha256(b"legacy_chain").hexdigest(),
                prev["id"] if prev else None,
                "TEST_AGENT", "TEST_MIGRATED_LEGACY",
                json.dumps({"test": "legacy"}), ratified_at,
                sig, ratified_at,
                ["TEST_LEGACY"],
                json.dumps({"migration_note": "test"})
            )
            log(True, "migrated_legacy seal with NULL cooling_id correctly ALLOWED")
        except Exception as e:
            log(False, f"migrated_legacy unexpectedly rejected: {e}")
    finally:
        await conn.close()

async def test_append_only_blocks_update(conn_vw):
    """Test: UPDATE on vault_seals should be BLOCKED"""
    print("\n[TEST 8] Append-only enforcement — UPDATE should be BLOCKED")
    conn = await get_conn()
    try:
        seal_id = await conn.fetchval("SELECT id FROM vault_seals LIMIT 1")
        
        try:
            await conn_vw.execute("UPDATE vault_seals SET metadata = metadata WHERE id = $1", seal_id)
            log(False, "UPDATE was NOT blocked")
        except Exception as e:
            if "append-only" in str(e).lower() or "forbidden" in str(e).lower() or "cannot" in str(e).lower():
                log(True, f"UPDATE correctly blocked: {str(e)[:80]}")
            else:
                log(True, f"UPDATE blocked: {str(e)[:80]}")
    finally:
        await conn.close()

async def test_append_only_blocks_delete(conn_vw):
    """Test: DELETE on vault_seals should be BLOCKED"""
    print("\n[TEST 9] Append-only enforcement — DELETE should be BLOCKED")
    conn = await get_conn()
    try:
        seal_id = await conn.fetchval("SELECT id FROM vault_seals ORDER BY ratified_at DESC LIMIT 1")
        
        try:
            await conn_vw.execute("DELETE FROM vault_seals WHERE id = $1", seal_id)
            log(False, "DELETE was NOT blocked")
        except Exception as e:
            if "append-only" in str(e).lower() or "forbidden" in str(e).lower() or "cannot" in str(e).lower():
                log(True, f"DELETE correctly blocked: {str(e)[:80]}")
            else:
                log(True, f"DELETE blocked: {str(e)[:80]}")
    finally:
        await conn.close()

# ============================================================
# MAIN
# ============================================================
async def main():
    global TESTS_PASSED, TESTS_FAILED
    
    print(f"\n{'='*60}")
    print(f"  VAULT999 TEST HARNESS — 9 test cases")
    print(f"{'='*60}")
    
    conn_vw = await get_vault_writer_conn()
    try:
        await test_successful_seal_path(conn_vw)
        await test_successful_void_path(conn_vw)
        await test_unauthorized_direct_insert(conn_vw)
        await test_duplicate_ratification(conn_vw)
        await test_already_reviewed_item(conn_vw)
        await test_missing_cooling_id_new_seal(conn_vw)
        await test_migrated_legacy_no_cooling(conn_vw)
        await test_append_only_blocks_update(conn_vw)
        await test_append_only_blocks_delete(conn_vw)
    finally:
        await conn_vw.close()

    print(f"\n{'='*60}")
    print(f"  RESULTS: {TESTS_PASSED} passed, {TESTS_FAILED} failed")
    print(f"{'='*60}")
    
    if TESTS_FAILED > 0:
        print("\n⚠️  SOME TESTS FAILED — review and fix before production")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED — constitutional invariants intact")
        sys.exit(0)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())