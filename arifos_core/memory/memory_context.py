"""
memory_context.py — 6-Band MemoryContext for arifOS v37

Implements the MemoryContext structure per ARIFOS_MEMORY_STACK_v36.3O.md canon
and memory_context_spec_v36.3O.json spec.

Six Memory Bands:
- ENV (EnvBand): Non-secret runtime context
- VLT (VaultBand): Read-only VAULT-999 L0 constitution snapshot
- LDG (LedgerBand): Recent Cooling Ledger projection
- ACT (ActiveStreamBand): Volatile working state for current interaction
- VEC (VectorBand): Witness memory and embedding-backed context
- VOID (VoidBand): Diagnostic scars, paradoxes, anomalies

Invariants (from canon):
- Vault Band is read-only; other bands cannot override it.
- Ledger Band is append-only projection; no re-order or edit.
- VoidBand entries must be signed when promoted and never silently discarded.

Specification:
- archive/versions/v36_3_omega/v36.3O/spec/memory_context_spec_v36.3O.json
- archive/versions/v36_3_omega/v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md

Author: arifOS Project
Version: v37
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


# =============================================================================
# BAND DEFINITIONS
# =============================================================================

@dataclass
class EnvBand:
    """
    Non-secret runtime context for interpreting the interaction.

    Invariant: Must not contain user secrets, long-term identifiers, or raw chat history.
    """
    runtime_manifest_id: str
    request_id: str
    session_id: Optional[str] = None
    stakes_class: str = "CLASS_A"  # CLASS_A or CLASS_B
    locale: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "runtime_manifest_id": self.runtime_manifest_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "stakes_class": self.stakes_class,
            "locale": self.locale,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvBand":
        return cls(
            runtime_manifest_id=data.get("runtime_manifest_id", "unknown"),
            request_id=data.get("request_id", str(uuid.uuid4())[:8]),
            session_id=data.get("session_id"),
            stakes_class=data.get("stakes_class", "CLASS_A"),
            locale=data.get("locale"),
            extra=data.get("extra", {}),
        )


@dataclass
class VaultBand:
    """
    Read-only snapshot of VAULT-999 L0 constitution.

    Invariant: No other band may override or shadow Vault Band fields.
    """
    epoch: str
    constitutional_floors: Dict[str, Any]
    version_hash: str
    deltaOmegaPsi: Dict[str, Any] = field(default_factory=dict)
    aaa_trinity: Dict[str, Any] = field(default_factory=dict)
    amendment_history_ref: Optional[str] = None

    # Internal flag to enforce read-only
    _frozen: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        if not self.version_hash:
            # Compute hash from constitutional_floors
            self.version_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of constitutional state."""
        content = json.dumps(
            {
                "epoch": self.epoch,
                "floors": self.constitutional_floors,
                "dop": self.deltaOmegaPsi,
                "aaa": self.aaa_trinity,
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()

    def freeze(self) -> None:
        """Freeze the band to prevent modifications."""
        object.__setattr__(self, "_frozen", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False) and name != "_frozen":
            raise AttributeError("VaultBand is read-only and cannot be modified")
        object.__setattr__(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "epoch": self.epoch,
            "constitutional_floors": self.constitutional_floors,
            "version_hash": self.version_hash,
            "deltaOmegaPsi": self.deltaOmegaPsi,
            "aaa_trinity": self.aaa_trinity,
            "amendment_history_ref": self.amendment_history_ref,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VaultBand":
        band = cls(
            epoch=data.get("epoch", "v37"),
            constitutional_floors=data.get("constitutional_floors", {}),
            version_hash=data.get("version_hash", ""),
            deltaOmegaPsi=data.get("deltaOmegaPsi", {}),
            aaa_trinity=data.get("aaa_trinity", {}),
            amendment_history_ref=data.get("amendment_history_ref"),
        )
        return band


@dataclass
class LedgerBand:
    """
    Projection of recent Cooling Ledger entries.

    Invariant: Append-only projection; must not re-order or edit entries.
    """
    entries: List[Dict[str, Any]] = field(default_factory=list)
    window_hours: Optional[float] = None
    head_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": self.entries,
            "window_hours": self.window_hours,
            "head_hash": self.head_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerBand":
        return cls(
            entries=data.get("entries", []),
            window_hours=data.get("window_hours"),
            head_hash=data.get("head_hash"),
        )


@dataclass
class ActiveStreamBand:
    """
    Volatile working state for current interaction.

    Invariant: Not a source of law or long-term evidence.
    """
    messages: List[Dict[str, Any]] = field(default_factory=list)
    governance_state: Dict[str, Any] = field(default_factory=dict)
    tools_invoked: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messages": self.messages,
            "governance_state": self.governance_state,
            "tools_invoked": self.tools_invoked,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActiveStreamBand":
        return cls(
            messages=data.get("messages", []),
            governance_state=data.get("governance_state", {}),
            tools_invoked=data.get("tools_invoked", []),
        )


@dataclass
class VectorIndex:
    """A single vector index entry."""
    index_id: str
    kind: str = "other"  # scar, witness, docs, policy, other
    dimension: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_id": self.index_id,
            "kind": self.kind,
            "dimension": self.dimension,
            "metadata": self.metadata,
        }


@dataclass
class VectorBand:
    """
    Witness memory backed by vector indices.

    Invariant: Content must be traceable to L1 evidence or external sources with provenance.
    """
    indices: List[VectorIndex] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indices": [idx.to_dict() for idx in self.indices],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorBand":
        indices = [
            VectorIndex(
                index_id=idx.get("index_id", ""),
                kind=idx.get("kind", "other"),
                dimension=idx.get("dimension"),
                metadata=idx.get("metadata", {}),
            )
            for idx in data.get("indices", [])
        ]
        return cls(indices=indices)


@dataclass
class ParadoxHotspot:
    """A detected paradox or conflict location."""
    hotspot_id: str
    description: str
    detected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotspot_id": self.hotspot_id,
            "description": self.description,
            "detected_at": self.detected_at,
        }


@dataclass
class VoidBand:
    """
    Diagnostics, anomalies, and scar proposals.

    Invariant: Entries must be signed when promoted, anchored to ledger events,
    never silently discarded.
    """
    scar_proposals: List[Dict[str, Any]] = field(default_factory=list)
    canonical_scars: List[Dict[str, Any]] = field(default_factory=list)
    paradox_hotspots: List[ParadoxHotspot] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scar_proposals": self.scar_proposals,
            "canonical_scars": self.canonical_scars,
            "paradox_hotspots": [h.to_dict() for h in self.paradox_hotspots],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VoidBand":
        hotspots = [
            ParadoxHotspot(
                hotspot_id=h.get("hotspot_id", ""),
                description=h.get("description", ""),
                detected_at=h.get("detected_at", ""),
            )
            for h in data.get("paradox_hotspots", [])
        ]
        return cls(
            scar_proposals=data.get("scar_proposals", []),
            canonical_scars=data.get("canonical_scars", []),
            paradox_hotspots=hotspots,
        )


# =============================================================================
# MEMORY CONTEXT
# =============================================================================

@dataclass
class MemoryContext:
    """
    Master 6-band memory context for arifOS v37.

    Implements ARIFOS_MEMORY_STACK_v36.3O.md canon with:
    - ENV: Non-secret runtime context
    - VLT: Read-only VAULT-999 constitution
    - LDG: Recent Cooling Ledger projection
    - ACT: Volatile working state
    - VEC: Vector/embedding memory
    - VOID: Diagnostics and scar proposals

    Invariants:
    - VaultBand is read-only after initialization
    - LedgerBand is append-only
    - VoidBand entries require signing before promotion
    """
    context_id: str
    epoch: str
    env: EnvBand
    vault: VaultBand
    ledger: LedgerBand
    active_stream: ActiveStreamBand
    vector: Optional[VectorBand] = None
    void: Optional[VoidBand] = None

    def __post_init__(self) -> None:
        # Freeze the vault band to enforce read-only
        self.vault.freeze()

    # =========================================================================
    # BAND ACCESS (with protection)
    # =========================================================================

    def get_env(self) -> EnvBand:
        """Get the environment band (mutable)."""
        return self.env

    def get_vault(self) -> VaultBand:
        """Get the vault band (read-only)."""
        return self.vault

    def get_ledger(self) -> LedgerBand:
        """Get the ledger band (read-only projection)."""
        return self.ledger

    def get_active_stream(self) -> ActiveStreamBand:
        """Get the active stream band (mutable)."""
        return self.active_stream

    def get_vector(self) -> Optional[VectorBand]:
        """Get the vector band (optional)."""
        return self.vector

    def get_void(self) -> Optional[VoidBand]:
        """Get the void band (optional)."""
        return self.void

    # =========================================================================
    # ACTIVE STREAM OPERATIONS
    # =========================================================================

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the active stream."""
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            msg["metadata"] = metadata
        self.active_stream.messages.append(msg)

    def update_governance_state(self, key: str, value: Any) -> None:
        """Update a governance state field."""
        self.active_stream.governance_state[key] = value

    def record_tool_invocation(self, tool_name: str, params: Dict[str, Any]) -> None:
        """Record a tool invocation in the active stream."""
        self.active_stream.tools_invoked.append({
            "tool": tool_name,
            "params": params,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # =========================================================================
    # VOID BAND OPERATIONS
    # =========================================================================

    def propose_scar(self, pattern: str, severity: str, evidence: Dict[str, Any]) -> None:
        """Propose a new scar (unsigned, in VoidBand)."""
        if self.void is None:
            self.void = VoidBand()

        proposal = {
            "pattern": pattern,
            "severity": severity,
            "evidence": evidence,
            "proposed_at": datetime.now(timezone.utc).isoformat(),
            "status": "PROPOSED",
        }
        self.void.scar_proposals.append(proposal)

    def add_paradox_hotspot(self, hotspot_id: str, description: str) -> None:
        """Record a detected paradox hotspot."""
        if self.void is None:
            self.void = VoidBand()

        self.void.paradox_hotspots.append(ParadoxHotspot(
            hotspot_id=hotspot_id,
            description=description,
        ))

    def promote_scar_to_canonical(
        self,
        proposal_index: int,
        ledger_entry_hash: str,
        signature: str,
    ) -> bool:
        """
        Promote a scar proposal to canonical status.

        INVARIANT: Scars MUST be signed with ledger reference before promotion.
        Unsigned scars remain proposals and cannot influence governance.

        Args:
            proposal_index: Index into void.scar_proposals
            ledger_entry_hash: Hash of the ledger entry anchoring this scar
            signature: Cryptographic signature (or approval hash)

        Returns:
            True if promotion succeeded, False otherwise

        Raises:
            ValueError: If signature or ledger_entry_hash is empty
        """
        if self.void is None:
            return False

        if not ledger_entry_hash:
            raise ValueError("VoidBand scar promotion requires ledger_entry_hash")
        if not signature:
            raise ValueError("VoidBand scar promotion requires signature")

        if proposal_index < 0 or proposal_index >= len(self.void.scar_proposals):
            return False

        proposal = self.void.scar_proposals[proposal_index]

        # Create signed canonical scar
        canonical_scar = {
            **proposal,
            "status": "CANONICAL",
            "ledger_entry_hash": ledger_entry_hash,
            "signature": signature,
            "promoted_at": datetime.now(timezone.utc).isoformat(),
        }

        self.void.canonical_scars.append(canonical_scar)

        # Mark proposal as promoted (don't remove, keep audit trail)
        proposal["status"] = "PROMOTED"
        proposal["promoted_to_canonical_at"] = canonical_scar["promoted_at"]

        return True

    # =========================================================================
    # SERIALIZATION
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the full context to a dictionary."""
        result = {
            "context_id": self.context_id,
            "epoch": self.epoch,
            "env": self.env.to_dict(),
            "vault": self.vault.to_dict(),
            "ledger": self.ledger.to_dict(),
            "active_stream": self.active_stream.to_dict(),
        }
        if self.vector is not None:
            result["vector"] = self.vector.to_dict()
        if self.void is not None:
            result["void"] = self.void.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryContext":
        """Deserialize from dictionary."""
        vector = None
        if "vector" in data:
            vector = VectorBand.from_dict(data["vector"])

        void = None
        if "void" in data:
            void = VoidBand.from_dict(data["void"])

        # Create vault band but don't freeze yet (will be frozen in __post_init__)
        vault = VaultBand.from_dict(data.get("vault", {}))

        return cls(
            context_id=data.get("context_id", str(uuid.uuid4())[:8]),
            epoch=data.get("epoch", "v37"),
            env=EnvBand.from_dict(data.get("env", {})),
            vault=vault,
            ledger=LedgerBand.from_dict(data.get("ledger", {})),
            active_stream=ActiveStreamBand.from_dict(data.get("active_stream", {})),
            vector=vector,
            void=void,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "MemoryContext":
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_memory_context(
    manifest_id: str = "v37",
    request_id: Optional[str] = None,
    stakes_class: str = "CLASS_A",
    vault_floors: Optional[Dict[str, Any]] = None,
    ledger_entries: Optional[List[Dict[str, Any]]] = None,
) -> MemoryContext:
    """
    Factory function to create a new MemoryContext.

    Args:
        manifest_id: Runtime manifest identifier
        request_id: Optional request ID (auto-generated if None)
        stakes_class: CLASS_A or CLASS_B
        vault_floors: Optional constitutional floors dict
        ledger_entries: Optional recent ledger entries

    Returns:
        Initialized MemoryContext
    """
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]

    context_id = str(uuid.uuid4())[:12]

    # Default floors from v35Ω if not provided
    if vault_floors is None:
        vault_floors = {
            "truth_min": 0.99,
            "delta_s_min": 0.0,
            "peace_squared_min": 1.0,
            "kappa_r_min": 0.95,
            "omega_band": {"min": 0.03, "max": 0.05},
            "amanah_lock": True,
            "rasa_required": True,
            "tri_witness_min": 0.95,
            "anti_hantu": True,
        }

    env = EnvBand(
        runtime_manifest_id=manifest_id,
        request_id=request_id,
        stakes_class=stakes_class,
    )

    vault = VaultBand(
        epoch="v37",
        constitutional_floors=vault_floors,
        version_hash="",  # Will be computed in __post_init__
    )

    ledger = LedgerBand(
        entries=ledger_entries or [],
        window_hours=72.0,
    )

    active_stream = ActiveStreamBand()

    return MemoryContext(
        context_id=context_id,
        epoch="v37",
        env=env,
        vault=vault,
        ledger=ledger,
        active_stream=active_stream,
        vector=VectorBand(),
        void=VoidBand(),
    )


# =============================================================================
# SCHEMA VALIDATION
# =============================================================================

def validate_memory_context(ctx: MemoryContext) -> tuple[bool, List[str]]:
    """
    Validate a MemoryContext against the spec.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: List[str] = []

    # Required fields
    if not ctx.context_id:
        errors.append("context_id is required")
    if not ctx.epoch:
        errors.append("epoch is required")

    # Env band validation
    if not ctx.env.runtime_manifest_id:
        errors.append("env.runtime_manifest_id is required")
    if not ctx.env.request_id:
        errors.append("env.request_id is required")
    if ctx.env.stakes_class not in ("CLASS_A", "CLASS_B"):
        errors.append(f"env.stakes_class must be CLASS_A or CLASS_B, got {ctx.env.stakes_class}")

    # Vault band validation
    if not ctx.vault.epoch:
        errors.append("vault.epoch is required")
    if not ctx.vault.constitutional_floors:
        errors.append("vault.constitutional_floors is required")
    if not ctx.vault.version_hash:
        errors.append("vault.version_hash is required")

    # Ledger band validation
    if ctx.ledger.entries is None:
        errors.append("ledger.entries must be a list (can be empty)")

    return (len(errors) == 0, errors)


# =============================================================================
# PUBLIC EXPORTS
# =============================================================================

__all__ = [
    # Bands
    "EnvBand",
    "VaultBand",
    "LedgerBand",
    "ActiveStreamBand",
    "VectorBand",
    "VectorIndex",
    "VoidBand",
    "ParadoxHotspot",
    # Main class
    "MemoryContext",
    # Factory
    "create_memory_context",
    # Validation
    "validate_memory_context",
]
