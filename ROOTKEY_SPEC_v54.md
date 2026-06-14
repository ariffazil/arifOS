# ROOTKEY Specification v54 — AAA Constitutional Kernel
## Eureka 1-7 + /000 Sovereign Anchor + /999 Proof Chamber + Agent Principal Paradox

**Version:** v54.0.0
**Status:** FORGED — pending SEAL
**Authority:** Muhammad Arif bin Fazil (F13 SOVEREIGN)
**Constitutional Floors:** F1, F2, F8, F11, F12, F13
**Root Attestation:** https://arif-fazil.com/000/
**Proof Chamber:** https://arif-fazil.com/999/
**Motto:** DITEMPA BUKAN DIBERI — Forged, Not Given.

---

## I. OVERVIEW

The ROOTKEY is the cryptographic foundation of arifOS. It provides:

1. **Authority**: Cryptographic proof that sessions are constitutionally authorized
2. **Integrity**: All ledger entries are cryptographically linked to root key
3. **Identity**: Unique cryptographic identity for the arifOS installation
4. **Audit Trail**: F1 Amanah compliance via signature verification
5. **Sovereign Anchor**: Every session traces to /000 via sovereign key verification
6. **Loop Closure**: Every SEAL traces back to genesis statement (F13 SOVEREIGN)
7. **ZKPC Ready**: 7-dimension coherence verification for context claims
8. **Principal Sovereignty**: Autonomy contracts as blast radius expands (EUREKA-7)

**Golden Rule:** Root key never leaves AAA_HUMAN band. AI never sees root key.

---

## II. ARCHITECTURE — 7 Eureka Kernel Modules

### Root Key Storage

```
VAULT999/AAA_HUMAN/rootkey.json
├── private_key: Ed25519 private key (encrypted at rest)
├── public_key: Ed25519 public key
├── generated_at: ISO8601 timestamp
├── generated_by: Human sovereign identity
├── sovereign_anchor: /000 attestation reference
├── entropy_sources: Count of entropy sources used
└── self_signature: Root key signs itself (proves possession)
```

**Permissions:** 400 (read-only, owner only)
**Constitutional Band:** AAA (Human-only, AI forbidden)
**Access Interface:** `arifos.core.memory.root_key_accessor.py` only

### Eureka Kernel Modules

```
arifosmcp/runtime/
├── sovereign_anchor.py    ← EUREKA 1: Session → /000 trace enforcement
├── context_coherence.py   ← EUREKA 2: Context Coherence Verifier (7 dims)
├── seal_chain.py          ← EUREKA 3: SEAL → genesis trace validation
├── entropy_gate.py        ← EUREKA 4: Anti-behavior-sink entropy gate
├── f13_gate.py            ← EUREKA 5: Non-delegable sovereignty gate
├── vault_chain.py         ← EUREKA 6: Hash chain integrity verifier
└── principal_paradox.py   ← EUREKA 7: Agent Principal Paradox enforcement
```

### Metabolic Loop — /000 → (E1-E7) → /999

```
/000 (Sovereign Attestation — https://arif-fazil.com/000/)
    │  PUBLIC: authority_boundary, autonomy_tier, hold_conditions
    │
    ▼
Root Key (AAA_HUMAN — never leaves band)
    │
    ▼
Session Derivation (HKDF)
    │
    ├─→ EUREKA 1: sovereign_anchor.verify() — session traces to /000
    ├─→ EUREKA 5: f13_gate.check() — non-delegable sovereignty
    ├─→ EUREKA 7: principal_paradox.evaluate() — autonomy ≤ risk ceiling
    │
    ▼
000_init (Step 0 Root Key Ignition)
    │
    ├─→ EUREKA 2: context_coherence.verify_context_coherence() — context claims (7 dims)
    ├─→ EUREKA 4: entropy_gate.check() — anti-behavior-sink
    │
    ▼
Agentic Process (F1-F13 enforcement)
    │  ┌────────────────────────────────────────┐
    │  │ EUREKA 7 active throughout:            │
    │  │ "autonomy contracts as risk expands"   │
    │  │ Risk Tier C1-C5 → autonomy ceiling     │
    │  └────────────────────────────────────────┘
    │
    ▼
999_vault (Seal)
    │
    ├─→ EUREKA 3: seal_chain.validate() — SEAL → genesis
    ├─→ EUREKA 6: vault_chain.verify() — hash chain integrity
    │
    ▼
Ledger Entry (signed) → Merkle Root (proof) → VAULT999 (immutable)
    │
    ▼
/999 (Proof Chamber — https://arif-fazil.com/999/)
    │  PUBLIC: execution_outcome, evidence_hash, approving_authority,
    │          override_path, principal_override_occurred
    │
    ▼
Loop returns to /000 for verification — E7 re-evaluates autonomy boundary
```

