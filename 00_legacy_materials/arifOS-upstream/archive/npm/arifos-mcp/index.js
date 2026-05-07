#!/usr/bin/env node
/**
 * arifOS MCP Server - npm entry point
 *
 * The world's first production-grade Constitutional AI Governance System.
 * 13 stationary floors (F1-F13), Trinity Architecture (ΔΩΨ), VAULT999 ledger.
 *
 * @version 2026.3.14
 * @author Muhammad Arif bin Fazil
 * @license AGPL-3.0-only
 */

const { spawn } = require('child_process');
const path = require('path');

// Find Python executable
async function findPython() {
  // Try common Python commands
  const commands = ['python3.12', 'python3', 'python', 'py'];

  for (const cmd of commands) {
    try {
      const { execSync } = require('child_process');
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      return cmd;
    } catch {
      continue;
    }
  }

  throw new Error(
    'Python 3.12+ is required but not found.\n' +
    'Please install Python: https://python.org\n' +
    'Then install arifosmcp: pip install arifosmcp'
  );
}

// Check if arifosmcp is installed
async function checkArifOS() {
  const { execSync } = require('child_process');
  const python = await findPython();

  try {
    execSync(`${python} -c "import arifosmcp"`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

// Main entry
async function main() {
  const args = process.argv.slice(2);
  const mode = args[0] || 'stdio';

  console.error('╔════════════════════════════════════════════════════════════╗');
  console.error('║  arifOS MCP Server - Constitutional AI Governance          ║');
  console.error('║  Version: 2026.3.14-VALIDATED                              ║');
  console.error('║  ΔΩΨ Trinity Architecture                                  ║');
  console.error('║  DITEMPA BUKAN DIBERI — Forged, Not Given                  ║');
  console.error('╚════════════════════════════════════════════════════════════╝');

  try {
    const python = await findPython();

    // Check arifosmcp installation
    const hasArifOS = await checkArifOS();
    if (!hasArifOS) {
      console.error('\n[arifOS MCP] Installing arifosmcp Python package...');
      const { execSync } = require('child_process');
      try {
        execSync(`${python} -m pip install arifosmcp`, {
          stdio: 'inherit',
          timeout: 300000
        });
      } catch (err) {
        console.error('[arifOS MCP] Failed to install arifosmcp. Please install manually:');
        console.error('  pip install arifosmcp');
        process.exit(1);
      }
    }

    // Spawn the Python MCP server
    const proc = require('child_process').spawn(python, ['-m', 'arifosmcp.runtime', mode], {
      stdio: ['inherit', 'inherit', 'inherit'],
      env: {
        ...process.env,
        ARIFOS_PUBLIC_TOOL_PROFILE: process.env.ARIFOS_PUBLIC_TOOL_PROFILE || 'full',
        ARIFOS_ENV: process.env.ARIFOS_ENV || 'production'
      }
    });

    proc.on('exit', (code) => {
      process.exit(code);
    });

    proc.on('error', (err) => {
      console.error('[arifOS MCP] Error:', err.message);
      process.exit(1);
    });

  } catch (err) {
    console.error('[arifOS MCP] Fatal:', err.message);
    process.exit(1);
  }
}

main();
