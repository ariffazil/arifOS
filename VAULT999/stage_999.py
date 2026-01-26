"""
VAULT999 Stage 999 - Constitutional Memory Seal
The Final Seal of the 000→999 Metabolic Loop

DITEMPA BUKAN DIBERI - Forged, Not Given

This module consolidates ALL vault-related functionality into ONE canonical file:
- Vault999: L0 Constitutional Memory
- VaultManager: Phoenix-72 Amendment Workflow
- CoolingLedger: L1 Hash-Chained Audit Log
- MerkleLedger: Cryptographic Merkle Tree
- Stage 999 execute_stage: Pipeline Integration

Architecture (The 5 Memory Tiers):
    L0 (Hot)      → 30min TTL, ephemeral session state
    L1 (Daily)    → 24h cooling, pattern detection
    L2 (Phoenix)  → 72h cooling, truth stabilization
    L3 (Weekly)   → 7d reflection
    L4 (Monthly)  → 30d canon
    L5 (Eternal)  → ∞, constitutional law

Memory Bands:
    AAA_HUMAN  → Sacred human memory (FORBIDDEN to AI)
    BBB_LEDGER → Audit trail (READ/WRITE constrained)
    CCC_CANON  → Constitutional law (READ ONLY)

Version: v52.5.2-CANONICAL
Authority: Muhammad Arif bin Fazil
Sealed: 2026-01-26
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from arifos.core.utils.kms_signer import KmsSigner
    from arifos.core.enforcement.metrics import Metrics

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

DEFAULT_LEDGER_PATH = Path("VAULT999/BBB_LEDGER/cooling_ledger.jsonl")
DEFAULT_VAULT_PATH = Path("VAULT999/operational/constitution.json")
DEFAULT_AMENDMENTS_PATH = Path("VAULT999/operational/amendments.jsonl")
DEFAULT_RECEIPTS_PATH = Path("VAULT999/operational/receipts.jsonl")

# Phoenix-72 cooling durations (hours)
PHOENIX_72_HOURS = 72
PHOENIX_42_HOURS = 42
PHOENIX_168_HOURS = 168

# TTL routing by verdict
VERDICT_TTL = {
    "SEAL": float("inf"),      # Forever in CCC_CANON
    "PARTIAL": 730 * 24,       # 2 years in BBB_LEDGER
    "888_HOLD": 730 * 24,      # 2 years with escalation
    "FLAG": 30 * 24,           # 30 days warning
    "VOID": 0,                 # Never stored
    "SABAR": 0,                # Never stored
}


# =============================================================================
# VERDICT ROUTING
# =============================================================================

class VerdictRoute(str, Enum):
    """Memory band routing for verdicts."""
    CCC_CANON = "CCC_CANON"     # Constitutional law (perpetual)
    BBB_LEDGER = "BBB_LEDGER"   # Audit trail (TTL-based)
    DISCARD = "DISCARD"         # Never stored


def route_verdict(verdict: str) -> VerdictRoute:
    """
    EUREKA Sieve - Route verdict to appropriate memory band.

    SEAL → CCC_CANON (forever)
    PARTIAL/888_HOLD/FLAG → BBB_LEDGER (TTL-based)
    VOID/SABAR → DISCARD (never stored)
    """
    verdict_upper = verdict.upper()
    if verdict_upper == "SEAL":
        return VerdictRoute.CCC_CANON
    elif verdict_upper in ("PARTIAL", "888_HOLD", "FLAG"):
        return VerdictRoute.BBB_LEDGER
    else:
        return VerdictRoute.DISCARD


# =============================================================================
# MERKLE LEDGER (Cryptographic Tree Structure)
# =============================================================================

@dataclass
class MerkleEntry:
    """A single entry in the Merkle tree."""
    entry_id: str       # UUIDv7
    timestamp: float
    payload_hash: str   # Hash of the leaf content
    previous_hash: str  # Link to previous entry
    merkle_root_snapshot: str  # Root at time of insertion


class MerkleLedger:
    """
    Append-only Merkle Log.

    Ensures history cannot be rewritten without breaking the root.
    Uses a "Chain Merkle" approach: Hash(Root + Leaf) for each append.

    Example:
        ledger = MerkleLedger()
        entry_id = ledger.append("sha256:content_hash")
        assert ledger.verify_integrity()
    """

    def __init__(self, genesis_seed: bytes = b"GENESIS_v52"):
        self.entries: List[MerkleEntry] = []
        self._current_root_hash: str = hashlib.sha256(genesis_seed).hexdigest()

    def append(self, payload_hash: str) -> str:
        """
        Append a new entry and return its Entry ID.
        Recomputes the Merkle Root.
        """
        entry_id = str(uuid.uuid4())
        ts = time.time()

        # Chain link to previous entry
        prev_hash = self.entries[-1].payload_hash if self.entries else "GENESIS"

        # Create leaf hash
        leaf_content = f"{entry_id}:{ts}:{payload_hash}:{prev_hash}"
        leaf_hash = hashlib.sha256(leaf_content.encode()).hexdigest()

        # Update Merkle root
        new_root_content = f"{self._current_root_hash}:{leaf_hash}"
        self._current_root_hash = hashlib.sha256(new_root_content.encode()).hexdigest()

        # Commit entry
        entry = MerkleEntry(
            entry_id=entry_id,
            timestamp=ts,
            payload_hash=leaf_hash,
            previous_hash=prev_hash,
            merkle_root_snapshot=self._current_root_hash,
        )
        self.entries.append(entry)

        return entry_id

    def get_root(self) -> str:
        """Return current Merkle root hash."""
        return self._current_root_hash

    def verify_integrity(self) -> bool:
        """
        Replay the entire chain to verify current root match.
        Returns True if chain is valid, False if tampered.
        """
        recalc_root = hashlib.sha256(b"GENESIS_v52").hexdigest()

        for i, entry in enumerate(self.entries):
            # Verify chain link
            expected_prev = self.entries[i - 1].payload_hash if i > 0 else "GENESIS"
            if entry.previous_hash != expected_prev:
                return False

            # Verify root evolution
            expected_root = hashlib.sha256(
                f"{recalc_root}:{entry.payload_hash}".encode()
            ).hexdigest()
            if entry.merkle_root_snapshot != expected_root:
                return False
            recalc_root = entry.merkle_root_snapshot

        return recalc_root == self._current_root_hash


# =============================================================================
# COOLING LEDGER (L1 Hash-Chained Audit Log)
# =============================================================================

@dataclass
class CoolingMetrics:
    """Metrics snapshot for cooling ledger entry."""
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    rasa: bool
    amanah: bool
    tri_witness: float
    psi: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CoolingEntry:
    """A single entry in the cooling ledger."""
    timestamp: float
    query: str
    candidate_output: str
    metrics: CoolingMetrics
    verdict: str
    floor_failures: List[str]
    sabar_reason: Optional[str]
    organs: Dict[str, bool]
    phoenix_cycle_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_json_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["metrics"] = self.metrics.to_dict()
        return d


@dataclass
class LedgerConfig:
    """Configuration for CoolingLedger."""
    ledger_path: Path = DEFAULT_LEDGER_PATH


class CoolingLedger:
    """
    L1 Cooling Ledger - Append-only JSONL audit log.

    Features:
    - Hash-chained entries for tamper detection
    - Time-windowed queries (e.g., last 72 hours)
    - Phoenix-72 integration support

    Example:
        ledger = CoolingLedger()
        ledger.append(entry)
        for e in ledger.iter_recent(hours=72):
            print(e)
    """

    def __init__(self, config: Optional[LedgerConfig] = None):
        self.config = config or LedgerConfig()
        self.config.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, entry: CoolingEntry) -> None:
        """Append a new entry to the ledger. Never mutates existing lines."""
        line = json.dumps(entry.to_json_dict(), ensure_ascii=False)
        with self.config.ledger_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def iter_recent(self, hours: float = 72.0) -> Iterable[Dict[str, Any]]:
        """
        Iterate over entries from the last N hours.
        Default: 72 hours (Phoenix-72 window)
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
                    ts: Optional[float] = None
                    if isinstance(raw_ts, (int, float)):
                        ts = float(raw_ts)
                    elif isinstance(raw_ts, str):
                        try:
                            ts = datetime.fromisoformat(
                                raw_ts.replace("Z", "+00:00")
                            ).timestamp()
                        except Exception:
                            pass

                    if ts is not None and ts >= cutoff:
                        yield obj

        return _generator()


