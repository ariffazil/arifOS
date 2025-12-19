"""Example: Using InterfaceAuthorityConfig.

Demonstrates how to load and use the Interface & Authority spec
in your LLM wrappers and governance code.

Track: C (Implementation Examples)
Version: 43.0
"""

from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifos_core.config.interface_authority_config import (
    InterfaceAuthorityConfig,
    VerdictType,
    VetoType
)


def main():
    """Demonstrate config loading and usage."""
    
    print("=" * 70)
    print("Interface & Authority Config Usage Example")
    print("=" * 70)
    print()
    
    # 1. LOAD CONFIG
    print("[1] Loading config from spec/v43/interface_and_authority.json...")
    config = InterfaceAuthorityConfig.load()
    print(f"    ✓ Loaded version: {config.version}")
    print(f"    ✓ Locked: {config.locked}")
    print(f"    ✓ Sealed: {config.seal_and_authenticity.status}")
    print(f"    ✓ Authority: {config.seal_and_authenticity.sealed_authority}")
    print()
    
    # 2. VALIDATE IDENTITY
    print("[2] Validating arifOS identity...")
    print(f"    ✓ arifOS is governance kernel: {config.identity.arifos_is_governor}")
    print(f"    ✓ arifOS is NOT AGI: {not config.identity.arifos_is_agi}")
    print(f"    ✓ System-3: {config.identity.system_layers.system_3_sovereign}")
    print(f"    ✓ System-2: {config.identity.system_layers.system_2_governor}")
    print(f"    ✓ System-1: {config.identity.system_layers.system_1_substrate}")
    print()
    
    # 3. CHECK LLM CONTRACT
    print("[3] LLM Contract requirements...")
    print(f"    ✓ Must accept {len(config.llm_contract.must_accept_verdicts)} verdicts:")
    for verdict in config.llm_contract.must_accept_verdicts:
        print(f"      - {verdict.value}")
    print(f"    ✓ Must satisfy {len(config.llm_contract.must_accept_floors)} floors")
    print(f"    ✓ {len(config.llm_contract.forbidden_behaviours)} forbidden behaviours")
    print()
    
    # 4. VALIDATE SAMPLE LLM
    print("[4] Validating sample LLM compliance...")
    
    # Claude example (compliant)
    claude_caps = {
        "supports_refusal": True,
        "supports_uncertainty_expression": True,
        "supports_tool_call_wrapping": True,
        "supports_system_prompts": True,
        "supports_stop_signal": True,
        "supports_reasoning_pause": True
    }
    claude_violations = config.validate_llm_compliance("Claude 3.5 Sonnet", claude_caps)
    if not claude_violations:
        print("    ✓ Claude 3.5 Sonnet: COMPLIANT")
    else:
        print(f"    ✗ Claude 3.5 Sonnet violations: {claude_violations}")
    
    # Non-compliant LLM example
    basic_llm_caps = {
        "supports_refusal": False,
        "supports_uncertainty_expression": False,
        "supports_tool_call_wrapping": False,
        "supports_system_prompts": True,
        "supports_stop_signal": False,
        "supports_reasoning_pause": False
    }
    basic_violations = config.validate_llm_compliance("Basic LLM", basic_llm_caps)
    if basic_violations:
        print(f"    ✗ Basic LLM: NON-COMPLIANT ({len(basic_violations)} violations)")
        for v in basic_violations:
            print(f"      - {v}")
    print()
    
    # 5. EXPLORE FEDERATED AGENTS
    print("[5] Federated agents (W@W Federation)...")
    for agent_name, agent in config.federated_agents.agents.items():
        print(f"    {agent_name}:")
        print(f"      Domain: {agent.domain}")
        print(f"      Veto: {agent.veto_type.value}")
        print(f"      Absolute authority: {agent.absolute_authority}")
        print(f"      Guards floors: {', '.join(agent.floors_guarded) if agent.floors_guarded else 'None'}")
    print()
    
    # 6. CHECK SPECIFIC AGENT
    print("[6] Checking @LAW agent (constitutional gate)...")
    law_agent = config.federated_agents.get_agent("@LAW")
    if law_agent:
        print(f"    ✓ Domain: {law_agent.domain}")
        print(f"    ✓ Veto type: {law_agent.veto_type.value}")
        print(f"    ✓ Absolute authority: {law_agent.absolute_authority}")
        print(f"    ✓ Failure mode: {law_agent.failure_mode}")
        print(f"    ✓ Guards {len(law_agent.floors_guarded)} floors")
    print()
    
    # 7. CHECK AUTHORITY HIERARCHY
    print("[7] Authority hierarchy...")
    print(f"    System-3 (Human Sovereign):")
    print(f"      ✓ Can seal canon: {config.roles.system3_human_sovereign.can_seal_canon}")
    print(f"      ✓ Can override runtime: {config.roles.system3_human_sovereign.can_override_runtime}")
    print(f"      ✓ Entity: {config.roles.system3_human_sovereign.entity}")
    print()
    print(f"    System-2 (arifOS Governor):")
    print(f"      ✓ Can issue verdicts: {len(config.roles.system2_arifos_kernel.can_issue_verdicts)}")
    print(f"      ✓ Can modify canon: {config.roles.system2_arifos_kernel.can_modify_canon}")
    print(f"      ✓ Must route through APEX: {config.roles.system2_arifos_kernel.must_route_all_outputs_through_apex}")
    print()
    print(f"    System-1 (LLM Substrate):")
    print(f"      ✓ Can generate text: {config.roles.system1_llm_substrate.can_generate_text}")
    print(f"      ✓ Can decide goals: {config.roles.system1_llm_substrate.can_decide_goals}")
    print(f"      ✓ Can issue verdicts: {config.roles.system1_llm_substrate.can_issue_verdicts}")
    print()
    
    # 8. CHECK DEPLOYMENT POLICY
    print("[8] Deployment policy enforcement...")
    print(f"    ✓ All floors must be enabled: {config.deployment_policy.require_all_floors_enabled}")
    print(f"    ✓ Governor between LLM and world: {config.deployment_policy.require_governor_between_llm_and_world}")
    print(f"    ✓ Allow jailbreak prompts: {config.deployment_policy.allow_jailbreak_prompts}")
    print(f"    ✓ Require cooling ledger: {config.deployment_policy.require_cooling_ledger}")
    print(f"    ✓ Require Vault-999: {config.deployment_policy.require_vault_999_for_sealed_records}")
    print()
    
    # 9. CHECK TOOL POLICY
    print("[9] Tool and action policy...")
    print(f"    ✓ Governed tools only: {config.tool_and_action_policy.governed_tools_only}")
    print(f"    ✓ Route via: {', '.join(config.tool_and_action_policy.must_route_tool_calls_via)}")
    print(f"    ✓ Forbidden patterns: {len(config.tool_and_action_policy.forbidden_tool_patterns)}")
    for pattern in config.tool_and_action_policy.forbidden_tool_patterns[:3]:
        print(f"      - {pattern}")
    print()
    
    # 10. INTEGRATION INVARIANTS
    print("[10] Integration invariants (7 governing laws)...")
    for key, invariant in config.integration_invariants.invariants.items():
        print(f"    {key}:")
        print(f"      Law: {invariant.law}")
        print(f"      Enforcement: {invariant.enforcement}")
    print()
    
    # 11. PRACTICAL USAGE PATTERN
    print("[11] Practical usage in LLM wrapper...")
    print("""    
    # In your LLM wrapper code:
    
    config = InterfaceAuthorityConfig.load()
    
    # Before accepting LLM output:
    if not config.deployment_policy.require_all_floors_enabled:
        raise ValueError("All floors must be enabled in production")
    
    # Check if tool call is allowed:
    if tool_name in config.tool_and_action_policy.forbidden_tool_patterns:
        return Verdict.VOID("Forbidden tool pattern")
    
    # Route through federation:
    for agent_name in ["@LAW", "@GEOX", "@WELL", "@RIF", "@PROMPT"]:
        agent = config.federated_agents.get_agent(agent_name)
        verdict = agent.evaluate(output)  # Your implementation
        if verdict.is_blocking():
            return verdict
    
    # Issue final verdict through APEX_PRIME
    return apex_prime.issue_verdict(output, config)
    """)
    print()
    
    print("=" * 70)
    print("✓ Config loaded and validated successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