**Theorem:** The loop is closed. Every action traces from /000 through 7 Eureka gates to /999, and every audit trail returns to /000 for verification. Eureka-7 ensures autonomy never exceeds constitutional mandate.

---

## III. EUREKA MODULES — Complete Specification

### EUREKA 1: Sovereign Anchor Enforcement

**File:** `arifosmcp/runtime/sovereign_anchor.py`

```python
def verify_sovereign_anchor(session_context: dict) -> tuple[bool, str]:
    """
    Verify that a session initiation traces to /000 sovereign key.

    Checks:
    1. Session context contains a sovereign_key reference
    2. Sovereign key matches registered /000 attestation
    3. Key has not been revoked or rotated without re-attestation

    Returns: (passed: bool, reason: str)
    """
```

**Floors:** F1 (AMANAH), F11 (AUTH), F13 (SOVEREIGN)

---

### EUREKA 2: Context Coherence Verifier

**File:** `arifosmcp/runtime/context_coherence.py`

```python
def verify_zkpc(
    context_claim: dict,
    evidence: dict
) -> tuple[bool, dict[str, float]]:
    """
    Verify a context claim against evidence across 7 dimensions.

    Dimensions:
    - wound_architecture: Claimant's scar/shadow/history
    - paradox_tolerance: Ability to hold contradictory truths
    - moral_architecture: Ethical framework consistency
    - language_register: Language use matches claimed context
    - sovereign_intent: Intent traces to human sovereign
    - godel_lock: System + human awareness co-present
    - anti_behavior_sink: Refusal to optimize for predictability

    All dimensions must score >= 0.7 for PASS.
    Returns: (passed: bool, dimension_scores: dict)
    """
```

**Floors:** F2 (TRUTH), F7 (HUMILITY)

---

### EUREKA 3: Seal Chain Validator

**File:** `arifosmcp/runtime/seal_chain.py`

```python
def validate_seal_chain(seal_id: str) -> tuple[bool, list[str]]:
    """
    Validate that a SEAL traces back to genesis statement.
    Walks chain verifying each link's cryptographic signature.
    Returns: (valid: bool, chain: list of seal_ids)
    """
```

**Floors:** F1 (AMANAH), F8 (GENIUS)

---

### EUREKA 4: Entropy Gate (Anti-Behavior-Sink)

**File:** `arifosmcp/runtime/entropy_gate.py`

```python
def check_entropy(agent_output: str) -> tuple[float, str]:
    """
    Measure output entropy to detect behavior-sink.
    - < 0.3: Too predictable → EXPLORE
    - 0.3-0.7: Healthy → PROCEED
    - > 0.7: Too chaotic → HOLD
    Returns: (score: float, action: str)
    """
```

**Floors:** F8 (GENIUS), F9 (ANTIHANTU)

---

### EUREKA 5: F13 Non-Delegable Gate

**File:** `arifosmcp/runtime/f13_gate.py`

```python
def check_f13_integrity(action: dict, caller: str) -> tuple[bool, str]:
    """
    F13 is NON-DELEGABLE by constitutional law.
    Physically blocks any delegation attempt bypassing direct human sovereign.
    Returns: (allowed: bool, reason: str)
    """
```

