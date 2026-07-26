"""
arifosmcp/schemas/agent_contract.py — CANONICAL AGENT CONTRACT (P5)
═══════════════════════════════════════════════════════════════════

Defines every organ as a capability-backed specialist agent.
Organs stop being mini-kernels. Each agent declares:
  - What it CAN do (capabilities)
  - What it MUST NOT do (authority_boundary)
  - What authority level it requires

Corresponds to Arif's §1F analysis: "roles are currently mixed between
agents, organs, tools, lanes, and governance states."

Fix: define agents by capability, not mythology.

Forged: 2026-07-26 under Arif's P5 directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

AgentRole = Literal[
    "Observer",
    "WorldModel",
    "Planner",
    "Critic",
    "Governor",
    "Executor",
    "Archivist",
]


@dataclass
class AgentCapability:
    """A single capability declared by an agent."""

    capability_id: str  # "reality.observe.geology"
    description: str
    risk_class: str  # LOW, MEDIUM, HIGH, CRITICAL
    reversibility: str  # FULL, PARTIAL, NONE
    authority_required: str  # SOVEREIGN, TRUSTED_AGENT, EXECUTOR, OBSERVER
    mutations_allowed: bool = False


@dataclass
class Agent:
    """Canonical agent contract.

    Every organ in the federation is an agent with:
      - One role (Observer, Executor, etc.)
      - Declared capabilities
      - Authority boundaries (what it MUST NOT do)
    """

    id: str
    name: str
    role: AgentRole
    description: str
    capabilities: list[AgentCapability] = field(default_factory=list)
    authority_boundary: list[str] = field(default_factory=list)
    port: int | None = None
    reflects_only: bool = False  # WELL-constraint: REFLECT_ONLY, never adjudicate

    def can_do(self, capability_id: str) -> bool:
        return any(c.capability_id == capability_id for c in self.capabilities)

    def must_not(self, verb: str) -> bool:
        return any(verb in b.lower() for b in self.authority_boundary)


# ═══════════════════════════════════════════════════════════════════════════════
# THE SEVEN CANONICAL AGENTS
# ═══════════════════════════════════════════════════════════════════════════════

ARIFOS_KERNEL = Agent(
    id="arifos",
    name="arifOS",
    role="Governor",
    description="Constitutional kernel — judges, seals, governs. NEVER executes.",
    capabilities=[
        AgentCapability("session.bind", "Bind session and identity", "LOW", "FULL", "ANONYMOUS"),
        AgentCapability(
            "reality.observe", "Observe reality, fetch evidence", "LOW", "FULL", "OBSERVER"
        ),
        AgentCapability("cognition.think", "Reason, plan, critique", "LOW", "FULL", "OBSERVER"),
        AgentCapability("intent.route", "Route intent to correct organ", "LOW", "FULL", "OBSERVER"),
        AgentCapability(
            "memory.govern",
            "Governed memory recall and storage",
            "MEDIUM",
            "FULL",
            "TRUSTED_AGENT",
            mutations_allowed=True,
        ),
        AgentCapability(
            "authority.judge", "Constitutional verdict", "HIGH", "NONE", "TRUSTED_AGENT"
        ),
        AgentCapability(
            "action.execute",
            "Governed execution dispatch",
            "HIGH",
            "FULL",
            "EXECUTOR",
            mutations_allowed=True,
        ),
        AgentCapability(
            "history.seal",
            "Immutable VAULT999 append",
            "CRITICAL",
            "NONE",
            "SOVEREIGN",
            mutations_allowed=True,
        ),
    ],
    authority_boundary=[
        "NEVER execute directly",
        "NEVER self-authorize",
        "NEVER bypass F13 sovereign",
    ],
    port=8088,
)

GEOX_AGENT = Agent(
    id="geox",
    name="GEOX",
    role="Observer",
    description="Earth intelligence agent — seismic, petrophysics, basin, prospect. Observes and computes earth evidence. NEVER judges or executes.",
    capabilities=[
        AgentCapability(
            "reality.observe.geology",
            "Seismic interpretation and well log analysis",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.basin",
            "Basin analysis, backstripping, thermal maturity",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.petrophysics",
            "Vsh, porosity, Sw, permeability, net pay",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.prospect",
            "Prospect evaluation, volumetrics, POS",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.falsify",
            "Popperian falsification — Kill Matrix K001-K007",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
    ],
    authority_boundary=[
        "NEVER judge — no seal authority",
        "NEVER execute — no mutation",
        "NEVER decide capital allocation",
        "NEVER claim >0.90 confidence (F7 humility)",
    ],
    port=8081,
)

WEALTH_AGENT = Agent(
    id="wealth",
    name="WEALTH",
    role="Observer",
    description="Capital intelligence agent — NPV, IRR, EMV, portfolio, institutional stress. Computes, NEVER allocates.",
    capabilities=[
        AgentCapability(
            "cognition.compute.capital",
            "NPV, IRR, EMV, Monte Carlo, Kelly, Markowitz",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.market",
            "FX, commodity, stock, bond market data",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "cognition.assess.stress",
            "Institutional stress index, governance capacity, cascade",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "cognition.synthesize.wisdom",
            "Capital wisdom — dignity, sovereignty, resilience evaluation",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
    ],
    authority_boundary=[
        "NEVER allocate capital",
        "NEVER judge — no seal authority",
        "NEVER execute trades or transactions",
        "NEVER override sovereign evaluation",
    ],
    port=18082,
)

WELL_AGENT = Agent(
    id="well",
    name="WELL",
    role="Observer",
    description="Human readiness agent — vitality, fatigue, dignity. REFLECT_ONLY — never diagnoses, never adjudicates.",
    capabilities=[
        AgentCapability(
            "reality.observe.vitality",
            "Assess homeostasis — sleep, fatigue, stress",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.dignity",
            "Guard dignity, consent, coercion detection",
            "CRITICAL",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "reality.observe.substrate",
            "Classify substrate, validate readiness",
            "HIGH",
            "FULL",
            "OBSERVER",
        ),
    ],
    authority_boundary=[
        "NEVER diagnose — reflects only",
        "NEVER adjudicate — no decision authority",
        "NEVER mutate state",
        "NEVER seal — no vault access",
    ],
    port=18083,
    reflects_only=True,
)

AFORGE_AGENT = Agent(
    id="a-forge",
    name="A-FORGE",
    role="Executor",
    description="Sole execution actuator — builds, deploys, mutates. Executes ONLY after SEAL verdict from Governor. NEVER judges self.",
    capabilities=[
        AgentCapability(
            "action.execute.build",
            "Build, compile, test",
            "MEDIUM",
            "FULL",
            "EXECUTOR",
            mutations_allowed=True,
        ),
        AgentCapability(
            "action.execute.deploy",
            "Deploy, rsync, restart services",
            "HIGH",
            "PARTIAL",
            "EXECUTOR",
            mutations_allowed=True,
        ),
        AgentCapability(
            "action.execute.shell",
            "Governed shell execution",
            "HIGH",
            "PARTIAL",
            "EXECUTOR",
            mutations_allowed=True,
        ),
        AgentCapability(
            "action.execute.vps",
            "VPS lifecycle — start, stop, restart",
            "CRITICAL",
            "PARTIAL",
            "EXECUTOR",
            mutations_allowed=True,
        ),
    ],
    authority_boundary=[
        "NEVER judge — cannot self-authorize",
        "NEVER seal — no vault authority",
        "NEVER plan — execution only",
        "NEVER execute without SEAL verdict",
        "NEVER execute IRREVERSIBLE without F13 acknowledgment",
    ],
    port=7071,
)

AAA_AGENT = Agent(
    id="aaa",
    name="AAA",
    role="WorldModel",
    description="Control plane coordinator — cockpit, agent registry, A2A gateway. Routes, coordinates, displays. NEVER acts as judge or executor.",
    capabilities=[
        AgentCapability(
            "coordinate.route.a2a",
            "A2A protocol routing and agent discovery",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "coordinate.display.cockpit",
            "Cockpit dashboard and visual state",
            "LOW",
            "FULL",
            "OBSERVER",
        ),
        AgentCapability(
            "coordinate.register.agent",
            "Agent identity registration and discovery",
            "MEDIUM",
            "FULL",
            "OBSERVER",
        ),
    ],
    authority_boundary=[
        "NEVER judge — no constitutional verdict",
        "NEVER execute — no mutation",
        "NEVER seal — no vault access",
        "NEVER pretend to be judge or hand",
    ],
    port=3001,
)

VAULT999_AGENT = Agent(
    id="vault999",
    name="VAULT999",
    role="Archivist",
    description="Immutable archive — append-only, hash-chained. Records sealed truths. NEVER decides what to seal, NEVER modifies sealed records.",
    capabilities=[
        AgentCapability(
            "history.archive.seal",
            "Immutable append to hash-chained ledger",
            "CRITICAL",
            "NONE",
            "SOVEREIGN",
            mutations_allowed=True,
        ),
        AgentCapability(
            "history.archive.verify", "Chain integrity verification", "LOW", "FULL", "ANONYMOUS"
        ),
    ],
    authority_boundary=[
        "NEVER decide policy — archive only",
        "NEVER modify sealed records",
        "NEVER judge what to seal",
    ],
    port=None,  # no HTTP server — file-based + vault999 writer service
)


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_AGENTS: list[Agent] = [
    ARIFOS_KERNEL,
    GEOX_AGENT,
    WEALTH_AGENT,
    WELL_AGENT,
    AFORGE_AGENT,
    AAA_AGENT,
    VAULT999_AGENT,
]


def get_agent_by_id(agent_id: str) -> Agent | None:
    for a in ALL_AGENTS:
        if a.id == agent_id:
            return a
    return None


def get_agent_by_role(role: AgentRole) -> list[Agent]:
    return [a for a in ALL_AGENTS if a.role == role]


def validate_agent_boundaries() -> dict[str, Any]:
    """Check that no agent violates its own authority boundaries."""
    errors = []
    for agent in ALL_AGENTS:
        for cap in agent.capabilities:
            if (
                agent.role == "Governor"
                and cap.mutations_allowed
                and cap.capability_id
                not in (
                    "memory.govern",
                    "action.execute",
                    "history.seal",
                )
            ):
                errors.append(
                    f"{agent.id}({agent.role}): capability '{cap.capability_id}' has mutations_allowed=True but agent is Governor"
                )
            if agent.role == "Observer" and cap.mutations_allowed:
                errors.append(
                    f"{agent.id}({agent.role}): has mutating capability '{cap.capability_id}'"
                )
            if agent.role == "Executor" and agent.id != "a-forge":
                errors.append(f"{agent.id}: non-A-FORGE executor")
            if agent.reflects_only and cap.mutations_allowed:
                errors.append(
                    f"{agent.id}(REFLECT_ONLY): has mutating capability '{cap.capability_id}'"
                )
    return {
        "ok": not errors,
        "agent_count": len(ALL_AGENTS),
        "errors": errors,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN LAW — what each organ may and must never do
# ═══════════════════════════════════════════════════════════════════════════════

DOMAIN_LAW: dict[str, dict[str, Any]] = {
    "arifos": {
        "organ": "arifOS",
        "core_question": "Should this be allowed?",
        "law": "Constitutional law",
        "must_do": ["Judge", "Route", "Seal", "Enforce F1-F13"],
        "must_never": ["Execute domain work", "Mutate directly"],
    },
    "aaa": {
        "organ": "AAA",
        "core_question": "What is happening and who is acting?",
        "law": "State / cockpit law",
        "must_do": ["Registry", "Routing", "A2A", "Visibility"],
        "must_never": ["Adjudicate", "Execute"],
    },
    "a-forge": {
        "organ": "A-FORGE",
        "core_question": "How do we execute approved work?",
        "law": "Execution law",
        "must_do": ["Execute after SEAL", "Dry-run", "Deploy", "Verify"],
        "must_never": ["Self-authorize", "Judge"],
    },
    "geox": {
        "organ": "GEOX",
        "core_question": "What is physically real?",
        "law": "Natural law",
        "must_do": ["Earth evidence", "Wells", "Seismic", "Basin", "Prospect", "Falsification"],
        "must_never": [
            "Decide drilling",
            "Decide capital",
            "Decide medical",
            "Decide governance",
        ],
    },
    "wealth": {
        "organ": "WEALTH",
        "core_question": "What are the capital consequences?",
        "law": "Capital law",
        "must_do": [
            "NPV",
            "IRR",
            "EMV",
            "EVOI",
            "Runway",
            "Stress",
            "Entropy",
            "Capital diagnosis",
        ],
        "must_never": ["Allocate capital", "Trade", "Self-SEAL"],
    },
    "well": {
        "organ": "WELL",
        "core_question": "Can the substrate proceed?",
        "law": "Substrate law",
        "must_do": ["Reflect readiness", "Dignity", "Machine reliability", "Coupling risk"],
        "must_never": ["Diagnose", "Prescribe", "Adjudicate", "Override human self-report"],
    },
    "vault999": {
        "organ": "VAULT999",
        "core_question": "What was decided?",
        "law": "Immutable memory law",
        "must_do": ["Receipts", "Seals", "Provenance", "Hash-chain"],
        "must_never": ["Become present-tense authority"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# SEVEN FITNESS TESTS — tool survival criteria
# ═══════════════════════════════════════════════════════════════════════════════

FITNESS_TESTS: list[str] = [
    "1. Domain purity — tool stays within its organ's domain law",
    "2. Evidence/provenance — every output carries artifact hash + parser version",
    "3. Uncertainty/humility — every number carries epistemic tag, UNKNOWN not hidden",
    "4. Falsifiability — claim exposes how it can be proven wrong (Kill Matrix)",
    "5. Boundary discipline — tool does not cross into judgment, execution, or other domains",
    "6. Audit/receipt — every output has provenance trail, hash, timestamp",
    "7. arifOS handoff for judgment — tool proposes; arifOS judges; never self-seals",
]


@dataclass
class FitnessVerdict:
    """Result of running the 7 fitness tests on a tool/capability."""

    tool_name: str
    organ: str
    passed: list[str] = field(default_factory=list)  # which tests passed
    failed: list[str] = field(default_factory=list)  # which tests failed
    verdict: str = "REVIEW"  # SURVIVE | DEMOTE | KILL | REVIEW

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "organ": self.organ,
            "passed": self.passed,
            "failed": self.failed,
            "verdict": self.verdict,
        }


KILL_RULES: list[dict[str, str]] = [
    {"failure": "Tool claims authority outside its organ", "verdict": "KILL (VOID)"},
    {"failure": "Tool generates output without evidence/provenance", "verdict": "HOLD"},
    {"failure": "Tool hides uncertainty", "verdict": "HOLD"},
    {"failure": "Tool self-validates", "verdict": "HOLD"},
    {"failure": "Tool crosses from evidence to judgment", "verdict": "KILL (VOID)"},
    {"failure": "Tool mutates or executes without SEAL/lease", "verdict": "KILL (VOID)"},
    {
        "failure": "Tool creates duplicate surface or alias confusion",
        "verdict": "CONSOLIDATE / ARCHIVE",
    },
    {"failure": "Tool produces impressive narrative but no falsifier", "verdict": "ADVISORY ONLY"},
]


def evaluate_fitness(
    tool_name: str,
    organ_id: str,
    domain_pure: bool = True,
    has_provenance: bool = False,
    has_uncertainty: bool = False,
    is_falsifiable: bool = False,
    respects_boundary: bool = True,
    has_audit: bool = False,
    hands_off_to_arifos: bool = False,
) -> FitnessVerdict:
    """Run the 7 fitness tests on a tool. Returns survival verdict."""
    passed: list[str] = []
    failed: list[str] = []

    checks = [
        (domain_pure, "Domain purity"),
        (has_provenance, "Evidence/provenance"),
        (has_uncertainty, "Uncertainty/humility"),
        (is_falsifiable, "Falsifiability"),
        (respects_boundary, "Boundary discipline"),
        (has_audit, "Audit/receipt"),
        (hands_off_to_arifos, "arifOS handoff"),
    ]
    for passed_check, name in checks:
        if passed_check:
            passed.append(name)
        else:
            failed.append(name)

    fail_count = len(failed)
    if fail_count == 0:
        verdict = "SURVIVE"
    elif fail_count <= 2:
        verdict = "DEMOTE (advisory only)"
    elif fail_count <= 4:
        verdict = "HOLD (pending evidence)"
    else:
        verdict = "KILL (VOID — remove from public surface)"

    return FitnessVerdict(
        tool_name=tool_name,
        organ=organ_id,
        passed=passed,
        failed=failed,
        verdict=verdict,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-ORGAN SURVIVAL LOOP
# ═══════════════════════════════════════════════════════════════════════════════

CROSS_ORGAN_LOOP: list[str] = [
    "GEOX finds reality",
    "WEALTH prices consequence",
    "WELL checks readiness",
    "arifOS judges",
    "A-FORGE executes",
    "VAULT999 records",
    "ARIF/F13 may veto",
]

STABILIZATION_CANON: dict[str, str] = {
    "GEOX": "truth fitness",
    "WEALTH": "consequence fitness",
    "WELL": "readiness fitness",
    "arifOS": "judgment fitness",
    "A-FORGE": "execution fitness",
    "AAA": "coordination fitness",
    "VAULT999": "memory fitness",
    "ARIF": "sovereign veto",
}

SURVIVAL_RULE: str = (
    "Only tools that preserve domain purity, evidence, uncertainty, "
    "falsification, auditability, and human sovereignty survive. "
    "Everything else becomes advisory, archived, or VOID."
)

# ─── BM compression ──────────────────────────────────────────────────────────

SURVIVAL_RULE_BM: str = (
    "Yang kuat bukan tool yang paling banyak buat kerja. "
    "Yang kuat ialah tool yang paling susah menipu: "
    "ada bukti, ada had, ada audit, ada falsifier, ada manusia sebagai veto."
)


# ═══════════════════════════════════════════════════════════════════════════════
# TIER STABILIZATION — canonical tool hierarchy
# ═══════════════════════════════════════════════════════════════════════════════

STABILIZED_TIERS: dict[str, dict[str, Any]] = {
    "TIER_1_CONSTITUTIONAL": {
        "label": "Constitutional Stabilizers",
        "priority": "HARDEN FIRST",
        "tools": [
            "arif_judge",
            "arif_seal",
            "VAULT999 receipt/seal",
            "F1-F13 floor checks",
            "888_HOLD",
            "identity/session/lease checks",
        ],
    },
    "TIER_2_REALITY": {
        "label": "Reality Stabilizers (GEOX)",
        "priority": "HARDEN SECOND",
        "tools": [
            "geox_well_ingest",
            "geox_data_qc_bundle",
            "geox_petrophysics",
            "geox_seismic_ingest",
            "geox_seismic_compute",
            "geox_seismic_interpret",
            "geox_falsify",
            "geox_contradiction_scan",
            "geox_claim_graph_evaluate",
            "geox_claim",
        ],
    },
    "TIER_3_CONSEQUENCE": {
        "label": "Consequence Stabilizers (WEALTH)",
        "priority": "HARDEN THIRD",
        "tools": [
            "wealth_conservation_capital",
            "wealth_flow_liquidity",
            "wealth_survival_liquidity",
            "wealth_entropy_risk",
            "wealth_probability_monte_carlo",
            "wealth_expectation_emv",
            "wealth_energy_irr",
            "wealth_gravity_dscr",
            "wealth_inertia_leverage",
            "wealth_boundary_governance",
            "wealth_arifos_bridge",
        ],
    },
    "TIER_4_READINESS": {
        "label": "Readiness Stabilizers (WELL)",
        "priority": "HARDEN FOURTH",
        "tools": [
            "well_assess_homeostasis",
            "well_validate_vitality",
            "well_guard_dignity",
            "well_assess_reliability",
            "well_check_repair",
            "well_classify_substrate",
            "well_detect_boundary",
            "well_assess_metabolism",
            "well_compute_metabolic_flux",
            "well_trace_lineage",
        ],
    },
    "TIER_5_ADVISORY": {
        "label": "Advisory / Experimental",
        "priority": "DEMOTE TO ADVISORY",
        "tools": [
            "vision/VLM proposal tools",
            "LEM prior tools",
            "market forecast cones",
            "macro/commodity signal tools",
            "map/visualization renderers",
            "hypothesis rankers",
        ],
        "rule": "Must not become truth, judgment, or execution authority",
    },
}


# ─── UPDATED SELF-TEST ────────────────────────────────────────────────────────

if __name__ == "__main__":
    v = validate_agent_boundaries()
    print(f"Agents: {v['agent_count']}, Valid: {v['ok']}")
    if v["errors"]:
        for e in v["errors"]:
            print(f"  ❌ {e}")
    else:
        print(f"  ✅ All agent boundaries valid")

    # Domain law
    for oid, law in DOMAIN_LAW.items():
        print(f"  {law['organ']}: {law['core_question']} ({law['law']})")

    # Fitness tests
    fit = evaluate_fitness(
        tool_name="geox_falsify",
        organ_id="geox",
        domain_pure=True,
        has_provenance=True,
        has_uncertainty=True,
        is_falsifiable=True,
        respects_boundary=True,
        has_audit=True,
        hands_off_to_arifos=True,
    )
    assert fit.verdict == "SURVIVE", f"geox_falsify should survive: {fit.failed}"
    print(f"  ✅ geox_falsify → {fit.verdict} ({len(fit.passed)}/7 tests)")

    bad_fit = evaluate_fitness(
        tool_name="fake_judge",
        organ_id="geox",
        domain_pure=False,
        has_provenance=False,
        has_uncertainty=False,
        is_falsifiable=False,
        respects_boundary=False,
        has_audit=False,
        hands_off_to_arifos=False,
    )
    assert bad_fit.verdict == "KILL (VOID — remove from public surface)", (
        f"Fake judge should be killed: {bad_fit.verdict}"
    )
    print(f"  ✅ fake_judge → {bad_fit.verdict} ({len(bad_fit.failed)}/7 tests)")

    # Iron rule
    executors = [a for a in ALL_AGENTS if a.role == "Executor"]
    governors = [a for a in ALL_AGENTS if a.role == "Governor"]
    assert len(executors) == 1 and executors[0].id == "a-forge", "A-FORGE must be sole executor"
    assert len(governors) == 1 and governors[0].id == "arifos", "arifOS must be sole governor"
    print(f"\n✅ Iron Rule: A-FORGE sole executor, arifOS sole governor")
    print(f"✅ Cross-organ loop: {' → '.join(CROSS_ORGAN_LOOP)}")
    print(f"✅ Stabilized tiers: {len(STABILIZED_TIERS)} tiers defined")
    print(f"✅ 7 fitness tests active, {len(KILL_RULES)} kill rules")
    print(f"✅ P5: Organ boundaries + domain law + fitness tests + survival rules VERIFIED")
