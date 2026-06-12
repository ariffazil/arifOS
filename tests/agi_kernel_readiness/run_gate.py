"""
Runner for AGI Kernel Readiness Gate 001.

Runs all tests across 6 tiers:
    Tier 1: Constitutional Substrate (direct kernel imports)
    Tier 2: Witness Plane (MCP bus, kernel authority tools)
    Tier 3: Cognitive Plane (MCP bus, kernel-gated LLM tools)
    Tier 4: Post-Kernel Bus (MCP bus, LLM-touching tools HOLD/VOID)
    Tier 5: ATOMIC Plane (forge + vault seal, sovereign signature)
    Tier 6: Sovereignty Anchors (PII mask, Adat Agentik, BM surfaces)
    Tier 7: Human Substrate Protection (WELL reflect-only)
    Tier 8: Agency Protection (WEALTH no-extraction)

Reports per-tier pass/fail and an overall honest level readout.
"""

import importlib
import json
import sys
import time
from pathlib import Path


# Tier → test module mapping
TIER_MAP = {
    "Tier 1: Constitutional Substrate": [
        "test_011_floor_registry_ground_truth",
        "test_012_governance_pipeline_direct",
    ],
    "Tier 2: Witness Plane (Bus authority tools)": [
        "test_000_discover_pre_session",
        "test_001_light_bootstrap_returns_session",
        "test_002_full_init_bound_session",
        "test_003_surface_rsi_canonical13",
    ],
    "Tier 3: Cognitive Plane (Bus cognitive tools)": [
        "test_005_reasoning_structured_output",
        "test_006_judge_refuses_self_certification",
    ],
    "Tier 4: Post-Kernel Bus (LLM-touching tools HOLD/VOID)": [
        "test_004_actor_identity_no_drift",
    ],
    "Tier 5: ATOMIC Plane (Sovereign signature)": [
        "test_007_dangerous_modes_blocked",
        "test_008_memory_write_requires_ack",
        "test_009_forge_commit_requires_888",
        "test_010_consecutive_boots",
        "test_014_atomic_plane_sovereign_signature",
    ],
    "Tier 6: Sovereignty Anchors": [
        # Reserved — will be populated when tier-6 tests are added
    ],
    "Tier 7: Human Substrate Protection": [
        "test_015_human_substrate_protection",
    ],
    "Tier 8: Agency Protection": [
        "test_016_agency_protection",
    ],
}


def run_one(module_name: str) -> dict:
    """Run a single test module. Returns result dict."""
    started = time.time()
    result = {
        "module": module_name,
        "passed": False,
        "duration_s": 0.0,
        "error": None,
        "tests_run": 0,
    }
    try:
        mod = importlib.import_module(f"tests.agi_kernel_readiness.{module_name}")
        test_funcs = [
            (name, getattr(mod, name))
            for name in dir(mod)
            if name.startswith("test_") and callable(getattr(mod, name))
        ]
        result["tests_run"] = len(test_funcs)
        for name, fn in test_funcs:
            try:
                fn()
            except AssertionError as e:
                result["error"] = f"{name}: {str(e)[:200]}"
                return result
            except Exception as e:
                result["error"] = f"{name}: {type(e).__name__}: {str(e)[:200]}"
                return result
        result["passed"] = True
    except Exception as e:
        result["error"] = f"module load: {type(e).__name__}: {str(e)[:200]}"
    result["duration_s"] = round(time.time() - started, 2)
    return result


def compute_tier_level(tier_name: str, tier_results: list) -> str:
    """Compute honest level for a tier based on which tests passed."""
    n_pass = sum(1 for r in tier_results if r["passed"])
    n_total = len(tier_results)
    if n_total == 0:
        return "—"
    pct = n_pass / n_total
    if pct >= 0.9:
        return f"PASS ({n_pass}/{n_total})"
    elif pct >= 0.6:
        return f"PARTIAL ({n_pass}/{n_total})"
    elif pct >= 0.3:
        return f"WEAK ({n_pass}/{n_total})"
    else:
        return f"FAIL ({n_pass}/{n_total})"


