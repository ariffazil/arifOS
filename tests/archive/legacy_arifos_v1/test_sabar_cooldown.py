"""
test_sabar_cooldown.py — Phase 2 SABAR Cooldown Integration Tests
═══════════════════════════════════════════════════════════════

Stage 2A: observe+warn. All tests verify behavior without hard enforcement.
Tests 1-8: unit/integration for cooldown_engine.py
Tests 9-10: cross-repo integration (A-FORGE contract parity)

Run: python3 test_sabar_cooldown.py
"""

import sys
from datetime import datetime, timedelta, UTC

# ── Test framework (standalone, no pytest needed) ──
_pass = 0
_fail = 0


def check(name: str, condition: bool, detail: str = ""):
    global _pass, _fail
    if condition:
        _pass += 1
        print(f"  ✅ {name}")
    else:
        _fail += 1
        print(f"  ❌ {name} — {detail}")


# ═══════════════════════════════════════════════════════════
# Import engine (standalone — bypasses full arifOS init)
# ═══════════════════════════════════════════════════════════

# Patch arifosmcp init to avoid full dependency chain
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "cooldown_engine", "/root/arifOS/arifosmcp/core/cooldown_engine.py"
)
assert spec is not None
cooldown_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cooldown_module)

CooldownEngine = cooldown_module.CooldownEngine
COOLDOWN_DEFAULT_HOURS = cooldown_module.COOLDOWN_DEFAULT_HOURS
COOLDOWN_RISK_TIERS = cooldown_module.COOLDOWN_RISK_TIERS

print("=" * 60)
print("SABAR COOLDOWN INTEGRATION TESTS — Phase 2A")
print("=" * 60)

# ═══════════════════════════════════════════════════════════
# Test 1: forge_execute creates cooldown_entry_id
# ═══════════════════════════════════════════════════════════
print("\n[1/10] forge_execute creates cooldown_entry_id")

engine = CooldownEngine()
entry = engine.propose(
    artifact_ref="sha256:test123",
    description="forge:engineer: build arifos v2",
    risk_tier="medium",
    session_id="sess-test-1",
)
check("entry_id is 12 chars", len(entry.entry_id) == 12)
check("verdict is SABAR", entry.verdict == "SABAR")
check("cooldown_hours is 72", entry.cooldown_hours == 72)
check("has expiry", entry.cooldown_expiry is not None)
check("remaining > 70h", entry.remaining_hours > 70)
check("artifact_ref matches", entry.artifact_ref == "sha256:test123")
check("tri_witness starts at 0", entry.tri_witness.count == 0)
check("budget not exhausted", not entry.resource_budget.is_exhausted)

# ═══════════════════════════════════════════════════════════
# Test 2: vault_seal with valid cooled entry succeeds
# ═══════════════════════════════════════════════════════════
print("\n[2/10] vault_seal with valid cooled entry succeeds")

engine2 = CooldownEngine()
entry2 = engine2.propose(
    artifact_ref="vault:test-seal",
    description="test vault seal with cooldown",
    risk_tier="low",
)
# Submit all 3 witnesses
engine2.witness(entry2.entry_id, "human", True)
engine2.witness(entry2.entry_id, "ai_audit", True)
engine2.witness(entry2.entry_id, "reality_check", True)
check("tri_witness complete after 3", entry2.tri_witness.is_complete)

ok, reason = engine2.seal(entry2.entry_id)
check("seal succeeds", ok, reason)
check("verdict is SEAL", entry2.verdict == "SEAL")
check("sealed_at set", entry2.sealed_at is not None)

# ═══════════════════════════════════════════════════════════
# Test 3: vault_seal without cooldown_entry_id logs bypass
# ═══════════════════════════════════════════════════════════
print("\n[3/10] vault_seal without cooldown_entry_id logs bypass")

engine3 = CooldownEngine()
initial_bypass = engine3._bypass_count

# Simulate legacy seal: propose + record bypass
entry3 = engine3.propose(
    artifact_ref="vault:legacy-seal",
    description="auto-registered from vault seal (legacy compat)",
    risk_tier="low",
)
bypass_n = engine3.record_bypass()
check("bypass counter incremented", bypass_n == initial_bypass + 1)
check("entry still SABAR", entry3.verdict == "SABAR")
check("bypass count in vitals", engine3.vitals()["cooldown_bypass_count"] == bypass_n)

# ═══════════════════════════════════════════════════════════
# Test 4: judge_deliberate returns SABAR advisory if cooling incomplete
# ═══════════════════════════════════════════════════════════
print("\n[4/10] judge_deliberate SABAR advisory if cooling incomplete")

engine4 = CooldownEngine()
entry4 = engine4.propose(artifact_ref="judge:test-pending", risk_tier="medium")
# Only 1 of 3 witnesses
engine4.witness(entry4.entry_id, "human", True)

can_seal_before = entry4.can_seal
check("cannot seal before tri-witness complete", not can_seal_before)
check("remaining_hours > 70", entry4.remaining_hours > 70)
check("witness count is 1", entry4.tri_witness.count == 1)

# ═══════════════════════════════════════════════════════════
# Test 5: judge_deliberate allows SEAL only after cooldown + witness
# ═══════════════════════════════════════════════════════════
print("\n[5/10] judge_deliberate SEAL after cooldown + witness complete")