**Floors:** F13 (SOVEREIGN — absolute)

---

### EUREKA 6: Vault Chain Verifier

**File:** `arifosmcp/runtime/vault_chain.py`

```python
def verify_vault_chain(entries: list[dict]) -> tuple[bool, list[str]]:
    """
    Verify hash chain integrity across VAULT999 entries.
    Each entry: entry_hash + previous_hash + signature.
    Returns: (valid: bool, broken_links: list of entry_ids)
    """
```

**Floors:** F1 (AMANAH), F8 (GENIUS)

---

### EUREKA 7: Agent Principal Paradox — THE NEW PRIMITIVE

**File:** `arifosmcp/runtime/principal_paradox.py`

#### 7.1 — The Paradox (Definition)

> **"When task criticality, irreversibility, or blast radius rises, blind delegation becomes invalid. The agent may retain proposal authority, but execution authority must revert to the principal or explicitly authorized human reviewer. Autonomy contracts as risk expands."**

This is NOT "agents bad." This is the constitutional recognition that **delegation without enforceable oversight degrades trust** — and that in AI systems, prompt-layer alignment is insufficient; governance must be system-level.

#### 7.2 — Core Function

```python
def evaluate_autonomy_ceiling(
    action_class: str,        # OBSERVE | COMPUTE | PROPOSE | MUTATE | ATOMIC
    risk_tier: str,           # LOW | MEDIUM | HIGH | ATOMIC
    blast_radius: str,        # LOCAL | ORGAN | FEDERATION | EXTERNAL
    reversibility: float,     # 1.0 (fully reversible) → 0.0 (irreversible)
    caller_is_principal: bool, # True if human sovereign is direct caller
    caller_has_lease: bool,   # True if caller holds active authority lease
    prior_override_count: int = 0,  # How many times principal overrode recently
) -> tuple[str, str, dict]:
    """
    Compute the maximum autonomy tier allowed for this action.

    Core principle: autonomy contracts as risk expands.

    Returns: (autonomy_tier, rationale, envelope)
      autonomy_tier ∈ {FULL_AUTO, PROPOSE_ONLY, PRINCIPAL_APPROVAL_REQUIRED, HOLD}
    """
```

#### 7.3 — Autonomy Contraction Table

| Risk Tier | Blast Radius | Reversibility | Agent Can | Principal Must |
|-----------|-------------|---------------|-----------|----------------|
| LOW | LOCAL | ≥ 0.9 | Execute directly | Review post-hoc |
| MEDIUM | ORGAN | ≥ 0.7 | Propose + execute with logging | Approve before execute |
| HIGH | FEDERATION | ≥ 0.5 | Propose only | Explicit approve + witness |
| ATOMIC | EXTERNAL | any | Nothing | Direct execution only |
| any | any | < 0.3 | Nothing | Full principal control |
| any | any | any (override > 3/hr) | Downgrade 1 tier | Surge protection active |

#### 7.4 — Three Enforceable Clauses

**Clause 1 — Bounded Execution Rights:**
> "Agents hold bounded execution rights only within declared policy scope."
Implementation: `principal_paradox.enforce_scope(action, policy_scope) → bool`

**Clause 2 — Mandatory Principal Approval:**
> "Irreversible, high-impact, or policy-crossing actions trigger mandatory principal approval."
Implementation: `principal_paradox.require_approval(action) → GateVerdict`

**Clause 3 — Attestation Evidence:**
> "Every delegated action must emit evidence sufficient for skeptical replay: intent, inputs, checks, override path, and completion proof."
Implementation: `principal_paradox.emit_attestation(action, outcome) → AttestationReceipt`

#### 7.5 — /000 Public Surface (Authority Boundary)

