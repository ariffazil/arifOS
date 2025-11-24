"""
Tests for Phoenix-72 metabolism (L2).
"""

from pathlib import Path
import shutil
import tempfile

from arifos_core.memory.vault999 import Vault999, VaultConfig
from arifos_core.memory.cooling_ledger import (
    CoolingLedger, LedgerConfig, CoolingEntry, CoolingMetrics
)
from arifos_core.memory.phoenix72 import Phoenix72


def _make_ledger_with_failure(tmpdir: str):
    ledger_path = Path(tmpdir) / "cooling_ledger.jsonl"
    ledger = CoolingLedger(LedgerConfig(ledger_path=ledger_path))

    metrics = CoolingMetrics(
        truth=0.90,                 # cause failure
        delta_s=0.01,
        peace_squared=1.00,
        kappa_r=0.95,
        omega_0=0.04,
        rasa=True,
        amanah=True,
        tri_witness=0.96,
        psi=0.90,
    )

    entry = CoolingEntry(
        timestamp=9999999999.0,
        query="test failure",
        candidate_output="bad answer",
        metrics=metrics,
        verdict="VOID",
        floor_failures=["Truth < 0.99"],
        sabar_reason="Truth floor breach",
        organs={},
        phoenix_cycle_id=None,
        metadata={},
    )

    ledger.append(entry)
    return ledger


def test_phoenix_collects_scars_and_updates_floors():
    tmpdir = tempfile.mkdtemp()
    try:
        # Initialize Vault
        constitution_path = Path(tmpdir) / "constitution.json"
        vault = Vault999(VaultConfig(vault_path=constitution_path))

        # Add failure to ledger
        ledger = _make_ledger_with_failure(tmpdir)

        phoenix = Phoenix72(vault, ledger)

        # Phase 1: Scars
        scars = phoenix.collect_scars()
        assert len(scars) >= 1

        # Phase 2: Pattern
        pattern = phoenix.synthesize_pattern(scars)
        assert pattern is not None

        # Phase 3: Amendment
        amendment = phoenix.draft_amendment(pattern)
        assert amendment.id.startswith("PHOENIX-72-")

        # Phase 4–5: Apply Amendment
        phoenix.apply_amendment(amendment)

        new_vault = Vault999(VaultConfig(vault_path=constitution_path))
        new_floors = new_vault.get_floors()
        assert new_floors["truth_min"] >= 0.99
    finally:
        shutil.rmtree(tmpdir)