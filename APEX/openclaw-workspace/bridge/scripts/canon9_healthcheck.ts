#!/usr/bin/env tsx
/**
 * Canon 9 LLM roster health check
 * Tests each model slot via OpenRouter API.
 */

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(__dirname, "..");

interface Canon9Slot {
  slot: string;
  provider: string;
  modelId: string;
  role: string;
  costTier: string;
  enabled: boolean;
  description: string;
}

interface HealthResult {
  slot: string;
  modelId: string;
  status: "OK" | "FAIL" | "MISSING_KEY";
  error?: string;
  responseTimeMs?: number;
  provider?: string;
  timestamp: string;
}

async function loadEnvFiles() {
  const envFiles = [
    "/root/.env.openclaw",
    "/root/.env.master",
    "/root/.env.openrouter",
    path.join(ROOT, ".env"),
  ];
  const env: Record<string, string> = {};
  for (const file of envFiles) {
    try {
      const content = await fs.readFile(file, "utf8");
      const lines = content.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) continue;
        const eq = trimmed.indexOf("=");
        if (eq === -1) continue;
        const key = trimmed.slice(0, eq).trim();
        const value = trimmed.slice(eq + 1).trim();
        // Remove surrounding quotes
        const clean = value.replace(/^['"]|['"]$/g, "");
        env[key] = clean;
      }
    } catch (err) {
      // ignore missing files
    }
  }
  // Merge process.env (overwrites file values)
  for (const [key, value] of Object.entries(process.env)) {
    if (value) env[key] = value;
  }
  return env;
}

function maskKey(key: string | undefined): string {
  if (!key) return "***";
  if (key.length <= 8) return "***";
  return key.slice(0, 4) + "***" + key.slice(-4);
}

async function testModel(
  slot: Canon9Slot,
  apiKey: string,
): Promise<Omit<HealthResult, "timestamp">> {
  const start = Date.now();
  const fullModelId = slot.modelId; // e.g., "anthropic/claude-opus-4-5"
  const url = "https://openrouter.ai/api/v1/chat/completions";
  const payload = {
    model: fullModelId,
    messages: [
      {
        role: "user",
        content: "Reply with the exact word FORGED.",
      },
    ],
    max_tokens: 16,
    temperature: 0.1,
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://arifos.arif-fazil.com",
        "X-Title": "arifOS Canon9 Healthcheck",
      },
      signal: AbortSignal.timeout(15000),
      body: JSON.stringify(payload),
    });

    const elapsed = Date.now() - start;
    if (!response.ok) {
      let error = `HTTP ${response.status}`;
      try {
        const body = await response.text();
        if (body) error += `: ${body.slice(0, 200)}`;
      } catch {}
      return {
        slot: slot.slot,
        modelId: slot.modelId,
        status: "FAIL",
        error,
        responseTimeMs: elapsed,
        provider: slot.provider,
      };
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content || "";
    const ok = reply.toUpperCase().includes("FORGED");
    return {
      slot: slot.slot,
      modelId: slot.modelId,
      status: ok ? "OK" : "FAIL",
      error: ok ? undefined : `Unexpected reply: ${reply.slice(0, 100)}`,
      responseTimeMs: elapsed,
      provider: slot.provider,
    };
  } catch (err: any) {
    const elapsed = Date.now() - start;
    return {
      slot: slot.slot,
      modelId: slot.modelId,
      status: "FAIL",
      error: err.message || String(err),
      responseTimeMs: elapsed,
      provider: slot.provider,
    };
  }
}

