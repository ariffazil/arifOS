import { createHash } from "node:crypto";
import { mkdirSync, appendFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

export function initVault999(filePath = resolve(process.cwd(), "data", "vault999.jsonl")) {
  mkdirSync(dirname(filePath), { recursive: true });
  return { path: filePath };
}

export function appendVault999(record, vault = initVault999()) {
  const epoch = record.epoch ?? new Date().toISOString();
  const payload = {
    ...record,
    epoch,
    vault_seal: "VAULT999",
  };
  const integrity = createHash("sha256").update(JSON.stringify(payload)).digest("hex").slice(0, 16);
  const entry = {
    ...payload,
    integrity,
  };

  appendFileSync(vault.path, `${JSON.stringify(entry)}\n`);
  return entry;
}
