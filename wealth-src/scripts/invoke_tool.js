/**
 * WEALTH Dimensional Kernel v1.3.0 - invoke_tool.js
 * Logic: Physics > Narrative
 * Convention: Absolute-Input, Under-Score Naming, Common Envelope
 */
import { calculateRiskAdjustedRate, compareCapitalAdvantage } from "../host/kernel/capitalx.js";
import {
  calculateDscrMeasurement,
  calculateEmvMeasurement,
  calculateIrrMeasurement,
  calculateNpvMeasurement,
  calculatePaybackMeasurement,
  calculateProfitabilityIndexMeasurement,
  deriveMetricGovernance,
  inferEpistemicFromFlags,
} from "../host/kernel/finance.js";
import { computeNetWorth } from "../host/wealth/networth.js";
import { computeCashflow } from "../host/wealth/cashflow.js";
import { projectCompoundGrowth, projectRunwayDepletion } from "../host/wealth/projection.js";

const [,, toolName, argsJson] = process.argv;
const args = JSON.parse(argsJson || "{}");

const ASSET_CLASSES = ["cash", "equity", "property", "digital", "debt", "business"];

function confidenceFromVerdict(verdict, flags) {
  if (verdict === "VOID") return "LOW";
  if (verdict === "888-HOLD") return "LOW";
  if (verdict === "QUALIFY" || flags.length > 0) return "MEDIUM";
  return "HIGH";
}

function createEnvelope(tool, dimension, primary, secondary = {}, flags = [], options = {}) {
  const verdict = options.verdict ?? deriveMetricGovernance(flags);
  const epistemic = options.epistemic ?? inferEpistemicFromFlags(flags, "CLAIM");
  return {
    tool,
    dimension,
    verdict,
    primary_result: primary,
    secondary_metrics: secondary,
    integrity_flags: flags,
    confidence: confidenceFromVerdict(verdict, flags),
    epistemic,
    assumptions: options.assumptions ?? [],
    epoch: new Date().toISOString()
  };
}

