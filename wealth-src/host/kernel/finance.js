const EPSILON = 1e-9;
const INVALID_FLAGS = new Set([
  "INVALID_INITIAL_INVESTMENT",
  "INVALID_CASHFLOW_SERIES",
  "INVALID_DISCOUNT_RATE",
  "INVALID_FINANCE_RATE",
  "INVALID_REINVESTMENT_RATE",
  "INVALID_SCENARIOS",
  "INVALID_SCENARIO",
  "PROBABILITY_MASS_INVALID",
  "INVALID_DEBT_SERVICE",
  "INVALID_CFADS",
]);
const HOLD_FLAGS = new Set([
  "LEVERAGE_CRITICAL",
  "LEVERAGE_DEFAULT",
  "MULTIPLE_IRR_POSSIBLE",
]);
const QUALIFY_FLAGS = new Set([
  "NON_NORMAL_FLOWS",
  "IRR_NOT_FOUND",
  "NOT_RECOVERED",
  "EBITDA_PROXY_USED",
]);

function round(value, digits = 6) {
  if (!Number.isFinite(value)) {
    return value;
  }

  return Number(value.toFixed(digits));
}

function countSignChanges(values) {
  let previousSign = 0;
  let changes = 0;

  for (const rawValue of values) {
    if (!Number.isFinite(rawValue) || Math.abs(rawValue) <= EPSILON) {
      continue;
    }

    const sign = rawValue > 0 ? 1 : -1;
    if (previousSign !== 0 && sign !== previousSign) {
      changes += 1;
    }
    previousSign = sign;
  }

  return changes;
}

function npvFromSeries(cashflowSeries, discountRate) {
  return cashflowSeries.reduce((sum, cashflow, index) => {
    if (index === 0) {
      return sum + cashflow;
    }

    return sum + cashflow / Math.pow(1 + discountRate, index);
  }, 0);
}

function presentValueBreakdown(cashflowSeries, discountRate) {
  const discounted = cashflowSeries.map((cashflow, index) => (
    index === 0 ? cashflow : cashflow / Math.pow(1 + discountRate, index)
  ));

  const pvInflows = discounted
    .filter((value) => value > 0)
    .reduce((sum, value) => sum + value, 0);
  const pvOutflows = discounted
    .filter((value) => value < 0)
    .reduce((sum, value) => sum + Math.abs(value), 0);

  return {
    discounted_cashflows: discounted.map((value) => round(value, 6)),
    pv_inflows: round(pvInflows, 6),
    pv_outflows: round(pvOutflows, 6),
  };
}

function validatePeriodicRate(rate, invalidFlag) {
  if (!Number.isFinite(rate) || rate <= -1) {
    return [invalidFlag];
  }

  return [];
}

function validateSeries(initialInvestment, cashFlows) {
  const flags = [];

  if (!Number.isFinite(initialInvestment) || initialInvestment === 0) {
    flags.push("INVALID_INITIAL_INVESTMENT");
  }
  if (!Array.isArray(cashFlows) || cashFlows.length === 0 || cashFlows.some((value) => !Number.isFinite(value))) {
    flags.push("INVALID_CASHFLOW_SERIES");
  }

  return flags;
}

function bracketRoots(npvFn, lower = -0.9999, upper = 10, steps = 4096) {
  const brackets = [];
  const step = (upper - lower) / steps;
  let previousRate = lower;
  let previousValue = npvFn(previousRate);

  for (let index = 1; index <= steps; index += 1) {
    const rate = lower + step * index;
    const value = npvFn(rate);

    if (!Number.isFinite(previousValue) || !Number.isFinite(value)) {
      previousRate = rate;
      previousValue = value;
      continue;
    }

    if (Math.abs(previousValue) <= EPSILON) {
      brackets.push([previousRate, previousRate]);
    } else if (previousValue * value < 0) {
      brackets.push([previousRate, rate]);
    } else if (Math.abs(value) <= EPSILON) {
      brackets.push([rate, rate]);
    }

    previousRate = rate;
    previousValue = value;
  }

  return brackets;
}

