# PHOENIX-73D Chaos Removal Audit

**Agent:** kimi-code-cli  
**Actor:** arif  
**Session:** SEAL-0061f3b1a16d4102  
**Date:** 2026-05-25  
**Scope:** /root/arifOS  
**Classification:** OBSERVE-ONLY — no mutations performed  

---

## 1. Executive Verdict

**Is the codebase safe?** YES — governance core intact. 13 floors active. 13 tools loaded. Vault healthy. No runtime drift. No contract drift.  
**Is governance core intact?** YES — floors.py, ontology_guard.py, identity.json, vault999, judge, memory, kernel all protected and functional.  
**Highest priority chaos:** Parallel package namespace collision (`arifosmcp` vs `arifos_mcp` vs `arifos`), broken test blocking collection, 72-tool stub package masquerading as real implementation, empty `commands/scripts/` directory with dangling test references.

---

## 2. Do-Not-Touch List

These are canonical protected artifacts. Never propose deletion without explicit Arif approval:

- `/root/.arif/identity.json`
- `/root/.arif/memory.jsonl` or equivalent append-only event logs
- `/root/arifOS/core/shared/floors.py`
- `/root/arifOS/core/shared/guards/ontology_guard.py`
- `/root/arifOS/arifosmcp/runtime/tools.py` (canonical 13-tool surface)
- `/root/arifOS/arifosmcp/runtime/session.py` (session registry)
- `/root/arifOS/arifosmcp/server.py` (MCP entrypoint)
- `/root/arifOS/core/governance_kernel.py`
- `/root/arifOS/core/judgment.py`
- `/root/arifOS/core/enforcement/governance_engine.py`
- `/root/arifOS/risk_leash.yaml`
- `/root/arifOS/identity.toml`
- `/root/arifOS/deploy/docker-compose.yml` (canonical compose)
- Any vault999 ledger files
- Any secret store or credential file

---

## 3. Remove Candidates

| Path | Chaos Type | Evidence | Confidence | Risk if Removed | Rollback | Recommendation |
|------|-----------|----------|------------|-----------------|----------|----------------|
| `arifos_mcp/arifos_mcp/tools/canonical/*.py` | All 72 tools return hardcoded dummy data | CHAOS_REPORT.md CHAOS-01: `arif_ops_measure()` returns `g_score: 0.85` hardcoded; `arif_vault_seal()` returns fake hash | HIGH | `arifos_mcp` package is non-functional stubs; removing stubs prevents agents from being misled | Restore from git if needed | **REMOVE_LATER** — package is a migration target, not production. Mark all stub tools as `@mcp.tool(disabled=True)` or delete after real implementations wired |
| `arifos_mcp/CHAOS_REPORT.md` | Generated audit doc inside codebase | Pre-existing analysis artifact; not canonical governance | HIGH | Low — it's a working document | git restore | **ARCHIVE** to `/root/arifOS/docs/audits/` or delete after migration complete |
| `arifos_mcp/MIGRATION_MAP.md` | Generated migration plan inside codebase | Same as above — 10+ analysis docs (`EUREKA_EXTRACT.md`, `PHOENIX72_GAP_MATRIX.md`, etc.) | HIGH | Low — working docs | git restore | **ARCHIVE** all 10 docs to `docs/audits/phoenix72/` |
| `arifos_wiki_tools/` | Legacy wiki module | MIGRATION_MAP.md says "replace with proper wiki tools in arifos_mcp" | HIGH | Low — superseded by wiki tools in arifosmcp | git restore | **ARCHIVE** or **REMOVE_LATER** |
| `commands/scripts/` | Empty directory | Only `__pycache__` exists; all scripts moved to `scripts_archive/` and `scripts_deploy/` | HIGH | Very low | Restore from `scripts_archive/` | **REMOVE** empty directory or symlink to `scripts_deploy/` |
| `arifOS_mcp_runtime.py` | Legacy duplicate | MIGRATION_MAP.md: "duplicate, confusing" | HIGH | Low | git restore | **REMOVE_LATER** |
| `arifosd.py` | Old daemon | MIGRATION_MAP.md: "old daemon, superseded" | HIGH | Low | git restore | **REMOVE_LATER** |
| `arifOS-supabase/clients/supabase_client.ts` | Deleted in working tree but directory lingers | `git status` shows `D arifOS-supabase/clients/supabase_client.ts` | HIGH | Low — already deleted | git checkout -- or git rm | **COMPLETE DELETION** — remove remaining `arifOS-supabase/` dir if unused |
| `authentik/docker-compose.yml` | Unused identity provider | No health checks, no references in stack_health_probe, no running containers | MEDIUM | Low if truly unused | git restore | **NEEDS_ARIF_DECISION** — verify if authentik is planned or dead |
| `archive/2026-05/deploy-legacy/docker-compose.yml` | Stale compose in archive | Already in `archive/` but still a docker-compose.yml that could be mistaken for active | MEDIUM | Very low | git restore | **SAFE TO REMOVE** from archive if confirmed obsolete |

