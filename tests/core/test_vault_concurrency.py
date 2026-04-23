import asyncio
import concurrent.futures
import hashlib
import json
import logging

import pytest

import core.organs._4_vault
from core.organs._4_vault import seal, verify_vault_ledger
from core.physics.thermodynamics_hardened import init_thermodynamic_budget

logging.basicConfig(level=logging.ERROR)


@pytest.mark.asyncio
async def test_vault999_merkle_chain_concurrency(tmp_path, monkeypatch):
    """
    Verify VAULT999 Merkle-chain integrity under high-concurrency loads.
    Ensures that multiple concurrent appends to the file ledger maintain a perfectly
    linked cryptographic chain without tearing or hash desyncs.
    """
    ledger_path = tmp_path / "concurrent_vault.jsonl"
    monkeypatch.setattr(core.organs._4_vault, "DEFAULT_VAULT_PATH", ledger_path)

    tasks = []
    num_concurrent = 50  # 50 concurrent seals

    async def worker(idx: int):
        session_id = f"concurency-test-{idx}"
        init_thermodynamic_budget(session_id, initial_budget=10.0)
        await seal(
            session_id=session_id,
            summary=f"Concurrent entry {idx}",
            verdict="SEAL",
            telemetry={"idx": idx},
            seal_mode="final",
        )

    for i in range(num_concurrent):
        tasks.append(worker(i))

    await asyncio.gather(*tasks)

    # Now verify the chain via the canonical ledger verifier
    ok, reason = verify_vault_ledger(ledger_path)

    assert ok is True, f"Merkle chain broken under concurrency: {reason}"
