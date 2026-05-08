const RELIABILITY_TO_TAG = {
  guaranteed: "CLAIM",
  regular: "PLAUSIBLE",
  irregular: "ESTIMATE",
  speculative: "HYPOTHESIS",
};

const EPISTEMIC_ORDER = ["UNKNOWN", "HYPOTHESIS", "ESTIMATE", "PLAUSIBLE", "CLAIM"];

function weakestTag(items = []) {
  if (items.length === 0) {
    return "UNKNOWN";
  }

  let weakestIndex = EPISTEMIC_ORDER.length - 1;
  for (const item of items) {
    const reliability = String(item?.reliability ?? "").toLowerCase();
    const candidate = String(item?.tag ?? RELIABILITY_TO_TAG[reliability] ?? "CLAIM").toUpperCase();
    const index = EPISTEMIC_ORDER.indexOf(candidate);
    if (index !== -1) {
      weakestIndex = Math.min(weakestIndex, index);
    }
  }
  return EPISTEMIC_ORDER[weakestIndex];
}

export function computeCashflow(income = [], expenses = [], liquidAssets = 0) {
  const activeIncome = income.filter((item) => item.active !== false);
  const activeExpenses = expenses.filter((item) => item.active !== false);
  const totalIncome = activeIncome.reduce((sum, i) => sum + (i.monthly_amount ?? 0), 0);
  const totalExpenses = activeExpenses.reduce((sum, e) => sum + (e.monthly_amount ?? 0), 0);
  const net = totalIncome - totalExpenses;
  const burnRate = net < 0 ? -net : 0;
  const runwayMonths = burnRate > 0
    ? Number((liquidAssets / burnRate).toFixed(1))
    : Number.POSITIVE_INFINITY;
  const tag = weakestTag([...activeIncome, ...activeExpenses]);
  const integrityFlags = [];

  if (burnRate > 0 && runwayMonths < 3) {
    integrityFlags.push("RUNWAY_CRITICAL");
  }

  return {
    monthly_income: totalIncome,
    monthly_expenses: totalExpenses,
    net_monthly: net,
    runway_months: runwayMonths,
    burn_rate: burnRate,
    liquid_assets: liquidAssets,
    tag,
    epistemic: tag,
    integrity_flags: integrityFlags,
    vault_log_entry: { tool: "wealth_compute_cashflow", epoch: new Date().toISOString() },
    witness: { human: false, ai: true, earth: true },
  };
}
