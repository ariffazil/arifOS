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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from arifos_core.kms_signer import KmsSigner
    from arifos_core.metrics import Metrics
    from arifos_core.genius_metrics import GeniusVerdict


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

                    raw_ts = obj.get("timestamp", 0)
                    # Support both legacy float timestamps and new ISO-8601 strings
                    ts: Optional[float]
                    if isinstance(raw_ts, (int, float)):
                        ts = float(raw_ts)
                    elif isinstance(raw_ts, str):
                        try:
                            ts = datetime.fromisoformat(
                                raw_ts.replace("Z", "+00:00")
                            ).timestamp()
                        except Exception:
                            ts = None
                    else:
                        ts = None

                    if ts is not None and ts >= cutoff:
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
    query: Optional[str] = None,
    candidate_output: Optional[str] = None,
    eye_report: Optional[Any] = None,
    stakes: str = "normal",
    pipeline_path: Optional[List[str]] = None,
    context_summary: str = "",
    tri_witness_components: Optional[Dict[str, float]] = None,
    logger=None,
    ledger_path: Union[Path, str] = LedgerConfig().ledger_path,
    high_stakes: Optional[bool] = None,
    # GENIUS LAW telemetry (v35.13.0+)
    energy: Optional[float] = None,
    entropy: Optional[float] = None,
    include_genius_metrics: bool = True,
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

    # Map floor verdicts to canonical failure codes (partial; F9 explicitly included)
    floor_failures: List[str] = list(floors.reasons)
    if not floors.anti_hantu_ok:
        floor_failures.append("F9_AntiHantu")

    # Extract @EYE flags if report is provided
    eye_flags: Optional[List[Dict[str, Any]]] = None
    if eye_report is not None:
        alerts = getattr(eye_report, "alerts", None)
        if isinstance(alerts, list):
            eye_flags = []
            for alert in alerts:
                view_name = getattr(alert, "view_name", None)
                severity = getattr(alert, "severity", None)
                message = getattr(alert, "message", None)
                eye_flags.append(
                    {
                        "view": view_name,
                        "severity": getattr(severity, "value", str(severity))
                        if severity is not None
                        else None,
                        "message": message,
                    }
                )

    # ISO-8601 UTC timestamp (v35Ω schema)
    timestamp_iso = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )

    entry = {
        "ledger_version": "v35Ω",
        "timestamp": timestamp_iso,
        "job_id": job_id,
        "stakes": stakes,
        "pipeline_path": pipeline_path,
        "metrics": metrics.to_dict(),
        "verdict": verdict,
        "floor_failures": floor_failures,
        "sabar_reason": None,
        "tri_witness_components": tri_witness_components or {},
        "context_summary": context_summary,
        "query": query,
        "candidate_output": candidate_output,
        "eye_flags": eye_flags,
    }

    # GENIUS LAW telemetry (v35.13.0+) — optional, non-breaking
    if include_genius_metrics:
        try:
            from arifos_core.genius_metrics import evaluate_genius_law, DEFAULT_ENERGY

            genius_verdict = evaluate_genius_law(
                metrics,
                energy=energy if energy is not None else DEFAULT_ENERGY,
                entropy=entropy if entropy is not None else 0.0,
            )
            entry["genius_law"] = genius_verdict.to_dict()
        except ImportError:
            # Module not available — skip silently
            pass
        except Exception:
            # Don't break ledger logging if genius_metrics fails
            pass

    append_entry(ledger_path, entry)

    if logger:
        logger.info("CoolingLedgerEntry: %s", entry)

    return entry


def log_cooling_entry_v36_stub(
    *,
    job_id: str,
    verdict: str,
    metrics: "Metrics",
    query_hash: Optional[str] = None,
    response_hash: Optional[str] = None,
    genius_verdict: Optional["GeniusVerdict"] = None,
) -> Dict[str, Any]:
    """
    Build (but do not persist) a v36Ω-style Cooling Ledger entry.

    This is a **docs-layer stub** for future migrations to the
    `spec/cooling_ledger_v36.schema.json` shape. It does not write to
    disk or affect the existing v35Ic ledger. Callers can use this to
    inspect the v36Ω entry shape and compare against the runtime v35Ic
    entries without any behavioural change.

    Args:
        job_id: Identifier for this processing job.
        verdict: APEX PRIME verdict string.
        metrics: Metrics instance at verdict time.
        query_hash: Optional SHA-256 hash of the input query.
        response_hash: Optional SHA-256 hash of the sealed response.
        genius_verdict: Optional GeniusVerdict with Truth Polarity metadata.

    Returns:
        A dictionary shaped according to the v36Ω design schema, with
        some fields left optional/omitted when not available.
    """
    from arifos_core.metrics import Metrics as _Metrics

    if not isinstance(metrics, _Metrics):
        raise TypeError("metrics must be a Metrics instance")

    # ISO-8601 UTC timestamp (v36Ω design)
    timestamp_iso = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )

    # Truth Polarity from GeniusVerdict if available
    truth_polarity = "truth_light"
    if genius_verdict is not None:
        # Fallback-safe access; this is a stub and may evolve
        polarity = getattr(genius_verdict, "truth_polarity", None)
        if isinstance(polarity, str) and polarity:
            truth_polarity = polarity

    metrics_block: Dict[str, Any] = {
        "truth": metrics.truth,
        "delta_s": metrics.delta_s,
        "truth_polarity": truth_polarity,
        "peace2": metrics.peace_squared,
        "kappa_r": metrics.kappa_r,
        "omega0": metrics.omega_0,
        "amanah": "LOCK" if metrics.amanah else "BROKEN",
        "rasa": metrics.rasa,
        # Optional v36Ω fields (left unset for now):
        # "peace3": ...,
        # "psi_vitality": ...,
        # "echo_debt": ...,
    }

    entry_v36: Dict[str, Any] = {
        "ledger_version": "v36Omega",
        "timestamp": timestamp_iso,
        "query_hash": query_hash,
        "response_hash": response_hash,
        "metrics": metrics_block,
        "verdict": verdict,
        # Optional blocks (tri_witness, cce_audits, risk_signals, etc.)
        # can be added in future migrations.
    }

    return entry_v36