async function testVeniceModel(
  slot: Canon9Slot,
  apiKey: string,
): Promise<Omit<HealthResult, "timestamp">> {
  const start = Date.now();
  const url = "https://api.venice.ai/api/v1/chat/completions";
  const payload: any = {
    model: slot.modelId,
    messages: [
      {
        role: "user",
        content: "Reply with the exact word FORGED.",
      },
    ],
    max_tokens: 16,
    temperature: 0.1,
  };
  // Add thinking budget for Claude Opus (required by Venice)
  if (slot.modelId.includes("claude-opus")) {
    payload.thinking = { enabled: true, budget_tokens: 1024 };
  }

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      signal: AbortSignal.timeout(15000),
      body: JSON.stringify(payload),
    });

    const elapsed = Date.now() - start;
    if (!response.ok) {
      let error = `HTTP ${response.status}`;
      try {
        const body = await response.text();
        if (body) error += `: ${body.slice(0, 200)}`;
      } catch {}
      return {
        slot: slot.slot,
        modelId: slot.modelId,
        status: "FAIL",
        error,
        responseTimeMs: elapsed,
        provider: slot.provider,
      };
    }

    const data = await response.json();
    const reply = data.choices?.[0]?.message?.content || "";
    const ok = reply.toUpperCase().includes("FORGED");
    return {
      slot: slot.slot,
      modelId: slot.modelId,
      status: ok ? "OK" : "FAIL",
      error: ok ? undefined : `Unexpected reply: ${reply.slice(0, 100)}`,
      responseTimeMs: elapsed,
      provider: slot.provider,
    };
  } catch (err: any) {
    const elapsed = Date.now() - start;
    return {
      slot: slot.slot,
      modelId: slot.modelId,
      status: "FAIL",
      error: err.message || String(err),
      responseTimeMs: elapsed,
      provider: slot.provider,
    };
  }
}

async function main() {
  console.log("🔍 Canon 9 health check starting...");
  const env = await loadEnvFiles();
  const openRouterKey = env.OPENROUTER_API_KEY;
  const veniceKey = env.VENICE_API_KEY;
  console.log(`   OPENROUTER_API_KEY: ${maskKey(openRouterKey)}`);
  console.log(`   VENICE_API_KEY: ${maskKey(veniceKey)}`);

  const canon9Path = path.join(ROOT, "canon9-models.json");
  const raw = await fs.readFile(canon9Path, "utf8");
  const data = JSON.parse(raw);
  const slots: Canon9Slot[] = data.slots;

  const results: HealthResult[] = [];
  for (const slot of slots) {
    if (!slot.enabled) {
      console.log(`   ⏭️  ${slot.slot} disabled, skipping`);
      continue;
    }
    console.log(`   Testing ${slot.slot} (${slot.modelId})...`);
    if (slot.provider === "openrouter") {
      if (!openRouterKey) {
        results.push({
          slot: slot.slot,
          modelId: slot.modelId,
          status: "MISSING_KEY",
          error: "OPENROUTER_API_KEY not found in environment",
          provider: slot.provider,
          timestamp: new Date().toISOString(),
        });
        continue;
      }
      const result = await testModel(slot, openRouterKey);
      results.push({ ...result, timestamp: new Date().toISOString() });
      console.log(`     ${result.status} ${result.error ? `- ${result.error}` : ""}`);
    } else if (slot.provider === "venice") {
      if (!veniceKey) {
        results.push({
          slot: slot.slot,
          modelId: slot.modelId,
          status: "MISSING_KEY",
          error: "VENICE_API_KEY not found in environment",
          provider: slot.provider,
          timestamp: new Date().toISOString(),
        });
        continue;
      }
      const result = await testVeniceModel(slot, veniceKey);
      results.push({ ...result, timestamp: new Date().toISOString() });
      console.log(`     ${result.status} ${result.error ? `- ${result.error}` : ""}`);
    } else {
      // future providers
      results.push({
        slot: slot.slot,
        modelId: slot.modelId,
        status: "FAIL",
        error: `Provider ${slot.provider} not yet supported`,
        provider: slot.provider,
        timestamp: new Date().toISOString(),
      });
    }
  }

  const logsDir = path.join(ROOT, "logs");
  await fs.mkdir(logsDir, { recursive: true });
  const outputPath = path.join(logsDir, "canon9_health.json");
  await fs.writeFile(outputPath, JSON.stringify(results, null, 2));
  console.log(`📊 Results written to ${outputPath}`);

  // Summary
  const ok = results.filter((r) => r.status === "OK").length;
  const fail = results.filter((r) => r.status === "FAIL").length;
  const missing = results.filter((r) => r.status === "MISSING_KEY").length;
  console.log(`\n📈 Summary: ${ok} OK, ${fail} FAIL, ${missing} MISSING_KEY`);
  if (missing > 0) {
    console.log("   Missing keys - check env vars: OPENROUTER_API_KEY, VENICE_API_KEY");
  }
  process.exit(fail + missing > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
