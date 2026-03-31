# AUTH PROTOCOL SPECIFICATION
> **Authority:** 888_JUDGE  
> **Version:** v1.0.0-SEAL  
> **Status:** CONSTITUTIONAL MANDATE  
> **Band:** 000_KERNEL (F11 Auth)

---

## 🎯 PURPOSE

Define the authentication and authorization schema for ALL arifOS tool interactions. Ensures cryptographically verifiable identity, session-bound access control, and tamper-evident audit trails.

**F11 (Auditability):** All actions must be attributable.  
**F1 (Amanah):** Compromised sessions must be revocable.

---

## 📐 AUTH_CONTEXT SCHEMA

Every tool invocation MUST include an `auth_context` object:

```typescript
interface AuthContext {
  // ═══════════════════════════════════════
  // SESSION IDENTITY (Required)
  // ═══════════════════════════════════════
  session_id: string;           // UUID v4, generated at init_anchor
  session_type: SessionType;    // interactive | batch | cron | delegate
  
  // ═══════════════════════════════════════
  // ACTOR IDENTITY (Required)
  // ═══════════════════════════════════════
  actor_id: string;             // 888_JUDGE | <agent_id> | anonymous
  actor_type: ActorType;        // sovereign | agent | service | user
  
  // ═══════════════════════════════════════
  // AUTHENTICATION PROOF (Required)
  // ═══════════════════════════════════════
  proof: {
    type: ProofType;            // session_token | hmac | api_key | jwt
    value: string;              // The actual proof (token/signature)
    issued_at: string;          // ISO 8601 timestamp
    expires_at: string;         // ISO 8601 timestamp
  };
  
  // ═══════════════════════════════════════
  // AUTHORIZATION SCOPE (Required)
  // ═══════════════════════════════════════
  scope: {
    tools: string[];            // ["*"] or ["init_anchor", "agi_mind", ...]
    risk_tiers: RiskTier[];     // ["low", "medium", "high"]
    modes: ModePermission[];    // ["read", "write", "execute", "forge"]
  };
  
  // ═══════════════════════════════════════
  // CHAIN OF CUSTODY (Required)
  // ═══════════════════════════════════════
  chain: {
    parent_session?: string;    // Parent session ID (for delegation)
    delegated_by?: string;      // Actor that delegated this session
    delegation_depth: number;   // 0 for root, max 3
  };
  
  // ═══════════════════════════════════════
  // ATTESTATION (Required for HIGH_RISK)
  // ═══════════════════════════════════════
  attestation?: {
    human_approved: boolean;    // Was this pre-approved by human?
    approval_token?: string;    // Reference to approval record
    approval_timestamp?: string;
  };
}

// ═══════════════════════════════════════
// ENUMERATIONS
// ═══════════════════════════════════════

type SessionType = 
  | "interactive"   // Human-in-the-loop session
  | "batch"         // Automated batch processing
  | "cron"          // Scheduled task
  | "delegate"      // Sub-agent delegation
  | "recovery";     // Emergency recovery mode

type ActorType = 
  | "sovereign"     // 888_JUDGE - unlimited authority
  | "agent"         // Autonomous agent with delegated scope
  | "service"       // Internal service component
  | "user"          // Human user (via CLI/UI)
  | "anonymous";    // Unauthenticated (limited access)

type ProofType = 
  | "session_token" // Short-lived opaque token
  | "hmac"          // HMAC-SHA256 signature
  | "jwt"           // JSON Web Token
  | "api_key"       // Long-lived API key (cron/services only)
  | "mcp_sig";      // MCP server native signature

type RiskTier = "low" | "medium" | "high" | "critical";

type ModePermission = "read" | "write" | "execute" | "forge" | "delete";
```

---

## 🔐 SESSION TOKEN SPECIFICATION

### Token Structure (Opaque)

```
aris_<base64url-encoded-payload>.<signature>
```

**Example:**
```
aris_eyJzaWQiOiJhYmMtMTIzIiwiYWlkIjoiODg4X0pVREdFIn0.signature_here
```

### Payload (Decoded)

```typescript
interface SessionTokenPayload {
  sid: string;          // Session ID (short form)
  aid: string;          // Actor ID
  iat: number;          // Issued at (Unix timestamp)
  exp: number;          // Expires at (Unix timestamp)
  scp: string[];        // Scope (tool permissions)
  rtl: string[];        // Risk tiers allowed
  ver: string;          // Token version
}
```

