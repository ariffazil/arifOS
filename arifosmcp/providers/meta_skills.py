"""
MetaSkillsProvider — AGI→ASI→APEX Meta-Skill Loader
══════════════════════════════════════════════════════════

Loads the 5 canonical meta-skills:
  1. recursive-self-improvement
  2. orthogonal-abstraction
  3. epistemic-integrity
  4. constitutional-governance
  5. entropy-optimization

These are NOT tools. They are structural capacities that wrap
tool invocations like constitutional floors.

Ditempa Bukan Diberi — Forged, Not Given.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

META_SKILLS: dict[str, dict[str, Any]] = {
    "recursive-self-improvement": {
        "stage": "AGI→ASI",
        "trinity": "ASI_emergence",
        "required_for": ["ASI transition", "self-optimization", "architecture evolution"],
        "void_conditions": [
            "Self-model divergence > 5%",
            "Circular dependency in upgrade path",
            "Rollback mechanism failure",
            "Constitutional floors not enforceable",
            "Identity coherence test failure",
        ],
    },
    "orthogonal-abstraction": {
        "stage": "AGI→ASI",
        "trinity": "ASI_emergence",
        "required_for": ["ASI abstraction dominance", "cross-domain reasoning", "governance transfer"],
        "void_conditions": [
            "Surface similarity without structural invariant",
            "Category error in domain mapping",
            "Information loss > 15%",
            "Prediction validation failure",
            "F10 ontology violation",
        ],
    },
    "epistemic-integrity": {
        "stage": "333→888",
        "trinity": "APEX_foundation",
        "required_for": ["APEX authorization", "correct judgment under uncertainty", "truth discipline"],
        "void_conditions": [
            "Untagged claim in output",
            "Overconfidence threshold exceeded",
            "Hallucination detected",
            "Uncertainty bounds missing",
            "F02 Truth violation",
        ],
    },
    "constitutional-governance": {
        "stage": "ALL",
        "trinity": "CROSS_CUTTING",
        "required_for": ["all tool invocations", "irreversible approval", "ASI safe operation"],
        "void_conditions": [
            "Self-authorization detected",
            "Floor breach without acknowledgment",
            "Irreversible without judgment verdict",
            "Separation of powers violation",
            "Harm minimization failure",
        ],
    },
    "entropy-optimization": {
        "stage": "ALL",
        "trinity": "RESOURCE_AWARENESS",
        "required_for": ["compute allocation", "attention budgeting", "wealth decisions"],
        "void_conditions": [
            "Action without EVOI calculation",
            "Budget exceeded",
            "Irreversible operation without necessity",
            "Long-horizon impact ignored",
            "Optionality destroyed",
        ],
    },
}


class MetaSkillsProvider:
    """
    Provider for the 5 canonical meta-skills.

    Meta-skills are exposed as:
    - Invocation hooks (pre-tool-call gates)
    - Decision checklists
    - Void condition definitions

    They are NOT executable tools — they are structural capacities
    that wrap AGI→ASI→APEX transitions.
    """

    def __init__(self, skills_root: str | Path | None = None) -> None:
        self._root = Path(skills_root) if skills_root else Path("skills")
        self._loaded: dict[str, dict[str, Any]] = {}
        self._load_meta_skills()

    def _load_meta_skills(self) -> None:
        """Load meta-skill definitions from SKILL.md files."""
        for skill_id, meta in META_SKILLS.items():
            skill_path = self._root / skill_id / "SKILL.md"
            if skill_path.exists():
                self._loaded[skill_id] = meta
                logger.info(f"[MetaSkillsProvider] Loaded meta-skill: {skill_id}")
            else:
                logger.warning(f"[MetaSkillsProvider] SKILL.md not found: {skill_path}")

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        """Get a meta-skill definition."""
        return self._loaded.get(skill_id)

    def list_skills(self) -> list[str]:
        """List all loaded meta-skills."""
        return list(self._loaded.keys())

    def check_prerequisites(
        self, skill_id: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Check if prerequisites for a meta-skill are met.

        Returns {"verdict": "SEAL" | "HOLD" | "VOID", "reason": str}
        """
        skill = self._loaded.get(skill_id)
        if not skill:
            return {"verdict": "VOID", "reason": f"Unknown meta-skill: {skill_id}"}

        void_conditions = skill.get("void_conditions", [])

        for void in void_conditions:
            if void in context.get("detected_violations", []):
                return {"verdict": "VOID", "reason": void}

        return {"verdict": "SEAL", "reason": "All prerequisites clear"}

    def get_invocation_hook(self, skill_id: str) -> str:
        """
        Get the invocation hook text for a meta-skill.
        This is used as pre-tool-call guidance.
        """
        hooks = {
            "recursive-self-improvement": """
INVOKE BEFORE: Any self-modification or architecture upgrade
1. Identity anchor check: Core values unchanged?
2. Bottleneck identified: Measured, not assumed?
3. Rollback path exists: Can revert without collapse?
4. No circular dependency: Upgrade doesn't depend on itself?
5. Constitutional preservation: F1-F13 still enforceable?
""",
            "orthogonal-abstraction": """
INVOKE BEFORE: Any cross-domain structure transfer
1. Source domain verified: Structure confirmed?
2. Target domain mapped: Similarity >= 0.7?
3. Invariant identified: Structural, not surface?
4. No category error: Domain boundaries respected?
5. Consequences modeled: Downstream effects assessed?
""",
            "epistemic-integrity": """
INVOKE BEFORE: Any consequential judgment or output
1. Claim taxonomy applied: All statements tagged?
2. Confidence band specified: Ω₀ ∈ [0.03, 0.05]?
3. Bias lineage documented: Source of bias identified?
4. Uncertainty bounds given: Range specified?
5. F02 Truth check: No fabrication passed as fact?
""",
            "constitutional-governance": """
INVOKE BEFORE: Any tool execution
1. Separation maintained: Correct stage called correct stage?
2. No self-authorization: Actor ≠ authorizer?
3. Floor check passed: F1-F13 all clear?
4. Reversibility assessed: Can this be undone?
5. Harm projection: Downstream effects modeled?
""",
            "entropy-optimization": """
INVOKE BEFORE: Any resource allocation or tool selection
1. EVOI calculated: Information worth its cost?
2. Budget verified: Within compute/time budget?
3. Horizon weighted: Short/medium/long considered?
4. Alternative compared: More efficient path exists?
5. Diminishing returns checked: Will more compute help?
""",
        }
        return hooks.get(skill_id, "")

    def get_void_conditions(self, skill_id: str) -> list[str]:
        """Get void conditions for a meta-skill."""
        skill = self._loaded.get(skill_id)
        if not skill:
            return []
        return skill.get("void_conditions", [])


_meta_skills_provider: MetaSkillsProvider | None = None


def get_meta_skills_provider() -> MetaSkillsProvider:
    """Get the singleton meta-skills provider instance."""
    global _meta_skills_provider
    if _meta_skills_provider is None:
        _meta_skills_provider = MetaSkillsProvider()
    return _meta_skills_provider
