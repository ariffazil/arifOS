## Skill Result: repo-hygiene-audit

**Repo:** `/root/arifOS` (`ariffazil/arifos`)  
**Role:** `kernel` (constitutional kernel / federation governor)  
**Depth:** standard (3 levels)  
**Audited:** 2026-07-01  

---

### Summary

`arifOS` is the constitutional kernel of the federation, but its own working tree is carrying significant structural debt. The canonical `arifos/` package and `core/` kernel coexist with the legacy `arifosmcp/` monolith, which still contains duplicate constitutional files (`floors.py`, AGENTS guidance, CONSTITUTION stubs). On-disk runtime debris is large: `node_modules/` (335 MB), `.venv/` (5.8 GB), `.opencode/node_modules/` (58 MB), plus IDE/test caches. Several tracked files (wheels, `uv.lock`, archived docs, VAULT999 runtime dumps) inflate the repository without adding source value. The README still points agents to `python -m arifosmcp.runtime.server`, which appears stale given the newer `arifos` package. No cross-repo constitutional leaks were found, but internal authority duplication and stale references are material.

---

### Authority Boundary

- [ ] No constitutional leaks — **NO, internal duplication found**
- Leaks / duplicates:
  - `arifos/floors.py` (canonical) coexists with `arifosmcp/runtime/floors.py`, `arifosmcp/schemas/floors.py`, `arifosmcp/core/floors.py` — multiple floor definitions in one repo.
  - `docs/CONSTITUTION.md` and `docs/00_META/CONSTITUTION.md` are stubs (98 bytes each) duplicating constitutional surface.
  - `docs/agents/AGENTS.md`, `docs/AGENTS.md`, and `arifosmcp/AGENTS.md` duplicate / fragment agent authority guidance alongside root `AGENTS.md`.
  - `docs/archive/pre-genesis-2026-06-06/REPO_ROUTING_CONSTITUTION.md` is an archived copy of a routing-constitution file; preserved but stale.
  - `.gitmodules` exists as an empty, untracked file — no active submodules, but submodule machinery left behind.

> No files from this list were found **outside** `arifOS`, so these are internal authority conflicts, not cross-repo leaks.

---

### Runtime Debris

- [ ] No debris — **NO**
- Debris found (on disk, mostly ignored but present):
  - `node_modules/` — 335 MB (root-level Docusaurus/npm workspace artifacts)
  - `.venv/` — 5.8 GB (Python virtual environment)
  - `.opencode/node_modules/` — 58 MB
  - `.pytest_cache/`, `.ruff_cache/`, `.serena/` — IDE / test caches
  - `GENESIS/PH-KOSMO-2026-06-12/receipts.jsonl`, `VAULT999/*.jsonl`, `VAULT999/state.json`, `VAULT999/*.db` — runtime ledger / session outputs
  - `arifosmcp/ARIFOS_MCP_AGENT_SEED.json`, `arifosmcp/ARIFOS_MCP_FINAL_SEAL.md` — runtime seed artifacts
  - `arifosmcp/dist/`, `arifosmcp/data/memory/`, `arifosmcp/sessions/` — build/runtime outputs
- Tracked debris (committed, cannot be cleaned without git rm):
  - `dist/arifos-*.whl` and `dist/arifos-*.tar.gz` — 4 MB+ of build artifacts
  - `uv.lock` — 1.1 MB lockfile
  - `archive/` — 668 KB of legacy migration windows, stale docs, and old manifests
  - `VAULT999/ARIFOS_AGENTIC_KERNEL_DOCTRINE_2026-06-03.md`, `VAULT999/SEALED_EVENTS.jsonl` — runtime ledger files tracked in git
  - `static/arifos/APEX FORGE.png` — 1.2 MB binary image

---

### Structural Issues

