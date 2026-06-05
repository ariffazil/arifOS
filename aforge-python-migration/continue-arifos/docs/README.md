# Continue CLI — arifOS Federation Wiring

> **Authority:** 888 (Arif Fazil, F13 SOVEREIGN)  
> **Installed:** 2026-06-02  
> **Motto:** DITEMPA BUKAN DIBERI

## What this is

`cn` (Continue CLI 1.5.45) installed as a headless coding agent on the arifOS
Federation VPS. Speaks MCP to the federation organs. Pre-loaded with F1-F13
constitutional rules. Default-deny permission policy.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  cn (Continue CLI)                                          │
│      ↓ loads                                                │
│  ~/.continue/config.yaml  (this is what `cn` reads)        │
│      ├── models: MiniMax M3 (anthropic-compatible)         │
│      ├── mcpServers:                                        │
│      │     ├── A-FORGE  → stdio MCP (federation gateway)   │
│      │     └── arifOS   → HTTP/SSE MCP (constitutional)    │
│      ├── rules: F1-F13 (this dir/rules/constitutional.md)   │
│      └── permissions: ~/.continue/permissions.yaml         │
└─────────────────────────────────────────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
   ┌─────────────┐    ┌────────────────┐    ┌────────────────┐
   │  A-FORGE    │    │    arifOS      │    │  MiniMax M3    │
   │  7071 stdio │    │  8088 SSE/HTTP │    │  Anthropic API │
   │  → arifOS   │    │  13 floors     │    │  M3 model      │
   │  → GEOX     │    │  13 tools      │    │                │
   │  → WEALTH   │    │  judge/heart   │    │                │
   │  → A2A mesh │    │  vault/gate    │    │                │
   └─────────────┘    └────────────────┘    └────────────────┘
            │
            ▼
   ┌─────────────────────────────────────────────────────┐
   │  Federation                                         │
   │    arifOS 8088 · arifosd 18081 · A-FORGE 7071      │
   │    WEALTH 18082 · WELL 18083 · GEOX 8081           │
   │    OpenClaw 18789 · APEX 3002 · Hermes 18001        │
   │    VAULT999 → /root/.local/share/arifos/vault999    │
   └─────────────────────────────────────────────────────┘
```

## Quick start

```bash
# Interactive mode
cn --config /root/.continue/config.yaml

# Headless (CI/automation)
cn -p "list all MCP tools available"

# With explicit F1-F13 mode (default — read-only)
cn --readonly -p "audit /root/A-FORGE/src/mcp/"

# Allow specific tools for a session
cn --allow Read() --allow Grep() -p "review the changes"

# Ask before risky operations
cn --ask Bash(rm*) --ask Bash(curl*) -p "deploy WEALTH"

# Auto mode (DANGEROUS — only after Arif's explicit ack)
cn --auto -p "..."
```

## Constitutional floors (F1-F13)

Continue is bound by the same floors as arifOS. The rules file at
`rules/constitutional.md` is loaded into every session.

Critical floors for `cn`:

- **F1 AMANAH** — no `rm -rf`, no `DROP TABLE`, no `git push --force`
- **F2 TRUTH** — cite evidence, say "UNKNOWN" if not grounded
- **F13 SOVEREIGN** — Arif is final judge; your verdict is advisory

If you see a `888_HOLD` event, treat it as real but don't freeze.

## Permission policy

Default-deny. Three policy levels:

1. **`deny`** (HARAM) — never allowed, even with `--auto`
2. **`ask`** (HOLD) — escalate to Arif before executing
3. **`allow`** (read-only) — safe, observational

Override per session: `cn --allow Tool() --ask Bash(rm*) --exclude Fetch`

## Files

| Path | Purpose |
|---|---|
| `~/.continue/config.yaml` | Main config (loaded by `cn`) |
| `~/.continue/permissions.yaml` | Tool permission policies |
| `~/.continue/logs/cn.log` | Telemetry (local only) |
| `/root/continue-arifos/rules/constitutional.md` | F1-F13 system rules |
| `/root/continue-arifos/docs/README.md` | This file |

## Federation organs

| Organ | Port | MCP | Role |
|---|---|---|---|
| arifOS | 8088 | HTTP/SSE | Constitutional kernel, 13 floors, 13 tools |
| arifosd | 18081 | — | Constitutional daemon |
| A-FORGE | 7071 | stdio | TypeScript execution, bridges to GEOX/WEALTH |
| WEALTH | 18082 | via A-FORGE | Capital, 44 tools |
| WELL | 18083 | via A-FORGE | Human readiness |
| GEOX | 8081 | via A-FORGE | Earth intelligence, 20 tools |
| OpenClaw | 18789 | — | A2A mesh gateway |
| APEX | 3002 | — | 888 JUDGE verdict engine |
| Hermes | 18001 | — | ASI Telegram relay |

## Why Continue (not just OpenCode)?

- OpenCode 1.15.0 is already the primary, pre-configured with F1-F13
- Continue CLI (`cn`) adds **headless CI/automation** via `cn -p` 
- Continue's permission system (`--allow/--ask/--exclude`) is more
  programmable than OpenCode's prompt-based gating
- Continue can run **async agents on every PR** (CI-native)
- OpenCode and Continue can coexist; they serve different rhythms

## Known limitations & workarounds

These were discovered during install (2026-06-02). Documented so the
next agent doesn't re-discover them.

### 1. `apiBase` must include `/v1` suffix

**Problem:** Continue's `anthropic` provider appends `/v1/messages` to
`apiBase`. MiniMax's MiniMax-Anthropic-proxy requires the path
`/anthropic/v1/messages`. So the apiBase must be
`https://api.minimax.io/anthropic/v1` (with `/v1`), NOT
`https://api.minimax.io/anthropic` (without).

