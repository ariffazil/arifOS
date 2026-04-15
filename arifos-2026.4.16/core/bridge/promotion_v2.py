"""
Promotion Bridge v2 — With Explicit Outcomes

Promotion outcomes:
- REJECTED_NON CONSEQUENTIAL
- HELD_PENDING_HUMAN_CONFIRMATION
- ELIGIBLE_FOR_SEAL
- SEALED
- SUPERSEDED
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from ..organs.memory.types_v2 import MemoryRecord, MemoryType, ConfidenceClass
from ..organs.vault.types import VaultEntry, VaultRecordType, Verdict, Evidence, Governance, VaultLineage, SealReceipt


class PromotionOutcome(Enum):
    """Explicit outcomes for promotion attempts."""
    REJECTED_NON_CONSEQUENTIAL = "rejected_non_consequential"
    HELD_PENDING_HUMAN_CONFIRMATION = "held_pending_human_confirmation"
    ELIGIBLE_FOR_SEAL = "eligible_for_seal"
    SEALED = "sealed"
    SUPERSEDED = "superseded"


@dataclass
class PromotionResult:
    """Result of promotion attempt."""
    outcome: PromotionOutcome
    memory_id: str
    vault_id: Optional[str] = None
    seal_receipt: Optional[SealReceipt] = None
    reason: str = ""
    requires_action: Optional[str] = None  # What needs to happen next


class PromotionBridge:
    """
    Bridge between memory and vault with explicit outcomes.
    """
    
    def __init__(self, memory_organ, vault_organ):
        self.memory = memory_organ
        self.vault = vault_organ
    
    def classify_for_promotion(self, memory: MemoryRecord) -> tuple[bool, str, Optional[PromotionOutcome]]:
        """
        Classify if a memory should be promoted to vault.
        
        Returns (should_promote, reason, preliminary_outcome).
        """
        # Check promotable flag
        if not memory.governance.promotable_to_vault:
            return False, "Not marked as promotable", PromotionOutcome.REJECTED_NON_CONSEQUENTIAL
        
        # Check confidence threshold
        if memory.governance.confidence < 0.85:
            return False, f"Confidence {memory.governance.confidence} < 0.85", PromotionOutcome.REJECTED_NON_CONSEQUENTIAL
        
        # Check for high-risk requiring human confirmation
        if memory.governance.sensitivity.value == "high":
            if not memory.source.origin.value == "user":
                return False, "High-risk requires human assertion", PromotionOutcome.HELD_PENDING_HUMAN_CONFIRMATION
        
        # Check for vault-worthy signals
        vault_signals = [
            "decided", "decision", "approved", "architecture",
            "policy", "governance", "sovereign", "hold", "refused",
            "sealed", "released", "verified", "constitutional",
        ]
        
        text = f"{memory.title} {memory.content}".lower()
        has_signal = any(sig in text for sig in vault_signals)
        
        if not has_signal:
            return False, "No vault-worthy signals", PromotionOutcome.REJECTED_NON_CONSEQUENTIAL
        
        # Check memory type
        if memory.memory_type == MemoryType.CONSTITUTIONAL:
            return True, "Constitutional rule", PromotionOutcome.ELIGIBLE_FOR_SEAL
        
        if memory.memory_type == MemoryType.SEMANTIC:
            if "arifos" in text and ("vault" in text or "memory" in text or "architecture" in text):
                return True, "Core architecture doctrine", PromotionOutcome.ELIGIBLE_FOR_SEAL
        
        if memory.memory_type == MemoryType.EPISODIC:
            if "decided" in text or "decision" in text:
                return True, "Recorded decision", PromotionOutcome.ELIGIBLE_FOR_SEAL
        
        return False, "Does not meet promotion criteria", PromotionOutcome.REJECTED_NON_CONSEQUENTIAL
    
    def promote(self, memory_id: str, session_id: str, force: bool = False) -> PromotionResult:
        """
        Promote a memory record to vault with explicit outcome.
        """
        # Find memory
        memory = None
        for lane in [self.memory.working, self.memory.episodic, self.memory.semantic]:
            mem = lane._memories.get(memory_id)
            if mem:
                memory = mem
                break
        
        if not memory:
            return PromotionResult(
                outcome=PromotionOutcome.REJECTED_NON_CONSEQUENTIAL,
                memory_id=memory_id,
                reason="Memory not found"
            )
        
        # Classify
        should_promote, reason, preliminary = self.classify_for_promotion(memory)
        
        if not should_promote and not force:
            return PromotionResult(
                outcome=preliminary,
                memory_id=memory_id,
                reason=reason
            )
        
        # Check if already has vault seal ref (supersession check)
        if memory.lineage.vault_seal_ref:
            # Check if vault entry exists and is valid
            existing = self.vault.get_entry(memory.lineage.vault_seal_ref)
            if existing:
                # Check if content changed significantly
                new_content_hash = hash(memory.content) % (2**32)
                old_content_hash = hash(existing.candidate_action) % (2**32)
                
                if new_content_hash != old_content_hash:
                    # This is a supersession
                    return self._supersede_vault_entry(memory, existing, session_id)
                else:
                    return PromotionResult(
                        outcome=PromotionOutcome.SEALED,
                        memory_id=memory_id,
                        vault_id=existing.vault_id,
                        reason="Already sealed with identical content"
                    )
        
        # Build vault entry
        entry = self._memory_to_vault_entry(memory, session_id)
        
        # Seal to vault
        receipt = self.vault.seal(entry)
        
        if receipt:
            # Update memory with vault reference
            memory.lineage.vault_seal_ref = receipt.vault_id
            memory.governance.confidence_class = ConfidenceClass.SEALED_FROM_VAULT
            memory.retrieval.vault_backed = True
            
            # Write receipt back to memory
            self._write_vault_receipt(memory, receipt)
            
            return PromotionResult(
                outcome=PromotionOutcome.SEALED,
                memory_id=memory_id,
                vault_id=receipt.vault_id,
                seal_receipt=receipt,
                reason=f"Successfully sealed: {reason}"
            )
        else:
            return PromotionResult(
                outcome=PromotionOutcome.HELD_PENDING_HUMAN_CONFIRMATION,
                memory_id=memory_id,
                reason="Vault seal failed — requires manual review"
            )
    
    def _supersede_vault_entry(
        self,
        memory: MemoryRecord,
        old_vault_entry: VaultEntry,
        session_id: str,
    ) -> PromotionResult:
        """Supersede existing vault entry with new version."""
        # Build new vault entry
        new_entry = self._memory_to_vault_entry(memory, session_id)
        
        # Mark as superseding
        new_entry.lineage.supersedes = old_vault_entry.vault_id
        
        # Seal new entry
        receipt = self.vault.seal(new_entry)
        
        if receipt:
            # Update memory
            memory.lineage.vault_seal_ref = receipt.vault_id
            
            return PromotionResult(
                outcome=PromotionOutcome.SUPERSEDED,
                memory_id=memory.memory_id,
                vault_id=receipt.vault_id,
                seal_receipt=receipt,
                reason=f"Superseded vault entry {old_vault_entry.vault_id}"
            )
        
        return PromotionResult(
            outcome=PromotionOutcome.HELD_PENDING_HUMAN_CONFIRMATION,
            memory_id=memory.memory_id,
            reason="Supersession failed"
        )
    
    def _memory_to_vault_entry(self, memory: MemoryRecord, session_id: str) -> VaultEntry:
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
        elif "partial" in memory.content.lower():
            verdict = Verdict.PARTIAL
        else:
            verdict = Verdict.APPROVED
        
        return VaultEntry(
            vault_id="",  # Assigned by vault
            record_type=record_type,
            verdict=verdict,
            candidate_action=memory.title,
            evidence=Evidence(
                summary=memory.summary or memory.content[:200],
                evidence_refs=[memory.memory_id],
                evidence_hash=str(hash(memory.content) % (2**32)),
            ),
            governance=Governance(
                risk_tier=memory.governance.sensitivity.value,
                judgment_required=True,
                human_confirmed=memory.source.origin.value == "user",
                decision_authority="ARIF" if memory.source.origin.value == "user" else "SYSTEM",
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
            content=(
                f"Memory promoted to vault. "
                f"Vault ID: {receipt.vault_id}. "
                f"Record hash: {receipt.record_hash[:16]}... "
                f"Timestamp: {receipt.timestamp.isoformat()}"
            ),
            source=memory.source,
            project=memory.scope.project,
        )
    
    async def process_session_for_promotion(self, session_id: str) -> list[PromotionResult]:
        """
        Scan session memories and promote consequential ones.
        Returns list of promotion results with explicit outcomes.
        """
        results = []
        
        # Check episodic memories
        for memory in self.memory.episodic._memories.values():
            if memory.source.session_id == session_id:
                result = self.promote(memory.memory_id, session_id)
                results.append(result)
        
        # Check semantic memories
        for memory in self.memory.semantic._memories.values():
            if (datetime.utcnow() - memory.time.updated_at).seconds < 3600:
                result = self.promote(memory.memory_id, session_id)
                results.append(result)
        
        # Check constitutional rules requiring vault mirror
        for memory in self.memory.constitutional.get_rules_requiring_vault_mirror():
            result = self.promote(memory.memory_id, session_id)
            results.append(result)
        
        return results
    
    def get_promotion_summary(self, results: list[PromotionResult]) -> dict:
        """Summarize promotion results."""
        summary = {
            "total": len(results),
            "sealed": 0,
            "superseded": 0,
            "eligible": 0,
            "held": 0,
            "rejected": 0,
            "vault_ids": [],
        }
        
        for r in results:
            if r.outcome == PromotionOutcome.SEALED:
                summary["sealed"] += 1
                if r.vault_id:
                    summary["vault_ids"].append(r.vault_id)
            elif r.outcome == PromotionOutcome.SUPERSEDED:
                summary["superseded"] += 1
            elif r.outcome == PromotionOutcome.ELIGIBLE_FOR_SEAL:
                summary["eligible"] += 1
            elif r.outcome == PromotionOutcome.HELD_PENDING_HUMAN_CONFIRMATION:
                summary["held"] += 1
            elif r.outcome == PromotionOutcome.REJECTED_NON_CONSEQUENTIAL:
                summary["rejected"] += 1
        
        return summary
