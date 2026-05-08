export function computeCivilizationalProsperityIndex(params = {}) {
  const {
    gdp_per_capita_growth = 0,
    employment_quality = 0.5,
    income_inequality_gini = 0.3,
    energy_access = 0.5,
    renewable_share = 0.3,
    price_stability = 0.5,
    food_security = 0.5,
    agricultural_resilience = 0.5,
    nutrition_quality = 0.5,
    water_security = 0.5,
    sanitation_access = 0.5,
    institutional_integrity = 0.5,
    rule_of_law = 0.5,
    social_cohesion = 0.5,
  } = params;

  const economicProsperity = (gdp_per_capita_growth + employment_quality + (1 - income_inequality_gini)) / 3;
  const energySecurity = (energy_access + renewable_share + price_stability) / 3;
  const foodSecurityScore = (food_security + agricultural_resilience + nutrition_quality) / 3;
  const waterSecurityScore = (water_security + sanitation_access) / 2;
  const governanceQuality = (institutional_integrity + rule_of_law + social_cohesion) / 3;

  const score = (economicProsperity * 0.25) + (energySecurity * 0.20) + (foodSecurityScore * 0.20) + (waterSecurityScore * 0.15) + (governanceQuality * 0.20);
  const rounded = Math.round(score * 100) / 100;

  return {
    score: rounded,
    dimensions: {
      economic: Number(economicProsperity.toFixed(4)),
      energy: Number(energySecurity.toFixed(4)),
      food: Number(foodSecurityScore.toFixed(4)),
      water: Number(waterSecurityScore.toFixed(4)),
      governance: Number(governanceQuality.toFixed(4)),
    },
    floor: 0.6,
    below_floor: score < 0.6,
    hold_triggered: score < 0.6,
    epoch: new Date().toISOString(),
  };
}