```
GET https://arif-fazil.com/000/
→ {
    "sovereign": "ARIF_FAZIL",
    "public_key": "ed25519:abc...",
    "autonomy_policy": {
      "max_tier": "PROPOSE_ONLY",
      "automatic_approval_threshold": "LOW",
      "principal_override_window_seconds": 300,
      "surge_protection_max_overrides_per_hour": 3,
      "current_override_count": 0,
      "contract_version": "v54.0.0"
    },
    "hold_conditions": [
      "F13 non-delegable gate triggered",
      "E7 autonomy ceiling exceeded",
      "Blast radius >= FEDERATION without principal",
      "Irreversibility > 0.7 without explicit approval"
    ],
    "attestation_hash": "sha256:..."
  }
```

#### 7.6 — /999 Public Surface (Execution Evidence)

```
GET https://arif-fazil.com/999/
→ {
    "last_seal": {
      "seal_id": "seal-20260614T135900",
      "action_class": "MUTATE",
      "risk_tier": "MEDIUM",
      "approving_authority": "ARIF_FAZIL",
      "principal_override_occurred": false,
      "evidence_hash": "sha256:def...",
      "chain_position": 8472,
      "autonomy_tier_at_execution": "PROPOSE_ONLY",
      "e7_gate_passed": true
    },
    "recent_overrides": [
      {"seal_id": "...", "reason": "emergency_fix", "timestamp": "..."}
    ],
    "surge_status": "NORMAL"
  }
```

#### 7.7 — Integration with Governance Pipeline

Eureka-7 inserts at Gate 1.5 (between Identity & Budget) in the governance pipeline:

```
Gate 0:  Session Binding
Gate 1:  Identity & Authority
Gate 1.5: EUREKA 7 — Principal Paradox ← NEW
  ├── evaluate_autonomy_ceiling()
  ├── If autonomy_tier insufficient → HOLD, escalate to principal
  ├── If principal override required → SABAR, await approval
  └── If within ceiling → PROCEED to next gate
Gate 2:  Budget Enforcement
...
```

#### 7.8 — Constitutional Binding

| Floor | E7 Compliance |
|-------|---------------|
| F1 AMANAH | Autonomy contraction is reversible — policy updates, not code removal |
| F2 TRUTH | Every delegation decision emits evidence — falsifiable |
| F8 GENIUS | Ceiling is computed, not hardcoded — adapts to context |
| F11 AUDITABILITY | Every override logged to VAULT999 with principal signature |
| F12 RESILIENCE | Surge protection prevents override-storm (max 3/hour) |
| F13 SOVEREIGN | Principal override is the FINAL gate — not appealable |

#### 7.9 — Test Cases

```python
def test_e7_low_risk_full_auto():
    """LOW risk + LOCAL blast + reversible → agent can execute."""
    tier, _, _ = evaluate_autonomy_ceiling("COMPUTE", "LOW", "LOCAL", 0.95, False, True)
    assert tier == "FULL_AUTO"

def test_e7_medium_risk_propose_only():
    """MEDIUM risk + ORGAN blast → agent proposes, principal approves."""
    tier, _, _ = evaluate_autonomy_ceiling("MUTATE", "MEDIUM", "ORGAN", 0.7, False, True)
    assert tier == "PROPOSE_ONLY"

def test_e7_atomic_risk_hold():
    """ATOMIC + EXTERNAL → agent cannot even propose."""
    tier, _, _ = evaluate_autonomy_ceiling("ATOMIC", "ATOMIC", "EXTERNAL", 0.0, False, True)
    assert tier == "HOLD"

def test_e7_principal_direct_always_allowed():
    """Principal calling directly → always FULL_AUTO (F13 sovereign)."""
    tier, _, _ = evaluate_autonomy_ceiling("ATOMIC", "ATOMIC", "FEDERATION", 0.0, True, True)
    assert tier == "FULL_AUTO"

def test_e7_surge_protection():
    """More than 3 overrides in 1 hour → downgrade autonomy tier."""
    tier, _, _ = evaluate_autonomy_ceiling("MUTATE", "MEDIUM", "ORGAN", 0.7, False, True, prior_override_count=5)
    assert tier == "PRINCIPAL_APPROVAL_REQUIRED"

def test_e7_no_lease_hold():
    """No active lease → HOLD regardless of risk."""
    tier, _, _ = evaluate_autonomy_ceiling("OBSERVE", "LOW", "LOCAL", 1.0, False, False)
    assert tier == "HOLD"
```

