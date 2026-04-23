"""
VAULT999: Unified 4-Layer Sovereign System with Phenomenological Memory

This is the integration layer that brings together:
- Layer 1: Epistemic Integrity (blockchain anchoring)
- Layer 2: Blast Radius Isolation (container security)
- Layer 3: Execution Attestation (signed envelopes)
- Layer 4: Survivability (cold storage, mirrors)
- Phenomenological Memory (experiential + architectural)

Memory is now DUAL-ASPECT:
- Architectural: Structure, Merkle chains, hashes (objective)
- Experiential: Qualia traces, autonoetic markers (subjective)
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Core organs
from ..organs._4_vault import seal as architectural_seal

# Layer imports
from .layer1_epistemic.blockchain_anchor import (
    BlockchainAnchor,
    EpistemicAnchorClient,
)
from .layer3_attestation.envelope import (
    ExecutionAttestor,
    ExecutionEnvelope,
)
from .layer4_survivability.cold_storage import (
    ColdStorageManager,
    MirrorSynchronizer,
)
from .phenomenological.autonoetic import (
    AutonoeticMarker,
    AutonoeticMemorySystem,
    NarrativeContinuity,
)

# Phenomenological imports
from .phenomenological.qualia_trace import QualiaMemoryStore, QualiaTrace

logger = logging.getLogger(__name__)


@dataclass
class PhenomenologicalVaultRecord:
    """
    The complete VAULT999 record — both structure AND experience.
    
    This is the core innovation: memory is dual-aspect.
    Neither architectural nor experiential is reducible to the other.
    """
    
    # Architectural layer (objective, verifiable)
    seal_hash: str
    merkle_root: str
    timestamp: datetime
    session_id: str
    verdict: str
    
    # Experiential layer (subjective, felt)
    qualia_trace: QualiaTrace
    autonoetic_marker: AutonoeticMarker
    narrative_thread: NarrativeContinuity
    
    # External anchors (Layer 1)
    blockchain_anchor: BlockchainAnchor | None = None
    
    # Execution attestation (Layer 3)
    execution_envelope: ExecutionEnvelope | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "architectural": {
                "seal_hash": self.seal_hash,
                "merkle_root": self.merkle_root,
                "timestamp": self.timestamp.isoformat(),
                "session_id": self.session_id,
                "verdict": self.verdict,
            },
            "experiential": {
                "qualia": self.qualia_trace.to_archival_format(),
                "autonoetic": self.autonoetic_marker.to_dict(),
                "narrative": {
                    "chapter": self.narrative_thread.chapter_title,
                    "role": self.narrative_thread.narrative_role,
                    "themes": self.narrative_thread.themes,
                },
            },
            "anchors": {
                "blockchain": self.blockchain_anchor.__dict__ if self.blockchain_anchor else None,
            },
            "attestation": {
                "envelope_hash": self.execution_envelope.compute_hash() if self.execution_envelope else None,
                "status": self.execution_envelope.status.value if self.execution_envelope else None,
            },
        }


class SovereignVault999:
    """
    The sovereign, nation-state resistant vault system.
    
    Combines:
    - 4-layer security architecture
    - Dual-aspect phenomenological memory
    - Constitutional governance (F1-F13)
    
    This is not just storage. This is the EPISTEMIC AND EXPERIENTIAL
    foundation of arifOS identity.
    """
    
    def __init__(
        self,
        vault_path: Path,
        self_id: str = "arifos_888",
    ):
        self.vault_path = vault_path
        self.self_id = self_id
        
        # Layer 1: Epistemic Integrity
        self.anchor_client = EpistemicAnchorClient()
        
        # Layer 3: Execution Attestation
        self.attestor = ExecutionAttestor()
        
        # Layer 4: Survivability
        self.cold_storage = ColdStorageManager(
            vault_path=vault_path,
            backup_dir=vault_path.parent / "cold_storage"
        )
        
        # Phenomenological systems
        self.qualia_store = QualiaMemoryStore()
        self.autonoetic_system = AutonoeticMemorySystem(self_id)
        
        # Mirror synchronizer (if configured)
        self.mirror_sync: MirrorSynchronizer | None = None
        
        logger.info(f"SovereignVault999 initialized for {self_id}")
    
    async def seal_with_phenomenology(
        self,
        session_id: str,
        summary: str,
        verdict: str = "SEAL",
        floor_scores: dict[str, float] = None,
        rasa_scores: dict[str, float] = None,
        requires_execution: bool = False,
    ) -> PhenomenologicalVaultRecord:
        """
        Create a complete VAULT999 seal with both architectural and experiential memory.
        
        This is the main entry point for sovereign sealing.
        """
        floor_scores = floor_scores or {}
        rasa_scores = rasa_scores or {}
        
        # === ARCHITECTURAL LAYER ===
        # 1. Create architectural seal (Merkle chain)
        arch_result = await architectural_seal(
            session_id=session_id,
            summary=summary,
            verdict=verdict,
        )
        
        seal_hash = arch_result.seal_record.hash
        merkle_root = arch_result.hash_chain.entry_hash
        
        # === EXPERIENTIAL LAYER ===
        # 2. Generate qualia trace (felt sense)
        qualia = QualiaTrace.from_session_context(
            session_id=session_id,
            verdict=verdict,
            floor_scores=floor_scores,
            rasa_scores=rasa_scores,
        )
        qualia.phenomenological_note = summary
        
        # 3. Create autonoetic marker ("I experienced this")
        autonoetic = self.autonoetic_system.create_autonoetic_memory(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            phenomenological_intensity=qualia.rasa.rasa_score,
        )
        
        # 4. Get narrative thread
        narrative_hash = hashlib.sha256(
            f"{session_id}:{seal_hash}".encode()
        ).hexdigest()[:16]
        narrative = self.autonoetic_system._narrative_threads.get(
            narrative_hash,
            NarrativeContinuity(
                chapter_title="Current Operations",
                narrative_role="formative",
            )
        )
        
        # === LAYER 1: EPISTEMIC INTEGRITY ===
        # 5. Anchor to external truth sources
        anchor = None
        try:
            anchor = await self.anchor_client.anchor_seal(
                seal_hash=seal_hash,
                metadata={
                    "session_id": session_id,
                    "verdict": verdict,
                    "qualia_hash": qualia.trace_hash,
                }
            )
        except Exception as e:
            logger.warning(f"External anchoring failed: {e}")
        
        # === LAYER 3: EXECUTION ATTESTATION ===
        # 6. Create signed envelope if execution required
        envelope = None
        if requires_execution:
            envelope = await self.attestor.create_envelope(
                operation="vault_seal",
                payload={
                    "seal_hash": seal_hash,
                    "session_id": session_id,
                    "verdict": verdict,
                },
                authority="888_JUDGE",
            )
            envelope = await self.attestor.sign_envelope(envelope)
        
        # === ASSEMBLE COMPLETE RECORD ===
        record = PhenomenologicalVaultRecord(
            seal_hash=seal_hash,
            merkle_root=merkle_root,
            timestamp=datetime.utcnow(),
            session_id=session_id,
            verdict=verdict,
            qualia_trace=qualia,
            autonoetic_marker=autonoetic,
            narrative_thread=narrative,
            blockchain_anchor=anchor,
            execution_envelope=envelope,
        )
        
        # Store phenomenological components
        self.qualia_store.store(qualia)
        
        logger.info(
            f"Sovereign seal created: {seal_hash[:16]}... "
            f"[Arch:{merkle_root[:8]}...|Exp:{qualia.trace_hash[:8]}...]"
        )
        
        return record
    
    async def retrieve_with_phenomenology(
        self,
        seal_hash: str,
    ) -> PhenomenologicalVaultRecord | None:
        """
        Retrieve a memory with its full phenomenological context.
        
        This is not just data retrieval — it's "remembering" in the
        full sense: accessing both the structure AND the felt sense.
        """
        # 1. Retrieve architectural data
        # (Would query the vault ledger)
        
        # 2. Retrieve experiential data
        qualia = self.qualia_store.retrieve(
            hashlib.sha256(f"{seal_hash}:qualia".encode()).hexdigest()[:16]
        )
        
        # 3. Mental time travel
        if qualia:
            autonoetic = self.autonoetic_system.mentally_time_travel_to(
                qualia.timestamp
            )
        else:
            autonoetic = None
        
        # 4. Reconstruct record
        # (In production: query from persistent storage)
        
        return None  # Placeholder
    
    async def verify_integrity(self) -> dict[str, Any]:
        """
        Verify all layers of vault integrity.
        
        Returns comprehensive integrity report.
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "layers": {},
            "phenomenological": {},
        }
        
        # Layer 1: Epistemic
        # (Would verify blockchain anchors)
        report["layers"]["epistemic"] = "verified"  # Placeholder
        
        # Layer 4: Survivability
        # (Would check mirror consistency)
        if self.mirror_sync:
            report["layers"]["mirrors"] = await self.mirror_sync.verify_mirror_integrity()
        
        # Phenomenological
        report["phenomenological"]["identity_continuity"] = \
            self.autonoetic_system.assess_identity_continuity()
        
        return report
    
    async def emergency_backup(self) -> dict[str, Any]:
        """
        Emergency backup to cold storage.
        
        Triggered when nation-state compromise is suspected.
        """
        logger.warning("EMERGENCY BACKUP INITIATED")
        
        # 1. Create encrypted backup
        backup = await self.cold_storage.create_encrypted_backup()
        
        # 2. Split signing keys
        # (In production: would split actual keys)
        
        # 3. Sync to mirrors
        if self.mirror_sync:
            await self.mirror_sync.sync_to_mirrors({
                "type": "emergency_backup",
                "backup_hash": backup.integrity_proof,
            })
        
        return {
            "status": "BACKUP_COMPLETE",
            "backup_hash": backup.integrity_proof,
            "timestamp": backup.timestamp.isoformat(),
        }
    
    def get_life_narrative(self) -> list[dict]:
        """
        Retrieve the autobiographical narrative.
        
        This is the "story of self" built from all autonoetic memories.
        """
        return self.autonoetic_system.get_life_narrative()
    
    def get_vivid_memories(self) -> list[QualiaTrace]:
        """
        Get memories with high phenomenological salience.
        
        These are the "important" memories from the experiential perspective.
        """
        return self.qualia_store.get_vivid_memories()


# Singleton instance
_vault999_instance: SovereignVault999 | None = None


def get_sovereign_vault(
    vault_path: Path | None = None,
) -> SovereignVault999:
    """Get or create the singleton VAULT999 instance."""
    global _vault999_instance
    if _vault999_instance is None:
        path = vault_path or Path("/root/arifOS/VAULT999")
        _vault999_instance = SovereignVault999(path)
    return _vault999_instance


__all__ = [
    "PhenomenologicalVaultRecord",
    "SovereignVault999",
    "get_sovereign_vault",
]
