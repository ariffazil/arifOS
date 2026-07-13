"""Test D1 + D2 — full integration test through arifOS package."""
import sys, tempfile, shutil, time
sys.path.insert(0, "/opt/arifos/app")

from arifosmcp.schemas.action_profile import (
    ActionProfile, MutationClass, Reversibility, BlastRadius,
    GovernanceImpact, InfrastructureImpact, ReceiptClass,
    RequiredCapability, classify_action, upgrade_to_sovereign,
    upgrade_to_session_closure, TOOL_CLASSIFICATION_MAP,
)

from arifosmcp.schemas.vault_outbox import (
    VaultOutbox, VaultOutboxEntry, OutboxStatus, ReceiptClass as ORC,
    SessionClosureState, SessionClosure, VaultOutboxConsumer,
)

from arifosmcp.schemas.dependency_gate import (
    GateContext, GateStatus, GateResult, run_pipeline, PIPELINE_GATES,
)

from arifosmcp.schemas.session_closure import (
    SessionClosureManager, SessionManifest, ServiceSigner,
    determine_closure_level,
)

from datetime import UTC, datetime

print("="*60)
print("D1: ACTION PROFILE")
print("="*60)

p = classify_action("arif_seal", "seal")
assert p.tool == "arif_seal"
assert p.mutation_class == MutationClass.APPEND_ONLY
assert p.reversibility == Reversibility.IRREVERSIBLE
assert p.blast_radius == BlastRadius.DATASET
assert p.governance_impact == GovernanceImpact.CONSTITUTIONAL
assert p.requires_human_ack is True
print(f"  ✅ seal: {p.tool}/{p.verb} → {p.mutation_class.value} | {p.reversibility.value} | {p.blast_radius.value}")

p2 = classify_action("arif_observe", "search")
assert p2.mutation_class == MutationClass.NONE
assert p2.blast_radius == BlastRadius.NONE
print(f"  ✅ observe/search: {p2.mutation_class.value} | {p2.blast_radius.value}")

p3 = classify_action("arif_forge", "engineer")
assert p3.mutation_class == MutationClass.MUTATE
assert p3.receipt_class == ReceiptClass.ROUTINE
print(f"  ✅ forge/engineer: {p3.mutation_class.value} | receipt={p3.receipt_class.value}")

p4 = upgrade_to_sovereign(p)
assert p4.receipt_class == ReceiptClass.SOVEREIGN_DECISION
assert p4.required_capability == RequiredCapability.VAULT_APPEND_SOVEREIGN
print(f"  ✅ sovereign upgrade: receipt={p4.receipt_class.value}")

p5 = classify_action("nonexistent", "blah")
assert p5.mutation_class == MutationClass.UNKNOWN
print(f"  ✅ unknown tool: UNKNOWN")

p6 = classify_action("infra", "*")
assert p6.sovereign_required is True
assert p6.infrastructure_impact == InfrastructureImpact.HARDWARE
print(f"  ✅ infra: sovereign={p6.sovereign_required}")

print()
print("="*60)
print("D2: VAULT OUTBOX")
print("="*60)

tmpdir = tempfile.mkdtemp(prefix="vo_")
try:
    outbox = VaultOutbox(tmpdir)
    e1 = outbox.enqueue("sess-1", ORC.SESSION_CLOSED, "hash_abc", "vault.append.session_closure")
    assert e1.status == OutboxStatus.PENDING
    assert e1.outbox_hash
    print(f"  ✅ enqueue: {e1.event_id[:8]}... status={e1.status.value}")

    # Idempotency
    e2 = outbox.enqueue("sess-1", ORC.SESSION_CLOSED, "hash_abc", "vault.append.session_closure",
                        idempotency_key=e1.idempotency_key)
    assert e2.event_id == e1.event_id
    print(f"  ✅ idempotency: same entry")

    # Claim → Append → Verify
    claimed = outbox.claim_next("tester")
    assert claimed is not None and claimed.status == OutboxStatus.CLAIMED
    outbox.mark_appended(claimed.event_id, "seal_123", "receipt_hash_xyz")
    outbox.mark_verified(claimed.event_id, "chain_head_abc")
    assert len(outbox.get_by_status(OutboxStatus.VERIFIED)) == 1
    assert len(outbox.get_by_session("sess-1")) == 1
    print(f"  ✅ claim→append→verify: full cycle")

    # Failure tracking
    e3 = outbox.enqueue("sess-2", ORC.SESSION_SOVEREIGN_SEALED, "hash_def", "vault.append.sovereign")
    outbox.mark_failed(e3.event_id, "timeout")
    assert len(outbox.get_by_status(OutboxStatus.FAILED_RETRYABLE)) == 1
    outbox.mark_failed(e3.event_id, "again")
    outbox.mark_failed(e3.event_id, "final")
    assert len(outbox.get_by_status(OutboxStatus.HOLD)) == 1
    print(f"  ✅ failure tracking: PENDING→FAILED_RETRYABLE→HOLD")

    # SessionClosure dataclass
    sc = SessionClosure(session_id="sess-1", closure_state=SessionClosureState.CLOSING,
                        receipt_class=ORC.SESSION_CLOSED)
    assert sc.to_dict()["session_id"] == "sess-1"
    print(f"  ✅ SessionClosure: state={sc.closure_state.value}")

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print()
print("="*60)
print("D1: DEPENDENCY GATE PIPELINE")
print("="*60)