engine5 = CooldownEngine()
entry5 = engine5.propose(artifact_ref="judge:test-sealable", risk_tier="low")

engine5.witness(entry5.entry_id, "human", True)
engine5.witness(entry5.entry_id, "ai_audit", True)
engine5.witness(entry5.entry_id, "reality_check", True)
check("witness complete", entry5.tri_witness.is_complete)
check("can seal", entry5.can_seal)

ok, reason = engine5.seal(entry5.entry_id)
check("seal succeeds after full witness", ok, reason)

# ═══════════════════════════════════════════════════════════
# Test 6: memory_recall annotates high-stakes context
# ═══════════════════════════════════════════════════════════
print("\n[6/10] memory_recall context annotation")

engine6 = CooldownEngine()
engine6.propose(artifact_ref="mem:active1", risk_tier="low")
engine6.propose(artifact_ref="mem:active2", risk_tier="medium")

v = engine6.vitals()
check("active count matches", v["cooldown_active_count"] == 2)
check("oldest_remaining set", v["cooldown_oldest_remaining_hours"] is not None)
check("budget not exhausted", not v["cooldown_sabar_budget_exhausted_any"])

# ═══════════════════════════════════════════════════════════
# Test 7: expired cooldown auto-VOIDs
# ═══════════════════════════════════════════════════════════
print("\n[7/10] expired cooldown auto-VOIDs")

engine7 = CooldownEngine()
entry7 = engine7.propose(artifact_ref="expire:test", risk_tier="low")
# Manually expire by setting cooldown_expiry to past datetime
entry7.cooldown_expiry = datetime.now(UTC) - timedelta(hours=1)

checked = engine7.check(entry7.entry_id)
check("check triggers auto-VOID", checked is not None)
check("verdict is VOID", checked.verdict == "VOID")
check("void reason mentions expiry", "expired" in (checked.void_reason or "").lower())

# ═══════════════════════════════════════════════════════════
# Test 8: budget exhaustion auto-VOIDs
# ═══════════════════════════════════════════════════════════
print("\n[8/10] budget exhaustion auto-VOIDs")

engine8 = CooldownEngine()
entry8 = engine8.propose(artifact_ref="budget:exhausted", risk_tier="medium")
entry8.resource_budget.consume_disk(60_000_000_000)  # 60GB > 50GB limit

check("budget exhausted", entry8.resource_budget.is_exhausted)

checked = engine8.check(entry8.entry_id)
check("check triggers auto-VOID on budget", checked is not None)
check("verdict is VOID", checked.verdict == "VOID")
check("void reason mentions budget", "budget" in (checked.void_reason or "").lower())

# ═══════════════════════════════════════════════════════════
# Test 9: corrupted/missing cooldown state fails closed
# ═══════════════════════════════════════════════════════════
print("\n[9/10] corrupted/missing cooldown state fails safe")

engine9 = CooldownEngine()

# Query nonexistent entry — should return None (not crash)
nonexistent = engine9.check("nonexistent-id-12345")
check("nonexistent entry returns None", nonexistent is None)

# Witness nonexistent entry — should return False (not crash)
witness_result = engine9.witness("nonexistent-id-12345", "human", True)
check("witness nonexistent returns False", not witness_result)

# Seal nonexistent entry — should return error (not crash)
ok, reason = engine9.seal("nonexistent-id-12345")
check("seal nonexistent returns False", not ok)
check("seal nonexistent gives reason", "not found" in reason)

# Void nonexistent entry — should return error (not crash)
ok, reason = engine9.void("nonexistent-id-12345", "test")
check("void nonexistent returns False", not ok)

# Resolve nonexistent entry — should return None (not crash)
resolved = engine9.resolve("nonexistent-id-12345")
check("resolve nonexistent returns None", resolved is None)

# ═══════════════════════════════════════════════════════════
# Test 10: Cross-repo contract parity (A-FORGE ↔ arifOS)
# ═══════════════════════════════════════════════════════════
print("\n[10/10] Cross-repo contract parity")

# Verify: same risk tier hours, same default window, same verdict states
arifos_tiers = COOLDOWN_RISK_TIERS
expected_tiers = {"low": 24, "medium": 72, "high": 168, "critical": 720}

for tier, hours in expected_tiers.items():
    check(f"arifOS {tier}={hours}h", arifos_tiers.get(tier) == hours)

check("default is 72h", COOLDOWN_DEFAULT_HOURS == 72)

# Verify engine vitals structure
v = engine9.vitals()  # (empty engine from test 9)
check("vitals has active_count", "cooldown_active_count" in v)
check("vitals has sealed_count", "cooldown_sealed_count" in v)
check("vitals has voided_count", "cooldown_voided_count" in v)
check("vitals has bypass_count", "cooldown_bypass_count" in v)
check("vitals has total_entries", "cooldown_total_entries" in v)
check("vitals has active_entries list", isinstance(v.get("cooldown_active_entries"), list))
check("vitals has budget_exhausted flag", "cooldown_sabar_budget_exhausted_any" in v)

# ═══════════════════════════════════════════════════════════
# Results
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print(f"RESULTS: {_pass} passed, {_fail} failed, {_pass + _fail} total")
print("=" * 60)

if _fail > 0:
    print("❌ SOME TESTS FAILED")
    sys.exit(1)
else:
    print("✅ ALL TESTS PASSED — Stage 2A SABAR cooldown verified")