const tools = {
  // 1. REWARD (wealth_npv_reward)
  "npv_reward": (a) => {
    const measurement = calculateNpvMeasurement(a);
    return createEnvelope(
      "wealth_npv_reward",
      "Reward",
      { npv: measurement.npv },
      {
        eaa: measurement.eaa,
        pv_inflows: measurement.pv_inflows,
        pv_outflows: measurement.pv_outflows,
        period_count: measurement.period_count,
        period_unit: measurement.period_unit,
        confidence_band: measurement.confidence_band,
      },
      measurement.flags,
      { assumptions: measurement.assumptions },
    );
  },

  // 2. ENERGY / YIELD (wealth_irr_yield)
  "irr_yield": (a) => {
    const measurement = calculateIrrMeasurement(a);
    return createEnvelope(
      "wealth_irr_yield",
      "Energy",
      { irr: measurement.irr },
      {
        mirr: measurement.mirr,
        sign_changes: measurement.sign_changes,
        period_count: measurement.period_count,
        period_unit: measurement.period_unit,
      },
      measurement.flags,
      { assumptions: measurement.assumptions },
    );
  },

  // 3. ENERGY / CONCENTRATION (wealth_pi_efficiency)
  "pi_efficiency": (a) => {
    const measurement = calculateProfitabilityIndexMeasurement(a);
    return createEnvelope(
      "wealth_pi_efficiency",
      "Energy",
      { pi: measurement.pi },
      { ranking_signal: measurement.pi !== null && measurement.pi >= 1 ? "EFFICIENT" : "EXTRACTIVE" },
      measurement.flags,
      { assumptions: measurement.assumptions },
    );
  },

  // 4. ENTROPY / RISK (wealth_emv_risk)
  "emv_risk": (a) => {
    const measurement = calculateEmvMeasurement(a);
    return createEnvelope(
      "wealth_emv_risk",
      "Entropy",
      { emv: measurement.emv },
      {
        scenario_count: a.scenarios?.length ?? 0,
        total_probability: measurement.total_probability,
        downside_probability: measurement.downside_probability,
        variance: measurement.variance,
        worst_outcome: measurement.worst_outcome,
        best_outcome: measurement.best_outcome,
      },
      measurement.flags,
      { assumptions: measurement.assumptions, epistemic: "ESTIMATE" },
    );
  },

  // 5. ENTROPY / INTEGRITY (wealth_audit_entropy)
  "audit_entropy": (a) => {
    const { initial_investment, cash_flows, discount_rate = 0.1 } = a;
    const irrMeasurement = calculateIrrMeasurement({
      initial_investment,
      cash_flows,
      finance_rate: discount_rate,
      reinvestment_rate: discount_rate,
    });
    const variations = [0.8, 0.9, 1.0, 1.1, 1.2];
    const sensitivity = variations.map(v => {
      const measurement = calculateNpvMeasurement({
        initial_investment,
        cash_flows,
        discount_rate: discount_rate * v,
      });
      return { multiplier: v, npv: measurement.npv };
    });
    const flags = [...irrMeasurement.flags];
    return createEnvelope(
      "wealth_audit_entropy",
      "Entropy",
      { sign_changes: irrMeasurement.sign_changes },
      { sensitivity_sweep: sensitivity },
      flags,
      { assumptions: irrMeasurement.assumptions, epistemic: "ESTIMATE" },
    );
  },

  // 6. SURVIVAL / LEVERAGE (wealth_dscr_leverage)
  "dscr_leverage": (a) => {
    const measurement = calculateDscrMeasurement(a);
    return createEnvelope(
      "wealth_dscr_leverage",
      "Survival",
      { dscr: measurement.dscr },
      { basis: measurement.basis, period_unit: measurement.period_unit, confidence_band: measurement.confidence_band },
      measurement.flags,
      { assumptions: measurement.assumptions },
    );
  },

  // 7. TIME / RECOVERY (wealth_payback_time)
  "payback_time": (a) => {
    const measurement = calculatePaybackMeasurement(a);
    return createEnvelope(
      "wealth_payback_time",
      "Time",
      { payback_periods: measurement.payback_periods },
      { period_unit: measurement.period_unit, discounted: measurement.discounted },
      measurement.flags,
      { assumptions: measurement.assumptions },
    );
  },

  // 8. VELOCITY / EXPANSION (wealth_growth_velocity)
  "growth_velocity": (a) => {
    const { principal, rate, years, annual_contribution = 0, monthly_burn } = a;
    const growth = projectCompoundGrowth(principal, rate, years, annual_contribution);
    const runway = projectRunwayDepletion(principal, monthly_burn, 0);
    const flags = runway.runway_months < 3 ? ["RUNWAY_CRITICAL"] : [];
    return createEnvelope(
      "wealth_growth_velocity",
      "Velocity",
      { growth_forecast: growth.result },
      { runway_months: runway.runway_months, final_value: growth.final_value },
      flags,
      { assumptions: ["Forward projections remain ESTIMATE by design."], epistemic: "ESTIMATE" },
    );
  },

  // 9. MASS / STATE (wealth_networth_state)
  "networth_state": (a) => {
    const validatedAssets = a.assets.map(asset => ({
      ...asset,
      asset_class: ASSET_CLASSES.includes((asset.asset_class ?? asset.category ?? "").toLowerCase())
        ? (asset.asset_class ?? asset.category).toLowerCase()
        : "other"
    }));
    const result = computeNetWorth(validatedAssets, a.liabilities);
    return createEnvelope(
      "wealth_networth_state",
      "Mass",
      result,
      {},
      result.integrity_flags ?? [],
      { epistemic: result.epistemic },
    );
  },

  // 10. FLOW / METABOLIC (wealth_cashflow_flow)
  "cashflow_flow": (a) => {
    const result = computeCashflow(a.income, a.expenses, a.liquid_assets ?? 0);
    return createEnvelope(
      "wealth_cashflow_flow",
      "Flow",
      result,
      { period_unit: "monthly" },
      result.integrity_flags ?? [],
      { epistemic: result.epistemic },
    );
  },

  // 11. ALLOCATION / KERNEL (wealth_score_kernel)
  "score_kernel": (a) => {
    const { base_rate, dS, peace2, maruahScore, compare = false, wealth_signals = {}, extractive_signals = {} } = a;
    const flags = [];
    if (dS > 0.3) flags.push("HIGH_ENTROPY_SIGNAL");
    if (maruahScore < 0.6) flags.push("SOVEREIGN_DIGNITY_LOW");

    if (compare) {
      const comparison = compareCapitalAdvantage(base_rate, { dS, peace2, maruahScore, ...wealth_signals }, extractive_signals);
      return createEnvelope(
        "wealth_score_kernel",
        "Allocation",
        comparison,
        {},
        [...flags, ...(comparison.integrity_flags ?? [])],
        { assumptions: comparison.assumptions ?? ["CapitalX remains an estimate until delta_bps is proven."], epistemic: "ESTIMATE" },
      );
    }
    const score = calculateRiskAdjustedRate(base_rate, { dS, peace2, maruahScore, ...wealth_signals });
    return createEnvelope(
      "wealth_score_kernel",
      "Allocation",
      score,
      {},
      [...flags, ...(score.integrity_flags ?? [])],
      { assumptions: score.assumptions ?? ["CapitalX remains an estimate until delta_bps is proven."], epistemic: "ESTIMATE" },
    );
  }
};

if (!tools[toolName]) {
  console.error(`Unknown tool: ${toolName}`);
  process.exit(1);
}

try {
  const result = tools[toolName](args);
  console.log(JSON.stringify(result, null, 2));
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