# Test 1: SOVEREIGN full seal → SEAL
ctx1 = GateContext(raw_request="seal", target_tool="arif_seal", target_verb="seal",
                   actor_id="arif", actor_verified=True,
                   session_id="t1", identity_band="SOVEREIGN",
                   capability_grants=["vault.append.session_closure"],
                   infra_green=True,
                   closure_state=SessionClosureState.CLOSED_PENDING_RECEIPT,
                   payload_hash="abc123deadbeef")
r1 = run_pipeline(ctx1)
assert r1.verdict == "SEAL", f"Expected SEAL got {r1.verdict}: {r1.to_dict()}"
assert r1.all_pass
print(f"  ✅ SOVEREIGN SEAL: {r1.verdict} — all {len(ctx1.gate_results)} gates PASS")
print(f"     Profile: {ctx1.action_profile.tool}/{ctx1.action_profile.verb} "
      f"→ {ctx1.action_profile.receipt_class.value}")

# Test 2: OBSERVER → HOLD at G3_IDENTITY
ctx2 = GateContext(raw_request="write", target_tool="arif_forge", target_verb="engineer",
                   actor_id="", session_id="t2",
                   identity_band="OBSERVER", capability_grants=[], infra_green=True)
r2 = run_pipeline(ctx2)
assert r2.verdict in ("HOLD", "DENY"), f"Expected block got {r2.verdict}"
print(f"  ✅ OBSERVER blocked: {r2.verdict} at {r2.first_failure.gate_name if r2.first_failure else '?'}")

# Test 3: Missing capability → DENY at G4
ctx3 = GateContext(raw_request="seal", target_tool="arif_seal", target_verb="seal",
                   actor_id="bot", actor_verified=True, session_id="t3",
                   identity_band="OPERATOR_SIGNED",
                   capability_grants=["observe.search"], infra_green=True,
                   payload_hash="abc", closure_state=SessionClosureState.CLOSED_PENDING_RECEIPT)
r3 = run_pipeline(ctx3)
assert r3.verdict in ("HOLD", "DENY")
print(f"  ✅ missing capability blocked: {r3.verdict} at {r3.first_failure.gate_name if r3.first_failure else '?'}")

# Test 4: Runtime drift → HOLD at G5
ctx4 = GateContext(raw_request="restart", target_tool="infra", target_verb="*",
                   actor_id="arif", actor_verified=True, session_id="t4",
                   identity_band="SOVEREIGN",
                   capability_grants=["infra.hardware"], infra_green=True,
                   runtime_drift=True, payload_hash="abc")
r4 = run_pipeline(ctx4)
assert r4.verdict in ("HOLD", "DENY")
print(f"  ✅ runtime drift blocked: {r4.verdict} at {r4.first_failure.gate_name if r4.first_failure else '?'}")

print()
print("="*60)
print("D2: SESSION CLOSURE")
print("="*60)

# Determine closure levels
rc, cs = determine_closure_level(SessionManifest(session_id="s", actor_id="a", identity_band="OBSERVER",
                                                  started_at=datetime.now(UTC).isoformat()),
                                 has_sovereign_seal=True, has_governance_action=True)
assert rc == ORC.SESSION_SOVEREIGN_SEALED
print(f"  ✅ SOVEREIGN closure: {rc.value}")

