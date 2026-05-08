import test from 'node:test';
import assert from 'node:assert/strict';
import { checkFloors, EPISTEMIC } from '../src/kernel/floors.js';
import { seal999 } from '../src/kernel/seal.js';
import { initVault999, appendVault999 } from '../src/kernel/vault999.js';
import { calculateRiskAdjustedRate, compareCapitalAdvantage } from '../src/kernel/capitalx.js';
import { computeNetWorth, netWorthDelta } from '../src/wealth/networth.js';
import { computeCashflow } from '../src/wealth/cashflow.js';
import { computeMaruahScore } from '../src/wealth/maruah-score.js';
import { projectCompoundGrowth } from '../src/wealth/projection.js';
import { tmpdir } from 'node:os';
import { resolve } from 'node:path';

test('checkFloors passes valid operation', () => {
  const result = checkFloors({ type: 'TEST', reversible: true, epistemic: EPISTEMIC.CLAIM });
  assert.strictEqual(result.pass, true);
});

test('checkFloors triggers 888 HOLD on irreversible action', () => {
  const result = checkFloors({ type: 'TEST', reversible: false });
  assert.strictEqual(result.pass, false);
  assert.ok(result.holds.some(h => h.includes('888')));
});

test('netWorthDelta triggers hold on >20% drop', () => {
  const result = netWorthDelta(100000, 75000);
  assert.strictEqual(result.hold, true);
});

test('computeMaruahScore below floor triggers hold', () => {
  const result = computeMaruahScore({
    financial_integrity: 0.3,
    sovereignty: 0.3,
    debt_dignity: 0.3,
    amanah_index: 0.3,
  });
  assert.strictEqual(result.below_floor, true);
  assert.strictEqual(result.hold_triggered, true);
});

test('projectCompoundGrowth returns ESTIMATE tag', () => {
  const result = projectCompoundGrowth(1000, 0.07, 10);
  assert.strictEqual(result.tag, EPISTEMIC.ESTIMATE);
  assert.ok(result.result.low < result.result.mid);
  assert.ok(result.result.mid < result.result.high);
});

test('capitalx reduces rate for high maruah and peace', () => {
  const result = calculateRiskAdjustedRate(0.05, {
    dS: 0,
    peace2: 1.2,
    maruahScore: 0.95,
    trustIndex: 0.9,
    deltaCiv: 0.2,
  });
  assert.ok(result.adjusted_rate < result.base_rate);
});

test('capitalx advantage comparison returns positive bps for virtuous node', () => {
  const wealthSignals = { dS: 0, peace2: 1.2, maruahScore: 0.95, trustIndex: 0.9, deltaCiv: 0.2 };
  const extractiveSignals = { dS: 0.4, peace2: 0.8, maruahScore: 0.4, trustIndex: 0.3, deltaCiv: -0.1 };
  const result = compareCapitalAdvantage(0.05, wealthSignals, extractiveSignals);
  assert.ok(result.advantage_bps > 0);
});

test('vault999 appends immutable record', () => {
  const vault = initVault999(resolve(tmpdir(), `vault999-${Date.now()}.jsonl`));
  const entry = appendVault999({ test: true }, vault);
  assert.strictEqual(entry.vault_seal, 'VAULT999');
  assert.ok(entry.integrity);
  assert.ok(entry.epoch);
});

test('seal999 blocks when floors fail', async () => {
  const sealed = await seal999({ peace2: 0.5, holds: [], violations: [] });
  assert.strictEqual(sealed.sealed, false);
  assert.strictEqual(sealed.verdict, '888-HOLD');
});

test('seal999 passes when floors pass', async () => {
  const sealed = await seal999({ peace2: 1.0, holds: [], violations: [] });
  assert.strictEqual(sealed.sealed, true);
  assert.strictEqual(sealed.verdict, 'SEALED');
  assert.ok(sealed.telemetry);
});

test('computeCashflow tags speculative income as HYPOTHESIS', () => {
  const income = [{ monthly_amount: 1000, reliability: 'speculative' }];
  const result = computeCashflow(income, [], 5000);
  assert.strictEqual(result.tag, EPISTEMIC.HYPOTHESIS);
});

test('computeCashflow tags irregular income as ESTIMATE', () => {
  const income = [{ monthly_amount: 1000, reliability: 'irregular' }];
  const result = computeCashflow(income, [], 5000);
  assert.strictEqual(result.tag, EPISTEMIC.ESTIMATE);
});
