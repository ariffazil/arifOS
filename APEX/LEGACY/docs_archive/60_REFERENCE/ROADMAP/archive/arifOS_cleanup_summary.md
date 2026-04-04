
# ARIFOS REPOSITORY CLEANUP - QUICK REFERENCE

## FILE CATEGORIES SUMMARY

| Category | Count | Action |
|----------|-------|--------|
| **DELETE** | 7 files + 10 dirs | Remove immediately |
| **ARCHIVE** | 15+ dirs | Move to archive/ |
| **HARDEN** | 20+ files | Consolidate/Merge |
| **GITIGNORE** | 5+ patterns | Add to .gitignore |
| **SHAMEFUL** | 1 dir | Move to separate repo |

---

## DELETE LIST (Immediate)

### Root Files
```
tmp_check.py
tmp_migrate.py
tmp_view.py
sitecustomize.py
nixpkgs.nix
runtime.txt
PR_SUMMARY_VAULT999_DOCTRINE.md
```

### Archive Directories
```
archive/2025_cleanup/
archive/2026-01-26-cleanup/
archive/2026-02-02-cleanup/
archive/README/
archive/VAULT999_housekeeping_2026_01_26/
archive/analysis/
archive/antigravity_v47/
archive/apex_theory_sources_v35/
archive/archive_local_v49/
archive/arifos_clip_20251214/
archive/arifos_legacy_20260129/
archive/constitutional-alignment-artifacts/
archive/deploy/
archive/entropy_analysis/
```

---

## ARCHIVE LIST (Move to archive/)

```
docs/archive/todelete/
docs/archives/v49/
ROADMAP/kimi_ai_deep_research_2026-01-12.md
ROADMAP/legacy_future_path.md
ROADMAP/legacy_roadmap_v50.md
```

---

## HARDEN LIST (Consolidate)

### Merge into docs/
```
000_THEORY/ → docs/10_THEORY/
SEAL999/ → docs/50_IMPLEMENTATION/
VAULT999/ → docs/50_IMPLEMENTATION/
spec/ → docs/60_REFERENCE/
ROADMAP/ → docs/40_ROADMAP/ (selectively)
```

### Merge agent configs
```
.agent/
.antigravity/
.claude/
.codex/
.cursor/
.gemini-clipboard/
.kimi/
.openmcp/
.serena/
→ agents/ (consolidated)
```

### Move to deployments/
```
Dockerfile
docker-compose.yml
Caddyfile
railway.json
railway.toml
railway_env_corrected.txt
```

### Move to examples/
```
demo_refusal_system.py
```

---

## SHAMEFUL (Move Out)

```
career-timeline/ → ariffazil/portfolio repo
```

---

## GITIGNORE ADDITIONS

```gitignore
# Temporary files
tmp_*.py
*_tmp.py
sitecustomize.py

# Environment patterns
.env.local
.env.*.local
railway_env_*.txt

# IDE
.idea/
.vscode/personal*

# OS
.DS_Store
Thumbs.db
```

---

## ESTIMATED IMPACT

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Root directories | 25+ | 10 | 60% |
| Root files | 40+ | 15 | 62% |
| Total entropy | HIGH | LOW | ~70% |
| Clone time | Slow | Fast | ~50% |
| Navigation | Confusing | Clear | Priceless |

---

## ONE-LINER CLEANUP COMMANDS

```bash
# Phase 1: Delete temp files
git rm tmp_*.py sitecustomize.py nixpkgs.nix runtime.txt

# Phase 2: Delete redundant archive dirs
git rm -r archive/2025_cleanup archive/2026-*-cleanup archive/README

# Phase 3: Move career content (create new repo first)
git rm -r career-timeline/

# Phase 4: Update .gitignore
echo "tmp_*.py\nsitecustomize.py\n.DS_Store" >> .gitignore
```

---

*Generated: 2026-02-02*