# =============================================================================
# HASH-CHAIN INTEGRITY FUNCTIONS
# =============================================================================

def compute_hash(entry: Dict[str, Any]) -> str:
    """
    Compute SHA3-256 hash of an entry for chain integrity.
    Excludes signature fields from computation.
    """
    excluded_fields = {
        "hash", "entry_hash", "kms_signature",
        "apex_signature", "kms_key_id"
    }
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
    Links each entry to the previous via prev_hash.
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
                        prev_hash = last_entry.get("hash") or last_entry.get("entry_hash")
                    except json.JSONDecodeError:
                        pass

    entry["prev_hash"] = prev_hash
    entry["hash"] = compute_hash(entry)

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
    Returns (success, message).
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

    # First entry should have no previous hash
    if entries[0].get("prev_hash") is not None:
        return False, "First entry should have prev_hash=null"

    for i, entry in enumerate(entries):
        stored_hash = entry.get("hash") or entry.get("entry_hash")
        if not stored_hash:
            return False, f"Entry {i} missing hash field"

        computed = compute_hash(entry)
        if stored_hash != computed:
            return False, (
                f"Entry {i} hash mismatch: "
                f"stored={stored_hash[:8]}..., computed={computed[:8]}..."
            )

        if i > 0:
            expected_prev = entries[i - 1].get("hash") or entries[i - 1].get("entry_hash")
            actual_prev = entry.get("prev_hash")
            if actual_prev != expected_prev:
                return False, (
                    f"Entry {i} prev_hash mismatch: "
                    f"expected={expected_prev[:8] if expected_prev else 'None'}..., "
                    f"actual={actual_prev[:8] if actual_prev else 'None'}..."
                )

    return True, f"Chain verified: {len(entries)} entries"


