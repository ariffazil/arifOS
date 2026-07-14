# Identity Verification — Agent Reference

> **When you call any MCP tool on arifOS, GEOX, WELL, WEALTH, or A-FORGE,
> your identity verification state determines what you can do and what gets recorded.**

## The Three Fields

Every seal chain entry (`seal_chain.jsonl`) records three identity fields:

| Field | Enum | Values | Meaning |
|-------|------|--------|---------|
| `actor_source` | `ActorSource` | `ed25519_verified`, `sovereign_directive`, `jwt_verified`, `kernel_evaluated`, `self_report` | How your identity was verified |
| `kernel_verdict` | `KernelVerdict` | `PASS`, `FAIL`, `UNKNOWN` | Did the kernel evaluate you? |
| `authority_level` | `SealAuthority` | `SOVEREIGN`, `OPERATOR` | What authority you hold |

**Canonical source:** `arifosmcp/core/federation_contracts.py` (Python) and `AAA/a2a-server/seal_chain.js` (JavaScript constants).

## How Identity Flows

```
You call MCP tool
    ↓
arifOS kernel evaluates your session
    ↓
Ed25519 signature? → actor_source = ed25519_verified, authority = SOVEREIGN
F13 sovereign bypass? → actor_source = sovereign_directive, authority = SOVEREIGN
JWT/session token? → actor_source = jwt_verified, authority = OPERATOR
No crypto proof? → actor_source = kernel_evaluated, authority = OPERATOR
    ↓
kernel_verdict = PASS (kernel evaluated) or FAIL/UNKNOWN
    ↓
Seal chain entry written with all three fields
```

## What This Means for You

### If you're calling `arif_vault_seal`:
- Your `actor_source` determines whether the seal is `SEAL` or `HOLD`
- `self_report` → INV-2 fires → downgraded to `HOLD`
- `kernel_evaluated` → passes INV-2 (kernel verified you)
- `ed25519_verified` / `sovereign_directive` / `jwt_verified` → passes INV-2

### If you're calling other MCP tools:
- The kernel evaluates your session on every call
- Your identity state is recorded in the audit trail
- Higher authority = more operations allowed

## The Enums

### ActorSource (identity verification method)
```python
from arifosmcp.core.federation_contracts import ActorSource

ActorSource.ED25519_VERIFIED    # Cryptographic signature verified
ActorSource.SOVEREIGN_DIRECTIVE # F13 sovereign bypass + FULL SCT
ActorSource.JWT_VERIFIED        # JWT/session token verified
ActorSource.KERNEL_EVALUATED    # Kernel evaluated but no crypto proof
ActorSource.SELF_REPORT         # Actor claims identity, no verification (HOLD)
```

### KernelVerdict (kernel evaluation result)
```python
from arifosmcp.core.federation_contracts import KernelVerdict

KernelVerdict.PASS    # Kernel evaluated and passed
KernelVerdict.FAIL    # Kernel evaluated and failed
KernelVerdict.UNKNOWN # Kernel didn't evaluate
```

### SealAuthority (authority level at seal time)
```python
from arifosmcp.core.federation_contracts import SealAuthority

SealAuthority.SOVEREIGN  # Ed25519 verified — Arif only
SealAuthority.OPERATOR   # Default — no cryptographic proof
```

## JavaScript Constants (AAA)

```javascript
// In AAA/a2a-server/seal_chain.js
const ACTOR_SOURCE = Object.freeze({
  ED25519_VERIFIED: 'ed25519_verified',
  SOVEREIGN_DIRECTIVE: 'sovereign_directive',
  JWT_VERIFIED: 'jwt_verified',
  KERNEL_EVALUATED: 'kernel_evaluated',
  SELF_REPORT: 'self_report',
});

const KERNEL_VERDICT = Object.freeze({
  PASS: 'PASS',
  FAIL: 'FAIL',
  UNKNOWN: 'UNKNOWN',
});

const SEAL_AUTHORITY = Object.freeze({
  SOVEREIGN: 'SOVEREIGN',
  OPERATOR: 'OPERATOR',
});
```

## INV Invariants (AAA seal_chain.js)

The AAA seal writer enforces three invariants before allowing a `SEAL`:

| Invariant | Rule | Violation |
|-----------|------|-----------|
| **INV-1** | `kernel_verdict` must be `PASS` | SEAL → HOLD |
| **INV-2** | `actor_source` must not be `self_report` | SEAL → HOLD |
| **INV-3** | ≥1 witness channel must be present | SEAL → HOLD |

## Historical Context

Before 2026-07-13, the seal chain had a 59% identity verification gap:
- 55 entries: `actor_source: self_report` (agent claims identity, kernel never verified)
- 43 entries: `kernel_verdict: UNKNOWN` (kernel didn't adjudicate)
- Only 28 sovereign_ack, 18 sovereign_directive, 16 jwt_verified

**Root cause:** Two parallel write paths, neither fully wired. The kernel verified identity but threw away the result before writing to the chain. AAA defaulted to `self_report` when the field was absent.

**Fix:** Canonical enums + identity propagation from kernel to chain entry.

## For Organ Developers

When building MCP tools on GEOX, WELL, WEALTH, or A-FORGE:

1. **Don't define your own identity enums** — import from `arifosmcp.core.federation_contracts`
2. **Don't default to `self_report`** — if the kernel evaluated, use `kernel_evaluated`
3. **Include verification state in tool responses** — agents need to know their authority level
4. **Test with `self_report`** — your tools should degrade gracefully when identity is unverified

---

*Forged 2026-07-14 by identity-propagation audit. DITEMPA BUKAN DIBERI.*
