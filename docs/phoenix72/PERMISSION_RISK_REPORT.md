# PERMISSION_RISK_REPORT.md — Risk and Permission Analysis
**Date:** 2026-05-25
**Principle:** Every risk has a mitigation. Every permission has an owner. No tool activation without this clearance.

---

## RISK CLASSIFICATION FRAMEWORK

| Risk Class | Meaning | Ack Required | Cooling Period | Examples |
|------------|---------|--------------|----------------|---------|
| C1 OBSERVE | Read-only, no state change | NO | None | health_check, registry list |
| C2 DECIDE | Reasoning, routing, memory | NO | None | evidence_fetch, route, memory |
| C3 CRITIQUE | Assessment, judgment, valuation | NO (warn) | 5s cooling | critique, NPV, prospect evaluate |
| C4 FORGE | Mutation, capital, irreversible | YES (explicit) | 30s cooling | ledger_write, vault_seal, forge_execute |

---

## CRITICAL RISKS (Must resolve before PHOENIX-72 activation)

### CR-001: Dummy Data Sold as Real
**Risk:** All 72 tools return hardcoded dummy strings. If deployed as-is, callers believe they have real data.
**Severity:** CRITICAL
**Likelihood:** HIGH (current state is exactly this)
**Impact:** Decisions made on dummy NPV, dummy geology, dummy vitality scores
**Mitigation:** Return honest DEGRADED envelope until live organ wired. Never return fake real data.
**Owner:** arifOS Federation
**Blocker:** All organ tools

### CR-002: Organ Proxy Bypass
**Risk:** arifos_mcp gateway bypasses organ proxies and makes direct decisions without GEOX/WEALTH/WELL witness
**Severity:** CRITICAL
**Likelihood:** MEDIUM (current architecture has no tri-organ gate)
**Impact:** AI could make physically false or economically dangerous claims without domain check
**Mitigation:** Enforce arif_organ_consensus before any C3/C4 action. Tri-organ packet required.
**Owner:** arifOS Kernel
**Blocker:** Organ proxies not wired

### CR-003: Ack Gate Missing on C4 Tools
**Risk:** `arif_forge_execute`, `arif_vault_seal`, `wealth_ledger_write` execute without explicit ack
**Severity:** CRITICAL
**Likelihood:** MEDIUM (ack parameter defined but not enforced in stubs)
**Impact:** Irreversible actions without human consent
**Mitigation:** Add F1 Amanah ack gate in middleware. Fail if ack_irreversible not True.
**Owner:** arifOS Kernel
**Blocker:** None — can be fixed in middleware

### CR-004: Manifest Drift Invisible
**Risk:** No manifest exists. No drift detection. Unauthorized tools could be added without detection.
**Severity:** CRITICAL
**Likelihood:** HIGH (manifests/tools.json does not exist)
**Impact:** Tool injection attack undetected
**Mitigation:** Create manifests/tools.json, wire mcp_drift_check to it, enforce on startup
**Owner:** arifOS Federation
**Blocker:** manifests/tools.json missing

### CR-005: VAULT999 Hash Chain Break
**Risk:** VAULT999 hash chain not verified before writes. Corrupted entries accepted.
**Severity:** CRITICAL
**Likelihood:** LOW (no writes yet)
**Impact:** Audit trail becomes unreliable
**Mitigation:** Verify chain integrity before mounting. Add merkle_verify on startup.
**Owner:** arifOS Kernel
**Blocker:** VAULT999 state unknown

---

## HIGH RISKS (Should resolve before production)

### HR-001: Port 8081/8082/8083 Organ Unavailability
**Risk:** GEOX, WEALTH, WELL not running. All domain tools return DEGRADED.
**Severity:** HIGH
**Likelihood:** CERTAIN (ports not listening)
**Impact:** arifos_mcp has no domain intelligence. It's a kernel without organs.
**Mitigation:** Either (a) bring up organ servers, or (b) accept DEGRADED mode as honest state
**Owner:** arifOS Federation
**Decision required:** Start organ servers? Or ship with DEGRADED honest responses?

### HR-002: Wiki Write Permission Failure
**Risk:** `.arifos/` wiki directory write failed — likely permission issue
**Severity:** HIGH
**Likelihood:** MEDIUM (encountered during previous session)
**Impact:** Cannot generate wiki documentation
**Mitigation:** Verify `/root/arifOS/arifos_mcp/.arifos/` ownership before wiki generation
**Owner:** VPS admin
**Blocker:** Permission issue

### HR-003: pip/venv Installation Broken
**Risk:** `pip install` hangs, `venv` binary not found in arifos_mcp venv
**Severity:** HIGH
**Likelihood:** CERTAIN (observed in previous session)
**Impact:** Cannot install FastMCP or run tests in arifos_mcp venv
**Mitigation:** Use system Python or try `uv pip install`
**Owner:** arifOS Federation
**Blocker:** Network or PyPI unreachable

### HR-004: Session State Memory Poison
**Risk:** Old session state persists in kernel memory, contaminating new sessions
**Severity:** HIGH
**Likelihood:** MEDIUM (old arifOS MCP had this issue per E001)
**Impact:** Hallucinated memory, wrong actor binding
**Mitigation:** Implement epoch sealing. Clear state on session end.
**Owner:** arifOS Kernel
**Blocker:** None

