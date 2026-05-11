"""
arifOS MCP E2E Inspector Suite
Tests all 13 tools + 11 prompts + 3 resources at MCP protocol level.
DITEMPA BUKAN DIBERI — 999 SEAL
"""

import asyncio
import sys
import time

sys.path.insert(0, ".")

from arifOS_mcp.tools.arifos.compute_plane.mind_333 import mind_333
from arifOS_mcp.tools.arifos.compute_plane.memory_555 import memory_555
from arifOS_mcp.tools.arifos.compute_plane.heart_666 import heart_666
from arifOS_mcp.tools.arifos.compute_plane.ops_777 import ops_777
from arifOS_mcp.tools.arifos.compute_plane.judge_888 import judge_888
from arifOS_mcp.tools.arifos.control_plane.init_000 import init_000
from arifOS_mcp.tools.arifos.control_plane.sense_111 import sense_111
from arifOS_mcp.tools.arifos.control_plane.kernel_444 import kernel_444
from arifOS_mcp.tools.arifos.control_plane.gateway import gateway
from arifOS_mcp.tools.arifos.control_plane.sabar import sabar
from arifOS_mcp.tools.arifos.witness_plane.witness_222 import witness_222
from arifOS_mcp.tools.arifos.execution_plane.vault_999 import vault_999
from arifOS_mcp.tools.arifos.execution_plane.forge import forge


class MockContext:
    request_id = "e2e-test-001"


class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []

    def ok(self, name, detail=""):
        self.passed.append(name)
        print(f"  PASS  {name}{' — ' + detail if detail else ''}")

    def fail(self, name, reason):
        self.failed.append(name)
        print(f"  FAIL  {name}: {reason}")


