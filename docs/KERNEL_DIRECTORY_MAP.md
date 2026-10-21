# KERNEL DIRECTORY MAP — read this before debugging or editing

Generated 2026-10-21 by FI-002 from live probes (git, grep, import graph,
`/health`). Every claim here carries its evidence method. If reality disagrees
with this file, **reality wins** — re-probe and fix this file.

Purpose: a future agent (human or machine) must be able to tell, in one read,
**where a thing lives, whether it is live, and whether it is safe to move.**

---

## 0. The five things that cause the most confusion

These are the actual navigation hazards in this repo. Everything else is noise
by comparison.

| Hazard | The confusion | The truth (probed) |
|---|---|---|
| `arifosmcp/schema/` **vs** `arifosmcp/schemas/` | Two dirs, nearly identical names | `schema/` = JSON-Schema files + `envelopes/` + `registry/`. `schemas/` = Python pydantic/dataclass models. **Different artifact kinds.** Neither is a copy of the other. |
| `arifosmcp/gate/` **vs** `arifosmcp/gates/` | Plural looks like the newer one | `gate/` = request-time gating (`mcp_gate_v0.py`, `forbidden_loader.py`). `gates/` = `independent_verify.py` (out-of-band verification). Different phase, not a rename pair. |
| root `contracts/` **vs** `arifosmcp/contracts/` | Root one looks authoritative | root `contracts/` = **external/interop** contracts (`.proto`, `EXTERNAL_WITNESS.md`, FALSIFICATION_PROTOCOL, incident reports). `arifosmcp/contracts/` = **internal kernel** models (`verdicts.py`, `identity.py`, `envelopes.py`). Known prior defect: `contracts/identity.py` ↔ `arifosmcp/contracts/identity.py` diverged once (mitigated 2026-09-30, consolidation still open). |
| `static/arifos/theory/000/` vs its old mirrors | Used to exist three times over | **Now single.** `static/arifos/docs/KERNEL/`, `static/arifos/kernel/`, `static/arifos/floors/` were byte-identical duplicates retired 2026-10-21 → `docs/_retired/2026-10-21-duplicate-canon/`. Only `theory/000/` is read by live code. |
| Root `server.py` vs `arifosmcp/server.py` vs `arifosmcp/runtime/server.py` | Three "server" files | `arifosmcp/runtime/server.py` = **the live one** (Docker CMD `uvicorn arifosmcp.runtime.server:app`). The other two are LEGACY / LEGACY_OR_ALT per `scripts/reachability_analysis.py`. |

---

## 1. The five top-level roots

| Root | What it is | Live? | Entry point |
|---|---|---|---|
| `arifosmcp/` | The kernel package. Everything that executes. | YES | `runtime/server.py`, `runtime/__main__.py` |
| `core/` | Constitutional core (floors, judge internals) | YES | imported by `arifosmcp` |
| `tests/` | Test suite. **Requires a live kernel on :8088** (`conftest.py` refuses without it, by design). | YES | `pytest tests/` |
| `scripts/` | Operator tooling. Invoked by Makefile / CI / cron / humans — **not imported**, so import-graph tools call these "dead" and they are NOT. | YES | `make <target>`, README, cron |
| `static/` | **Generated + published public artifacts.** Source of truth for `federation-manifest.json`. Not hand-edited. | YES | generators write here |

---

## 2. The critical warning about `scripts/`

`scripts/reachability_analysis.py` classifies unreferenced `scripts/*.py` as
`UNREACHABLE_DEAD_CANDIDATE`. **That classification is wrong for scripts.**

Probed 2026-10-21: 44 "unwired" scripts, every one had 3–13 references across
docs/Makefile/systemd/cron. Real wiring surfaces:

- `Makefile` → `audit_sot.py`, `canon_drift_check.py`, `federation_reality_probe.py`, `verify_live.py`, `verify_public.py`, `verify_vault_chain.py`
- `README.md` → `generate_current_state.py`, `sync_kernel_abi.py`, `update_readme_sot.py`, `verify_vault_chain.py`
- `RUNBOOK.md` → `federation_reality_probe.py`, `vault999_status.py`
- systemd → `arifos-drift-check.service`
- cron → `arifos-sovereignty-drill`, `sot-cron-vault-bridge`, `arifos-governed-obligations`

**Rule: never delete a `scripts/` file on the strength of an import graph.**
Check Makefile + CI + systemd + cron + docs first.

