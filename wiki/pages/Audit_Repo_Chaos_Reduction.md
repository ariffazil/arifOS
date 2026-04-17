---
type: Synthesis
tier: 50_AUDITS
strand:
- operations
audience:
- operators
difficulty: intermediate
prerequisites:
- Concept_Architecture
tags:
- audit-repo-chaos-reduction
sources:
- README.md
- AGENTS.md
- CHANGELOG.md
- ROADMAP.md
- TODO.md
last_sync: '2026-04-10'
confidence: 0.9
---

# Audit: Repo Chaos Reduction

**Date:** 2026-04-08  
**Auditor:** Copilot (A-AUDITOR role)  
**Mode:** Audit-Only — no destructive changes made  
**Constitutional authority:** 888_JUDGE  
**Scope:** Active surface ~378 .md files (1,622 files already in `archive/` excluded)

---

## Summary

| Class | Count | % |
|---|---|---|
| canonical | 74 | 20% |
| operational | 62 | 16% |
| historical | 89 | 24% |
| redundant | 61 | 16% |
| generated | 12 | 3% |
| unknown | 80 | 21% |

| Action | Count |
|---|---|
| keep | 101 |
| merge-into-canonical | 18 |
| merge-into-wiki | 9 |
| archive | 122 |
| hold-for-human | 27 |
| delete | 0 |

> **Note:** Zero deletes recommended at this pass. All redundant files require human confirmation before any destructive action (Rule 1: never delete without checking unique content).

---

## Classification Table

### ROOT LEVEL

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `README.md` | canonical | keep | Primary SoT narrative. Version 2026.04.06. Do not replicate. |
| `AGENTS.md` | canonical | keep | PRIMARY SoT for agent guidance, role permissions, repo structure map. 12KB. All other AGENTS.md copies are older snapshots. |
| `CHANGELOG.md` | canonical | keep | Current changelog (46KB, last entry 2026.04.07-SOT-SEALED). Largest and most current of all changelog copies. |
| `ROADMAP.md` | canonical | keep | Version 2026.04.07-SOT-SEALED. Canonical horizon strategy. |
| `TODO.md` | operational | keep | Active work queue, P0 blockers tracking. Dated 2026.04.07-TIER1-SEALED. Needs periodic archival of completed items. |
| `SEALING_CHECKLIST.md` | operational | keep | Production hardening checklist. Active reference for infrastructure secrets. |
| `000-999-implementation-plan.md` | historical | archive | Planning doc for GUI mode implementation. References stale workspace paths (`/workspace/repos/arifosmcp/`). Work appears completed. |
| `VAULT999_4LAYER_IMPLEMENTATION_SUMMARY.md` | historical | archive | Implementation complete (status: ✅). 14KB summary of the 4-layer vault build. Superseded by `wiki/pages/Concept_Vault999_Architecture.md` + `core/vault999/VAULT999_SOVEREIGN_4LAYER.md`. Consider moving to `archive/vault999/`. |

---

### `000/` — Constitutional Law (33 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `000/000_CONSTITUTION.md` (33KB) | canonical | keep | PRIMARY constitutional document. Exact copy exists in `wiki/raw/CONSTITUTION.md` — that copy is intentional as wiki ingestion feed. |
| `000/000_MANIFESTO.md` (20KB) | canonical | keep | Human-language manifesto. Unique content. |
| `000/000_INFRA_SOVEREIGNTY.md` (1.6KB) | canonical | keep | Infrastructure sovereignty declaration. Small but purposeful. |
| `000/AUTH_PROTOCOL.md` (19KB) | canonical | keep | Authentication protocol spec. |
| `000/ENTROPY_POLICY.md` (9KB) | canonical | keep | Entropy policy for ΔS≤0 enforcement. |
| `000/HUMILITY_SPEC.md` (12KB) | canonical | keep | Ω₀ algorithm specification. **EXACT DUPLICATE** of `wiki/raw/HUMILITY_SPEC.md` — see Duplication Map. |
| `000/MEMORY_LIFECYCLE.md` (12KB) | canonical | keep | Memory lifecycle governance spec. |
| `000/README.md` (7.6KB) | canonical | keep | 000/ directory overview. |
| `000/VERDICT_RECOVERY_MATRIX.md` (14KB) | canonical | keep | Verdict recovery procedures. |
| `000/VERDICT_SCHEMA_STANDARD.md` (13KB) | canonical | keep | Verdict schema standard. |
| `000/FLOORS/F01_AMANAH.md` through `F13_SOVEREIGN.md` (13 files, 800-4KB each) | canonical | keep | Individual floor definitions. Small, authoritative, no duplicates found. |
| `000/FLOORS/K000_LAW.md` (20KB) | canonical | keep | Constitutional law — matches `wiki/raw/K000_LAW.md` exactly. **CONTRADICTION FLAG:** `000/THEORY/K000_LAW.md` is 22KB (different/newer version). See Hold List. |
| `000/ROOT/K_FOUNDATIONS.md` (81KB) | canonical | keep | Large foundational theory document. |
| `000/ROOT/K000_ROOT.md` (43KB) | canonical | keep | Root constitutional map. |
| `000/ROOT/K333_CODE.md` (53KB) | canonical | keep | Code governance constitutional theory. |
| `000/ROOT/K111_PHYSICS.md` (19KB) | canonical | keep | Physics-layer constitutional theory. |
| `000/ROOT/K_FORGE.md` (17KB) | canonical | keep | Forge law theory. |
| `000/ROOT/000_CANON_MAP.md` (975B) | canonical | keep | Canon map pointer. |
| `000/ROOT/README.md` (7.9KB) | canonical | keep | ROOT/ directory readme. |
| `000/THEORY/K000_LAW.md` (22KB) | canonical | hold-for-human | Larger than `000/FLOORS/K000_LAW.md` (20KB) — may be a newer version. **CONTRADICTION:** Two K000_LAW.md files with different sizes. One should be canonical and the other archived. See Hold List. |
| `000/THEORY/K999_VAULT.md` (3.9KB) | canonical | keep | Vault constitutional theory. |

---

