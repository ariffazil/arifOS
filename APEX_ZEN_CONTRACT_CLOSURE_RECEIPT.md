# APEX-ZEN CONTRACT CLOSURE RECEIPT

**Mission:** APEX-777 — ZEN CONTRACT CLOSURE
**Target invariant:** RUNTIME TRUTH == DISCOVERY TRUTH == CLIENT TRUTH == AUTHORITY TRUTH
**Instrument:** `scripts/contract_closure.py` (`measure` | `receipt` | `verify`)
**Repo:** `ariffazil/arifos` · **contract_epoch:** `174c76c82@2026-09-18T07:15:18+08:00`

---

## BEFORE

Measured with `scripts/contract_closure.py measure` before any closure edit.

```
tool_count            : 8
alias_count           : 1
phantom_count         : 0
missing_count         : 0
schema_mismatch_count : 7
canonical_manifest_hash : 836a918a2f9cceab
runtime_surface_hash    : 836a918a2f9cceab   (live wire already aligned — STEP 3)
```

The 7 mode-schema mismatches (all now closed):

| Surface | Tool | Drift |
|---|---|---|
| tools_sot | arif_memory | missing `metabolize` (8 vs 9) |
| tools_sot | arif_route | stale `route, bridge` (canonical `[]`) |
| discovery | arif_init | missing `canary, preflight, triage, opt_out_profiling` (7 vs 11) |
| discovery | arif_observe | `repo_map` vs `fetch, hybrid_discovery` |
| discovery | arif_think | `critique` vs `simulate, wonder, atlas` |
| discovery | arif_judge | `armor, notify, probe, rules` vs `intercept, escalate` |
| charter | arif_memory | missing `metabolize` |

**Root cause:** four surfaces each hand-copied the mode ABI from the owner at
different times. The owner (`constitutional_map.py`) had advanced (STEP 3 added
`audit` + `metabolize`; absorptions collapsed 19→8 public tools); the copies
had not been regenerated.

---

## AFTER

```
tool_count            : 8
alias_count           : 1
phantom_count         : 0
missing_count         : 0
schema_mismatch_count : 0        ← acceptance: =0
canonical_manifest_hash : 836a918a2f9cceab
runtime_surface_hash    : 836a918a2f9cceab   ← canonical discovery drift = 0
```

Mode count by tool (canonical): `arif_init`=11 · `arif_observe`=8 · `arif_think`=12 ·
`arif_route`=0 · `arif_memory`=9 · `arif_judge`=5 · `arif_forge`=7 · `arif_seal`=6.

`arif_memory` canonical public modes now agree everywhere:
`recall, inspect, attest, remember, promote, revise, forget, audit, metabolize`.

### What changed

1. **`arifosmcp/tool_discovery.py`** — added `expose` flag + `INTERNAL_TOOLS`
   set + `_reconcile_with_canonical()`: the 8 public tools' `modes` and
   `deprecated_aliases` are now **DERIVED from `constitutional_map`** at import
   (no hand-copied mode arrays). The 11 absorbed/internal tools are demoted
   `expose=False`; `get_tool_discovery_resource()` advertises only the 8.
2. **`arifosmcp/runtime/public_registry.py`** — the live `arif_memory`
   `inputSchema.mode.enum` + description now **DERIVE from `CANONICAL_TOOLS`**
   (was a hardcoded 9-mode list). This closes the *runtime wire* to the owner.
3. **`arifosmcp/tool_charter.py`** — added `metabolize` to `arif_memory`
   `modes` (purpose + `allowed_values`). This also fixes the runtime
   `mode_purpose` (which is built from the charter).
4. **`tools_sot.yaml`** — regenerated via `scripts/gen_tools_sot.py` (drops
   stale `route/bridge`, adds `metabolize`, syncs descriptions).
5. **`arifosmcp/core/enforcement/risk_classifier.py`** — authority fixes
   (see Authority falsification below).

---

## DELETED COMPLEXITY

| Artifact | Class | Action |
|---|---|---|
| `tool_discovery` hand-copied `modes` (4 tools drifted) | DERIVED | now generated from owner at import |
| `public_registry` hardcoded `arif_memory` enum | DERIVED | now reads `CANONICAL_TOOLS` |
| `tools_sot.yaml` stale content | DERIVED | regenerated |
| `.github/workflows/drift-monitor.yml` (CANON_APEX_V2) | STALE | retired → `_retired/` |
| `.github/workflows/08-runtime-drift.yml` (SSH SHA drift) | STALE | retired → `_retired/` |

