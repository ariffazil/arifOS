#!/usr/bin/env node
/**
 * Minimal MCP smoke test for the canonical WEALTH kernel (`server.py`).
 */

import { spawn } from "node:child_process";
import { resolve } from "node:path";

const SERVER_PATH = resolve(import.meta.dirname, "../server.py");

let nextId = 1;
let buffer = "";
const pending = new Map();

function req(id, method, params) {
  return JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n";
}

const child = spawn("python", [SERVER_PATH], { stdio: ["pipe", "pipe", "pipe"] });

function send(method, params) {
  const id = nextId++;
  child.stdin.write(req(id, method, params));
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
  });
}

child.stdout.on("data", (chunk) => {
  buffer += chunk.toString("utf8");
  const lines = buffer.split("\n");
  buffer = lines.pop() ?? "";

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const msg = JSON.parse(line);
      if (msg.id !== undefined && pending.has(msg.id)) {
        pending.get(msg.id).resolve(msg);
        pending.delete(msg.id);
      }
    } catch {
      // ignore non-JSON lines from server startup noise
    }
  }
});

child.stderr.on("data", () => {
  // keep stderr quiet for a simple smoke pass
});

async function main() {
  const init = await send("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "wealth-smoke", version: "1.0.0" }
  });

  const tools = await send("tools/list", {});

  const wealthInit = await send("tools/call", {
    name: "wealth_init",
    arguments: {
      session_id: "wealth-smoke-session",
      actor_id: "copilot-cli",
      intent: "repo-sot-smoke"
    }
  });

  const npv = await send("tools/call", {
    name: "wealth_npv_reward",
    arguments: {
      initial_investment: 100000,
      cash_flows: [30000, 40000, 50000],
      discount_rate: 0.1
    }
  });

  const floors = await send("tools/call", {
    name: "wealth_check_floors",
    arguments: {
      reversible: true,
      human_confirmed: true,
      epistemic: "CLAIM",
      peace2: 1.0,
      maruah_score: 0.8,
      operation_type: "PROJECTION",
      task_definition: "WEALTH MCP smoke test"
    }
  });

  const summary = {
    initialized: !init.error,
    listed_tools: tools.result?.tools?.length ?? null,
    wealth_init_ok: !wealthInit.error,
    npv_ok: !npv.error,
    floors_ok: !floors.error
  };

  console.log(JSON.stringify(summary, null, 2));
  child.kill();
}

main().catch((error) => {
  console.error(error);
  child.kill();
  process.exitCode = 1;
});
