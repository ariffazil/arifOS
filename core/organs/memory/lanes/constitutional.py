"""
Constitutional Memory Lane

Smallest and highest-trust layer.

Characteristics:
- Non-overridable rules
- Risk floors
- Role boundaries
- Hold logic
- Sovereignty markers
- Read often, written rarely
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..types import Governance, MemoryRecord, MemoryType, RetentionClass, Scope, Source, Time


@dataclass
class ConstitutionalMemoryLane:
    """
    Constitutional memory stores the highest-trust rules.
    
    This is the smallest lane but the most important.
    
    Contents:
    - Non-overridable rules (F1-F13)
    - Risk floors
    - Role boundaries
    - Hold logic
    - Sovereignty markers
    
    Rules:
    - Read on every operation
    - Written only by 888_JUDGE or constitutional amendment
    - Never auto-expire
    - Never superseded without trace
    """
    
    _memories: dict[str, MemoryRecord] = field(default_factory=dict)
    _rule_index: dict[str, str] = field(default_factory=dict)  # rule_id -> memory_id
    
    def __post_init__(self):
        """Initialize with core constitutional rules."""
        self._initialize_core_rules()
    
    def _initialize_core_rules(self):
        """Load immutable constitutional rules."""
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
            self._create_core_rule(
                rule_id=rule["rule_id"],
                title=rule["title"],
                content=rule["content"],
                priority=rule["priority"],
            )
    
    def _create_core_rule(
        self,
        rule_id: str,
        title: str,
        content: str,
        priority: float,
    ) -> MemoryRecord:
        """Create a core constitutional rule."""
        memory_id = f"mem_const_{rule_id}"
        
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
                confidence=1.0,  # Constitutional rules are absolute
                sensitivity="high",
                requires_confirmation=True,  # Changes require confirmation
                promotable_to_vault=True,  # Constitutional rules ARE vault material
                revocable=False,  # Cannot be deleted, only superseded by amendment
            ),
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=None,  # Never expires
            ),
            retrieval={
                "keywords": ["constitutional", "floor", rule_id.split("_")[0].lower()],
                "importance_score": priority,
            },
            lane_data={
                "retention_class": RetentionClass.CONSTITUTIONAL.value,
                "rule_id": rule_id,
                "floor_number": rule_id.split("_")[0],
                "amendment_version": "v1.0",
            }
        )
        
        self._memories[memory_id] = record
        self._rule_index[rule_id] = memory_id
        
        return record
    
    def get_rule(self, rule_id: str) -> MemoryRecord | None:
        """Get constitutional rule by ID."""
        memory_id = self._rule_index.get(rule_id)
        if memory_id:
            return self._memories.get(memory_id)
        return None
    
    def get_all_rules(self) -> list[MemoryRecord]:
        """Get all constitutional rules."""
        return list(self._memories.values())
    
    def get_floors(self) -> list[MemoryRecord]:
        """Get all floor rules (F1-F13)."""
        return [m for m in self._memories.values() if "F" in m.lane_data.get("floor_number", "")]
    
    def check_compliance(
        self,
        operation: str,
        context: dict,
    ) -> tuple[bool, list[str]]:
        """
        Check if operation complies with constitutional rules.
        
        Returns (is_compliant, list_of_violations).
        """
        violations = []
        
        for rule in self._memories.values():
            # Simplified check - would have actual logic per rule
            if rule.lane_data.get("rule_id") == "F1_AMANAH":
                if not context.get("is_reversible", True):
                    violations.append("F1_AMANAH: Operation not reversible")
            
            if rule.lane_data.get("rule_id") == "F4_CLARITY":
                delta_s = context.get("entropy_delta", 0)
                if delta_s > 0:
                    violations.append(f"F4_CLARITY: Entropy increased (ΔS = {delta_s})")
        
        return len(violations) == 0, violations
    
    def amend_rule(
        self,
        rule_id: str,
        new_content: str,
        amendment_authority: str,
    ) -> MemoryRecord | None:
        """
        Amend a constitutional rule.
        
        Requires 888_JUDGE authority. Creates new version, marks old as superseded.
        """
        if amendment_authority != "888_JUDGE":
            return None
        
        old_rule = self.get_rule(rule_id)
        if not old_rule:
            return None
        
        # Create amended version
        new_version = old_rule.lane_data.get("amendment_version", "v1.0")
        # Increment version
        version_parts = new_version.replace("v", "").split(".")
        new_version = f"v{version_parts[0]}.{int(version_parts[1]) + 1}"
        
        memory_id = f"mem_const_{rule_id}_{new_version}"
        
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
                sensitivity="high",
                requires_confirmation=True,
                promotable_to_vault=True,
                revocable=False,
            ),
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
                **old_rule.lane_data,
                "amendment_version": new_version,
                "amended_by": amendment_authority,
                "amended_at": datetime.utcnow().isoformat(),
            }
        )
        
        # Mark old as superseded
        old_rule.lineage.superseded_by = memory_id
        
        self._memories[memory_id] = record
        self._rule_index[rule_id] = memory_id
        
        return record
