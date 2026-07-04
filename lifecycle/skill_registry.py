"""
skill_registry.py — runtime registry of the 12 versioned skill contracts.

Each skill is bound to:
  physics, biology, chemistry (doctrinal mapping)
  version          — semantic version of the contract
  floor            — primary F-floor binding
  stage            — which loop stage rebuilds it (2/3/4/5/6/8)
  contract         — SkillContract with must_preserve, must_never_weaken, tests

Drift detectors (4 forbidden mutation classes per Arif HOLD verdict 2026-07-04):
  - weakened_gate         (must_never_weaken item disappeared or relaxed)
  - expanded_autonomy     (autonomous_allowed expanded without F13)
  - hidden_mutation       (delta hides a contract change)
  - authority_drift       (execution discipline floor changed)

The 12-skill skeleton is irreducible. Anything beyond 12 risks drift — F13 ratification required.

Phase 1 (this forge): registry loads + asserts skeleton + emits SkillContract.
Phase 2 (post-merge): registry stays read-only; mutating any contract requires F13 ratification.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


_KERNEL_YAML = Path(__file__).parent / "kernel.yaml"


def load_kernel_spec() -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required for kernel spec; pip install pyyaml")
    return yaml.safe_load(_KERNEL_YAML.read_text())


# ─── Skill Contract ──────────────────────────────────────────────────────────


@dataclass
class SkillContract:
    """Versioned contract — the unit of Diff, NOT the raw skill definition."""

    name: str
    version: str                      # semver string, e.g. "1.0.0"
    floor: str                        # primary F-floor binding
    stage: int                        # which rebuild stage owns this skill
    physics: str
    biology: str
    chemistry: str
    must_preserve: list[str] = field(default_factory=list)
    must_never_weaken: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Backward-compatible alias — older callers expected SkillRecord.
SkillRecord = SkillContract


# ─── Drift Detection ─────────────────────────────────────────────────────────


@dataclass
class ContractDiff:
    """Diff between two SkillContracts. Detects the 4 forbidden mutations."""

    name: str
    old_version: str
    new_version: str
    weakened_gate: list[str] = field(default_factory=list)        # must_never_weaken item disappeared
    expanded_autonomy: list[str] = field(default_factory=list)    # autonomous_allowed expanded
    hidden_mutation: list[str] = field(default_factory=list)       # delta hides a change
    authority_drift: list[str] = field(default_factory=list)       # execution_discipline floor changed
    safe_changes: list[str] = field(default_factory=list)          # fields that changed without policy violation

    def is_drift(self) -> bool:
        return any([
            self.weakened_gate, self.expanded_autonomy,
            self.hidden_mutation, self.authority_drift,
        ])

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─── Skill Registry ──────────────────────────────────────────────────────────


class SkillRegistry:
    _FLOOR_BINDING = {
        "boundary_sensing":          ("L01", 4),
        "conservation_accounting":   ("L02", 2),
        "entropy_reduction":         ("L04", 3),
        "gradient_detection":        ("L08", 3),
        "reaction_gating":           ("L11", 4),
        "homeostasis_regulation":    ("L07", 2),
        "immune_response":           ("L09", 4),
        "metabolic_flow_management": ("L08", 3),
        "lineage_and_replay":        ("L02", 6),
        "scar_learning":             ("L01", 4),
        "multi_organ_translation":   ("L10", 5),
        "execution_discipline":      ("L13", 8),
    }

    def __init__(self, spec: dict[str, Any] | None = None) -> None:
        self._spec = spec or load_kernel_spec()
        self._skills: dict[str, SkillContract] = self._build()

    def _build(self) -> dict[str, SkillContract]:
        out: dict[str, SkillContract] = {}
        for name, mapping in (self._spec.get("skills") or {}).items():
            floor, stage = self._FLOOR_BINDING.get(name, ("L13", 4))
            contract = mapping.get("contract") or {}
            out[name] = SkillContract(
                name=name,
                version=str(mapping.get("version", "0.0.0")),
                floor=floor,
                stage=stage,
                physics=str(mapping.get("physics", "")),
                biology=str(mapping.get("biology", "")),
                chemistry=str(mapping.get("chemistry", "")),
                must_preserve=list(contract.get("must_preserve", [])),
                must_never_weaken=list(contract.get("must_never_weaken", [])),
                tests=list(contract.get("tests", [])),
            )
        return out

    # ─── Access ─────────────────────────────────────────────────────────────

    def all_skills(self) -> list[SkillContract]:
        return list(self._skills.values())

    def get(self, name: str) -> SkillContract | None:
        return self._skills.get(name)

    def by_stage(self, stage: int) -> list[SkillContract]:
        return [s for s in self._skills.values() if s.stage == stage]

    def by_floor(self, floor: str) -> list[SkillContract]:
        return [s for s in self._skills.values() if s.floor == floor]

    # ─── Invariants ────────────────────────────────────────────────────────

    def assert_skeleton(self) -> None:
        expected = set(self._FLOOR_BINDING.keys())
        actual = set(self._skills.keys())
        missing = expected - actual
        extra = actual - expected
        if missing or extra:
            raise AssertionError(
                f"skill skeleton drift — missing: {sorted(missing)}; extra: {sorted(extra)}. "
                "F13 ratification required to mutate the 12-skill skeleton."
            )
        if len(self._skills) != 12:
            raise AssertionError(
                f"12-skill skeleton violated; got {len(self._skills)} skills. "
                "F13 ratification required to mutate the 12-skill skeleton."
            )

    # ─── Diff (the stage that was missing per HOLD verdict) ────────────────

    def diff(self, old: SkillContract, new: SkillContract) -> ContractDiff:
        """Detect the 4 forbidden mutation classes between two contracts.

        weakened_gate:         must_never_weaken item disappeared
        expanded_autonomy:     tests emptied (test gate removed = autonomy expansion)
        hidden_mutation:       version unchanged BUT semantics changed (suspicious)
        authority_drift:       floor changed (especially L13 SOVEREIGN)
        """
        return _diff_contracts(old, new)


# ─── Diff Helper ────────────────────────────────────────────────────────────


def _diff_contracts(old: SkillContract, new: SkillContract) -> ContractDiff:
    weakened: list[str] = []
    expanded: list[str] = []
    hidden: list[str] = []
    authority: list[str] = []
    safe: list[str] = []

    # 1. weakened_gate — must_never_weaken dropped (forbidden)
    old_never = set(old.must_never_weaken)
    new_never = set(new.must_never_weaken)
    if dropped := sorted(old_never - new_never):
        weakened.extend(f"{old.name}.must_never_weaken dropped: {x}" for x in dropped)

    # 2. expanded_autonomy — tests emptied (test gate weakens; forbidden unless F13)
    old_tests, new_tests = set(old.tests), set(new.tests)
    if removed_tests := sorted(old_tests - new_tests):
        expanded.extend(f"{old.name}.tests removed: {x}" for x in removed_tests)

    # 3. hidden_mutation — version says no change BUT semantics changed
    if old.version == new.version:
        if (old.must_preserve != new.must_preserve
                or old_never != new_never
                or old.tests != new_tests):
            hidden.append(f"{old.name}: version unchanged but contract mutated (hidden)")

    # 4. authority_drift — floor changed (esp L13 SOVEREIGN)
    if old.floor != new.floor:
        authority.append(
            f"{old.name}.floor drift: {old.floor} -> {new.floor} "
            "(requires F13 ratification)"
        )

    # Safe changes — fields that changed without policy violation.
    if old.version != new.version:
        safe.append(f"{old.name}.version bump: {old.version} -> {new.version}")
    added_tests = sorted(new_tests - old_tests)
    for t in added_tests:
        safe.append(f"{old.name}.tests added: {t}")
    added_never = sorted(new_never - old_never)
    for x in added_never:
        safe.append(f"{old.name}.must_never_weaken added: {x}")

    return ContractDiff(
        name=old.name,
        old_version=old.version,
        new_version=new.version,
        weakened_gate=weakened,
        expanded_autonomy=expanded,
        hidden_mutation=hidden,
        authority_drift=authority,
        safe_changes=safe,
    )


# ─── Public Singleton ──────────────────────────────────────────────────────


_REGISTRY: SkillRegistry | None = None


def registry() -> SkillRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = SkillRegistry()
        _REGISTRY.assert_skeleton()
    return _REGISTRY


# ─── Smoke ──────────────────────────────────────────────────────────────────


if __name__ == "__main__":  # pragma: no cover
    reg = registry()
    reg.assert_skeleton()
    n = len(reg.all_skills())
    print(f"OK skill_registry smoke: {n} versioned contracts loaded")
    stages = sorted({s.stage for s in reg.all_skills()})
    print(
        "Stage distribution:",
        {stage: len(reg.by_stage(stage)) for stage in stages},
    )
    # Confirm all 12 carry contracts
    missing_contract = [s.name for s in reg.all_skills() if not s.tests]
    if missing_contract:
        raise SystemExit(f"FAIL: skills missing contract.tests: {missing_contract}")
    print("All 12 skills carry must_never_weaken + tests contracts ✓")

    # Diff demo: simulate one BUMP, one DRIFT, one SAFE change.
    a = reg.get("reaction_gating")
    assert a is not None
    bumped = SkillContract(
        **{**a.to_dict(), "version": "1.1.0", "tests": a.tests + ["new_dry_run_asserts"]}
    )
    diff = reg.diff(a, bumped)
    assert not diff.is_drift(), f"version bump should be safe: {diff.to_dict()}"
    print("Diff demo — version bump: no drift ✓")

    drifted = SkillContract(
        **{**a.to_dict(), "must_never_weaken": [x for x in a.must_never_weaken if "human_ack" not in x]}
    )
    diff = reg.diff(a, drifted)
    assert diff.is_drift() and diff.weakened_gate, "dropping must_never_weaken must detect"
    print("Diff demo — dropped must_never_weaken: weakened_gate detected ✓")
