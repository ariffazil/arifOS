#!/usr/bin/env node
/**
 * WEALTH CLI — Layer 1 Runnable Kernel + Minimal Layer 2
 * Commands: boot | check | seal | capitalx
 * DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
 */

import { checkFloors, EPISTEMIC } from './src/kernel/floors.js';
import { seal999 } from './src/kernel/seal.js';
import { emitTelemetry } from './src/kernel/telemetry.js';
import { initVault999, appendVault999 } from './src/kernel/vault999.js';
import { calculateRiskAdjustedRate } from './src/kernel/capitalx.js';

const [,, cmd, ...args] = process.argv;
const vault = initVault999();

function usage() {
  console.log(`Usage: node cli.js <boot|check|seal|capitalx> [args]`);
  console.log(`  boot                    — Boot WEALTH OS and emit telemetry`);
  console.log(`  check '<json>'          — Run floor check on an operation`);
  console.log(`  seal '<json>'           — Attempt 999 SEAL on a state`);
  console.log(`  capitalx <baseRate> '<signals>' — Calculate risk-adjusted rate`);
  process.exit(1);
}

async function main() {
  switch (cmd) {
    case 'boot': {
      console.log('🔱 WEALTH OS booted. 999 SEAL ALIVE.');
      const telemetry = await emitTelemetry({
        sealed: true,
        peace2: 1.0,
        confidence: 0.92,
        holds: [],
        violations: [],
      });
      appendVault999({ event: 'BOOT', telemetry }, vault);
      console.log(JSON.stringify(telemetry, null, 2));
      break;
    }

    case 'check': {
      const op = JSON.parse(args[0] || '{}');
      const result = checkFloors(op);
      console.log(JSON.stringify(result, null, 2));
      appendVault999({ event: 'FLOOR_CHECK', op, result }, vault);
      break;
    }

    case 'seal': {
      const state = JSON.parse(args[0] || '{}');
      const sealed = await seal999(state);
      console.log(JSON.stringify(sealed, null, 2));
      appendVault999({ event: 'SEAL', state, sealed }, vault);
      break;
    }

    case 'capitalx': {
      const [baseRate, signalsJson] = args;
      if (!baseRate) usage();
      const signals = JSON.parse(signalsJson || '{}');
      const result = calculateRiskAdjustedRate(parseFloat(baseRate), signals);
      console.log(JSON.stringify(result, null, 2));
      appendVault999({ event: 'CAPITALX', baseRate, signals, result }, vault);
      break;
    }

    default:
      usage();
  }
}

main().catch((e) => {
  console.error('[WEALTH ERROR]', e.message);
  process.exit(1);
});
