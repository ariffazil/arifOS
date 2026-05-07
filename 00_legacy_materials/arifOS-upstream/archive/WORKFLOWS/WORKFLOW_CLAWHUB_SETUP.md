# WORKFLOW_CLAWHUB_SETUP.md

**Purpose:** Guide for setting up ClawHub CLI and browsing skills
**Status:** ACTIVE (2026-02-11)
**Ω₀:** 0.04

---

## Summary

✅ **Task 3: Browse Skills** — COMPLETED
✅ **Task 4: Setup CLI** — PARTIAL (CLI installed, auth pending)

---

## ClawHub CLI Status

**Installation:** ✅ Installed via npx
**Version:** v0.6.0
**Usage:** `npx clawhub [command]`

---

## Skills Discovered (Browse Results)

### Latest Skills (20 shown)
| Skill | Version | Description |
|-------|---------|-------------|
| openclaw-airesearchos | v1.0.2 | Deep research powered by AIresearchOS |
| context-compactor | v0.3.0 | Token-based context compaction for local models |
| variflight | v1.0.1 | Query flight info, train tickets, travel |
| slk | v1.0.0 | Slack messages and channels management |
| claude-code | v1.0.0 | Claude Code integration for OpenClaw |
| frontend-dev | v0.1.0 | Next.js projects with Tailwind CSS |
| workspace-cleaner | v1.0.0 | Automated workspace cleanup |
| web-clipper | v1.0.0 | Web content clipping |
| tiktok-poster | v1.0.0 | TikTok automation via browser |

### Research Skills (Top 5)
1. **deepresearchwork** v1.0.0 — Deep Research Work
2. **parallel-ai-research** v1.0.0 — Parallel research
3. **research-engine** v1.0.0 — Research engine
4. **academic-deep-research** v1.0.0 — Academic research
5. **research-tracker** v0.1.0 — Research tracking

### GitHub Skills (Top 5)
1. **gh** v0.1.0 — GitHub CLI integration
2. **github-pro** v1.0.0 — Advanced GitHub operations
3. **gitclassic** v1.0.0 — Classic git workflows
4. **github** v1.0.0 — GitHub integration
5. **pr-reviewer** v1.0.0 — PR review automation

---

## GitHub Authentication Setup (Task 4)

### Option A: Browser Login (Interactive)

```bash
# This will open a browser for GitHub OAuth
npx clawhub login
```

**Note:** Requires browser access. Use Option B for headless environments.

### Option B: Token-Based Login (Headless)

**Step 1:** Get token from ClawHub website
1. Visit: https://clawhub.ai
2. Click "Login with GitHub"
3. Authorize access
4. Go to Settings → API Tokens
5. Generate new token

**Step 2:** Login with token

```bash
npx clawhub login --token YOUR_TOKEN --no-browser
```

**Step 3:** Verify

```bash
npx clawhub whoami
```

---

## Useful ClawHub Commands

```bash
# Browse latest skills
npx clawhub explore --limit 20

# Search skills
npx clawhub search <query>

# Inspect skill details
npx clawhub inspect <skill-name>

# Install a skill
npx clawhub install <skill-name>

# List installed skills
npx clawhub list

# Update skills
npx clawhub update

# Sync local skills to registry
npx clawhub sync
```

---

## Recommended Skills for Your Stack

Based on your arifOS/OpenClaw setup:

1. **claude-code** — Claude Code integration (already inspected)
2. **github-pro** — Enhanced GitHub operations
3. **deepresearchwork** — For research workflows
4. **workspace-cleaner** — Automated maintenance
5. **context-compactor** — Optimize token usage

---

## Next Steps

1. **Complete GitHub auth** using Option A or B above
2. **Install useful skills:** `npx clawhub install claude-code`
3. **Publish your workflows** as skills to ClawHub
4. **Publish SOUL.md** to onlycrabs.ai

---

*Last Updated: 2026-02-11 | Ω₀ = 0.04*