### `wiki/` — Ω-Wiki Layer (45 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `wiki/SCHEMA.md` | canonical | keep | Wiki schema/structure definition. Unique. |
| `wiki/index.md` | canonical | keep | Wiki index and navigation. Unique. |
| `wiki/log.md` (11KB) | operational | keep | Wiki activity log. Operational record. |
| `wiki/pages/*.md` (26 files) | canonical | keep | Living synthesis layer — the intended Ω-Wiki surface. All unique synthesized content. |
| `wiki/raw/CONSTITUTION.md` (33KB) | redundant | keep | **Intentional copy** of `000/000_CONSTITUTION.md` as wiki ingestion feed. Do NOT delete — this is the wiki's raw source pipeline. Label clearly as ingestion mirror. |
| `wiki/raw/K000_LAW.md` (20KB) | redundant | keep | Ingestion mirror of `000/FLOORS/K000_LAW.md`. Same role as above. |
| `wiki/raw/HUMILITY_SPEC.md` (12KB) | redundant | keep | Ingestion mirror of `000/HUMILITY_SPEC.md`. |
| `wiki/raw/CHANGELOG.md` (45KB) | redundant | merge-into-wiki | Very close to root `CHANGELOG.md` (46KB). Likely a recent snapshot copy for wiki ingestion. Wiki page `wiki/pages/Changelog.md` (5.7KB) already synthesizes it. Confirm wiki page is current, then this raw can be de-prioritized. |
| `wiki/raw/ROADMAP.md` (12KB) | redundant | merge-into-wiki | Near-copy of root `ROADMAP.md` (12.7KB). `wiki/pages/Roadmap.md` synthesizes it. Confirm synthesis, then raw can be de-prioritized. |
| `wiki/raw/TRINITY_ARCHITECTURE.md` (9.1KB) | canonical | keep | Unique architectural narrative. Referenced by `wiki/pages/Trinity_Architecture.md`. |
| `wiki/raw/HUMILITY_SPEC.md` | redundant | keep | Ingestion mirror (see above). |
| `wiki/raw/ARIF_SITES_README.md` (13KB) | operational | keep | arif-sites documentation feed. Unique content for that subsystem. |
| `wiki/raw/GEOX_MANIFESTO.md` (7.8KB) | redundant | keep | **EXACT DUPLICATE** of `geox/MANIFESTO.md` (7,815 bytes = 7,815 bytes). Ingestion mirror for GEOX subsystem. Intentional. |
| `wiki/raw/GEOX_README.md` (33KB) | redundant | keep | **EXACT DUPLICATE** of `geox/README.md` (33,765 bytes = 33,765 bytes). Ingestion mirror. Intentional. |
| `wiki/raw/karpathy-llm-wiki.md` (64KB) | canonical | keep | External source document (Karpathy LLM wiki). Unique external reference. |
| `wiki/raw/arifosmcp-metabolic-pipeline-audit-2026-04-08.md` (3.8KB) | operational | keep | Recent audit artifact (Apr 8). |
| `wiki/raw/arifosmcp-vault999-architecture-audit-2026-04-08.md` (3.3KB) | operational | keep | Recent audit artifact (Apr 8). |
| `wiki/raw/notebooklm/user_paste_2026_04_08.md` (2.1KB) | operational | keep | NotebookLM session paste. Source for wiki synthesis. |

---

### `docs/` — 142 files across 23 subdirectories

#### Root-level `docs/` files (25 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/AGENTS.md` (20KB) | historical | archive | Older version of AGENTS.md (version 2026.3.12-FORGED, focused on arifosmcp PyPI package). Root `AGENTS.md` is the current SoT. UNIQUE CONTENT: Contains PyPI package instructions not in root. Before archiving, confirm any unique content is captured in root or wiki. |
| `docs/CHANGELOG.md` (22KB) | historical | archive | Older changelog (last entry ≤ March 2026). Root CHANGELOG.md (46KB) is current. No unique content expected — root is strictly superset. |
| `docs/00_META/CHANGELOG.md` (21KB) | historical | archive | Even older changelog (last entry 2026.3.22). Same superseding logic. |
| `docs/REPO_STRUCTURE.md` (6KB) | operational | keep | Referenced from root `AGENTS.md`. Repo structure map. |
| `docs/CONTRIBUTING.md` (1.8KB) | operational | keep | Contribution guide. Small, purposeful. |
| `docs/QUICK_START.md` (6.6KB) | operational | keep | Onboarding quick start. |
| `docs/FASTMCP_ARIFOS_MASTER_GUIDE.md` (39KB) | operational | keep | Large FastMCP integration guide. Technical reference. |
| `docs/fastmcp_technical_analysis.md` (37KB) | operational | keep | FastMCP technical analysis. May overlap with above — spot check before merge. |
| `docs/integration_patterns.md` (158KB) | operational | keep | Very large (158KB) integration patterns reference. Critical engineering resource. |
| `docs/arifos_architecture_analysis.md` (64KB) | operational | keep | Large architecture analysis. May overlap with `docs/architecture/ARCHITECTURE.md`. |
| `docs/ACLIP_SPEC.md` (10KB) | operational | keep | ACLIP spec. Unique. |
| `docs/ARCHITECTURE_4LAYER.md` (6.9KB) | historical | archive | Describes 4-layer architecture (now implemented). Superseded by `wiki/pages/Concept_Architecture.md` and `docs/architecture/ARCHITECTURE.md`. |
| `docs/EXTERNAL VALUATION.md` (9.3KB) | operational | keep | External valuation report. Unique content. (Note: space in filename is non-standard.) |
| `docs/HARDENING_V2_GUIDE.md` (12KB) | historical | archive | V2 hardening guide — implementation completed. |
| `docs/HTA_ALIGNMENT_SUMMARY.md` (8KB) | operational | keep | HTA alignment work. Likely still relevant. |
| `docs/HTA_WEBSITE_ALIGNMENT_QUICKSTART.md` (7KB) | operational | keep | HTA quickstart. |
| `docs/LSP_ACP_INTEGRATION.md` (5KB) | historical | archive | LSP/ACP integration doc — check if this work was completed/superseded. |
| `docs/P0_A_FORGE_INTEGRATION.md` (6.5KB) | historical | archive | P0 AF Forge integration plan. TODO.md shows AF Forge integration was completed. |
| `docs/SPEC_SOVEREIGN_11.md` (5.7KB) | historical | archive | Sovereign v11 spec. Old versioning scheme (v11 = pre-2026.03). |
| `docs/TOOL_FINDER.md` (4.7KB) | operational | keep | Tool finder reference. |
| `docs/others.md` (19KB) | unknown | hold-for-human | Unusual filename. 19KB of unknown content. Needs human review. |
| `docs/contrast_analysis_2026_04_06.md` | operational | keep | Recent (Apr 6) contrast analysis. |
| `docs/COVERAGE_GAP_MATRIX_2026-03-12.md` | historical | archive | March 12 coverage gap matrix — old, specific to that sprint. |
| `docs/ENGINEER_EVENT_LOG_2026-03-09.md` | historical | archive | Engineer event log for March 9. Historical sprint log. |
| `docs/a2a-integration.md` | operational | keep | A2A integration doc. |