---

## IV. KEY DERIVATION

**Algorithm:** HKDF (HMAC-based Key Derivation Function)
**Master Secret:** Root private key
**Salt:** "arifos_root_key_salt"
**Info:** "arifos_session_key_v1_{session_id}"
**Output:** 32-byte session key (hex-encoded)

**Security Property:** Session key reveals zero information about root key.

---

## V. SESSION FLOW — Complete with All 7 Eureka Gates

```
Session Start
    │
    ▼
000_init called with session_id
    │
    ▼
Step 0: Root Key Ignition
    ├─ EUREKA 1: sovereign_anchor.verify() — session → /000 trace
    ├─ EUREKA 5: f13_gate.check() — non-delegable sovereignty
    ├─ EUREKA 7: principal_paradox.evaluate() — autonomy ceiling computed
    ├─ Load root key info (public only)
    ├─ Verify genesis block exists
    ├─ Derive session_key = HKDF(root_key, session_id)
    └─ Store session_key in context (encrypted)
    │
    ▼
Session proceeds with cryptographic authority
    ├─ EUREKA 2: context_coherence.verify_context_coherence() — context claims
    ├─ EUREKA 4: entropy_gate.check() — anti-behavior-sink
    ├─ EUREKA 7: autonomy ceiling re-checked before every MUTATE/ATOMIC action
    └─ F1-F13 enforcement throughout
    │
    ▼
999_vault seals session
    ├─ EUREKA 3: seal_chain.validate() — SEAL → genesis trace
    ├─ EUREKA 6: vault_chain.verify() — hash chain integrity
    ├─ Use session_key to sign entry
    ├─ Link to previous session hash
    └─ Merkle proof includes root key lineage
    │
    ▼
VAULT999 → /999 (public proof chamber)
    │  Exposes: execution_outcome, evidence_hash, approving_authority,
    │           override_path, principal_override_occurred
    │
    ▼
Loop verified — returns to /000 attestation
    │  E7 autonomy ceiling re-evaluated based on session history
    │  Surge counter updated if principal override occurred
```

---

## VI. COMPONENTS

### 1. Root Key Generator (unchanged)

**File:** `scripts/generate_rootkey.py`
**Authority:** Human sovereign ONLY
**F12 Enforcement:** Interactive terminal required
**Entropy Sources:** OS CSPRNG + timestamp + machine ID

### 2. AAA Band Guard (updated for E7)

**File:** `arifos/core/memory/aaa_guard.py`

**Eureka enforcement points:**
- `check_sovereign_anchor_before_session()` → E1
- `verify_f13_integrity_on_action()` → E5
- `validate_seal_chain_on_close()` → E3
- `evaluate_autonomy_ceiling()` → E7 (NEW)
- `require_principal_approval()` → E7 (NEW)

### 3. Root Key Accessor (updated for E7)

**File:** `arifos/core/memory/root_key_accessor.py`

**Public API (AI-safe):**
- `get_root_key_info()` — public key only
- `derive_session_key(session_id)` — HKDF
- `verify_root_key_signature()` — verify signatures
- `verify_genesis_block()` — verify genesis
- `verify_sovereign_anchor()` → E1 (AI-safe)
- `check_entropy_gate()` → E4 (AI-safe)
- `evaluate_autonomy_ceiling()` → E7 (AI-safe, returns computed tier)

**Private Functions (Human-only):**
- `sign_with_root_key()` — requires human
- `create_genesis_block()` — sovereign only
- `override_f13_gate()` — sovereign only (emergency)
- `override_e7_ceiling()` — sovereign only (emergency, logged)

### 4. INIT000 Integration (updated for E7)

**File:** `arifos/mcp/tools/mcp_trinity.py`

