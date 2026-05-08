export function checkPlanetaryBoundaries(data = {}) {
  const { co2_concentration = 420, biosphere_integrity = 0.8, biogeochemical_flows = 0.5, land_system_change = 0.7, freshwater_use = 0.6 } = data;
  const status = { safe: true, critical: [] };
  if (co2_concentration > 450) { status.critical.push("co2_concentration"); status.safe = false; }
  return { safe: status.safe, critical: status.critical, timestamp: new Date().toISOString() };
}