function bisectRoot(npvFn, lower, upper, iterations = 200) {
  if (lower === upper) {
    return lower;
  }

  let left = lower;
  let right = upper;
  let leftValue = npvFn(left);
  let rightValue = npvFn(right);

  for (let index = 0; index < iterations; index += 1) {
    const midpoint = (left + right) / 2;
    const midpointValue = npvFn(midpoint);

    if (!Number.isFinite(midpointValue)) {
      break;
    }
    if (Math.abs(midpointValue) <= EPSILON) {
      return midpoint;
    }

    if (leftValue * midpointValue <= 0) {
      right = midpoint;
      rightValue = midpointValue;
    } else {
      left = midpoint;
      leftValue = midpointValue;
    }

    if (Math.abs(right - left) <= EPSILON || Math.abs(rightValue - leftValue) <= EPSILON) {
      return (left + right) / 2;
    }
  }

  return (left + right) / 2;
}

export function deriveMetricGovernance(flags = [], defaultVerdict = "SEAL") {
  if (flags.some((flag) => INVALID_FLAGS.has(flag))) {
    return "VOID";
  }
  if (flags.some((flag) => HOLD_FLAGS.has(flag))) {
    return "888-HOLD";
  }
  if (flags.some((flag) => QUALIFY_FLAGS.has(flag))) {
    return "QUALIFY";
  }

  return defaultVerdict;
}

export function inferEpistemicFromFlags(flags = [], defaultEpistemic = "CLAIM") {
  if (flags.some((flag) => INVALID_FLAGS.has(flag))) {
    return "UNKNOWN";
  }
  if (flags.some((flag) => HOLD_FLAGS.has(flag) || QUALIFY_FLAGS.has(flag))) {
    return "ESTIMATE";
  }

  return defaultEpistemic;
}

export function deriveAllocationSignal(flags = [], primary = {}, toolName = "", scaleMode = "enterprise") {
  if (flags.some((flag) => INVALID_FLAGS.has(flag))) {
    return "INSUFFICIENT_DATA";
  }

  const SCALE_DEFAULTS = {
    personal: { discountRate: 0.03 },
    household: { discountRate: 0.04 },
    sme: { discountRate: 0.10 },
    enterprise: { discountRate: 0.10 },
    national: { discountRate: 0.02 },
    crisis: { discountRate: Infinity },
    civilization: { discountRate: 0.005 },
    agentic: { discountRate: 0.15 },
  };
  const scale = SCALE_DEFAULTS[scaleMode] || SCALE_DEFAULTS.enterprise;

  if (toolName === "npv" || toolName === "wealth_npv_reward") {
    const npv = primary.npv;
    if (npv === null || npv === undefined) return "INSUFFICIENT_DATA";
    if (npv > 0) return "ACCEPT";
    if (npv < 0) return "REJECT";
    return "MARGINAL";
  }

  if (toolName === "pi" || toolName === "wealth_pi_efficiency") {
    const pi = primary.pi;
    if (pi === null || pi === undefined) return "INSUFFICIENT_DATA";
    if (pi > 1) return "ACCEPT";
    if (pi < 1) return "REJECT";
    return "MARGINAL";
  }

  if (toolName === "irr" || toolName === "wealth_irr_yield") {
    const irr = primary.irr;
    if (irr === null || irr === undefined) return "INSUFFICIENT_DATA";
    const hurdle = scale.discountRate === Infinity ? 0.10 : scale.discountRate;
    if (irr > hurdle) return "ACCEPT";
    if (irr < hurdle) return "REJECT";
    return "MARGINAL";
  }

  if (toolName === "payback" || toolName === "wealth_payback_time") {
    const payback = primary.payback_periods;
    if (payback === null || payback === undefined) {
      return flags.includes("NOT_RECOVERED") ? "REJECT" : "INSUFFICIENT_DATA";
    }
    return "ACCEPT";
  }

  if (toolName === "dscr" || toolName === "wealth_dscr_leverage") {
    const dscr = primary.dscr;
    if (dscr === null || dscr === undefined) return "INSUFFICIENT_DATA";
    if (dscr >= 1.5) return "ACCEPT";
    if (dscr >= 1.25) return "MARGINAL";
    return "REJECT";
  }

  return "MARGINAL";
}

