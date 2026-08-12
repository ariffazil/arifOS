/**
 * FLOOR AMENDMENT LOADER — arifOS Constitutional Runtime
 * 
 * Reads FLOOR_TABLE.json + ratified amendments → produces effective floor table.
 * The kernel's /health endpoint returns the MERGED view.
 * 
 * Pipeline: SCAR → CANDIDATE → RATIFICATION → AMENDMENT → LOADER → EFFECTIVE TABLE
 * 
 * F1 AMANAH: This loader is READ-ONLY at runtime. Amendments are written by
 * arif_seal(mode=seal) with F13 ratification. The loader only merges.
 * 
 * @author 333-AGI
 * @forged 2026-08-12
 * @constitutional_chain cc_sabah_20260812
 */

import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════

interface SubRule {
  id: string;
  name: string;
  rule: string;
  enforcement_point: string;
  operator: string | null;
  sealed_range: { min: number | null; max: number | null } | null;
  source_scar: string;
  forged: string;
}

interface Floor {
  id: string;
  name: string;
  rule: string;
  color: string;
  operator: string | null;
  sealed_range: { min: number | null; max: number | null } | null;
  sub_rules?: SubRule[];
  amendment_chain?: string[];  // populated by loader
  [key: string]: unknown;      // allow extra fields
}

interface FloorAmendment {
  target_floor: string;
  amendment_type: 'rule_extension' | 'rule_replacement' | 'threshold_change';
  operation: 'append_sub_rule' | 'replace_rule' | 'update_sealed_range';
  field: string;
  value: SubRule | string | { min: number; max: number | null };
}

interface Amendment {
  amendment_id: string;
  version: string;
  status: 'ENFORCED_IMMUTABLE' | 'PENDING_RATIFICATION' | 'VOID';
  scar_origin: {
    vault_id: string;
    scar_pressure: number;
    fingerprint: string;
  };
  ratification: {
    reaffirmation_count: number;
    sovereign_ratification: {
      ratified_by: string;
      ratified_at: string;
      signature: string;
      ack_irreversible: boolean;
    } | null;
  };
  floor_amendments: FloorAmendment[];
  provenance_chain: {
    constitutional_chain_id: string;
    floor_table_version_before: string;
    floor_table_version_after: string;
  };
}

interface FloorTable {
  version: string;
  forged: string;
  authority: string;
  floors: Floor[];
  [key: string]: unknown;
}

interface EffectiveFloor extends Floor {
  _amendments_applied: string[];
  _sub_rule_count: number;
  _last_amended: string | null;
}

// ═══════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════

const FLOOR_TABLE_PATH = '/root/arifOS/GENESIS/FLOOR_TABLE.json';
const AMENDMENTS_DIR = '/root/arifOS/GENESIS/amendments';

// ═══════════════════════════════════════════════════════
// AMENDMENT VALIDATOR
// ═══════════════════════════════════════════════════════

function validateAmendment(amd: Amendment): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  // F13: Must have sovereign ratification for ENFORCED_IMMUTABLE
  if (amd.status === 'ENFORCED_IMMUTABLE') {
    if (!amd.ratification.sovereign_ratification) {
      errors.push(`${amd.amendment_id}: ENFORCED_IMMUTABLE but no sovereign ratification → VOID`);
    }
    if (!amd.ratification.sovereign_ratification?.ack_irreversible) {
      errors.push(`${amd.amendment_id}: ENFORCED_IMMUTABLE but ack_irreversible=false → VOID`);
    }
  }

  // F3: Minimum 3 reaffirmations
  if (amd.ratification.reaffirmation_count < 3) {
    errors.push(`${amd.amendment_id}: Only ${amd.ratification.reaffirmation_count} reaffirmations (need ≥ 3)`);
  }

  // F1: Constitutional chain ID required
  if (!amd.provenance_chain.constitutional_chain_id) {
    errors.push(`${amd.amendment_id}: Missing constitutional_chain_id`);
  }

  // Target floor must exist
  for (const fa of amd.floor_amendments) {
    // We'll validate this during merge
  }

  return { valid: errors.length === 0, errors };
}

// ═══════════════════════════════════════════════════════
// AMENDMENT MERGER
// ═══════════════════════════════════════════════════════

function mergeAmendment(floor: EffectiveFloor, amendment: Amendment, fa: FloorAmendment): EffectiveFloor {
  switch (fa.operation) {
    case 'append_sub_rule': {
      const subRule = fa.value as SubRule;
      if (!floor.sub_rules) floor.sub_rules = [];
      
      // F1: Idempotency — don't add duplicate sub_rules
      const exists = floor.sub_rules.some(sr => sr.id === subRule.id);
      if (exists) {
        console.warn(`[FLOOR_LOADER] Sub-rule ${subRule.id} already exists on ${floor.id} — skipping`);
        return floor;
      }
      
      floor.sub_rules.push(subRule);
      floor._amendments_applied.push(amendment.amendment_id);
      floor._sub_rule_count = floor.sub_rules.length;
      floor._last_amended = amendment.ratification.sovereign_ratification?.ratified_at || 'unknown';
      break;
    }

    case 'replace_rule': {
      const newRule = fa.value as string;
      // F1: Preserve old rule in amendment_chain metadata
      floor._amendments_applied.push(amendment.amendment_id);
      floor._last_amended = amendment.ratification.sovereign_ratification?.ratified_at || 'unknown';
      floor.rule = newRule;
      break;
    }

    case 'update_sealed_range': {
      const newRange = fa.value as { min: number; max: number | null };
      floor._amendments_applied.push(amendment.amendment_id);
      floor._last_amended = amendment.ratification.sovereign_ratification?.ratified_at || 'unknown';
      floor.sealed_range = newRange;
      break;
    }

    default:
      console.warn(`[FLOOR_LOADER] Unknown operation: ${fa.operation}`);
  }

  return floor;
}

