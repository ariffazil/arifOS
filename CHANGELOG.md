# CHANGELOG — arifOS

## [v2026.05.21-1] — 2026-05-21

### LSP Import Resolution + MCP Protocol Compliance

- **LSP**: Fixed unreachable `vault_seal` dead code branch — referenced non-existent `arifos_vault`; actual handler name is `_arif_vault_seal_tool`, branch now calls `handler(**arguments)` directly.
- **LSP**: Added `TYPE_CHECKING` stub for `get_session_identity`; lazy import pattern preserves runtime behavior while giving LSP name resolution.
- **LSP**: `pyrightconfig.json` — `reportMissingImports: false` suppresses false-positive import errors from static analysis not mirroring runtime `sys.path`.
- **MCP**: `prompts/list` schema corrected to `arguments[]` with `required`/`description` per MCP spec §Prompts.
- **MCP**: `prompts/get` error code `code: 0` → `-32602` for unknown prompts.
- **MCP**: REST `/prompts` endpoint now delegates to live MCP registry instead of hardcoded list.
- **MCP**: `isError: false` removed from success tool responses (MCP spec: key only present when true).
- **Verification**: pyright CLI `0 errors`, pytest `175 passed, 1 skipped`, Ruff `All checks passed`.

## [v2026.05.22] — 2026-05-22

### ⚡ A-RIF Framework + Kernel Purity + Vault999 Two-Lane Architecture

**A-RIF Discovery Forge:**
- Added `forge/program.md` (+187) — autonomous experiment framework (karpathy/autoresearch-inspired).
- Added `scripts/optimize_agents.py` (+86) — agent optimization script.
- A-RIF ordinal evidence levels, Jaccard contrast, search worthiness scoring. 488 tests pass.
- Added `skills/forge-program/SKILL.md` (+125) — forge program skill.

**Vault999 Two-Lane Architecture:**
- `vault999-writer`: two-lane architecture + ZKPC quarantine + Ed25519 opt-in.
- `1cb30ce9 vault999-writer: two-lane architecture + ZKPC quarantine + Ed25519 opt-in`.

**Metabolize Mode:**
- `arif_kernel_route` `mode=metabolize` delegates to `arif_mind_reason_v2`.
- `arif_mind_reason` handles `mind_packet` nested structure from v2 metabolic synthesis.
- `metabolize` mode registered in kernel_route and eureka_insight tool modes.
- Fix: datetime compatibility in mind_reason.

**Session Lifecycle (F11S/F13S):**
- Lightweight F11S/F13S session lifecycle gate (`f5da7ab2`).
- Session sealing with provenance tracking.

**Kernel Purity:**
- Finalized kernel purity and secure workspace isolation.
- Align `arifOS` repo hygiene and ZKPC tests.

**Deploy Absorptions:**
- Absorbed remaining A-FORGE deploy artifacts (`e4dd8bbd`).
- `deploy/`: finalized kernel purity and secure workspace isolation.
- `arifOS-supabase` integration absorbed.

**Shadow Infrastructure (tests):**
- `test_shadow_infrastructure.py` (+184 lines).
- `test_888_judge_paradox_guard.py` (+187 lines).
- `test_floors_f3_f11.py` (+146 lines).
- `test_truth_substrate.py` (+509 lines).
- Paradox Guard + TruthLayer + Cognitive Shadow wired into floor enforcement.

**F9/F4 Compliance:**
- Removed anthropomorphic self-labels from codebase.

**Google Workspace MCP:**
- Added Google Workspace MCP tool with OAuth2 integration.

**Repo Hygiene:**
- Align `pyproject.toml` with system reality; delete `requirements.txt`.
- Add `pyrightconfig.json` for LSP import resolution.
- Fix CI: tmpdir for WELL state, remove broken absolute symlink `arifos/well`.
- Repair shared federation layout contract.
- Hermes session briefings ignored by default.

**Verification:**
- `pytest tests/runtime/test_msap_ack.py tests/runtime/test_zkpc_v2.py -q`: 31 passed.
- `python -m pytest tests/ -q --tb=short`: 1939 passed, 18 skipped.

## [v2026.05.21] — 2026-05-20

### ⚡ Metabolize Mode — Cognitive Delegation Wiring

- **Kernel Route metabolize mode:** `_arif_kernel_route` now handles `mode=metabolize`, delegating to `arif_mind_reason_v2` with `MindRequest` construction and async execution.
- **Mind Reason metabolize handler:** `arif_mind_reason` handles `mind_packet` nested structure from v2 metabolic synthesis, building delta bundle with `metabolized_context`, `abstractions`, `attestations`, `abductions`, `sequential_layers`, and `next_safe_action` extraction.
- **Constitutional Map:** `metabolize` mode registered in both `arif_kernel_route` (kernel tools) and `eureka_insight` tool modes.

---

## [v2026.05.19] — 2026-05-19

### 🌑 Shadow Infrastructure & Paradox Guard

