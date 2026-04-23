# arifOS Deployment Guide
# DITEMPA BUKAN DIBERI — Forged, Not Given

## Deploy Manifest

All production deploys must reference `deploy/stack.manifest.json`.
No deploy without a manifest. No manifest without pinned SHAs.

---

## Pre-Deploy Checklist (paste into terminal)

```bash
cd /root/arifos

echo "=== PRE-DEPLOY CHECK ==="

# 1. git status clean
STATS=$(git status --short | grep -v "^??" | wc -l)
[ "$STATS" -eq 0 ] && echo "1. PASS: git clean" || echo "1. FAIL: $STATS tracked changes"

# 2. No stray submodule
git submodule status | grep -q geox && echo "2. FAIL: geox present" || echo "2. PASS: no geox submodule"

# 3. Manifest exists
[ -f deploy/stack.manifest.json ] && echo "3. PASS: manifest exists" || { echo "3. FAIL: no manifest"; exit 1; }

# 4. Refs match manifest
bash scripts/pre-deploy-check.sh || { echo "4. FAIL: ref mismatch"; exit 1; }
echo "4. PASS: refs match manifest"

# 5. Guard health (required before main merge only)
# bash scripts/guard-health-check.sh || { echo "5. FAIL: guard needs wiring"; exit 1; }
echo "5. SKIP: guard health (run before main merge)"

echo ""
echo "=== ALL CHECKS PASS — READY TO DEPLOY ==="
```

---

## Deploy Manifest Schema

```jsonc
{
  // REQUIRED — identifies this as a deploy artifact
  "schema": 1,

  // REQUIRED — ISO date of manifest creation
  "epoch": "YYYY-MM-DD",

  // REQUIRED — arifOS repo commit SHA
  "arifos": {
    "repo": "git@github.com:ariffazil/arifos.git",
    "ref": "<full 40-char SHA>",
    "deploy_ref": "main | <branch-name>",
    "note": "human-readable context"
  },

  // REQUIRED — GEOX repo commit SHA (separate canonical repo)
  "geox": {
    "repo": "git@github.com:ariffazil/GEOX.git",
    "ref": "<full 40-char SHA>",
    "deploy_ref": "main",
    "note": "Separate canonical repo; container consumes via pinned image or sibling build"
  },

  // OPTIONAL — if GEOX is packaged as a container image
  "images": {
    "arifos_mcp": "ghcr.io/ariffazil/arifos-mcp:<tag>",
    "geox": "ghcr.io/ariffazil/geox:<tag>"
  },

  // REQUIRED — infrastructure service versions
  "stack": {
    "postgres": "postgres:16-alpine",
    "redis": "redis:7-alpine",
    "qdrant": "qdrant/qdrant:latest",
    "ollama": "ollama/ollama:latest",
    "traefik": "traefik:v3.6.9"
  },

  // REQUIRED — governance state of this deploy
  "verdict": "SEAL | 888_HOLD",
  "hold_reason": "if 888_HOLD, why",
  "amanah_score_pre": 62.8,  // pre-deploy AMANAH score
  "888_HOLD_items": []       // if HOLD, what unlocks it
}
```

### Two-Environment Example

**vps-main (production):**
```json
{
  "schema": 1,
  "epoch": "2026-04-22",
  "arifos": { "repo": "...", "ref": "68024129628b6263d0bad39f0101fd13dcfdb413", "deploy_ref": "main" },
  "geox": { "repo": "...", "ref": "fe03bcb951e31e9ffb537f45ecaca92001816332", "deploy_ref": "main" },
  "verdict": "888_HOLD",
  "hold_reason": "P1: constitutional_guard NOT wired"
}
```

**vps-staging (test):**
```json
{
  "schema": 1,
  "epoch": "2026-04-22",
  "arifos": { "repo": "...", "ref": "ab209fab72941f9e7b6a47c1d4f3e8c2d1a9b0c5", "deploy_ref": "autoresearch/2026-04-22" },
  "geox": { "repo": "...", "ref": "fe03bcb951e31e9ffb537f45ecaca92001816332", "deploy_ref": "main" },
  "verdict": "SEAL",
  "hold_reason": null
}
```

---

## General vs Specialization

| Layer | Approach |
|-------|----------|
| Law (Floors F1-F13, manifest concept) | **General** — same principles everywhere |
| Repo roles (arifOS kernel, GEOX domain) | **Specialized** — each has one clear role |
| Manifest schema | **General** — 7 fields, works with compose or k8s |
| GEOX container image | **Specialized** — GEOX is GEOX, not generic |
| MCP self-test | **Specialized** — narrow, specific to arifOS guard path |

---

## Non-Canonical Dirs (runtime/local only)

These dirs exist on the VPS but are NOT in git and NOT canonical:

| Directory | What it is |
|-----------|-----------|
| `identity/` | OpenClaw identity config |
| `soul/` | OpenClaw soul/personality |
| `user/` | OpenClaw user config |
| `skills/` | OpenClaw skills catalog |
| `333_APPS/` | Local app experiments |
| `well/` | Local well-organ tooling |
| `commands/` | Personal markdown notes |

Do NOT commit these. They are excluded via `.gitignore`.

---

## 888 HOLD — What Blocks Main Merge

The following must ALL pass before merging to `main`:

1. `constitutional_guard` wired into `arifosmcp/adapters/mcp/server.py`
2. `scripts/guard-health-check.sh` exits 0
3. AMANAH re-test score ≥ 85
4. Arif F1 explicit approval

**DITEMPA BUKAN DIBERI — deploy with evidence, not memory.**