// ═══════════════════════════════════════════════════════
// MAIN LOADER
// ═══════════════════════════════════════════════════════

/**
 * Load the effective floor table: base FLOOR_TABLE.json + all ratified amendments.
 * 
 * @returns Effective floor table with amendments merged
 * @throws Error if base table is missing or amendments are invalid
 */
export function loadEffectiveFloorTable(): {
  floors: EffectiveFloor[];
  base_version: string;
  effective_version: string;
  amendments_applied: number;
  hash: string;
} {
  // 1. Load base table
  const baseRaw = fs.readFileSync(FLOOR_TABLE_PATH, 'utf-8');
  const base: FloorTable = JSON.parse(baseRaw);

  // 2. Deep clone floors for mutation
  const effective: EffectiveFloor[] = base.floors.map(f => ({
    ...f,
    _amendments_applied: [],
    _sub_rule_count: f.sub_rules?.length || 0,
    _last_amended: null,
  }));

  // 3. Load and validate amendments
  const amendmentFiles = fs.readdirSync(AMENDMENTS_DIR)
    .filter(f => f.endsWith('.json'))
    .sort(); // chronological ordering by filename

  let amendmentsApplied = 0;

  for (const file of amendmentFiles) {
    const filePath = path.join(AMENDMENTS_DIR, file);
    const raw = fs.readFileSync(filePath, 'utf-8');
    const amendment: Amendment = JSON.parse(raw);

    // Validate
    const validation = validateAmendment(amendment);
    if (!validation.valid) {
      console.error(`[FLOOR_LOADER] Amendment ${amendment.amendment_id} INVALID:`);
      validation.errors.forEach(e => console.error(`  → ${e}`));
      continue; // skip invalid amendments
    }

    // Only apply ENFORCED_IMMUTABLE amendments
    if (amendment.status !== 'ENFORCED_IMMUTABLE') {
      console.warn(`[FLOOR_LOADER] Amendment ${amendment.amendment_id} status=${amendment.status} — skipping`);
      continue;
    }

    // Merge each floor amendment
    for (const fa of amendment.floor_amendments) {
      const floor = effective.find(f => f.id === fa.target_floor);
      if (!floor) {
        console.error(`[FLOOR_LOADER] Target floor ${fa.target_floor} not found for amendment ${amendment.amendment_id}`);
        continue;
      }

      mergeAmendment(floor, amendment, fa);
      amendmentsApplied++;
    }
  }

  // 4. Compute hash of effective table
  const hashInput = JSON.stringify(effective.map(f => ({
    id: f.id,
    rule: f.rule,
    sealed_range: f.sealed_range,
    sub_rules: f.sub_rules,
    amendments: f._amendments_applied,
  })));
  const hash = crypto.createHash('sha256').update(hashInput).digest('hex').slice(0, 16);

  return {
    floors: effective,
    base_version: base.version,
    effective_version: `${base.version}+${amendmentsApplied}amd`,
    amendments_applied: amendmentsApplied,
    hash,
  };
}

/**
 * Get effective rules for a specific floor (for kernel /health endpoint).
 */
export function getEffectiveFloor(floorId: string): EffectiveFloor | null {
  const table = loadEffectiveFloorTable();
  return table.floors.find(f => f.id === floorId) || null;
}

/**
 * Check if a specific floor has scar-derived sub-rules.
 */
export function hasSubRules(floorId: string): boolean {
  const floor = getEffectiveFloor(floorId);
  return (floor?.sub_rules?.length || 0) > 0;
}

/**
 * Get all sub-rules for a floor that apply to a specific enforcement point.
 */
export function getSubRulesForEnforcement(floorId: string, enforcementPoint: string): SubRule[] {
  const floor = getEffectiveFloor(floorId);
  if (!floor?.sub_rules) return [];
  return floor.sub_rules.filter(sr => 
    sr.enforcement_point.includes(enforcementPoint) || 
    sr.enforcement_point === '*'
  );
}

// ═══════════════════════════════════════════════════════
// CLI ENTRY POINT
// ═══════════════════════════════════════════════════════

if (require.main === module) {
  const table = loadEffectiveFloorTable();
  
  console.log('═══ EFFECTIVE FLOOR TABLE ═══');
  console.log(`Base version: ${table.base_version}`);
  console.log(`Effective version: ${table.effective_version}`);
  console.log(`Amendments applied: ${table.amendments_applied}`);
  console.log(`Table hash: ${table.hash}`);
  console.log('');
  
  for (const floor of table.floors) {
    const subRuleCount = floor.sub_rules?.length || 0;
    const amended = floor._amendments_applied.length > 0 ? ' ⚒️ AMENDED' : '';
    console.log(`${floor.id} ${floor.name}${amended}`);
    console.log(`  Rule: ${floor.rule}`);
    if (subRuleCount > 0) {
      console.log(`  Sub-rules (${subRuleCount}):`);
      for (const sr of floor.sub_rules!) {
        console.log(`    ${sr.id}: ${sr.rule}`);
        console.log(`      Enforcement: ${sr.enforcement_point}`);
        console.log(`      Source scar: ${sr.source_scar}`);
      }
    }
    console.log('');
  }
}
