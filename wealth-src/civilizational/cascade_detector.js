export function detectSystemicRisk(domains = {}) {
  const { markets = { risk: 0.2 }, energy = { risk: 0.3 }, food = { risk: 0.2 } } = domains;
  let totalRisk = (markets.risk * 0.3) + (energy.risk * 0.4) + (food.risk * 0.3);
  return { systemic_risk_score: totalRisk, hold_triggered: totalRisk > 0.6, timestamp: new Date().toISOString() };
}
