# WORKFLOW_ELEVATED_APPROVAL.md

**Purpose:** Document elevated state approval and advanced OpenClaw power tips
**Status:** APPROVED by 888 Judge (Arif) — 2026-02-11
**Ω₀:** 0.04

---

## Elevated State Approval

**APPROVED BY:** Muhammad Arif bin Fazil (888 Judge)
**DATE:** 2026-02-11
**AUTHORITY:** Constitutional sovereign under arifOS F11

### Approved Configuration

```json
{
  "tools": {
    "elevated": {
      "enabled": true,
      "allowFrom": {
        "telegram": ["267378578"],
        "webchat": ["267378578"]
      }
    },
    "exec": {
      "security": "full",
      "safeBins": ["apt", "npm", "pip", "docker", "git", "curl", "wget", "gh", ...]
    }
  },
  "agents": {
    "defaults": {
      "elevatedDefault": "ask"
    }
  }
}
```

### What This Means

✅ **ENABLED:** Elevated tool execution
✅ **SECURITY:** Full shell execution capabilities
✅ **SAFE BINS:** 70+ approved binaries
⚠️ **MODE:** `ask` — human approval required for high-risk actions
✅ **WHITELIST:** Only Telegram ID 267378578 authorized

### Constitutional Safeguards

Even with elevated approval, **F1 Amanah** applies:
- Reversible actions preferred
- Destructive operations (`rm`, `drop`, `chmod`) require explicit confirmation
- All elevated actions logged to VAULT999

---

## Advanced Power Tips (from CloudVyn)

### 1. Environment Variables

**Use `${ENV_VAR}` in workflows for secrets:**

```yaml
# workflow.yml
steps:
  - name: Fetch API data
    run: curl -H "Authorization: Bearer ${API_KEY}" https://api.example.com/data
```

**Secure storage:**
- API keys in `/root/.env.openclaw`
- Never commit secrets to git
- Use `env` skill to load variables

### 2. Workflow Chaining

**Pipe output between workflows:**

```bash
# Fetch data → Process → Analyze
openclaw run fetch-data.yml | openclaw run process-data.yml | openclaw run analyze.yml
```

**Use cases:**
- Data pipelines
- Multi-stage processing
- ETL workflows

### 3. Headless Mode (Development)

**Visual browser debugging:**

```bash
# Watch browser actions during development
openclaw run browser-task.yml --headless=false

# Production (default)
openclaw run browser-task.yml --headless=true
```

---

## Usage Examples

### Secure API Call with Env Vars

```bash
# Set secret
export GITHUB_TOKEN="ghp_xxx"

# Use in workflow
openclaw run github-sync.yml
```

### Chained Workflow

```bash
# Morning briefing pipeline
openclaw run fetch-calendar.yml | \
  openclaw run fetch-emails.yml | \
  openclaw run generate-briefing.yml
```

### Browser Automation (Debug Mode)

```bash
# Watch the bot work
openclaw run scrape-pricing.yml --headless=false
```

---

## Governance Notes

- **F1 Amanah:** All elevated actions reversible where possible
- **F2 Truth:** Document all workflow dependencies
- **F7 Humility:** Mark experimental workflows with Ω₀ > 0.05
- **F9 Anti-Hantu:** No "magic" — all tips documented and auditable

---

**APPROVED BY 888 JUDGE** ✅
*Elevated state active under constitutional constraints.*

---

*Last Updated: 2026-02-11 | Ω₀ = 0.04*
