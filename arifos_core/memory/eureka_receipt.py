"""
eureka_receipt.py — EUREKA zkPC Receipt Manager for arifOS v37

Implements zkPC (Zero-Knowledge Proof of Cognition) receipts per:
- archive/versions/v36_3_omega/v36.3O/canon/VAULT999_ARCHITECTURE_v36.3O.md (L4 layer)
- archive/versions/v36_3_omega/v36.3O/spec/eureka_receipt_spec_v36.3O.json

Key concepts:
- EUREKA receipts anchor governed cognition without exposing internal reasoning
- Each receipt proves floor checks occurred without revealing actual values
- Hash-chained for integrity (like a blockchain of cognition proofs)
- Only SEAL/PARTIAL verdicts generate receipts (VOID/SABAR do not)

This is a STUB implementation using HMAC-SHA256 for signatures.
Production v37+ should use hardware-backed keys and actual zkSNARK proofs.

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from arifos_core.enforcement.metrics import Metrics


logger = logging.getLogger(__name__)


# =============================================================================
# TYPES
# =============================================================================

Stakeholder = Literal["user", "system", "earth", "third_party", "future"]
StakesClass = Literal["CLASS_A", "CLASS_B"]
ReceiptVerdict = Literal["SEAL", "PARTIAL"]


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class CareScope:
    """
    Who/what this cognition was caring for.

    Fields:
        who: List of stakeholders in scope
        risk_cooled: Primary risk that was governed
        harm_prevented: Description of harm prevented (optional)
    """
    who: List[Stakeholder]
    risk_cooled: str
    harm_prevented: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "who": self.who,
            "risk_cooled": self.risk_cooled,
            "harm_prevented": self.harm_prevented,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CareScope":
        return cls(
            who=data.get("who", ["user"]),
            risk_cooled=data.get("risk_cooled", "unspecified"),
            harm_prevented=data.get("harm_prevented"),
        )


@dataclass
class FloorProofs:
    """
    Per-floor proof status.

    Each boolean indicates that the floor was evaluated (not the result).
    This proves governance occurred without revealing actual metric values.
    """
    F1_truth: bool = True
    F2_delta_s: bool = True
    F3_peace_squared: bool = True
    F4_kappa_r: bool = True
    F5_omega_0: bool = True
    F6_amanah: bool = True
    F7_rasa: bool = True
    F8_tri_witness: bool = True
    F9_anti_hantu: bool = True

    def to_dict(self) -> Dict[str, bool]:
        return {
            "F1_truth": self.F1_truth,
            "F2_delta_s": self.F2_delta_s,
            "F3_peace_squared": self.F3_peace_squared,
            "F4_kappa_r": self.F4_kappa_r,
            "F5_omega_0": self.F5_omega_0,
            "F6_amanah": self.F6_amanah,
            "F7_rasa": self.F7_rasa,
            "F8_tri_witness": self.F8_tri_witness,
            "F9_anti_hantu": self.F9_anti_hantu,
        }

    def all_checked(self) -> bool:
        """Return True if all floors were evaluated."""
        return all([
            self.F1_truth, self.F2_delta_s, self.F3_peace_squared,
            self.F4_kappa_r, self.F5_omega_0, self.F6_amanah,
            self.F7_rasa, self.F8_tri_witness, self.F9_anti_hantu,
        ])


@dataclass
class CCEProofs:
    """
    CCE (Crown Cognitive Equation) audit proofs.

    Proves that the Delta/Omega/Psi/Phi computations were performed.
    """
    delta_p: bool = True
    omega_p: bool = True
    psi_p: bool = True
    phi_p: bool = False  # Phi (Paradox) is optional

    def to_dict(self) -> Dict[str, bool]:
        return {
            "delta_p": self.delta_p,
            "omega_p": self.omega_p,
            "psi_p": self.psi_p,
            "phi_p": self.phi_p,
        }


@dataclass
class TriWitnessScores:
    """
    Tri-Witness scores at the time of cognition.

    These are the actual scores (not proofs), included for transparency.
    In a true zkPC system, these would be committed but hidden.
    """
    human: float = 1.0
    ai: float = 1.0
    earth: float = 1.0
    consensus: float = 1.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "human": self.human,
            "ai": self.ai,
            "earth": self.earth,
            "consensus": self.consensus,
        }

    @classmethod
    def from_metrics(cls, metrics: "Metrics") -> "TriWitnessScores":
        """Extract Tri-Witness scores from Metrics."""
        # Default to full scores; in production these would come from
        # actual witness consensus mechanisms
        return cls(
            human=1.0,
            ai=1.0,
            earth=1.0,
            consensus=getattr(metrics, "tri_witness", 1.0),
        )


@dataclass
class EurekaReceipt:
    """
    A EUREKA zkPC receipt per eureka_receipt_spec_v36.3O.json.

    Anchors governed cognition without exposing internal reasoning.
    Only SEAL/PARTIAL verdicts generate receipts.
    """
    receipt_id: str
    timestamp: str
    event_id: str  # SHA-256 of linked Cooling Ledger entry
    zkpc_hash: str  # SHA-256 of zkPC payload
    care_scope: CareScope
    floor_proofs: FloorProofs
    verdict: ReceiptVerdict
    stakes_class: StakesClass
    apex_signature: str
    merkle_root: str
    previous_receipt_hash: Optional[str]
    receipt_hash: str
    cce_proofs: Optional[CCEProofs] = None
    tri_witness: Optional[TriWitnessScores] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "event_id": self.event_id,
            "zkpc_hash": self.zkpc_hash,
            "care_scope": self.care_scope.to_dict(),
            "floor_proofs": self.floor_proofs.to_dict(),
            "verdict": self.verdict,
            "class": self.stakes_class,
            "apex_signature": self.apex_signature,
            "merkle_root": self.merkle_root,
            "previous_receipt_hash": self.previous_receipt_hash,
            "receipt_hash": self.receipt_hash,
        }

        if self.cce_proofs:
            data["cce_proofs"] = self.cce_proofs.to_dict()

        if self.tri_witness:
            data["tri_witness"] = self.tri_witness.to_dict()

        if self.extra:
            data["extra"] = self.extra

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EurekaReceipt":
        care_scope = CareScope.from_dict(data.get("care_scope", {}))

        floor_proofs_data = data.get("floor_proofs", {})
        floor_proofs = FloorProofs(
            F1_truth=floor_proofs_data.get("F1_truth", True),
            F2_delta_s=floor_proofs_data.get("F2_delta_s", True),
            F3_peace_squared=floor_proofs_data.get("F3_peace_squared", True),
            F4_kappa_r=floor_proofs_data.get("F4_kappa_r", True),
            F5_omega_0=floor_proofs_data.get("F5_omega_0", True),
            F6_amanah=floor_proofs_data.get("F6_amanah", True),
            F7_rasa=floor_proofs_data.get("F7_rasa", True),
            F8_tri_witness=floor_proofs_data.get("F8_tri_witness", True),
            F9_anti_hantu=floor_proofs_data.get("F9_anti_hantu", True),
        )

        cce_proofs = None
        if "cce_proofs" in data:
            cce_data = data["cce_proofs"]
            cce_proofs = CCEProofs(
                delta_p=cce_data.get("delta_p", True),
                omega_p=cce_data.get("omega_p", True),
                psi_p=cce_data.get("psi_p", True),
                phi_p=cce_data.get("phi_p", False),
            )

        tri_witness = None
        if "tri_witness" in data:
            tw_data = data["tri_witness"]
            tri_witness = TriWitnessScores(
                human=tw_data.get("human", 1.0),
                ai=tw_data.get("ai", 1.0),
                earth=tw_data.get("earth", 1.0),
                consensus=tw_data.get("consensus", 1.0),
            )

        return cls(
            receipt_id=data.get("receipt_id", ""),
            timestamp=data.get("timestamp", ""),
            event_id=data.get("event_id", ""),
            zkpc_hash=data.get("zkpc_hash", ""),
            care_scope=care_scope,
            floor_proofs=floor_proofs,
            verdict=data.get("verdict", "SEAL"),
            stakes_class=data.get("class", "CLASS_A"),
            apex_signature=data.get("apex_signature", ""),
            merkle_root=data.get("merkle_root", ""),
            previous_receipt_hash=data.get("previous_receipt_hash"),
            receipt_hash=data.get("receipt_hash", ""),
            cce_proofs=cce_proofs,
            tri_witness=tri_witness,
            extra=data.get("extra", {}),
        )


# =============================================================================
# EUREKA RECEIPT MANAGER
# =============================================================================

@dataclass
class EurekaConfig:
    """Configuration for EUREKA receipt manager."""
    receipts_path: Path = Path("runtime/vault_999/eureka_receipts.jsonl")
    merkle_state_path: Path = Path("runtime/vault_999/eureka_merkle_state.json")
    # HMAC key for signing (stub - in production use KMS)
    # TODO(Arif): Replace with hardware-backed keys in v37+
    hmac_key: bytes = field(default_factory=lambda: b"eureka_apex_stub_key_v37")


@dataclass
class MerkleState:
    """
    Merkle tree state for EUREKA receipt chain.

    In production, this would be a proper Merkle tree.
    This stub maintains just the root hash updated incrementally.
    """
    merkle_root: str = "0" * 64
    receipt_count: int = 0
    last_receipt_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "merkle_root": self.merkle_root,
            "receipt_count": self.receipt_count,
            "last_receipt_hash": self.last_receipt_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MerkleState":
        return cls(
            merkle_root=data.get("merkle_root", "0" * 64),
            receipt_count=data.get("receipt_count", 0),
            last_receipt_hash=data.get("last_receipt_hash"),
        )


class EurekaReceiptManager:
    """
    Manager for EUREKA zkPC receipts (L4 layer of VAULT-999).

    Responsibilities:
    - Generate receipts for SEAL/PARTIAL verdicts
    - Maintain hash chain of receipts
    - Update Merkle root
    - Sign receipts with APEX PRIME authority

    This is a STUB implementation. Production v37+ should:
    - Use actual zkSNARK proofs
    - Use hardware-backed signing keys
    - Integrate with external transparency logs (e.g., Rekor)

    Usage:
        manager = EurekaReceiptManager()

        # Generate receipt for a governed cognition event
        receipt = manager.generate_receipt(
            ledger_entry_hash="abc123...",
            verdict="SEAL",
            stakes_class="CLASS_A",
            care_scope=CareScope(who=["user"], risk_cooled="misinformation"),
            metrics=metrics,
        )

        # Verify a receipt
        valid, error = manager.verify_receipt(receipt)
    """

    def __init__(self, config: Optional[EurekaConfig] = None):
        self.config = config or EurekaConfig()
        self.config.receipts_path.parent.mkdir(parents=True, exist_ok=True)

        # Load Merkle state
        self._merkle_state = self._load_merkle_state()

    def _load_merkle_state(self) -> MerkleState:
        """Load Merkle state from JSON file."""
        path = self.config.merkle_state_path
        if not path.exists():
            return MerkleState()

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return MerkleState.from_dict(data)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load Merkle state: {e}")
            return MerkleState()

    def _save_merkle_state(self) -> bool:
        """Save Merkle state to JSON file."""
        try:
            path = self.config.merkle_state_path
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8") as f:
                json.dump(self._merkle_state.to_dict(), f, indent=2)
            return True
        except IOError as e:
            logger.error(f"Failed to save Merkle state: {e}")
            return False

    def _generate_receipt_id(self) -> str:
        """Generate a unique EUREKA receipt ID per spec pattern."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        random_suffix = secrets.token_hex(4).upper()
        return f"EUREKA-{date_str}-{random_suffix}"

    def _compute_zkpc_hash(
        self,
        metrics: Optional["Metrics"],
        floor_proofs: FloorProofs,
    ) -> str:
        """
        Compute zkPC hash from metrics and floor proofs.

        In production, this would be the hash of an actual zkSNARK proof.
        This stub hashes the floor proof booleans and a metrics summary.
        """
        payload = {
            "floor_proofs": floor_proofs.to_dict(),
            "metrics_summary": "checked" if metrics else "none",
            "timestamp": time.time(),
        }
        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _compute_receipt_hash(self, receipt_data: Dict[str, Any]) -> str:
        """
        Compute hash of receipt (excluding receipt_hash, apex_signature, merkle_root).

        These fields are added after the hash is computed, so they must be excluded
        from hash computation during verification.

        Uses canonical JSON representation.
        """
        # Exclude fields that are added after hash computation
        excluded_fields = {"receipt_hash", "apex_signature", "merkle_root"}
        data = {k: v for k, v in receipt_data.items() if k not in excluded_fields}
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _sign_receipt(self, receipt_hash: str) -> str:
        """
        Sign the receipt hash using HMAC-SHA256.

        In production, this should use hardware-backed APEX PRIME keys.
        """
        sig = hmac.new(
            self.config.hmac_key,
            receipt_hash.encode(),
            hashlib.sha256,
        ).hexdigest()
        return sig

    def _update_merkle_root(self, receipt_hash: str) -> str:
        """
        Update the Merkle root with a new receipt.

        This stub uses a simple chain: new_root = hash(old_root + receipt_hash)
        Production should use a proper Merkle tree structure.
        """
        combined = self._merkle_state.merkle_root + receipt_hash
        new_root = hashlib.sha256(combined.encode()).hexdigest()
        return new_root

    def _append_receipt(self, receipt: EurekaReceipt) -> bool:
        """Append a receipt to the JSONL file."""
        try:
            path = self.config.receipts_path
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(receipt.to_dict(), sort_keys=True) + "\n")
            return True
        except IOError as e:
            logger.error(f"Failed to append receipt: {e}")
            return False

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def generate_receipt(
        self,
        ledger_entry_hash: str,
        verdict: ReceiptVerdict,
        stakes_class: StakesClass,
        care_scope: CareScope,
        metrics: Optional["Metrics"] = None,
        floor_proofs: Optional[FloorProofs] = None,
        cce_proofs: Optional[CCEProofs] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[EurekaReceipt], Optional[str]]:
        """
        Generate an EUREKA receipt for a governed cognition event.

        Only SEAL and PARTIAL verdicts should generate receipts.
        VOID and SABAR do not generate receipts (cognition was blocked).

        Args:
            ledger_entry_hash: SHA-256 hash of the linked Cooling Ledger entry
            verdict: The governance verdict (SEAL or PARTIAL)
            stakes_class: CLASS_A (fast path) or CLASS_B (full pipeline)
            care_scope: Who/what this cognition was caring for
            metrics: Optional Metrics instance for Tri-Witness extraction
            floor_proofs: Optional custom floor proofs (defaults to all True)
            cce_proofs: Optional CCE audit proofs
            extra: Optional extra fields

        Returns:
            Tuple of (success, EurekaReceipt or None, error message or None)
        """
        # Validate verdict
        if verdict not in ("SEAL", "PARTIAL"):
            return (False, None, f"Invalid verdict for receipt: {verdict}")

        # Generate IDs and timestamps
        receipt_id = self._generate_receipt_id()
        timestamp = datetime.now(timezone.utc).isoformat()

        # Floor proofs default to all checked
        if floor_proofs is None:
            floor_proofs = FloorProofs()

        # Compute zkPC hash
        zkpc_hash = self._compute_zkpc_hash(metrics, floor_proofs)

        # Extract Tri-Witness from metrics if available
        tri_witness = None
        if metrics:
            tri_witness = TriWitnessScores.from_metrics(metrics)

        # Get previous receipt hash for chaining
        previous_hash = self._merkle_state.last_receipt_hash

        # Build receipt data (without hash and signature yet)
        receipt_data = {
            "receipt_id": receipt_id,
            "timestamp": timestamp,
            "event_id": ledger_entry_hash,
            "zkpc_hash": zkpc_hash,
            "care_scope": care_scope.to_dict(),
            "floor_proofs": floor_proofs.to_dict(),
            "verdict": verdict,
            "class": stakes_class,
            "previous_receipt_hash": previous_hash,
        }

        if cce_proofs:
            receipt_data["cce_proofs"] = cce_proofs.to_dict()

        if tri_witness:
            receipt_data["tri_witness"] = tri_witness.to_dict()

        if extra:
            receipt_data["extra"] = extra

        # Compute receipt hash
        receipt_hash = self._compute_receipt_hash(receipt_data)
        receipt_data["receipt_hash"] = receipt_hash

        # Sign the receipt
        apex_signature = self._sign_receipt(receipt_hash)
        receipt_data["apex_signature"] = apex_signature

        # Update Merkle root
        new_merkle_root = self._update_merkle_root(receipt_hash)
        receipt_data["merkle_root"] = new_merkle_root

        # Create receipt object
        receipt = EurekaReceipt(
            receipt_id=receipt_id,
            timestamp=timestamp,
            event_id=ledger_entry_hash,
            zkpc_hash=zkpc_hash,
            care_scope=care_scope,
            floor_proofs=floor_proofs,
            verdict=verdict,
            stakes_class=stakes_class,
            apex_signature=apex_signature,
            merkle_root=new_merkle_root,
            previous_receipt_hash=previous_hash,
            receipt_hash=receipt_hash,
            cce_proofs=cce_proofs,
            tri_witness=tri_witness,
            extra=extra or {},
        )

        # Persist receipt
        if not self._append_receipt(receipt):
            return (False, None, "Failed to persist receipt")

        # Update Merkle state
        self._merkle_state.merkle_root = new_merkle_root
        self._merkle_state.receipt_count += 1
        self._merkle_state.last_receipt_hash = receipt_hash

        if not self._save_merkle_state():
            logger.warning("Receipt saved but Merkle state update failed")

        logger.info(f"Generated EUREKA receipt: {receipt_id}")
        return (True, receipt, None)

    def verify_receipt(self, receipt: EurekaReceipt) -> Tuple[bool, Optional[str]]:
        """
        Verify an EUREKA receipt.

        Checks:
        1. Receipt hash matches computed hash
        2. Signature is valid
        3. Floor proofs are present

        Note: Does NOT verify chain integrity (use verify_chain for that)

        Args:
            receipt: The receipt to verify

        Returns:
            Tuple of (valid, error message or None)
        """
        # Recompute receipt hash
        receipt_data = receipt.to_dict()
        computed_hash = self._compute_receipt_hash(receipt_data)

        if computed_hash != receipt.receipt_hash:
            return (False, f"Receipt hash mismatch: expected {receipt.receipt_hash[:8]}..., computed {computed_hash[:8]}...")

        # Verify signature
        expected_sig = self._sign_receipt(receipt.receipt_hash)
        if expected_sig != receipt.apex_signature:
            return (False, "Invalid APEX signature")

        # Check floor proofs are present
        if not receipt.floor_proofs.all_checked():
            return (False, "Not all floors were checked")

        return (True, None)

    def verify_chain(self) -> Tuple[bool, str]:
        """
        Verify the integrity of the EUREKA receipt chain.

        Checks that each receipt properly chains to the previous one.

        Returns:
            Tuple of (valid, status message)
        """
        path = self.config.receipts_path
        if not path.exists():
            return (True, "Empty receipt chain (valid)")

        receipts: List[EurekaReceipt] = []

        try:
            with path.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        receipt = EurekaReceipt.from_dict(data)
                        receipts.append(receipt)
                    except (json.JSONDecodeError, TypeError) as e:
                        return (False, f"Parse error at line {line_num}: {e}")
        except IOError as e:
            return (False, f"IO error: {e}")

        if not receipts:
            return (True, "Empty receipt chain (valid)")

        # Verify first receipt has no previous
        if receipts[0].previous_receipt_hash is not None:
            return (False, "First receipt should have null previous_receipt_hash")

        # Verify chain integrity
        for i, receipt in enumerate(receipts):
            # Verify individual receipt
            valid, error = self.verify_receipt(receipt)
            if not valid:
                return (False, f"Receipt {i} invalid: {error}")

            # Verify chain link
            if i > 0:
                expected_prev = receipts[i - 1].receipt_hash
                if receipt.previous_receipt_hash != expected_prev:
                    return (False, f"Receipt {i} chain break: expected prev={expected_prev[:8]}..., actual={receipt.previous_receipt_hash[:8] if receipt.previous_receipt_hash else 'null'}...")

        return (True, f"Chain verified: {len(receipts)} receipts")

    def get_merkle_state(self) -> MerkleState:
        """Return current Merkle state."""
        return self._merkle_state

    def get_receipt_count(self) -> int:
        """Return total number of receipts."""
        return self._merkle_state.receipt_count

    def iter_receipts(self, limit: int = 100) -> List[EurekaReceipt]:
        """
        Iterate over recent receipts (most recent first).

        Args:
            limit: Maximum number of receipts to return

        Returns:
            List of EurekaReceipts
        """
        path = self.config.receipts_path
        if not path.exists():
            return []

        receipts: List[EurekaReceipt] = []

        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        receipt = EurekaReceipt.from_dict(data)
                        receipts.append(receipt)
                    except (json.JSONDecodeError, TypeError):
                        continue
        except IOError:
            return []

        # Return most recent first
        receipts.reverse()
        return receipts[:limit]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_eureka_receipt(
    ledger_entry_hash: str,
    verdict: str,
    stakes_class: str = "CLASS_A",
    risk_cooled: str = "general governance",
    stakeholders: Optional[List[str]] = None,
    metrics: Optional["Metrics"] = None,
) -> Tuple[bool, Optional[EurekaReceipt], Optional[str]]:
    """
    Convenience function to generate an EUREKA receipt.

    Args:
        ledger_entry_hash: Hash of the linked Cooling Ledger entry
        verdict: The governance verdict
        stakes_class: CLASS_A or CLASS_B
        risk_cooled: Description of the risk that was governed
        stakeholders: List of stakeholder types
        metrics: Optional Metrics instance

    Returns:
        Tuple of (success, EurekaReceipt or None, error message or None)
    """
    # Only generate for SEAL/PARTIAL
    if verdict not in ("SEAL", "PARTIAL"):
        return (True, None, None)  # Not an error, just no receipt needed

    care_scope = CareScope(
        who=stakeholders or ["user"],
        risk_cooled=risk_cooled,
    )

    manager = EurekaReceiptManager()
    return manager.generate_receipt(
        ledger_entry_hash=ledger_entry_hash,
        verdict=verdict,
        stakes_class=stakes_class,
        care_scope=care_scope,
        metrics=metrics,
    )


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Stakeholder",
    "StakesClass",
    "ReceiptVerdict",
    # Data structures
    "CareScope",
    "FloorProofs",
    "CCEProofs",
    "TriWitnessScores",
    "EurekaReceipt",
    # Manager
    "EurekaConfig",
    "MerkleState",
    "EurekaReceiptManager",
    # Convenience
    "generate_eureka_receipt",
]
