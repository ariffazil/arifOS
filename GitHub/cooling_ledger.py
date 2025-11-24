"""
cooling_ledger.py — L1 Cooling Ledger for arifOS v33Ω.

Responsibilities:
- Append-only audit log for high-stakes interactions
- Provide recent-window queries for Phoenix-72 analysis

Specification:
- See spec/VAULT_999.md and cooling_ledger_schema.json for schema.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class CoolingMetrics:
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    rasa: bool
    amanah: bool
    tri_witness: float
    psi: Optional[float] = None


@dataclass
class CoolingEntry:
    timestamp: float
    query: str
    candidate_output: str
    metrics: CoolingMetrics
    verdict: str
    floor_failures: List[str]
    sabar_reason: Optional[str]
    organs: Dict[str, bool]
    phoenix_cycle_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_json_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metrics"] = asdict(self.metrics)
        return d


@dataclass
class LedgerConfig:
    ledger_path: Path = Path("runtime/vault_999/cooling_ledger.jsonl")


class CoolingLedger:
    """
    CoolingLedger — Append-only JSONL audit log.

    Usage:
        ledger = CoolingLedger()
        ledger.append(entry)
        for e in ledger.iter_recent(hours=72): ...
    """

    def __init__(self, config: Optional[LedgerConfig] = None):
        self.config = config or LedgerConfig()
        self.config.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: CoolingEntry) -> None:
        """
        Append a new entry to the ledger. Never mutates existing lines.
        """
        line = json.dumps(entry.to_json_dict(), ensure_ascii=False)
        with self.config.ledger_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def iter_recent(self, hours: float = 72.0) -> Iterable[Dict[str, Any]]:
        """
        Iterate over entries from the last N hours.

        Note: This is a simple implementation; real systems might index by time.
        """
        cutoff = time.time() - hours * 3600.0
        path = self.config.ledger_path
        if not path.exists():
            return []

        def _generator():
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("timestamp", 0) >= cutoff:
                        yield obj

        return _generator()