---

## 3. `arifosmcp/` internal map (only the parts that matter)

68 subdirectories, 2,688 files. This is the real size of the codebase and the
main reason agents get lost. Ranked by size:

| Subdir | Files | Role |
|---|---|---|
| `runtime/` | 956 | **The live kernel.** Server, routes, gates, governance runtime, workers. |
| `core/` | 201 | Kernel internals: kernel loop, jurisdiction, paradox, physics, protocols. |
| `schemas/` | 196 | Python models for every wire contract. |
| `tools/` | 169 | MCP tool implementations. |
| `resources/` | 107 | MCP resources (read surfaces). |
| `sessions/` | 82 | Persisted session material (incl. `hermes-briefings`). |
| `packages/` | 69 | Vendored/installable sub-packages. |
| `apps/` | 55 | Operator apps (`ops_dashboard`, `judge_console`, `metabolic_monitor`, `geox_app`). |
| `sites/` | 51 | Developer-site content. **Not** the same as root `static/`. |
| `kernel/` | 38 | Legacy-ish kernel helpers (`decision_torus`, `simulative_gate`, `tool_id_resolver`, `skill_graph`). Distinct from `runtime/kernel*`. |
| `abi/` | 29 | Cross-organ ABI + security gates (`amanah_gate`, `cross_organ_probe`). |
| `transport/` | 28 | Transport dialects (stdio / http / webmcp / a2a). |
| `constitution/` | 22 | Constitutional source text bindings. |
| `evals/` | 31 | Eval + conformance runners. Run manually / by CI, not imported. |

### Dynamic-import trap (this will bite you)

`arifosmcp/server.py` loads modules via **`__import__()` at runtime**, which a
static grep cannot see:

```python
# server.py ~3315
for mod in reality_modules:            # session_enforcer, envelope_validator,
    __import__(f"arifosmcp.runtime.{mod}")   # risk_ledger, incident_harness,
                                            # cooling_harness, rsi_patch_harness,
                                            # reality_bridge
__import__("arifosmcp.runtime.world_state")     # ~3342
__import__("arifosmcp.runtime.memory_quarantine")  # ~3556
```

`rsi_patch_harness.py`, `world_state.py` and `memory_quarantine.py` all look
unreferenced to a grep. **They are live.** A grep-based "dead code" sweep in
this repo produces false positives by construction.

---

## 4. What is NOT stale-and-dead

Probed 2026-10-21 across 2,606 tracked files untouched since 2026-07-21:

- **Zero Python files are truly unreferenced.** Every candidate had a live
  reference once dynamic imports, CI, Makefile, systemd, cron, and docs were
  accounted for.
- The population is dominated by things that are *supposed* to be frozen:
  sealed receipts, ADRs, archive trees, constitutional canon, and tests.

**Conclusion: age is not evidence of death in this repo.** Do not run an
age-based deletion sweep here. That was the finding of this audit.

---

## 5. Provenance / audit surfaces (do not reorganize casually)

| Path | Meaning |
|---|---|
| `docs/seals/`, `vault/scars/`, `docs/_retired/` | Immutable history. Move = rewrite of the record. |
| `docs/evidence/claims.yaml` | Machine-readable claim registry. The README gap table is generated from it. |
| `.well-known/current-state.json` | Generated truth block. Regenerate with `scripts/generate_current_state.py`, never hand-edit. |
| `GENESIS/` | Constitutional genesis. Source of the floor map. |
| `okf/` | Cross-organ doctrine namespace (ZEN, ATLAS333, paradox taxonomy). Referenced by `okf/ZEN.md` and the federation docs — low code-consumer count is expected, not a smell. |

---

## 6. Rule of thumb for the next agent

1. Probe before claiming. `git log -1 --format=%cs -- <file>`, then grep for
   consumers, then check `server.py` for `__import__` of it.
2. The live kernel reads `/opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp/`
   — **not** your working tree. A green import in `/root/arifOS` is NOT proof the
   deployed kernel is fine, and vice versa.
3. Self-measurement ≠ independent audit. `/health` reporting `degraded` is the
   kernel grading itself. Only `scripts/verify_vault_chain.py` and the
   independent-audit receipts are outside that circle.
4. When in doubt: `scripts/reachability_analysis.py` (then read its
   `limitations` field — it lists exactly what it cannot resolve).