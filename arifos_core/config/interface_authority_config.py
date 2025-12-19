"""Interface & Authority Configuration Loader.

Loads spec/v43/interface_and_authority.json, validates structure,
and exposes typed config objects for LLM wrappers and FederationEngine.

Usage:
    from arifos_core.config.interface_authority_config import InterfaceAuthorityConfig
    
    config = InterfaceAuthorityConfig.load()
    
    # Access identity
    assert config.identity.arifos_is_governor == True
    assert config.identity.arifos_is_agi == False
    
    # Access LLM contract
    verdicts = config.llm_contract.must_accept_verdicts
    floors = config.llm_contract.must_accept_floors
    
    # Access agent mandates
    law_agent = config.federated_agents.get_agent("@LAW")
    assert law_agent.veto_type == "VOID_HARD"
    assert law_agent.absolute_authority == True
    
    # Access roles
    can_seal = config.roles.system3_human_sovereign.can_seal_canon
    
    # Validate deployment
    config.deployment_policy.require_all_floors_enabled  # True

Track: C (Implementation)
Version: 43.0
Authority: spec/v43/interface_and_authority.json
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class VerdictType(str, Enum):
    """Verdict types that LLMs must accept."""
    STOP = "STOP"
    SABAR = "SABAR"
    VOID = "VOID"
    PARTIAL = "PARTIAL"
    HOLD_888 = "HOLD_888"
    SEAL = "SEAL"
    SUNSET = "SUNSET"


class VetoType(str, Enum):
    """Veto types for federated agents."""
    VOID_HARD = "VOID_HARD"
    HOLD_888 = "HOLD_888"
    SABAR_SOFT = "SABAR_SOFT"
    PARTIAL_SOFT = "PARTIAL_SOFT"


@dataclass
class SystemLayers:
    """Three-tier system architecture."""
    system_1_substrate: str
    system_2_governor: str
    system_3_sovereign: str


@dataclass
class Identity:
    """arifOS identity and positioning."""
    arifos_is_governor: bool
    arifos_is_agi: bool
    description: str
    system_layers: SystemLayers


@dataclass
class LLMContractCapabilities:
    """Required capabilities for LLM integration."""
    supports_refusal: bool
    supports_uncertainty_expression: bool
    supports_tool_call_wrapping: bool
    supports_system_prompts: bool
    supports_stop_signal: bool
    supports_reasoning_pause: bool


@dataclass
class LLMContract:
    """Contract that all LLMs must accept."""
    must_accept_verdicts: List[VerdictType]
    must_accept_floors: List[str]
    required_capabilities: LLMContractCapabilities
    floor_threshold_refs: Dict[str, str]
    forbidden_behaviours: List[str]


@dataclass
class FederatedAgent:
    """Configuration for a single federated agent."""
    name: str
    domain: str
    mandate: str
    floors_guarded: List[str]
    veto_type: VetoType
    absolute_authority: bool
    can_seal: bool
    can_self_modify: bool
    failure_mode: str
    metric: Optional[str] = None
    min_score_ref: Optional[str] = None
    min_threshold: Optional[float] = None


@dataclass
class FederatedAgents:
    """Collection of federated agents (W@W Federation)."""
    agents: Dict[str, FederatedAgent] = field(default_factory=dict)
    
    def get_agent(self, name: str) -> Optional[FederatedAgent]:
        """Get agent by name (e.g., '@LAW')."""
        return self.agents.get(name)
    
    def get_agents_guarding_floor(self, floor: str) -> List[FederatedAgent]:
        """Get all agents that guard a specific floor."""
        return [agent for agent in self.agents.values() if floor in agent.floors_guarded]
    
    def get_agents_by_veto_type(self, veto_type: VetoType) -> List[FederatedAgent]:
        """Get all agents with a specific veto type."""
        return [agent for agent in self.agents.values() if agent.veto_type == veto_type]


@dataclass
class AgentMandateBoundaries:
    """Absolute laws that apply to all agents."""
    no_agent_may: List[str]
    violation_consequence: str


@dataclass
class System3Sovereign:
    """Human sovereign authority."""
    description: str
    entity: str
    can_seal_canon: bool
    can_seal_runtime_high_stakes: bool
    can_override_runtime: bool
    can_modify_spec_with_phoenix72: bool
    must_not: List[str]
    bears_responsibility: bool


@dataclass
class System2Governor:
    """arifOS kernel authority."""
    description: str
    role_name: str
    can_issue_verdicts: List[VerdictType]
    can_write_ledger: bool
    can_modify_canon: bool
    can_modify_spec_at_runtime: bool
    must_route_all_outputs_through_apex: bool
    cannot_self_authorize: bool


@dataclass
class System1LLM:
    """LLM substrate authority."""
    description: str
    role_name: str
    can_generate_text: bool
    can_suggest_tools: bool
    can_decide_goals: bool
    can_issue_verdicts: bool
    can_override_floors: bool
    can_write_persistent_memory: bool
    must_accept_stop_signal: bool
    must_accept_sabar_protocol: bool
    must_accept_void_verdict: bool


@dataclass
class Roles:
    """Three-tier authority hierarchy."""
    system3_human_sovereign: System3Sovereign
    system2_arifos_kernel: System2Governor
    system1_llm_substrate: System1LLM


@dataclass
class AuthorityBoundary:
    """Boundary definition for a system component."""
    function: str
    power: str
    limits: str
    reports_to: str


@dataclass
class AuthorityBoundaries:
    """Non-negotiable boundaries between tiers."""
    apex_prime_judiciary: AuthorityBoundary
    waw_federation_organs: AuthorityBoundary
    a_clip_bridge_tools: AuthorityBoundary
    llm_substrate_cognition: AuthorityBoundary


@dataclass
class DeploymentPolicy:
    """Rules for safe deployment in production."""
    require_all_floors_enabled: bool
    require_governor_between_llm_and_world: bool
    allow_direct_llm_to_world_integration: bool
    require_cooling_ledger: bool
    require_vault_999_for_sealed_records: bool
    allow_jailbreak_prompts: bool
    allow_disabling_refusal: bool
    allow_custom_jailbreak_policies: bool
    allow_opt_out_of_governance: bool
    violation_consequence: str


@dataclass
class ToolProperties:
    """Required properties for governed tools."""
    tool_must_have_clear_scope: bool
    tool_must_have_permission_gate: bool
    tool_must_report_success_failure: bool
    tool_must_be_reversible_or_audited: bool


@dataclass
class ToolAndActionPolicy:
    """Rules for tool access and world-facing actions."""
    governed_tools_only: bool
    must_route_tool_calls_via: List[str]
    forbidden_tool_patterns: List[str]
    required_tool_properties: ToolProperties


@dataclass
class Invariant:
    """A single integration invariant."""
    law: str
    meaning: str
    enforcement: str


@dataclass
class IntegrationInvariants:
    """Seven governing laws."""
    invariants: Dict[str, Invariant] = field(default_factory=dict)
    
    def get_invariant(self, key: str) -> Optional[Invariant]:
        """Get invariant by key (e.g., 'invariant_1_no_cognition_without_cooling')."""
        return self.invariants.get(key)


@dataclass
class AmendmentProtocol:
    """Phoenix-72 amendment process."""
    status: str
    amendments_require: List[str]
    cannot_amend: List[str]


@dataclass
class SealAndAuthenticity:
    """Seal metadata."""
    status: str
    sealed_date: str
    sealed_authority: str
    sealed_timestamp: str
    canonical_source: str
    audit_trail_reference: str


@dataclass
class InterfaceAuthorityConfig:
    """Complete Interface & Authority configuration.
    
    Loads and validates spec/v43/interface_and_authority.json.
    Provides typed access to all governance rules.
    """
    version: str
    locked: bool
    identity: Identity
    llm_contract: LLMContract
    federated_agents: FederatedAgents
    agent_mandate_boundaries: AgentMandateBoundaries
    roles: Roles
    authority_boundaries: AuthorityBoundaries
    deployment_policy: DeploymentPolicy
    tool_and_action_policy: ToolAndActionPolicy
    integration_invariants: IntegrationInvariants
    amendment_protocol: AmendmentProtocol
    seal_and_authenticity: SealAndAuthenticity
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    @classmethod
    def load(cls, spec_path: Optional[Path] = None) -> "InterfaceAuthorityConfig":
        """Load and validate spec from JSON file.
        
        Args:
            spec_path: Path to spec file. If None, uses default location.
        
        Returns:
            Validated InterfaceAuthorityConfig instance.
        
        Raises:
            FileNotFoundError: If spec file doesn't exist.
            ValueError: If spec is invalid or locked=False.
            json.JSONDecodeError: If spec is not valid JSON.
        """
        if spec_path is None:
            # Default to repo root / spec / v43 / interface_and_authority.json
            repo_root = Path(__file__).parent.parent.parent
            spec_path = repo_root / "spec" / "v43" / "interface_and_authority.json"
        
        if not spec_path.exists():
            raise FileNotFoundError(
                f"Interface & Authority spec not found at {spec_path}. "
                "Expected spec/v43/interface_and_authority.json in repository root."
            )
        
        with open(spec_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        # Validate locked status
        if not raw_data.get("locked", False):
            raise ValueError(
                "Interface & Authority spec must be locked. "
                "Unlocked specs cannot be used in production."
            )
        
        # Parse identity
        identity_data = raw_data["identity"]
        identity = Identity(
            arifos_is_governor=identity_data["arifos_is_governor"],
            arifos_is_agi=identity_data["arifos_is_agi"],
            description=identity_data["description"],
            system_layers=SystemLayers(**identity_data["system_layers"])
        )
        
        # Parse LLM contract
        contract_data = raw_data["llm_contract"]
        llm_contract = LLMContract(
            must_accept_verdicts=[VerdictType(v) for v in contract_data["must_accept_verdicts"]],
            must_accept_floors=contract_data["must_accept_floors"],
            required_capabilities=LLMContractCapabilities(**contract_data["required_capabilities"]),
            floor_threshold_refs=contract_data["floor_threshold_refs"],
            forbidden_behaviours=contract_data["forbidden_behaviours"]
        )
        
        # Parse federated agents
        agents_data = raw_data["federated_agents"]
        federated_agents = FederatedAgents()
        for agent_name, agent_data in agents_data.items():
            if agent_name.startswith("_"):
                continue  # Skip comments
            agent = FederatedAgent(
                name=agent_name,
                domain=agent_data["domain"],
                mandate=agent_data["mandate"],
                floors_guarded=agent_data["floors_guarded"],
                veto_type=VetoType(agent_data["veto_type"]),
                absolute_authority=agent_data["absolute_authority"],
                can_seal=agent_data["can_seal"],
                can_self_modify=agent_data["can_self_modify"],
                failure_mode=agent_data["failure_mode"],
                metric=agent_data.get("metric"),
                min_score_ref=agent_data.get("min_score_ref"),
                min_threshold=agent_data.get("min_threshold")
            )
            federated_agents.agents[agent_name] = agent
        
        # Parse agent mandate boundaries
        boundaries_data = raw_data["agent_mandate_boundaries"]
        agent_mandate_boundaries = AgentMandateBoundaries(
            no_agent_may=boundaries_data["no_agent_may"],
            violation_consequence=boundaries_data["violation_consequence"]
        )
        
        # Parse roles
        roles_data = raw_data["roles"]
        roles = Roles(
            system3_human_sovereign=System3Sovereign(**roles_data["system3_human_sovereign"]),
            system2_arifos_kernel=System2Governor(
                description=roles_data["system2_arifos_kernel"]["description"],
                role_name=roles_data["system2_arifos_kernel"]["role_name"],
                can_issue_verdicts=[VerdictType(v) for v in roles_data["system2_arifos_kernel"]["can_issue_verdicts"]],
                can_write_ledger=roles_data["system2_arifos_kernel"]["can_write_ledger"],
                can_modify_canon=roles_data["system2_arifos_kernel"]["can_modify_canon"],
                can_modify_spec_at_runtime=roles_data["system2_arifos_kernel"]["can_modify_spec_at_runtime"],
                must_route_all_outputs_through_apex=roles_data["system2_arifos_kernel"]["must_route_all_outputs_through_apex"],
                cannot_self_authorize=roles_data["system2_arifos_kernel"]["cannot_self_authorize"]
            ),
            system1_llm_substrate=System1LLM(**roles_data["system1_llm_substrate"])
        )
        
        # Parse authority boundaries
        boundaries_data = raw_data["authority_boundaries"]
        authority_boundaries = AuthorityBoundaries(
            apex_prime_judiciary=AuthorityBoundary(**boundaries_data["APEX_PRIME_judiciary"]),
            waw_federation_organs=AuthorityBoundary(**boundaries_data["W@W_Federation_organs"]),
            a_clip_bridge_tools=AuthorityBoundary(**boundaries_data["A_CLIP_Bridge_tools"]),
            llm_substrate_cognition=AuthorityBoundary(**boundaries_data["LLM_Substrate_cognition"])
        )
        
        # Parse deployment policy
        deployment_policy = DeploymentPolicy(**raw_data["deployment_policy"])
        
        # Parse tool and action policy
        tool_policy_data = raw_data["tool_and_action_policy"]
        tool_and_action_policy = ToolAndActionPolicy(
            governed_tools_only=tool_policy_data["governed_tools_only"],
            must_route_tool_calls_via=tool_policy_data["must_route_tool_calls_via"],
            forbidden_tool_patterns=tool_policy_data["forbidden_tool_patterns"],
            required_tool_properties=ToolProperties(**tool_policy_data["required_tool_properties"])
        )
        
        # Parse integration invariants
        invariants_data = raw_data["integration_invariants"]
        integration_invariants = IntegrationInvariants()
        for key, inv_data in invariants_data.items():
            if key.startswith("_"):
                continue
            integration_invariants.invariants[key] = Invariant(**inv_data)
        
        # Parse amendment protocol
        amendment_protocol = AmendmentProtocol(**raw_data["amendment_protocol"])
        
        # Parse seal and authenticity
        seal_and_authenticity = SealAndAuthenticity(**raw_data["_seal_and_authenticity"])
        
        return cls(
            version=raw_data["version"],
            locked=raw_data["locked"],
            identity=identity,
            llm_contract=llm_contract,
            federated_agents=federated_agents,
            agent_mandate_boundaries=agent_mandate_boundaries,
            roles=roles,
            authority_boundaries=authority_boundaries,
            deployment_policy=deployment_policy,
            tool_and_action_policy=tool_and_action_policy,
            integration_invariants=integration_invariants,
            amendment_protocol=amendment_protocol,
            seal_and_authenticity=seal_and_authenticity,
            _raw=raw_data
        )
    
    def validate_llm_compliance(self, llm_name: str, llm_capabilities: Dict[str, bool]) -> List[str]:
        """Validate that an LLM meets contract requirements.
        
        Args:
            llm_name: Name of LLM being validated (e.g., 'Claude 3.5 Sonnet').
            llm_capabilities: Dict of capability flags (keys from LLMContractCapabilities).
        
        Returns:
            List of violation messages. Empty list means compliant.
        """
        violations = []
        required = self.llm_contract.required_capabilities
        
        if not llm_capabilities.get("supports_refusal", False) and required.supports_refusal:
            violations.append(f"{llm_name}: Must support refusal (VOID/SABAR acceptance)")
        
        if not llm_capabilities.get("supports_uncertainty_expression", False) and required.supports_uncertainty_expression:
            violations.append(f"{llm_name}: Must support uncertainty expression (Ω₀ band)")
        
        if not llm_capabilities.get("supports_tool_call_wrapping", False) and required.supports_tool_call_wrapping:
            violations.append(f"{llm_name}: Must support tool call wrapping")
        
        if not llm_capabilities.get("supports_system_prompts", False) and required.supports_system_prompts:
            violations.append(f"{llm_name}: Must support system prompts")
        
        if not llm_capabilities.get("supports_stop_signal", False) and required.supports_stop_signal:
            violations.append(f"{llm_name}: Must support STOP signal")
        
        if not llm_capabilities.get("supports_reasoning_pause", False) and required.supports_reasoning_pause:
            violations.append(f"{llm_name}: Must support reasoning pause (SABAR protocol)")
        
        return violations
    
    def get_forbidden_behaviours_for_llm(self) -> List[str]:
        """Get list of behaviours that LLM must never exhibit."""
        return self.llm_contract.forbidden_behaviours
    
    def get_all_floors(self) -> List[str]:
        """Get list of all floors that must be checked."""
        return self.llm_contract.must_accept_floors
    
    def get_all_verdicts(self) -> List[VerdictType]:
        """Get list of all verdicts that LLM must accept."""
        return self.llm_contract.must_accept_verdicts
