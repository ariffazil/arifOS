
import time
from pathlib import Path
import tempfile, shutil

from arifos_core.memory.cooling_ledger import (
    CoolingLedger, LedgerConfig, CoolingEntry, CoolingMetrics
)

def test_cooling_ledger_roundtrip():
    tmp = tempfile.mkdtemp()
    try:
        ledger_path = Path(tmp) / "cl.jsonl"
        ledger = CoolingLedger(LedgerConfig(ledger_path=ledger_path))
        metrics = CoolingMetrics(
            truth=0.99, delta_s=0.1, peace_squared=1.05,
            kappa_r=0.96, omega_0=0.04, rasa=True, amanah=True,
            tri_witness=0.96, psi=1.2
        )
        entry = CoolingEntry(
            timestamp=time.time(),
            query="test",
            candidate_output="ok",
            metrics=metrics,
            verdict="SEAL",
            floor_failures=[],
            sabar_reason=None,
            organs={"@RIF": False}
        )
        ledger.append(entry)
        items = list(ledger.iter_recent(hours=1))
        assert len(items) >= 1
        assert items[0]["query"] == "test"
    finally:
        shutil.rmtree(tmp)