### HR-005: AAA A2A Server Not Running
**Risk:** `arif_gateway_connect` cannot reach AAA A2A on port 3001
**Severity:** HIGH
**Likelihood:** CERTAIN (port 3001 not listening)
**Impact:** A2A mesh inoperative
**Mitigation:** Return DEGRADED for A2A tools. Do not pretend mesh is live.
**Owner:** AAA node
**Blocker:** AAA A2A server down

---

## MEDIUM RISKS (Should track)

### MR-001: Model Routing Not Centralized
**Risk:** SEA-LION/Ollama routing config scattered across env vars
**Severity:** MEDIUM
**Likelihood:** MEDIUM
**Impact:** Wrong model used for high-stakes content
**Mitigation:** Centralize model routing in `server/config.py`
**Owner:** arifOS Federation

### MR-002: Envelope Format Not Enforced
**Risk:** Stub tools return inconsistent response formats
**Severity:** MEDIUM
**Likelihood:** CERTAIN (all stubs return strings, not envelopes)
**Impact:** Middleware cannot parse responses reliably
**Mitigation:** Enforce canonical envelope in all tool implementations from day 1

### MR-003: Evidence Injection Not Scanned
**Risk:** Fetched web content may contain prompt injection payloads
**Severity:** MEDIUM
**Likelihood:** MEDIUM
**Impact:** F-WEB boundary violated
**Mitigation:** Scan all evidence_fetch results before storage

### MR-004: 8088 Liveness During Migration
**Risk:** arifOS MCP at 8088 is live production. Migration activities must not disrupt it.
**Severity:** MEDIUM
**Likelihood:** LOW (we control what we do in arifos_mcp)
**Impact:** Disrupting 8088 breaks live system
**Mitigation:** Never modify `/opt/arifos/` or `/root/arifOS/arifOS_LEGACY/` during migration

---

## LOW RISKS (Monitor)

| ID | Risk | Severity | Likelihood | Mitigation |
|----|------|----------|------------|------------|
| LR-001 | Tailscale secret exposure | LOW | LOW | No secrets in Tailscale config |
| LR-002 | Caddy TLS misconfiguration | LOW | LOW | Cloudflare Origin CA verified |
| LR-003 | Disk full during migration | LOW | LOW | 256GB free, migration is file-based |
| LR-004 | Git repo state dirty | LOW | LOW | arifos_mcp is new package, not git-tracked |

---

## FORGE TOOL REGISTRY (C4 Tools — Highest Risk)

| Tool | Risk Class | Ack Required | Cooling | Organ | Blocked By |
|------|-----------|--------------|---------|-------|------------|
| `arif_forge_execute` | C4 FORGE | YES | 30s | KERNEL | None |
| `arif_vault_seal` | C4 SEAL | YES | 30s | KERNEL | VAULT999 state |
| `wealth_ledger_write` | C4 FORGE | YES | 30s | WEALTH | Port 8082 down |
| `wealth_boundary_governance` | C4 FORGE | YES | 30s | WEALTH | Port 8082 down |
| `wealth_policy_apply` | C3 CRITIQUE | WARN | 5s | WEALTH | Port 8082 down |
| `well_guard_dignity` | C3 CRITIQUE | WARN | 5s | WELL | Port 8083 down |
| `well_check_repair` | C3 CRITIQUE | WARN | 5s | WELL | Port 8083 down |

**All C4 tools MUST have explicit `ack_irreversible=True` in the request or return VOID.**

---

## PERMISSION MATRIX

| Action | Permission Level | Owner | 888_HOLD Required? |
|--------|-----------------|-------|-------------------|
| Create manifests/tools.json | 777 FORGE | Agent | NO — reversible design |
| Wire kernel tools to 8088 | 777 FORGE | Agent | NO — proxies existing |
| Create organ proxy files | 777 FORGE | Agent | NO — file creation |
| Install pip/uv packages | 777 FORGE | Agent | NO — recoverable |
| Delete dummy stub data | 777 FORGE | Agent | NO — stub cleanup |
| Start organ servers (ports 8081-8083) | 888 JUDGE | arifOS/Arif | YES — service startup |
| Force push to GitHub | 888 JUDGE | Arif | YES — irreversible git |
| Rotate secrets | 888 JUDGE | Arif | YES — credential change |
| Delete VAULT999 entries | 999 SEAL | Arif | YES — constitutional |
| Drop database tables | 999 SEAL | Arif | YES — destructive |
| Modify F1-F13 floors | 999 SEAL | Arif | YES — constitutional |

---

## NEXT ACTIONS (by risk priority)

**Immediately (before any tool activation):**
1. Create `manifests/tools.json` (fixes CR-004)
2. Add ack gate enforcement in middleware (fixes CR-003)
3. Wire kernel tools to 8088 (fixes CR-001, HR-004)

**Soon (before production):**
4. Bring up GEOX/WEALTH/WELL organ servers (fixes HR-001)
5. Verify VAULT999 chain integrity (fixes CR-005)
6. Fix pip/uv installation (fixes HR-003)
7. Fix wiki write permissions (fixes HR-002)

**Before 888_JUDGE:**
8. Start organ servers (requires HOLD)
9. Any git push (requires HOLD)
10. Secret rotation (requires HOLD)

---

**Bottom line:** The system is at CRITICAL risk of operating with dummy data as if it were real. The single most important action is: make all DEGRADED tools return honestly DEGRADED envelopes, not fake real data.