export function validateMeasurementInvariants(initialInvestment, cashFlows, discountRate, terminalValue = 0, measurementResults = {}) {
  const flags = [];
  const { npv, irr, pi, pv_inflows } = measurementResults;

  const series = buildCashflowSeries(initialInvestment, cashFlows, terminalValue);
  const signChanges = countSignChanges(series);

  if (pi !== null && pi !== undefined && pv_inflows !== null && pv_inflows !== undefined) {
    const expectedPi = pv_inflows / Math.abs(initialInvestment);
    if (Math.abs(pi - expectedPi) > 0.001) {
      flags.push("INVARIANT_VIOLATION");
    }
  }

  if (npv !== null && npv !== undefined && pi !== null && pi !== undefined && signChanges <= 1) {
    if ((npv > 0 && pi <= 1) || (npv < 0 && pi >= 1)) {
      flags.push("INVARIANT_VIOLATION");
    }
  }

  if (npv !== null && npv !== undefined && irr !== null && irr !== undefined && discountRate !== null && discountRate !== undefined && signChanges <= 1) {
    if ((npv > 0 && irr <= discountRate) || (npv < 0 && irr >= discountRate)) {
      flags.push("INVARIANT_VIOLATION");
    }
  }

  return flags;
}

export function buildCashflowSeries(initialInvestment, cashFlows, terminalValue = 0) {
  const series = [-Math.abs(initialInvestment), ...cashFlows];
  if (terminalValue !== 0 && series.length > 1) {
    series[series.length - 1] += terminalValue;
  }
  return series;
}

export function deriveConfidenceBand(value, epistemic = "CLAIM", mode = "relative") {
  if (!Number.isFinite(value)) {
    return null;
  }

  const upperEpistemic = String(epistemic).toUpperCase();
  const relativeWidth = upperEpistemic === "HYPOTHESIS"
    ? 0.25
    : upperEpistemic === "ESTIMATE"
      ? 0.15
      : upperEpistemic === "PLAUSIBLE"
        ? 0.08
        : 0;

  if (relativeWidth === 0) {
    return null;
  }

  if (mode === "absolute-nonnegative") {
    const delta = Math.max(0.05, Math.abs(value) * relativeWidth);
    return [round(Math.max(0, value - delta), 6), round(value + delta, 6)];
  }

  return [
    round(value * (1 - relativeWidth), 6),
    round(value * (1 + relativeWidth), 6),
  ];
}

export function calculateNpvMeasurement({
  initial_investment,
  cash_flows,
  discount_rate,
  terminal_value = 0,
  period_unit = "annual",
  input_epistemic = "CLAIM",
}) {
  const flags = [
    ...validateSeries(initial_investment, cash_flows),
    ...validatePeriodicRate(discount_rate, "INVALID_DISCOUNT_RATE"),
  ];

  if (flags.length > 0) {
    return {
      npv: null,
      eaa: null,
      pv_inflows: null,
      pv_outflows: null,
      discounted_cashflows: [],
      period_count: Array.isArray(cash_flows) ? cash_flows.length : 0,
      period_unit,
      assumptions: [
        "Cash flows are periodic and sign-preserving.",
        "Discount rate must match the cash flow period.",
      ],
      flags,
    };
  }

  const series = buildCashflowSeries(initial_investment, cash_flows, terminal_value);
  const breakdown = presentValueBreakdown(series, discount_rate);
  const npv = npvFromSeries(series, discount_rate);
  const periods = cash_flows.length;
  const eaa = periods === 0
    ? null
    : (
      Math.abs(discount_rate) <= EPSILON
        ? npv / periods
        : (npv * discount_rate) / (1 - Math.pow(1 + discount_rate, -periods))
    );

  return {
    npv: round(npv, 6),
    eaa: round(eaa, 6),
    pv_inflows: breakdown.pv_inflows,
    pv_outflows: breakdown.pv_outflows,
    discounted_cashflows: breakdown.discounted_cashflows,
    period_count: periods,
    period_unit,
    assumptions: [
      "NPV is the primary accept/reject metric.",
      "Discount rate and cash flow periodicity are aligned.",
    ],
    input_epistemic: String(input_epistemic).toUpperCase(),
    confidence_band: deriveConfidenceBand(npv, input_epistemic),
    flags,
  };
}

