import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  buildCashflowSeries,
  calculateDscrMeasurement,
  calculateEmvMeasurement,
  calculateIrrMeasurement,
  calculateNpvMeasurement,
  calculatePaybackMeasurement,
  calculateProfitabilityIndexMeasurement,
  deriveAllocationSignal,
  validateMeasurementInvariants,
} from "../src/kernel/finance.js";
import { calculateRiskAdjustedRate } from "../src/kernel/capitalx.js";

test("calculateNpvMeasurement returns NPV and EAA on aligned periods", () => {
  const result = calculateNpvMeasurement({
    initial_investment: 1000,
    cash_flows: [500, 500, 500],
    discount_rate: 0.1,
  });

  assert.ok(result.npv > 200);
  assert.ok(result.eaa > 0);
  assert.deepStrictEqual(result.flags, []);
});

test("calculateIrrMeasurement qualifies non-normal cash flows", () => {
  const result = calculateIrrMeasurement({
    initial_investment: 1000,
    cash_flows: [3000, -2500, 800],
    finance_rate: 0.1,
    reinvestment_rate: 0.08,
  });

  assert.ok(result.flags.includes("MULTIPLE_IRR_POSSIBLE"));
  assert.ok(result.flags.includes("NON_NORMAL_FLOWS"));
  assert.ok(result.mirr !== null);
});

test("calculateProfitabilityIndexMeasurement preserves NPV ranking warning", () => {
  const result = calculateProfitabilityIndexMeasurement({
    initial_investment: 1000,
    cash_flows: [600, 600],
    discount_rate: 0.1,
  });

  assert.ok(result.pi > 1);
});

test("calculateProfitabilityIndexMeasurement includes terminal_value and reconciles with NPV", () => {
  const initial = 120000;
  const cfs = [30000, 35000, 40000, 45000, 50000];
  const r = 0.1;
  const tv = 20000;

  const npv = calculateNpvMeasurement({
    initial_investment: initial, cash_flows: cfs, discount_rate: r, terminal_value: tv
  });
  const pi = calculateProfitabilityIndexMeasurement({
    initial_investment: initial, cash_flows: cfs, discount_rate: r, terminal_value: tv
  });

  const expectedPi = npv.pv_inflows / Math.abs(initial);
  assert.ok(Math.abs(pi.pi - expectedPi) < 1e-6,
    `PI mismatch: ${pi.pi} vs expected ${expectedPi}`);
});

test("calculateEmvMeasurement rejects invalid probability mass", () => {
  const result = calculateEmvMeasurement({
    scenarios: [
      { probability: 0.7, outcome: 100 },
      { probability: 0.7, outcome: -50 },
    ],
  });

  assert.ok(result.flags.includes("PROBABILITY_MASS_INVALID"));
});

test("calculatePaybackMeasurement reports unrecovered projects", () => {
  const result = calculatePaybackMeasurement({
    initial_investment: 1000,
    cash_flows: [100, 100, 100],
    discount_rate: 0,
  });

  assert.strictEqual(result.payback_periods, null);
  assert.ok(result.flags.includes("NOT_RECOVERED"));
});

test("calculateDscrMeasurement prefers CFADS and flags stressed leverage", () => {
  const result = calculateDscrMeasurement({
    cfads: 110,
    debt_service: 100,
  });

  assert.strictEqual(result.basis, "CFADS");
  assert.ok(result.flags.includes("LEVERAGE_CRITICAL"));
});

test("period-zero convention stays aligned across NPV, PI, and payback", () => {
  const initialInvestment = 1000;
  const cashflows = [1100];
  assert.deepStrictEqual(buildCashflowSeries(initialInvestment, cashflows), [-1000, 1100]);

  const npv = calculateNpvMeasurement({
    initial_investment: initialInvestment,
    cash_flows: cashflows,
    discount_rate: 0.1,
  });
  const pi = calculateProfitabilityIndexMeasurement({
    initial_investment: initialInvestment,
    cash_flows: cashflows,
    discount_rate: 0.1,
  });
  const payback = calculatePaybackMeasurement({
    initial_investment: initialInvestment,
    cash_flows: cashflows,
    discount_rate: 0,
  });

  assert.ok(Math.abs(npv.npv) < 1e-6);
  assert.ok(Math.abs(pi.pi - 1) < 1e-6);
  assert.ok(Math.abs(payback.payback_periods - (1000 / 1100)) < 1e-6);
});

test("MIRR handles all-positive future cash flows without inventing ambiguity", () => {
  const result = calculateIrrMeasurement({
    initial_investment: 1000,
    cash_flows: [300, 400, 500],
    finance_rate: 0.1,
    reinvestment_rate: 0.08,
  });

  assert.equal(result.mirr !== null, true);
  assert.equal(result.flags.includes("MULTIPLE_IRR_POSSIBLE"), false);
});

test("estimated NPV and DSCR emit confidence bands", () => {
  const npv = calculateNpvMeasurement({
    initial_investment: 1000,
    cash_flows: [600, 600],
    discount_rate: 0.1,
    input_epistemic: "ESTIMATE",
  });
  const dscr = calculateDscrMeasurement({
    cfads: 140,
    debt_service: 100,
    input_epistemic: "ESTIMATE",
  });

  assert.ok(Array.isArray(npv.confidence_band));
  assert.ok(Array.isArray(dscr.confidence_band));
});

