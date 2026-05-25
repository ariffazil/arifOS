# LEGACY_EXTRACTION_MAP.md
**Mission:** Map every significant artifact in `arifosmcp/` for extraction decision.
**Date:** 2026-05-25
**Rule:** Extract insight only. No direct copy unless criteria are met.

---

## arifosmcp/ Full Directory Map

| Path | Classification | Extraction Action |
|------|---------------|-------------------|
| `abi/` | UNKNOWN | Review — may contain ABI compatibility layer |
| `agents/` | LEGACY SOURCE | Mine for agent patterns; re-implement, don't copy |
| `agentzero/` | ASI DELIBERATIVE | APEX review required before any extraction |
| `apps/` | LEGACY SOURCE | Review; some may be canonical candidates |
| `archive/` | DEPRECATED | Archive only; do not extract |
| `arifos/` | CORE KERNEL | HIGH VALUE — review for floor/governance logic |
| `audit/` | OPERATIONAL | Extract audit patterns if still relevant |
| `commands/` | UNKNOWN | Review for CLI patterns |
| `config/` | LEGACY CONFIG | Extract valid config values; discard old paths |
| `contracts/` | HIGH VALUE | Extract schemas; re-register in `arifos_mcp/manifests/` |
| `core/` | HIGH VALUE | Review for constitutional enforcement logic |
| `data/` | UNKNOWN | Review for seed/data artifacts |
| `docs/` | LEGACY DOCS | Extract still-valid docs to `arifos_mcp/docs/` |
| `evals/` | EVALUATION | Keep for eval continuity; separate concern |
| `evidence/` | EVIDENCE STORE | F-WEB evidence receipts — preserve |
| `infrastructure/` | INFRA | Review for infra patterns; may be VPS-specific |
| `integrations/` | INTEGRATIONS | Extract valid integrations; re-register |
| `intelligence/` | COGNITIVE | Review 9-Sense / thinking session logic |
| `memory/` | MEMORY LAYER | Review architecture; Qdrant/PG patterns |
| `metadata/` | METADATA | Extract if contains tool/surface metadata |
| `migrations/` | MIGRATION ARTIFACTS | Historical only; archive |
| `models/` | MODEL CONFIGS | Review; may contain provider configs |
| `packages/` | UNKNOWN | Review contents |
| `prompts/` | HIGH VALUE | Extract constitutional prompt templates |
| `protocols/` | LEGACY PROTOCOL | A2A protocol patterns; may be superseded |
| `providers/` | HIGH VALUE | LLM provider configs — extract valid ones |
| `resources/` | MCP RESOURCES | Review; some may be canonical candidates |
| `runtime/` | RUNTIME | Review; server bootstrapping logic |
| `schema/` | SCHEMA | Review; Pydantic schemas |
| `schemas/` | HIGH VALUE | Extract schemas; re-register in `arifos_mcp/schemas/` |
| `sessions/` | SESSION ARTIFACTS | See special items below |
| `sites/` | PUBLIC SURFACES | Belongs to `arif-sites` — do not extract |
| `specs/` | SPECS | Review for canonical tool specs |
| `static/` | STATIC ASSETS | Extract if non-duplicate |
| `telemetry/` | TELEMETRY | Review for Prometheus/observability patterns |
| `tests/` | HIGH VALUE | Extract test patterns; adapt to arifos_mcp/ |
| `tools/` | HIGH VALUE | One-by-one: validate → re-register → test |
| `transforms/` | UNKNOWN | Review for data transform patterns |
| `transport/` | TRANSPORT | Review for MCP transport implementations |
| `widgets/` | UI COMPONENTS | Belongs to AAA/frontend — do not extract |

---

## Special Items in arifosmcp/

| File | Classification | Extraction Action |
|------|---------------|-------------------|
| `ARIFOS_MCP_AGENT_SEED.json` | CONFIG ARTIFACT | Extract valid config values to `arifos_mcp/manifests/agent_config.json` |
| `ARIFOS_MCP_FINAL_SEAL.md` | HISTORICAL RECEIPT | Archive; not current authority |
| `sessions/INFRA_NOTICE.md` | INFRA NOTICE | Review; migrate valid content to `arifos_mcp/docs/` |
| `VAULT999/` | APPEND-ONLY LEDGER | Preserve; vault-ops review only |
| `.env` | SECRETS | DO NOT EXTRACT; confirm purge/rotate |
| `pyproject.toml` | PACKAGE CONFIG | Extract dependency list for audit only |
| `Dockerfile` | LEGACY DOCKERFILE | Historical reference; arifos_mcp has its own |

---

## Priority Extraction Queue

### Tier 1 — Critical:
1. `schemas/` → `arifos_mcp/schemas/` (Pydantic validation)
2. `contracts/` → `arifos_mcp/manifests/` (tool contracts)
3. `tools/` → review for canonical tool surface
4. `prompts/` → `arifos_mcp/prompts/` (constitutional templates)

### Tier 2 — High Value:
5. `core/` → review for floor enforcement patterns
6. `providers/` → extract valid LLM configs
7. `memory/` → review memory layer architecture
8. `resources/` → review MCP resources

### Tier 3 — Review Only:
9. `intelligence/` → 9-Sense cognitive patterns
10. `runtime/` → server bootstrapping
11. `config/` → valid config values
12. `tests/` → test patterns (adapt, don't copy)

### Tier 4 — Archive / Do Not Extract:
- `archive/` → archive only
- `sites/` → belongs to arif-sites
- `widgets/` → belongs to AAA
- `.env` → secrets, do not touch
- `VAULT999/` → vault-ops review

---

## Extraction Gates

Before extracting from `arifosmcp/` to `arifos_mcp/`, each item must pass:

1. Is it registered in arifos_mcp/manifests/ ?
2. Does it have F1-F13 floor classification ?
3. Does it have Pydantic input/output schema ?
4. Does it use canonical arif_* tool naming ?
5. Does it pass arifos_mcp/ test suite ?
6. Does it increase or decrease runtime drift ?

If ANY answer is NO → archive, do not extract.

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