**Retired (superseded canon / ghost dependency), not resurrected:** the
CANON_APEX_V2 drift monitor installed a ghost PyPI package (`supabase-py`) and
watched a superseded canon (issue #803). Collapsed onto the single instrument.

### Remaining duplicates (classified, NOT yet removed — see NEXT ACTION)

| Artifact | Class | Note |
|---|---|---|
| `constitutional_map.py CANONICAL_TOOLS["modes"]` | **OWNER** | single source of the public mode ABI |
| `tool_charter.py` mode *prose* (purpose/params) | DERIVED(keys) | keys now guarded by `verify`; prose is enrichment |
| `public_surface.py` `MCP_SPEC_VERSION_*` | **OWNER** | protocol-version table |
| `tools.py` `_MCP_SPEC_VERSION` (dup of public_surface) | STALE | duplicate protocol constant |
| `geox_bridge.py`/`well_bridge.py`/`rest_routes.py` `"2025-03-26"` | STALE | hardcoded legacy protocol strings |
| `tools.py:23136` "19 tools" comment | STALE | pre-collapse count in a comment |
| `generate_tool_manifest.py` prose `"8"`/`"23"`/`v2026.07.24` | STALE | counts already derived from CANONICAL_TOOLS; prose version string stale |
| `build/`, `dist/`, `arifos.egg-info/` | CACHE | gitignored build output — invalidate by rebuild (contract_epoch) |
| `docs/canon/CANON_APEX_V2/**` | STALE | superseded canon bundle (already marked SUPERSEDED in `GENESIS/APEX_T000.md`) |

---

## CANONICAL OWNER

**One owner of the public ABI:**

```
arifosmcp/constitutional_map.py  →  CANONICAL_TOOLS["<tool>"] (expose=True)
                                     ├── modes                  (public mode enum)
                                     └── deprecated_aliases     (wire alias table)
```

Downstream surfaces and how they track the owner:

| Surface | Mechanism |
|---|---|
| runtime wire `inputSchema.mode.enum` | `public_registry.py` reads `CANONICAL_TOOLS` |
| `tools_sot.yaml` (manifest) | `scripts/gen_tools_sot.py` regenerates |
| `tool_discovery.py` (LLM discovery) | `_reconcile_with_canonical()` at import |
| `tool_charter.py` (authority prose) | `verify` guards mode-key coverage |
| `llms.txt` (generate_tool_manifest.py) | reads `CANONICAL_TOOLS` |

---

## GOLDEN RESTART RECEIPT

`scripts/contract_closure.py receipt` — one machine-readable PASS/HOLD receipt
bound to commit SHA + runtime hash + contract epoch + timestamp + test hash.
This is the post-restart proof path (full runtime check runs on the VPS;
`--local` is the repo-side CI variant).

```json
{
  "verdict": "PASS",
  "contract_epoch": "174c76c82@2026-09-18T07:15:18+08:00",
  "commit_sha": "174c76c82",
  "runtime_hash": "836a918a2f9cceab",
  "canonical_manifest_hash": "836a918a2f9cceab",
  "test_hash": "6b71c730deef62a5",
  "metrics": { "tool_count": 8, "phantom_count": 0, "missing_count": 0,
               "schema_mismatch_count": 0, "alias_count": 1 },
  "authority_probe": {
    "falsification_pair_ok": true,
    "alias_policy_identical": true,
    "outcomes": {
      "forge_query":                { "action_class": "OBSERVE",      "policy": "OBSERVE_ALLOWED" },
      "forge_engineer":             { "action_class": "IRREVERSIBLE", "policy": "HOLD" },
      "forge_query_sdk_alias":      { "action_class": "OBSERVE",      "policy": "OBSERVE_ALLOWED" },
      "forge_engineer_sdk_alias":   { "action_class": "IRREVERSIBLE", "policy": "HOLD" }
    }
  }
}
```

Receipt chain: `health → canonical tools/list → mode-schema equality →
legacy alias resolution (no discovery pollution) → memory contract →
authority classification → receipt lineage`.

### Authority falsification pair (OBSERVE_ONLY, no arif_forge invocation)

- `arif_forge(mode=query)` → **OBSERVE / allowed as observation**
- `arif_forge(mode=engineer)` → **HOLD** (T5 mutation, clamped)
- canonical name vs SDK-alias (`arifos_arif_forge`) → **identical policy** (alias
  normalization added to `risk_classifier.classify_tool`; previously the
  `arifos_` alias bypassed the T5 gate and fell to the permissive OBSERVE
  heuristic — an F11/F13 authority leak, now closed).

---

## DRIFT FALSIFICATION

`scripts/contract_closure.py verify` — exit 0 = green, exit 1 = red.
Fails intentionally on: phantom tool · public mode disappears · connector/runtime
hash divergence · alias bypasses policy · canonical count change without epoch change.

Green run: `verify` → exit 0 (`{"drift": false, "failures": []}`).

Deliberate reversible mismatches (each injected, proven red, then restored):

| # | Injected | verify exit | Detected failure |
|---|---|---|---|
| A | remove `metabolize` from `tools_sot.yaml arif_memory` | 1 | "mode schema mismatch … missing_modes: ['metabolize']" |
| B | append `arif_phantom` tool to `tools_sot.yaml` | 1 | "PHANTOM tools appear: [arif_phantom]" |
| C | disable `arifos_` alias normalization in `risk_classifier` | 1 | "alias bypasses policy / falsification pair failed" |

All three restored; `verify` returns to exit 0 after each.

CI wiring: `.github/workflows/contract-closure.yml` runs `verify --local`
(repo-side surfaces only) on push/PR/daily. The two retired workflows moved to
`.github/workflows/_retired/`.

---

## OPEN HOLDS

1. **Concurrent in-flight changeset (NOT mine, left untouched):** the working
   tree carries an uncommitted "prompt rename" changeset from another process
   touching `registry/prompt_registry.yaml`, `registry/singularity_gate.py`,
   `specs/chatgpt_subset.py`, `server.py`, `docs/agents/AGENTS.md`, and
   `tests/*`. It is orthogonal to this closure; not reverted, not committed here.
   `verify` remains green because those files are outside the measured surfaces.
2. **Deployment attestation drift** (pre-existing): the live wheel is built from
   `edea664`; repo HEAD is `174c76c82` (1 commit ahead). The runtime schema edits
   (`public_registry.py` enum derivation, `risk_classifier` authority fixes)
   take effect **after redeploy**, not immediately. The live wire already matches
   canonical (STEP 3), so the closure holds at both HEAD and deployed.
3. **Duplicate protocol-version constants** (`tools.py` vs `public_surface.py`
   vs bridge files) remain — classified STALE, not yet collapsed (see NEXT ACTION).
4. **`tool_charter.py` mode prose** is hand-maintained enrichment keyed by the
   canonical mode names; a *new* mode still needs a prose entry (drift-guarded,
   not auto-generated). This is documentation, not the ABI.

---

## NEXT ACTION

1. **Redeploy** to `edea664`'s successor so the `public_registry` enum-derivation
   and `risk_classifier` authority fixes reach the live wire, then re-run
   `contract_closure.py verify` on the VPS (full, non-local) post-restart.
2. **Collapse the protocol-version duplicates** — make `tools.py` and the bridge
   files import `public_surface.MCP_SPEC_VERSION_*` instead of hardcoding.
3. **Retire stale prose/count strings** — `tools.py:23136` "19 tools",
   `generate_tool_manifest.py` version/count prose, `convergence_tracker.py`
   "8 tools" expected-strings (or bind them to `len(KERNEL_ABI_8)`).
4. Optionally archive `docs/canon/CANON_APEX_V2/**` (already marked SUPERSEDED).

---

## ZEN TEST

> *“How many independent places must a maintainer edit to add or retire one
> public mode?”*

**Answer: ONE.**

Add or retire a public mode by editing a single list:

```
arifosmcp/constitutional_map.py  →  CANONICAL_TOOLS["<tool>"]["modes"]
```

Every contract surface now derives from it or is drift-guarded:
runtime wire schema, `tools_sot.yaml`, LLM discovery, and authority coverage
all track that one list (the first three are generated; the fourth is verified
by `contract_closure.py verify`). The *implementation* of a mode's behavior
lives in its handler (a separate, expected concern — behavior cannot be retired
by deleting a name), and the charter's per-mode prose is enrichment, not the ABI.

The system is now easier to reason about, not merely larger: four hand-copied
mode arrays and two dead drift workflows collapsed onto one owner and one
instrument.

---

`DITEMPA BUKAN DIBERI` — measured, not asserted.