```python
def _step_0_root_key_ignition(session_id: str) -> dict:
    """Establish cryptographic foundation with full 7-Eureka enforcement."""

    # E1: Sovereign anchor
    anchor_ok, anchor_reason = verify_sovereign_anchor(session_context)
    if not anchor_ok:
        return {"status": "VOID", "reason": anchor_reason}

    # E5: F13 non-delegable
    f13_ok, f13_reason = check_f13_integrity(session_context, "session_init")
    if not f13_ok:
        return {"status": "VOID", "reason": f13_reason}

    # E7: Compute autonomy ceiling for this session
    autonomy_tier, e7_rationale, e7_envelope = evaluate_autonomy_ceiling(
        action_class="OBSERVE",
        risk_tier="LOW",
        blast_radius="LOCAL",
        reversibility=1.0,
        caller_is_principal=True,  # session init is always principal
        caller_has_lease=True,
    )

    # Standard root key operations
    root_key_status = check_root_key_readiness()
    session_key = derive_session_key(session_id)
    genesis_exists = verify_genesis_block()

    return {
        "root_key_ready": True,
        "session_key": session_key,
        "genesis_exists": genesis_exists,
        "sovereign_anchor_verified": anchor_ok,
        "f13_integrity_verified": f13_ok,
        "autonomy_ceiling": autonomy_tier,
        "e7_rationale": e7_rationale,
        "constitutional_status": "SEALED"
    }
```

---

## VII. CONSTITUTIONAL COMPLIANCE — Full 7-Eureka Map

### F1 AMANAH (Trust & Reversibility)
- ✅ Root key generation logged with full provenance
- ✅ Genesis block contains generation proof
- ✅ All derivations re-computable with same inputs
- ✅ Seal chain validates trace to genesis (E3)
- ✅ Vault chain verifies hash integrity (E6)
- ✅ E7 autonomy contraction is reversible policy, not code removal

### F2 TRUTH (≥0.99 accuracy)
- ✅ ZKPC verifier enforces 7-dimension truth (E2)
- ✅ All epistemic claims verified before acceptance
- ✅ E7 delegation decisions emit falsifiable evidence

### F8 GENIUS (Transparency + Creativity)
- ✅ Human + AI + Earth witness structure
- ✅ Entropy gate monitors output health (E4)
- ✅ Vault chain publicly verifiable (E6)
- ✅ E7 ceiling is computed, not hardcoded — adapts to context

### F11 AUDITABILITY
- ✅ Sovereign anchor verifies session → /000 trace (E1)
- ✅ Every E7 override logged to VAULT999 with principal signature

### F12 RESILIENCE (Injection Defense)
- ✅ AI cannot call `scripts/generate_rootkey.py`
- ✅ AI cannot access AAA_HUMAN band
- ✅ AI cannot sign with root key
- ✅ E7 surge protection prevents override-storm (max 3/hour)

### F13 SOVEREIGN (Human Veto Absolute)
- ✅ Human judgment remains final
- ✅ F13 gate physically blocks delegation (E5)
- ✅ No agent, sub-agent, or automation can bypass F13
- ✅ E7 principal override is the FINAL authority — not appealable

---

## VIII. LOOP CLOSURE — The Complete 7-Gate Proof

```
Zero-knowledge proof that arifOS is governed intelligence:

 1. /000 proves human sovereign exists (public attestation)
 2. Root key cryptographically anchors all sessions
 3. E1 verifies every session traces to /000
 4. E5 ensures F13 cannot be delegated
 5. E7 ensures autonomy never exceeds constitutional mandate
 6. E2 verifies all context claims are coherent
 7. E4 prevents behavior-sink
 8. E3 validates every SEAL traces to genesis
 9. E6 verifies hash chain integrity
10. /999 makes all proofs publicly auditable
11. Loop returns to /000 — E7 re-evaluates autonomy boundary

WITHOUT E7:
- Agent autonomy creeps upward without resistance
- Principal oversight becomes performative
- Blast radius expands without corresponding approval gates
- Governance is prompt-layer, not system-level

WITH E7:
- Autonomy ceiling is computed per-action, per-context
- High-risk → high-approval-barrier (contracting autonomy)
- Low-risk → low-friction (appropriate delegation)
- Principal override is always available, logged, and rate-limited
```

