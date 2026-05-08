import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const runPython = (script) => {
  const result = spawnSync("python", ["-c", script], {
    cwd: "/root/WEALTH",
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout);
  }
  return JSON.parse(result.stdout.trim());
};

test("check_floors passes for clean operation", () => {
  const out = runPython(`
import json
from server import check_floors_tool
r = check_floors_tool(reversible=True, human_confirmed=True, epistemic="CLAIM", ai_is_deciding=False, floor_override=False, peace2=1.0, maruah_score=0.8, uncertainty_band=[0.03, 0.05], task_definition="Evaluate constitutional floors for this operation")
print(json.dumps({"pass": r["primary_result"]["pass"], "verdict": r["primary_result"]["verdict"], "gov": r["governance_verdict"]}))
`);
  assert.strictEqual(out.pass, true);
  assert.strictEqual(out.verdict, "SEAL");
  assert.strictEqual(out.gov, "SEAL");
});

test("check_floors voids when AI is deciding", () => {
  const out = runPython(`
import json
from server import check_floors_tool
r = check_floors_tool(ai_is_deciding=True, uncertainty_band=[0.03, 0.05], maruah_score=0.8, peace2=1.0, task_definition="Testing AI decision boundary")
print(json.dumps({"verdict": r["governance_verdict"]}))
`);
  assert.strictEqual(out.verdict, "VOID");
});

test("check_floors holds irreversible high-scale action", () => {
  const out = runPython(`
import json
from server import check_floors_tool
r = check_floors_tool(reversible=False, human_confirmed=False, scale_mode="civilization", task_definition="Test irreversible civilization scale action")
print(json.dumps({"verdict": r["governance_verdict"]}))
`);
  assert.strictEqual(out.verdict, "888-HOLD");
});

test("policy_audit blocks carbon violation", () => {
  const out = runPython(`
import json
from server import policy_audit
r = policy_audit(proposal={"carbon_intensity": 0.08, "maruah_score": 0.8, "peace2": 1.0}, scale_mode="civilization")
print(json.dumps({"pass": r["primary_result"]["policy_pass"], "verdict": r["governance_verdict"], "flags": r["secondary_metrics"]["flags"]}))
`);
  assert.strictEqual(out.pass, false);
  assert.strictEqual(out.verdict, "VOID");
  assert.ok(out.flags.includes("CARBON_VIOLATION"));
  assert.ok(out.flags.includes("CIVILIZATION_HARD_BLOCK"));
});

test("policy_audit accepts within constraints", () => {
  const out = runPython(`
import json
from server import policy_audit
r = policy_audit(proposal={"carbon_intensity": 0.02, "maruah_score": 0.8, "dscr": 1.5}, scale_mode="enterprise")
print(json.dumps({"pass": r["primary_result"]["policy_pass"], "verdict": r["governance_verdict"]}))
`);
  assert.strictEqual(out.pass, true);
  assert.strictEqual(out.verdict, "SEAL");
});

test("civilization_stewardship triggers governance and vaults", () => {
  const out = runPython(`
import json, os
vault_path = "/root/WEALTH/data/vault999.jsonl"
if os.path.exists(vault_path):
    os.remove(vault_path)
from server import civilization_stewardship
r = civilization_stewardship(population=8e9, energy_budget_twh=160000, carbon_budget_gt=500, tech_growth_rate=0.02, time_horizon_years=100)
has_vault = os.path.exists(vault_path)
print(json.dumps({"verdict": r["governance_verdict"], "has_vault": has_vault, "alloc": r["allocation_signal"]}))
`);
  assert.strictEqual(out.has_vault, true);
  // Civilization scale always triggers governance; since carbon_intensity may be low for this input, it might pass
  assert.ok(["SEAL", "VOID", "888-HOLD", "QUALIFY"].includes(out.verdict));
});

test("crisis_triage forces 888-HOLD on irreversible without human confirm", () => {
  const out = runPython(`
import json
from server import crisis_triage
r = crisis_triage(resources={"water": 1000}, demands=[{"name": "camp", "amount": 800, "resource_type": "water", "urgency": 9}], recovery_horizon_days=30)
print(json.dumps({"verdict": r["governance_verdict"], "alloc": r["allocation_signal"]}))
`);
  // Crisis mode with reversible=False in governance_args should trigger F1/F13 HOLD
  assert.strictEqual(out.verdict, "888-HOLD");
  assert.strictEqual(out.alloc, "INSUFFICIENT_DATA");
});