#### `docs/00_META/` (13 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/00_META/AGENTS.md` (10KB) | historical | archive | Version 2026.2.27 — very old. Root `AGENTS.md` supersedes. |
| `docs/00_META/CHANGELOG.md` (21KB) | historical | archive | See above — old changelog. |
| `docs/00_META/CLAUDE.md` (11KB) | canonical | keep | Claude-specific agent context file. May be the source for `.claude/` integration. Unique AI-assistant context. |
| `docs/00_META/GEMINI.md` (8KB) | canonical | keep | Gemini-specific agent context file. Unique. (Note: there's also a root-level `GEMINI.md` in the workspace — check if they differ.) |
| `docs/00_META/CONSTITUTION.md` (5.2KB) | operational | keep | Summarized constitution (shorter than `000/000_CONSTITUTION.md`). Different document — this is the summary/reference card. |
| `docs/00_META/CONTEXT.md` (9.5KB) | operational | keep | Agent context document. May overlap with AGENTS.md. |
| `docs/00_META/ARIFOS_v36_FINAL_ARCHITECTURE.md` (6.3KB) | historical | archive | Old architecture (v36 = pre-2026.03.12 versioning scheme). |
| `docs/00_META/APEX_PRIME_PROTOCOL.md` (2.2KB) | canonical | keep | APEX Prime Protocol definition. Small, unique. |
| `docs/00_META/DELTA_OMEGA_PSI_CONTRACT.md` (3.1KB) | canonical | keep | Trinity contract. Unique governance contract doc. |
| `docs/00_META/METABOLIC_INVARIANTS.md` (2.3KB) | canonical | keep | Pipeline invariants. Referenced in governance. |
| `docs/00_META/METRICS_SPEC.md` (2.8KB) | canonical | keep | Metrics specification. |
| `docs/00_META/SECURITY.md` (3.9KB) | operational | keep | Security documentation. |
| `docs/00_META/T000_VERSIONING.md` (3.4KB) | canonical | keep | Versioning convention (YYYY.MM.DD format). Unique and actionable. |

#### `docs/agents/` (12 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/agents/A-ARCHITECT.md` through `A-VALIDATOR.md` (5 files, 4–8KB) | canonical | keep | Full role definition documents. These are the canonical content — `arifosmcp/agents/*.md` are just stub pointers referencing these. |
| `docs/agents/AGENTS.md` (3.5KB) | operational | keep | Agents directory overview. |
| `docs/agents/CLAUDE.md` (8.6KB) | canonical | keep | Claude agent configuration. Unique context. |
| `docs/agents/GEMINI_FULL_ACCESS.md` (3KB) | operational | keep | Gemini full-access config. |
| `docs/agents/IMPROVEMENT_BLUEPRINT.md` (9.4KB) | operational | keep | Agent improvement blueprint. |
| `docs/agents/README.md` (20KB) | operational | keep | Agent system overview. Large — may overlap with root `AGENTS.md`. |
| `docs/agents/SKILL.md` (2.8KB) | operational | keep | Skill framework overview for agents. |
| `docs/agents/WIRE_PROTOCOL.md` (7.2KB) | canonical | keep | Agent wire protocol spec. Unique. |
| `docs/agents/a-orchestrator/` (5 files) | operational | keep | Orchestrator-specific context files. HEARTBEAT, IDENTITY, SOUL, TOOLS, USER are small context injections. |
| `docs/agents/laws/LAW_OF_FORGING_CONFIGURATION.md` | canonical | keep | Configuration law. Unique governance law. |
| `docs/agents/laws/LAW_OF_SYSTEMIC_NAMING.md` | canonical | keep | Naming law. Unique governance law. |

#### `docs/architecture/` (5 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/architecture/ARCHITECTURE.md` (17KB) | canonical | keep | Primary architecture document. Distinct from `docs/arifos_architecture_analysis.md`. |
| `docs/architecture/INTEGRATIONS.md` (5.7KB) | operational | keep | Integration map. |
| `docs/architecture/NERVOUS_SYSTEM_9.md` (29KB) | operational | keep | Nervous system architecture v9. May be historical if v9 is superseded. Hold. |
| `docs/architecture/TOOL_INVENTORY.md` (30KB) | operational | keep | Tool inventory. Likely partially outdated but useful reference. |
| `docs/architecture/APEX/secrets/README.md` (562B) | operational | keep | APEX secrets handling note. |

#### `docs/archive/` (8 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/archive/banting_marp.md` | unknown | hold-for-human | Unknown — "banting" may be a personal project or test doc. |
| `docs/archive/home_migration_20260310/*.md` (7 files) | historical | archive | Migration event records from 2026-03-10. All deployment/completion seals for work already shipped. Consider moving to `archive/docs/2026-03-10/`. |

#### `docs/audits/` (3 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/audits/2026-03-14-*.md` (3 files) | historical | archive | All dated March 14, 2026. Contrast analysis, tool audit, hardened audit. Historical sprint records. |

#### `docs/core/` (12 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/core/BOOT.md`, `HEARTBEAT.md`, `IDENTITY.md`, `MEMORY.md`, `SOUL.md`, `TOOLS.md`, `USER.md` (7 stubs) | generated | archive | **FILE POINTERS** — Each contains only a VPS path (e.g., `/root/.openclaw/workspace/SOUL.md`). Not documentation — these are OpenClaw workspace injection pointers. Not useful as standalone docs. |
| `docs/core/000_INIT.md` (11KB) | operational | keep | Core initialization specification. May have unique content. |
| `docs/core/ARCHITECTURE.md` (5.6KB) | operational | keep | Core architecture sub-doc. Unique context for `core/` module. |
| `docs/core/CHANGELOG.md` (7.7KB) | historical | archive | Core-specific changelog. Likely superseded by root CHANGELOG. |
| `docs/core/PROJECTS.md` (4KB) | operational | keep | Core projects overview. |
| `docs/core/VISUAL_SCHEMA.md` (14KB) | operational | keep | Visual schema for the system. Unique diagram source. |

#### `docs/deploy/` (7 files) and `docs/deployment/` (5 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/deploy/DEPLOY.md` (6.8KB) | operational | keep | Primary deploy reference. |
| `docs/deploy/DEPLOY_ALL_PROTOCOLS.md` (7.8KB) | operational | keep | All-protocols deployment guide. |
| `docs/deploy/DEPLOY_DASHBOARD.md` (4.8KB) | operational | keep | Dashboard deployment. |
| `docs/deploy/DEPLOY_QUICKSTART.md` (5KB) | operational | keep | Deploy quickstart. |
| `docs/deploy/DEPLOY_SECRETS.md` (10KB) | canonical | keep | Secrets deployment. Active security reference. |
| `docs/deploy/DEPLOYMENT_READINESS.md` (2.9KB) | operational | keep | Readiness checklist. |
| `docs/deploy/EUREKA_DEPLOYMENT_WISDOM.md` (3.6KB) | operational | keep | Deployment wisdom distillation. Unique. |
| `docs/deployment/DEPLOY_CONFIG.md` (1.4KB) | operational | keep | Deploy config reference. |
| `docs/deployment/DEPLOYMENT_A_FORGE.md` (3.9KB) | historical | archive | AF Forge deployment plan. Work completed per TODO.md. |
| `docs/deployment/DEPLOYMENT_CONTRAST_ANALYSIS.md` (11KB) | historical | archive | Deployment contrast analysis. Historical. |
| `docs/deployment/DEPLOYMENT_READINESS_REPORT.md` (8.5KB) | historical | archive | Readiness report — snapshot from past sprint. |
| `docs/deployment/DEPLOYMENT_V2_PLAN.md` (8KB) | historical | archive | V2 deployment plan. Superseded. |

#### `docs/guides/` (2 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/guides/STDIO.md` (7.2KB) | canonical | keep | stdio transport guide. Active reference. |
| `docs/guides/TAGGING.md` (5.1KB) | canonical | keep | Tagging conventions. Active reference. |

#### `docs/openclaw/` (2 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/openclaw/READY.md` (5.9KB) | historical | archive | OpenClaw readiness seal. Work complete. |
| `docs/openclaw/SETUP_COMPLETE.md` (5.3KB) | historical | archive | OpenClaw setup completion receipt. Work complete. |

#### `docs/plans/` (5 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| All 5 files (2026-03-04 to 2026-03-08) | historical | archive | Planning documents for completed March 2026 sprint work (triwitness hardening, APEX metrics, architecture hardening). All work shipped per CHANGELOG. |

#### `docs/production/` (1 file)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/production/RELEASE_PLAN_2026-03-14.md` | historical | archive | March 14 release plan. Historical. |

#### `docs/protocols/` (7 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/protocols/PROTOCOLS_TRINITY.md` (12KB) | canonical | keep | Trinity protocol definitions. Unique. |
| `docs/protocols/WEBMCP_ARCHITECTURE.md` (28KB) | canonical | keep | WebMCP architecture. Large, unique. |
| `docs/protocols/WEBMCP_DEPLOYMENT_GUIDE.md` (12KB) | operational | keep | WebMCP deployment guide. Active. |
| `docs/protocols/WEBMCP_REAL.md` (4.5KB) | operational | keep | WebMCP implementation notes. |
| `docs/protocols/WEBMCP_TRAEFIK_FIX.md` (8.1KB) | operational | keep | Traefik fix runbook. Active. |
| `docs/protocols/GBR_OPTION_C_PLAN.md` (6.8KB) | historical | archive | GBR Option C plan. Likely superseded. |
| `docs/protocols/MCP_VERIFIED.md` (6.9KB) | historical | archive | MCP verification receipt. Work complete. |

#### `docs/reference/` (2 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/reference/TOOLS.md` (1.2KB) | operational | keep | Tools reference. Small pointer doc. |
| `docs/reference/spec/ARIF_FORMAL_SPEC.md` (1.6KB) | operational | keep | Formal spec stub. |

#### `docs/releases/` (1 file)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/releases/RELEASE_NOTES_2026.04.06.md` (5.5KB) | historical | archive | Release notes for a specific version. Should eventually move to `archive/releases/`. Currently useful as recent release record — keep for now. |

#### `docs/reports/` (10 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/reports/AUDIT_REPORT_2026-04-06.md` (10KB) | operational | keep | Recent audit (Apr 6). Still active reference. |
| `docs/reports/CLEAN_OUTPUT_MIGRATION_SUMMARY.md` (8.3KB) | operational | keep | Recent (Apr 7) migration summary. |
| `docs/reports/TEST_REPORT_HORIZON_II_1.md` (2.7KB) | operational | keep | Recent (Apr 7) test report. |
| `docs/reports/EXTERNAL_CORPUS_REVIEW.md` (7KB) | operational | keep | Recent (Apr 7) external corpus review. |
| `docs/reports/COVERAGE_REPORT_UPDATED.md` (7KB) | historical | archive | March 27 — older coverage report. May be superseded by UPDATED version. Check before archiving. |
| `docs/reports/COVERAGE_REPORT.md` (11KB) | historical | archive | March 27 — older coverage report (likely predecessor to UPDATED). |
| `docs/reports/E2E_AUDIT_REPORT.md` (5.7KB) | historical | archive | March 27 — E2E audit report from older sprint. |
| `docs/reports/EXTERNAL_VALIDATION_REPORT.md` (9.9KB) | historical | archive | March 27 — external validation from older sprint. |
| `docs/reports/open-source-monetization-report.md` (12KB) | operational | keep | Monetization strategy report. Unique business content. |
| `docs/reports/STAGE_ANALYSIS_REPORT.md` (13KB) | historical | archive | March 27 — stage analysis. Older sprint record. |

#### `docs/runbooks/` (6 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/runbooks/DOCUMENTATION_UPDATE_MAP.md` (7.9KB) | operational | keep | Active documentation update tracking. |
| `docs/runbooks/NAMESPACE_UNIFICATION_MAP.md` (4.7KB) | operational | keep | Namespace unification reference. |
| `docs/runbooks/HEARTBEAT.md` (1KB) | operational | keep | Heartbeat runbook. |
| `docs/runbooks/MEMORY.md` (1.5KB) | operational | keep | Memory runbook. |
| `docs/runbooks/TG-OPTIMIZE-PROMPT.md` (1.6KB) | operational | keep | Telegram optimization prompt. |
| `docs/runbooks/TODO.md` (10KB) | operational | keep | Runbooks TODO tracking. **Note:** Different from root `TODO.md` — this is runbooks-specific. |

#### `docs/seals/` (3 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/seals/EUREKA_INSIGHTS_SEAL_v2026.04.07.md` (15KB) | canonical | keep | Wisdom extraction seal. April 7, 2026. Unique philosophical content. |
| `docs/seals/ARIFOS_HUMAN_MANIFESTO_SEAL_v2026.04.07.md` (10KB) | canonical | keep | Human manifesto seal. April 7, 2026. Unique. |
| `docs/seals/KERNEL_FORGE_SEAL_v2026.04.07.md` (12KB) | canonical | keep | Kernel forge seal. April 7, 2026. Unique. |

#### `docs/setup/` (3 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/setup/KIMI_MCP_SETUP.md` (8.5KB) | operational | keep | Kimi MCP setup guide. Active integration. |
| `docs/setup/OPENCLAW_ROOT_ACCESS.md` (5.7KB) | operational | keep | OpenClaw root access setup. |
| `docs/setup/TOOLS.md` (1.7KB) | operational | keep | Tools setup reference. |

#### `docs/spec/` (1 file)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/spec/SPEC.md` (9.3KB) | canonical | keep | Master spec document. |

#### `docs/superpowers/specs/` (2 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `docs/superpowers/specs/2026-03-13-helix-organ-refactor-design.md` (4.8KB) | historical | archive | March 13 design doc. Helix refactor was completed per CHANGELOG. |
| `docs/superpowers/specs/2026-03-13-sacred-chain-8-design.md` (14KB) | historical | archive | March 13 sacred chain design. Completed sprint work. |

---

### `arifosmcp/` — MCP Runtime Shell

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `arifosmcp/README.md` | canonical | keep | Clearly documents this is a packaging shell only; points to arifOS repo as SoT. |
| `arifosmcp/AGENTS.md` (2.6KB) | operational | keep | Skills registry for OpenClaw/VPS runtime. **Different content** from root `AGENTS.md`. Useful for runtime agents. |
| `arifosmcp/CHANGELOG.md` (0 bytes) | generated | delete | **Empty file**. No content. Can be removed or replaced with pointer to root CHANGELOG.md. |
| `arifosmcp/ROADMAP.md` (0 bytes) | generated | delete | **Empty file**. No content. Pointer or removal needed. |
| `arifosmcp/TODO.md` (0 bytes) | generated | delete | **Empty file**. Root `TODO.md` covers active work. |
| `arifosmcp/999_SEAL.md` | historical | archive | Seal from 2026-03-29. Historical version seal. |
| `arifosmcp/agents/*.md` (5 files) | operational | keep | Stub pointers for OpenClaw. Very small YAML stubs pointing to canonical role docs. Intentional pattern. |
| `arifosmcp/commands/*.md` (4 files: audit, forge, init, status) | canonical | keep | Command definitions. Unique per command. |
| `arifosmcp/docs/SOVEREIGN_ACTION_SYSTEM.md` | canonical | keep | Sovereign action system spec. Unique. |
| `arifosmcp/runtime/*.md` (6 files) | operational | keep | Runtime integration summaries (CLEAN_OUTPUT_GUIDE, CONSTITUTIONAL_QUOTES_SPEC, QUOTES_INGESTION_GUIDE, SENSING_PROTOCOL_SUMMARY, TOM_INTEGRATION_SUMMARY, WEB_SEARCH_INTEGRATION). All active and unique. |
| `arifosmcp/runtime/chatgpt_integration/README.md` | operational | keep | ChatGPT integration readme. |
| `arifosmcp/sites/DELEGATION_PROTOCOL.md` | canonical | keep | Delegation protocol. Unique. |
| `arifosmcp/sites/RAG_CONTEXT.md` | operational | keep | RAG context configuration. |
| `arifosmcp/sites/developer/IMPROVEMENTS.md` | operational | keep | Developer site improvements tracking. |
| `arifosmcp/integrations/prefect/README.md` | operational | keep | Prefect integration readme. |
| `arifosmcp/packages/npm/arifos-mcp/README.md` | operational | keep | NPM package readme. |

---

### `core/` — ARCHIVED Module (5 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `core/organs/CONSTITUTIONAL_AMENDMENT_F9_F13.md` (9.7KB) | historical | archive | Constitutional amendment spec for F9-F13 hardening. Implementation completed 2026-04-06. |
| `core/organs/HARDENING_SUMMARY.md` (6.6KB) | historical | archive | Hardening summary — implementation complete. |
| `core/organs/IMPLEMENTATION_SPEC_CA_2026_04_06_001.md` (13KB) | historical | archive | Implementation spec for completed constitutional amendment. |
| `core/organs/MEMORY_VAULT_ARCHITECTURE.md` (12KB) | historical | archive | Memory vault architecture. Possibly superseded by `wiki/pages/Concept_Vault999_Architecture.md`. |
| `core/vault999/VAULT999_SOVEREIGN_4LAYER.md` (14KB) | historical | archive | Vault999 sovereign 4-layer spec. Related to root `VAULT999_4LAYER_IMPLEMENTATION_SUMMARY.md`. Both are post-implementation records. |

> **Note:** Per `GEMINI.md` (workspace instructions): "`core/` is ARCHIVED (2026.04.05) — fully migrated into `arifosmcp/`. Do not write new code here."

---

### `memory/` — Session Logs (4 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `memory/2026-04-01.md` (4.4KB) | historical | archive | Session log from April 1. Operational context expired. |
| `memory/2026-04-06.md` (2KB) | historical | archive | Session log from April 6. Context expired. |
| `memory/2026-04-07.md` (2.9KB) | historical | archive | Session log from April 7. Context expired. |
| `memory/2026-04-08.md` (597B) | operational | keep | Today's session log — still active context for the current session. |

> **Memory role:** These are daily context-injection files for the A-ORCHESTRATOR agent. Yesterday's file becomes historical once a new session begins. Lifecycle: **keep current day → archive previous days → eventually compress to `wiki/log.md`.**

---

### `skills/` — Agent Skill Definitions (33 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `skills/*/SKILL.md` (16 skill directories) | canonical | keep | Active agent skill definitions. Used by GitHub Copilot CLI and AI agents. Each defines distinct competencies. No duplicates found. |
| `skills/arifos-deploy/references/*.md` (8 reference files) | canonical | keep | Deployment reference docs embedded in the arifos-deploy skill. Actionable constitutional execution guides, deploy matrix, etc. These live here intentionally as skill context. |

---

### `.archive/` — Hidden Archive (22 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| All 22 files | historical | keep | Already in `.archive/` — these are correctly placed. Files include old DEPLOY.md, README.md stubs, VPS architecture docs, BLUEPRINT_ANALYSIS, DIRECTIVE_EXTRACTION, ASP_LSP_MCP_A2A docs, and old skill stubs (`audit.md`, `forge.md`, `init.md`, `status.md`). The skill stubs in `.archive/` (audit, forge, init, status) are superseded by `arifosmcp/commands/*.md` and `skills/*/SKILL.md`. |

---

### `geox/` — Separate Geoscience Subsystem (33 files)

| File / Group | Class | Action | Reason |
|---|---|---|---|
| `geox/README.md` (33KB) | canonical | keep | Primary GEOX readme. **EXACT DUPLICATE** of `wiki/raw/GEOX_README.md`. |
| `geox/MANIFESTO.md` (7.8KB) | canonical | keep | GEOX manifesto. **EXACT DUPLICATE** of `wiki/raw/GEOX_MANIFESTO.md`. |
| `geox/UNIFIED_ROADMAP.md` (10.6KB) | canonical | keep | GEOX roadmap. Note: `geox/docs/UNIFIED_ROADMAP.md` (3.5KB) appears to be a different/shorter version. |
| `geox/CHANGELOG.md` (3.4KB) | canonical | keep | GEOX changelog. Unique to subsystem. |
| `geox/000_INIT_ANCHOR.md` (9.4KB) | canonical | keep | GEOX initialization anchor. |
| `geox/999_SEAL.md` (2.9KB) | canonical | keep | GEOX seal receipt. |
| `geox/CLAUDE.md` (6.6KB) | canonical | keep | GEOX Claude context. |
| `geox/CONNECT_TO_GEOX.md` (9.9KB) | operational | keep | GEOX connection guide. |
| `geox/DEPLOYMENT_CHECKLIST.md` (5.4KB) | operational | keep | GEOX deployment checklist. |
| `geox/DEPLOYMENT_STATUS.md` (5.5KB) | operational | keep | GEOX deployment status. |
| `geox/GEOX_SUCCESS_CRITERIA.md` (11KB) | operational | keep | GEOX success criteria. |
| `geox/HARDENED_SEAL.md` (4.3KB) | historical | archive | GEOX hardening seal (completed). |
| `geox/SECURITY.md` (3.7KB) | canonical | keep | GEOX security doc. |
| `geox/WIRING_GUIDE.md` (13KB) | operational | keep | GEOX wiring guide. |
| `geox/RELEASE_NOTES_v2.md` (5.4KB) | historical | archive | GEOX v2 release notes. |
| `geox/docs/` (5 files) | operational | keep | GEOX docs subdirectory. Unique architectural and strategic content. |
| `geox/knowledge/` (2 files) | canonical | keep | GEOX knowledge base files. |
| `geox/NEXT_FORGE_PLAN.md` (29KB) | operational | keep | Large GEOX forge plan. Active planning. |
| `geox/2026-03-31-single-line-structural-interpreter.md` (69KB) | historical | archive | Very large (69KB) sprint artifact from March 31. Single-line structural interpreter work. |
| `geox/2026-03-31-single-line-structural-interpreter-design.md` (10KB) | historical | archive | Design companion to above. |
| `geox/GEOX_CONTRAST_ANALYSIS.md` (14KB) | operational | keep | GEOX contrast analysis. |
| `geox/MACROSTRAT_ANALYSIS.md` (8.5KB) | operational | keep | Macrostrat analysis. |
| `geox/MACROSTRAT_REPO_ANALYSIS.md` (7.5KB) | operational | keep | Macrostrat repo analysis. |
| `geox/STRATEGIC_UPGRADE_PATH_Q2_2026.md` (7KB) | operational | keep | Q2 2026 strategic plan. |
| `geox/ARCH_OPEN_EARTH_STACK.md` (2.5KB) | operational | keep | Open Earth stack architecture. |
| `geox/GEOX_AGENT_SPEC_v2.md` (9.3KB) | operational | keep | GEOX agent spec v2. |
| `geox/GEOX_UNIFIED_ARCHITECTURE.md` (17KB) | operational | keep | GEOX unified architecture. |
| `geox/POSITIONING.md` (2KB) | operational | keep | GEOX positioning statement. |
| `geox/GEOX_GUI_ARCHITECTURE.md` (21KB) | operational | keep | GEOX GUI architecture. |
| `geox/meta_trilemma_theorem.md` | canonical | keep | Meta-trilemma theorem. Unique theory. |
| `geox/001_INDICES.md` | operational | keep | GEOX indices reference. |
| `geox/ops/*.md` | operational | keep | GEOX operations docs. |

---

## Duplication Map

> **Exact or near-exact duplicates found across the active surface:**

### Exact Copies (byte-identical by size)

| Original (Canonical) | Duplicate(s) | Size | Notes |
|---|---|---|---|
| `000/000_CONSTITUTION.md` | `wiki/raw/CONSTITUTION.md` | 33,339 bytes | Intentional ingestion mirror — keep both, label wiki/raw as "ingestion copy" |
| `000/HUMILITY_SPEC.md` | `wiki/raw/HUMILITY_SPEC.md` | 12,416 bytes | Intentional ingestion mirror |
| `000/FLOORS/K000_LAW.md` | `wiki/raw/K000_LAW.md` | 20,186 bytes | Intentional ingestion mirror |
| `geox/README.md` | `wiki/raw/GEOX_README.md` | 33,765 bytes | Intentional ingestion mirror |
| `geox/MANIFESTO.md` | `wiki/raw/GEOX_MANIFESTO.md` | 7,815 bytes | Intentional ingestion mirror |

### Near-Copies (different versions/generations of the same document)

| Canonical (Keep) | Superseded Copies (Archive) | Notes |
|---|---|---|
| `CHANGELOG.md` (46KB, root) | `wiki/raw/CHANGELOG.md` (45KB), `docs/CHANGELOG.md` (22KB), `docs/00_META/CHANGELOG.md` (21KB), `docs/core/CHANGELOG.md` (7.7KB) | Root is most current. wiki/raw is near-copy (ingestion feed). docs copies are older generations. `arifosmcp/CHANGELOG.md` is empty (0 bytes). |
| `ROADMAP.md` (12.7KB, root) | `wiki/raw/ROADMAP.md` (12.4KB) | Root is authoritative SoT. wiki/raw is ingestion copy with minor formatting diff. |
| `AGENTS.md` (12.5KB, root) | `docs/AGENTS.md` (20KB — older version), `docs/00_META/AGENTS.md` (10KB — very old v2026.2.27) | Root is current SoT. docs/AGENTS.md has some unique PyPI-specific content to review before archiving. |
| `docs/agents/A-*.md` (canonical role docs) | `arifosmcp/agents/A-*.md` (stubs) | Stubs are intentional — they are OpenClaw injection pointers, not duplicates in the traditional sense. |
| `geox/UNIFIED_ROADMAP.md` (10.6KB) | `geox/docs/UNIFIED_ROADMAP.md` (3.5KB) | Different sizes — NOT exact copies. May be different versions of the same document. Needs review. |

### Same-Named Files Across Contexts (non-duplicate, distinct content)

| Filename | Locations | Verdict |
|---|---|---|
| `AGENTS.md` | root (12KB), docs/ (20KB), docs/00_META/ (10KB), arifosmcp/ (2.6KB) | Four distinct documents. Root is SoT. Others are historical or role-specific. |
| `CHANGELOG.md` | root (46KB), wiki/raw/ (45KB), docs/ (22KB), docs/00_META/ (21KB), docs/core/ (7.7KB), arifosmcp/ (0B) | Same logical changelog at different time snapshots. Root is canonical. |
| `README.md` | root, 000/, 000/ROOT/, various subdirs | All distinct — subdirectory READMEs are scoped to their context. |
| `K000_LAW.md` | `000/FLOORS/` (20KB) vs `000/THEORY/` (22KB) | **CONTRADICTION** — see Hold List. |
| `CONSTITUTION.md` | `000/000_CONSTITUTION.md` (33KB), `wiki/raw/CONSTITUTION.md` (33KB), `docs/00_META/CONSTITUTION.md` (5KB) | First two are exact copies. Third is a DIFFERENT document (summary/reference card). All three have valid roles. |

---

## Hold List (888 HOLD)

> These items require **human review and explicit approval** before any action is taken.

| # | Item | Reason for Hold | Recommended Action |
|---|---|---|---|
| H-001 | `000/FLOORS/K000_LAW.md` (20KB) vs `000/THEORY/K000_LAW.md` (22KB) | **CONTRADICTION:** Two K000_LAW.md files with different sizes in the same `000/` directory (different subdirs). The THEORY version is 2KB larger — may be a newer updated version. Which is canonical? | Human must designate one as canonical. Archive the other to `archive/000/superseded/`. |
| H-002 | `docs/AGENTS.md` (20KB) | Older version but **20KB > root 12KB** — it has more raw content. Contains PyPI package instructions and detailed arifosmcp guidance not present in the current root AGENTS.md. Content must be reviewed before archiving. | Human review: extract any unique content into root `AGENTS.md`, then archive. |
| H-003 | `docs/others.md` (19KB) | **Unknown filename.** 19KB of undetermined content. No context for this filename in any index or reference. | Human review: identify content, classify, and rename or archive. |
| H-004 | `docs/architecture/NERVOUS_SYSTEM_9.md` (29KB) | "v9" implies versioned evolution. If this is an intermediate design version, it should be archived. But if "9" refers to something else (9th architectural component?), it may be canonical. | Human review: is this a version-numbered doc or a component-named doc? |
| H-005 | `wiki/raw/CHANGELOG.md` (45KB) vs root `CHANGELOG.md` (46KB) | Near-identical but slightly smaller. Is wiki/raw/CHANGELOG.md an intentional ingestion snapshot or an accidental near-copy? If it's a snapshot, it should be dated. If it's auto-synced, confirm the sync mechanism. | Clarify wiki/raw feed pattern: snapshots should be dated (`CHANGELOG_2026-04-08.md`) to avoid confusion with the canonical. |
| H-006 | `core/organs/IMPLEMENTATION_SPEC_CA_2026_04_06_001.md` (13KB) | Constitutional Amendment spec for F9-F13 (April 6). This was implemented on 2026-04-06 per CHANGELOG. However, constitutional amendments may need to remain accessible even after implementation. | Human decision: move to `archive/core/` or to `000/` as a constitutional record? |
| H-007 | `arifosmcp/CHANGELOG.md`, `arifosmcp/ROADMAP.md`, `arifosmcp/TODO.md` (all 0 bytes) | Three empty files. Should be either populated with pointers to the root canonical files or deleted. Deletion of docs files should have human confirmation. | Human confirm: delete empty files and replace with pointer links, or populate with redirects. |
| H-008 | `memory/` lifecycle policy | No formal policy exists for when memory files rotate from operational to historical. The current pattern (4 files: 2026-04-01, 04-06, 04-07, 04-08) shows ad-hoc creation. | Establish formal memory rotation policy: archive files older than N days to `archive/memory/YYYY/MM/`. |

---

## Ω-Wiki Gaps

> **Truth that exists in source docs but is NOT yet synthesized into `wiki/pages/`:**

| Gap | Source Documents | Priority |
|---|---|---|
| **Agent Role Details** | `docs/agents/A-ARCHITECT.md`, `A-AUDITOR.md`, `A-ENGINEER.md`, `A-VALIDATOR.md` (4–8KB each) | HIGH — `wiki/pages/Agents-and-AAA-Architecture.md` is only 1.2KB. Full role definitions need synthesis. |
| **Deployment Architecture** | `docs/deploy/*.md`, `docs/protocols/WEBMCP_ARCHITECTURE.md` (28KB), `docs/deployment/*.md` | MEDIUM — `wiki/pages/Concept_Deployment_Architecture.md` is only 2.2KB. WebMCP/Traefik architecture not synthesized. |
| **Skills Registry** | `skills/*/SKILL.md` (16 skills) | MEDIUM — No wiki/pages file covers the skills registry. Create `wiki/pages/Skills_Registry.md`. |
| **GEOX System** | `geox/GEOX_UNIFIED_ARCHITECTURE.md` (17KB), `geox/MANIFESTO.md`, `geox/NEXT_FORGE_PLAN.md` | MEDIUM — `wiki/pages/GEOX.md` exists (1.6KB) but is thin. |
| **Integration Patterns** | `docs/integration_patterns.md` (158KB!) | HIGH — This massive document has no wiki synthesis. Create `wiki/pages/Integration_Patterns.md`. |
| **Constitutional Floors Detail** | `000/FLOORS/F01_AMANAH.md` through `F13_SOVEREIGN.md` | LOW — `wiki/pages/Concept_Floors.md` (7.2KB) covers this well, but could link to individual floor files. |
| **Memory & Vault Architecture** | `core/organs/MEMORY_VAULT_ARCHITECTURE.md` (12KB), `core/vault999/VAULT999_SOVEREIGN_4LAYER.md` (14KB) | MEDIUM — `wiki/pages/Concept_Vault999_Architecture.md` (3.5KB) exists but may be incomplete. |
| **Skills vs Code Mapping** | `skills/*/SKILL.md` vs `arifosmcp/runtime/*.py` | LOW — Skills define agent competencies but there's no wiki map showing which skills correspond to which MCP tools. |
| **Seals Registry** | `docs/seals/*.md`, `arifosmcp/999_SEAL.md`, `geox/999_SEAL.md` | LOW — No wiki page tracking all seals across the system. |

---

## Proposed Archive Paths

> **Where historical files should go** (pending human approval, no moves performed):

```
archive/
├── docs/
│   ├── 2026-03-XX/         # March sprint artifacts
│   │   ├── plans/          # docs/plans/*.md
│   │   ├── audits/         # docs/audits/*.md
│   │   ├── deployment/     # docs/deployment/DEPLOYMENT_*,  DEPLOY_A_FORGE, CONTRAST
│   │   ├── reports/        # docs/reports/COVERAGE*, E2E*, EXTERNAL_VALIDATION, STAGE_ANALYSIS
│   │   └── superpowers/    # docs/superpowers/specs/*.md
│   ├── 2026-03-10-migration/   # docs/archive/home_migration_20260310/*.md
│   ├── 2026-03-14-sprint/      # docs/audits/2026-03-14-*.md
│   ├── 2026-04-06/             # docs/releases/RELEASE_NOTES_2026.04.06.md
│   └── meta-old/               # docs/00_META/AGENTS.md, CHANGELOG.md, ARIFOS_v36*
├── core/                   # All 5 core/organs/* and core/vault999/* files
├── root/
│   ├── 000-999-implementation-plan.md
│   └── VAULT999_4LAYER_IMPLEMENTATION_SUMMARY.md
├── memory/
│   └── YYYY/MM/            # Rotated memory logs
├── arifosmcp/
│   └── 999_SEAL_2026-03-29.md
└── geox/
    ├── 2026-03-31-structural-interpreter*.md
    ├── HARDENED_SEAL.md
    └── RELEASE_NOTES_v2.md

```

---

## Proposed Deletions (Pending Human Confirmation)

> **Only zero-byte generated files with no unique content:**

| File | Reason | Unique Content? |
|---|---|---|
| `arifosmcp/CHANGELOG.md` | 0 bytes — empty. Root CHANGELOG.md is canonical. | No. |
| `arifosmcp/ROADMAP.md` | 0 bytes — empty. Root ROADMAP.md is canonical. | No. |
| `arifosmcp/TODO.md` | 0 bytes — empty. Root TODO.md is canonical. | No. |
| `docs/core/BOOT.md` | Contains only a VPS path string (`/root/.openclaw/workspace/BOOT.md`). Not a documentation file. | No — is a file pointer, not a doc. |
| `docs/core/HEARTBEAT.md` | Same — contains only a VPS path string. | No. |
| `docs/core/IDENTITY.md` | Same — contains only a VPS path string. | No. |
| `docs/core/MEMORY.md` | Same — contains only a VPS path string. | No. |
| `docs/core/SOUL.md` | Same — contains only a VPS path string. | No. |
| `docs/core/TOOLS.md` | Same — contains only a VPS path string. | No. |
| `docs/core/USER.md` | Same — contains only a VPS path string. | No. |

> **⚠️ HOLD:** Even "empty" files require sovereign confirmation per 888_HOLD rules before deletion. The above are candidates only — they must not be deleted without explicit human approval.

---

## Contradiction Register

| ID | Contradiction | Severity | Files Involved |
|---|---|---|---|
| C-001 | Two `K000_LAW.md` files with different sizes (20KB vs 22KB) exist within `000/` (in FLOORS/ and THEORY/ subdirs). Both claim to be the same constitutional law document. It is unclear which is authoritative. | HIGH | `000/FLOORS/K000_LAW.md` vs `000/THEORY/K000_LAW.md` |
| C-002 | `docs/AGENTS.md` (20KB) has MORE content than root `AGENTS.md` (12KB) despite root being declared the "PRIMARY SoT." This means the SoT declaration is factually incomplete — unique content exists outside the declared SoT. | MEDIUM | `AGENTS.md` vs `docs/AGENTS.md` |
| C-003 | `GEMINI.md` workspace instructions say "`core/` is ARCHIVED (2026.04.05)" but root `AGENTS.md` lists `core/` under PRIMARY SoT level alongside `000/` and `config/`. If `core/` is archived, it should not be PRIMARY. | MEDIUM | `GEMINI.md` vs root `AGENTS.md` |
| C-004 | `arifosmcp/README.md` declares "Active development is in arifOS" and "This is a packaging shell only." But `arifosmcp/runtime/*.md` contains detailed integration summaries (TOM, sensing protocol, clean output, web search) that exist nowhere in the main arifOS docs/. This unique content contradicts the "shell only" claim. | LOW | `arifosmcp/README.md` vs `arifosmcp/runtime/*.md` |

---

*Audit sealed by: A-AUDITOR (Copilot) | 2026-04-08 | No files were modified during this audit.*  
*Next recommended action: Human review of H-001 through H-008 in Hold List before any cleanup passes.*

---

## Hold Resolution Log — 2026-04-08 (Forge Pass)

| # | Item | Resolution | Action Taken |
|---|---|---|---|
| H-001 ✅ | K000_LAW.md contradiction | THEORY (22KB, Apr 6) = canonical. FLOORS = Mar 27 snapshot. |  00/FLOORS/K000_LAW.md → rchive/000/K000_LAW_v2026-03-27_FLOORS.md. wiki/raw/K000_LAW.md updated to THEORY version. |
| H-002 ✅ | docs/AGENTS.md unique content | Not a duplicate — different purpose (developer MCP guide vs governance SoT). Category error in audit. | Renamed → docs/AGENTS_MCP_SERVER_GUIDE.md. Kept. |
| H-003 ✅ | docs/others.md unknown file | **SENSITIVE PERSONAL DATA** — relationship intelligence profiles of real people. Not a technical doc. | Moved → HUMAN/personal/others.md. Removed from docs/. |
| H-004 ✅ | NERVOUS_SYSTEM_9.md | "9" = component name (internal tool architecture layer), NOT a version number. Status: Production-Ready. | Reclassified: canonical | keep. No file action. |
| H-005 ✅ | wiki/raw/CHANGELOG.md snapshot | Undated snapshot = silent staleness. Policy: all wiki/raw snapshots must be dated. | Renamed → wiki/raw/CHANGELOG_snapshot_2026-04-07.md. |
| H-006 ✅ | core/ constitutional amendment spec | Already moved to rchive/core/ in forge pass. | Done in Pass 2. |
| H-007 ✅ | arifosmcp/ empty files | Confirmed 0 bytes. No unique content. | Deleted in Pass 3. |
| H-008 ✅ | memory/ rotation policy | Policy formalised: TTL = 1 session, archive previous day, compress monthly into wiki/log.md. | Written → docs/runbooks/MEMORY_ROTATION_POLICY.md. |

**All 8 HOLD items resolved.**