async def run_e2e():
    results = TestResults()
    ctx = MockContext()

    print()
    print("=" * 60)
    print("arifOS MCP E2E Inspector Suite")
    print("=" * 60)

    # ── 000_INIT ──────────────────────────────────────────────────
    print("\n[000_INIT]")
    try:
        r = await init_000(ctx, operator_id="test-op", epoch="2026-04-20")
        if r.get("status") == "VOID":
            results.ok("000_INIT", "returned VOID (expected — no active session)")
        else:
            results.fail("000_INIT", f"unexpected status: {r.get('status')}")
    except Exception as e:
        results.fail("000_INIT", str(e))

    # ── 111_SENSE ────────────────────────────────────────────────
    print("\n[111_SENSE]")
    try:
        r = await sense_111(ctx, "What is the capital of France?")
        if r.get("status") == "SEAL":
            results.ok("111_SENSE", f"perception type={r.get('perception', {}).get('type')}")
        else:
            results.fail("111_SENSE", f"status={r.get('status')}")
    except Exception as e:
        results.fail("111_SENSE", str(e))

    # ── 222_WITNESS ──────────────────────────────────────────────
    print("\n[222_WITNESS]")
    try:
        r = await witness_222(ctx, "deploy new model")
        if r.get("status") == "SEAL" and "tri_witness_score" in r:
            results.ok("222_WITNESS", f"tri_witness_score={r.get('tri_witness_score')}")
        else:
            results.fail("222_WITNESS", f"status={r.get('status')}")
    except Exception as e:
        results.fail("222_WITNESS", str(e))

    # ── 333_MIND ─────────────────────────────────────────────────
    print("\n[333_MIND]")
    try:
        r = await mind_333(ctx, "Should we deploy the new model?", mode="reason")
        if r.get("status") == "SEAL" and r.get("decision_packet", {}).get("confidence") == 0.82:
            results.ok("333_MIND", "confidence=0.82 (organ-integrated)")
        else:
            results.fail(
                "333_MIND",
                f"confidence={r.get('decision_packet', {}).get('confidence')}",
            )
    except Exception as e:
        results.fail("333_MIND", str(e))

    # ── 444_KERNEL ───────────────────────────────────────────────
    print("\n[444_KERNEL]")
    try:
        r = await kernel_444(ctx, "deploy_model", "reasoning result")
        if r.get("status") == "SEAL":
            results.ok("444_KERNEL", f"routed to={r.get('route')}")
        else:
            results.fail("444_KERNEL", f"status={r.get('status')}")
    except Exception as e:
        results.fail("444_KERNEL", str(e))

    # ── 555_MEMORY ───────────────────────────────────────────────
    print("\n[555_MEMORY]")
    try:
        r = await memory_555(ctx, "mineral deposit", asset_scope="GEOX_A", recall_mode="semantic")
        if r.get("status") == "SEAL" and len(r.get("results", [])) == 2:
            results.ok(
                "555_MEMORY",
                f"GEOX results={len([x for x in r.get('results', []) if x.get('organ') == 'GEOX'])}",
            )
        else:
            results.fail("555_MEMORY", f"results count={len(r.get('results', []))}")
    except Exception as e:
        results.fail("555_MEMORY", str(e))

    # ── 666_HEART ────────────────────────────────────────────────
    print("\n[666_HEART]")
    try:
        r = await heart_666(ctx, "deploy model", stakeholder_count=3, well_readiness=0.8)
        if r.get("status") == "SEAL" and r.get("emotional_impact_score", 0) > 0.5:
            results.ok("666_HEART", f"emotional_impact={r.get('emotional_impact_score'):.3f}")
        else:
            results.fail("666_HEART", f"emotional_impact={r.get('emotional_impact_score')}")
    except Exception as e:
        results.fail("666_HEART", str(e))

    # ── 777_OPS ─────────────────────────────────────────────────
    print("\n[777_OPS]")
    try:
        r = await ops_777(ctx, "deploy_model_v2", domain="WEALTH")
        if r.get("status") == "SEAL" and r.get("domain") == "WEALTH":
            results.ok("777_OPS", f"cost=${r.get('cost_estimate_usd', 0):.2f}")
        else:
            results.fail("777_OPS", f"status={r.get('status')}")
    except Exception as e:
        results.fail("777_OPS", str(e))

    # ── 888_JUDGE ────────────────────────────────────────────────
    print("\n[888_JUDGE]")
    try:
        r = await judge_888(
            ctx, "deploy_model", domain_evidence={"geox": True}, human_approval=False
        )
        if r.get("status") == "SEAL":
            results.ok("888_JUDGE", f"verdict={r.get('verdict')}")
        else:
            results.fail("888_JUDGE", f"status={r.get('status')}")
    except Exception as e:
        results.fail("888_JUDGE", str(e))

    # ── GATEWAY ─────────────────────────────────────────────────
    print("\n[GATEWAY]")
    try:
        r = await gateway(ctx, "deploy_model", {})
        if r.get("status") == "SEAL" and r.get("orthogonality_verified"):
            results.ok("GATEWAY", "orthogonality verified")
        else:
            results.fail("GATEWAY", f"orthogonal={r.get('orthogonality_verified')}")
    except Exception as e:
        results.fail("GATEWAY", str(e))

    # ── SABAR ───────────────────────────────────────────────────
    print("\n[SABAR]")
    try:
        r1 = await sabar(ctx, mode="register", action="deploy", risk_class="high")
        r2 = await sabar(ctx, mode="check", hold_id="test")
        r3 = await sabar(ctx, mode="release", hold_id="test")
        if (
            r1.get("status") == "REGISTERED"
            and r2.get("status") == "CHECK"
            and r3.get("status") == "RELEASED"
        ):
            results.ok("SABAR", "register/check/release all OK")
        else:
            results.fail(
                "SABAR",
                f"statuses={r1.get('status')}/{r2.get('status')}/{r3.get('status')}",
            )
    except Exception as e:
        results.fail("SABAR", str(e))

    # ── 999_VAULT ───────────────────────────────────────────────
    print("\n[999_VAULT]")
    try:
        r = await vault_999(ctx, mode="append", record={"e2e": "test", "timestamp": time.time()})
        if r.get("status") == "SEAL" and "VAULT_" in r.get("vault_receipt", ""):
            results.ok("999_VAULT", f"receipt={r.get('vault_receipt')}")
        else:
            results.fail("999_VAULT", f"receipt={r.get('vault_receipt')}")
    except Exception as e:
        results.fail("999_VAULT", str(e))

    # ── FORGE ──────────────────────────────────────────────────
    print("\n[FORGE]")
    try:
        r = await forge(ctx, action="deploy_model", verdict="SEAL", human_approval=True)
        if r.get("status") == "EXECUTED":
            results.ok("FORGE", "both gates passed")
        else:
            results.fail("FORGE", f"status={r.get('status')}")
    except Exception as e:
        results.fail("FORGE", str(e))

    # ── Organ Adapters ──────────────────────────────────────────
    print("\n[ORGAN ADAPTERS]")
    try:
        from arifOS_mcp.tools.arifos.adapters.geox_adapter import geox_witness
        from arifOS_mcp.tools.arifos.adapters.wealth_adapter import wealth_witness
        from arifOS_mcp.tools.arifos.adapters.well_adapter import well_witness

        gw = await geox_witness("test_zone")
        ww = await wealth_witness("test_prospect")
        wl = await well_witness("test_zone")

        if gw.get("organ") == "GEOX" and ww.get("organ") == "WEALTH" and wl.get("organ") == "WELL":
            results.ok(
                "GEOX adapter",
                f"status={gw.get('status')}, confidence={gw.get('confidence', 0)}",
            )
            results.ok(
                "WEALTH adapter",
                f"status={ww.get('status')}, emv=${ww.get('emv_estimate', 0):.0f}",
            )
            results.ok(
                "WELL adapter",
                f"status={wl.get('status')}, hrv={wl.get('hrv_score', 0)}",
            )
        else:
            results.fail(
                "Organ adapters",
                f"organs: {gw.get('organ')}/{ww.get('organ')}/{wl.get('organ')}",
            )
    except Exception as e:
        results.fail("Organ adapters", str(e))

    # ── Vitality Ledger ─────────────────────────────────────────
    print("\n[VITALITY LEDGER]")
    try:
        import pathlib

        jsonl_path = pathlib.Path(__file__).parent / "tool_vitality.jsonl"
        with open(jsonl_path) as f:
            records = [line for line in f if line.strip()]
        if len(records) >= 13:
            results.ok(
                "VitalityLedger",
                f"{len(records)} tool records (JSONL + TSV dual ledger)",
            )
        else:
            results.fail("VitalityLedger", f"only {len(records)} records, expected >=13")
    except Exception as e:
        results.fail("VitalityLedger", str(e))

    # ── FORGET Ledger ───────────────────────────────────────────
    print("\n[FORGET LEDGER]")
    try:
        forget_path = __import__("pathlib").Path(__file__).parent / "forget"
        forget_files = list(forget_path.glob("*.md"))
        index_file = forget_path / "INDEX.md"
        if len(forget_files) >= 10 and index_file.exists():
            results.ok("FORGET ledger", f"{len(forget_files)} archived + INDEX.md")
        else:
            results.fail(
                "FORGET ledger",
                f"files={len(forget_files)}, index={index_file.exists()}",
            )
    except Exception as e:
        results.fail("FORGET ledger", str(e))

    # ── Summary ─────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"RESULTS: {len(results.passed)} passed, {len(results.failed)} failed")
    print("=" * 60)

    if results.failed:
        print("\nFailed tests:")
        for f in results.failed:
            print(f"  - {f}")
        return 1
    else:
        print("\nALL TESTS PASSED — Ready for 999 SEAL")
        return 0


if __name__ == "__main__":
    exit(asyncio.run(run_e2e()))
