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

DEFAULT_LEDGER_PATH = Path("cooling_ledger") / "L1_cooling_ledger.jsonl"

if TYPE_CHECKING:
    from arifos_core.utils.kms_signer import KmsSigner
    from arifos_core.enforcement.metrics import Metrics
    from arifos_core.enforcement.genius_metrics import GeniusVerdict


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
    ledger_path: Path = DEFAULT_LEDGER_PATH


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
                            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).timestamp()
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
            return (
                False,
                f"Entry {i} hash mismatch: stored={stored_hash[:8]}..., computed={computed_hash[:8]}...",
            )

        if i > 0:
            expected_prev_hash = entries[i - 1].get("hash")
            actual_prev_hash = entry.get("prev_hash")
            if actual_prev_hash != expected_prev_hash:
                return (
                    False,
                    f"Entry {i} prev_hash mismatch: expected={expected_prev_hash[:8]}..., actual={actual_prev_hash[:8] if actual_prev_hash else 'null'}...",
                )

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
    ledger_path: Union[Path, str] = DEFAULT_LEDGER_PATH,
    high_stakes: Optional[bool] = None,
    # GENIUS LAW telemetry (v35.13.0+)
    energy: Optional[float] = None,
    entropy: Optional[float] = None,
    include_genius_metrics: bool = True,
    # Codex CLI metadata (optional, non-breaking)
    source: Optional[str] = None,
    task_type: Optional[str] = None,
    task_description: Optional[str] = None,
    scope: Optional[str] = None,
    codex_audit: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Append a hash-chained Cooling Ledger entry and return the entry dict."""

    # v42: Use new locations
    from arifos_core.system.apex_prime import check_floors, normalize_verdict_code
    from arifos_core.enforcement.metrics import Metrics

    if pipeline_path is None:
        pipeline_path = []

    if not isinstance(metrics, Metrics):
        raise TypeError("metrics must be a Metrics instance")

    # Normalize verdict using SSoT
    verdict = normalize_verdict_code(verdict)

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
    timestamp_iso = (
        datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
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
            from arifos_core.enforcement.genius_metrics import evaluate_genius_law, DEFAULT_ENERGY

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

    # Optional Codex CLI metadata (non-breaking additions)
    if source is not None:
        entry["source"] = source
    if task_type is not None:
        entry["task_type"] = task_type
    if task_description:
        entry["task_description"] = task_description
    if scope is not None:
        entry["scope"] = scope
    if codex_audit is not None:
        entry["codex_audit"] = codex_audit

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
    from arifos_core.enforcement.metrics import Metrics as _Metrics

    if not isinstance(metrics, _Metrics):
        raise TypeError("metrics must be a Metrics instance")

    # ISO-8601 UTC timestamp (v36Ω design)
    timestamp_iso = (
        datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
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
            from arifos_core.enforcement.genius_metrics import GeniusVerdict as _GeniusVerdict

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


# =============================================================================
# V37 EXTENSIONS — HEAD STATE, ROTATION, FAIL-OPEN HARDENING
# =============================================================================

import logging
import shutil

_ledger_logger = logging.getLogger(__name__)


@dataclass
class LedgerConfigV37:
    """
    Enhanced ledger config for v37 per COOLING_LEDGER_INTEGRITY_v36.3O.md.

    Adds:
    - head_state.json tracking for crash recovery
    - rotation thresholds for hot segment
    - fail behavior configuration
    """

    ledger_path: Path = DEFAULT_LEDGER_PATH
    head_state_path: Path = Path("runtime/vault_999/head_state.json")
    archive_path: Path = Path("runtime/vault_999/archive/")
    hot_segment_days: int = 7  # TODO(Arif): confirm
    hot_segment_max_entries: int = 10000  # TODO(Arif): confirm
    fail_behavior: str = "SABAR_HOLD_WITH_LOG"  # Options: SABAR_HOLD_WITH_LOG, SILENT_FAIL, RAISE


@dataclass
class HeadState:
    """
    Head state for crash recovery per COOLING_LEDGER_INTEGRITY canon.

    Tracks the latest entry hash for fast chain verification on startup.
    """

    last_entry_hash: Optional[str] = None
    entry_count: int = 0
    last_timestamp: Optional[str] = None
    epoch: str = "v37"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "last_entry_hash": self.last_entry_hash,
            "entry_count": self.entry_count,
            "last_timestamp": self.last_timestamp,
            "epoch": self.epoch,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HeadState":
        return cls(
            last_entry_hash=data.get("last_entry_hash"),
            entry_count=data.get("entry_count", 0),
            last_timestamp=data.get("last_timestamp"),
            epoch=data.get("epoch", "v37"),
        )


class CoolingLedgerV37:
    """
    Enhanced Cooling Ledger for v37 with:
    - head_state.json tracking for crash recovery
    - Hot segment rotation
    - Fail-open hardening (SABAR/HOLD + logging, not silent SEAL)

    Implements:
    - archive/versions/v36_3_omega/v36.3O/spec/cooling_ledger_entry_spec_v36.3O.json
    - archive/versions/v36_3_omega/v36.3O/canon/COOLING_LEDGER_INTEGRITY_v36.3O.md

    Usage:
        ledger = CoolingLedgerV37()
        result = ledger.append_v37(entry)
        if not result.success:
            # Handle failure - trigger SABAR/HOLD
            logger.error(f"Ledger write failed: {result.error}")
    """

    def __init__(self, config: Optional[LedgerConfigV37] = None):
        self.config = config or LedgerConfigV37()
        self.config.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self.config.archive_path.mkdir(parents=True, exist_ok=True)

        # Load head state
        self._head_state = self._load_head_state()

    def _load_head_state(self) -> HeadState:
        """Load head state from JSON file."""
        path = self.config.head_state_path
        if not path.exists():
            return HeadState()

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return HeadState.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            _ledger_logger.warning(f"Failed to load head_state.json: {e}")
            return HeadState()

    def _save_head_state(self) -> bool:
        """Save head state to JSON file."""
        try:
            path = self.config.head_state_path
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(self._head_state.to_dict(), f, indent=2)
            return True
        except IOError as e:
            _ledger_logger.error(f"Failed to save head_state.json: {e}")
            return False

    def get_head_state(self) -> HeadState:
        """Return current head state."""
        return self._head_state

    @dataclass
    class AppendResult:
        """Result of an append operation."""

        success: bool
        entry_hash: Optional[str] = None
        error: Optional[str] = None
        triggered_rotation: bool = False

    def append_v37(
        self,
        entry: Dict[str, Any],
        kms_signer: Optional["KmsSigner"] = None,
    ) -> "CoolingLedgerV37.AppendResult":
        """
        Append an entry with v37 features (head state, fail hardening).

        On IO error:
        - If fail_behavior == "SABAR_HOLD_WITH_LOG": returns failure result (caller should SABAR/HOLD)
        - If fail_behavior == "RAISE": raises exception
        - If fail_behavior == "SILENT_FAIL": logs warning and returns failure

        Never silently returns success if write failed.

        Args:
            entry: Entry dictionary to append
            kms_signer: Optional KmsSigner for signatures

        Returns:
            AppendResult with success status and details
        """
        path = self.config.ledger_path

        try:
            # Get previous hash from head state (fast) or file (fallback)
            prev_hash = self._head_state.last_entry_hash

            # If no head state, verify from file
            if prev_hash is None and path.exists() and path.stat().st_size > 0:
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

            # Set chain fields
            entry["prev_hash"] = prev_hash
            entry["entry_hash"] = _compute_hash(entry)

            # Sign if signer provided
            if kms_signer is not None:
                hash_bytes = bytes.fromhex(entry["entry_hash"])
                signature_b64 = kms_signer.sign_hash(hash_bytes)
                entry["apex_signature"] = signature_b64

            # Write entry
            line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
            with path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

            # Update head state
            self._head_state.last_entry_hash = entry["entry_hash"]
            self._head_state.entry_count += 1
            self._head_state.last_timestamp = entry.get("timestamp")

            # Persist head state
            if not self._save_head_state():
                _ledger_logger.warning("Entry written but head_state.json update failed")

            # Check for rotation
            triggered_rotation = False
            if self._should_rotate():
                self._rotate_hot_segment()
                triggered_rotation = True

            return self.AppendResult(
                success=True,
                entry_hash=entry["entry_hash"],
                triggered_rotation=triggered_rotation,
            )

        except IOError as e:
            error_msg = f"Ledger IO error: {e}"
            _ledger_logger.error(error_msg)

            if self.config.fail_behavior == "RAISE":
                raise

            return self.AppendResult(success=False, error=error_msg)

        except Exception as e:
            error_msg = f"Unexpected ledger error: {e}"
            _ledger_logger.error(error_msg)

            if self.config.fail_behavior == "RAISE":
                raise

            return self.AppendResult(success=False, error=error_msg)

    def _should_rotate(self) -> bool:
        """Check if hot segment should be rotated."""
        # Check entry count
        if self._head_state.entry_count >= self.config.hot_segment_max_entries:
            return True

        # Check age of oldest entry
        # (simplified - in production would track first_timestamp)
        return False

    def _rotate_hot_segment(self) -> bool:
        """
        Rotate the hot segment to warm archive.

        Creates a timestamped copy in archive/ and clears the hot segment.
        """
        try:
            path = self.config.ledger_path
            if not path.exists():
                return True

            # Create archive filename
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            archive_name = f"cooling_ledger_{ts}.jsonl"
            archive_path = self.config.archive_path / archive_name

            # Copy to archive
            shutil.copy2(path, archive_path)

            # Clear hot segment
            path.write_text("")

            # Reset head state
            self._head_state = HeadState()
            self._save_head_state()

            _ledger_logger.info(f"Rotated hot segment to {archive_path}")
            return True

        except IOError as e:
            _ledger_logger.error(f"Failed to rotate hot segment: {e}")
            return False

    def verify_chain_quick(self) -> Tuple[bool, str]:
        """
        Quick chain verification using head state.

        Only checks that head_state.json matches the actual last entry.
        For full verification, use verify_chain().
        """
        path = self.config.ledger_path
        if not path.exists():
            if self._head_state.entry_count == 0:
                return True, "Empty ledger (valid)"
            return False, "Head state shows entries but ledger missing"

        # Get actual last hash
        try:
            with path.open("r", encoding="utf-8") as f:
                lines = f.readlines()
                if not lines:
                    if self._head_state.entry_count == 0:
                        return True, "Empty ledger (valid)"
                    return False, "Head state shows entries but ledger empty"

                last_line = lines[-1].strip()
                if not last_line:
                    return False, "Last line is empty"

                last_entry = json.loads(last_line)
                actual_hash = last_entry.get("entry_hash") or last_entry.get("hash")

        except (json.JSONDecodeError, IOError) as e:
            return False, f"Failed to read last entry: {e}"

        # Compare with head state
        if actual_hash != self._head_state.last_entry_hash:
            return False, (
                f"Head state mismatch: expected {self._head_state.last_entry_hash[:8] if self._head_state.last_entry_hash else 'None'}..., "
                f"actual {actual_hash[:8] if actual_hash else 'None'}..."
            )

        return True, f"Quick verify passed: {self._head_state.entry_count} entries"

    def iter_recent(self, hours: float = 72.0) -> Iterable[Dict[str, Any]]:
        """
        Iterate over entries from the last N hours.

        Delegates to base CoolingLedger behavior.
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
                    ts: Optional[float]
                    if isinstance(raw_ts, (int, float)):
                        ts = float(raw_ts)
                    elif isinstance(raw_ts, str):
                        try:
                            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).timestamp()
                        except Exception:
                            ts = None
                    else:
                        ts = None

                    if ts is not None and ts >= cutoff:
                        yield obj

        return _generator()