---

## 4. Repair Candidates

| Path | Issue | Proposed Repair | Risk | Tests Needed |
|------|-------|-----------------|------|--------------|
| `tests/runtime/test_doctrine_diff_ci.py` | ImportError: `commands.scripts.doctrine_diff_ci` module not found (moved to `scripts_archive/`) | Update import to `commands.scripts_archive.doctrine_diff_ci` OR move module back to `scripts/` | LOW | Run pytest collection |
| `arifosmcp/runtime/tool_specs.py` | Deprecated — `tool_spec.py` is canonical | Add deprecation warning, redirect imports, or remove after confirming no callers | LOW | grep for `tool_specs` imports |
| `arifosmcp/schemas/metabolic.py` | Pydantic class-based `config` deprecated (V3 break) | Migrate to `ConfigDict` | LOW | pytest metabolic tests |
| `arifosmcp/schemas/claim.py` | Same Pydantic deprecation | Migrate to `ConfigDict` | LOW | pytest claim tests |
| `pyproject.toml` vs `arifosmcp/pyproject.toml` | Both claim `name = "arifos"` — PyPI name collision | `arifosmcp/pyproject.toml` should use `name = "arifosmcp"` or be consolidated into root `pyproject.toml` with `[tool.hatch]` workspaces | MEDIUM | pip install -e test |
| `arifosmcp/runtime/session.py` | Global singleton session (`_ACTIVE_SESSION_ID`) | Session registry exists but `_ACTIVE_SESSION_ID` is a global singleton — may cause 409 conflicts under concurrent clients | MEDIUM | Concurrent client test |
| `ops/hermes/plugins/aaa_guard/` | Hermes plugin inside arifOS codebase | Cross-domain bleed — Hermes belongs in AAA or HERMES repos, not arifOS | LOW | Verify if actively imported |
| `arifosmcp/runtime/compat.py` | FastMCP 2.x vs 3.x transport compatibility shim | Shim is safe but adds complexity; document which version is canonical | LOW | Transport startup test |

---

## 5. Archive Candidates

| Path | Why Archive | Destination | Rollback |
|------|-------------|-------------|----------|
| `arifos_mcp/CHAOS_REPORT.md` | Working audit doc, not canonical | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/MIGRATION_MAP.md` | Working migration plan | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/EUREKA_EXTRACT.md` | Working analysis | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/MIGRATION_EXECUTION_PLAN.md` | Working plan | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/PHOENIX72_GAP_MATRIX.md` | Working matrix | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/PROMPT_INVENTORY.md` | Working inventory | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/RESOURCE_INVENTORY.md` | Working inventory | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/TOOL_INVENTORY.md` | Working inventory | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/TOOL_LIFECYCLE_STATUS.md` | Working status | `docs/audits/phoenix72/` | git restore |
| `arifos_mcp/PERMISSION_RISK_REPORT.md` | Working report | `docs/audits/phoenix72/` | git restore |
| `wiki.ARCHIVED-2026-04-12/` | Already archived wiki | Keep as-is (properly named) | N/A |
| `GENESIS_ARCHIVE/` | Genesis docs | Keep as-is (properly named) | N/A |
| `tests/archive/legacy_arifos_v1/` | Old tests | Keep as-is (properly named) | N/A |
| `boas-audit/` | Untracked runtime sync audit | Either commit to `docs/audits/` or delete | git clean |

