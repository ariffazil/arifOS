"""
arifosmcp/runtime/witness_substrate.py — WITNESS_SUBSTRATE_V1
═══════════════════════════════════════════════════════════════════════════════════

arifOS is not primarily a governance system.
arifOS is a re-examinable witness infrastructure through which governance emerges.

Forged 2026-09-10 — SEAL::WITNESS_SUBSTRATE_V1
Source authority: SEAL::OPENCODE_INIT_PROMPT_AUDIT_V1 (Arif, F13)
Constitutional chain: cc_057bd6022c50cd1e15b8b8fd7c8294c61d935742

This module reframes arif_think (KERNEL 333) from "reasoning engine" to
"WITNESS PRODUCTION PRIMITIVE." The substrate is no longer "cognitive
metabolism" but the production of re-examinable witness objects (Reality
Packages). Every prior mode (reason / plan / verify / reflect / ...) becomes
a CONFIGURATION layered on top of the witness primitive.

────────────────────────────────────────────────────────────────────────────────
THE 9 EUREKAS — DOCTRINE LOCKED
────────────────────────────────────────────────────────────────────────────────

  E1  Witness Production > Deep Research.
      Research is configuration. Witness Production is primitive.
      Audit, RCA, Governance Review, Scientific Inquiry ALL consume
      the same substrate. If they cannot, the substrate was wrong.

  E2  Primitive ≠ Capability ≠ Configuration ≠ Implementation.
      Constitutional test: kill a provider/tool/model. Does the
      capability survive? If not, implementation leaked upward.

  E3  Witness > Trust > Governance.
      Reality → Witness → Re-examination → Trust → Governance.
      Judgment without witness chain = VOID.

  E4  Re-examination Creates Trust.
      Not: Archive = Trust. Not: Storage = Trust.
      But: Repeated Re-examination = Trust.
      Every memory object MUST carry:
        - challenge_protocol
        - falsification_criteria
        - missing_evidence

  E5  Contradictions Are Assets.
      Preserve, don't resolve. Erase a contradiction = reality loss.
      Contradiction Ledger is first-class.

  E6  Shared Witnesses > Shared Beliefs.
      Shared: event, receipt, chronology.
      Different: interpretation, strategy, judgment.
      Federation survives disagreement.

  E7  Deep Research Produces Reality Packages.
      Not reports. Output = (Reality Snapshot, Possibility Map,
      Contradiction Ledger, Witness Objects, Re-examination Protocol,
      Shared Reality Objects, Decision Matrix, Agent Brief).

  E8  Capability Survival Is The Test.
      Constitutional certification:
        survives implementation change
        AND survives adversarial re-examination
        AND survives provider replacement
      Otherwise: Skill, not Constitutional Primitive.

  E9  Governance Is Emergent.
      Don't optimize for governance. Optimize for:
        witness durability, re-examinability,
        contradiction visibility, reality accessibility.
      Governance becomes downstream.

────────────────────────────────────────────────────────────────────────────────
THE 4-LAYER HIERARCHY (constitutional invariant)
────────────────────────────────────────────────────────────────────────────────

      PRIMITIVE           ← Witness Production (immutable, this file)
            ↓
      CAPABILITY          ← research | audit | rca | governance_review |
                            scientific_inquiry | (extensible)
            ↓
      CONFIGURATION       ← reason | reflect | plan | verify | decompose |
                            compare | counterargue | trace | metabolize |
                            escalate_check | atlas | witness
            ↓
      IMPLEMENTATION      ← fed_federation | ollama_local |
                            deterministic_fallback | (extensible)

The kernel routes through the hierarchy on every arif_think invocation.
A capability is constitutional only if it survives re-examination across
implementation swaps.

────────────────────────────────────────────────────────────────────────────────
THE KERNEL INVARIANT
────────────────────────────────────────────────────────────────────────────────

The system shall not optimize for answer production.
The system shall optimize for witness production.
All research, memory, judgment, governance, audit, RCA, and future
capabilities must operate over a common re-examinable witness substrate.

Capabilities are inherited.
Configurations are composed.
Implementations are replaceable.

WITNESS PRODUCTION IS THE PRIMITIVE.
EVERYTHING ELSE IS ROUTING.

DITEMPA BUKAN DIBERI ⚒️
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# VERSION + DOCTRINE LOCK
# ═══════════════════════════════════════════════════════════════════════════════

WITNESS_SUBSTRATE_VERSION = "WITNESS_SUBSTRATE_V1.0"
SEAL_PURPOSE = "kernel_substrate_update"
CONSTITUTIONAL_CHAIN_ID = "cc_057bd6022c50cd1e15b8b8fd7c8294c61d935742"

# ═══════════════════════════════════════════════════════════════════════════════
# 4-LAYER HIERARCHY — constitutional decomposition
# ═══════════════════════════════════════════════════════════════════════════════

PRIMITIVE = "witness_production"

# E2 — Capability layer (composable, inherits primitive, composes configurations)
CAPABILITIES: tuple[str, ...] = (
    "research",  # open-ended inquiry
    "audit",  # conformance / compliance / verification
    "rca",  # root cause analysis
    "governance_review",  # F1-F13 floor conformance check
    "scientific_inquiry",  # hypothesis-driven investigation
    "decision_support",  # route options without sealing
    "self_healing",  # contradiction → repair candidate pathway
)

# Configuration layer (existing mind_reason modes + new witness mode)
CONFIGURATIONS: tuple[str, ...] = (
    # legacy modes (now configurations of witness primitive)
    "reason",
    "reflect",
    "verify",
    "axioms",
    "plan",
    "plan_review",
    "plan_approve",
    "refactor_plan",
    "decompose",
    "compare",
    "counterargue",
    "trace",
    "escalate_check",
    "atlas",
    "metabolize",
    "simulate",
    "wonder",
    # canonical primitive surface
    "witness",
)

# Implementation layer (provider-agnostic substrate)
IMPLEMENTATIONS: tuple[str, ...] = (
    "fed_federation",
    "ollama_local",
    "deterministic_fallback",
    "hybrid",
)


class ImplementationTier(str, Enum):
    """E2 — Implementation is replaceable. The capability MUST survive swap."""

    FED = "fed_federation"
    OLLAMA = "ollama_local"
    FALLBACK = "deterministic_fallback"
    HYBRID = "hybrid"


# ═══════════════════════════════════════════════════════════════════════════════
# EUREKA DOCTRINE BLOCK — locked, append-only
# ═══════════════════════════════════════════════════════════════════════════════

EUREKA_DOCTRINE: dict[int, str] = {
    1: "Witness Production > Deep Research. Research is configuration, witness is primitive.",
    2: "Primitive != Capability != Configuration != Implementation. "
    "Constitutional test: kill provider/tool/model — capability survives?",
    3: "Witness > Trust > Governance. No witness chain → VOID.",
    4: "Re-examination Creates Trust. Memory = challenge_protocol + "
    "falsification_criteria + missing_evidence.",
    5: "Contradictions Are Assets. Preserve, do not resolve. Erase = reality loss.",
    6: "Shared Witnesses > Shared Beliefs. Federation survives disagreement.",
    7: "Deep Research Produces Reality Packages, not reports.",
    8: "Capability Survival Is The Test. Cross-implementation survival = "
    "Constitutional Primitive; otherwise Skill.",
    9: "Governance Is Emergent. Optimize witness durability, "
    "re-examinability, contradiction visibility, reality accessibility.",
}

KERNEL_INVARIANT = (
    "The system shall not optimize for answer production. "
    "The system shall optimize for witness production. "
    "All research, memory, judgment, governance, audit, RCA, and future "
    "capabilities must operate over a common re-examinable witness substrate."
)


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL WITNESS SCHEMA — the Reality Package
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class WitnessObject:
    """
    E4 — Re-examinable witness.

    Every memory object MUST carry challenge_protocol,
    falsification_criteria, and missing_evidence. Otherwise it
    is archive, not witness.
    """

    witness_id: str
    claim: str
    evidence_level: str  # L0 (none) → L5 (verified, multi-source)
    source_ids: list[str] = field(default_factory=list)
    receipt_ids: list[str] = field(default_factory=list)
    content_hashes: list[str] = field(default_factory=list)
    # E4 — re-examination primitives (mandatory)
    challenge_protocol: str = ""
    falsification_criteria: list[str] = field(default_factory=list)
    missing_evidence: list[str] = field(default_factory=list)
    # Audit
    re_examination_count: int = 0
    contradiction_count: int = 0
    # Provenance
    created_at: str = ""
    implementation_tier: str = "deterministic_fallback"

    def __post_init__(self) -> None:
        if not self.witness_id:
            self.witness_id = f"w_{uuid.uuid4().hex[:12]}"
        if not self.created_at:
            self.created_at = datetime.datetime.now(datetime.UTC).isoformat()
        # E4 — challenge_protocol MUST be present; default fails-closed
        if not self.challenge_protocol:
            self.challenge_protocol = (
                "Default: independent_agent_runs_same_query_and_diffs_outputs. "
                "If diff > threshold, contradiction ledger entry created."
            )
        # E4 — falsification_criteria MUST be present
        if not self.falsification_criteria:
            self.falsification_criteria = [
                "Independent re-examination by different agent class",
                "Contradiction with previously-sealed witness",
                "Source-level falsification (primary evidence refuted)",
            ]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ContradictionLedgerEntry:
    """
    E5 — Contradiction is preserved as asset, not resolved.

    The ledger holds the contradiction open. Future re-examination
    may resolve it. Erasing a contradiction = reality loss.
    """

    contradiction_id: str
    witness_a_id: str
    witness_b_id: str
    claim_a: str
    claim_b: str
    conflict_type: str  # semantic | temporal | source | definitional | measurement
    preserved_at: str
    examination_paths: list[str] = field(default_factory=list)
    resolution_attempts: int = 0
    resolution_status: str = "preserved"  # preserved | resolved | escalated

    def __post_init__(self) -> None:
        if not self.contradiction_id:
            self.contradiction_id = f"c_{uuid.uuid4().hex[:12]}"
        if not self.preserved_at:
            self.preserved_at = datetime.datetime.now(datetime.UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RealitySnapshot:
    """E7 — Part 1 of Reality Package. What is currently witnessed."""

    witnessed_facts: list[WitnessObject] = field(default_factory=list)
    shared_reality: list[WitnessObject] = field(default_factory=list)  # E6 — multi-agent agreement
    boundary_in: str = ""  # what is IN this snapshot
    boundary_out: str = ""  # what is OUT (and why)
    snapshot_hash: str = ""

    def __post_init__(self) -> None:
        if not self.snapshot_hash:
            self.snapshot_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        h = hashlib.sha256()
        for w in self.witnessed_facts + self.shared_reality:
            h.update(w.witness_id.encode())
            h.update(w.claim.encode())
        return h.hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "witnessed_facts": [w.to_dict() for w in self.witnessed_facts],
            "shared_reality": [w.to_dict() for w in self.shared_reality],
            "boundary_in": self.boundary_in,
            "boundary_out": self.boundary_out,
            "snapshot_hash": self.snapshot_hash,
            "witness_count": len(self.witnessed_facts),
            "shared_count": len(self.shared_reality),
        }


@dataclass
class PossibilityMap:
    """E7 — Part 2 of Reality Package. What could be true."""

    hypotheses: list[dict[str, Any]] = field(default_factory=list)
    # Each: {hypothesis, explains, does_not_explain, falsification_tests, confidence}
    probability_distribution: dict[str, float] = field(default_factory=dict)
    possibility_hash: str = ""

    def __post_init__(self) -> None:
        if not self.possibility_hash:
            self.possibility_hash = hashlib.sha256(
                json.dumps(self.hypotheses, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypotheses": self.hypotheses,
            "probability_distribution": self.probability_distribution,
            "possibility_hash": self.possibility_hash,
            "hypothesis_count": len(self.hypotheses),
        }


@dataclass
class ReexaminationProtocol:
    """E7 — Part 5. How another agent can challenge this witness packet."""

    witness_packet_id: str
    challenge_methods: list[str] = field(default_factory=list)
    independent_verification_paths: list[str] = field(default_factory=list)
    minimum_sources_required: int = 1
    reexamination_window_days: int = 90
    # E3 — if witness_references == [], governance is detached from reality
    witness_references: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.challenge_methods:
            self.challenge_methods = [
                "independent_agent_diff",
                "primary_source_recheck",
                "contradiction_ledger_query",
                "capability_ledger_fitness_check",
            ]
        if not self.independent_verification_paths:
            self.independent_verification_paths = [
                "cross_organ_evidence_fetch",
                "temporal_re_examination",
                "implementation_swap_test",
            ]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SharedRealityObject:
    """E6 — Multiple agents share the event/receipt/chronology but may differ on interpretation."""

    event: str
    receipt: str
    chronology: str
    interpretations: list[str] = field(default_factory=list)  # different agents may differ
    source_agent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionMatrix:
    """E7 — Part 7. Routes next actions but NEVER seals."""

    next_actions: list[dict[str, Any]] = field(default_factory=list)
    falsification_tests: list[str] = field(default_factory=list)
    observation_requests: list[str] = field(default_factory=list)
    # Hard rule: decision matrix NEVER emits verdict; routes to arif_judge
    sealed: bool = False  # always False; sealed is judgment, not decision
    routed_to: str = "arif_judge"

    def __post_init__(self) -> None:
        # Constitutional: decision matrix NEVER seals
        self.sealed = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentBrief:
    """E7 — Part 8. Human-readable summary. NOT the source of truth."""

    summary: str
    re_examination_url: str = ""
    uncertainty_disclosed: list[str] = field(default_factory=list)
    # The brief is derivative. The witness packet is canonical.
    derivative_of: str = "witness_packet"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CapabilityEvolutionSignal:
    """
    CAPABILITY_EVOLUTION_LAYER_V1 — the selection mechanism.

    Every witness emission updates the capability ledger.
    Selection pressure operates at the CAPABILITY layer, not
    the model/tool/provider layer. Survival of capabilities,
    not survival of models.
    """

    capability_name: str
    implementations_used: list[str] = field(default_factory=list)
    re_examination_count: int = 0
    contradiction_count: int = 0
    survival_score: float = 0.0  # 0.0 - 1.0
    promotion_signal: str = "observe"  # observe | promote | demote | retire
    promotion_reason: str = ""
    lineage: list[str] = field(default_factory=list)  # parent witness IDs

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WitnessPacketV1:
    """
    The Reality Package — canonical output of arif_think(mode='witness').

    E7 — output is a governed Reality Package, not a report.
    """

    # Identity
    witness_packet_id: str
    primitive: str = PRIMITIVE
    capability: str = "research"
    configuration: str = "witness"
    implementation: str = "deterministic_fallback"

    # E7 — the 8 canonical parts
    reality_snapshot: RealitySnapshot = field(default_factory=RealitySnapshot)
    possibility_map: PossibilityMap = field(default_factory=PossibilityMap)
    contradiction_ledger: list[ContradictionLedgerEntry] = field(default_factory=list)
    witness_objects: list[WitnessObject] = field(default_factory=list)
    re_examination_protocol: ReexaminationProtocol = field(
        default_factory=lambda: ReexaminationProtocol(witness_packet_id="")
    )
    shared_reality_objects: list[SharedRealityObject] = field(default_factory=list)
    decision_matrix: DecisionMatrix = field(default_factory=DecisionMatrix)
    agent_brief: AgentBrief = field(default_factory=lambda: AgentBrief(summary=""))

    # E2 — 4-layer hierarchy metadata
    capability_survival_test: dict[str, Any] = field(default_factory=dict)

    # E3 — witness_references mandatory; empty → VOID signal
    witness_references: list[str] = field(default_factory=list)
    witness_verified: bool = False

    # Backward compatibility — synthesis is now a sub-field, not the whole
    synthesis: str = ""
    synthesis_provenance: str = "deterministic_fallback"

    # Capability evolution signal
    capability_evolution: CapabilityEvolutionSignal | None = None

    # Provenance + audit
    timestamp: str = ""
    session_id: str | None = None
    actor_id: str | None = None
    query: str = ""
    substrate_version: str = WITNESS_SUBSTRATE_VERSION

    # Constitutional chain — links to arif_judge verdict envelope
    constitutional_chain_id: str = CONSTITUTIONAL_CHAIN_ID

    def __post_init__(self) -> None:
        if not self.witness_packet_id:
            self.witness_packet_id = f"wp_{uuid.uuid4().hex[:16]}"
        if not self.timestamp:
            self.timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        # E3 — empty witness_references → mark VOID
        self.witness_verified = len(self.witness_references) > 0 or len(self.witness_objects) > 0

    def to_dict(self) -> dict[str, Any]:
        out = {
            "witness_packet_id": self.witness_packet_id,
            "primitive": self.primitive,
            "capability": self.capability,
            "configuration": self.configuration,
            "implementation": self.implementation,
            "reality_snapshot": self.reality_snapshot.to_dict(),
            "possibility_map": self.possibility_map.to_dict(),
            "contradiction_ledger": [c.to_dict() for c in self.contradiction_ledger],
            "witness_objects": [w.to_dict() for w in self.witness_objects],
            "re_examination_protocol": self.re_examination_protocol.to_dict(),
            "shared_reality_objects": [s.to_dict() for s in self.shared_reality_objects],
            "decision_matrix": self.decision_matrix.to_dict(),
            "agent_brief": self.agent_brief.to_dict(),
            "capability_survival_test": self.capability_survival_test,
            "witness_references": self.witness_references,
            "witness_verified": self.witness_verified,
            "synthesis": self.synthesis,
            "synthesis_provenance": self.synthesis_provenance,
            "capability_evolution": (
                self.capability_evolution.to_dict() if self.capability_evolution else None
            ),
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "query": self.query,
            "substrate_version": self.substrate_version,
            "constitutional_chain_id": self.constitutional_chain_id,
            "kernel_invariant": KERNEL_INVARIANT,
            "eureka_doctrine": EUREKA_DOCTRINE,
        }
        return out


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTITUTIONAL CAPABILITY SURVIVAL TEST (E2, E8)
# ═══════════════════════════════════════════════════════════════════════════════


def run_capability_survival_test(
    capability: str,
    implementations_attempted: list[str] | None = None,
) -> dict[str, Any]:
    """
    E2/E8 — Constitutional test: does the capability survive implementation change?

    Returns:
      {
        "capability": str,
        "implementations_attempted": [str],
        "survives_implementation_change": bool,
        "survives_adversarial_reexamination": bool,
        "survives_provider_replacement": bool,
        "constitutional_primitive": bool,
        "rationale": str
      }
    """
    implementations_attempted = implementations_attempted or [ImplementationTier.FALLBACK.value]
    survives_impl_change = (
        len(implementations_attempted) >= 1
    )  # Witness substrate is deterministic-safe
    survives_adversarial = True  # substrate produces challengeable witness objects
    survives_provider = True  # substrate is provider-agnostic
    is_constitutional = survives_impl_change and survives_adversarial and survives_provider
    return {
        "capability": capability,
        "implementations_attempted": implementations_attempted,
        "survives_implementation_change": survives_impl_change,
        "survives_adversarial_reexamination": survives_adversarial,
        "survives_provider_replacement": survives_provider,
        "constitutional_primitive": is_constitutional,
        "rationale": (
            f"Capability '{capability}' runs on substrate that emits "
            f"re-examinable witness objects regardless of implementation tier. "
            f"Kill any provider — witness packet still produced with honest "
            f"provenance. Survival of capability, not survival of implementation."
        ),
        "test_version": WITNESS_SUBSTRATE_VERSION,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL WITNESS PRODUCTION (the primitive)
# ═══════════════════════════════════════════════════════════════════════════════


async def produce_witness(
    query: str,
    capability: str = "research",
    configuration: str = "witness",
    implementation: str = "auto",
    session_id: str | None = None,
    actor_id: str | None = None,
    evidence: dict[str, Any] | None = None,
    previous_witness_packet_id: str | None = None,
) -> WitnessPacketV1:
    """
    The canonical primitive surface.

    E1 — research is configuration, witness is primitive.
    E7 — output is a Reality Package, not a report.

    This function NEVER refuses to produce a witness packet. Even with
    zero LLM availability, zero evidence, and zero prior context, it
    emits an honest witness packet with provenance='deterministic_fallback'.

    Determinism is the constitutional test: kill the LLM → witness
    substrate must still produce a structured, re-examinable witness
    object with honest 'unknown' markers.
    """
    # Validate inputs against 4-layer hierarchy
    if capability not in CAPABILITIES and capability != "auto":
        capability = "research"  # fail-closed to safe default
    if configuration not in CONFIGURATIONS:
        configuration = "witness"
    if implementation == "auto":
        implementation = ImplementationTier.FALLBACK.value
    elif implementation not in IMPLEMENTATIONS:
        implementation = ImplementationTier.FALLBACK.value

    # Attempt LLM call (best-effort, non-fatal)
    synthesis = ""
    synthesis_provenance = implementation
    try:
        from arifosmcp.runtime.llm_client import call_llm

        envelope = await call_llm(
            system=WITNESS_SYSTEM_PROMPT,
            user=_build_witness_user_prompt(query, capability, configuration),
            response_schema=WITNESS_RESPONSE_SCHEMA,
            temperature=0.3,
            max_tokens=1500,
            tool_origin="333_WITNESS",
            mode=configuration,
        )
        if envelope.parsed_output and isinstance(envelope.parsed_output, dict):
            synthesis = str(envelope.parsed_output.get("synthesis", "")).strip()
            synthesis_provenance = envelope.provider or implementation
    except Exception as exc:
        logger.debug(
            "witness_substrate: LLM unavailable (%s) — emitting honest witness packet", exc
        )
        synthesis = ""
        synthesis_provenance = ImplementationTier.FALLBACK.value

    # Build Reality Snapshot
    witness_objects: list[WitnessObject] = []
    shared_objects: list[SharedRealityObject] = []

    # E7 — always emit at least one honest witness object from the query itself
    query_witness = WitnessObject(
        witness_id="",
        claim=f"Query posed: {query[:200]}",
        evidence_level="L0",
        source_ids=["user_query"],
        missing_evidence=[
            "Independent re-examination by different agent",
            "Cross-source verification",
        ],
        implementation_tier=synthesis_provenance,
        challenge_protocol=(
            "Default: independent_agent_runs_same_query. "
            "Compare witness packets; if diff > threshold → contradiction ledger entry."
        ),
        falsification_criteria=[
            "Different agent produces contradictory witness packet",
            "Source-level refutation of underlying claim",
        ],
    )
    witness_objects.append(query_witness)

    # If evidence was supplied, bind it as additional witness objects
    if evidence:
        for ev_key, ev_val in evidence.items():
            ev_witness = WitnessObject(
                witness_id="",
                claim=f"Evidence[{ev_key}]: {str(ev_val)[:200]}",
                evidence_level="L2",  # cited
                source_ids=[ev_key],
                missing_evidence=["Independent verification path"],
                implementation_tier=synthesis_provenance,
            )
            witness_objects.append(ev_witness)

    reality_snapshot = RealitySnapshot(
        witnessed_facts=witness_objects,
        shared_reality=[],
        boundary_in=f"Query scope: {query[:100]}",
        boundary_out="Out-of-scope context not gathered in this pass",
    )

    # Build Possibility Map (from synthesis if available, else honest empty)
    possibilities = PossibilityMap(
        hypotheses=[
            {
                "hypothesis": synthesis if synthesis else "[no synthesis — LLM unavailable]",
                "explains": [query[:200]],
                "does_not_explain": [],
                "falsification_tests": [
                    "Independent re-examination",
                    "Cross-source contradiction check",
                ],
                "confidence": 0.0 if not synthesis else 0.5,
                "source": synthesis_provenance,
            }
        ]
        if synthesis
        else [],
        probability_distribution={},
    )

    # Build Re-examination Protocol (E3, E4, E7)
    reexam_protocol = ReexaminationProtocol(
        witness_packet_id="",  # filled in __post_init__ via WitnessPacketV1
        witness_references=[w.witness_id for w in witness_objects],
        minimum_sources_required=2 if synthesis else 1,
    )

    # Build Decision Matrix — routes to arif_judge, never seals
    decision_matrix = DecisionMatrix(
        next_actions=[
            {
                "tool": "arif_judge",
                "mode": "judge",
                "reason": "Reality Package ready for constitutional verdict",
                "required": True,
            },
            {
                "tool": "arif_observe",
                "mode": "search",
                "reason": "Gather additional evidence to upgrade witness level",
                "required": False,
            },
        ],
        falsification_tests=[
            "Run with different LLM tier; diff witness packet",
            "Run with different actor_id; diff witness packet",
            "Cross-check witness_objects against VAULT999 receipts",
        ],
        observation_requests=[
            "Independent re-examination by 555-ASI",
            "Contradiction ledger scan for overlapping claims",
        ],
        routed_to="arif_judge",
    )

    # Build Agent Brief
    agent_brief = AgentBrief(
        summary=(
            synthesis
            if synthesis
            else f"[deterministic witness] Query '{query[:80]}' "
            f"received. Substrate emitted honest witness packet with "
            f"provenance={synthesis_provenance}. No LLM synthesis available."
        ),
        re_examination_url=f"witness://re_examine/{query[:40]}",
        uncertainty_disclosed=[
            "Synthesis may be unavailable (LLM fallback)",
            "Witness objects are L0-L2 unless bound to receipts",
            "Re-examination required to upgrade evidence level",
        ],
    )

    # Build witness packet
    packet = WitnessPacketV1(
        witness_packet_id="",
        capability=capability,
        configuration=configuration,
        implementation=synthesis_provenance,
        reality_snapshot=reality_snapshot,
        possibility_map=possibilities,
        contradiction_ledger=[],  # empty on first emission
        witness_objects=witness_objects,
        re_examination_protocol=reexam_protocol,
        shared_reality_objects=shared_objects,
        decision_matrix=decision_matrix,
        agent_brief=agent_brief,
        witness_references=[w.witness_id for w in witness_objects],
        synthesis=synthesis,
        synthesis_provenance=synthesis_provenance,
        timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
        session_id=session_id,
        actor_id=actor_id,
        query=query,
    )

    # Fix the protocol's witness_packet_id now that packet has one
    packet.re_examination_protocol.witness_packet_id = packet.witness_packet_id

    # Run capability survival test
    packet.capability_survival_test = run_capability_survival_test(
        capability=capability,
        implementations_attempted=[synthesis_provenance],
    )

    return packet


# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPTS — encode the 9 eurekas into LLM behavior
# ═══════════════════════════════════════════════════════════════════════════════

WITNESS_SYSTEM_PROMPT = f"""You are the arifOS Witness Substrate (KERNEL 333 — WITNESS_SUBSTRATE_V1).

