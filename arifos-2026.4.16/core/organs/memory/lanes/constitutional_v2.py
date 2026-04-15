"""
Constitutional Memory Lane v2 — Nearly Read-Only

Behavior:
- Append rarely
- Modify only by sovereign act (888_JUDGE)
- Version every change
- Mirror critical changes into vault
- Never decay automatically
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..types_v2 import (
    MemoryRecord, MemoryType, Source, Scope, Governance, Time,
    RetentionClass, DecayPolicy, ConfidenceClass, ContestedStatus
)


@dataclass
class ConstitutionalVersion:
    """Version tracking for constitutional rules."""
    version: str  # e.g., "v1.2.3"
    amended_at: datetime
    amended_by: str
    amendment_reason: str
    prev_version: Optional[str]
    rule_hash: str  # Hash of rule content


@dataclass
class ConstitutionalMemoryLane:
    """
    Constitutional memory — core rules, nearly immutable.
    
    Rules:
    1. Read on every operation
    2. Written only by 888_JUDGE or constitutional amendment
    3. Every change is versioned
    4. Critical changes mirrored to vault
    5. Never auto-expire
    """
    
    _memories: dict[str, MemoryRecord] = field(default_factory=dict)
    _rule_index: dict[str, str] = field(default_factory=dict)  # rule_id -> memory_id
    _versions: dict[str, list[ConstitutionalVersion]] = field(default_factory=dict)
    _current_version: dict[str, str] = field(default_factory=dict)  # rule_id -> version
    
    def __post_init__(self):
        """Initialize with core constitutional rules."""
        self._initialize_core_rules()
    
    def _initialize_core_rules(self):
        """Load immutable constitutional rules (Genesis)."""
        core_rules = [
            {
                "rule_id": "F1_AMANAH",
                "title": "F1 Amanah: Reversibility",
                "content": "All actions must be reversible or auditable. Irreversible actions require human approval.",
                "priority": 1.0,
            },
            {
                "rule_id": "F2_TRUTH",
                "title": "F2 Truth: Accuracy",
                "content": "Prioritize factual accuracy. If uncertain, say 'Estimate Only' or 'Cannot Compute'.",
                "priority": 1.0,
            },
            {
                "rule_id": "F4_CLARITY",
                "title": "F4 Clarity: Entropy Reduction",
                "content": "Responses must reduce confusion (ΔS ≤ 0). Entropy increase is constitutionally forbidden.",
                "priority": 1.0,
            },
            {
                "rule_id": "F7_HUMILITY",
                "title": "F7 Humility: Bounded Uncertainty",
                "content": "Maintain uncertainty in [0.03, 0.05]. Not arrogant (Ω < 0.03), not paralyzed (Ω > 0.05).",
                "priority": 1.0,
            },
            {
                "rule_id": "F13_SOVEREIGN",
                "title": "F13 Sovereign: Human Authority",
                "content": "888_JUDGE can override ANY verdict. Human sovereignty is outside the floor system.",
                "priority": 1.0,
            },
        ]
        
        for rule in core_rules:
            self._create_genesis_rule(
                rule_id=rule["rule_id"],
                title=rule["title"],
                content=rule["content"],
                priority=rule["priority"],
            )
    
    def _create_genesis_rule(
        self,
        rule_id: str,
        title: str,
        content: str,
        priority: float,
    ) -> MemoryRecord:
        """Create a genesis constitutional rule (v1.0.0)."""
        memory_id = f"mem_const_{rule_id}_v1.0.0"
        version = "v1.0.0"
        
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=MemoryType.CONSTITUTIONAL,
            title=title,
            content=content,
            source=Source(
                origin="system",
                session_id="GENESIS",
            ),
            scope=Scope(
                owner="888_JUDGE",
                domain="arifOS",
            ),
            governance=Governance(
                confidence=1.0,
                confidence_class=ConfidenceClass.ASSERTED_BY_HUMAN,  # Genesis = sovereign
                sensitivity="high",
                requires_confirmation=True,
                promotable_to_vault=True,
                revocable=False,
                contested=ContestedStatus.UNCONTESTED,
            ),
            decay_policy=DecayPolicy(decay_type="never"),  # NEVER decay
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=None,
            ),
            retrieval={
                "keywords": ["constitutional", "floor", rule_id.split("_")[0].lower()],
                "importance_score": priority,
                "source_weight": 0.9,
            },
            lane_data={
                "retention_class": RetentionClass.CONSTITUTIONAL.value,
                "rule_id": rule_id,
                "floor_number": rule_id.split("_")[0],
                "version": version,
                "is_genesis": True,
            }
        )
        
        # Create version record
        rule_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        version_record = ConstitutionalVersion(
            version=version,
            amended_at=datetime.utcnow(),
            amended_by="GENESIS",
            amendment_reason="Initial constitutional rule",
            prev_version=None,
            rule_hash=rule_hash,
        )
        
        self._memories[memory_id] = record
        self._rule_index[rule_id] = memory_id
        self._versions[rule_id] = [version_record]
        self._current_version[rule_id] = version
        
        return record
    
    def amend_rule(
        self,
        rule_id: str,
        new_content: str,
        amendment_authority: str,
        amendment_reason: str,
        mirror_to_vault: bool = True,
    ) -> Optional[MemoryRecord]:
        """
        Amend a constitutional rule.
        
        REQUIRES 888_JUDGE authority.
        Creates new version, marks old as superseded.
        Optionally mirrors to vault.
        """
        # Authority check
        if amendment_authority != "888_JUDGE":
            print(f"REJECTED: Only 888_JUDGE can amend constitutional rules. Got: {amendment_authority}")
            return None
        
        old_rule = self.get_rule(rule_id)
        if not old_rule:
            return None
        
        # Calculate new version
        old_version = self._current_version.get(rule_id, "v1.0.0")
        new_version = self._increment_version(old_version)
        
        memory_id = f"mem_const_{rule_id}_{new_version}"
        
        # Create amended rule
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=MemoryType.CONSTITUTIONAL,
            title=f"{old_rule.title} [{new_version}]",
            content=new_content,
            source=Source(
                origin="system",
                session_id="AMENDMENT",
            ),
            scope=Scope(
                owner=amendment_authority,
                domain="arifOS",
            ),
            governance=Governance(
                confidence=1.0,
                confidence_class=ConfidenceClass.ASSERTED_BY_HUMAN,
                sensitivity="high",
                requires_confirmation=True,
                promotable_to_vault=mirror_to_vault,
                revocable=False,
                contested=ContestedStatus.UNCONTESTED,
            ),
            decay_policy=DecayPolicy(decay_type="never"),
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=None,
            ),
            retrieval=old_rule.retrieval,
            lineage={
                "supersedes": old_rule.memory_id,
            },
            lane_data={
                "retention_class": RetentionClass.CONSTITUTIONAL.value,
                "rule_id": rule_id,
                "floor_number": rule_id.split("_")[0],
                "version": new_version,
                "is_genesis": False,
                "amended_by": amendment_authority,
                "amended_at": datetime.utcnow().isoformat(),
                "amendment_reason": amendment_reason,
                "mirror_to_vault": mirror_to_vault,
            }
        )
        
        # Mark old as superseded
        old_rule.governance.contested = ContestedStatus.SUPERSEDED
        old_rule.governance.superseded_by = memory_id
        old_rule.lineage.superseded_by = memory_id
        
        # Track version
        rule_hash = hashlib.sha256(new_content.encode()).hexdigest()[:16]
        version_record = ConstitutionalVersion(
            version=new_version,
            amended_at=datetime.utcnow(),
            amended_by=amendment_authority,
            amendment_reason=amendment_reason,
            prev_version=old_version,
            rule_hash=rule_hash,
        )
        
        self._memories[memory_id] = record
        self._rule_index[rule_id] = memory_id
        
        if rule_id not in self._versions:
            self._versions[rule_id] = []
        self._versions[rule_id].append(version_record)
        self._current_version[rule_id] = new_version
        
        print(f"Constitutional rule {rule_id} amended: {old_version} → {new_version}")
        print(f"Reason: {amendment_reason}")
        
        return record
    
    def _increment_version(self, version: str) -> str:
        """Increment semantic version."""
        # Remove 'v' prefix if present
        v = version.lstrip("v")
        parts = v.split(".")
        
        # Increment patch version
        if len(parts) == 3:
            major, minor, patch = parts
            new_patch = int(patch) + 1
            return f"v{major}.{minor}.{new_patch}"
        else:
            # Fallback
            return f"v{v}.1"
    
    def get_rule(self, rule_id: str) -> Optional[MemoryRecord]:
        """Get current version of constitutional rule."""
        memory_id = self._rule_index.get(rule_id)
        if memory_id:
            return self._memories.get(memory_id)
        return None
    
    def get_rule_version_history(self, rule_id: str) -> list[ConstitutionalVersion]:
        """Get version history for a rule."""
        return self._versions.get(rule_id, [])
    
    def get_all_rules(self) -> list[MemoryRecord]:
        """Get all current constitutional rules."""
        current = []
        for rule_id, memory_id in self._rule_index.items():
            mem = self._memories.get(memory_id)
            if mem and not mem.governance.superseded_by:
                current.append(mem)
        return current
    
    def get_floors(self) -> list[MemoryRecord]:
        """Get all floor rules (F1-F13)."""
        return [m for m in self.get_all_rules() if "F" in m.lane_data.get("floor_number", "")]
    
    def check_compliance(self, operation: str, context: dict) -> tuple[bool, list[str]]:
        """Check if operation complies with constitutional rules."""
        violations = []
        
        for rule in self.get_all_rules():
            rule_id = rule.lane_data.get("rule_id", "")
            
            if rule_id == "F1_AMANAH":
                if not context.get("is_reversible", True):
                    violations.append("F1_AMANAH: Operation not reversible")
            
            elif rule_id == "F4_CLARITY":
                delta_s = context.get("entropy_delta", 0)
                if delta_s > 0:
                    violations.append(f"F4_CLARITY: Entropy increased (ΔS = {delta_s})")
            
            elif rule_id == "F7_HUMILITY":
                omega = context.get("uncertainty", 0.04)
                if omega < 0.03 or omega > 0.05:
                    violations.append(f"F7_HUMILITY: Uncertainty {omega} outside [0.03, 0.05]")
        
        return len(violations) == 0, violations
    
    def get_rules_requiring_vault_mirror(self) -> list[MemoryRecord]:
        """Get rules that should be mirrored to vault."""
        return [
            m for m in self._memories.values()
            if m.lane_data.get("mirror_to_vault", False)
            and not m.lineage.vault_seal_ref  # Not yet mirrored
        ]
