# arifOS v2026.05.05-SSCT — Sole Source Constitutional Track

**Seal date:** 2026-05-05
**Tag target:** `v2026.05.05-ssct`
**Commit to:** `main`

---

## Version Identity

- **Version:** `2026.05.05-SSCT`
- **Schema:** `arifos-ssct-v2026.05.05-kanon-ssct`
- **Source:** `arifosmcp.constitutional_map.CANONICAL_TOOLS` (sole source of truth)
- **MCP surface:** 13 canonical tools, 100% schema coverage
- **Constitutional floors:** F01–F13 (all ≥ 2 tools each, zero thin floors)
- **Motto:** `DITEMPA BUKAN DIBERI — Forged, Not Given`

---

## What Changed

### 1. PHASE 1 — Single Source of Truth (SSCT)

**Archived legacy files** (deprecated, read-only, F1 Amanah guard active):

| File | Archived As | Legacy Naming |
|------|-------------|---------------|
| `/root/arifOS/constitution.py` | `_archived/constitution_v2_deprecated.py` | `void_000`, `anchor_111` |
| `/root/arifOS/capability.py` | `_archived/capability_legacy_deprecated.py` | `arifos.*` dotted aliases |
| `/root/arifOS/arifosmcp/capability_map.py` | `_archived/capability_map_deprecated.py` | duplicate alias map |

**Active sole source:**
- `arifosmcp/constitutional_map.py` — 13-tool canonical registry, floor bindings, Eureka insights, schema contracts

**Archived files MUST NOT be imported at runtime.** They are kept for historical audit only.

### 2. PHASE 2 — Floor Rebalancing (Zero Thin Floors)

All 13 floors now have ≥ 2 tools covering them:

| Floor | Tools | Status |
|-------|-------|--------|
| F01 AMANAH | 6 | ✅ (session_init, kernel_route, memory_recall, gateway_connect, vault_seal, forge_execute) |
| F02 TRUTH | 3 | ✅ (sense_observe, evidence_fetch, mind_reason) |
| F03 WITNESS | 3 | ✅ FIXED (was 2: added kernel_route) |
| F04 CLARITY | 3 | ✅ (kernel_route, reply_compose, ops_measure) |
| F05 PEACE | 2 | ✅ FIXED (was 1: added evidence_fetch) |
| F06 EMPATHY | 2 | ✅ (heart_critique, reply_compose) |
| F07 HUMILITY | 2 | ✅ (sense_observe, mind_reason) |
| F08 GENIUS | 2 | ✅ (mind_reason, memory_recall) |
| F09 ANTIHANTU | 2 | ✅ FIXED (was 1: added reply_compose) |
| F10 ONTOLOGY | 2 | ✅ FIXED (was 1: added mind_reason) |
| F11 AUTH | 4 | ✅ (session_init, judge_deliberate, vault_seal, forge_execute) |
| F12 INJECTION | 2 | ✅ (session_init, evidence_fetch) |
| F13 SOVEREIGN | 3 | ✅ (judge_deliberate, vault_seal, forge_execute) |

### 3. PHASE 3 — Schema I/O Canonicalization

- **`_TOOL_INPUT_SCHEMAS`** — 13/13 tools, 100% coverage. All fields typed. F12 `[F12: sanitized]` annotations on all string inputs.
- **`_TOOL_OUTPUT_SCHEMAS`** — 13/13 tools, 100% coverage. Nine-Signal envelope + verdict + reasons contract.
- **`validate_tool_response_schema()`** — now enforces F10 `omega_ont` field presence in nine_signal block.
- **`check_schema_coverage()`** — now also checks floor coverage (thin floors = CI failure).
- **`get_floor_coverage()`** — new query function, returns which tools cover each floor.
- **Nine-Signal fields:** `tau, omega, delta_S, w3, p2, kappa, c_dark, omega_ont`

### 4. Eureka Insights Wired to Floors

Every tool now carries `eureka_insight` field wiring its floor thresholds to the physics equations from `EUREKA_INSIGHTS_SEAL_v2026.04.07`:

- F1: `∃ undo(a)` — irreversibility requires explicit human ack
- F2: `τ ≥ 0.99` — truth score threshold
- F3: `W₃ = ∛(Human × AI × Earth) ≥ 0.75` — tri-witness consensus
- F4: `ΔS ≤ 0` — entropy must decrease for SEAL
- F5: `P² ≥ 1.0` — safety margin baseline
- F6: `κᵣ ≥ 0.70` — RASA empathy protocol
- F7: `Ω ∈ [0.03, 0.05]` — healthy uncertainty band
- F8: `G = capability × ethics × continuity × resilience² ≥ 0.80`
- F9: `C_dark ≤ 0.30` — dark pattern detection threshold
- F10: structural coherence enforced
- F11: identity verification mandatory
- F12: `injection_probability < 0.85`
- F13: human veto absolute

### 5. Version String Uniformity

All hardcoded version strings updated to `v2026.05.05-SSCT`:

| File | Field |
|------|-------|
| `arifosmcp/__init__.py` | `__version__` |
| `arifosmcp/runtime/DNA.py` | `VERSION` |
| `arifosmcp/runtime/jwt_auth.py` | header comment |
| `arifosmcp/runtime/floor.py` | header comment + floor status |
| `arifosmcp/runtime/tools.py` | constitution_id, changelog version, env default |
| `tool_registry.json` | `_schema`, `_source` |

### 6. tool_registry.json Regenerated

- `_schema`: `arifos-ssct-v2026.05.05-kanon-ssct`
- `_source`: `arifosmcp.constitutional_map.CANONICAL_TOOLS`
- Canonical operational metadata from `tool_charter.py` merged in
- Eureka insights embedded per tool

---

## Quality Gates

| Gate | Status |
|------|--------|
| `check_schema_coverage()` PASS | ✅ 100% input + output |
| Thin floors | ✅ 0 (all F01–F13 ≥ 2 tools) |
| `constitutional_map.py` imports clean | ✅ |
| Pytest (310 passed, 1 pre-existing qdrant env issue) | ✅ |
| MCP `/health` — 13 tools loaded | ✅ |

---

## Migration Notes

- **Archived files** (`_archived/`) are read-only. Do not import them.
- **Legacy aliases** (`void_000`, `anchor_111`, `arifos.*` dotted names) are no longer valid. Use `arif_*` canonical names.
- **Runtime drift detected** means the running container image was older than git HEAD. Image rebuild required.

---

**DITEMPA BUKAN DIBERI — Intelligence is forged, not given.**