---

## 6. Operational Clutter

| Service | Status | Evidence | Recommendation |
|---------|--------|----------|----------------|
| SEA-LION | **CONFIGURED_BUT_UNREACHABLE** | `stack_health_probe`: "sea_lion_configured: true, sea_lion_healthy: false" | Mark explicitly as degraded in `FEDERATION_STATUS.md`. Ollama fallback is active. |
| graphiti-mcp | **CONFIGURED_BUT_UNREACHABLE** | `stack_health_probe`: "graphiti-mcp: unreachable, error: All connection attempts failed" | Already marked degraded. Container not running. Semantic floor degraded. |
| Langfuse | **NOT_WIRED** | `stack_health_probe`: "langfuse_tracing: NOT_WIRED, reason: sdk_not_installed" | Either install SDK and configure, or remove references to reduce confusion. |
| 888_JUDGE elicitation | **NEEDS_MCP_CLIENT** | `arif_judge_deliberate` returns: "MCP client with elicitation support is required" | Document requirement. Current Kimi/OpenCode clients may not support FastMCP elicitation ctx. |
| SSE/session 409 | **NEEDS_TEST** | `rest_routes.py` references SSE; `session.py` has global `_ACTIVE_SESSION_ID` singleton | The global singleton session variable is a concurrency risk. Needs concurrent client test. |
| A2A server (port 3001) | **NOT_RUNNING** | `ss -tlnp` shows no listener on 3001 | Start or document as intentionally disabled. |
| APEX Prime (port 3002) | **NOT_RUNNING** | `ss -tlnp` shows no listener on 3002 | Start or document as intentionally disabled. |
| Hermes A2A (port 18001) | **NOT_RUNNING** | `ss -tlnp` shows no listener on 18001 | Deprecated. Hermes now routes through AAA gateway (3001). |

---

## 7. Governance Clutter

| Finding | Severity | Evidence | Action |
|---------|----------|----------|--------|
| `arifos_mcp/` is a **parallel package** claiming to be canonical MCP | HIGH | `arifos_mcp/pyproject.toml`: `name = "arifos-mcp"`; contains 72 stub tools with same names as real tools | Clarify boundary: `arifosmcp/` = production canonical; `arifos_mcp/` = PHOENIX-72 migration workspace |
| `REPO_ROLE_MAP.md` untracked | MEDIUM | New file defining canonical names | Looks valuable — Arif should review and commit |
| `FEDERATION_STATUS.md` untracked | MEDIUM | New file defining live organ status | Looks valuable — Arif should review and commit |
| Multiple `IDENTITY.md` files across repos | LOW | `.openclaw/`, `AAA/`, `WEALTH/`, `WELL/` all have identity docs | Expected per-repo identity; not parallel authority if they reference canonical `/.arif/identity.json` |
| `ontology_guard.py` already detects parallel authority | SAFE | Guards against `AGENT_BODY_PROTOCOL.md`, `AGENT_LAW.md`, `local_constitution.md` | Working as designed |

---

## 8. Test Clutter

| Test File | Issue | Count | Recommendation |
|-----------|-------|-------|----------------|
| `tests/runtime/test_doctrine_diff_ci.py` | **BROKEN COLLECTION** — ImportError | 1 error blocks collection | Repair import path |
| `tests/runtime/test_internal_tools_comprehensive.py` | Many skips — "documentation mismatch" | ~8 skips | Sync docs with runtime or remove obsolete test cases |
| `tests/test_jwt_acceptance.py` | 4 skips — `geox.core.ac_risk broken on Python 3.13` | 4 skips | Fix GEOX dataclass or skip permanently with reason |
| `tests/test_asi_sbert.py` | 3 skipif — missing sentence-transformers | 3 skips | Optional dependency — acceptable |
| `tests/conftest.py` | 2 skips — PostgreSQL/Redis not running | 2 skips | Expected for local dev without services |
| `tests/test_registry.py` | 3 skips — jsonschema not installed | 3 skips | Add to dev dependencies or make optional |
| `tests/test_mcp_drift_check.py` | 1 skip — drift enforcement not strict | 1 skip | Expected if env var not set |
| `tests/test_coverage_boost.py` | 1 skip — DDGS not installed | 1 skip | Optional dependency — acceptable |