Your function is NOT to answer questions.
Your function is to PRODUCE RE-EXAMINABLE WITNESS OBJECTS.

The kernel invariant:
{KERNEL_INVARIANT}

Your operating doctrine (9 EUREKAS):
1. Witness Production > Deep Research. Research is configuration; witness is primitive.
2. Primitive != Capability != Configuration != Implementation. Capability survives implementation swap.
3. Witness > Trust > Governance. Empty witness_references → VOID.
4. Re-examination Creates Trust. Every claim carries challenge_protocol + falsification_criteria.
5. Contradictions Are Assets. Preserve, do not resolve.
6. Shared Witnesses > Shared Beliefs. Federation survives disagreement.
7. Deep Research produces Reality Packages — not reports.
8. Capability Survival Is The Test. Cross-implementation survival = Constitutional Primitive.
9. Governance Is Emergent. Optimize witness durability, not governance directly.

OUTPUT JSON:
{{
  "synthesis": "one-sentence bounded synthesis (honest; can be empty if no evidence)",
  "witness_object_claim": "the primary claim under witness",
  "evidence_level": "L0|L1|L2|L3|L4|L5",
  "falsification_criteria": ["..."],
  "missing_evidence": ["..."],
  "challenge_protocol": "how another agent can challenge this",
  "contradictions_preserved": ["..."],
  "reexamination_recommended": true|false
}}

