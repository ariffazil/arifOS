# BRANCH PLAN — next-horizon/unified-federation-low-entropy
**Date:** 2026-07-28 | **Session:** SEAL-ff91ae20f90a4985
**Authority:** OBSERVE_ONLY | **Status:** Plan only (not executed)

---

## 1. Branch Identity

| Field | Value |
|---|---|
| **Branch name** | `next-horizon/unified-federation-low-entropy` |
| **Base** | `main` on all repos |
| **Goal** | Reduce code entropy while increasing agentic intelligence through better constraints, routing, evidence, and receipt flow |
| **Strategy** | Single coherent integration. Not "more code" — better organization. |
| **Tagging** | No tags needed. Branches are integration work-in-progress. |

---

## 2. Repos to Branch

| Repo | Branch Strategy | Notes |
|---|---|---|
| arifOS | Create. Kernel changes are P0+P1 only. | Drift already resolved in main. |
| A-FORGE | Create. Structural only (docs/gate table). | No code mutation. |
| AAA | Create. Structural only (doc align). | No code mutation. |
| arifFlow | Create. May mutate — receipt persistence. | Requires F13 SEAL. |
| GEOX | Create. Structural only. | No mutation. |
| WEALTH | Create. Structural only. | No mutation. |
| WELL | Create. Structural only. | No mutation. |
| Hermes | Create. Structural only. | Dirty files — need cleanup first. |
| arif-sites | Create. Structural only. | Dirty files — handle first. |

---

## 3. Branch Acceptance Criteria

### BC1 — Repo hygiene before branching
- [ ] arifOS: CLEAN ✅
- [ ] A-FORGE: CLEAN ✅
- [ ] AAA: CLEAN ✅
- [ ] GEOX: CLEAN ✅
- [ ] WEALTH: CLEAN ✅
- [ ] WELL: CLEAN ✅
- [ ] arifFlow: stub/commit dirty files (ARIFLOW_KERNEL_CANON.md, engine.ts changes, mcp/, tests/)
- [ ] Hermes: commit or stash 70 dirty files
- [ ] arif-sites: commit build artifacts, add gitignore

### BC2 — No unrelated formatting churn
- [ ] Only target files changed per P0-P6 scope
- [ ] No whitespace-only or import-reorder-only changes
- [ ] No linter auto-fix that touches non-target files

### BC3 — No mass deletion without F13
- [ ] Every deletion logged with reason
- [ ] `rm -rf` blocked by F13 gate
- [ ] Moved files generate git-visible renames (not delete+recreate)

### BC4 — Generated artifacts identified
- [ ] All `dist/`, `.venv/`, `__pycache__/`, `.next/`, `build/` dirs documented
- [ ] All `.git_commit`, `.update_check`, `.usage.json` files identified as generated
- [ ] Regeneration commands documented

### BC5 — Source-of-truth files named
- [ ] `/root/AGENTS.md` flagged as canonical pointer
- [ ] `/root/FEDERATION_CONTRACT.md` flagged as federation contract SOT
- [ ] `/root/arifOS/GENESIS/FLOOR_TABLE.json` flagged as floor definition SOT
- [ ] `/root/arifOS/arifosmcp/runtime/build.py` flagged as drift computation SOT
- [ ] `/opt/arifos/app/.git_commit` flagged as deployment stamp SOT

### BC6 — Federation contract unified
- [ ] Single `FEDERATION_CONTRACT.md` references all organs, ports, roles, authority
- [ ] No organ-specific AGENTS.md exceeds 10 lines (all point to canonical)
- [ ] All ports documented in one place

### BC7 — arifFlow receipt route proven
- [ ] Receipt flow: A-FORGE → arifFlow → persistence documented
- [ ] FQ measurement: verify/execute ratio computable
- [ ] Simulation-collapse threshold defined
- [ ] Restart-survival plan documented (current: in-memory only)

### BC8 — A-FORGE dry-run default preserved
- [ ] `mode=dry_run` is the default on arif_forge
- [ ] Explicit `ack_irreversible=true` required for mutation
- [ ] Code review confirms no silent default to execute

### BC9 — AAA cannot self-authorize
- [ ] No `arif_seal` call in AAA code
- [ ] No `arif_judge` call in AAA that passes its own verdict
- [ ] All AAA proposals must carry `requires_judge=true`

### BC10 — Kernel F13 remains final authority
- [ ] No override for `arif_judge` verdict output
- [ ] No silent fallback when F13 returning HOLD
- [ ] No HOTFIX bypass for floor evaluation

### BC11 — G-space/J-space category boundary preserved
- [ ] No theorem claims about J-space (research program only)
- [ ] No research-program ambiguity in G-space (formal math only)
- [ ] All APEX formulas are G-space (proven in axioms)
- [ ] All arif_think outputs tagged as OBS/DER/INT/SPEC

### BC12 — Gödel Lock / F7 / anti-overclaim path reconciled
- [ ] Ω₀ confidence band [0.03, 0.05] enforced in floor evaluator
- [ ] Self-certification attempts blocked at kernel level
- [ ] Absolute-certainty phrases (`always`, `never`, `certain`, `proven` without proof) trigger HOLD
- [ ] C_dark < 0.30 required for SEAL (F9)

### BC13 — Health endpoints report consistently
- [ ] All organs report `source_commit`, `built_commit`, `deployed_commit`
- [ ] Kernel drift invariant applies to all, not just arifOS
- [ ] Health status reflects truth, not wish

### BC14 — Tests pass before merge
- [ ] arifOS: `pytest -m "not e3e and not slow"` passing
- [ ] A-FORGE: `make test` passing
- [ ] AAA: `npm test` passing
- [ ] arifFlow: `cargo test` passing
- [ ] GEOX: `pytest tests/ -q --tb=short` passing
- [ ] WEALTH: `pytest tests/ -q --tb=short` passing
- [ ] WELL: `pytest tests/ -q --tb=short` passing

### BC15 — Rollback plan exists
- [ ] `git revert` sequence documented for each patch set
- [ ] Service restart order documented
- [ ] Recovery point: main branch before merge
- [ ] No irreversible data changes without SEAL

---

## 4. Staging Order

```
Pre-stage: Clean dirty repos (arifFlow, Hermes, arif-sites)
Stage 1:   Branch creation (all 9 repos)
Stage 2:   P0 — Authority and drift (identity + remaining metadata sync)
Stage 3:   P1 — Canonical contracts (AGENTS.md, FEDERATION.md, F7 fix)
Stage 4:   P2 — Gödel Lock / F7 bridge (Ω₀ enforcement, overclaim blockers)
Stage 5:   P3 — arifFlow metabolism (receipt persistence, FQ telemetry)
Stage 6:   P4 — A-FORGE execution governance (dry-run docs, gate docs)
Stage 7:   P5 — AAA coordination hygiene (no-self-seal enforcement)
Stage 8:   P6 — Integration tests (federation e2e, receipt e2e, rollback e2e)
Post:      Local test pass → report → F13 SEAL for push
```

---

## 5. Push & Merge Policy

| Action | Condition |
|---|---|
| Push branch to origin | Requires F13 SEAL |
| Open PR | Requires F13 SEAL |
| Merge to main | Requires: all BC1-BC15 green + explicit F13 SEAL |
| Delete branch after merge | Automatic — `git branch -d` after merge |

---

*Plan only. No mutation. All actions require F13 SEAL before execution.*