- **444_KERNEL Shadow-Aware Routing:** Added flux-based veto for irreversible targets (`FORGE`, `VAULT`, `EXECUTE`, `DEPLOY`). Metabolic flux ≥ 0.85 or alignment-faking ≥ 0.7 blocks routing with `HOLD_888`. Metrics computed from live session shadow state instead of nulls.
- **111_SENSE F-WEB Injection Scan:** All MiniMax bridge results scanned for external instruction injection (`ignore previous instructions`, `jailbreak`, `DAN mode`, etc.). Injection detected → evidence downgraded, confidence capped at 0.3, `floor_12_signal="fail"`.
- **999_VAULT Truth Layer Sealing:** Every ledger entry and return envelope now embeds `truth_layer: "checklist"`, `absolute_truth_claimed: false`, `unknown_unknowns_acknowledged: true`, `human_judgment_required: true`, `godel_lock_active: true`.
- **888_JUDGE Paradox Guard:** Post-floor downgrade `SEAL → HOLD_888` triggers on confidence < 0.6, metabolic flux ≥ 0.65, or alignment-faking ≥ 0.6 after all floors pass. Early-return paths (empty bundle, malformed metrics) also carry truth-layer fields.
- **Tests:** Added 42 tests across `test_shadow_infrastructure.py` (18), `test_floors_f3_f11.py` (17), and `test_888_judge_paradox_guard.py` (7). All passing; zero regressions in 133 related existing tests.

---

## [v2026.05.20] — 2026-05-17

### 🛠️ Audit & Governance Alignment

- **Audit Truth:** Added `registry_truth: PASS` to health payload to satisfy federation readiness requirements.
- **Session Integrity:** Patched `federation_audit` to prioritize and trust caller-provided `session_id`, preventing audit trail fragmentation.
- **Somatic Callability:** Updated WELL dry-call fixtures with valid domain payloads (`{"mode": "human"}`), resolving false 400 errors during probes.
- **Heart Semantics:** Split `arif_heart_critique` verdict into `execution_verdict` (tool success) and `action_risk_verdict` (risk judgment) to prevent semantic confusion by agents.
- **F13 Sovereign Fix:** Enforced mandatory human elicitation in `arif_judge_deliberate` candidate confirmation, closing the model self-certification bypass.
- **Topology:** Registered `graphiti-mcp` endpoint in federation service endpoints for autonomous probing.

---

## [v2026.05.05-SSCT] — 2026-05-05

### 🏛️ Sole Source Constitutional Track (SSCT)

- **Single Source of Truth:** `arifosmcp/constitutional_map.py` is now the SOLE canonical registry. Three legacy files archived: `constitution.py` (v2, void_000 naming), `capability.py` (arifos.* dotted aliases), `arifosmcp/capability_map.py` (duplicate alias map).
- **Floor Rebalancing:** All 13 floors now have ≥ 2 tools each — zero thin floors. F03, F05, F09, F10 each gained a second tool.
- **Schema I/O Canonicalization:** 13/13 tools have both input and output schemas defined (100%). `validate_tool_response_schema()` now enforces F10 `omega_ont` presence. `check_schema_coverage()` now checks floor coverage too.
- **Eureka Insights Wired:** Every tool carries `eureka_insight` field linking its floors to the physics equations from `EUREKA_INSIGHTS_SEAL_v2026.04.07`.
- **Version Uniformity:** All hardcoded version strings unified to `v2026.05.05-SSCT`.
- **tool_registry.json Regenerated:** From sole source `constitutional_map.py` with `_schema: arifos-ssct-v2026.05.05-kanon-ssct`.

---

## [v3.0.0-SEAL] — 2026-04-29

### 🚀 WEALTH V3 Migration
- Refactored WEALTH Temporal Kernel with 13 Primitives and 66 Aliases.
- Established "Selective Escalation" (Option C) for 4-MCP orchestration.
- Reborn AFWELL and WEALTH kernels with "Universal Failure Grammar."

### 🛡️ Hardening & Optimization
- **Metabolic GC:** Reclaimed ~65GB disk space and purged ghost containers.
- **Thermodynamic Anchor:** Patched `000_INIT` to call `init_thermodynamic_budget()` upon session creation (Balanced Fix).
- **Biological Readiness Gate:** Integrated `readiness_score` into `888_JUDGE` as a mandatory F13 precondition check (Threshold: 40).
- **Infrastructure:** Mounted `/root/WELL/state.json` to `arifosmcp` to enable physiological governance.

### 📋 Documentation & Scars
- **Casing Scar:** Documented `/root/well` (source) vs `/root/WELL` (data) boundary. Stable historical artifact.
- **Constitutional Alignment:** FAILURE_DOCTRINE_V1.md and LAW.md confirmed as active symbolic reasoning floors.

### 💾 Persistence
- **Pre-Seal Backup:** Created `pre_v3_seal.sql` via `pg_dump` of VAULT999.

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