rc2, cs2 = determine_closure_level(SessionManifest(session_id="s", actor_id="a", identity_band="OBSERVER",
                                                    started_at=datetime.now(UTC).isoformat()),
                                   has_sovereign_seal=False, has_governance_action=True)
assert rc2 == ORC.SESSION_CLOSED
print(f"  ✅ CLOSED closure: {rc2.value}")

rc3, cs3 = determine_closure_level(SessionManifest(session_id="s", actor_id="a", identity_band="OBSERVER",
                                                    started_at=datetime.now(UTC).isoformat()),
                                   has_sovereign_seal=False, has_governance_action=False)
assert rc3 == ORC.SESSION_OBSERVED
print(f"  ✅ OBSERVED closure: {rc3.value}")

# Full session closure lifecycle
tmpdir2 = tempfile.mkdtemp(prefix="sc_")
try:
    manager = SessionClosureManager(outbox=VaultOutbox(tmpdir2))
    
    # Step 1: Initiate
    closure = manager.initiate_closure("sess-5", "SOVEREIGN", "arif",
                                       has_sovereign_seal=True, has_governance_action=True)
    assert closure.receipt_class == ORC.SESSION_SOVEREIGN_SEALED
    assert closure.closure_state == SessionClosureState.CLOSING
    print(f"  ✅ 1. Initiate: {closure.receipt_class.value} state={closure.closure_state.value}")
    
    # Step 2: Freeze manifest
    manifest = SessionManifest(session_id="sess-5", actor_id="arif", identity_band="SOVEREIGN",
                               started_at=datetime.now(UTC).isoformat(),
                               tool_calls=7, unique_tools=["init", "judge", "seal"],
                               judge_verdicts=["SEAL", "SEAL"])
    mhash = manager.freeze_manifest(manifest)
    assert mhash == manifest.manifest_hash
    assert manifest.duration_seconds >= 0  # no longer crashes on datetime comparison
    print(f"  ✅ 2. Freeze: hash={mhash[:16]}... duration={manifest.duration_seconds:.1f}s")
    
    # Step 3: Write Supabase (skip — no writer)
    manager.write_supabase()
    
    # Step 4: Enqueue outbox
    entry = manager.enqueue_outbox()
    assert entry is not None
    assert entry.receipt_class == ORC.SESSION_SOVEREIGN_SEALED
    assert closure.closure_state == SessionClosureState.CLOSED_PENDING_RECEIPT
    print(f"  ✅ 3. Outbox: {entry.event_id[:8]}... status=PENDING")
    
    # Step 5: Finalise (close operational authority IMMEDIATELY)
    final = manager.finalise()
    assert final.session_closed_at
    print(f"  ✅ 4. Finalise: operational authority closed at {final.session_closed_at}")
    
    # Step 6: Mark sealed (called by outbox consumer)
    sealed = manager.mark_sealed("vault_seal_789", "receipt_hash_abc", "chain_head_def")
    assert sealed.closure_state == SessionClosureState.CLOSED_SEALED
    assert sealed.outbox_appended
    assert sealed.chain_head_verified
    print(f"  ✅ 5. Sealed: CLOSED_SEALED vault={sealed.outbox_event_id[:8]}...")

    # Verify OBSERVED session skips VAULT
    manager2 = SessionClosureManager(outbox=VaultOutbox(tmpdir2))
    closure2 = manager2.initiate_closure("sess-6", "OBSERVER", "anon",
                                         has_sovereign_seal=False, has_governance_action=False)
    manifest2 = SessionManifest(session_id="sess-6", actor_id="anon", identity_band="OBSERVER",
                                started_at=datetime.now(UTC).isoformat())
    manager2.freeze_manifest(manifest2)
    entry2 = manager2.enqueue_outbox()
    assert entry2 is None  # OBSERVED → no outbox entry
    final2 = manager2.finalise()
    assert final2.closure_state == SessionClosureState.CLOSED_UNSEALED
    print(f"  ✅ 6. OBSERVED skips VAULT: CLOSED_UNSEALED (no outbox)")

finally:
    shutil.rmtree(tmpdir2, ignore_errors=True)

print()
print("="*60)
print("🔥 ALL D1 + D2 TESTS PASSED")
print("  D1: action_profile + dependency_gate — forged")
print("  D2: vault_outbox + session_closure — forged")
print("DITEMPA BUKAN DIBERI 🔥⚒️")
print("="*60)