### Token Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│  TOKEN LIFECYCLE                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. ISSUANCE (init_anchor)                               │
│     └─> 888_JUDGE or authorized agent calls init        │
│     └─> Server generates session_id + token             │
│     └─> Token stored in session_governance.db           │
│                                                          │
│  2. VALIDATION (tool invocation)                         │
│     └─> Tool extracts token from auth_context           │
│     └─> Server validates signature + expiry             │
│     └─> Server checks scope against requested tool      │
│                                                          │
│  3. REFRESH (optional)                                   │
│     └─> Valid refresh_token + session_id required       │
│     └─> New token issued, old token revoked             │
│     └─> Max refresh: 10 times per session               │
│                                                          │
│  4. REVOCATION                                           │
│     └─> Explicit: vault_ledger(mode="revoke")           │
│     └─> Implicit: Session expiry, max retries exceeded  │
│     └─> Emergency: 888_JUDGE kill-switch                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🛡️ VERIFICATION ALGORITHM

### Step-by-Step Validation

```python
async def verify_auth_context(auth_context: dict, requested_tool: str) -> AuthResult:
    """
    Verify authentication and authorization for tool invocation.
    Returns AuthResult or raises AuthError.
    """
    
    # ─────────────────────────────────────
    # 1. STRUCTURE VALIDATION
    # ─────────────────────────────────────
    required_fields = ['session_id', 'actor_id', 'proof', 'scope']
    for field in required_fields:
        if field not in auth_context:
            raise AuthError(f"VOID_AUTH: Missing {field}", code="VOID_AUTH_MALFORMED")
    
    # ─────────────────────────────────────
    # 2. TOKEN EXTRACTION
    # ─────────────────────────────────────
    proof = auth_context['proof']
    if proof['type'] not in ['session_token', 'hmac', 'jwt', 'api_key', 'mcp_sig']:
        raise AuthError("VOID_AUTH: Unknown proof type", code="VOID_AUTH_TYPE")
    
    token = proof['value']
    
    # ─────────────────────────────────────
    # 3. SIGNATURE VERIFICATION
    # ─────────────────────────────────────
    if proof['type'] == 'session_token':
        payload, signature = token.split('.')
        expected_sig = hmac_sha256(payload, SECRET_KEY)
        if not constant_time_compare(signature, expected_sig):
            raise AuthError("VOID_AUTH: Invalid signature", code="VOID_AUTH_SIGNATURE")
    
    # ─────────────────────────────────────
    # 4. EXPIRATION CHECK
    # ─────────────────────────────────────
    now = datetime.utcnow()
    exp = datetime.fromisoformat(proof['expires_at'])
    if now > exp:
        raise AuthError("VOID_AUTH: Token expired", code="VOID_AUTH_EXPIRED")
    
    # ─────────────────────────────────────
    # 5. SESSION LOOKUP
    # ─────────────────────────────────────
    session = await session_store.get(auth_context['session_id'])
    if not session:
        raise AuthError("VOID_AUTH: Unknown session", code="VOID_AUTH_SESSION")
    
    if session['status'] == 'revoked':
        raise AuthError("VOID_AUTH: Session revoked", code="VOID_AUTH_REVOKED")
    
    # ─────────────────────────────────────
    # 6. SCOPE VALIDATION
    # ─────────────────────────────────────
    scope = auth_context['scope']
    
    # Check tool permission
    if '*' not in scope['tools'] and requested_tool not in scope['tools']:
        raise AuthError(
            f"VOID_AUTH_SCOPE: {requested_tool} not in scope", 
            code="VOID_AUTH_SCOPE"
        )
    
    # Check delegation depth
    chain = auth_context.get('chain', {})
    if chain.get('delegation_depth', 0) > 3:
        raise AuthError("VOID_AUTH: Max delegation depth exceeded", code="VOID_AUTH_DELEGATION")
    
    # ─────────────────────────────────────
    # 7. ATTESTATION CHECK (HIGH_RISK only)
    # ─────────────────────────────────────
    tool_risk = get_tool_risk_tier(requested_tool)
    if tool_risk in ['high', 'critical']:
        attestation = auth_context.get('attestation', {})
        if not attestation.get('human_approved', False):
            raise AuthError(
                "VOID_AUTH: Human approval required", 
                code="VOID_AUTH_ATTESTATION"
            )
    
    # ─────────────────────────────────────
    # 8. AUDIT LOG
    # ─────────────────────────────────────
    await audit_log.record({
        'event': 'AUTH_SUCCESS',
        'session_id': auth_context['session_id'],
        'actor_id': auth_context['actor_id'],
        'tool': requested_tool,
        'timestamp': now.isoformat()
    })
    
    return AuthResult(
        session_id=auth_context['session_id'],
        actor_id=auth_context['actor_id'],
        authorized=True,
        scope=scope
    )
```

---

## 👤 ACTOR HIERARCHY