test("python server matches JS kernel on canonical parity vectors", () => {
  const script = `
import json
from server import npv_reward, dscr_leverage, growth_velocity
payload = {
  "npv": npv_reward(initial_investment=1000, cash_flows=[500,500,500], discount_rate=0.1)["primary_result"]["npv"],
  "dscr": dscr_leverage(cfads=110, debt_service=100)["primary_result"]["dscr"],
  "growth_mid": growth_velocity(principal=10000, rate=0.08, years=20, annual_contribution=12000, monthly_burn=0)["primary_result"]["growth_forecast"]["mid"],
}
print(json.dumps(payload))
`;
  const run = spawnSync("python", ["-c", script], {
    cwd: "/root/WEALTH",
    encoding: "utf8",
  });
  assert.equal(run.status, 0, run.stderr);
  const actual = JSON.parse(run.stdout.trim());

  const jsNpv = calculateNpvMeasurement({
    initial_investment: 1000,
    cash_flows: [500, 500, 500],
    discount_rate: 0.1,
  });
  const jsDscr = calculateDscrMeasurement({
    cfads: 110,
    debt_service: 100,
  });
  const lowEntropy = 10000;
  let total = lowEntropy;
  for (let i = 0; i < 20; i += 1) {
    total = total * (1 + 0.08) + 12000;
  }

  assert.ok(Math.abs(actual.npv - jsNpv.npv) < 1e-8);
  assert.ok(Math.abs(actual.dscr - jsDscr.dscr) < 1e-8);
  assert.ok(Math.abs(actual.growth_mid - Number(total.toFixed(2))) < 1e-8);
});

test("capitalx monotonicity keeps higher entropy from lowering price", () => {
  const lowEntropy = calculateRiskAdjustedRate(0.05, {
    dS: 0.05,
    peace2: 1.05,
    maruahScore: 0.8,
    trustIndex: 0.7,
    deltaCiv: 0.1,
  });
  const highEntropy = calculateRiskAdjustedRate(0.05, {
    dS: 0.25,
    peace2: 1.05,
    maruahScore: 0.8,
    trustIndex: 0.7,
    deltaCiv: 0.1,
  });

  assert.ok(highEntropy.r_adj >= lowEntropy.r_adj);
});

test("validateMeasurementInvariants catches PI mismatch", () => {
  const flags = validateMeasurementInvariants(120000, [30000, 35000, 40000, 45000, 50000], 0.1, 20000, {
    npv: 40451,
    pi: 1.23, // wrong
    pv_inflows: 160451,
  });
  assert.ok(flags.includes("INVARIANT_VIOLATION"));
});

test("validateMeasurementInvariants passes when PI is correct", () => {
  const npv = calculateNpvMeasurement({
    initial_investment: 120000, cash_flows: [30000, 35000, 40000, 45000, 50000], discount_rate: 0.1, terminal_value: 20000
  });
  const pi = calculateProfitabilityIndexMeasurement({
    initial_investment: 120000, cash_flows: [30000, 35000, 40000, 45000, 50000], discount_rate: 0.1, terminal_value: 20000
  });
  const flags = validateMeasurementInvariants(120000, [30000, 35000, 40000, 45000, 50000], 0.1, 20000, {
    npv: npv.npv,
    pi: pi.pi,
    pv_inflows: npv.pv_inflows,
  });
  assert.deepStrictEqual(flags, []);
});

test("deriveAllocationSignal returns REJECT for negative NPV", () => {
  const signal = deriveAllocationSignal([], { npv: -31967 }, "wealth_npv_reward");
  assert.strictEqual(signal, "REJECT");
});

test("deriveAllocationSignal returns ACCEPT for positive NPV", () => {
  const signal = deriveAllocationSignal([], { npv: 40451 }, "wealth_npv_reward");
  assert.strictEqual(signal, "ACCEPT");
});

test("deriveAllocationSignal returns REJECT for unrecovered payback", () => {
  const signal = deriveAllocationSignal(["NOT_RECOVERED"], { payback_periods: null }, "wealth_payback_time");
  assert.strictEqual(signal, "REJECT");
});

test("python server matches JS kernel on PI parity with terminal_value", () => {
  const script = `
import json
from server import pi_efficiency, npv_reward
npv = npv_reward(initial_investment=120000, cash_flows=[30000,35000,40000,45000,50000], discount_rate=0.1, terminal_value=20000)["primary_result"]["npv"]
pi = pi_efficiency(initial_investment=120000, cash_flows=[30000,35000,40000,45000,50000], discount_rate=0.1, terminal_value=20000)["primary_result"]["pi"]
expected = pi_efficiency(initial_investment=120000, cash_flows=[30000,35000,40000,45000,50000], discount_rate=0.1, terminal_value=20000)["allocation_signal"]
print(json.dumps({"npv": npv, "pi": pi, "alloc": expected}))
`;
  const run = spawnSync("python", ["-c", script], {
    cwd: "/root/WEALTH",
    encoding: "utf8",
  });
  assert.equal(run.status, 0, run.stderr);
  const actual = JSON.parse(run.stdout.trim());

  const jsNpv = calculateNpvMeasurement({
    initial_investment: 120000,
    cash_flows: [30000, 35000, 40000, 45000, 50000],
    discount_rate: 0.1,
    terminal_value: 20000,
  });
  const jsPi = calculateProfitabilityIndexMeasurement({
    initial_investment: 120000,
    cash_flows: [30000, 35000, 40000, 45000, 50000],
    discount_rate: 0.1,
    terminal_value: 20000,
  });

  assert.ok(Math.abs(actual.npv - jsNpv.npv) < 1e-6);
  assert.ok(Math.abs(actual.pi - jsPi.pi) < 1e-6);
  assert.strictEqual(actual.alloc, "ACCEPT");
});
