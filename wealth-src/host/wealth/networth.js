const EPISTEMIC_ORDER = ["UNKNOWN", "HYPOTHESIS", "ESTIMATE", "PLAUSIBLE", "CLAIM"];

function weakestEpistemic(items = []) {
  let weakestIndex = EPISTEMIC_ORDER.length - 1;

  for (const item of items) {
    const tag = String(item?.tag ?? item?.epistemic ?? "CLAIM").toUpperCase();
    const index = EPISTEMIC_ORDER.indexOf(tag);
    if (index !== -1) {
      weakestIndex = Math.min(weakestIndex, index);
    }
  }

  return EPISTEMIC_ORDER[weakestIndex];
}

export function computeNetWorth(assets = [], liabilities = []) {
  const assetValue = assets.reduce((sum, a) => sum + (a.value ?? 0), 0);
  const liabilityValue = liabilities.reduce((sum, l) => sum + (l.outstanding ?? l.principal ?? 0), 0);
  const tag = weakestEpistemic([...assets, ...liabilities]);
  return {
    net_worth: assetValue - liabilityValue,
    assets: assetValue,
    liabilities: liabilityValue,
    tag,
    epistemic: tag,
    integrity_flags: [],
    vault_log_entry: { tool: "wealth_compute_networth", epoch: new Date().toISOString() },
    witness: { human: false, ai: true, earth: true },
  };
}

export function netWorthDelta(previousNetWorth, currentNetWorth, holdThreshold = -0.2) {
  const delta = currentNetWorth - previousNetWorth;
  const ratio = previousNetWorth === 0 ? null : delta / previousNetWorth;
  const hold = ratio !== null && ratio <= holdThreshold;

  return {
    previous_net_worth: previousNetWorth,
    current_net_worth: currentNetWorth,
    delta,
    delta_ratio: ratio,
    hold,
    hold_reason: hold ? "NET_WORTH_DROP_OVER_20_PERCENT" : null,
  };
}
