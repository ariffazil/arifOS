"""
arifos_plan v1.1 — Test Suite
Run: python test_arifos_plan.py

Tests cover:
  T1: propose_plan (LOW risk — auto-approves)
  T2: propose_plan (HIGH risk — triggers 888_HOLD)
  T3: propose_plan with irreversible task (DB migration → 888_HOLD)
  T4: get_plan with receipts
  T5: list_pending with filters
  T6: update_status — sovereign APPROVED (SEAL)
  T7: update_status — sovereign REJECTED (VOID → ABORTED)
  T8: update_status — sovereign HOLD
  T9: abort_plan shortcut
  T10: write_execution_receipt
  T11: gk_can_execute — APPROVED plan, no hold → PASS
  T12: gk_can_execute — PENDING_APPROVAL → BLOCK
  T13: gk_can_execute — ABORTED plan → BLOCK
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from arifos_plan import (
    propose_plan, get_plan, list_pending,
    update_status, abort_plan,
    write_execution_receipt, gk_can_execute,
    _store,
)

def reset():
    """Clear in-memory store between tests."""
    _store.intents.clear()
    _store.plans.clear()
    _store.receipts.clear()
    _store.exec_receipts.clear()

def test(name, cond, got):
    tag = "✅ PASS" if cond else "❌ FAIL"
    print(f"  {tag} {name}: {got}")
    assert cond, f"Expected {cond}, got {got}"

print("\n" + "="*60)
print("arifos_plan v1.1 — Test Suite")
print("="*60)

# ─── T1: LOW-risk plan auto-approves ───────────────────────────────────────
reset()
print("\n[T1] LOW-risk plan → auto-approves (SEAL)")
r = propose_plan(
    intent={"description": "Git pull latest main", "constraints": {}, "floors": {}, "risk_prelude": {}},
    tasks=[{"description": "git pull", "tool": "mcpgit", "mutates_external_state": True,
            "target_surface": "git_repo", "reversible": True, "risk_band": "LOW"}],
    risk_band="LOW", irreversible=False, created_by="test-agent"
)
test("verdict", r["verdict"] == "SEAL", r["verdict"])
test("plan status", r["plan"]["status"] == "APPROVED", r["plan"]["status"])
test("no hold_reason", r.get("hold_reason") is None, r.get("hold_reason"))
test("analysis returned", "analysis" in r, True)
plan_low = r["plan"]["plan_id"]
print(f"  plan_id: {plan_low}")

# ─── T2: HIGH-risk plan triggers 888_HOLD ─────────────────────────────────────
reset()
print("\n[T2] HIGH-risk plan → 888_HOLD (HOLD)")
r = propose_plan(
    intent={"description": "Deploy to staging", "constraints": {}, "floors": {}, "risk_prelude": {}},
    tasks=[{"description": "deploy", "tool": "mcpdeploy", "mutates_external_state": True,
            "target_surface": "k8s-staging", "reversible": False, "risk_band": "HIGH"}],
    risk_band="HIGH", irreversible=False, created_by="test-agent"
)
test("verdict", r["verdict"] == "HOLD", r["verdict"])
test("status PENDING_APPROVAL", r["plan"]["status"] == "PENDING_APPROVAL", r["plan"]["status"])
test("hold_reason set", r.get("hold_reason") is not None, r.get("hold_reason"))
plan_high = r["plan"]["plan_id"]
print(f"  plan_id: {plan_high}")

# ─── T3: Plan with irreversible task triggers 888_HOLD ───────────────────────
reset()
print("\n[T3] Irreversible task (DB DROP) → 888_HOLD")
r = propose_plan(
    intent={"description": "Reset staging DB", "constraints": {}, "floors": {}, "risk_prelude": {}},
    tasks=[
        {"description": "git pull", "tool": "mcpgit", "mutates_external_state": True,
         "target_surface": "git_repo", "reversible": True, "risk_band": "LOW"},
        {"description": "DROP DATABASE staging", "tool": "mcpsql", "mutates_external_state": True,
         "target_surface": "staging_postgres", "reversible": False, "risk_band": "HIGH"},
    ],
    risk_band="MEDIUM", irreversible=True, created_by="test-agent"
)
test("verdict HOLD", r["verdict"] == "HOLD", r["verdict"])
test("task-02 in holds", any(h["task_id"] == r["plan"]["tasks"][1]["task_id"] for h in r["analysis"]["holds"]), True)
plan_db = r["plan"]["plan_id"]
print(f"  plan_id: {plan_db}")

# ─── T4: get_plan returns receipts ───────────────────────────────────────────
reset()
r1 = propose_plan(intent={"description": "test"}, tasks=[], risk_band="LOW", irreversible=False)
update_status(r1["plan"]["plan_id"], "APPROVED", "APPROVED", {"F0": "ok", "F1": "ok"}, "LGTM", "arif-human")
r2 = get_plan(r1["plan"]["plan_id"])
test("get_plan verdict", r2["verdict"] == "SEAL", r2["verdict"])
test("has receipts", len(r2["receipts"]) == 1, len(r2["receipts"]))
test("receipt decision APPROVED", r2["receipts"][0]["decision"] == "APPROVED", r2["receipts"][0]["decision"])
print(f"  receipts: {len(r2['receipts'])}")

# ─── T5: list_pending with filters ─────────────────────────────────────────
reset()
r1 = propose_plan(intent={"description": "test1"}, tasks=[], risk_band="LOW", irreversible=False)
r2 = propose_plan(intent={"description": "test2"}, tasks=[{"description": "x", "tool": "y",
            "mutates_external_state": True, "target_surface": "z", "reversible": False, "risk_band": "HIGH"}],
          risk_band="HIGH", irreversible=False)
pending = list_pending()
test("count >= 1", pending["count"] >= 1, pending["count"])
pending_hi = list_pending(risk_band="HIGH")
test("filter HIGH", pending_hi["count"] >= 1, pending_hi["count"])
pending_irrev = list_pending(contains_irreversible=True)
test("filter irreversible", pending_irrev["count"] >= 1, pending_irrev["count"])
print(f"  all pending: {pending['count']}, HIGH: {pending_hi['count']}, irrev: {pending_irrev['count']}")

# ─── T6: Sovereign APPROVED → plan APPROVED, receipt SEAL ────────────────────
reset()
r = propose_plan(intent={"description": "staging deploy"}, tasks=[], risk_band="HIGH", irreversible=True)
test("starts PENDING_APPROVAL", r["plan"]["status"] == "PENDING_APPROVAL", r["plan"]["status"])
r2 = update_status(r["plan"]["plan_id"], "APPROVED", "APPROVED",
                   {"F0": "ok", "F1": "ok", "F13": "ok"}, "Staging only, rollback ready", "arif-human")
test("verdict SEAL", r2["verdict"] == "SEAL", r2["verdict"])
test("plan APPROVED", r2["plan"]["status"] == "APPROVED", r2["plan"]["status"])
test("receipt has floor sigs", len(r2["receipt"]["floor_signatures"]) >= 3, r2["receipt"]["floor_signatures"])
print(f"  receipt_id: {r2['receipt']['receipt_id']}")

# ─── T7: Sovereign REJECTED → plan ABORTED, receipt VOID ─────────────────────
reset()
r = propose_plan(intent={"description": "risky op"}, tasks=[], risk_band="HIGH", irreversible=True)
r2 = update_status(r["plan"]["plan_id"], "REJECTED", "REJECTED", {}, "Not ready", "arif-human")
test("verdict VOID", r2["verdict"] == "VOID", r2["verdict"])
test("plan ABORTED", r2["plan"]["status"] == "ABORTED", r2["plan"]["status"])

# ─── T8: Sovereign HOLD → plan stays PENDING_APPROVAL ────────────────────────
reset()
r = propose_plan(intent={"description": "needs review"}, tasks=[], risk_band="HIGH", irreversible=True)
r2 = update_status(r["plan"]["plan_id"], "PENDING_APPROVAL", "HOLD", {}, "Need more info", "arif-human")
test("verdict HOLD", r2["verdict"] == "HOLD", r2["verdict"])
test("plan still PENDING_APPROVAL", r2["plan"]["status"] == "PENDING_APPROVAL", r2["plan"]["status"])

# ─── T9: abort_plan shortcut ─────────────────────────────────────────────────
reset()
r = propose_plan(intent={"description": "to-abort"}, tasks=[], risk_band="LOW", irreversible=False)
r2 = abort_plan(r["plan"]["plan_id"], "Changed mind", "arif-human")
test("verdict SEAL", r2["verdict"] == "SEAL", r2["verdict"])
test("plan ABORTED", r2["plan"]["status"] == "ABORTED", r2["plan"]["status"])

# ─── T10: write_execution_receipt ────────────────────────────────────────────
reset()
r = propose_plan(intent={"description": "task-exec"}, tasks=[{"description": "git push", "tool": "mcpgit",
            "mutates_external_state": True, "target_surface": "git", "reversible": True, "risk_band": "LOW"}],
            risk_band="LOW", irreversible=False)
task_id = r["plan"]["tasks"][0]["task_id"]
r2 = write_execution_receipt(
    plan_id=r["plan"]["plan_id"], task_id=task_id,
    status="COMPLETED", started_at="2026-04-23T01:30:00Z", finished_at="2026-04-23T01:30:05Z",
    logs_ref="s3://logs/2026-04-23/git-push-001", error="", epoch_id="2026-04-23T01Z"
)
test("verdict SEAL", r2["verdict"] == "SEAL", r2["verdict"])
test("execution_receipt returned", "execution_receipt" in r2, True)
test("task status updated", r["plan"]["tasks"][0]["status"] == "COMPLETED",
     r2["execution_receipt"]["status"])

# ─── T11: gk_can_execute — APPROVED plan, no hold → PASS ────────────────────
reset()
r = propose_plan(intent={"description": "low-risk"}, tasks=[{"description": "read", "tool": "mcpgit",
            "mutates_external_state": True, "target_surface": "git", "reversible": True, "risk_band": "LOW"}],
            risk_band="LOW", irreversible=False)
check = gk_can_execute(r["plan"]["plan_id"], r["plan"]["tasks"][0]["task_id"])
test("can_execute=True", check["can_execute"] == True, check)

# ─── T12: gk_can_execute — PENDING_APPROVAL → BLOCK ─────────────────────────
reset()
r = propose_plan(intent={"description": "high-risk"}, tasks=[], risk_band="HIGH", irreversible=True)
check = gk_can_execute(r["plan"]["plan_id"], r["plan"]["tasks"][0]["task_id"]) if r["plan"]["tasks"] else None
# If no tasks, create a dummy check
if not r["plan"]["tasks"]:
    from arifos_plan import Task
    t = Task(task_id="task-test", description="x", tool="y", mutates_external_state=True,
             target_surface="z", reversible=False, risk_band="HIGH")
    r["plan"].tasks.append(t)
    check = gk_can_execute(r["plan"]["plan_id"], "task-test")
test("can_execute=False", check["can_execute"] == False, check)
test("reason contains HOLD", "HOLD" in check.get("reason","") or "approval" in check.get("reason","").lower(),
     check.get("reason"))

# ─── T13: gk_can_execute — ABORTED plan → BLOCK ─────────────────────────────
reset()
r = propose_plan(intent={"description": "abort-test"}, tasks=[], risk_band="LOW", irreversible=False)
abort_plan(r["plan"]["plan_id"], "test abort", "arif-human")
task_id = r["plan"]["tasks"][0]["task_id"] if r["plan"]["tasks"] else "fake-task"
check = gk_can_execute(r["plan"]["plan_id"], task_id)
test("can_execute=False (ABORTED)", check["can_execute"] == False, check)
test("reason ABORTED", "ABORTED" in check.get("reason",""), check.get("reason"))

print("\n" + "="*60)
print("ALL 13 TESTS PASSED — arifos_plan v1.1 ✅")
print("="*60)
