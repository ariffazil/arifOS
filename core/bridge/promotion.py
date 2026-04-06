"""
Promotion Bridge: Memory → Vault

This is the forge that binds the two organs.

Flow:
input → working memory → episodic/semantic memory → governance classifier
                                           ↓
                              if consequential → apex judgment → vault seal
                                           ↓
                              vault receipt → back to memory
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..organs.memory.types import MemoryRecord, MemoryType
from ..organs.vault.types import (
    VaultEntry, VaultRecordType, Verdict, Evidence, 
    Governance, VaultLineage, SealReceipt
)


@dataclass
class PromotionCandidate:
    """A memory record candidate for vault promotion."""
    memory_id: str
    title: str
    content: str
    memory_type: str
    confidence: float
    reason: str


class PromotionBridge:
    """
    Bridge between memory and vault.
    
    Determines which memories become vault records.
    Writes vault receipts back to memory.
    """
    
    def __init__(self, memory_organ, vault_organ):
        self.memory = memory_organ
        self.vault = vault_organ
    
    def classify_for_promotion(self, memory: MemoryRecord) -> tuple[bool, str]:
        """
        Classify if a memory should be promoted to vault.
        
        Returns (should_promote, reason).
        """
        # Already checked promotable flag
        if not memory.governance.promotable_to_vault:
            return False, "Not marked as promotable"
        
        # Must be high confidence
        if memory.governance.confidence < 0.85:
            return False, "Confidence too low"
        
        # Check for vault-worthy signals
        vault_signals = [
            "decided", "decision", "approved", "architecture",
            "policy", "governance", "sovereign", "hold", "refused",
            "sealed", "released", "verified", "constitutional",
        ]
        
        text = f"{memory.title} {memory.content}".lower()
        has_signal = any(sig in text for sig in vault_signals)
        
        if not has_signal:
            return False, "No vault-worthy signals"
        
        # Check memory type
        if memory.memory_type == MemoryType.CONSTITUTIONAL:
            return True, "Constitutional rule"
        
        if memory.memory_type == MemoryType.SEMANTIC:
            # Semantic facts about core architecture
            if "arifos" in text and ("vault" in text or "memory" in text):
                return True, "Core architecture doctrine"
        
        if memory.memory_type == MemoryType.EPISODIC:
            # Important decisions
            if "decided" in text or "decision" in text:
                return True, "Recorded decision"
        
        return False, "Does not meet promotion criteria"
    
    def promote(self, memory_id: str, session_id: str) -> Optional[SealReceipt]:
        """
        Promote a memory record to vault.
        
        Creates vault entry, seals it, writes receipt back to memory.
        """
        # Find memory
        memory = None
        for lane in [self.memory.working, self.memory.episodic, self.memory.semantic]:
            mem = lane._memories.get(memory_id)
            if mem:
                memory = mem
                break
        
        if not memory:
            return None
        
        # Classify
        should_promote, reason = self.classify_for_promotion(memory)
        if not should_promote:
            return None
        
        # Build vault entry
        entry = self._memory_to_vault_entry(memory, session_id)
        
        # Seal to vault
        receipt = self.vault.seal(entry)
        
        if receipt:
            # Write receipt back to memory
            self._write_vault_receipt(memory, receipt)
        
        return receipt
    
    def _memory_to_vault_entry(
        self,
        memory: MemoryRecord,
        session_id: str,
    ) -> VaultEntry:
        """Convert memory record to vault entry."""
        # Determine record type
        if memory.memory_type == MemoryType.CONSTITUTIONAL:
            record_type = VaultRecordType.POLICY
        elif "decided" in memory.content.lower() or "decision" in memory.content.lower():
            record_type = VaultRecordType.VERDICT
        elif "release" in memory.content.lower():
            record_type = VaultRecordType.RELEASE
        else:
            record_type = VaultRecordType.VERDICT
        
        # Determine verdict
        if "approved" in memory.content.lower():
            verdict = Verdict.APPROVED
        elif "hold" in memory.content.lower():
            verdict = Verdict.HOLD
        elif "void" in memory.content.lower():
            verdict = Verdict.VOID
        else:
            verdict = Verdict.APPROVED
        
        return VaultEntry(
            vault_id="",  # Will be assigned by vault
            record_type=record_type,
            verdict=verdict,
            candidate_action=memory.title,
            evidence=Evidence(
                summary=memory.summary or memory.content[:200],
                evidence_refs=[memory.memory_id],
                evidence_hash=hash(memory.content) % (2**32),  # Simplified
            ),
            governance=Governance(
                risk_tier="medium" if memory.governance.sensitivity.value == "medium" else "low",
                judgment_required=True,
                human_confirmed=memory.source.origin.value == "user",
                decision_authority="ARIF",  # Would be actual authority
                policy_version="arifOS.constitution.v1",
            ),
            lineage=VaultLineage(
                session_id=session_id,
                derived_from=[memory.memory_id],
            ),
        )
    
    def _write_vault_receipt(self, memory: MemoryRecord, receipt: SealReceipt):
        """Write vault receipt back to memory as episodic record."""
        self.memory.episodic.record_event(
            title=f"Vault sealed: {memory.title[:50]}...",
            content=f"Memory promoted to vault. Vault ID: {receipt.vault_id}. Record hash: {receipt.record_hash[:16]}...",
            source=memory.source,
            project=memory.scope.project,
        )
    
    async def process_session_for_promotion(self, session_id: str) -> list[SealReceipt]:
        """
        Scan session memories and promote consequential ones.
        
        Called at end of session.
        """
        receipts = []
        
        # Check episodic memories
        for memory in self.memory.episodic._memories.values():
            if memory.source.session_id == session_id:
                receipt = self.promote(memory.memory_id, session_id)
                if receipt:
                    receipts.append(receipt)
        
        # Check semantic memories
        for memory in self.memory.semantic._memories.values():
            # Only check recent updates
            if (datetime.utcnow() - memory.time.updated_at).seconds < 3600:
                receipt = self.promote(memory.memory_id, session_id)
                if receipt:
                    receipts.append(receipt)
        
        return receipts


def create_bridge(memory_organ, vault_organ) -> PromotionBridge:
    """Create promotion bridge."""
    return PromotionBridge(memory_organ, vault_organ)
