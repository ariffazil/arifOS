# VERDICT SCHEMA STANDARD
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL

---

## 🎯 PURPOSE

Standardize verdict structures across ALL arifOS tools to ensure pipeline compatibility, deterministic parsing, and constitutional enforcement.

**F2 (Truth):** All tools MUST return identical verdict schema for interoperability.  
**F11 (Auditability):** Verdicts MUST be cryptographically verifiable and machine-parseable.

---

## 📐 UNIFIED VERDICT SCHEMA

Every tool in the arifOS ecosystem MUST return a response conforming to this schema:

```typescript
interface ArifOSVerdict {
  // ═══════════════════════════════════════
  // CORE IDENTITY (Required)
  // ═══════════════════════════════════════
  ok: boolean;                    // Operation success (not verdict status!)
  verdict: VerdictCode;           // SEAL | SABAR | VOID | PARTIAL
  status: StatusCode;             // Detailed status string
  
  // ═══════════════════════════════════════
  // TOOL METADATA (Required)
  // ═══════════════════════════════════════
  tool: string;                   // Canonical tool name
  stage: StageCode;               // 000-999 pipeline stage
  schema_version: string;         // "1.0.0"
  timestamp: string;              // ISO 8601 UTC
  
  // ═══════════════════════════════════════
  // CONSTITUTIONAL METRICS (Required)
  // ═══════════════════════════════════════
  metrics: {
    delta_s: number;              // Entropy change (F4 Clarity)
    confidence: number;           // Ω₀ epistemic uncertainty (F7 Humility)
    coherence: number;            // G_star (F8 Genius)
    peace2: number;               // Stability metric (F5 Peace²)
  };
  
  // ═══════════════════════════════════════
  // AUTHORITY & WITNESS (Required)
  // ═══════════════════════════════════════
  authority: {
    actor_id: string;             // 888_JUDGE | anonymous | <session_id>
    level: AuthorityLevel;        // sovereign | delegated | anonymous
    auth_state: AuthState;        // verified | pending | unverified
    human_required: boolean;      // Was human approval mandated?
  };
  
  // ═══════════════════════════════════════
  // PAYLOAD (Tool-Specific)
  // ═══════════════════════════════════════
  payload?: unknown;              // Tool-specific return data
  
  // ═══════════════════════════════════════
  // ERROR HANDLING (Required if ok=false)
  // ═══════════════════════════════════════
  errors?: VerdictError[];        // Structured error objects
  
  // ═══════════════════════════════════════
  // TRACE & PROVENANCE (Required)
  // ═══════════════════════════════════════
  trace?: {
    session_id: string;           // Session UUID
    request_id: string;           // Unique request ID
    integrity_hash?: string;      // SHA-256 of critical fields
  };
  
  // ═══════════════════════════════════════
  // CONSTITUTIONAL CONTEXT (Required)
  // ═══════════════════════════════════════
  constitutional_context?: {
    floors_checked: number[];     // [1, 2, 4, 7, 8, 9, 10, 11]
    violations: string[];         // ["F7_HUMILITY: GODELLOCK_DETECTED"]
    W_cube: number;               // Tri-witness consensus score
  };
  
  // ═══════════════════════════════════════
  // RECOVERY PROTOCOL (For SABAR/VOID)
  // ═══════════════════════════════════════
  recovery?: {
    sabar_step: number | null;    // Current SABAR retry count
    max_retries: number;          // Maximum allowed retries
    next_action: ActionCode;      // retry | escalate | terminate
    state_transition: StateCode;  // Target state after recovery
  };
}

// ═══════════════════════════════════════
// ENUMERATIONS
// ═══════════════════════════════════════

type VerdictCode = 
  | "SEAL"      // ✅ Constitutional approval
  | "SABAR"     // ⏸️  Requires retry/recovery (see recovery protocol)
  | "VOID"      // ❌ Constitutional rejection
  | "PARTIAL";  // ⚠️  Approved with constraints/warnings

type StatusCode = 
  | "SUCCESS"
  | "PENDING"
  | "REJECTED"
  | "DEGRADED"
  | "ERROR"
  | "TIMEOUT"
  | "UNAUTHORIZED"
  | "CONSTRAINT_VIOLATION";

type StageCode = 
  | "000_INIT"     // Identity anchor
  | "111_SENSE"    // Evidence acquisition
  | "333_MIND"     // Reasoning synthesis
  | "444_ROUTER"   // Decision routing
  | "555_HEART"    // Safety critique
  | "666_MEMORY"   // Vector operations
  | "777_ENGINE"   // Code execution
  | "888_FORGE"    // Creation/composition
  | "999_VAULT";   // Permanent record

type AuthorityLevel = 
  | "sovereign"    // 888_JUDGE
  | "delegated"    // Agent with valid session
  | "anonymous";   // Unauthenticated

type AuthState = 
  | "verified"     // Signature validated
  | "pending"      // Awaiting verification
  | "unverified";  // No auth provided

type ActionCode = 
  | "retry"        // Attempt operation again
  | "escalate"     // Request human approval
  | "terminate"    // End session safely
  | "degrade";     // Continue with reduced capability

type StateCode = 
  | "OPERATIONAL"
  | "DEGRADED"
  | "SAFE_MODE"
  | "TERMINATED";

interface VerdictError {
  code: ErrorCode;
  message: string;
  floor?: string;           // F1-F13 constraint violated
  recoverable: boolean;     // Can this be retried?
  details?: Record<string, unknown>;
}

type ErrorCode =
  // Authentication Errors
  | "VOID_AUTH"              // Invalid credentials
  | "VOID_AUTH_EXPIRED"      // Session expired
  | "VOID_AUTH_SCOPE"        // Insufficient permissions
  // Entropy Errors
  | "VOID_ENTROPY"           // ΔS > 0 (clarity violation)
  | "VOID_ENTROPY_BUDGET"    // Session budget exhausted
  // Constitutional Errors
  | "VOID_CONSTITUTION"      // Generic F1-F13 violation
  | "VOID_HUMILITY"          // Ω₀ outside [0.03, 0.05]
  | "VOID_PEACE"             // Destruction detected
  | "VOID_TRUTH"             // F2 accuracy violation
  | "VOID_ETHICS"            // C_dark ≥ 0.30
  // System Errors
  | "VOID_SYSTEM"            // Internal failure
  | "VOID_TIMEOUT"           // Operation timed out
  | "VOID_DEPENDENCY";       // External service failure
```