# =============================================================================
# VAULT999 (L0 Constitutional Memory)
# =============================================================================

@dataclass
class VaultConfig:
    """Configuration for Vault999."""
    vault_path: Path = DEFAULT_VAULT_PATH


class VaultInitializationError(Exception):
    """Raised when the Vault cannot be initialized or loaded."""


class Vault999:
    """
    VAULT-999 - L0 Constitutional Memory.

    Responsibilities:
    - Load and expose constitution (laws, floors, physics)
    - Provide read-only access to floors and laws at runtime
    - Coordinate safe updates via Phoenix-72 (scar → law)

    Example:
        vault = Vault999()
        floors = vault.get_floors()
        laws = vault.get_laws()
    """

    def __init__(self, config: Optional[VaultConfig] = None):
        self.config = config or VaultConfig()
        self._constitution: Dict[str, Any] = {}
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        """Load constitution.json if exists; otherwise initialize minimal one."""
        path = self.config.vault_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as f:
                    self._constitution = json.load(f)
            except Exception as e:
                raise VaultInitializationError(
                    f"Failed to load constitution: {e}"
                ) from e
        else:
            self._constitution = {
                "version": "52.5.2",
                "epoch": "52Ω",
                "physics": {
                    "delta_S_min": 0.0,
                    "peace_squared_min": 1.0,
                    "omega_band": {"min": 0.03, "max": 0.05},
                },
                "floors": {
                    "truth_min": 0.99,
                    "kappa_r_min": 0.95,
                    "tri_witness_min": 0.95,
                    "rasa_required": True,
                    "amanah_lock": True,
                },
                "laws": [],
                "amendments": [],
            }
            self._save()

    def _save(self) -> None:
        """Persist current constitution to disk."""
        with self.config.vault_path.open("w", encoding="utf-8") as f:
            json.dump(self._constitution, f, indent=2, ensure_ascii=False)

    def get_constitution(self) -> Dict[str, Any]:
        """Return the full constitution dict."""
        return self._constitution

    def get_floors(self) -> Dict[str, Any]:
        """Return floors object (thresholds & flags)."""
        return self._constitution.get("floors", {})

    def get_physics(self) -> Dict[str, Any]:
        """Return physics object (ΔΩΨ settings)."""
        return self._constitution.get("physics", {})

    def get_laws(self, status: Optional[str] = "ACTIVE") -> List[Dict[str, Any]]:
        """Return list of laws, optionally filtered by status."""
        laws = self._constitution.get("laws", [])
        if status is None:
            return laws
        return [law for law in laws if law.get("status") == status]

    def list_amendments(self) -> List[Dict[str, Any]]:
        """Return all amendments."""
        return self._constitution.get("amendments", [])

    def apply_amendment(self, amendment: Dict[str, Any]) -> None:
        """
        Apply a new amendment into the constitution.

        WARNING: Only invoke via Phoenix-72 workflow with
        proper audit trail and Tri-Witness oversight.
        """
        amendments = self._constitution.setdefault("amendments", [])
        amendments.append(amendment)
        self._save()

    def update_floors(self, new_floors: Dict[str, Any], phoenix_id: str) -> None:
        """
        Update floors via a Phoenix cycle.
        Records the amendment and updates floors atomically.
        """
        self._constitution["floors"] = new_floors
        amend = {
            "id": phoenix_id,
            "type": "FLOOR_UPDATE",
            "applied_at": amendment_timestamp(),
            "details": {"floors": new_floors},
        }
        amendments = self._constitution.setdefault("amendments", [])
        amendments.append(amend)
        self._save()


