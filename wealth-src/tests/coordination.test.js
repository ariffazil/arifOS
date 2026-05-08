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

test("lp_allocator solves simple water allocation", () => {
  const out = runPython(`
import json
from host.coordination.lp_allocator import allocate
agents = [
    {"name": "A", "utility": {"water": 2.0}, "demand": {"water": 100}},
    {"name": "B", "utility": {"water": 1.0}, "demand": {"water": 100}},
]
resources = {"water": 120}
r = allocate(agents, resources)
print(json.dumps({
    "feasible": r["feasible"],
    "total_welfare": r["total_welfare"],
    "A_water": r["allocations"]["A"]["water"],
    "B_water": r["allocations"]["B"]["water"],
    "shadow": r["shadow_prices"].get("water"),
}))
`);
  assert.strictEqual(out.feasible, true);
  assert.ok(out.total_welfare > 0);
  assert.ok(out.A_water >= out.B_water, "Higher utility agent should get more");
});

test("commons_risk detects scarcity accurately", () => {
  const out = runPython(`
import json
from host.coordination.commons import commons_risk
agents = [
    {"name": "A", "utility": {"water": 1.0}, "demand": {"water": 100}},
    {"name": "B", "utility": {"water": 1.0}, "demand": {"water": 100}},
]
resources = {"water": 80}
r = commons_risk(agents, resources)
print(json.dumps({"tragedy_risk": r["tragedy_risk"], "scarcity": r["scarcity_index"]["water"]}))
`);
  assert.ok(out.scarcity > 0.19, `Expected scarcity > 0.19, got ${out.scarcity}`);
  assert.ok(out.tragedy_risk > 0.0);
});

test("shapley_values distributes surplus fairly", () => {
  const out = runPython(`
import json
from host.coordination.cooperative import shapley_values
agents = [
    {"name": "A", "utility": {"water": 2.0}, "demand": {"water": 100}},
    {"name": "B", "utility": {"water": 1.0}, "demand": {"water": 100}},
]
resources = {"water": 150}
r = shapley_values(agents, resources)
print(json.dumps({"A": r["shapley"]["A"], "B": r["shapley"]["B"], "total": r["total_value"]}))
`);
  assert.ok(out.A >= out.B, "Higher utility agent should have higher Shapley value");
  assert.ok(out.total > 0);
});

test("core_feasibility identifies blocking coalitions", () => {
  const out = runPython(`
import json
from host.coordination.cooperative import core_feasibility
agents = [
    {"name": "A", "utility": {"water": 2.0}, "demand": {"water": 100}},
    {"name": "B", "utility": {"water": 1.0}, "demand": {"water": 100}},
]
resources = {"water": 120}
r = core_feasibility(agents, resources)
print(json.dumps({"in_core": r["in_core"], "blocking": len(r["blocking_coalitions"])}))
`);
  assert.strictEqual(typeof out.in_core, "boolean");
});

test("nash_approximation converges for symmetric game", () => {
  const out = runPython(`
import json
from host.coordination.strategic import nash_approximation
agents = [
    {"name": "A", "utility": {"water": 1.0}, "demand": {"water": 100}},
    {"name": "B", "utility": {"water": 1.0}, "demand": {"water": 100}},
]
resources = {"water": 100}
r = nash_approximation(agents, resources, max_iterations=100)
print(json.dumps({"converged": r["converged"], "A": r["equilibrium"]["A"]["water"], "B": r["equilibrium"]["B"]["water"]}))
`);
  assert.strictEqual(out.converged, true);
  assert.ok(Math.abs(out.A - 50) < 5);
  assert.ok(Math.abs(out.B - 50) < 5);
});

test("wealth_game_theory_solve returns LP + Shapley + Core + Nash", () => {
  const out = runPython(`
import json
from server import game_theory_solve
agents = [
    {"name": "Farmer", "utility": {"water": 3.0}, "resource_demand": {"water": 80}, "cooperative_value": 100},
    {"name": "Factory", "utility": {"water": 1.5}, "resource_demand": {"water": 60}, "cooperative_value": 80},
]
resources = {"water": 100}
r = game_theory_solve(agents, resources, mechanism="cooperative", solve_equilibrium=True)
print(json.dumps({
    "welfare": r["primary_result"]["total_welfare"],
    "in_core": r["primary_result"]["in_core"],
    "has_shapley": "Farmer" in r["secondary_metrics"]["shapley"],
    "eq_converged": r["secondary_metrics"]["equilibrium"].get("converged", False),
    "alloc_farmer": r["secondary_metrics"]["allocations"].get("Farmer", {}).get("water"),
}))
`);
  assert.ok(out.welfare > 0);
  assert.strictEqual(out.has_shapley, true);
  assert.strictEqual(typeof out.in_core, "boolean");
  assert.strictEqual(out.eq_converged, true);
  assert.ok(out.alloc_farmer > 0);
});

test("wealth_coordination_equilibrium uses LP shadow prices", () => {
  const out = runPython(`
import json
from server import coordination_equilibrium
agents = [
    {"name": "A", "utility": {"gpu": 1.0}, "resource_demand": {"gpu": 15}, "cooperative_value": 100},
    {"name": "B", "utility": {"gpu": 1.0}, "resource_demand": {"gpu": 15}, "cooperative_value": 100},
]
r = coordination_equilibrium(agents, {"gpu": 20}, mechanism="cooperative")
print(json.dumps({
    "tragedy": r["primary_result"]["tragedy_risk"],
    "has_shadow": "gpu" in r["secondary_metrics"].get("shadow_prices", {}),
    "welfare": r["primary_result"]["total_welfare"],
}))
`);
  assert.ok(out.tragedy > 0.0);
  assert.strictEqual(out.has_shadow, true);
  assert.ok(out.welfare > 0);
});