export function calculateIrrMeasurement({
  initial_investment,
  cash_flows,
  finance_rate = 0.1,
  reinvestment_rate = 0.1,
  period_unit = "annual",
}) {
  const flags = [
    ...validateSeries(initial_investment, cash_flows),
    ...validatePeriodicRate(finance_rate, "INVALID_FINANCE_RATE"),
    ...validatePeriodicRate(reinvestment_rate, "INVALID_REINVESTMENT_RATE"),
  ];

  if (flags.length > 0) {
    return {
      irr: null,
      mirr: null,
      sign_changes: 0,
      period_count: Array.isArray(cash_flows) ? cash_flows.length : 0,
      period_unit,
      assumptions: [
        "IRR requires at least one negative and one positive cash flow.",
        "MIRR separates finance and reinvestment assumptions.",
      ],
      flags,
    };
  }

  const series = buildCashflowSeries(initial_investment, cash_flows);
  const signChanges = countSignChanges(series);
  if (signChanges > 1) {
    flags.push("NON_NORMAL_FLOWS", "MULTIPLE_IRR_POSSIBLE");
  }

  const npvFn = (rate) => npvFromSeries(series, rate);
  const brackets = bracketRoots(npvFn);
  const roots = [...new Set(brackets.map(([lower, upper]) => round(bisectRoot(npvFn, lower, upper), 10)))];

  let irr = null;
  if (roots.length === 1) {
    irr = roots[0];
  } else if (roots.length === 0) {
    flags.push("IRR_NOT_FOUND");
  }

  const periodCount = series.length - 1;
  const pvNegative = series.reduce((sum, cashflow, index) => {
    if (cashflow >= 0) {
      return sum;
    }

    return sum + (cashflow / Math.pow(1 + finance_rate, index));
  }, 0);
  const fvPositive = series.reduce((sum, cashflow, index) => {
    if (cashflow <= 0) {
      return sum;
    }

    return sum + (cashflow * Math.pow(1 + reinvestment_rate, periodCount - index));
  }, 0);

  const mirr = (pvNegative < 0 && fvPositive > 0 && periodCount > 0)
    ? Math.pow(fvPositive / Math.abs(pvNegative), 1 / periodCount) - 1
    : null;

  return {
    irr: irr === null ? null : round(irr, 8),
    mirr: mirr === null ? null : round(mirr, 8),
    sign_changes: signChanges,
    period_count: periodCount,
    period_unit,
    assumptions: [
      "NPV remains the primary ranking metric for mutually exclusive projects.",
      "MIRR is preferred when reinvestment should not equal IRR.",
    ],
    flags,
  };
}

export function calculateProfitabilityIndexMeasurement({
  initial_investment,
  cash_flows,
  discount_rate,
  terminal_value = 0,
}) {
  const npvMeasurement = calculateNpvMeasurement({
    initial_investment,
    cash_flows,
    discount_rate,
    terminal_value,
  });

  const flags = [...npvMeasurement.flags];
  const series = buildCashflowSeries(initial_investment, cash_flows, terminal_value);
  if (countSignChanges(series) > 1) {
    flags.push("NON_NORMAL_FLOWS");
  }

  const pi = npvMeasurement.pv_inflows === null
    ? null
    : npvMeasurement.pv_inflows / Math.abs(initial_investment);

  return {
    pi: pi === null ? null : round(pi, 8),
    pv_inflows: npvMeasurement.pv_inflows,
    assumptions: [
      "Profitability Index is for ranking under capital rationing.",
      "PI does not override NPV for mutually exclusive decisions.",
    ],
    flags,
  };
}

export function calculateEmvMeasurement({ scenarios }) {
  const flags = [];
  if (!Array.isArray(scenarios) || scenarios.length === 0) {
    flags.push("INVALID_SCENARIOS");
    return {
      emv: null,
      total_probability: null,
      downside_probability: null,
      worst_outcome: null,
      best_outcome: null,
      variance: null,
      assumptions: [
        "EMV is a weighted scenario summary, not a standalone decision metric.",
      ],
      flags,
    };
  }

  for (const scenario of scenarios) {
    if (!scenario || !Number.isFinite(scenario.probability) || !Number.isFinite(scenario.outcome)) {
      flags.push("INVALID_SCENARIO");
      break;
    }
  }

  if (flags.length > 0) {
    return {
      emv: null,
      total_probability: null,
      downside_probability: null,
      worst_outcome: null,
      best_outcome: null,
      variance: null,
      assumptions: [
        "EMV is a weighted scenario summary, not a standalone decision metric.",
      ],
      flags,
    };
  }

  const totalProbability = scenarios.reduce((sum, scenario) => sum + scenario.probability, 0);
  if (Math.abs(totalProbability - 1) > 1e-6) {
    flags.push("PROBABILITY_MASS_INVALID");
  }

  const emv = scenarios.reduce((sum, scenario) => sum + scenario.probability * scenario.outcome, 0);
  const downsideProbability = scenarios
    .filter((scenario) => scenario.outcome < 0)
    .reduce((sum, scenario) => sum + scenario.probability, 0);
  const variance = scenarios.reduce((sum, scenario) => {
    const deviation = scenario.outcome - emv;
    return sum + scenario.probability * deviation * deviation;
  }, 0);

  return {
    emv: round(emv, 6),
    total_probability: round(totalProbability, 6),
    downside_probability: round(downsideProbability, 6),
    worst_outcome: round(Math.min(...scenarios.map((scenario) => scenario.outcome)), 6),
    best_outcome: round(Math.max(...scenarios.map((scenario) => scenario.outcome)), 6),
    variance: round(variance, 6),
    assumptions: [
      "EMV should be paired with downside probability and scenario dispersion.",
      "Scenario probabilities should sum to 1.0.",
    ],
    flags,
  };
}