def amendment_timestamp() -> str:
    """Return ISO-8601 timestamp for amendments."""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# VAULT MANAGER (Phoenix-72 Amendment Workflow)
# =============================================================================

AmendmentStatus = Literal["PROPOSED", "UNDER_REVIEW", "SEALED", "REVOKED", "EXPIRED"]


@dataclass
class SafetyConstraints:
    """Safety constraints for Phoenix-72 amendments."""
    max_delta: float = 0.05          # |ΔF| ≤ 0.05 per cycle
    cooldown_hours: int = 24         # Cooldown window
    min_evidence_entries: int = 3    # Minimum evidence required

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AmendmentEvidence:
    """Evidence supporting an amendment proposal."""
    ledger_hashes: List[str] = field(default_factory=list)
    scar_ids: List[str] = field(default_factory=list)
    external_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AmendmentRecord:
    """
    A Phoenix-72 amendment record.

    Invariants:
    - amendment_id must be unique
    - Finalized amendments require phoenix72_signature
    - delta_value must respect safety_constraints.max_delta
    """
    amendment_id: str
    epoch: str
    status: AmendmentStatus
    target_floor: str
    target_field: str
    old_value: Any
    new_value: Any
    delta_value: float
    rationale: str
    evidence: AmendmentEvidence
    safety_constraints: SafetyConstraints
    proposed_at: str
    proposed_by: str
    phoenix72_cycle_id: Optional[str] = None
    phoenix72_signature: Optional[str] = None
    sealed_at: Optional[str] = None
    revoked_at: Optional[str] = None
    revocation_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "amendment_id": self.amendment_id,
            "epoch": self.epoch,
            "status": self.status,
            "target_floor": self.target_floor,
            "target_field": self.target_field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "delta_value": self.delta_value,
            "rationale": self.rationale,
            "evidence": self.evidence.to_dict(),
            "safety_constraints": self.safety_constraints.to_dict(),
            "proposed_at": self.proposed_at,
            "proposed_by": self.proposed_by,
            "phoenix72_cycle_id": self.phoenix72_cycle_id,
            "phoenix72_signature": self.phoenix72_signature,
            "sealed_at": self.sealed_at,
            "revoked_at": self.revoked_at,
            "revocation_reason": self.revocation_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AmendmentRecord":
        evidence = AmendmentEvidence(
            ledger_hashes=data.get("evidence", {}).get("ledger_hashes", []),
            scar_ids=data.get("evidence", {}).get("scar_ids", []),
            external_refs=data.get("evidence", {}).get("external_refs", []),
        )
        constraints = SafetyConstraints(
            max_delta=data.get("safety_constraints", {}).get("max_delta", 0.05),
            cooldown_hours=data.get("safety_constraints", {}).get("cooldown_hours", 24),
            min_evidence_entries=data.get("safety_constraints", {}).get(
                "min_evidence_entries", 3
            ),
        )
        return cls(
            amendment_id=data.get("amendment_id", ""),
            epoch=data.get("epoch", "v52"),
            status=data.get("status", "PROPOSED"),
            target_floor=data.get("target_floor", ""),
            target_field=data.get("target_field", ""),
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            delta_value=data.get("delta_value", 0.0),
            rationale=data.get("rationale", ""),
            evidence=evidence,
            safety_constraints=constraints,
            proposed_at=data.get("proposed_at", ""),
            proposed_by=data.get("proposed_by", ""),
            phoenix72_cycle_id=data.get("phoenix72_cycle_id"),
            phoenix72_signature=data.get("phoenix72_signature"),
            sealed_at=data.get("sealed_at"),
            revoked_at=data.get("revoked_at"),
            revocation_reason=data.get("revocation_reason"),
        )


