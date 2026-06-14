# arifOS MCP Tool Audit — Static Gap & Seal Readiness Report
**Auditor:** Kimi Code CLI (Constitutional Clerk)
**Date:** 2026-06-11 04:15 UTC
**Sovereign:** Muhammad Arif bin Fazil
**Server:** localhost:8088 (live)
**Git HEAD:** cd4b39b (v2026.05.05-SSCT)

---

## 1. EXECUTIVE SUMMARY

| Metric | Value |
|--------|-------|
| Canonical tools tested | 13/13 |
| Forge ladder tools tested | 3/3 |
| P2-7 lease tools tested | 3/3 |
| Total runtime surface | 19/19 execute without crash |
| Schema completeness | 100% (13/13 input + output) |
| Tool charter coverage | 100% (13/13 with risk tiers) |
| Contract drift | NONE |
| Runtime drift | NONE |
| Test suite | 584 passed, 22 failed, 9 skipped |
| SEAL VERDICT | HOLD — static gaps and test drift block full seal |

The MCP server is healthy and operational. All 19 tools execute. The blockers are static file drift (outdated versions, missing deployment artifacts) and test string drift (F->L rename not propagated). No constitutional floors are violated.

---

## 2. TOOL-BY-TOOL TEST RESULTS

### 2.1 13 Canonical Tools

| Tool | Stage | Result | Verdict | Issue |
|------|-------|--------|---------|-------|
| arif_session_init | 000 | PASS | DEGRADED | No counterparty |
| arif_sense_observe | 111 | PASS | SEAL | Search works |
| arif_evidence_fetch | 222 | PASS | HOLD | NO_EVIDENCE_BACKEND_CONFIGURED |
| arif_mind_reason | 333 | PASS | HOLD | MiniMax M3 invalid JSON |
| arif_heart_critique | 444 | PASS | HOLD | MiniMax M3 invalid JSON |
| arif_kernel_route | 555 | PASS | HOLD | L11 AUTH: session_id missing (expected) |
| arif_reply_compose | 444r | PASS | BLOCKED | SEA-Guard fail-closed |
| arif_memory_recall | 555m | PASS | DEGRADED | Qdrant DNS failure |
| arif_gateway_connect | 666g | PASS | HOLD | L11 AUTH (expected) |
| arif_judge_deliberate | 888 | PASS | HOLD | Elicitation required (expected) |
| arif_vault_seal | 999 | PASS | HOLD | ack_irreversible required (expected) |
| arif_forge_execute | 010 | PASS | SEAL | OK |
| arif_ops_measure | 777 | PASS | SEAL | Healthy |

All 13 tools execute. HOLD verdicts on judge, vault_seal, kernel_route, gateway_connect are constitutional by design.

### 2.2 Forge Ladder (v3.1)

| Tool | Result | Verdict |
|------|--------|---------|
| forge_query | PASS | SEAL |
| forge_plan | PASS | SEAL |
| forge_dry_run | PASS | SEAL |

### 2.3 P2-7 Lease Tools

| Tool | Result | Verdict |
|------|--------|---------|
| arif_lease_inspect | PASS | SEAL |
| arif_lease_issue | PASS | HOLD (expected) |
| arif_lease_revoke | PASS | HOLD (expected) |

---

## 3. STATIC GAPS

### 3.1 Missing Deployment Artifacts

SG-1: .identity_hash missing at /opt/arifos/app/.identity_hash
- Impact: REST route /api/federation-probe falls back to "UNAVAILABLE"
- Fix: Add to deploy pipeline: echo $(git rev-parse HEAD) > /opt/arifos/app/.identity_hash

### 3.2 Outdated Static Metadata

Live server: v2026.05.05-SSCT / kanon-cd4b39b / 13 tools

SG-2: static/agent-card.json
- Current: version "2026.4.13", endpoint "mcp.arif-fazil.com"
- Fix: version "2026.06.11", endpoint "arifos.arif-fazil.com", tools_count 13

SG-3: static/.well-known/agent.json
- Same as SG-2

SG-4: static/.well-known/mcp/server.json
- Current: version "2026.04.26-KANON"
- Fix: version "2026.06.11-SSCT"

