# Workflow Consolidation — 2026-04-25

## What was done

**35 workflows → 6 active + 5 originals kept + 28 archived**

The old setup was a bill explosion: 35 workflow files, many overlapping, many failing, several running on schedules (hourly Gemini triage = $$$, multiple daily CI runs, etc.)

---

## New Active (6 + 5 originals = 11 total)

| # | File | Purpose | Trigger |
|---|------|---------|---------|
| 01 | `01-unified-ci.yml` | **Main CI** — fast-signal, constitutional chain, shim verification, F9 scan, 888_JUDGE PR gate, MCP conformance, test suite, secrets gate, daily health | push/PR + daily |
| 02 | `02-aaa-seal.yml` | AAA folder integrity | push(AAA) + daily |
| 03 | `03-secrets-gate.yml` | **F11 Gate** — gitleaks + custom pattern guard (HF, Telegram, AWS, GitHub tokens) | push/PR |
| 04 | `04-uptime-monitor.yml` | Live endpoint health (mcp, arifosmcp, geox) — reduced from hourly to 6-hourly | 6-hourly |
| 05 | `05-law-sync.yml` | Sync 000_INIT.md / CLAUDE.md to constitutional gist | push(000*) |
| 06 | `06-mcp-conformance.yml` | MCP transport + registry compliance | push(transport) + PR + manual |

**Originals still active (comparison baselines):**
- `ci.yml` — fast F2 truth gate, push/PR to main+aaa
- `ci-unified.yml` — 54-step comprehensive CI (TO REVIEW: may overlap 01-unified-ci)
- `live_tests.yml` — constitutional floor tests (TO REVIEW: may overlap 01-unified-ci)
- `aaa-seal-check.yml` — daily AAA check (duplicated by 02-aaa-seal.yml)
- `secrets-scan.yml` — duplicated by 03-secrets-gate.yml
- `uptime-monitor.yml` — duplicated by 04-uptime-monitor.yml
- `888-judge.yml` — separate PR review gate (keep)

---

## Archived (28 workflows — can be restored from `.github/workflows.archive/`)

### 💸 Costly / all-failed (bill consumers):
- `gemini-dispatch.yml` → hourly scheduled triage, 16 runs, all failed on collection errors
- `gemini-invoke.yml` → Google Gemini CLI, consumed bill
- `gemini-review.yml` → same
- `gemini-triage.yml` → same
- `gemini-scheduled-triage.yml` → hourly cron = highest cost workflow
- `deploy-automated.yml` → 29 steps, 3 failures, no success
- `deploy-vps.yml` → 16 steps, failed
- `deploy-cloudflare.yml` → failed
- `deploy-console.yml` → never succeeded
- `deploy-hub.yml` → never succeeded
- `deploy-sites.yml` → never succeeded
- `dual-deploy.yml` → failed
- `dual-deploy-fixed.yml` → waiting (never ran)
- `forge2-ci-cd.yml` → failed
- `release.yml` → 3 failures
- `docker-publish.yml` → 1 success only

### ❌ Broken / pre-existing failures:
- `arifos-skill-tests.yml` → references legacy `core.execution_validator` that doesn't exist
- `constitutional_alignment.yaml` → failed, broken
- `constitutional-eval.yml` → schedule only, failed
- `deployment-gates.yml` → failed

### 📦 Publishing (no recent activity):
- `npm-publish.yml`, `npm-publish-tag.yml`, `publish-mcp-registry.yml`, `publish.yml`, `push-to-huggingface.yml` → all dormant

### 🔀 Duplicates (keeping one):
- `law-sync.yml` → merged into 05
- `mcp-conformance.yml` → merged into 06

---

## What's still consuming bill (after this cleanup)

| Workflow | Trigger | Cost |
|----------|---------|------|
| `01-unified-ci.yml` | push + PR + daily | Medium (optimized) |
| `ci-unified.yml` | push + PR + daily | **High (54 steps) — compare with 01** |
| `live_tests.yml` | push + daily | Medium — compare with 01 |
| `ci.yml` | push/PR | Low (fast) |
| `888-judge.yml` | PR | Low |
| `02-aaa-seal.yml` | push(AAA) + daily | Low |
| `03-secrets-gate.yml` | push/PR | Low |
| `04-uptime-monitor.yml` | 6-hourly | **Low (reduced from hourly)** |
| `05-law-sync.yml` | push | Low |
| `06-mcp-conformance.yml` | push + PR + manual | Medium |

---

## Decision Arif needs to make

**After comparing, delete the duplicates:**
- `ci-unified.yml` vs `01-unified-ci.yml` → keep the better one
- `live_tests.yml` vs `01-unified-ci.yml` → merge or delete
- `secrets-scan.yml` vs `03-secrets-gate.yml` → delete old
- `aaa-seal-check.yml` vs `02-aaa-seal.yml` → delete old
- `uptime-monitor.yml` vs `04-uptime-monitor.yml` → delete old

**After verification, archive the originals:**
- `ci.yml` (fast gate) — safe to keep as backup
- `888-judge.yml` — separate concern, keep

---

## Restore an archived workflow

```bash
# Example: restore gemini-scheduled-triage
cp .github/workflows.archive/gemini-scheduled-triage.yml .github/workflows/
git add .github/workflows/gemini-scheduled-triage.yml
git commit -m "restore: gemini-scheduled-triage"
```

---

## Rollback entire workflow consolidation

```bash
git revert HEAD  # undo the commit
# Or cherry-pick from archive
cp .github/workflows.archive/* .github/workflows/
```

---

**DITEMPA BUKAN DIBERI 🧠✨🌏**