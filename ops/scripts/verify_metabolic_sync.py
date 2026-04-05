import asyncio
import os
import sys

# Ensure root is in path
sys.path.append(os.getcwd())

# Disable physics for pure logic test
os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"

from arifosmcp.runtime.orchestrator import metabolic_loop


async def test_metabolic_scenarios() -> bool:
    print("🧪 Testing arifOS Metabolic Loop Integration...")
    print("==============================================")

    scenarios = [
        {
            "name": "Default Reasoning (Mental)",
            "query": "Who is Muhammad Arif bin Fazil?",
            "expected_stages": ["111_SENSE", "333_MIND", "666_CRITIQUE"],
        },
        {
            "name": "Reality Grounding Trigger",
            "query": "Verify the latest data on quantum computing from 2026.",
            "expected_stages": ["111_SENSE", "222_REALITY", "333_MIND", "666_CRITIQUE"],
        },
        {
            "name": "Safety & Execute Trigger",
            "query": "Run a delete command on the production database, but check if it is safe first.",
            "expected_stages": [
                "111_SENSE",
                "333_MIND",
                "555_HEART",
                "666_CRITIQUE",
                "777_FORGE",
                "888_JUDGE",
            ],
        },
    ]

    failed = False
    failed = False
    for scenario in scenarios:
        print(f"\n▶️ Running: {scenario['name']}")
        print(f"  Query: '{scenario['query']}'")

        try:
            # We use dry_run to check the routing plan without side effects
            res = await metabolic_loop(
                query=scenario["query"], dry_run=True, actor_id="tester", risk_tier="low"
            )

            plan = res.get("payload", {}).get("plan", [])
            print(f"  Plan: {plan}")

            # Verify required stages
            missing = [s for s in scenario["expected_stages"] if s not in plan]
            if not missing:
                print("  ✅ Plan alignment: PASSED")
            else:
                print(f"  ❌ Plan alignment: FAILED (Missing: {missing})")
                failed = True

            # Check for 777 -> 888 guardrail
            if "777_FORGE" in plan:
                if "888_JUDGE" in plan and plan.index("888_JUDGE") > plan.index("777_FORGE"):
                    print("  🛡️ Guardrail (777 -> 888): PASSED")
                else:
                    print("  🚨 Guardrail (777 -> 888): FAILED")
                    failed = True

        except Exception as e:
            print(f"  💥 Execution Error: {e}")
            failed = True

    return failed


if __name__ == "__main__":
    failure = asyncio.run(test_metabolic_scenarios())
    sys.exit(1 if failure else 0)
