# RECEIPT — kernel entropy audit (stale-file sweep)

Date: 2026-10-21 · Actor: claude-code-kvm8 (FI-002) · Lane: B (receipt, NOT a SEAL)
Scope: `/root/arifOS` tracked files, cutoff = untouched since 2026-07-21 (>3 months)

## Method (OBS, reproducible)
1. `git -c core.quotepath=false log --name-only` → last-touched map (14,048 paths)
2. join against `git ls-files` → 4,104 / 4,107 mapped
3. consumer check per candidate: Python import, `__import__()` in server.py,
   Makefile, `.github/workflows/`, systemd units, `/etc/cron.d/`, crontab,
   README/RUNBOOK/AGENTS docs

## Population
| Bucket | Count |
|---|---|
| Stale tracked files (excl. `00_legacy_materials/`, `_retired/`) | 2,606 |
| — Python | 1,382 |
| — Markdown | 737 |
| — JSON / YAML / other | 487 |
| Largest areas | `arifosmcp` 1,129 · `tests` 398 · `docs` 310 · `static` 190 · `core` 136 |

## FINDING 1 — Zero stale Python files are dead (the headline)
Every stale-Python candidate resolved to a live consumer once dynamic imports
and non-import wiring were accounted for. **Age is not evidence of death here.**

Two concrete false positives that a naive sweep would have broken:
- `arifosmcp/runtime/world_state.py` — `__import__()` at `server.py:3342`
- `arifosmcp/runtime/memory_quarantine.py` — `__import__()` at `server.py:3556`
- `arifosmcp/runtime/rsi_patch_harness.py` — `__import__()` in the
  `reality_modules` loop at `server.py:3315`

### The 44-script trap (documented, not deleted)
`scripts/reachability_analysis.py` flagged 44 `scripts/*.py` as
`UNREACHABLE_DEAD_CANDIDATE`. All 44 have 3–13 references each across
Makefile / README / RUNBOOK / systemd / cron. Its own `limitations` field
admits it does not resolve "string-based module path selection". **Scripts are
invoked, not imported.** No script was deleted.

## FINDING 2 — Real defect: phantom console_script `aclip-cai` (P1)
`pyproject.toml:282` declares `aclip-cai = "arifosmcp.intelligence.cli:main"`.
`arifosmcp/intelligence/cli.py` **does not exist and never has** (absent from
git history, not deleted from it). The script is installed at
`/usr/local/bin/aclip-cai` and raises `ModuleNotFoundError` on execution.
`scripts/reachability_analysis.py` nevertheless classifies it as a live
`CLI_ADAPTER / PRODUCTION_ROOT`, which propagated the phantom into the audit.
→ Full receipt: `docs/conformance/RECEIPT_ACLIP_CAI_PHANTOM_ENTRYPOINT_2026-10-21.md`

## FINDING 3 — Entropy removed: 3-way duplicated canon (DONE)
`static/arifos/` held byte-identical copies of constitutional canon in
`docs/KERNEL/`, `kernel/`, and `floors/`, duplicating the canonical
`theory/000/`. 64 files / 720 KB.

Zero code, CI, script, or HTML consumers — the only repo references were inside
`.ua/intermediate/batches.json` (a tool cache). Live reader is
`arifosmcp/runtime/organ_attestation.py:139-144`, which loads
`static/arifos/theory/000/000_CONSTITUTION.md`.

Moved (F1 `git mv`, zero deletions) → `docs/_retired/2026-10-21-duplicate-canon/`
with a README stating the canonical path and forbidding resurrection.

Why it mattered: three copies of canon = three edit sites, none of which fail
loudly on divergence. That is a silent-drift trap for the next agent.

## FINDING 4 — 19 git worktrees (~1.5 GB) — NOT TOUCHED, F13 required
Registered worktrees outside the main tree. Branch distance from `main`:

| Worktree | ahead | dirty | Note |
|---|---|---|---|
| `arifOS-wt-record-append` | **3** | 5 | unmerged work |
| `arifOS-wt-mcp-hardening` | 1 | 5 | unmerged work |
| `arifOS-wt-lock`, `arifOS-wt-pr904`, `.qwen/…`, `worktrees/arifos-audit` | 1 | 0 | unmerged |
| `arifOS-wt-phoenix`, `arifOS-wt-qrl-incr1`, `forge_work/sa-fix` | 0 | 0 | safe to drop |
| several `/tmp/…` detached | — | 0–5 | baseline snapshots |

Only 3 worktrees are provably safe (0 ahead, 0 dirty). The rest hold
**unmerged commits or uncommitted work** — deleting them destroys work and is
F13-class, not agent-class. Disk is at 82% (72 G free), so there is no
operational pressure justifying the risk.

## FINDING 5 — Navigation hazards documented
`schema/` vs `schemas/`, `gate/` vs `gates/`, root `contracts/` vs
`arifosmcp/contracts/`, and three different `server.py` files. All are
near-name collisions, not duplicates — resolved in
`docs/KERNEL_DIRECTORY_MAP.md` rather than moved, because merging them would
be an architectural change.

## Verification after mutation
- `arifosmcp.runtime.organ_attestation`, `arifosmcp.runtime.world_state`,
  `arifosmcp.runtime.memory_quarantine` all import cleanly.
- `/health` → `status: degraded`, `drift: false`, `source=built=deployed=9f3716a`,
  canon integrity `ok`. Unchanged from pre-mutation state.
- `git status` → 64 `R` (renames), **0 `D` (deletions)**.

Note: the live kernel imports from `/opt/arifos/current/venv/.../site-packages`,
not this working tree, so the move cannot affect the running service.

## OPEN for F13
1. `aclip-cai` phantom entrypoint — remove the declaration or restore the module.
2. Worktree reclamation — 16 of 19 hold unmerged work; needs an owner decision
   per branch (merge / archive / drop).
3. `contracts/identity.py` ↔ `arifosmcp/contracts/identity.py` consolidation
   (pre-existing, still open per README gap table).