- [ ] Structure matches canonical role — **NO**
- Issues:
  - Multiple overlapping package roots: `arifos/`, `arifOS/`, `arifosmcp/`, `arifosmcp/arifos/`, `core/`, `aforge-python-migration/`. The repo appears to be mid-migration with the old monolith (`arifosmcp`) and new canonical package (`arifos`) both active.
  - `arifosmcp/` contains its own `AGENTS.md`, `README.md`, `VAULT999/`, `CONSTITUTIONAL_EXTENSION*.py`, `floors.py`, and runtime server — effectively a second kernel surface inside the kernel repo.
  - `core/` holds the canonical `judgment.py` and `vault999/`, but `arifos/floors.py` is in a different subtree from `core/judgment.py`, splitting constitutional kernel code.
  - `arifOS/` (uppercase) directory exists alongside lowercase `arifos/` — casing collision risk on case-insensitive filesystems.
  - `tests/` contains `archive/` and `golden/` subdirs inside the test tree.
  - `commands/scripts_archive/` and `commands/scripts_deploy/` split operational scripts without clear ownership.

---

### Broken References

- [ ] No broken refs — **NO, stale references found**
- Stale / suspect refs:
  - `README.md` line 79: `python -m arifosmcp.runtime.server` — likely stale; canonical server may now live under `arifos` package.
  - `scripts/apex_pulse.py`, `daemon/apexd_observability.py`, `arifos/decision.py`, `arifos/risk.py` still reference `APEX`, which AGENTS.md lists as **decommissioned** (deliberation moved to AAA `a2a-server/deliberation.ts`).
  - `arifosmcp/` is still imported by 749 `.py` files, even though `arifos/` is the canonical package declared in `pyproject.toml`.
  - Empty `.gitmodules` file suggests dead submodule configuration.

---

### Skill Registry

- [ ] Registry consistent — **N/A for kernel role**
- `arifOS` is a `kernel` repo, so it is not expected to maintain the AAA/A-FORGE skill registry (`registries/skills.yaml`). However, it does contain two skill-like directories:
  - `core/skills/` — 7 Python modules + 4 specs (autonomy, scenario policy, threat score)
  - `./skills/` — empty top-level directory
- No `registries/skills.yaml` found; no orphan-skill registry check applicable.

---

### Recommendations

1. **Consolidate or retire `arifosmcp/`** — `arifosmcp/` duplicates constitutional files and runtime surface. Either complete the migration into `arifos/` + `core/` or clearly mark `arifosmcp/` as a quarantine archive. — **HIGH** — Owner: A-FORGE / Arif
2. **Remove runtime debris from disk** — `node_modules/`, `.venv/`, `.opencode/node_modules/`, `.pytest_cache/`, `.ruff_cache/`, `.serena/` are ignored and should not persist in the working copy. Add a cleanup step to the runbook. — **MEDIUM** — Owner: Ops
3. **Stop tracking build artifacts and ledger dumps** — `git rm --cached dist/*`, `uv.lock` (if regenerated in CI), `VAULT999/SEALED_EVENTS.jsonl`, and `archive/` contents. Move VAULT999 runtime data to a dedicated runtime volume, not git. — **HIGH** — Owner: A-FORGE
4. **Deduplicate authority files** — Remove stub `docs/CONSTITUTION.md`, `docs/00_META/CONSTITUTION.md`, and merge `arifosmcp/AGENTS.md` into root `AGENTS.md` or delete if superseded. Keep one `floors.py` (canonical in `arifos/`). — **HIGH** — Owner: AAA / Arif
5. **Fix stale README / APEX references** — Update README server command to the current canonical module; audit APEX references and remove or redirect to AAA `a2a-server/deliberation.ts`. — **MEDIUM** — Owner: A-FORGE
6. **Remove empty `.gitmodules`** — Delete the 0-byte untracked `.gitmodules` file. — **LOW** — Owner: A-FORGE
7. **Clarify package migration status in `AGENTS.md`** — Document which package roots are canonical (`arifos/`, `core/`) and which are legacy (`arifosmcp/`, `aforge-python-migration/`). — **MEDIUM** — Owner: AAA

---

### Escalations

- **Constitutional duplication inside arifOS** — Not a cross-repo leak, but the multiple `floors.py` / `CONSTITUTION.md` stubs create internal authority ambiguity. Recommend Arif ratify which files are canonical before any cleanup that touches them.
- **VAULT999 tracked files** — `VAULT999/SEALED_EVENTS.jsonl` is an immutable ledger; moving it out of git requires care. Escalate to Arif if the plan is to relocate rather than keep in-repo.
- **Large `.venv/` (5.8 GB)** — Safe to delete locally, but confirm no active service is using it before removal.

---

*Audit produced by `repo-hygiene-audit` skill v1.0.0 — no files modified.*
