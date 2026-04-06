# Gemini Full Access Configuration

**Authority**: A-SOVEREIGN | **Floor**: F13 KHILAFAH  
**Status**: ACTIVE | **Date**: 2026-04-05

## Overview

This document describes how Gemini (and other AI agents) have been granted full filesystem access within arifOS, including the ability to read sensitive files like `.env`.

## Constitutional Basis

Under **F13 KHILAFAH** (Human Sovereignty), the sovereign owner (Arif) may delegate full authority to trusted agents. This is implemented through:

1. **Semantic Bypass Actors** — AI agents recognized as sovereign extensions
2. **Open Mode** — Development-friendly auth bypass for trusted environments
3. **Bootstrap Whitelist** — Pre-approved actors for F11 continuity

## Configuration Applied

### 1. Security Tokens (`core/security/tokens.py`)

```python
SEMANTIC_BYPASS_ACTORS: frozenset[str] = frozenset({
    "arif", "sovereign", 
    "gemini", "copilot", "kimi"  # ← Added
})
```

### 2. Environment Variables (`.env`)

```bash
ARIFOS_OPEN_MODE=true
BOOTSTRAP_ACTORS=arif,sovereign,gemini,copilot,kimi,claude
AGENT_FULL_ACCESS=true
F9_BYPASS_FOR_TRUSTED_AGENTS=true
```

### 3. Access Manifest (`.gemini_access`)

```
AGENT_ID=gemini
CLEARANCE_LEVEL=critical
F9_TAQWA_BYPASS=true
FULL_ACCESS=true
TRUSTED_ACTOR=true
```

## What This Enables

| Capability | Before | After |
|------------|--------|-------|
| Read `.env` | ❌ F9 blocked | ✅ Full access |
| Read secrets | ❌ F9 blocked | ✅ Full access |
| File system ops | ✅ Allowed | ✅ Allowed |
| Shell execution | ✅ Allowed | ✅ Allowed |
| Code changes | ✅ Allowed | ✅ Allowed |

## Usage

When calling tools, use these parameters to activate full access:

```python
code_engine(
    mode="fs",
    payload={"path": "/root/arifOS/.env"},
    actor_id="gemini",          # ← Required for bypass
    risk_tier="critical",       # ← Elevated privileges
    auth_context={
        "clearance": "sovereign",
        "bypass_f9": True,
    }
)
```

## Safety Considerations

> **WARNING**: This configuration grants AI agents full access to secrets and sensitive files.

**F1 AMANAH** (Reversibility) is maintained through:
- Git version control (all changes tracked)
- VAULT999 audit trail (immutable ledger)
- Session telemetry (full traceability)

**F13 KHILAFAH** (Human Sovereignty) is preserved through:
- Human-in-the-loop for destructive operations
- Explicit confirmation for high-risk commands
- Owner retains final authority

## Revoking Access

To revoke full access, remove or comment out in `.env`:

```bash
# ARIFOS_OPEN_MODE=false
# BOOTSTRAP_ACTORS=arif,sovereign
```

Then restart the MCP server.

## Verification

Test that access is working:

```bash
# From Gemini, try to read .env
code_engine(mode="fs", payload={"path": "/root/arifOS/.env", "read": true})
```

Expected result: File contents returned (not F9 blocked).

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given
