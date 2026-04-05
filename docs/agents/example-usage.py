#!/usr/bin/env python3
"""
arifOS Agent Control Plane - Example Usage
Demonstrates the 6 blindspot fixes in action.

For architectural doctrine, see:
- /arifOS/AGENTS/EUREKA_COMPENDIUM.md (TCP analogy, Trinity, 13 Floors)
- /arifOS/AGENTS/A000_HUB.md (Trinity mapping)
- /arifOS/AGENTS/A100_ARCHITECT.md (System design)

This runtime: /arifosmcp/AGENTS/ (operational control plane)
"""

from execution_controller import (
    AgentRole,
    ExecutionController,
    check_quarantined,
)


def example_1_agent_identity():
    """BLINDSPOT #1: Per-agent identity and policy."""
    print("=" * 60)
    print("EXAMPLE 1: Agent Identity + Policy")
    print("=" * 60)

    controller = ExecutionController()

    # Check what A-ENGINEER can do
    engineer = controller.get_agent_identity(AgentRole.ENGINEER)
    print("\nA-ENGINEER Identity:")
    print(f"  UUID: {engineer.uuid}")
    print(f"  Can write: {engineer.can_write}")
    print(f"  Can deploy: {engineer.can_deploy}")
    print(f"  Allowed tools: {len(engineer.tools_allowed)}")
    print(f"  Forbidden tools: {len(engineer.tools_forbidden)}")

    # Check what A-VALIDATOR can do
    validator = controller.get_agent_identity(AgentRole.VALIDATOR)
    print("\nA-VALIDATOR Identity:")
    print(f"  Can write: {validator.can_write}")
    print(f"  Can deploy: {validator.can_deploy}")
    print(f"  Can issue SEAL: {validator.can_issue_seal}")


def example_2_policy_enforcement():
    """BLINDSPOT #1: Policy-gated execution."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Policy Enforcement")
    print("=" * 60)

    controller = ExecutionController()

    # A-ENGINEER tries to deploy (should fail)
    print("\nA-ENGINEER attempting deploy:")
    receipt = controller.execute(
        agent_role=AgentRole.ENGINEER,
        intent="Deploy to production",
        tools=["docker_deploy"],
        files=[],
        dry_run=True,
    )
    print(f"  Verdict: {receipt.verdict.value}")
    print("  Reason: Only A-VALIDATOR can deploy")

    # A-VALIDATOR attempts deploy (would need approval)
    print("\nA-VALIDATOR attempting deploy:")
    receipt = controller.execute(
        agent_role=AgentRole.VALIDATOR,
        intent="Deploy v2.5 to production",
        tools=["docker_deploy"],
        files=[],
        dry_run=True,
    )
    print(f"  Verdict: {receipt.verdict.value}")
    print(f"  Human approval: {receipt.human_approval}")


def example_3_quarantined_paths():
    """BLINDSPOT #5: Broken power paths quarantined."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Quarantined Broken Paths")
    print("=" * 60)

    quarantined = [
        "kimi_inside_openclaw",
        "aider_inside_openclaw",
        "opencode_inside_openclaw",
    ]

    for path in quarantined:
        ok, msg = check_quarantined(path)
        print(f"\n  {path}:")
        print(f"    Status: {'QUARANTINED' if not ok else 'ACTIVE'}")
        print(f"    Reason: {msg}")


def example_4_execution_receipt():
    """All actions generate immutable receipts."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Execution Receipt (VAULT999)")
    print("=" * 60)

    controller = ExecutionController()

    receipt = controller.execute(
        agent_role=AgentRole.ARCHITECT,
        intent="Design memory subsystem",
        tools=["read_file", "search_reality"],
        files=["memory.py"],
        dry_run=True,
    )

    print(f"\n  Receipt ID: {receipt.receipt_id}")
    print(f"  Agent: {receipt.agent_id}")
    print(f"  Verdict: {receipt.verdict.value}")
    print(f"  Merkle Hash: {receipt.merkle_hash[:16]}...")
    print(f"  Vault Seal: {receipt.sealed_to_vault999}")


def example_5_hard_separation():
    """Hard separation between read, edit, deploy, destroy."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Hard Separation Matrix")
    print("=" * 60)

    controller = ExecutionController()

    actions = ["read_file", "write_file", "file_delete", "docker_deploy"]
    agents = [
        ("ARCHITECT", AgentRole.ARCHITECT),
        ("ENGINEER", AgentRole.ENGINEER),
        ("AUDITOR", AgentRole.AUDITOR),
        ("VALIDATOR", AgentRole.VALIDATOR),
    ]

    print("\n  Permission Matrix:")
    print(f"  {'Action':<20} {'ARCH':<8} {'ENG':<8} {'AUD':<8} {'VAL':<8}")
    print("  " + "-" * 60)

    for action in actions:
        row = f"  {action:<20}"
        for _, role in agents:
            agent = controller.get_agent_identity(role)
            ok, _ = agent.has_permission(action)
            row += f" {'✓' if ok else '✗':<8}"
        print(row)


def main():
    print("\n" + "🛡️ " * 20)
    print("arifOS Constitutional Agent Control Plane")
    print("6 Blindspots Fixed - Demonstration")
    print("🛡️ " * 20 + "\n")

    example_1_agent_identity()
    example_2_policy_enforcement()
    example_3_quarantined_paths()
    example_4_execution_receipt()
    example_5_hard_separation()

    print("\n" + "=" * 60)
    print("SUMMARY: 6 Blindspots Addressed")
    print("=" * 60)
    print("""
  ✅ #1: Agent identity + policy-gated execution
  ✅ #2: Unified memory ledger (memory-ledger.yaml)
  ✅ #3: Event-driven orchestration (event-bus.yaml)
  ✅ #4: Capability self-knowledge (capability-manifest.yaml)
  ✅ #5: Broken paths quarantined (kimi/aider/opencode DISABLED)
  ✅ #6: Immutable operational replay (forensic-replay.yaml)
    """)
    print("=" * 60)


if __name__ == "__main__":
    main()