```
┌─────────────────────────────────────────────────────────┐
│  ACTOR HIERARCHY                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  L0: 888_JUDGE (Sovereign)                              │
│  ├── Scope: [*] (all tools, all tiers)                  │
│  ├── Can: Override any verdict, revoke any session      │
│  ├── Cannot: Be auto-generated (requires manual auth)   │
│  └── Proof: HMAC with master key                        │
│                                                          │
│  L1: A-ARCHITECT (Delegated Sovereign)                  │
│  ├── Scope: [init_anchor, agi_mind, engineering_memory] │
│  ├── Can: Spawn sub-sessions, approve medium-risk       │
│  ├── Cannot: Approve critical without 888               │
│  └── Proof: Session token with delegation chain         │
│                                                          │
│  L2: A-ENGINEER (Specialized Agent)                     │
│  ├── Scope: [code_engine, agentzero_engineer]           │
│  ├── Can: Execute code, modify files (reversible)       │
│  ├── Cannot: Access vault_ledger, init_anchor           │
│  └── Proof: Session token (depth=1)                     │
│                                                          │
│  L3: A-VALIDATOR (Read-Only Observer)                   │
│  ├── Scope: [math_estimator, physics_reality]           │
│  ├── Can: Query, analyze, report                        │
│  ├── Cannot: Modify state, execute code                 │
│  └── Proof: Session token (depth=0-2)                   │
│                                                          │
│  L4: Service (Cron/Batch)                               │
│  ├── Scope: Configured per workflow                     │
│  ├── Can: Automated operations within bounds            │
│  ├── Cannot: Exceed pre-configured risk limits          │
│  └── Proof: API key + IP whitelist                      │
│                                                          │
│  L5: Anonymous (Unauthenticated)                        │
│  ├── Scope: [physics_reality mode=status]               │
│  ├── Can: Read public status only                       │
│  ├── Cannot: Any state modification                     │
│  └── Proof: None                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔑 KEY MANAGEMENT

### Secret Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│  KEY HIERARCHY                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MASTER_KEY (888_JUDGE only)                            │
│  ├── Used for: Sovereign session issuance               │
│  ├── Storage: Hardware security module (HSM)            │
│  └── Rotation: Never (destructive)                      │
│                                                          │
│  SESSION_SIGNING_KEY                                    │
│  ├── Used for: Token signatures                         │
│  ├── Storage: Vault (encrypted at rest)                 │
│  └── Rotation: Quarterly, with 30-day overlap           │
│                                                          │
│  API_KEYS (Services only)                               │
│  ├── Used for: Cron jobs, external integrations         │
│  ├── Storage: Environment variables (Docker secrets)    │
│  └── Rotation: Monthly                                  │
│                                                          │
│  DELEGATION_KEYS (Agent-to-Agent)                       │
│  ├── Used for: Sub-session authorization                │
│  ├── Storage: Session-bound (ephemeral)                 │
│  └── Rotation: Per-session                              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚨 REVOCATION PROTOCOL

### Emergency Revocation

```python
async def revoke_session(session_id: str, reason: str, actor_id: str):
    """
    Emergency session revocation (888_JUDGE only).
    F1 (Amanah): All revocations are reversible within 24h.
    """
    
    # Verify actor is sovereign
    if actor_id != "888_JUDGE":
        raise AuthError("VOID_AUTH: Revocation requires sovereign authority")
    
    # Soft revoke (24h grace period)
    await session_store.update(session_id, {
        'status': 'revoked',
        'revoked_at': datetime.utcnow().isoformat(),
        'revoked_by': actor_id,
        'revocation_reason': reason,
        'grace_expires': (datetime.utcnow() + timedelta(hours=24)).isoformat()
    })
    
    # Broadcast revocation to all nodes
    await event_bus.publish('session.revoked', {
        'session_id': session_id,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Log to vault
    await vault_ledger({
        'mode': 'seal',
        'evidence': f"Session {session_id} revoked: {reason}",
        'actor_id': actor_id
    })
```

---

## 📋 COMPLIANCE CHECKLIST

For tool implementers:

- [ ] Accept `auth_context` as first parameter
- [ ] Validate auth_context structure before processing
- [ ] Verify token signature using constant-time comparison
- [ ] Check token expiration
- [ ] Validate scope against requested operation
- [ ] Check delegation depth (max 3)
- [ ] Require attestation for HIGH_RISK operations
- [ ] Log all auth events to audit trail
- [ ] Return VOID_AUTH error with specific code on failure
- [ ] Support session revocation broadcast

---

## 🔄 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-30 | Initial specification |

---

*Ditempa Bukan Diberi* [ΔΩΨ|888] 🔐
