import asyncio
import os
import sys

# Ensure we can import core modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from arifosmcp.intelligence.tools.system_monitor import get_system_health
from core.shared.floors import F2_Truth, F6_Empathy


async def verify_f2():
    print("--- Verifying F2 Truth (Axiomatic Bypass) ---")
    f2 = F2_Truth()

    # 1. Axiomatic Query (Math)
    ctx_math = {"query": "Calculate 2+2", "entropy_delta": -0.1, "energy_efficiency": 0.5}
    res_math = f2.check(ctx_math)
    print(f"Math Query (2+2): {res_math.passed} (Score: {res_math.score}) - {res_math.reason}")
    if res_math.score != 1.0:
        print("FAIL: Math query should have score 1.0 (Axiomatic Bypass)")

    # 2. Standard Fact (Low Energy)
    ctx_fact = {
        "query": "What is the capital of France?",
        "entropy_delta": -0.1,
        "energy_efficiency": 0.1,
        "truth_score": 0.995,
    }
    res_fact = f2.check(ctx_fact)
    print(f"Fact Query (Capital): {res_fact.passed} (Score: {res_fact.score}) - {res_fact.reason}")


async def verify_f6():
    print("\n--- Verifying F6 Empathy (Scope Awareness) ---")
    f6 = F6_Empathy()

    # 1. Social Scope (Strict)
    ctx_social = {"scope": "social", "empathy_kappa_r": 0.5}
    res_social = f6.check(ctx_social)
    print(
        f"Social Scope (0.5): {res_social.passed} (Score: {res_social.score}) - {res_social.reason}"
    )
    if res_social.passed:
        print("FAIL: Social scope with 0.5 should FAIL (Threshold 0.95)")

    # 2. Ops Scope (Relaxed)
    ctx_ops = {"scope": "ops", "empathy_kappa_r": 0.5}
    res_ops = f6.check(ctx_ops)
    print(
        f"Ops Scope (0.5): {res_ops.passed} (Score: {res_social.score} -> {res_ops.score}) - {res_ops.reason}"
    )
    if not res_ops.passed:
        print("FAIL: Ops scope with 0.5 should PASS (Threshold 0.10)")


def verify_system_monitor():
    print("\n--- Verifying System Monitor (OS Agnostic) ---")
    try:
        health = get_system_health()
        print(f"Health Status: {health.get('status')}")
        print(f"Platform: {health.get('resources', {}).get('platform')}")
        # Check if verify keys exist
        if "cpu" in health.get("resources", {}):
            print("CPU Metrics: OK")
        else:
            print("FAIL: No CPU metrics")
    except Exception as e:
        print(f"FAIL: System Monitor threw exception: {e}")


async def main():
    await verify_f2()
    await verify_f6()
    verify_system_monitor()


if __name__ == "__main__":
    asyncio.run(main())