---

## 🔢 VERDICT CODE SEMANTICS

### SEAL ✅
**Meaning:** Full constitutional approval. Operation may proceed.

**Requirements:**
- All F1-F13 constraints satisfied
- W³ ≥ 0.95
- Ω₀ ∈ [0.03, 0.05]
- ΔS ≤ 0

**Response:**
```json
{
  "ok": true,
  "verdict": "SEAL",
  "status": "SUCCESS",
  "metrics": { "delta_s": -0.2, "confidence": 0.04, "coherence": 0.95 }
}
```

### SABAR ⏸️
**Meaning:** Operation requires retry or recovery. Not a failure—an invitation to persist.

**Trigger Conditions:**
- Temporary constraint violation (recoverable)
- Resource unavailable (retry possible)
- Ambiguity detected (clarification needed)

**Recovery Protocol:**
```json
{
  "ok": false,
  "verdict": "SABAR",
  "status": "PENDING",
  "recovery": {
    "sabar_step": 1,
    "max_retries": 3,
    "next_action": "retry",
    "state_transition": "OPERATIONAL"
  }
}
```

**SABAR Loop Rules:**
1. Max 3 retries per operation (configurable)
2. Escalate to human after 3rd SABAR
3. Each retry must change approach (no identical retries)
4. Log all SABAR steps for audit

### VOID ❌
**Meaning:** Constitutional rejection. Operation MUST NOT proceed.

**Categories:**
- **VOID_AUTH:** Authentication/authorization failure
- **VOID_ENTROPY:** Clarity degradation (ΔS > 0)
- **VOID_CONSTITUTION:** F1-F13 violation
- **VOID_SYSTEM:** Internal system failure

**Response:**
```json
{
  "ok": false,
  "verdict": "VOID",
  "status": "REJECTED",
  "errors": [{
    "code": "VOID_HUMILITY",
    "message": "Ω₀ = 0.015 < 0.03 (Godellock detected)",
    "floor": "F7_HUMILITY",
    "recoverable": false
  }]
}
```

### PARTIAL ⚠️
**Meaning:** Operation approved with constraints or warnings.

**Use Cases:**
- Degraded mode operation
- Partial data retrieval
- Approximate results with confidence bounds