export function calculatePaybackMeasurement({
  initial_investment,
  cash_flows,
  discount_rate = 0,
  period_unit = "annual",
}) {
  const flags = [
    ...validateSeries(initial_investment, cash_flows),
    ...validatePeriodicRate(discount_rate, "INVALID_DISCOUNT_RATE"),
  ];

  if (flags.length > 0) {
    return {
      payback_periods: null,
      discounted: discount_rate > 0,
      period_unit,
      assumptions: [
        "Payback is a liquidity metric, not a value metric.",
      ],
      flags,
    };
  }

  let remaining = Math.abs(initial_investment);
  let paybackPeriods = null;

  for (let index = 0; index < cash_flows.length; index += 1) {
    const rawCashflow = cash_flows[index];
    const adjustedCashflow = discount_rate > 0
      ? rawCashflow / Math.pow(1 + discount_rate, index + 1)
      : rawCashflow;

    if (adjustedCashflow <= 0) {
      continue;
    }
    if (remaining > adjustedCashflow) {
      remaining -= adjustedCashflow;
      continue;
    }

    paybackPeriods = index + (remaining / adjustedCashflow) + 1e-12;
    remaining = 0;
    break;
  }

  if (remaining > EPSILON) {
    flags.push("NOT_RECOVERED");
  }

  return {
    payback_periods: paybackPeriods === null ? null : round(paybackPeriods, 6),
    discounted: discount_rate > 0,
    period_unit,
    assumptions: [
      "Payback should only support, not replace, NPV.",
    ],
    flags,
  };
}

export function calculateDscrMeasurement({
  cfads,
  debt_service,
  ebitda,
  principal = 0,
  interest = 0,
  leases = 0,
  period_unit = "annual",
  input_epistemic = "CLAIM",
}) {
  const flags = [];
  const numerator = Number.isFinite(cfads) ? cfads : ebitda;
  const denominator = Number.isFinite(debt_service) ? debt_service : principal + interest + leases;

  if (!Number.isFinite(numerator)) {
    flags.push("INVALID_CFADS");
  }
  if (!Number.isFinite(denominator) || denominator <= 0) {
    flags.push("INVALID_DEBT_SERVICE");
  }
  if (!Number.isFinite(cfads) && Number.isFinite(ebitda)) {
    flags.push("EBITDA_PROXY_USED");
  }

  const dscr = flags.length > 0 ? null : numerator / denominator;

  if (dscr !== null && dscr < 1.0) {
    flags.push("LEVERAGE_DEFAULT");
  } else if (dscr !== null && dscr < 1.25) {
    flags.push("LEVERAGE_CRITICAL");
  }

  return {
    dscr: dscr === null ? null : round(dscr, 6),
    numerator: numerator ?? null,
    denominator: denominator ?? null,
    basis: Number.isFinite(cfads) ? "CFADS" : "EBITDA",
    period_unit,
    assumptions: [
      "DSCR should use CFADS when available.",
      "Minimum covenant floor defaults to 1.25x.",
    ],
    input_epistemic: String(input_epistemic).toUpperCase(),
    confidence_band: dscr === null ? null : deriveConfidenceBand(dscr, input_epistemic, "absolute-nonnegative"),
    flags,
  };
}