def log_cooling_entry_with_v36_telemetry(
    *,
    job_id: str,
    verdict: str,
    metrics: "Metrics",
    query: Optional[str] = None,
    candidate_output: Optional[str] = None,
    eye_report: Optional[Any] = None,
    stakes: str = "normal",
    pipeline_path: Optional[List[str]] = None,
    context_summary: str = "",
    tri_witness_components: Optional[Dict[str, float]] = None,
    logger=None,
    ledger_path: Union[Path, str] = LedgerConfig().ledger_path,
    high_stakes: Optional[bool] = None,
    # GENIUS LAW telemetry (v35.13.0+)
    energy: Optional[float] = None,
    entropy: Optional[float] = None,
    include_genius_metrics: bool = True,
    # v36Omega telemetry sink (design-only)
    v36_telemetry_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Dual logger: write v35Ic entry to disk and emit v36Omega telemetry.

    This is a safe, design-only bridge that reuses log_cooling_entry for
    the canonical v35Ic ledger entry, and then uses log_cooling_entry_v36_stub
    to build an in-memory v36Omega-shaped entry for telemetry/logging.

    Behaviour:
        - Always writes the v35Ic entry to `ledger_path` (unchanged).
        - Optionally computes a GeniusVerdict and v36 entry and passes it to
          `v36_telemetry_sink` or the provided logger.

    It does NOT change the on-disk schema or mutate existing ledger lines.
    """
    # First, log the canonical v35Ic entry
    entry_v35 = log_cooling_entry(
        job_id=job_id,
        verdict=verdict,
        metrics=metrics,
        query=query,
        candidate_output=candidate_output,
        eye_report=eye_report,
        stakes=stakes,
        pipeline_path=pipeline_path,
        context_summary=context_summary,
        tri_witness_components=tri_witness_components,
        logger=logger,
        ledger_path=ledger_path,
        high_stakes=high_stakes,
        energy=energy,
        entropy=entropy,
        include_genius_metrics=include_genius_metrics,
    )

    # Build query/response hashes for v36 telemetry
    query_hash: Optional[str] = None
    response_hash: Optional[str] = None
    if query is not None:
        query_hash = hashlib.sha256(str(query).encode("utf-8")).hexdigest()
    if candidate_output is not None:
        response_hash = hashlib.sha256(str(candidate_output).encode("utf-8")).hexdigest()

    # Reconstruct a minimal GeniusVerdict-like object from v35 entry if present
    genius_verdict_obj: Optional["GeniusVerdict"] = None
    genius_block = entry_v35.get("genius_law")
    if isinstance(genius_block, dict):
        try:
            # Lazy import; if structure changes, this fails safely
            from arifos_core.genius_metrics import GeniusVerdict as _GeniusVerdict

            genius_verdict_obj = _GeniusVerdict(**genius_block)
        except Exception:
            genius_verdict_obj = None

    # Build v36Omega-shaped telemetry entry
    try:
        v36_entry = log_cooling_entry_v36_stub(
            job_id=job_id,
            verdict=verdict,
            metrics=metrics,
            query_hash=query_hash,
            response_hash=response_hash,
            genius_verdict=genius_verdict_obj,
        )

        if v36_telemetry_sink is not None:
            v36_telemetry_sink(v36_entry)
        elif logger is not None:
            logger.info("CoolingLedgerEntryV36: %s", v36_entry)
    except Exception:
        # Telemetry must never break primary ledger logging
        if logger is not None:
            logger.exception("Failed to emit v36Omega Cooling Ledger telemetry entry")

    return entry_v35


__all__ = [
    "CoolingMetrics",
    "CoolingEntry",
    "CoolingLedger",
    "LedgerConfig",
    "append_entry",
    "verify_chain",
    "log_cooling_entry",
    "log_cooling_entry_v36_stub",
    "log_cooling_entry_with_v36_telemetry",
]