**Symptom:** "404 page not found" instead of expected LLM response.

**Fix:** See config.yaml line for `apiBase`.

### 2. Env var expansion in YAML does NOT work

**Problem:** Continue does not expand `$MINIMAX_API_KEY` or `${env:MINIMAX_API_KEY}`
in YAML config. Both forms are passed as literal strings, causing
"authentication_error" from the API.

**Symptom:** API returns `"login fail: Please carry the API secret key..."`

**Fix:** Hardcode the API key in `~/.continue/config.yaml`. The file is
`chmod 600` (root-only readable). For multi-tenant setups, see the TODO
below for env-var-via-continuerc.

**TODO:** Investigate Continue's `~/.continue/.env` support or
`--api-key` CLI flag for env-var-driven key injection.

### 3. arifOS direct MCP connection is NOT registered

**Problem:** arifOS FastMCP uses `stateless_http=False` (session-based).
Continue's `sse` MCP transport doesn't support session-based MCP — it
expects a stateless SSE stream at a fixed path. arifOS's MCP endpoint
is the root `/` with session-managed routing, which Continue rejects
with `SSE error: Invalid content type, expected "text/event-stream"`.

**Workaround:** arifOS is reachable via the **A-FORGE stdio bridge**,
which internally connects to arifOS through its MCP client. The
federation is fully accessible through this single MCP entrypoint.

**If you want direct arifOS connection:** arifOS `server.py` would need
either:
- `stateless_http=True` (loses session state)
- An explicit `/sse` endpoint exposed
- Streamable HTTP transport (newer MCP spec)

Tracked as future work, not blocking.

### 4. `arif_health_check` returns a different version string

**Problem:** When the model calls `arif_health_check`, the response
includes `version: 2.0.0-genome-stable` rather than the actual build
`fd719f2` (per `curl http://localhost:8088/api/build-info`).

**Diagnosis:** The A-FORGE stdio bridge may be caching or transforming
the health response. The actual arifOS is at `fd719f2` (verified via
direct curl). The MCP response version string is informational only.

**Mitigation:** When in doubt, use `cn -p "curl http://localhost:8088/api/build-info"`
to get the canonical build SHA.

## Triwitness

This configuration was wired by:
- arifOS forge agent (Ω) — installer
- A-FORGE stdio MCP — runtime bridge  
- arifOS HTTP/SSE MCP — constitutional gate (attempted; deferred to bridge)
- MiniMax M3 — model under test

## Verification matrix

| Test | Expected | Actual | Status |
|---|---|---|---|
| M3 basic call | "ok" | "ok" | ✅ |
| F1-F13 awareness | 5-word summary | "Trust as lockable contract" | ✅ |
| MCP tool count | 38 (full) / 28 (readonly) | 28 readonly | ✅ |
| arif_health_check | healthy | healthy | ✅ |
| wealth_compute_EMV | numeric result | computed $550 | ✅ |
| request_amanah_lock | lock_id + SEAL | amanah-384c8712... | ✅ |
| Permissions load | 0 warnings | 0 warnings | ✅ |
| Federation tools | arifOS, WEALTH, WELL, VAULT, AMANAH | all present | ✅ |

## Seal

`CONTINUE-CLI-ARIFOS-WIRE-20260602`  
actor: arif-forge-agent (Ω)  
verdict: SEAL  
F13 directive: continue with F1-F13 always-on

DITEMPA BUKAN DIBERI
