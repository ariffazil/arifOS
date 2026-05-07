#!/usr/bin/env node
/**
 * Post-install script for @arifos/mcp
 * Ensures arifosmcp Python package is installed
 */

const { execSync } = require('child_process');

console.log('[arifOS MCP] Checking Python environment...');

function findPython() {
  const commands = ['python3.12', 'python3', 'python', 'py'];

  for (const cmd of commands) {
    try {
      execSync(`${cmd} --version`, { stdio: 'ignore' });
      return cmd;
    } catch {
      continue;
    }
  }

  console.warn('[arifOS MCP] Warning: Python not found. Please install Python 3.12+ and arifosmcp:');
  console.warn('  https://python.org');
  console.warn('  pip install arifosmcp');
  process.exit(0);
}

function checkArifOS(python) {
  try {
    execSync(`${python} -c "import arifosmcp"`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

try {
  const python = findPython();

  if (!checkArifOS(python)) {
    console.log('[arifOS MCP] Installing arifosmcp Python package...');
    try {
      execSync(`${python} -m pip install arifosmcp`, {
        stdio: 'inherit',
        timeout: 300000
      });
      console.log('[arifOS MCP] Installation complete!');
    } catch (err) {
      console.error('[arifOS MCP] Failed to install. Please run manually:');
      console.error('  pip install arifosmcp');
    }
  } else {
    console.log('[arifOS MCP] arifosmcp is already installed.');
  }
} catch (err) {
  console.error('[arifOS MCP] Error during install:', err.message);
}