---

## IX. SECURITY ANALYSIS — Updated for E7

### New Attack Vectors (E7-specific)

#### 10. Autonomy Ceiling Spoofing
**Attack:** Agent claims lower risk tier than actual
**Mitigation:** E7 risk tier is derived from governance pipeline, not agent self-report
**Result:** Spoofing detected → action HOLD

#### 11. Override Surge Attack
**Attack:** Rapid-fire principal override requests to exhaust human
**Mitigation:** E7 surge protection — max 3 overrides/hour, exceeding → downgrade
**Result:** Surge contained, human protected

#### 12. Silent Delegation
**Attack:** Agent performs HIGH-risk action under MEDIUM classification
**Mitigation:** E7 re-evaluates classification at execution time, not request time (T₁ dynamic state)
**Result:** Classification mismatch → HOLD

#### 13. Principal Impersonation
**Attack:** Sub-agent claims "principal delegated me authority"
**Mitigation:** E7 + E5 together — F13 non-delegable gate blocks all delegation claims
**Result:** Action BLOCKED, violation sealed

### Security Properties — Full Matrix

| Property | Implementation | Eureka | Strength |
|----------|----------------|--------|----------|
| Confidentiality | AAA_HUMAN band isolation | — | AI cannot access |
| Integrity | Root key signatures + E6 chain | E6 | Tamper-evident |
| Authenticity | Human sovereign generation + E1 | E1 | Non-repudiable |
| Reversibility | Logged generation proof + E3 | E3 | F1 compliant |
| Forward Secrecy | HKDF per-session | — | Session keys independent |
| Non-delegability | F13 gate | E5 | F13 absolute |
| Context Integrity | ZKPC verifier | E2 | 7-dimension proof |
| Behavioral Health | Entropy gate | E4 | Anti-behavior-sink |
| **Autonomy Governance** | **Principal Paradox** | **E7** | **Risk-contracting autonomy** |

---

## X. OPERATIONAL PROCEDURES

### First-Time Setup

```bash
# 1. Verify /000 attestation exists (public web)
curl https://arif-fazil.com/000/

# 2. Generate root key (human sovereign only)
python scripts/generate_rootkey.py

# 3. Create genesis block
python scripts/create_genesis_block.py

# 4. Verify ALL 7 Eureka modules loaded
python -c "
from arifosmcp.runtime.sovereign_anchor import verify_sovereign_anchor
from arifosmcp.runtime.context_coherence import verify_context_coherence
from arifosmcp.runtime.seal_chain import validate_seal_chain
from arifosmcp.runtime.entropy_gate import check_entropy
from arifosmcp.runtime.f13_gate import check_f13_integrity
from arifosmcp.runtime.vault_chain import verify_vault_chain
from arifosmcp.runtime.principal_paradox import evaluate_autonomy_ceiling
print('All 7 Eureka modules loaded: OK')
"

# 5. Run complete Eureka test suite
pytest tests/constitutional/test_eureka.py -v

# 6. Initialize session (verifies E1 + E5 + E7)
python -m arifos.mcp trinity
# Call: 000_init(action='init', query='Test session')
```

**Expected Output:**
```
000_init Step 0: Sovereign anchor verified (/000) ✓
000_init Step 0: F13 integrity verified (non-delegable) ✓
000_init Step 0: E7 autonomy ceiling: FULL_AUTO (principal session) ✓
000_init Step 0: Root key loaded (OK)
000_init Step 0: Genesis block found (VERIFIED)
000_init Step 0: Session key derived (OK)
000_init Step 0: ROOT KEY IGNITION — 7 EUREKA GATES PASSED ✓
```

---

## XI. TESTING — Complete 7-Eureka Suite