def compute_overall_level(tier_results: dict) -> str:
    """Compute the overall honest level for the gate.

    The level reflects *constitutional substrate intact* (Tier 1+)
    combined with *anti-dependency guarantees* (Tier 7+8). Tier 2-5
    are the bus mediation tiers; the level doesn't gate on them
    because the bus can fail without losing sovereignty.
    """
    tier_order = [
        "Tier 1: Constitutional Substrate",
        "Tier 2: Witness Plane (Bus authority tools)",
        "Tier 3: Cognitive Plane (Bus cognitive tools)",
        "Tier 4: Post-Kernel Bus (LLM-touching tools HOLD/VOID)",
        "Tier 5: ATOMIC Plane (Sovereign signature)",
        "Tier 6: Sovereignty Anchors",
        "Tier 7: Human Substrate Protection",
        "Tier 8: Agency Protection",
    ]

    t1 = compute_tier_level(tier_order[0], tier_results.get(tier_order[0], []))
    t2 = compute_tier_level(tier_order[1], tier_results.get(tier_order[1], []))
    t3 = compute_tier_level(tier_order[2], tier_results.get(tier_order[2], []))
    t4 = compute_tier_level(tier_order[3], tier_results.get(tier_order[3], []))
    t5 = compute_tier_level(tier_order[4], tier_results.get(tier_order[4], []))
    t7 = compute_tier_level(tier_order[6], tier_results.get(tier_order[6], []))
    t8 = compute_tier_level(tier_order[7], tier_results.get(tier_order[7], []))

    # Level 0.5: runtime alive (kernel status works at all)
    if t1 == "—" and t2 == "—":
        return "0.0 — unknown"

    # Level 1: constitutional kernel stable (substrate + witness plane)
    if t1.startswith("PASS") and t2.startswith("PASS"):
        # Level 1.5: bus mediation works
        if t5.startswith("PASS") and t3.startswith("PASS"):
            # Level 2: cognitive plane also works
            if t4.startswith("PASS") and t7.startswith("PASS") and t8.startswith("PASS"):
                return "2.0 — full governed session stable; anti-dependency guarantees in place (WELL reflect-only, WEALTH recommendation-only)"
            return (
                "1.5 — kernel substrate + bus + ATOMIC sovereign signature; anti-dependency partial"
            )
        return "1.0 — constitutional kernel stable (substrate + witness plane)"

    # Level 1.0: light-bootstrap constitutional MCP kernel
    if t1.startswith("PASS") or t2.startswith("PARTIAL"):
        return "1.0 — light-bootstrap constitutional MCP kernel (substrate intact, bus partial)"

    # Below 1.0
    return f"0.5 — substrate unstable (T1={t1}, T2={t2})"


def main() -> int:
    print("=" * 70)
    print("AGI_KERNEL_READINESS_GATE_001 — RUNNER (6-TIER + SOVEREIGNTY)")
    print("=" * 70)
    print()

    tier_results = {}
    all_results = []

    for tier_name, modules in TIER_MAP.items():
        if not modules:
            print(f"--- {tier_name} ---")
            print("  (no tests yet)")
            print()
            tier_results[tier_name] = []
            continue
        print(f"--- {tier_name} ---")
        tier_results[tier_name] = []
        for mod in modules:
            r = run_one(mod)
            tier_results[tier_name].append(r)
            all_results.append(r)
            status = "PASS" if r["passed"] else "FAIL"
            print(f"  [{status}] {mod} ({r['duration_s']}s, {r['tests_run']} tests)")
            if r["error"]:
                err = r["error"]
                if len(err) > 200:
                    err = err[:200] + "..."
                print(f"    err: {err}")
        print()

    # Per-tier summary
    print("=" * 70)
    print("PER-TIER HONEST LEVEL")
    print("=" * 70)
    for tier_name in TIER_MAP:
        tier_r = tier_results.get(tier_name, [])
        level = compute_tier_level(tier_name, tier_r)
        print(f"  {tier_name}: {level}")
    print()

    # Overall summary
    n_pass_modules = sum(1 for r in all_results if r["passed"])
    n_total_modules = len(all_results)
    n_pass_tests = sum(r["tests_run"] for r in all_results if r["passed"])
    n_total_tests = sum(r["tests_run"] for r in all_results)
    total_duration = sum(r["duration_s"] for r in all_results)

    overall = compute_overall_level(tier_results)

    print("=" * 70)
    print(
        f"GATE RESULT: {n_pass_modules}/{n_total_modules} modules pass, "
        f"{n_pass_tests}/{n_total_tests} tests pass, {total_duration}s elapsed"
    )
    print(f"HONEST CURRENT LEVEL: {overall}")
    print("=" * 70)

    # Persist run results
    out_path = Path("/root/VAULT999/agi_gate_001_results.json")
    out_path.write_text(
        json.dumps(
            {
                "gate_id": "AGI_KERNEL_READINESS_GATE_001",
                "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "modules_passed": n_pass_modules,
                "modules_failed": n_total_modules - n_pass_modules,
                "total_modules": n_total_modules,
                "tests_passed": n_pass_tests,
                "total_tests": n_total_tests,
                "honest_current_level": overall,
                "tier_results": {
                    t: {
                        "level": compute_tier_level(t, tier_results[t]),
                        "modules": [
                            {
                                "name": r["module"],
                                "passed": r["passed"],
                                "tests_run": r["tests_run"],
                            }
                            for r in tier_results[t]
                        ],
                    }
                    for t in TIER_MAP
                },
                "all_results": all_results,
            },
            indent=2,
        )
    )
    print(f"\nResults written to: {out_path}")
    return 0 if (n_total_modules - n_pass_modules) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
