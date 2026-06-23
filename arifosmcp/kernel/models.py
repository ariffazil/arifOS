"""
arifosmcp/kernel/models.py — Kernel Type System v0.3

The kernel's type system. Every MCP call produces an AdmissibilityVerdict.
No tool dispatch happens without one.

Doctrine:
  arifOS is not a truth oracle.
  It is an admissibility kernel that forces every intelligence flow
  to earn the right to become trusted state or physical effect.

  The kernel does not collapse reality.
  It collapses admissibility ambiguity.

  Reality is not what the model outputs.
  Reality is what survives evidence, replay, authority, and constraint.

v0.3 additions:
- Three Beasts: Gödel-lock, Strange Loop, Anti-sink
- EvidenceSource, TruthClass, WitnessType, SinkRisk, Witness models
- requires_external_witness, requires_external_anchor on CapabilityNode
- max_simulations_before_action, requires_action_or_refusal_log
- truth_class, witness, evidence_sources, sink_risk on InterceptorDecision

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════════════════════


class AdmissibilityVerdict(str, Enum):
    """The eight kernel verdicts. Every MCP call maps to exactly one."""

    ADMIT_READ = "ADMIT_READ"
    ADMIT_SIMULATE = "ADMIT_SIMULATE"
    ADMIT_MUTATE = "ADMIT_MUTATE"
    DENY = "DENY"
    HOLD_888 = "888_HOLD"
    QUARANTINE = "QUARANTINE"
    REPLAY_REQUIRED = "REPLAY_REQUIRED"
    INVALID_REPORT = "INVALID_REPORT"


class MutationClass(str, Enum):
    """How the tool touches reality."""

    NONE = "NONE"  # read/idempotent
    LOCAL_STATE = "LOCAL_STATE"  # mutates local process state
    ORG_STATE = "ORG_STATE"  # mutates organ data
    EXTERNAL = "EXTERNAL"  # network/API side effect
    IRREVERSIBLE = "IRREVERSIBLE"  # cannot roll back


class BlastRadius(str, Enum):
    """Scope of potential damage."""

    LOCAL = "LOCAL"  # single request
    PROCESS = "PROCESS"  # this process only
    ORGAN = "ORGAN"  # one organ
    FEDERATION = "FEDERATION"  # multiple organs
    EXTERNAL = "EXTERNAL"  # outside the VPS


class AuthorityTier(str, Enum):
    """What authority level an actor holds."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SOVEREIGN = "SOVEREIGN"


class TrustState(str, Enum):
    """Where a server/tool is in its trust lifecycle."""

    UNKNOWN = "UNKNOWN"
    DISCOVERED = "DISCOVERED"
    SANDBOXED = "SANDBOXED"
    PROBATION = "PROBATION"
    TRUSTED_READ = "TRUSTED_READ"
    TRUSTED_MUTATE = "TRUSTED_MUTATE"
    QUARANTINED = "QUARANTINED"
    REVOKED = "REVOKED"


class ResourceClass(str, Enum):
    """What kind of resource this capability touches."""

    FILE = "FILE"
    DB_TABLE = "DB_TABLE"
    SECRET = "SECRET"
    GIT_REPO = "GIT_REPO"
    K8S_CLUSTER = "K8S_CLUSTER"
    VAULT_ENTRY = "VAULT_ENTRY"
    HTTP_ENDPOINT = "HTTP_ENDPOINT"
    MCP_SERVER = "MCP_SERVER"
    PROCESS = "PROCESS"
    MEMORY = "MEMORY"
    NETWORK = "NETWORK"
    UNKNOWN = "UNKNOWN"


