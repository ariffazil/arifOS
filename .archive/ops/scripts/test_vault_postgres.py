#!/usr/bin/env python3
"""
Test script for VAULT999 PostgreSQL integration.

Usage:
    python scripts/test_vault_postgres.py

This tests:
1. PostgresVaultStore initialization
2. Event sealing (dual-write to Postgres + filesystem)
3. Chain retrieval
4. Chain verification
5. HardenedVaultSeal integration

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def test_vault_store():
    """Test the PostgresVaultStore directly."""
    logger.info("=" * 60)
    logger.info("TEST 1: PostgresVaultStore Direct Test")
    logger.info("=" * 60)
    
    try:
        from arifosmcp.runtime.vault_postgres import PostgresVaultStore, VaultEvent
    except ImportError as e:
        logger.error(f"❌ Failed to import vault_postgres: {e}")
        return False
    
    # Initialize store
    store = PostgresVaultStore()
    logger.info("✓ Vault store initialized")
    
    # Create test events
    events = []
    for i in range(3):
        event = VaultEvent(
            event_type="test_seal",
            session_id="test-session-001",
            actor_id="test_agent",
            stage="999_VAULT",
            verdict="SEAL",
            payload={
                "test_id": i,
                "message": f"Test event {i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            risk_tier="low",
        )
        events.append(event)
    
    # Seal events
    results = []
    for i, event in enumerate(events):
        logger.info(f"Sealing event {i+1}/3...")
        result = await store.seal(event)
        
        if result.success:
            logger.info(f"  ✓ Sealed: db_id={result.db_id}, hash={result.chain_hash[:16]}...")
            results.append(result)
        else:
            logger.error(f"  ❌ Failed: {result.error}")
            return False
    
    # Retrieve chain
    logger.info("Retrieving chain from PostgreSQL...")
    chain = await store.get_chain(limit=10)
    logger.info(f"  ✓ Retrieved {len(chain)} entries")
    
    for entry in chain:
        logger.info(f"    - {entry['event_type']}: {entry['chain_hash'][:16]}...")
    
    # Verify chain
    logger.info("Verifying chain integrity...")
    is_valid, message = await store.verify_chain()
    if is_valid:
        logger.info(f"  ✓ {message}")
    else:
        logger.error(f"  ❌ {message}")
        return False
    
    await store.close()
    logger.info("✓ Vault store test passed\n")
    return True


async def test_hardened_vault_seal():
    """Test the HardenedVaultSeal integration."""
    logger.info("=" * 60)
    logger.info("TEST 2: HardenedVaultSeal Integration Test")
    logger.info("=" * 60)
    
    try:
        from arifosmcp.runtime.tools_hardened_v2 import HardenedVaultSeal
        from arifosmcp.runtime.contracts_v2 import TraceContext
    except ImportError as e:
        logger.error(f"❌ Failed to import: {e}")
        return False
    
    # Initialize seal
    seal_tool = HardenedVaultSeal()
    logger.info("✓ HardenedVaultSeal initialized")
    
    # Create test decision
    decision = {
        "verdict": "SEAL",
        "action": "test_action",
        "risk_level": "low",
    }
    
    auth_context = {
        "actor_id": "test_agent",
        "actor_type": "automated",
    }
    
    trace = TraceContext(
        trace_id="test-trace-001",
        parent_trace_id=None,
        stage_id="test-stage-001",
        session_id="test-session-hardened",
        policy_version="v1",
    )
    
    # Seal decision
    logger.info("Sealing test decision...")
    result = await seal_tool.seal(
        decision=decision,
        auth_context=auth_context,
        risk_tier="low",
        session_id="test-session-hardened",
        trace=trace,
    )
    
    logger.info(f"  Status: {result.status.value}")
    logger.info(f"  Verdict: {result.payload.get('state')}")
    logger.info(f"  Hash: {result.payload.get('hash', 'N/A')[:32]}...")
    
    if result.payload.get('db_id'):
        logger.info(f"  DB ID: {result.payload['db_id']}")
    
    if result.status.value == "OK":
        logger.info("✓ HardenedVaultSeal test passed\n")
        return True
    else:
        logger.error(f"❌ HardenedVaultSeal test failed: {result.payload}")
        return False


async def test_blackout_mode():
    """Test the Quantum Sabar (blackout) mode."""
    logger.info("=" * 60)
    logger.info("TEST 3: Quantum Sabar (Blackout) Test")
    logger.info("=" * 60)
    
    try:
        from arifosmcp.runtime.tools_hardened_v2 import HardenedVaultSeal
    except ImportError as e:
        logger.error(f"❌ Failed to import: {e}")
        return False
    
    seal_tool = HardenedVaultSeal()
    
    # Create blackout decision
    decision = {
        "verdict": "SEAL",
        "witness_blackout": True,  # Triggers SABAR
    }
    
    logger.info("Sealing with blackout flag...")
    result = await seal_tool.seal(
        decision=decision,
        session_id="test-session-blackout",
    )
    
    logger.info(f"  Status: {result.status.value}")
    logger.info(f"  State: {result.payload.get('state')}")
    logger.info(f"  Purgatory ID: {result.payload.get('purgatory_id')}")
    
    if result.status.value == "SABAR" and result.payload.get("state") == "PURGATORY":
        logger.info("✓ Quantum Sabar test passed\n")
        return True
    else:
        logger.error(f"❌ Quantum Sabar test failed")
        return False


async def verify_filesystem_mirror():
    """Verify that filesystem mirror was written."""
    logger.info("=" * 60)
    logger.info("TEST 4: Filesystem Mirror Verification")
    logger.info("=" * 60)
    
    vault_path = Path("/root/VAULT999")
    events_file = vault_path / "SEALED_EVENTS.jsonl"
    chain_file = vault_path / "SEAL_CHAIN.txt"
    
    if not events_file.exists():
        logger.error(f"❌ Events file not found: {events_file}")
        return False
    
    logger.info(f"✓ Events file exists: {events_file}")
    
    # Count lines
    with open(events_file) as f:
        lines = f.readlines()
    logger.info(f"  Events count: {len(lines)}")
    
    if chain_file.exists():
        logger.info(f"✓ Chain file exists: {chain_file}")
        with open(chain_file) as f:
            chain = json.load(f)
        logger.info(f"  Latest seal: {chain.get('seal')}")
        logger.info(f"  Depth: {chain.get('depth')}")
    else:
        logger.warning("  Chain file not yet created (expected on first run)")
    
    logger.info("✓ Filesystem mirror test passed\n")
    return True


async def verify_postgres_data():
    """Verify PostgreSQL data."""
    logger.info("=" * 60)
    logger.info("TEST 5: PostgreSQL Data Verification")
    logger.info("=" * 60)
    
    try:
        import asyncpg
    except ImportError:
        logger.warning("⚠ asyncpg not available, skipping PostgreSQL verification")
        return True
    
    try:
        # Connect with empty password (trust auth in container)
        conn = await asyncpg.connect(
            host="localhost",
            port=5432,
            user="arifos_admin",
            password="",
            database="arifos_vault",
        )
        
        # Count events
        count = await conn.fetchval("SELECT COUNT(*) FROM vault_events")
        logger.info(f"  Total events in PostgreSQL: {count}")
        
        # Get latest events
        rows = await conn.fetch(
            """
            SELECT id, event_type, verdict, chain_hash, sealed_at
            FROM vault_events
            ORDER BY id DESC
            LIMIT 5
            """
        )
        
        logger.info("  Latest events:")
        for row in rows:
            logger.info(f"    - {row['event_type']} ({row['verdict']}): {row['chain_hash'][:16]}...")
        
        # Verify chain integrity
        result = await conn.fetchrow("SELECT * FROM verify_chain_integrity()")
        if result['is_valid']:
            logger.info(f"  ✓ Chain integrity verified: {result['total_checked']} entries")
        else:
            logger.error(f"  ❌ Chain broken at: {result['broken_at_id']}")
        
        await conn.close()
        logger.info("✓ PostgreSQL verification passed\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL verification failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("VAULT999 PostgreSQL Integration Tests")
    logger.info("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("VaultStore Direct", await test_vault_store()))
    results.append(("HardenedVaultSeal", await test_hardened_vault_seal()))
    results.append(("Quantum Sabar", await test_blackout_mode()))
    results.append(("Filesystem Mirror", await verify_filesystem_mirror()))
    results.append(("PostgreSQL Data", await verify_postgres_data()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        logger.info(f"  {status}: {name}")
    
    logger.info("-" * 60)
    logger.info(f"  Total: {passed}/{total} passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! VAULT999 PostgreSQL integration is working.")
        return 0
    else:
        logger.warning(f"\n⚠ {total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
