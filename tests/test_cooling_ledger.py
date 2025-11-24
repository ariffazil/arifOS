"""
Basic tests for CoolingLedger (L1).
"""

import time
from pathlib import Path
import shutil
import tempfile

from arifos_core.memory.cooling_ledger import (
    CoolingLedger,
    LedgerConfig,
    CoolingMetrics,
    CoolingEntry,
)


def test_cooling_ledger_append_and_read_recent():
    tmpdir = tempfile.mkdtemp()
    try:
        path = Path(tmpdir) / "cooling_ledger.jsonl"
        ledger = CoolingLedger(LedgerConfig(ledger_path=path))

        metrics = CoolingMetrics(
            truth=0.995,
            delta_s=0.12,
            peace_squared=1.08,
            kappa_r=0.97,
            omega_0=0.041,
            rasa=True,
            amanah=True,
            tri_witness=0.96,
            psi=1.10,
        )

        entry = CoolingEntry(
            timestamp=time.time(),
            query="test query",
            candidate_output="test answer",
            metrics=metrics,
            verdict="SEAL",
            floor_failures=[],
            sabar_reason=None,
            organs={"@RIF": False},
            phoenix_cycle_id=None,
            metadata={"unit_test": True},
        )

        ledger.append(entry)

        recent = list(ledger.iter_recent(hours=1))
        assert len(recent) == 1
        assert recent[0]["query"] == "test query"
        assert recent[0]["verdict"] == "SEAL"
    finally:
        shutil.rmtree(tmpdir)