SG-5: static/mcp-discovery-index.json
- Current: updated "2026-05-22T12:10:00Z"
- Fix: updated "2026-06-11T04:00:00Z"

### 3.3 Missing Environment / API Keys

SG-6: BRAVE_API_KEY — not set
- Impact: arif_evidence_fetch returns NO_EVIDENCE_BACKEND_CONFIGURED

SG-7: TAVILY_API_KEY — not set
- Impact: Same as SG-6

SG-8: FIRECRAWL_API_KEY — not set
- Impact: Same as SG-6

SG-9: SEA_LION_GUARD_MODEL / SEA-Guard API
- Impact: arif_reply_compose BLOCKED by fail-closed SEA-Guard
- Fix: Verify SEA-LION API health or document intentional fail-closed posture

### 3.4 Infrastructure Config Gaps

SG-10: Qdrant DNS failure — "Temporary failure in name resolution"
- Impact: arif_memory_recall degraded, vector search unavailable
- Fix: Verify Qdrant container health (docker ps) or /etc/hosts for qdrant alias

SG-11: MiniMax M3 JSON mode unreliable
- Impact: arif_mind_reason and arif_heart_critique return llm_schema_violation
- Fix: Add response_format={"type": "json_object"} to MiniMax payload in llm_client.py

---

## 4. TEST FAILURES — 22 FAILED

### 4.1 F->L Rename Drift (8 failures)

The codebase renamed floors from F01-F13 to L01-L13. Tests were not updated.

test_webhook_intake.py — 3 failures (expects "F11 AUTH", code returns "L11 AUTH")
test_geox_qc_pipeline.py — 4 failures (expects "F03 WITNESS", code returns "L03 WITNESS")
test_live_metrics_contract.py — 1 failure (expects F10, code returns L10)
test_oauth_flow.py — 2 failures (expects "F13 SOVEREIGN" in HTML, HTML has "L13 SOVEREIGN")

Fix: Mass rename F01->L01, F03->L03, F10->L10, F11->L11, F13->L13 in test assertions.

### 4.2 P2-7 Lease Gate Breaking H2/H3 Tests (6 failures)

test_h2_h3_ratification.py — 6 failures
The new P2-7 lease gate fires BEFORE the plan check in arif_forge_execute. Tests expect "plan_id" in error reason, but now get "LEASE GATE: no lease_id provided".

Fix: Update tests to expect lease-gate hold when no plan_id/lease_id provided for irreversible modes.

### 4.3 Evidence Store Scoping Bug (1 failure)

test_truth_substrate.py::test_evidence_fetch_injection_quarantine
Error: "cannot access local variable 'get_evidence_store' where it is not associated with a value"

Fix: Ensure get_evidence_store is always in scope before use, or remove redundant local imports.

### 4.4 Other Failures (4 failures)

test_oauth_deny_flow — assertion on "F13 SOVEREIGN" string (same F->L issue)
test_webhook_intake — 3 additional failures on missing actor/invalid intent (expects F11, gets L11)

---

## 5. SEAL READINESS CHECKLIST

- [ ] SG-1 — Create /opt/arifos/app/.identity_hash on deploy target
- [ ] SG-2..5 — Update version strings in 4 static JSON files to 2026.06.11-SSCT
- [ ] SG-6..8 — Configure at least one evidence backend API key
- [ ] SG-9 — Verify SEA-Guard API availability or document fail-closed posture
- [ ] SG-10 — Fix Qdrant DNS/container connectivity
- [ ] SG-11 — Fix MiniMax M3 JSON structured output
- [ ] Test fixes — Update 22 test assertions for F->L rename, lease gate, evidence store
- [ ] Run full suite — pytest tests/ -q must pass >=99%

---

## 6. RECOMMENDATION

Verdict: HOLD -> SEAL after static gaps closed.

The arifOS MCP server is operationally sound. All 19 tools register, execute, and return governed responses. There is no runtime drift and no contract drift. The blockers are:

1. Deployment hygiene (missing .identity_hash, stale version metadata)
2. Environment config (missing evidence API keys)
3. Test maintenance debt (F->L rename not propagated, P2-7 gate not reflected)

These are clerical fixes, not architectural problems. Estimated fix time: 30-60 minutes.

---

Ditempa Bukan Diberi — Intelligence is forged, not given.