def log_cooling_entry_v37(
    *,
    job_id: str,
    verdict: str,
    metrics: "Metrics",
    query: Optional[str] = None,
    candidate_output: Optional[str] = None,
    stakes_class: str = "CLASS_A",
    floor_warnings: Optional[List[str]] = None,
    tri_witness_components: Optional[Dict[str, float]] = None,
    cce_audits: Optional[Dict[str, str]] = None,
    truth_polarity: Optional[str] = None,
    phoenix_cycle_id: Optional[str] = None,
    eureka_receipt_id: Optional[str] = None,
    scar_ids: Optional[List[str]] = None,
    ledger: Optional[CoolingLedgerV37] = None,
    logger: Optional[Any] = None,
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Log a v37 Cooling Ledger entry per cooling_ledger_entry_spec_v36.3O.json.

    Returns:
        Tuple of (success, entry_dict, error_message)
        If success is False, caller should trigger SABAR/HOLD.
    """
    from arifos_core.enforcement.metrics import Metrics as _Metrics

    if not isinstance(metrics, _Metrics):
        return (False, {}, "metrics must be a Metrics instance")

    # Compute query/response hashes
    query_hash = hashlib.sha256(str(query or "").encode()).hexdigest()
    response_hash = hashlib.sha256(str(candidate_output or "").encode()).hexdigest()

    # ISO-8601 UTC timestamp
    timestamp_iso = (
        datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    )

    # Build metrics block per spec
    metrics_block: Dict[str, Any] = {
        "truth": metrics.truth,
        "delta_s": metrics.delta_s,
        "peace_squared": metrics.peace_squared,
        "kappa_r": metrics.kappa_r,
        "omega_0": metrics.omega_0,
        "amanah": "LOCK" if metrics.amanah else "BROKEN",
        "rasa": metrics.rasa,
        "tri_witness": metrics.tri_witness,
        "anti_hantu": getattr(metrics, "anti_hantu", True),
    }

    # Add derived metrics if available
    try:
        from arifos_core.enforcement.genius_metrics import evaluate_genius_law, DEFAULT_ENERGY

        genius = evaluate_genius_law(metrics, energy=DEFAULT_ENERGY, entropy=0.0)
        metrics_block["psi"] = genius.psi
        metrics_block["G"] = genius.G
        metrics_block["C_dark"] = genius.C_dark
    except Exception:
        pass

    entry: Dict[str, Any] = {
        "ledger_version": "v36.3Omega",
        "timestamp": timestamp_iso,
        "query_hash": query_hash,
        "response_hash": response_hash,
        "metrics": metrics_block,
        "verdict": verdict,
        "class": stakes_class,
        "floor_warnings": floor_warnings,
        "phoenix_cycle_id": phoenix_cycle_id,
        "eureka_receipt_id": eureka_receipt_id,
        "scar_ids": scar_ids,
    }

    # Optional blocks
    if tri_witness_components:
        entry["tri_witness_detail"] = tri_witness_components

    if truth_polarity:
        entry["truth_polarity"] = truth_polarity

    if cce_audits:
        entry["cce_audits"] = cce_audits

    # Append via v37 ledger
    if ledger is None:
        ledger = CoolingLedgerV37()

    result = ledger.append_v37(entry)

    if logger:
        if result.success:
            logger.info(f"CoolingLedgerV37: entry_hash={result.entry_hash[:8]}...")
        else:
            logger.error(f"CoolingLedgerV37 FAILED: {result.error}")

    return (result.success, entry, result.error)


__all__ = [
    # v35 classes
    "CoolingMetrics",
    "CoolingEntry",
    "CoolingLedger",
    "LedgerConfig",
    "append_entry",
    "verify_chain",
    "log_cooling_entry",
    "log_cooling_entry_v36_stub",
    "log_cooling_entry_with_v36_telemetry",
    # v37 extensions
    "LedgerConfigV37",
    "HeadState",
    "CoolingLedgerV37",
    "log_cooling_entry_v37",
]
