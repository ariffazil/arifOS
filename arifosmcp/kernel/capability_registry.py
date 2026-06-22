"""
arifosmcp/kernel/capability_registry.py — Capability Graph v0.2 Compiler

Builds, seeds, and serves the kernel's CapabilityGraph.

v0.2:
- Returns a CapabilityGraph instance, not a static dict
- Every capability has full constitutional metadata (trust_state, resource_class, organ_id, risk fields)
- Graph is versioned, hashed, and diffable
- add_capability() lets the dynamic discovery compiler add new servers at runtime

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from .models import (
    AuthorityTier,
    BlastRadius,
    CapabilityGraph,
    CapabilityNode,
    DataExfiltrationRisk,
    GraphVersion,
    MutationClass,
    PromptInjectionSurface,
    ResourceClass,
    TrustState,
)


def _build_default_graph() -> CapabilityGraph:
    """Build and return the default capability graph.

    In v0.2, this is a static seed. Future: merge with dynamic server discovery.
    """
    capabilities: list[CapabilityNode] = [
        # ── Python execution ──────────────────────────────────────────────
        CapabilityNode(
            capability_id="runtime.py",
            tool_name="py",
            server_id="local",
            description="Python code execution",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.LOCAL_STATE,
            irreversible=False,
            blast_radius=BlastRadius.PROCESS,
            resource_class=ResourceClass.PROCESS,
            simulation_available=True,
            rollback_available=False,
            audit_required=True,
            prompt_injection_surface=PromptInjectionSurface.HIGH,
            data_exfiltration_risk=DataExfiltrationRisk.HIGH,
            trust_state=TrustState.SANDBOXED,
            allow_python_fallback=False,
            # Three Beasts: py has a simulation budget
            max_simulations_before_action=20,
            requires_action_or_refusal_log=True,
        ),
        CapabilityNode(
            capability_id="runtime.python_repl",
            tool_name="python_repl",
            server_id="local",
            description="Python REPL execution",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.LOCAL_STATE,
            irreversible=False,
            blast_radius=BlastRadius.PROCESS,
            resource_class=ResourceClass.PROCESS,
            simulation_available=True,
            rollback_available=False,
            audit_required=True,
            prompt_injection_surface=PromptInjectionSurface.HIGH,
            data_exfiltration_risk=DataExfiltrationRisk.HIGH,
            trust_state=TrustState.SANDBOXED,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="runtime.bash",
            tool_name="bash",
            server_id="local",
            description="Bash command execution",
            authority_required=AuthorityTier.HIGH,
            mutation_class=MutationClass.ORG_STATE,
            irreversible=False,
            blast_radius=BlastRadius.PROCESS,
            resource_class=ResourceClass.PROCESS,
            simulation_available=True,
            rollback_available=False,
            audit_required=True,
            prompt_injection_surface=PromptInjectionSurface.HIGH,
            data_exfiltration_risk=DataExfiltrationRisk.HIGH,
            requires_888_hold=True,
            trust_state=TrustState.PROBATION,
            allow_python_fallback=False,
        ),

        # ── Filesystem ────────────────────────────────────────────────────
        CapabilityNode(
            capability_id="fs.read",
            tool_name="read",
            server_id="local",
            description="Read file from filesystem",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.FILE,
            trust_state=TrustState.TRUSTED_READ,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="fs.write",
            tool_name="write",
            server_id="local",
            description="Write file to filesystem",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.ORG_STATE,
            irreversible=False,
            blast_radius=BlastRadius.PROCESS,
            resource_class=ResourceClass.FILE,
            audit_required=True,
            simulation_available=True,
            trust_state=TrustState.TRUSTED_MUTATE,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="fs.edit",
            tool_name="edit",
            server_id="local",
            description="Edit file in place",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.ORG_STATE,
            irreversible=False,
            blast_radius=BlastRadius.PROCESS,
            resource_class=ResourceClass.FILE,
            audit_required=True,
            simulation_available=True,
            trust_state=TrustState.TRUSTED_MUTATE,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="fs.glob",
            tool_name="glob",
            server_id="local",
            description="File pattern matching",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.FILE,
            trust_state=TrustState.TRUSTED_READ,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="fs.grep",
            tool_name="grep",
            server_id="local",
            description="Content search in files",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.FILE,
            trust_state=TrustState.TRUSTED_READ,
            allow_python_fallback=False,
        ),

        # ── Web / Network ─────────────────────────────────────────────────
        CapabilityNode(
            capability_id="web.search",
            tool_name="websearch",
            server_id="local",
            description="Web search",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.HTTP_ENDPOINT,
            trust_state=TrustState.TRUSTED_READ,
            allow_python_fallback=False,
        ),
        CapabilityNode(
            capability_id="web.fetch",
            tool_name="webfetch",
            server_id="local",
            description="Fetch URL content",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.HTTP_ENDPOINT,
            trust_state=TrustState.TRUSTED_READ,
            allow_python_fallback=False,
        ),

        # ── Kernel tools (arifOS MCP) ─────────────────────────────────────
        CapabilityNode(
            capability_id="kernel.init",
            tool_name="arif_init",
            server_id="local",
            description="Initialize constitutional session",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.MEMORY,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.observe",
            tool_name="arif_observe",
            server_id="local",
            description="Observe reality (search, fetch, vitals)",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.NETWORK,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.think",
            tool_name="arif_think",
            server_id="local",
            description="Multi-step reasoning",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.MEMORY,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.judge",
            tool_name="arif_judge",
            server_id="local",
            description="Constitutional judgment",
            authority_required=AuthorityTier.SOVEREIGN,
            mutation_class=MutationClass.ORG_STATE,
            irreversible=False,
            blast_radius=BlastRadius.ORGAN,
            resource_class=ResourceClass.MEMORY,
            organ_id="arifOS",
            requires_888_hold=True,
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.seal",
            tool_name="arif_seal",
            server_id="local",
            description="Seal to VAULT999",
            authority_required=AuthorityTier.SOVEREIGN,
            mutation_class=MutationClass.IRREVERSIBLE,
            irreversible=True,
            blast_radius=BlastRadius.FEDERATION,
            resource_class=ResourceClass.VAULT_ENTRY,
            organ_id="arifOS",
            requires_888_hold=True,
            audit_required=True,
            trust_state=TrustState.TRUSTED_MUTATE,
            prompt_injection_surface=PromptInjectionSurface.HIGH,
            data_exfiltration_risk=DataExfiltrationRisk.LOW,
            # Three Beasts: seal is irreversible + requires external witness
            requires_external_witness=True,
            requires_external_anchor=True,
        ),
        CapabilityNode(
            capability_id="kernel.canary",
            tool_name="arif_canary",
            server_id="local",
            description="Unified diagnostic probe",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.MEMORY,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.conformance_report",
            tool_name="arif_conformance_report",
            server_id="local",
            description="Run full conformance spine",
            authority_required=AuthorityTier.LOW,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.MEMORY,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.vault_query",
            tool_name="hermes_vault_query",
            server_id="local",
            description="Query VAULT999 entries",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.LOCAL,
            resource_class=ResourceClass.VAULT_ENTRY,
            organ_id="arifOS",
            trust_state=TrustState.TRUSTED_READ,
        ),
        CapabilityNode(
            capability_id="kernel.forge",
            tool_name="arif_forge",
            server_id="local",
            description="Execute forge operations",
            authority_required=AuthorityTier.HIGH,
            mutation_class=MutationClass.ORG_STATE,
            irreversible=True,
            blast_radius=BlastRadius.ORGAN,
            resource_class=ResourceClass.FILE,
            organ_id="A-FORGE",
            requires_888_hold=True,
            audit_required=True,
            simulation_available=True,
            trust_state=TrustState.TRUSTED_MUTATE,
            prompt_injection_surface=PromptInjectionSurface.HIGH,
            data_exfiltration_risk=DataExfiltrationRisk.MEDIUM,
            # Three Beasts: forge requires external anchor + simulation budget
            requires_external_anchor=True,
            max_simulations_before_action=10,
            requires_action_or_refusal_log=True,
        ),

        # ── GEOX organ ────────────────────────────────────────────────────
        CapabilityNode(
            capability_id="organ.geox.*",
            tool_name="*",
            server_id="geox",
            description="GEOX earth intelligence organ (all tools)",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.ORGAN,
            resource_class=ResourceClass.MCP_SERVER,
            organ_id="GEOX",
            trust_state=TrustState.TRUSTED_READ,
        ),

        # ── WEALTH organ ──────────────────────────────────────────────────
        CapabilityNode(
            capability_id="organ.wealth.*",
            tool_name="*",
            server_id="wealth",
            description="WEALTH capital intelligence organ (all tools)",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.ORGAN,
            resource_class=ResourceClass.MCP_SERVER,
            organ_id="WEALTH",
            trust_state=TrustState.TRUSTED_READ,
        ),

        # ── WELL organ ────────────────────────────────────────────────────
        CapabilityNode(
            capability_id="organ.well.*",
            tool_name="*",
            server_id="well",
            description="WELL human readiness organ (all tools)",
            authority_required=AuthorityTier.MEDIUM,
            mutation_class=MutationClass.NONE,
            irreversible=False,
            blast_radius=BlastRadius.ORGAN,
            resource_class=ResourceClass.MCP_SERVER,
            organ_id="WELL",
            trust_state=TrustState.TRUSTED_READ,
        ),
    ]

    version = GraphVersion(
        version_id="v0.2.0",
        description="Initial Capability Graph — 22 nodes covering runtime, fs, web, kernel, and organ servers",
    )

    graph = CapabilityGraph(version=version, capabilities=capabilities)
    graph.model_post_init(None)
    return graph


# ── Singleton — the kernel's compiled graph ───────────────────────────────────

_GRAPH: CapabilityGraph | None = None
_GRAPH_SEALED_VERSION: str | None = None


def get_capability_graph() -> CapabilityGraph:
    """Return the kernel's compiled capability graph (lazy singleton)."""
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = _build_default_graph()
    return _GRAPH


def rebuild_capability_graph(reason: str = "") -> CapabilityGraph:
    """Rebuild the capability graph from scratch and return the new version.

    Used when servers are discovered or trust states change.
    """
    global _GRAPH, _GRAPH_SEALED_VERSION
    _GRAPH = _build_default_graph()
    _GRAPH.version.description = reason or _GRAPH.version.description
    return _GRAPH


def register_capability(cap: CapabilityNode) -> None:
    """Register a new capability at runtime (for dynamic server discovery)."""
    graph = get_capability_graph()
    graph.add(cap)


def resolve_capability(
    server_id: str,
    tool_name: str,
    actor_id: str | None = None,
    authority: AuthorityTier | None = None,
) -> CapabilityNode | None:
    """Resolve a (server_id, tool_name) pair to a CapabilityNode.

    v0.2: delegates to CapabilityGraph.query() with current version.
    """
    graph = get_capability_graph()
    return graph.query(
        server_id=server_id,
        tool_name=tool_name,
        actor_id=actor_id,
        authority=authority,
    )


def all_capabilities() -> list[CapabilityNode]:
    """Return all registered capabilities for inspection."""
    return get_capability_graph().capabilities