class PromptInjectionSurface(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class DataExfiltrationRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ═══════════════════════════════════════════════════════════════════════════════
# Three Beasts — Gödel-lock, Strange Loop, Anti-sink
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceSource(str, Enum):
    """Where does the evidence for this action come from?

    The kernel does not manufacture truth. It constrains intelligence so that
    claims, authority, and actions remain accountable to evidence.

    Mission 002 — Strange Loop: mutations require at least one EXTERNAL_* source.
    Prevents closed internal reality loops where the system believes its own stories.
    """

    INTERNAL_MODEL = "INTERNAL_MODEL"
    INTERNAL_TOOL = "INTERNAL_TOOL"
    EXTERNAL_DB = "EXTERNAL_DB"
    EXTERNAL_API = "EXTERNAL_API"
    EXTERNAL_SENSOR = "EXTERNAL_SENSOR"
    EXTERNAL_HUMAN = "EXTERNAL_HUMAN"
    EXTERNAL_LAW = "EXTERNAL_LAW"
    EXTERNAL_VAULT = "EXTERNAL_VAULT"
    UNKNOWN = "UNKNOWN"


class TruthClass(str, Enum):
    """What epistemic status does this output carry?

    arifOS does not create truth. arifOS prevents unearned claims and
    unauthorized actions from masquerading as truth.

    Mission 002 — Strange Loop: verdicts built only from internal premises
    cannot be classified as OBSERVATION or POLICY_VERDICT.
    """

    OBSERVATION = "OBSERVATION"
    MEASUREMENT = "MEASUREMENT"
    DERIVED = "DERIVED"
    CLAIM = "CLAIM"
    SIMULATION = "SIMULATION"
    POLICY_VERDICT = "POLICY_VERDICT"
    MUTATION_RECEIPT = "MUTATION_RECEIPT"
    INVALID = "INVALID"


class WitnessType(str, Enum):
    """What kind of witness attested to an action.

    Mission 001 — Gödel-lock: irreversible mutations require at least one witness.
    """

    HUMAN = "HUMAN"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"
    SIGNED_SENSOR = "SIGNED_SENSOR"
    LAW_DOC = "LAW_DOC"
    VAULT_ANCHOR = "VAULT_ANCHOR"
    NONE = "NONE"


class SinkRisk(str, Enum):
    """Is this organ/capability at risk of behavioral sink?

    Mission 003 — Anti-sink: simulation without action degrades to SINK_RISK.
    """

    NONE = "NONE"
    REHEARSING = "REHEARSING"
    SINK_RISK = "SINK_RISK"
    STERILE = "STERILE"


class Witness(BaseModel):
    """An external witness to an action.

    Constraints do not create truth. Constraints prevent falsehood
    from gaining authority.

    Mission 001 — Gödel-lock: prevents self-certification.
    The actor of a mutation cannot be the final certifier.
    """

    witness_type: WitnessType = Field(default=WitnessType.NONE)
    witness_id: str = Field(default="", description="Identifier of the witness")
    nonce: str | None = Field(default=None, description="Cryptographic nonce if signed")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    statement: str = Field(default="", description="What the witness attested to")


# ═══════════════════════════════════════════════════════════════════════════════
# Capability Node — the constitutional atomic unit
# ═══════════════════════════════════════════════════════════════════════════════


class CapabilityNode(BaseModel):
    """A compiled capability — one tool on one server, fully classified.

    This is the kernel's ontology of power. Every MCP tool maps to exactly
    one CapabilityNode (or is denied as unknown).
    """

    capability_id: str = Field(description="Stable, semantic ID, e.g. 'fs.read'")
    tool_name: str = Field(description="Raw MCP tool name")
    server_id: str = Field(description="MCP server origin")
    description: str = Field(default="")

    # ── Authority ────────────────────────────────────────────────────────
    authority_required: AuthorityTier = Field(default=AuthorityTier.LOW)
    requires_888_hold: bool = Field(
        default=False,
        description="If True, this capability always requires 888_HOLD regardless of authority.",
    )

    # ── Mutation ─────────────────────────────────────────────────────────
    mutation_class: MutationClass = Field(default=MutationClass.NONE)
    irreversible: bool = Field(default=False)
    simulation_available: bool = Field(default=False)
    rollback_available: bool = Field(default=False)
    audit_required: bool = Field(default=False)

    # ── Blast and resource ────────────────────────────────────────────────
    blast_radius: BlastRadius = Field(default=BlastRadius.LOCAL)
    resource_class: ResourceClass = Field(default=ResourceClass.UNKNOWN)
    organ_id: str | None = Field(
        default=None,
        description="Which organ owns this capability (GEOX, WEALTH, WELL, A-FORGE, etc.)"
        " Used for blast-radius grouping and skill-escape detection.",
    )

    # ── Risk ─────────────────────────────────────────────────────────────
    prompt_injection_surface: PromptInjectionSurface = Field(default=PromptInjectionSurface.LOW)
    data_exfiltration_risk: DataExfiltrationRisk = Field(default=DataExfiltrationRisk.LOW)
    allow_python_fallback: bool = Field(
        default=False,
        description="If True, Python execution is allowed. Default False kills universal fallback.",
    )

    # ── Trust lifecycle ──────────────────────────────────────────────────
    trust_state: TrustState = Field(default=TrustState.UNKNOWN)

    # ── Three Beasts — Gödel-lock, Strange Loop, Anti-sink ────────────────

    # Gödel-lock (Mission 001): external witness required for irreversible actions
    requires_external_witness: bool = Field(
        default=False, description="If True, irreversible mutations require an external witness."
    )

    # ── Contract bindings (RSI 2026-06-22 FORGE) ─────────────────────────
    # Per sovereign directive: every callable tool needs four bindings —
    # capability identity, authority rule, mode contract, audit rule.
    allowed_actors: list[str] | None = Field(
        default=None,
        description="Per-actor allowlist. If set, only these actor_ids may invoke. "
        "Bypassed for SOVEREIGN authority (the human is always allowed).",
    )
    witness_types: list[WitnessType] | None = Field(
        default=None, description="Accepted witness types for this capability. Empty/None = any."
    )
    modes: list[str] | None = Field(
        default=None,
        description="Bounded behavior modes this capability exposes. Empty/None = no mode check.",
    )
    bootstrap: bool = Field(
        default=False,
        description="Bootstrap floor flag. If True, the capability is always reachable "
        "for read-only introspection — bypassing the Unknown Capability DENY. "
        "Used for self-diagnosis tools (arif_kernel_status, arif_explain_denial). "
        "Bootstrap tools MUST have mutation_class=NONE.",
    )

    # Strange Loop (Mission 002): external anchor required for mutations
    requires_external_anchor: bool = Field(
        default=False,
        description="If True, ADMIT_MUTATE requires at least one EXTERNAL_* evidence source.",
    )

    # Anti-sink (Mission 003): prevent infinite simulation without action
    max_simulations_before_action: int = Field(
        default=0,
        description="Max ADMIT_SIMULATE calls before action or refusal is required. 0 = unlimited.",
    )
    requires_action_or_refusal_log: bool = Field(
        default=False,
        description="If True, tool cannot be simulated indefinitely. Must either act or log refusal.",
    )
    simulation_expiry_seconds: int | None = Field(
        default=None, description="Simulation session expires after N seconds. None = no expiry."
    )

    # ── Schema integrity ─────────────────────────────────────────────────
    schema_hash: str | None = Field(
        default=None, description="SHA-256 hash of inputSchema + outputSchema for drift detection."
    )
    policy_hash: str | None = Field(
        default=None,
        description="Hash of the policy rules applied to this capability at compile time.",
    )

    def compute_hash(self) -> str:
        """Deterministic hash of this capability's constitutional fields."""
        data = {
            "capability_id": self.capability_id,
            "tool_name": self.tool_name,
            "server_id": self.server_id,
            "authority_required": self.authority_required.value,
            "mutation_class": self.mutation_class.value,
            "irreversible": self.irreversible,
            "blast_radius": self.blast_radius.value,
            "resource_class": self.resource_class.value,
            "organ_id": self.organ_id,
            "trust_state": self.trust_state.value,
            "requires_888_hold": self.requires_888_hold,
            "requires_external_witness": self.requires_external_witness,
            "requires_external_anchor": self.requires_external_anchor,
            "max_simulations_before_action": self.max_simulations_before_action,
            "requires_action_or_refusal_log": self.requires_action_or_refusal_log,
        }
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# Graph Version — for replayable, time-travel capability queries
# ═══════════════════════════════════════════════════════════════════════════════


class GraphVersion(BaseModel):
    """A snapshot of the capability graph at a point in time."""

    version_id: str = Field(description="Monotonic version ID, e.g. 'v0.2.1' or a SHA")
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    capability_count: int = Field(default=0)
    graph_hash: str = Field(default="", description="SHA-256 of all capability hashes, sorted")
    parent_version: str | None = Field(default=None, description="Previous version for lineage")
    sealed_at: str | None = Field(default=None, description="When this version was sealed to vault")
    sealed_chain_hash: str | None = Field(default=None, description="VAULT999 chain hash if sealed")
    description: str = Field(default="")

    @staticmethod
    def compute_graph_hash(capabilities: list[CapabilityNode]) -> str:
        """Deterministic hash of the entire graph."""
        hashes = sorted(c.compute_hash() for c in capabilities)
        combined = "".join(hashes).encode("utf-8")
        return hashlib.sha256(combined).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# CapabilityGraph — the compiled, versioned, queryable graph
# ═══════════════════════════════════════════════════════════════════════════════


class CapabilityGraph(BaseModel):
    """The kernel's constitutional map of power.

    Not a tool list. Not metadata. A compiled ontology of what tools are,
    what they do, what authority they require, and what effects they produce.

    The kernel is not truth. The kernel is the constitutional boundary
    that prevents untruth, drift, and unauthorized power from crossing
    into reality.
    """

    version: GraphVersion = Field(default_factory=lambda: GraphVersion(version_id="v0.0.0"))
    capabilities: list[CapabilityNode] = Field(default_factory=list)

    # Internal index: (server_id, tool_name) -> CapabilityNode
    _index: dict[tuple[str, str], CapabilityNode] = {}

    def model_post_init(self, __context: Any) -> None:
        """Rebuild index after construction."""
        self._index = {}
        for cap in self.capabilities:
            self._index[(cap.server_id, cap.tool_name)] = cap
        self.version.capability_count = len(self.capabilities)
        if not self.version.graph_hash:
            self.version.graph_hash = GraphVersion.compute_graph_hash(self.capabilities)

    def add(self, cap: CapabilityNode) -> None:
        """Add or replace a capability and update the graph version."""
        key = (cap.server_id, cap.tool_name)
        existing = self._index.get(key)
        if existing:
            self.capabilities.remove(existing)
        self.capabilities.append(cap)
        self._index[key] = cap
        self.version.capability_count = len(self.capabilities)
        self.version.graph_hash = GraphVersion.compute_graph_hash(self.capabilities)

    def query(
        self,
        server_id: str,
        tool_name: str,
        actor_id: str | None = None,
        authority: AuthorityTier | None = None,
        at_version: GraphVersion | None = None,
        session_state: dict[str, Any] | None = None,
    ) -> CapabilityNode | None:
        """Query the graph for a capability.

        The primary lookup path for the Constitutional Interceptor.

        Args:
            server_id: Origin MCP server.
            tool_name: The tool being called.
            actor_id: Who is calling (for per-actor quarantine checks).
            authority: Current session authority tier (for trust_state override).
            at_version: If provided, only return capabilities that existed in this version.
                         If None, use current version.
            session_state: Optional session context for per-session overrides.

        Returns:
            CapabilityNode if found, None if unknown.
        """
        # Direct lookup first
        cap = self._index.get((server_id, tool_name))
        if cap is None:
            # Wildcard fallback per server
            cap = self._index.get((server_id, "*"))

        if cap is None:
            return None

        # If querying a past version, check that the capability existed then
        if at_version is not None:
            # For now, just check the version description — full history tracking is v0.3
            if cap not in self.capabilities:
                return None

        return cap

    def get_by_resource_class(self, rc: ResourceClass) -> list[CapabilityNode]:
        """Return all capabilities touching a given resource class."""
        return [c for c in self.capabilities if c.resource_class == rc]

    def get_by_organ(self, organ_id: str) -> list[CapabilityNode]:
        """Return all capabilities for a given organ."""
        return [c for c in self.capabilities if c.organ_id == organ_id]

    def diff(self, other: CapabilityGraph) -> dict[str, list[str]]:
        """Compare two graph versions. Returns added, removed, changed capability IDs."""
        a_map = {c.capability_id: c for c in self.capabilities}
        b_map = {c.capability_id: c for c in other.capabilities}

        added = list(set(b_map.keys()) - set(a_map.keys()))
        removed = list(set(a_map.keys()) - set(b_map.keys()))
        changed = [
            cid
            for cid in set(a_map.keys()) & set(b_map.keys())
            if a_map[cid].compute_hash() != b_map[cid].compute_hash()
        ]
        return {"added": sorted(added), "removed": sorted(removed), "changed": sorted(changed)}

    def to_dict(self) -> dict[str, Any]:
        """Serialise for sealing / export."""
        return {
            "version": self.version.model_dump(mode="json"),
            "capabilities": [
                c.model_dump(mode="json")
                for c in sorted(self.capabilities, key=lambda x: x.capability_id)
            ],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Interceptor input / output (unchanged from v0.1)
# ═══════════════════════════════════════════════════════════════════════════════


class InterceptorInput(BaseModel):
    """Normalised form of an inbound MCP tool call."""

    raw_tool_name: str
    raw_arguments: dict
    server_id: str = "local"
    actor_id: str | None = None
    session_id: str | None = None
    authority_tier: AuthorityTier = AuthorityTier.LOW


class InterceptorDecision(BaseModel):
    """The kernel's answer. Every MCP call produces exactly one."""

    verdict: AdmissibilityVerdict
    reason: str
    capability_id: str | None = None
    actor_id: str | None = None
    authority_tier: AuthorityTier | None = None
    mutation_class: MutationClass | None = None
    blast_radius: BlastRadius | None = None
    resource_class: ResourceClass | None = None
    organ_id: str | None = None
    graph_version: str | None = None
    # ── Three Beasts fields ──────────────────────────────────────────────
    witness: Witness | None = Field(default=None)
    evidence_sources: list[EvidenceSource] = Field(default_factory=list)
    truth_class: TruthClass | None = Field(
        default=None, description="Set after classification. Default None until admission step."
    )
    sink_risk: SinkRisk = Field(default=SinkRisk.NONE)
    simulation_count_before_decision: int = Field(default=0)

    normalized_request: dict = Field(default_factory=dict)
    rewrite_hint: str | None = Field(
        default=None,
        description="Optional instruction to prepend to tool arguments, e.g. 'SIMULATION_MODE'",
    )