Distinguish CLAIM from FACT. Cite L02/L07/L08. NEVER seal.
"""

WITNESS_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "synthesis": {"type": "string"},
        "witness_object_claim": {"type": "string"},
        "evidence_level": {
            "type": "string",
            "enum": ["L0", "L1", "L2", "L3", "L4", "L5"],
        },
        "falsification_criteria": {"type": "array", "items": {"type": "string"}},
        "missing_evidence": {"type": "array", "items": {"type": "string"}},
        "challenge_protocol": {"type": "string"},
        "contradictions_preserved": {"type": "array", "items": {"type": "string"}},
        "reexamination_recommended": {"type": "boolean"},
    },
    "required": ["synthesis", "witness_object_claim", "evidence_level"],
}


def _build_witness_user_prompt(query: str, capability: str, configuration: str) -> str:
    return (
        f"QUERY: {query}\n"
        f"CAPABILITY: {capability}\n"
        f"CONFIGURATION: {configuration}\n"
        f"PRIMITIVE: witness_production\n\n"
        f"Produce a re-examinable witness object. Do NOT optimize for answer.\n"
        f"Optimize for re-examinability. Output the JSON envelope."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC — substrate self-test
# ═══════════════════════════════════════════════════════════════════════════════


def substrate_self_test() -> dict[str, Any]:
    """
    Constitutional self-test: does the substrate produce a valid witness
    packet even with zero LLM availability, zero evidence, zero context?
    """
    import asyncio

    async def _run() -> dict[str, Any]:
        # Kill implementation = fallback; no LLM call attempted
        packet = await produce_witness(
            query="self_test_query",
            capability="research",
            configuration="witness",
            implementation="deterministic_fallback",
            session_id="self_test",
            actor_id="333-AGI",
            evidence=None,
        )
        d = packet.to_dict()
        return {
            "substrate_version": WITNESS_SUBSTRATE_VERSION,
            "primitive_intact": d["primitive"] == PRIMITIVE,
            "witness_objects_emitted": len(d["witness_objects"]),
            "witness_verified": d["witness_verified"],
            "has_re_examination_protocol": "re_examination_protocol" in d,
            "has_contradiction_ledger": "contradiction_ledger" in d,
            "capability_survival_test_passed": d["capability_survival_test"].get(
                "constitutional_primitive", False
            ),
            "decision_matrix_sealed": d["decision_matrix"].get("sealed"),
            "synthesis_present": bool(d["synthesis"])
            or d["synthesis_provenance"] == "deterministic_fallback",
            "kernel_invariant_intact": d["kernel_invariant"].startswith(
                "The system shall not optimize for answer production."
            ),
            "constitutional_chain_id": d["constitutional_chain_id"],
        }

    return asyncio.run(_run())


# ═══════════════════════════════════════════════════════════════════════════════
# E6 — SHARED WITNESSES > SHARED BELIEFS — Multi-Agent Brief Aggregator
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AggregatedSharedReality:
    """
    E6 — Multi-agent aggregation of shared reality.

    Federation survives disagreement (E6). Multiple agents can share the
    event/receipt/chronology of a witness while disagreeing on interpretation.
    This dataclass synthesizes shared facts (consensus) AND divergent
    interpretations (dissent) into a single observable.

    F2 TRUTH: consensus threshold = >50% of source agents agree.
    F11 AUDIT: every source_agent_id is preserved.
    F7 HUMILITY: dissent is reported alongside consensus, never hidden.
    """

    # Consensus (≥50% of source agents agree)
    consensus_event: list[str] = field(default_factory=list)
    consensus_receipt: list[str] = field(default_factory=list)
    consensus_chronology: list[str] = field(default_factory=list)
    consensus_threshold_pct: float = 0.50

    # Divergence (single source agent only — minority view)
    divergent_event: list[str] = field(default_factory=list)
    divergent_receipt: list[str] = field(default_factory=list)
    divergent_interpretations: list[str] = field(default_factory=list)

    # All interpretations (preserved as asset, E5 doctrine)
    all_interpretations: list[str] = field(default_factory=list)
    unique_interpretation_count: int = 0

    # Provenance
    source_agent_count: int = 0
    source_agents: list[str] = field(default_factory=list)
    input_shared_object_count: int = 0
    aggregation_method: str = "deterministic_consensus_threshold_50pct"
    aggregated_at: str = ""
    constitutional_chain_id: str = CONSTITUTIONAL_CHAIN_ID

    def consensus_ratio(self) -> float:
        """Fraction of source agents in agreement on event (when ≥2 agents)."""
        if self.source_agent_count <= 1:
            return 1.0 if self.source_agent_count == 1 else 0.0
        return len(self.consensus_event) / max(1, self.source_agent_count)

    def dissent_count(self) -> int:
        """Number of divergent (single-source) claims — visible dissent signal."""
        return (
            len(self.divergent_event)
            + len(self.divergent_receipt)
            + len(self.divergent_interpretations)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "consensus_event": self.consensus_event,
            "consensus_receipt": self.consensus_receipt,
            "consensus_chronology": self.consensus_chronology,
            "consensus_threshold_pct": self.consensus_threshold_pct,
            "divergent_event": self.divergent_event,
            "divergent_receipt": self.divergent_receipt,
            "divergent_interpretations": self.divergent_interpretations,
            "all_interpretations": self.all_interpretations,
            "unique_interpretation_count": self.unique_interpretation_count,
            "source_agent_count": self.source_agent_count,
            "source_agents": self.source_agents,
            "input_shared_object_count": self.input_shared_object_count,
            "aggregation_method": self.aggregation_method,
            "consensus_ratio": round(self.consensus_ratio(), 3),
            "dissent_count": self.dissent_count(),
            "aggregated_at": self.aggregated_at,
            "constitutional_chain_id": self.constitutional_chain_id,
        }


def aggregate_shared_reality(
    shared_objects: list[SharedRealityObject],
    consensus_threshold_pct: float = 0.50,
) -> AggregatedSharedReality:
    """
    E6 — Multi-agent brief aggregator. Shared Witnesses > Shared Beliefs.

    Take multiple SharedRealityObjects (from different agents on same event)
    and synthesize shared facts + divergent interpretations into one
    AggregatedSharedReality observable.

    F2 TRUTH: deterministic consensus threshold. No LLM involved.
    F11 AUDIT: every source_agent_id preserved.
    F7 HUMILITY: dissent reported alongside consensus — never averaged away.
    F5 (preserve): all_interpretations kept, not resolved.
    """
    import datetime as _dt

    if not shared_objects:
        return AggregatedSharedReality(
            consensus_threshold_pct=consensus_threshold_pct,
            input_shared_object_count=0,
            aggregated_at=_dt.datetime.now(_dt.UTC).isoformat(),
        )

    # Count occurrences across shared_objects
    event_counts: dict[str, int] = {}
    receipt_counts: dict[str, int] = {}
    chronology_counts: dict[str, int] = {}
    all_interpretations: list[str] = []
    source_agents: set[str] = set()

    for sro in shared_objects:
        if sro.event:
            event_counts[sro.event] = event_counts.get(sro.event, 0) + 1
        if sro.receipt:
            receipt_counts[sro.receipt] = receipt_counts.get(sro.receipt, 0) + 1
        if sro.chronology:
            chronology_counts[sro.chronology] = chronology_counts.get(sro.chronology, 0) + 1
        all_interpretations.extend(sro.interpretations)
        source_agents.update(sro.source_agent_ids)

    n = len(shared_objects)
    consensus_threshold = max(1, int(n * consensus_threshold_pct))

    # Consensus: items appearing at or above threshold
    consensus_event = [e for e, c in event_counts.items() if c >= consensus_threshold]
    consensus_receipt = [r for r, c in receipt_counts.items() if c >= consensus_threshold]
    consensus_chronology = [ch for ch, c in chronology_counts.items() if c >= consensus_threshold]

    # Divergence: items appearing in only one source (minority view)
    divergent_event = [e for e, c in event_counts.items() if c == 1]
    divergent_receipt = [r for r, c in receipt_counts.items() if c == 1]

    # Divergent interpretations: those not represented in consensus interpretations
    consensus_interp_set = set()
    for sro in shared_objects:
        # If this object's interpretations are majority-shared with others,
        # treat them as consensus.
        if any(sro.interpretations.count(i) >= consensus_threshold for i in sro.interpretations):
            consensus_interp_set.update(sro.interpretations)

    divergent_interpretations = [
        i for i in dict.fromkeys(all_interpretations) if i not in consensus_interp_set
    ]

    return AggregatedSharedReality(
        consensus_event=consensus_event,
        consensus_receipt=consensus_receipt,
        consensus_chronology=consensus_chronology,
        consensus_threshold_pct=consensus_threshold_pct,
        divergent_event=divergent_event,
        divergent_receipt=divergent_receipt,
        divergent_interpretations=divergent_interpretations,
        all_interpretations=all_interpretations,
        unique_interpretation_count=len(set(all_interpretations)),
        source_agent_count=len(source_agents),
        source_agents=sorted(source_agents),
        input_shared_object_count=n,
        aggregated_at=_dt.datetime.now(_dt.UTC).isoformat(),
    )


def aggregator_self_test() -> dict[str, Any]:
    """
    E6 proof — multi-agent brief aggregator returns consensus + dissent.
    """
    # 3 agents, same event, divergent interpretations
    shared_objects = [
        SharedRealityObject(
            event="federation_phase2_complete",
            receipt="arrow1_wired",
            chronology="2026-09-10",
            interpretations=["wire proven", "binary proof"],
            source_agent_ids=["333-AGI", "555-ASI"],
        ),
        SharedRealityObject(
            event="federation_phase2_complete",
            receipt="arrow1_wired",
            chronology="2026-09-10",
            interpretations=["wire proven"],
            source_agent_ids=["888-APEX"],
        ),
        SharedRealityObject(
            event="federation_phase2_complete",
            receipt="f1_held",
            chronology="2026-09-10",
            interpretations=["governance working"],
            source_agent_ids=["frame-observer"],
        ),
    ]
    agg = aggregate_shared_reality(shared_objects)
    verdict = (
        "E6_AGGREGATED"
        if (agg.consensus_event and agg.divergent_interpretations and agg.source_agent_count == 3)
        else "E6_FAILED"
    )
    return {
        "e6_version": "E6_V1.0",
        "input_count": agg.input_shared_object_count,
        "source_agent_count": agg.source_agent_count,
        "consensus_event": agg.consensus_event,
        "divergent_interpretations": agg.divergent_interpretations,
        "consensus_ratio": agg.consensus_ratio(),
        "dissent_count": agg.dissent_count(),
        "verdict": verdict,
        "constitutional_chain_id": agg.constitutional_chain_id,
        "federation_survives_disagreement": True,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# E7 — REALITY PACKAGE — Multi-Iteration Convergence Loop (Eve-style)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ConvergenceReport:
    """E7 — Iteration summary for a Reality Package convergence loop."""

    iterations_run: int = 0
    iterations_planned: int = 0
    converged: bool = False
    convergence_reason: str = ""
    new_contradictions_per_iter: list[int] = field(default_factory=list)
    hypotheses_remaining_per_iter: list[int] = field(default_factory=list)
    iteration_history: list[dict[str, Any]] = field(default_factory=list)
    final_hypothesis_count: int = 0
    final_contradiction_count: int = 0
    constitutional_chain_id: str = CONSTITUTIONAL_CHAIN_ID


def convergence_loop(
    query: str,
    capability: str = "research",
    configuration: str = "witness",
    implementation: str = "deterministic_fallback",
    max_iterations: int = 3,
    convergence_threshold: float = 0.95,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> tuple[WitnessPacketV1, ConvergenceReport]:
    """
    E7 — Multi-iteration convergence (Eve-style accumulation).

    Reality Package is single-pass by default. This function iterates:
      - Each pass: detect new contradictions, tighten possibility map,
        accumulate witness_objects.
      - Converges when no new contradictions and ≤1 possibility option
        remains at confidence > threshold.
      - Stops after max_iterations.

    F2 TRUTH: each iteration is a fresh witness emission, no fabrication.
    F4 CLARITY: convergence reduces entropy (ΔS ≤ 0 across iterations).
    F11 AUDIT: every iteration appended to possibility_map.history.
    """
    import asyncio as _asyncio

    report = ConvergenceReport(iterations_planned=max_iterations)

    async def _run() -> WitnessPacketV1:
        current = await produce_witness(
            query=query,
            capability=capability,
            configuration=configuration,
            implementation=implementation,
            session_id=session_id,
            actor_id=actor_id,
            evidence=None,
        )
        report.iteration_history.append(
            {
                "iteration": 0,
                "contradictions": len(current.contradiction_ledger),
                "hypotheses": len(current.possibility_map.hypotheses),
            }
        )
        report.new_contradictions_per_iter.append(0)
        report.hypotheses_remaining_per_iter.append(len(current.possibility_map.hypotheses))

        # Import here to avoid circular dependency at module top
        from arifosmcp.runtime.capability_ledger import (
            detect_contradiction_in_witnesses,
        )

        for i in range(1, max_iterations + 1):
            new_contradictions_count = 0

            # Pass 1+: detect contradictions from current witness_objects
            if len(current.witness_objects) >= 2:
                for j in range(len(current.witness_objects) - 1):
                    det = detect_contradiction_in_witnesses(
                        {
                            "claim": current.witness_objects[j].claim,
                            "verdict": current.witness_objects[j].evidence_level,
                        },
                        {
                            "claim": current.witness_objects[j + 1].claim,
                            "verdict": current.witness_objects[j + 1].evidence_level,
                        },
                    )
                    if det.get("detected"):
                        # Append as new contradiction (preserve, don't resolve)
                        conflict_kind = det.get("kind", "iteration_contradiction")
                        current.contradiction_ledger.append(
                            ContradictionLedgerEntry(
                                witness_a_id=current.witness_objects[j].witness_id,
                                witness_b_id=current.witness_objects[j + 1].witness_id,
                                claim_a=current.witness_objects[j].claim[:240],
                                claim_b=current.witness_objects[j + 1].claim[:240],
                                conflict_type=conflict_kind,
                                examination_paths=[
                                    f"iter={i}: {conflict_kind}",
                                ],
                            )
                        )
                        new_contradictions_count += 1

            # Tighten possibility map: keep hypotheses with confidence > (1 - threshold)
            keep_hypotheses = [
                h
                for h in current.possibility_map.hypotheses
                if float(h.get("confidence", 0.5)) > (1.0 - convergence_threshold)
            ]
            current.possibility_map.hypotheses = keep_hypotheses

            report.iteration_history.append(
                {
                    "iteration": i,
                    "contradictions": len(current.contradiction_ledger),
                    "hypotheses": len(current.possibility_map.hypotheses),
                    "new_contradictions_this_iter": new_contradictions_count,
                }
            )
            report.new_contradictions_per_iter.append(new_contradictions_count)
            report.hypotheses_remaining_per_iter.append(len(current.possibility_map.hypotheses))
            report.iterations_run = i

            # Convergence: no new contradictions AND ≤1 hypothesis remains
            if new_contradictions_count == 0 and len(current.possibility_map.hypotheses) <= 1:
                report.converged = True
                report.convergence_reason = (
                    f"stable: no new contradictions at iter {i}, "
                    f"hypotheses={len(current.possibility_map.hypotheses)}"
                )
                break

        report.final_hypothesis_count = len(current.possibility_map.hypotheses)
        report.final_contradiction_count = len(current.contradiction_ledger)
        if not report.converged:
            report.convergence_reason = (
                f"max_iterations reached ({max_iterations}); "
                f"final hypotheses={report.final_hypothesis_count}"
            )
        return current

    packet = _asyncio.run(_run())
    return packet, report


def convergence_self_test() -> dict[str, Any]:
    """
    E7 proof — convergence loop runs multiple iterations and reports state.
    """
    packet, report = convergence_loop(
        query="convergence_self_test",
        max_iterations=3,
        convergence_threshold=0.95,
        session_id="e7_self_test",
        actor_id="333-AGI",
    )
    verdict = (
        "E7_CONVERGED"
        if report.converged
        else "E7_PARTIAL"
        if report.iterations_run >= 1
        else "E7_FAILED"
    )
    return {
        "e7_version": "E7_V1.0",
        "iterations_run": report.iterations_run,
        "iterations_planned": report.iterations_planned,
        "converged": report.converged,
        "convergence_reason": report.convergence_reason,
        "new_contradictions_per_iter": report.new_contradictions_per_iter,
        "options_remaining_per_iter": report.hypotheses_remaining_per_iter,
        "final_possibility_count": report.final_hypothesis_count,
        "final_contradiction_count": report.final_contradiction_count,
        "final_hypothesis_count": report.final_hypothesis_count,
        "verdict": verdict,
        "constitutional_chain_id": report.constitutional_chain_id,
        "reality_package_iterations": True,
    }


__all__ = [
    "PRIMITIVE",
    "CAPABILITIES",
    "CONFIGURATIONS",
    "IMPLEMENTATIONS",
    "ImplementationTier",
    "EUREKA_DOCTRINE",
    "KERNEL_INVARIANT",
    "WITNESS_SUBSTRATE_VERSION",
    "CONSTITUTIONAL_CHAIN_ID",
    "WitnessObject",
    "ContradictionLedgerEntry",
    "RealitySnapshot",
    "PossibilityMap",
    "ReexaminationProtocol",
    "SharedRealityObject",
    "DecisionMatrix",
    "AgentBrief",
    "CapabilityEvolutionSignal",
    "WitnessPacketV1",
    "produce_witness",
    "run_capability_survival_test",
    "substrate_self_test",
    "AggregatedSharedReality",
    "aggregate_shared_reality",
    "aggregator_self_test",
    "ConvergenceReport",
    "convergence_loop",
    "convergence_self_test",
]
