# arifOS v2026.04.26-KANON — The True 13-Tool Canonical Surface

**Release Date:** 2026-04-26
**Commit:** `5acd35fb`
**Tag:** `v2026.04.26-KANON`
**Codename:** KANON-13

---

## 🎯 Executive Summary

This release seals the **canonical 13-tool public MCP surface**. Diagnostic probes (`arif_ping`, `arif_selftest`) and interpretive witness tooling have been **internalized** — they remain fully operational as runtime diagnostics and internal governance sidecars, but are no longer exposed as public MCP tools. This reduces public surface entropy, hardens the external contract, and aligns the live system with the constitutional architecture.

**Public surface:** 13 capability tools only.
**Internal runtime:** 2 diagnostics + context witness emission.
**External ops:** `/health` (liveness) + `/ready` (readiness selftest).

---

## 🔧 Surface Changes

### Canonical 13 Public Tools

| # | Tool | Purpose |
|---|------|---------|
| 1 | `arif_session_init` | Constitutional session anchor |
| 2 | `arif_sense_observe` | Environmental sensing |
| 3 | `arif_evidence_fetch` | Evidence-preserving web ingestion |
| 4 | `arif_mind_reason` | Constitutional reasoning |
| 5 | `arif_heart_critique` | Risk critique & empathy scan |
| 6 | `arif_kernel_route` | Intent routing & dispatch |
| 7 | `arif_reply_compose` | Governed reply composition |
| 8 | `arif_memory_recall` | Vector memory retrieval |
| 9 | `arif_gateway_connect` | Agent-to-agent mesh |
| 10 | `arif_judge_deliberate` | Constitutional adjudication |
| 11 | `arif_vault_seal` | Immutable ledger sealing |
| 12 | `arif_forge_execute` | Metabolic execution |
| 13 | `arif_ops_measure` | Health & thermodynamics |

### Removed from Public Surface

- `arif_ping` → internal `_runtime_ping()` (used by `/health`)
- `arif_selftest` → internal `_runtime_selftest()` (used by `/ready`)
- `arif_meaning_witness` / `arif_context_witness` → internal emission pipeline only

---

## 🛡️ Governance Hardening

### Context Witness Sidecar
- **SEA-LION Bridge**: Added `interpret_with_sea_lion()` for meaning interpretation using approved quote candidates only. The interpreter **never generates quotes, invents authors, or mutates text**.
- **Locked Ledger**: `wisdom_quotes_lite.json` — 20 curated, schema-validated quotes with canonical `action_bias`, `risk_use`, and `source_status`.
- **Context Safety**: `context_safety.py` enforces **fail-closed** validation:
  - Exact string matching on quote text and author (no fuzzy matching, no silent correction)
  - Unknown `selected_quote_id` → `HOLD`
  - Mutated quote text or author → `HOLD`
  - Irreversible risk + forbidden action verb (execute, commit, deploy, seal, push) → `REFUSE`

### External Ops Endpoints
- `GET /health` — lightweight liveness (calls `_runtime_ping`)
- `GET /ready` — structured readiness with selftest verdict (calls `_runtime_selftest`)

---

## 🧪 Test Coverage

- **54 targeted tests passing** (up from 45)
- Registry count validation
- Health endpoint verification
- Context witness internal emission logic
- Quote drift rejection (adversarial)
- Governance boundary enforcement
- Safety gate callability
- `python -m compileall arifosmcp` — clean

---

## 📦 Package Updates

| File | Change |
|------|--------|
| `pyproject.toml` | Version `2026.04.26`, description updated to 13 canonical tools |
| `arifosmcp/__init__.py` | Version `2026.04.26-KANON` |
| `arifosmcp/server.py` | Version strings synced |
| `arifosmcp/packages/npm/arifos-mcp/package.json` | Version `2026.04.26`, description aligned |
| `uv.lock` | Regenerated with `uv lock` |
| `Dockerfile` | LABEL updated to reflect 13-tool surface |

---

## 🚀 Deployment Notes

1. Ensure `SEA_LION_API_KEY` is present in `.env` for Context Witness interpretation.
2. Build with `--build-arg ARIFOS_VERSION=2026.04.26-KANON`.
3. Verify `/health` and `/ready` return expected payloads before marking deploy complete.
4. The `ARIFOS_GOVERNANCE_SECRET` must remain **identical** across restarts (F11 continuity).

Full deployment prompt: see `/root/DEPLOY_PROMPT_OPENCODE.md`

---

## 🏛️ Constitutional Compliance

| Floor | Status |
|-------|--------|
| F1 Amanah | ✅ No destructive changes without hold |
| F2 Truth | ✅ Registry count honest (13) |
| F3 Witness | ✅ Evidence-preserving fetch |
| F4 Clarity | ✅ Public/internal boundary explicit |
| F5 Peace | ✅ No consciousness claims |
| F6 Empathy | ✅ Risk critique hardened |
| F7 Humility | ✅ Uncertainty bands in witness |
| F8 Genius | ✅ G ≥ 0.80, elegant reduction |
| F9 Anti-Hantu | ✅ No emotion/consciousness claims |
| F10 Ontology | ✅ Map/handler alignment verified |
| F11 Auth | ✅ Session required |
| F12 Injection | ✅ Input sanitization |
| F13 Sovereign | ✅ Human veto absolute |

---

## 📝 Changelog (since v2026.04.24)

- `5acd35fb` — chore(docker): update LABEL to reflect canonical 13-tool surface
- `9373d012` — docs: align README and CHANGELOG with v2026.04.26-KANON release
- `47f909e9` — fix(registry): purge ping/selftest from public surface — true 13-tool canonical surface
- `d5dc81cb` — test(context_safety): align assertion with error_code field
- `cc2d4189` — fix(arifos): resolve ghost module imports and update version to KANON
- `3f149a5d` — refactor(arifos): internalize Context Witness and restore Canonical 13 surface
- `9636d0a8` — feat(wisdom): SEA-LION bridge + gated philosophy sidecar

---

**DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**

*Sealed by ARIF-999-RITUAL-v1.1 | 2026-04-26*