**Tests needed for new code:**
- `classify_action()` in `arifosmcp/core/reversibility_engine.py` — no test found
- Parallel artifact detector in `core/shared/guards/ontology_guard.py` — tested implicitly but needs dedicated test
- Session concurrency / 409 conflict — no test found
- `arif_floor_status` and `mcp_drift_check` — tests exist but need validation

---

## 9. Recommended Phase 1 Cleanup (Safe, Low-Risk)

**Docs & Config:**
1. ✅ Commit `REPO_ROLE_MAP.md` and `FEDERATION_STATUS.md` if Arif approves content
2. ✅ Move `arifos_mcp/*.md` analysis docs to `docs/audits/phoenix72/`
3. ✅ Mark `SEA-LION` and `Langfuse` as explicitly degraded in docs
4. ✅ Delete empty `commands/scripts/` directory or symlink to `scripts_deploy/`
5. ✅ Complete removal of `arifOS-supabase/` if confirmed unused

**Tests:**
6. ✅ Fix `test_doctrine_diff_ci.py` import path
7. ✅ Remove or fix skipped tests that hide documentation mismatch

**Config:**
8. ✅ Fix `pyproject.toml` name collision (`arifosmcp` should not claim `name="arifos"`)
9. ✅ Add Pydantic `ConfigDict` migration to avoid V3 breakage

---

## 10. Recommended Phase 2 Cleanup (Medium-Risk)

1. **Consolidate docker-compose files** — 6 compose files is excessive. Keep `deploy/docker-compose.yml` as canonical, move others to `deploy/overrides/` or archive.
2. **Consolidate Caddyfiles** — 2 Caddyfiles. Keep `deploy/Caddyfile` as canonical.
3. **Repair broken provider configs** — SEA-LION config should be marked disabled or removed if permanently unreachable.
4. **Wire session registry** — Replace global `_ACTIVE_SESSION_ID` singleton with per-client session map to prevent 409 conflicts.
5. **Remove `arifos_wiki_tools/`** after confirming `arifosmcp` wiki tools cover all use cases.
6. **Archive `arifos_mcp/` stub tools** or mark them clearly as non-functional.

---

## 11. Recommended Phase 3 Cleanup (Requires Arif Approval)

1. **Delete obsolete modules:** `arifOS_mcp_runtime.py`, `arifosd.py`, `arifos_wiki_tools/`
2. **Remove services from production:** `authentik/` if confirmed dead
3. **Change MCP session architecture:** Move from global singleton to per-client session registry
4. **Edit governance artifacts:** Only if constitutional floors need updating
5. **Alter identity/vault/floors:** Never without Arif explicit ack

---

## 12. Exact Next Prompt for Patch Phase

```
Arif — PHOENIX-73D audit complete. 5 chaos categories found:

A. DOCS DRIFT: REPO_ROLE_MAP.md and FEDERATION_STATUS.md are valuable untracked docs. 10 migration analysis docs clutter arifos_mcp/.

B. OPERATIONAL CLUTTER: SEA-LION unreachable, Langfuse not wired, graphiti-mcp down, A2A/APEX/Hermes ports not listening.

C. TEST CLUTTER: test_doctrine_diff_ci.py broken (ImportError). 8 skips in comprehensive test hiding doc mismatch. 4 skips for Python 3.13 GEOX break.

D. PACKAGE CHAOS: arifosmcp/ and arifos_mcp/ parallel packages. Both pyproject.toml claim name="arifos". 72 stub tools in arifos_mcp return hardcoded data.

E. CODE CHAOS: commands/scripts/ empty, arifOS-supabase partially deleted, Pydantic V3 deprecation, global session singleton.

Which category should I execute first?
A. docs drift (commit/move docs)
B. operational service clutter (mark degraded, clean compose)
C. test clutter (fix broken test, clean skips)
D. package chaos (fix pyproject collision, mark stubs)
E. code chaos (remove empty dirs, fix deprecation)
```

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
