import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const runPython = (script) => {
  const result = spawnSync("python", ["-c", script], {
    cwd: "/root/WEALTH",
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(result.stderr || result.stdout);
  }
  return JSON.parse(result.stdout.trim());
};

test("ingest_sources lists available adapters", () => {
  const out = runPython(`
import json
from server import ingest_sources
r = ingest_sources()
print(json.dumps({"sources": r["primary_result"]["sources"], "verdict": r["governance_verdict"]}))
`);
  assert.ok(Array.isArray(out.sources));
  assert.ok(out.sources.includes("WorldBank"));
  assert.strictEqual(out.verdict, "SEAL");
});

test("ingest_fetch returns WorldBank GDP growth records for USA", () => {
  const out = runPython(`
import json
from server import ingest_fetch
r = ingest_fetch("WorldBank", "NY.GDP.MKTP.KD.ZG", "USA", use_cache=False)
print(json.dumps({"count": r["primary_result"]["count"], "verdict": r["governance_verdict"], "has_records": len(r["secondary_metrics"]["records"]) > 0}))
`);
  assert.ok(out.count > 0, `Expected records, got count=${out.count}`);
  assert.strictEqual(out.verdict, "SEAL");
  assert.strictEqual(out.has_records, true);
});

test("ingest_snapshot assembles multi-source snapshot for MYS", () => {
  const out = runPython(`
import json
from server import ingest_snapshot
r = ingest_snapshot("MYS", sources=["WorldBank", "OWID"])
print(json.dumps({"coverage": r["primary_result"]["coverage"], "verdict": r["governance_verdict"]}))
`);
  assert.ok(out.coverage >= 1, `Expected coverage >= 1, got ${out.coverage}`);
  assert.strictEqual(out.verdict, "SEAL");
});

test("DataRecord validation flags missing fields", () => {
  const out = runPython(`
import json
from host.ingest.schema import DataRecord, validate_record
r = DataRecord(source_system="", series_id="", entity_code="", observation_time="")
flags = validate_record(r)
print(json.dumps({"flags": flags}))
`);
  assert.ok(out.flags.includes("MISSING_SOURCE_SYSTEM"));
  assert.ok(out.flags.includes("MISSING_SERIES_ID"));
  assert.ok(out.flags.includes("MISSING_ENTITY_CODE"));
  assert.ok(out.flags.includes("MISSING_RETRIEVAL_TIME"));
});

test("ingest_fetch gracefully handles unknown source", () => {
  const out = runPython(`
import json
from server import ingest_fetch
r = ingest_fetch("UnknownSource", "XYZ", "USA")
print(json.dumps({"count": r["primary_result"]["count"], "flags": r["secondary_metrics"]["flags"]}))
`);
  assert.strictEqual(out.count, 0);
  assert.ok(out.flags.some(f => f.includes("ADAPTER_NOT_FOUND")));
});

test("ingest_health tracks adapter metrics", () => {
  const out = runPython(`
import json, os
health_path = "/root/WEALTH/data/ingest_health.json"
if os.path.exists(health_path):
    os.remove(health_path)
from server import ingest_fetch, ingest_health
# trigger a fetch to populate health
r = ingest_fetch("WorldBank", "NY.GDP.MKTP.KD.ZG", "USA")
h = ingest_health("WorldBank")
health = h["primary_result"]["health"]
print(json.dumps({"has_total": "total_requests" in health, "success": health.get("success_count", 0) >= 1}))
`);
  assert.strictEqual(out.has_total, true);
  assert.strictEqual(out.success, true);
});

test("ingest_reconcile returns divergence analysis", () => {
  const out = runPython(`
import json
from server import ingest_reconcile
r = ingest_reconcile("MYS")
print(json.dumps({"has_divergences": isinstance(r["primary_result"]["divergences"], list), "verdict": r["governance_verdict"]}))
`);
  assert.strictEqual(out.has_divergences, true);
  assert.strictEqual(out.verdict, "SEAL");
});

test("DataRecord supports vintage_id for FRED", () => {
  const out = runPython(`
import json
from host.ingest.schema import DataRecord
r = DataRecord(
    source_system="FRED",
    series_id="GDPC1",
    entity_code="USA",
    observation_time="2023-01-01",
    retrieval_time=DataRecord.now(),
    vintage_id="2023-07-27",
    revision_flag=True,
    value=20000.0,
    unit="Billions of Chained 2017 Dollars"
)
print(json.dumps({"vintage": r.vintage_id, "revision": r.revision_flag}))
`);
  assert.strictEqual(out.vintage, "2023-07-27");
  assert.strictEqual(out.revision, true);
});
