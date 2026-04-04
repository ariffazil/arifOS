# arifOS MCP Naming Guide
## For Non-Coders

---

### THE SIMPLE RULE

**Use `arifos_aaa_mcp`**  
**Ignore `aaa_mcp`**

That is it. That is the whole guide.

---

### WHY ARE THERE TWO NAMES?

Think of it like a restaurant:

```
FRONT OF HOUSE (Customers see)
  arifos_aaa_mcp
  - Waiters, menu, dining room
  - This is what you interact with
        |
        v
BACK OF HOUSE (Kitchen)
  aaa_mcp
  - Chefs, ovens, recipes  
  - Works behind the scenes
```

---

### WHEN TO USE WHICH

| If you want to... | Use this | Example |
|-------------------|----------|---------|
| Start the server | arifos_aaa_mcp | python -m arifos_aaa_mcp http |
| Connect from GitHub | arifos_aaa_mcp | Already configured |
| Check health | arifos_aaa_mcp | curl localhost:8080/health |
| Fix something inside | aaa_mcp | Only if AGI tells you to |

---

### DOCKER COMPOSE CHEAT SHEET

Your server runs this command:
```yaml
# In docker-compose.arifos.yml
CMD: ["python", "-m", "arifos_aaa_mcp", "http"]
          ↑
          USE THIS ONE
```

---

### COMMON CONFUSION

WRONG:
```
python -m aaa_mcp        ← Old way, do not use
```

RIGHT:
```
python -m arifos_aaa_mcp ← New way, use this
```

---

### FILE LOCATIONS

| Path | Purpose |
|------|---------|
| /srv/arifOS/arifos_aaa_mcp/ | **Public API** ← You care about this |
| /srv/arifOS/aaa_mcp/ | **Internal code** ← Ignore this |

---

### WHAT IF I SEE BOTH?

**Example:** You see two files:
- arifos_aaa_mcp/server.py ✅
- aaa_mcp/server.py ⚠️

**What to do:**  
Use the one with **arifos_** prefix. Ignore the shorter one.

---

### QUICK CHECKLIST

Before running any command:

- [ ] Does it say arifos_aaa_mcp? → ✅ Good to go
- [ ] Does it only say aaa_mcp? → ❌ Stop, ask first
- [ ] Are you unsure? → ❌ Ask AGI-Opencode

---

### FOR FUTURE AGENTS

If an AI agent (like me) is working on your VPS:

**Tell them:**
> Use arifos_aaa_mcp as the canonical surface. aaa_mcp is legacy internal.

---

### SUMMARY

| Name | Role | Use? |
|------|------|------|
| arifos_aaa_mcp | Public interface | ✅ YES |
| aaa_mcp | Internal implementation | ❌ NO |

---

**Created:** 2026-03-05  
**By:** AGI-Opencode  
**For:** Arif Fazil  
**Purpose:** Prevent confusion about MCP naming
