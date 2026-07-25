# Amendment A00 — Lease-Based Session Model (arifOS Kernel)

## 1. Context
**Organ:** arifOS Kernel (MCP runtime)  
**Scope:** Identity → Governance → Execution chain  
**EUREKA:** Six-Plane Execution Loop — Steps 1–4 (Identity, Class, Verdict)  
**Canon:** 000_KERNEL_CANON §3 — Identity Primacy  
**Canon:** 000_KERNEL_CANON §4 — 000→999 Pipeline

## 2. Doctrine Violated (Before)
- `arif_init` requires interactive session.
- Cron / wrappers cannot obtain Lease ID (LID) without chat context.
- A01/A02/A03 membranes cannot operate as governed wrappers.
- Identity binding collapses for non-interactive agents.

**Result:**
- Golden Lifecycle cannot be applied to OpenClaw, Hermes, OpenCode.
- F3 (TRI-WITNESS) and F11 (AUDITABILITY) incomplete.

## 3. Constitutional Amendment (Membrane)
Kernel MUST support sessionless lease issuance:

### 3.1 Lease Identity
```
arif_init --lease-class=<CLASS>
```
→ issues LID (UUIDv7) without interactive session.

### 3.2 Lease Continuity
All governance tools MUST accept:
```
--lease-id <LID>
```
for:
- `arif_think`
- `arif_judge`
- `arif_seal`

### 3.3 Lease Validity Rules
- **TTL:** 30s default (configurable per class)
- **Scope:** BOOTSTRAP, DIGEST, CODE_PATCH
- **Binding:** LID MUST be recognized across all MCP endpoints
- **Rejection:** Expired or mismatched LID → VOID verdict

### 3.4 Kernel Interface Contract
New MCP endpoints:
- `/mcp/arif_init_lease`
- `/mcp/arif_think_lease`
- `/mcp/arif_judge_lease`
- `/mcp/arif_seal_lease`

All MUST operate without chat session.

## 4. Doctrine Restored (After)
- Identity binding restored for non-interactive agents.
- A01/A02/A03 become fully operational.
- Golden Lifecycle applies universally across federation.
- F1, F3, F4, F11 measurable for all organs.

## 5. Seal
**Branch:** `arch/tri-agent-boundaries` (arifOS repo)  
**Verdict:** SEAL  
**Scope:** Kernel MUST implement lease-based session model for governed wrappers.
