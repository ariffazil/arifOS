export function calculateRiskAdjustedRate(base_rate, signals, opts = {}) {
  const flags = [];

  if (!Number.isFinite(base_rate) || base_rate < 0) {
    flags.push("INVALID_BASE_RATE");
  }

  let deltaCiv = signals.deltaCiv ?? 0;
  const wealth_basis = opts.wealth_basis ?? signals.wealth_basis ?? null;
  const defects = opts.defects ?? signals.defects ?? null;

  if (wealth_basis && defects) {
    const { e_hat, s_hat, echo_hat } = wealth_basis;
    const { paradox, scar, shadow } = defects;
    deltaCiv =
      0.2 * Math.log1p(e_hat) +
      0.3 * (1 - s_hat) +
      0.25 * echo_hat -
      0.15 * paradox -
      0.2 * scar -
      0.1 * shadow;
  }

  const entropyPenalty = Math.max(0, (signals.dS ?? 0) * 0.5);
  const peaceDiscount = Math.min(0.02, Math.max(0, ((signals.peace2 ?? 1.0) - 1.0) * 0.05));
  const maruahDiscount = Math.min(0.03, Math.max(0, ((signals.maruahScore ?? 0.5) - 0.5) * 0.06));
  const trustDiscount = Math.min(0.02, Math.max(0, ((signals.trustIndex ?? 0.5) - 0.5) * 0.04));
  const civDiscount = Math.min(0.02, Math.max(0, deltaCiv * 0.1));

  const raw_r_adj =
    base_rate +
    entropyPenalty -
    peaceDiscount -
    maruahDiscount -
    trustDiscount -
    civDiscount;

  const r_adj = Math.max(0, Number(raw_r_adj.toFixed(6)));
  const clamped = r_adj !== Number(raw_r_adj.toFixed(6));
  if ((signals.dS ?? 0) > 0.3) flags.push("HIGH_ENTROPY_SIGNAL");
  if ((signals.maruahScore ?? 0.5) < 0.6) flags.push("SOVEREIGN_DIGNITY_LOW");
  if (clamped) flags.push("RATE_CLAMP_TRIGGERED");

  const shadow = defects?.shadow ?? 0;
  const uncertaintyRadius = Number((0.01 + shadow * 0.05 + (signals.dS ?? 0) * 0.02).toFixed(6));
  const uncertainty_band = [
    Math.max(0, Number((r_adj - uncertaintyRadius).toFixed(6))),
    Number((r_adj + uncertaintyRadius).toFixed(6)),
  ];

  return {
    base_rate: Number(base_rate.toFixed(6)),
    adjusted_rate: r_adj,
    r_adj,
    adjustments: {
      entropy_penalty: Number(entropyPenalty.toFixed(6)),
      peace_discount: Number(peaceDiscount.toFixed(6)),
      maruah_discount: Number(maruahDiscount.toFixed(6)),
      trust_discount: Number(trustDiscount.toFixed(6)),
      civ_discount: Number(civDiscount.toFixed(6)),
    },
    anomaly: clamped ? "RATE_CLAMP_TRIGGERED" : undefined,
    integrity_flags: flags,
    uncertainty_band,
    epistemic: "ESTIMATE",
    assumptions: [
      "CapitalX pricing is an estimate layered on top of the base rate.",
      "If entropy or shadow rises, r_adj must not decrease.",
    ],
    vault_log_entry: { tool: "wealth_price_capitalx", epoch: new Date().toISOString() },
    witness: { human: false, ai: true, earth: true },
  };
}

export function compareCapitalAdvantage(base_rate, wealth_signals, extractive_signals) {
  const wealth = calculateRiskAdjustedRate(base_rate, wealth_signals);
  const extractive = calculateRiskAdjustedRate(base_rate, extractive_signals);
  const advantage_bps = Math.round((extractive.r_adj - wealth.r_adj) * 10000);
  return {
    base_rate: Number(base_rate.toFixed(6)),
    wealth_r_adj: wealth.r_adj,
    extractive_r_adj: extractive.r_adj,
    advantage_bps,
    integrity_flags: [
      ...(wealth.integrity_flags ?? []),
      ...(extractive.integrity_flags ?? []),
    ],
    epistemic: "ESTIMATE",
    vault_log_entry: { tool: "wealth_capitalx_compare", epoch: new Date().toISOString() },
    witness: { human: false, ai: true, earth: true },
  };
}