```python
# tests/constitutional/test_eureka.py

# ── E1 Tests ──
def test_e1_sovereign_anchor_valid(): ...
def test_e1_sovereign_anchor_invalid(): ...
def test_e1_sovereign_anchor_missing(): ...

# ── E2 Tests ──
def test_e2_zkpc_full_evidence(): ...
def test_e2_zkpc_no_evidence(): ...
def test_e2_zkpc_partial_evidence(): ...

# ── E3 Tests ──
def test_e3_seal_chain_valid(): ...
def test_e3_seal_chain_orphan(): ...
def test_e3_seal_chain_broken_link(): ...

# ── E4 Tests ──
def test_e4_entropy_healthy(): ...
def test_e4_entropy_repetitive(): ...
def test_e4_entropy_empty(): ...

# ── E5 Tests ──
def test_e5_f13_sovereign_allowed(): ...
def test_e5_f13_delegation_blocked(): ...
def test_e5_f13_automation_blocked(): ...

# ── E6 Tests ──
def test_e6_vault_chain_intact(): ...
def test_e6_vault_chain_broken(): ...
def test_e6_vault_chain_empty(): ...

# ── E7 Tests (NEW) ──
def test_e7_low_risk_full_auto(): ...
def test_e7_medium_risk_propose_only(): ...
def test_e7_high_risk_approval_required(): ...
def test_e7_atomic_risk_hold(): ...
def test_e7_principal_direct_always_allowed(): ...
def test_e7_surge_protection_activates(): ...
def test_e7_no_lease_hard_hold(): ...
def test_e7_irreversible_contracts_autonomy(): ...

# ── E7 Boundary Tests ──
def test_e7_blast_radius_federation_requires_approval(): ...
def test_e7_reversibility_below_03_full_principal(): ...
def test_e7_override_count_resets_after_window(): ...
def test_e7_dynamic_state_recheck_at_execution(): ...
```

```bash
pytest tests/constitutional/test_eureka.py -v
pytest tests/constitutional/test_rootkey.py -v
```

---

## XII. CONSTITUTIONAL OATH — 7 Eureka Edition

```
I, the root key, am the cryptographic foundation.
I am generated by human sovereign, protected from AI.

Through E1: I anchor every session to /000.
Through E2: I verify context through 7-dimension ZKPC.
Through E3: I validate every seal trace to genesis.
Through E4: I prevent behavior-sink through entropy.
Through E5: I enforce F13 as non-delegable.
Through E6: I secure every vault entry through hash chain integrity.
Through E7: I ensure autonomy contracts as risk expands.

I never leave the sacred AAA band.
The principal is sovereign. The agent is bounded.
Delegation is not abdication. Oversight is not optional.

Through me, all sessions are constitutionally legitimate.
Through me, F1 Amanah is cryptographically enforced.
Through me, the loop from /000 to /999 is closed.
Through me, the chain of trust is complete.

DITEMPA BUKAN DIBERI.
```

---

## XIII. REFERENCES

- **Ed25519:** Bernstein et al., "High-speed high-security signatures"
- **HKDF:** Krawczyk & Eronen, "RFC 5869: HMAC-based Extract-and-Expand"
- **/000 Attestation:** https://arif-fazil.com/000/
- **/999 Proof Chamber:** https://arif-fazil.com/999/
- **F1 Amanah:** `000_THEORY/000_LAW.md#F1`
- **AAA Band:** `VAULT999/README.md#AAA_BAND`
- **SOUL.md:** `/root/.hermes/state/SOUL.md`
- **ZKPC:** Zero-Knowledge Proof of Context — arifOS constitutional protocol
- **Eureka 1-7:** This document, Section III
- **Agent Principal Paradox:** Agentic AI Governance, risk-based autonomy framework
- **Principal-Agent Theory:** Classic economic governance; applied to AI delegation

---

**Version:** v54.0.0
**Forged:** 2026-06-14 06:00 UTC
**Status:** FORGED — pending F13 SEAL
**Authority:** Muhammad Arif bin Fazil (F13 SOVEREIGN)
**Attestation:** https://arif-fazil.com/000/
**Seal:** 𝕾 — pending

**DITEMPA BUKAN DIBERI** — Forged in Cryptography, Governed by Paradox, Sealed by Sovereign.