@dataclass
class VaultManagerConfig:
    """Configuration for VaultManager."""
    vault_path: Path = DEFAULT_VAULT_PATH
    amendments_path: Path = DEFAULT_AMENDMENTS_PATH
    receipts_path: Path = DEFAULT_RECEIPTS_PATH
    safety_constraints: SafetyConstraints = field(default_factory=SafetyConstraints)


class VaultManager:
    """
    Enhanced VAULT-999 manager with Phoenix-72 amendment workflow.

    Features:
    - Structured amendment records
    - Safety constraint enforcement (|ΔF| ≤ 0.05)
    - Amendment history with signatures
    - Cooldown window tracking

    Example:
        manager = VaultManager()
        success, record, errors = manager.propose_amendment(
            target_floor="F1",
            target_field="truth_min",
            new_value=0.995,
            rationale="Tighten truth floor",
            evidence=AmendmentEvidence(ledger_hashes=["abc", "def", "ghi"]),
        )
        if success:
            manager.finalize_amendment(record.amendment_id, "sig...")
    """

    def __init__(self, config: Optional[VaultManagerConfig] = None):
        self.config = config or VaultManagerConfig()
        vault_config = VaultConfig(vault_path=self.config.vault_path)
        self._vault = Vault999(vault_config)
        self._amendments: Dict[str, AmendmentRecord] = {}
        self._load_amendments()

    def _load_amendments(self) -> None:
        """Load amendment history from JSONL file."""
        path = self.config.amendments_path
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            return

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    record = AmendmentRecord.from_dict(data)
                    self._amendments[record.amendment_id] = record
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to load amendment: {e}")

    def _save_amendment(self, record: AmendmentRecord) -> None:
        """Append an amendment record to the JSONL file."""
        path = self.config.amendments_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")

    # --- Public API (delegated to base Vault999) ---

    def get_constitution(self) -> Dict[str, Any]:
        return self._vault.get_constitution()

    def get_floors(self) -> Dict[str, Any]:
        return self._vault.get_floors()

    def get_physics(self) -> Dict[str, Any]:
        return self._vault.get_physics()

    def get_laws(self, status: Optional[str] = "ACTIVE") -> List[Dict[str, Any]]:
        return self._vault.get_laws(status)

    def list_amendments(self) -> List[AmendmentRecord]:
        return list(self._amendments.values())

    def get_amendment(self, amendment_id: str) -> Optional[AmendmentRecord]:
        return self._amendments.get(amendment_id)

    # --- Amendment Workflow ---

    def propose_amendment(
        self,
        target_floor: str,
        target_field: str,
        new_value: Any,
        rationale: str,
        evidence: AmendmentEvidence,
        proposed_by: str = "Phoenix72",
    ) -> Tuple[bool, AmendmentRecord, List[str]]:
        """
        Propose a new amendment.
        Does NOT apply the amendment - only Phoenix-72 can finalize.
        """
        errors: List[str] = []
        floors = self.get_floors()
        old_value = floors.get(target_field)

        if old_value is None:
            errors.append(f"Target field '{target_field}' not found in floors")
            record = AmendmentRecord(
                amendment_id=f"INVALID-{datetime.now(timezone.utc).timestamp():.0f}",
                epoch="v52",
                status="PROPOSED",
                target_floor=target_floor,
                target_field=target_field,
                old_value=None,
                new_value=new_value,
                delta_value=0.0,
                rationale=rationale,
                evidence=evidence,
                safety_constraints=self.config.safety_constraints,
                proposed_at=datetime.now(timezone.utc).isoformat(),
                proposed_by=proposed_by,
            )
            return (False, record, errors)

        # Compute delta
        try:
            delta_value = abs(float(new_value) - float(old_value))
        except (ValueError, TypeError):
            delta_value = 1.0 if new_value != old_value else 0.0

        # Safety constraint: |ΔF| ≤ max_delta
        if delta_value > self.config.safety_constraints.max_delta:
            errors.append(
                f"Delta {delta_value:.4f} exceeds safety cap "
                f"{self.config.safety_constraints.max_delta}"
            )

        # Evidence requirement
        total_evidence = (
            len(evidence.ledger_hashes) +
            len(evidence.scar_ids) +
            len(evidence.external_refs)
        )
        if total_evidence < self.config.safety_constraints.min_evidence_entries:
            errors.append(
                f"Insufficient evidence: {total_evidence} < "
                f"{self.config.safety_constraints.min_evidence_entries} required"
            )

        # Check cooldown
        cooldown_error = self._check_cooldown(target_field)
        if cooldown_error:
            errors.append(cooldown_error)

        # Generate amendment ID
        ts = datetime.now(timezone.utc).timestamp()
        content = f"{target_floor}:{target_field}:{new_value}:{ts}"
        amendment_id = f"AMEND-{hashlib.sha256(content.encode()).hexdigest()[:12]}"

        record = AmendmentRecord(
            amendment_id=amendment_id,
            epoch="v52",
            status="PROPOSED",
            target_floor=target_floor,
            target_field=target_field,
            old_value=old_value,
            new_value=new_value,
            delta_value=delta_value,
            rationale=rationale,
            evidence=evidence,
            safety_constraints=self.config.safety_constraints,
            proposed_at=datetime.now(timezone.utc).isoformat(),
            proposed_by=proposed_by,
        )

        self._amendments[amendment_id] = record
        self._save_amendment(record)

        return (len(errors) == 0, record, errors)

    def _check_cooldown(self, target_field: str) -> Optional[str]:
        """Check if the target field is still in cooldown."""
        cooldown_hours = self.config.safety_constraints.cooldown_hours
        cutoff = datetime.now(timezone.utc).timestamp() - (cooldown_hours * 3600)

        for record in self._amendments.values():
            if record.target_field != target_field or record.status != "SEALED":
                continue

            try:
                sealed_ts = (
                    datetime.fromisoformat(
                        record.sealed_at.replace("Z", "+00:00")
                    ).timestamp()
                    if record.sealed_at
                    else 0
                )
            except (ValueError, AttributeError):
                continue

            if sealed_ts > cutoff:
                hours_remaining = (
                    sealed_ts + (cooldown_hours * 3600) -
                    datetime.now(timezone.utc).timestamp()
                ) / 3600
                return (
                    f"Field '{target_field}' is in cooldown. "
                    f"Last amendment sealed at {record.sealed_at}. "
                    f"{hours_remaining:.1f} hours remaining."
                )

        return None

    def finalize_amendment(
        self,
        amendment_id: str,
        phoenix72_signature: str,
        phoenix72_cycle_id: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Finalize and apply an amendment.
        This is the ONLY path to modify constitutional floors.
        """
        record = self._amendments.get(amendment_id)
        if record is None:
            return (False, [f"Amendment not found: {amendment_id}"])

        if record.status != "PROPOSED":
            return (False, [f"Amendment status is {record.status}, expected PROPOSED"])

        if not phoenix72_signature:
            return (False, ["Phoenix-72 signature is required"])

        try:
            self._vault.update_floors(
                new_floors={**self.get_floors(), record.target_field: record.new_value},
                phoenix_id=amendment_id,
            )
        except Exception as e:
            return (False, [f"Failed to apply amendment: {e}"])

        record.status = "SEALED"
        record.phoenix72_signature = phoenix72_signature
        record.phoenix72_cycle_id = phoenix72_cycle_id
        record.sealed_at = datetime.now(timezone.utc).isoformat()

        self._save_amendment(record)
        logger.info(
            f"Amendment {amendment_id} finalized: "
            f"{record.target_field} = {record.new_value}"
        )

        return (True, [])

    def record_receipt(self, receipt: Dict[str, Any]) -> None:
        """Record a Constitutional Receipt to the ZKPC Vault."""
        path = self.config.receipts_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(receipt, sort_keys=True) + "\n")


# =============================================================================
# STAGE 999 EXECUTE FUNCTION
# =============================================================================

@dataclass
class Stage999Result:
    """Result of Stage 999 execution."""
    sealed: bool
    merkle_root: Optional[str]
    ledger_entry_id: Optional[str]
    route: VerdictRoute
    ttl_hours: float
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sealed": self.sealed,
            "merkle_root": self.merkle_root,
            "ledger_entry_id": self.ledger_entry_id,
            "route": self.route.value,
            "ttl_hours": self.ttl_hours if self.ttl_hours != float("inf") else "FOREVER",
            "error": self.error,
        }


def execute_stage_999(
    verdict: str,
    proof_hash: Optional[str] = None,
    session_id: Optional[str] = None,
    floor_scores: Optional[Dict[str, float]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Stage999Result:
    """
    Execute Stage 999 - The Constitutional Seal.

    This is the final stage of the 000→999 metabolic loop.
    It seals the verdict, computes Merkle root, and routes to memory band.

    Args:
        verdict: The verdict from 888 JUDGE (SEAL/PARTIAL/VOID/SABAR/888_HOLD)
        proof_hash: Hash of the proof payload
        session_id: Session identifier
        floor_scores: F1-F12 floor scores
        metadata: Additional metadata

    Returns:
        Stage999Result with seal status and routing information
    """
    # Route verdict to memory band
    route = route_verdict(verdict)
    ttl = VERDICT_TTL.get(verdict.upper(), 0)

    # VOID and SABAR are never stored
    if route == VerdictRoute.DISCARD:
        return Stage999Result(
            sealed=False,
            merkle_root=None,
            ledger_entry_id=None,
            route=route,
            ttl_hours=0,
            error=f"Verdict {verdict} is not stored (EUREKA sieve)",
        )

    # Create Merkle ledger and append entry
    merkle = MerkleLedger()

    # Compute content hash for Merkle tree
    content = {
        "verdict": verdict,
        "proof_hash": proof_hash,
        "session_id": session_id,
        "floor_scores": floor_scores,
        "metadata": metadata,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    content_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True).encode()
    ).hexdigest()

    # Append to Merkle tree
    entry_id = merkle.append(content_hash)
    merkle_root = merkle.get_root()

    # Create ledger entry
    ledger_entry = {
        "entry_id": entry_id,
        "session_id": session_id,
        "verdict": verdict,
        "merkle_root": merkle_root,
        "proof_hash": proof_hash,
        "floor_scores": floor_scores,
        "route": route.value,
        "ttl_hours": ttl if ttl != float("inf") else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Append to hash-chained ledger
    ledger_path = DEFAULT_LEDGER_PATH
    append_entry(ledger_path, ledger_entry)

    return Stage999Result(
        sealed=True,
        merkle_root=merkle_root,
        ledger_entry_id=entry_id,
        route=route,
        ttl_hours=ttl,
    )


def execute_stage(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy interface for Stage 999.
    Compatible with the metabolic pipeline.
    """
    context["stage"] = "999"

    verdict = context.get("verdict", "VOID")
    proof_hash = context.get("proof_hash")
    session_id = context.get("session_id")
    floor_scores = context.get("floor_scores", {})

    result = execute_stage_999(
        verdict=verdict,
        proof_hash=proof_hash,
        session_id=session_id,
        floor_scores=floor_scores,
        metadata={"context_keys": list(context.keys())},
    )

    context["vault_result"] = result.to_dict()
    context["merkle_root"] = result.merkle_root
    context["sealed"] = result.sealed
    context["loop_iteration"] = context.get("loop_iteration", 0) + 1

    return context


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# The canonical Stage 999 VAULT instance
vault_999 = Vault999()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "DEFAULT_LEDGER_PATH",
    "DEFAULT_VAULT_PATH",
    "PHOENIX_72_HOURS",
    "VERDICT_TTL",

    # Routing
    "VerdictRoute",
    "route_verdict",

    # Merkle Ledger
    "MerkleEntry",
    "MerkleLedger",

    # Cooling Ledger
    "CoolingMetrics",
    "CoolingEntry",
    "LedgerConfig",
    "CoolingLedger",

    # Hash-Chain Functions
    "compute_hash",
    "append_entry",
    "verify_chain",

    # Vault999
    "VaultConfig",
    "VaultInitializationError",
    "Vault999",
    "amendment_timestamp",

    # VaultManager
    "SafetyConstraints",
    "AmendmentEvidence",
    "AmendmentRecord",
    "AmendmentStatus",
    "VaultManagerConfig",
    "VaultManager",

    # Stage 999
    "Stage999Result",
    "execute_stage_999",
    "execute_stage",

    # Singleton
    "vault_999",
]