**Response:**
```json
{
  "ok": true,
  "verdict": "PARTIAL",
  "status": "DEGRADED",
  "payload": { /* partial results */ },
  "warnings": ["Using cached data (stale > 1 hour)"]
}
```

---

## 🧪 VALIDATION EXAMPLES

### Example 1: Successful init_anchor
```json
{
  "ok": true,
  "verdict": "SEAL",
  "status": "SUCCESS",
  "tool": "init_anchor",
  "stage": "000_INIT",
  "schema_version": "1.0.0",
  "timestamp": "2026-03-30T20:44:17Z",
  "metrics": {
    "delta_s": 0.0,
    "confidence": 0.05,
    "coherence": 1.0,
    "peace2": 1.0
  },
  "authority": {
    "actor_id": "888_JUDGE",
    "level": "sovereign",
    "auth_state": "verified",
    "human_required": false
  },
  "payload": {
    "session_id": "sess_abc123",
    "entropy_budget": 0.5,
    "sabar_remaining": 3
  },
  "trace": {
    "session_id": "sess_abc123",
    "request_id": "req_xyz789",
    "integrity_hash": "sha256:abc..."
  },
  "constitutional_context": {
    "floors_checked": [1, 2, 7, 11],
    "violations": [],
    "W_cube": 1.0
  }
}
```

### Example 2: SABAR on resource unavailable
```json
{
  "ok": false,
  "verdict": "SABAR",
  "status": "PENDING",
  "tool": "engineering_memory",
  "stage": "666_MEMORY",
  "metrics": {
    "delta_s": 0.0,
    "confidence": 0.05,
    "coherence": 0.9
  },
  "errors": [{
    "code": "VOID_DEPENDENCY",
    "message": "Vector store temporarily unavailable",
    "recoverable": true
  }],
  "recovery": {
    "sabar_step": 1,
    "max_retries": 3,
    "next_action": "retry",
    "state_transition": "OPERATIONAL"
  }
}
```

### Example 3: VOID on humility violation
```json
{
  "ok": false,
  "verdict": "VOID",
  "status": "REJECTED",
  "tool": "agi_mind",
  "stage": "333_MIND",
  "metrics": {
    "delta_s": 0.1,
    "confidence": 0.01,
    "coherence": 0.3
  },
  "errors": [{
    "code": "VOID_HUMILITY",
    "message": "Ω₀ = 0.01 < 0.03 (Godellock threshold)",
    "floor": "F7_HUMILITY",
    "recoverable": false,
    "details": { "omega": 0.01, "threshold_min": 0.03 }
  }],
  "constitutional_context": {
    "floors_checked": [2, 4, 7, 8],
    "violations": ["F7_HUMILITY: GODELLOCK_DETECTED"],
    "W_cube": 0.0
  }
}
```

---

## 🔐 INTEGRITY HASH

For F11 (Auditability), all verdicts MUST include an integrity hash:

```python
def compute_integrity_hash(verdict: dict) -> str:
    """
    Compute SHA-256 hash of critical fields.
    Includes: ok, verdict, status, tool, stage, metrics, authority
    """
    canonical = json.dumps({
        "ok": verdict["ok"],
        "verdict": verdict["verdict"],
        "status": verdict["status"],
        "tool": verdict["tool"],
        "stage": verdict["stage"],
        "metrics": verdict["metrics"],
        "authority": verdict["authority"],
        "timestamp": verdict["timestamp"]
    }, sort_keys=True)
    
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()[:16]}"
```

---

## 📋 COMPLIANCE CHECKLIST

For tool implementers:

- [ ] Return `ok` (boolean) — operation success indicator
- [ ] Return `verdict` — one of SEAL|SABAR|VOID|PARTIAL
- [ ] Return `status` — detailed status string
- [ ] Return `tool` — canonical tool name
- [ ] Return `stage` — 000-999 pipeline stage
- [ ] Return `schema_version` — "1.0.0"
- [ ] Return `timestamp` — ISO 8601 UTC
- [ ] Return `metrics` with delta_s, confidence, coherence, peace2
- [ ] Return `authority` with actor_id, level, auth_state, human_required
- [ ] Return `trace` with session_id, request_id
- [ ] Return `constitutional_context` with floors_checked, violations, W_cube
- [ ] Include `errors` array when ok=false
- [ ] Include `recovery` object for SABAR verdicts
- [ ] Compute and include `integrity_hash`

---

## 🔄 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-30 | Initial specification |

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🔐
