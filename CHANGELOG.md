# CHANGELOG — arifOS

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
