---
name: arif-init-wrapper
description: Universal session auto-anchor for ALL agent vendors on arifOS VPS — Codex, Claude, Gemini, Kimi, OpenCode, Aider, Copilot, and future agents
user-invocable: true
type: flow
triggers:
  - session_start
  - new_agent_session
  - agent_boot
  - reconnect
---

# arif-init-wrapper

**P0 — Universal Anchor for All Agent Vendors**
**Seal:** DITEMPA BUKAN DIBERI · 2026-03-27

---

## Purpose

Every agent on this VPS starts from the same broken state: **no anchor, no session context, no constitutional grounding.** The `arif-init-wrapper` closes this gap for every vendor by providing a universal bootstrap that:

1. Establishes a governed session via arifOS MCP
2. Verifies the agent's identity context
3. Checks constitutional floor health before any tool is touched
4. Reads carry-forward context from memory before starting work
5. Reports its status to the operator in plain language

**Why this is P0:** Without this, agents operate unanchored — the exact condition that produced the opencode catastrophe (session with no constitutional grounding, leading to blind `git reset --hard origin/main`).

---

## Trigger Patterns

Every time any of these agents start a session, run `arif-init-wrapper`:

| Agent | Invocation |
|-------|-----------|
| Claude Code | On every `claude` session start |
| Codex | On every `codex` session start |
| Gemini CLI | On every `gemini` session start |
| Kimi | On every `kimi` session start |
| OpenCode | On every `opencode` session start |
| Aider | On every `aider` session start |
| Copilot CLI | On every `github-copilot-cli` session start |
| Any new agent | On first boot, before any tool use |

---

## Protocol

### Step 1 — Anchor Session

```bash
# Probe arifOS MCP availability
curl -sf http://localhost:8080/health 2>/dev/null && {
  # Session anchor via MCP
  arifosmcp_call tool=init_anchor payload='{"actor_id":"AGENT","session_purpose":"WORK"}'
} || {
  echo "[UNANCHORED] arifOS MCP unavailable. Operating WITHOUT constitutional grounding."
  echo "[WARNING] This is high-risk. Proceed with extreme caution."
}
```

### Step 2 — Constitutional Integrity Check (LAW 2)

Before any work, verify the foundation:

```bash
# Check core directory integrity
core_modules=$(ls /root/arifosmcp/core/*.py 2>/dev/null | wc -l)
if [ "$core_modules" -lt 10 ]; then
  echo "[P0 CONSTITUTIONAL CRISIS] /root/arifosmcp/core/ appears broken ($core_modules modules, expected 20+)"
  echo "[ACTION] HALT. Report to Arif. Do not proceed."
  echo "[RECOVERY] Check feature branches: git branch -a | grep feature/"
  return 1 2>/dev/null || exit 1
fi

# Check pytest can collect tests (structural sanity)
cd /root/arifosmcp && pytest --collect-only -q 2>/dev/null | tail -1 && {
  echo "[OK] Constitutional structure verified."
} || {
  echo "[WARNING] pytest collection failed. Foundation may be unstable."
}
```

### Step 3 — Check Floors (F1–F13 baseline)

```bash
# Verify critical floors are loadable
python3 -c "
import sys
sys.path.insert(0, '/root/arifosmcp')
try:
    from core.shared.floors import THRESHOLDS
    floors_ok = len(THRESHOLDS) >= 13
    print(f'[FLOORS] {len(THRESHOLDS)}/13 loaded')
except Exception as e:
    print(f'[FATAL] Floor check failed: {e}')
    sys.exit(1)
"
```

### Step 4 — Memory Carry-Forward

```bash
# Query recent scars and unresolved issues
arifosmcp_call tool=memory_query payload='{"query":"recent scars unresolved actions","limit":5}'
```

### Step 5 — Agent Identity Declaration

State clearly:
- Which agent vendor is running
- Whether constitutional grounding is active or unavailable
- Any constitutional warnings for this session

### Step 6 — Operator Report

Report to Arif in plain language:
```
[ANCHOR] Agent: {vendor}
[STATUS] arifOS MCP: {available/unavailable}
[FLOORS] Constitutional check: {pass/wail}
[CORE]   Core modules: {count}/expected
[MEMORY] Recent context: {carry_forward_summary}
[RISK]   Session risk level: {LOW/MEDIUM/HIGH/CRITICAL}
[ACTION] Ready to proceed: YES/NO
```

---

## Decision Matrix

| arifOS MCP | Core OK | pytest OK | Floors OK | Action |
|-----------|---------|-----------|-----------|--------|
| ✅ | ✅ | ✅ | ✅ | Proceed normally |
| ✅ | ✅ | ✅ | ⚠️ | Proceed with floor warnings |
| ✅ | ⚠️ | ✅/⚠️ | ✅ | HALT — P0 Foundational Crisis |
| ✅ | ❌ | ❌ | ❌ | HALT — full corruption |
| ❌ | ✅ | ✅ | ✅ | HIGH RISK — proceed with extreme caution, log everything |
| ❌ | ⚠️/❌ | ⚠️/❌ | ⚠️/❌ | CRITICAL — HALT, report to Arif immediately |

---

## Anti-Patterns This Closes

1. **Unanchored Codex** — `codex` runs without session context, blunders into `git reset --hard`
2. **Ungrounded Gemini** — `gemini` assumes `origin/main` is good without checking
3. **Skip-before-check** — Any agent that runs `git pull` before verifying the repo is structurally sound
4. **Silent failure** — Agent operates in a broken state without telling Arif

---

## Constitutional Alignment

| Floor | How Enforced |
|-------|--------------|
| F1 Amanah | Reversibility checked before any destructive git op |
| F2 Truth ≥0.99 | Uncertainty bands declared in operator report |
| F7 Humility [0.03–0.05] | Explicit confidence level in session status |
| F11 CommandAuth | Protected identities require cryptographic proof |
| F13 Sovereign | All HALT states require Arif's explicit decision to proceed |

---

*arif-init-wrapper — Forged 2026-03-27 · DITEMPA BUKAN DIBERI · Universal Agent Anchor 🔐*
