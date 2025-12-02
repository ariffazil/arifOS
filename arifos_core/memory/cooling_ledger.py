"""
cooling_ledger.py — L1 Cooling Ledger for arifOS v35Ω.

Responsibilities:
- Append-only audit log for high-stakes interactions
- Provide recent-window queries for Phoenix-72 analysis
- Hash-chain integrity verification

Specification:
- See spec/VAULT_999.md and cooling_ledger_schema.json for schema.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from arifos_core.kms_signer import KmsSigner
    from arifos_core.metrics import Metrics


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


# ——————————————————— HASH-CHAIN INTEGRITY FUNCTIONS ——————————————————— #


def _compute_hash(entry: Dict[str, Any]) -> str:
    """
    Compute SHA3-256 hash of an entry for chain integrity.

    Excludes the 'hash', 'kms_signature', and 'kms_key_id' fields from the computation.
    Uses canonical JSON representation.
    """
    excluded_fields = {"hash", "kms_signature", "kms_key_id"}
    data = {k: v for k, v in entry.items() if k not in excluded_fields}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canonical.encode("utf-8")).hexdigest()


def append_entry(
    path: Union[Path, str],
    entry: Dict[str, Any],
    kms_signer: Optional["KmsSigner"] = None,
) -> None:
    """
    Append an entry to the ledger with hash-chain integrity.

    Args:
        path: Path to the ledger file (JSONL format)
        entry: Entry dictionary to append
        kms_signer: Optional KmsSigner instance for cryptographic signing
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    prev_hash = None
    if path.exists() and path.stat().st_size > 0:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                if last_line:
                    try:
                        last_entry = json.loads(last_line)
                        prev_hash = last_entry.get("hash")
                    except json.JSONDecodeError:
                        pass

    entry["prev_hash"] = prev_hash
    entry["hash"] = _compute_hash(entry)

    if kms_signer is not None:
        hash_bytes = bytes.fromhex(entry["hash"])
        signature_b64 = kms_signer.sign_hash(hash_bytes)
        entry["kms_signature"] = signature_b64
        entry["kms_key_id"] = kms_signer.config.key_id

    line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def verify_chain(path: Union[Path, str]) -> Tuple[bool, str]:
    """
    Verify the integrity of the hash chain in the ledger.
    """
    path = Path(path)

    if not path.exists():
        return False, "Ledger file does not exist"

    entries: List[Dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as e:
                return False, f"JSON decode error at line {line_num}: {e}"

    if not entries:
        return True, "Empty ledger (valid)"

    if entries[0].get("prev_hash") is not None:
        return False, "First entry should have prev_hash=null"

    for i, entry in enumerate(entries):
        stored_hash = entry.get("hash")
        if not stored_hash:
            return False, f"Entry {i} missing hash field"

        computed_hash = _compute_hash(entry)
        if stored_hash != computed_hash:
            return False, f"Entry {i} hash mismatch: stored={stored_hash[:8]}..., computed={computed_hash[:8]}..."

        if i > 0:
            expected_prev_hash = entries[i - 1].get("hash")
            actual_prev_hash = entry.get("prev_hash")
            if actual_prev_hash != expected_prev_hash:
                return False, f"Entry {i} prev_hash mismatch: expected={expected_prev_hash[:8]}..., actual={actual_prev_hash[:8] if actual_prev_hash else 'null'}..."

    return True, f"Chain verified: {len(entries)} entries"


def log_cooling_entry(
    *,
    job_id: str,
    verdict: str,
    metrics: "Metrics",
    stakes: str = "normal",
    pipeline_path: Optional[List[str]] = None,
    context_summary: str = "",
    tri_witness_components: Optional[Dict[str, float]] = None,
    logger=None,
    ledger_path: Union[Path, str] = LedgerConfig().ledger_path,
    high_stakes: Optional[bool] = None,
) -> Dict[str, Any]:
    """Append a hash-chained Cooling Ledger entry and return the entry dict."""

    from arifos_core.APEX_PRIME import check_floors
    from arifos_core.metrics import Metrics

    if pipeline_path is None:
        pipeline_path = []

    if not isinstance(metrics, Metrics):
        raise TypeError("metrics must be a Metrics instance")

    floors = check_floors(
        metrics,
        tri_witness_required=high_stakes if high_stakes is not None else stakes == "high",
    )

    entry = {
        "ledger_version": "v35Ω",
        "timestamp": time.time(),
        "job_id": job_id,
        "stakes": stakes,
        "pipeline_path": pipeline_path,
        "metrics": metrics.to_dict(),
        "verdict": verdict,
        "floor_failures": floors.reasons,
        "sabar_reason": None,
        "tri_witness_components": tri_witness_components or {},
        "context_summary": context_summary,
    }

    append_entry(ledger_path, entry)

    if logger:
        logger.info("CoolingLedgerEntry: %s", entry)

    return entry


__all__ = [
    "CoolingMetrics",
    "CoolingEntry",
    "CoolingLedger",
    "LedgerConfig",
    "append_entry",
    "verify_chain",
    "log_cooling_entry",
]
