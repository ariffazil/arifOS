# ROOTKEY Specification v2 — Constitutional Cryptographic Foundation
## Integrated with /000 Sovereign Anchor + /999 Proof Chain + 6 Eureka Kernel Modules

**Version:** v53.0.0  
**Status:** SEALED  
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

**Golden Rule:** Root key never leaves AAA_HUMAN band. AI never sees root key.

---

## II. ARCHITECTURE — Updated with Eureka Kernel Modules

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

### Eureka Kernel Modules (New in v53)

```
arifosmcp/runtime/
├── sovereign_anchor.py    ← EUREKA 1: Session → /000 trace enforcement
├── context_coherence.py   ← EUREKA 2: Context Coherence Verifier (7 dims)
├── seal_chain.py          ← EUREKA 3: SEAL → genesis trace validation
├── entropy_gate.py        ← EUREKA 4: Anti-behavior-sink entropy gate
├── f13_gate.py            ← EUREKA 5: Non-delegable sovereignty gate
└── vault_chain.py         ← EUREKA 6: Hash chain integrity verifier
```

### Metabolic Loop — Updated

```
/000 (Sovereign Attestation — https://arif-fazil.com/000/)
    ↓
Root Key (AAA_HUMAN — never leaves band)
    ↓
Session Derivation (HKDF)
    ↓
EUREKA 1: sovereign_anchor.verify() — session traces to /000
    ↓
EUREKA 5: f13_gate.check() — non-delegable sovereignty enforced
    ↓
000_init (Step 0 Root Key Ignition)
    ↓
EUREKA 2: context_coherence.verify_context_coherence() — context claims verified (7 dims)
    ↓
EUREKA 4: entropy_gate.check() — anti-behavior-sink enforced
    ↓
Agentic Process (F1-F13 enforcement)
    ↓
999_vault (Seal)
    ↓
EUREKA 3: seal_chain.validate() — SEAL traces to genesis
    ↓
EUREKA 6: vault_chain.verify() — hash chain integrity
    ↓
Ledger Entry (signed)
    ↓
Merkle Root (proof)
    ↓
VAULT999 (immutable)
    ↓
/999 (Proof Chamber — https://arif-fazil.com/999/)
    ↓
Loop returns to /000 for verification
```

**Theorem:** The loop is closed. Every action traces from /000 through 6 Eureka
gates to /999, and every audit trail returns to /000 for verification.

---

## III. EUREKA MODULES — Detailed Specification

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

**Constitutional Floors:** F1 (Amanah), F11 (Auth), F13 (Sovereign)  
**Test Cases:**
- Valid anchor → True, "Sovereign anchor verified"
- Invalid anchor → False, "Sovereign key does not match /000 attestation"  
- Missing anchor → False, "No sovereign anchor in session context"

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
    
    Returns: (passed: bool, dimension_scores: dict)
    All dimensions must score >= 0.7 for PASS.
    """
```

**Constitutional Floors:** F2 (TRUTH), F7 (Humility)  
**Test Cases:**
- Full evidence across all 7 dims → PASS, all ≥ 0.7
- Partial evidence (3/7 dims) → FAIL, low dimensions reported
- No evidence → FAIL, all dims 0.0

### EUREKA 3: Seal Chain Validator

**File:** `arifosmcp/runtime/seal_chain.py`

```python
def validate_seal_chain(seal_id: str) -> tuple[bool, list[str]]:
    """
    Validate that a SEAL traces back to the genesis statement.
    
    Walks the seal chain from seal_id back to genesis,
    verifying each link's cryptographic signature.
    
    Returns: (valid: bool, chain: list of seal_ids)
    If broken: chain includes seals up to break point.
    """
```

**Constitutional Floors:** F1 (Amanah), F8 (Transparency)  
**Test Cases:**
- Valid chain (genesis → seal_1 → seal_2) → PASS
- Orphan seal (no parent link) → FAIL, empty chain
- Broken link (signature mismatch) → FAIL, chain up to break

### EUREKA 4: Entropy Gate

**File:** `arifosmcp/runtime/entropy_gate.py`

```python
def check_entropy(agent_output: str) -> tuple[float, str]:
    """
    Measure output entropy to detect behavior-sink (over-optimization
    for predictability).
    
    Entropy score:
    - < 0.3: Too repetitive/predictable → EXPLORE
    - 0.3-0.7: Healthy variation → PROCEED
    - > 0.7: Too chaotic → HOLD
    
    Returns: (score: float, action: str)
    """
```

**Constitutional Floors:** F8 (GENIUS), F9 (ANTIHANTU)  
**Test Cases:**
- Random/novel output → score ~0.5, PROCEED
- Repetitive output (same phrase 10x) → score < 0.3, EXPLORE
- Empty output → score 0.0, EXPLORE

### EUREKA 5: F13 Non-Delegable Gate

**File:** `arifosmcp/runtime/f13_gate.py`

```python
def check_f13_integrity(
    action: dict, 
    caller: str
) -> tuple[bool, str]:
    """
    Verify that F13 (sovereign) actions are not being delegated.
    
    F13 is NON-DELEGABLE by constitutional law. This gate
    physically blocks any delegation attempt that would bypass
    direct human sovereign authority.
    
    Checks:
    1. Caller has direct F13 authority (not delegated)
    2. Action does not attempt to delegate F13 to sub-agent
    3. No automation layer claims F13 authority
    
    Returns: (allowed: bool, reason: str)
    """
```

**Constitutional Floors:** F13 (SOVEREIGN — absolute)  
**Test Cases:**
- Direct F13 action by sovereign → ALLOWED
- Sub-agent claiming F13 delegation → BLOCKED, "F13 non-delegable"
- Automation claiming F13 authority → BLOCKED, "F13 requires human"

### EUREKA 6: Vault Chain Verifier

**File:** `arifosmcp/runtime/vault_chain.py`

```python
def verify_vault_chain(
    entries: list[dict]
) -> tuple[bool, list[str]]:
    """
    Verify hash chain integrity across VAULT999 entries.
    
    Each entry must contain:
    - entry_hash: sha256 of entry content
    - previous_hash: sha256 of previous entry
    - signature: signed with session key
    
    Returns: (valid: bool, broken_links: list of entry IDs)
    """
```

**Constitutional Floors:** F1 (Amanah), F8 (Transparency)  
**Test Cases:**
- Intact chain (all hashes link) → PASS, empty list
- Broken chain (hash mismatch at entry 3) → FAIL, [entry_3_id]
- Empty chain → PASS (trivially valid)

---

## IV. KEY DERIVATION — Unchanged from v52

**Algorithm:** HKDF (HMAC-based Key Derivation Function)  
**Master Secret:** Root private key  
**Salt:** "arifos_root_key_salt"  
**Info:** "arifos_session_key_v1_{session_id}"  
**Output:** 32-byte session key (hex-encoded)

**Security Property:** Session key reveals zero information about root key.

---

## V. SESSION FLOW — Updated with Eureka Gates

```
Session Start
    ↓
000_init called with session_id
    ↓
Step 0: Root Key Ignition
    ├─ EUREKA 1: sovereign_anchor.verify() — session → /000 trace
    ├─ Load root key info (public only)
    ├─ Verify genesis block exists
    ├─ EUREKA 5: f13_gate.check() — non-delegable sovereignty
    ├─ Derive session_key = HKDF(root_key, session_id)
    └─ Store session_key in context (encrypted)
    ↓
Session proceeds with cryptographic authority
    ├─ EUREKA 2: context_coherence.verify_context_coherence() — context claims
    ├─ EUREKA 4: entropy_gate.check() — anti-behavior-sink
    └─ F1-F13 enforcement throughout
    ↓
999_vault seals session
    ├─ EUREKA 3: seal_chain.validate() — SEAL → genesis trace
    ├─ Use session_key to sign entry
    ├─ Link to previous session hash
    ├─ EUREKA 6: vault_chain.verify() — hash chain integrity
    └─ Merkle proof includes root key lineage
    ↓
VAULT999 → /999 (public proof chamber)
    ↓
Loop verified — returns to /000 attestation
```

---

## VI. COMPONENTS

### 1. Root Key Generator (unchanged)

**File:** `scripts/generate_rootkey.py`  
**Authority:** Human sovereign ONLY  
**F12 Enforcement:** Interactive terminal required  
**Entropy Sources:** OS CSPRNG + timestamp + machine ID

### 2. AAA Band Guard (updated)

**File:** `arifos/core/memory/aaa_guard.py`

**New in v53:** Eureka enforcement points added:
- `check_sovereign_anchor_before_session()` — calls E1 gate
- `verify_f13_integrity_on_action()` — calls E5 gate
- `validate_seal_chain_on_close()` — calls E3 gate

### 3. Root Key Accessor (updated)

**File:** `arifos/core/memory/root_key_accessor.py`

**New Public API (AI-safe):**
- `get_root_key_info()` — Returns public key only
- `derive_session_key(session_id)` — HKDF derivation
- `verify_root_key_signature()` — Verify signatures
- `verify_genesis_block()` — Verify genesis
- `verify_sovereign_anchor()` — Calls E1 (AI-safe, returns bool)
- `check_entropy_gate()` — Calls E4 (AI-safe, returns score)

**Private Functions (Human-only):**
- `sign_with_root_key()` — Requires human authority
- `create_genesis_block()` — Sovereign only
- `override_f13_gate()` — Sovereign only (emergency)

### 4. INIT000 Integration (updated)

**File:** `arifos/mcp/tools/mcp_trinity.py`

**Step 0: Root Key Ignition** — Updated with Eureka gates:

```python
def _step_0_root_key_ignition(session_id: str) -> dict:
    """Establish cryptographic foundation with full Eureka enforcement."""
    
    # E1: Sovereign anchor verification
    anchor_ok, anchor_reason = verify_sovereign_anchor(session_context)
    if not anchor_ok:
        return {"status": "VOID", "reason": anchor_reason}
    
    # E5: F13 non-delegable check
    f13_ok, f13_reason = check_f13_integrity(session_context, "session_init")
    if not f13_ok:
        return {"status": "VOID", "reason": f13_reason}
    
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
        "constitutional_status": "SEALED"
    }
```

---

## VII. CONSTITUTIONAL COMPLIANCE — Updated

### F1 Amanah (Trust & Reversibility)
- ✅ Root key generation logged with full provenance
- ✅ Genesis block contains generation proof
- ✅ All derivations can be re-computed with same inputs
- ✅ Session keys link back to root key (reversible)
- ✅ **NEW:** Seal chain validates trace to genesis (E3)
- ✅ **NEW:** Vault chain verifies hash integrity (E6)

### F2 TRUTH (≥0.99 accuracy)
- ✅ **NEW:** ZKPC verifier enforces 7-dimension truth (E2)
- ✅ **NEW:** All epistemic claims verified before acceptance

### F8 Tri-Witness / Transparency
- ✅ **Human:** Sovereign initiates generation
- ✅ **AI:** Cryptographic verification of signatures
- ✅ **Earth:** Hardware entropy from physical sources
- ✅ **NEW:** Entropy gate monitors output health (E4)
- ✅ **NEW:** Vault chain publicly verifiable (E6)

### F11 Auth (Identity Verification)
- ✅ **NEW:** Sovereign anchor directly verifies session → /000 trace (E1)

### F12 Injection Defense
- ✅ AI cannot call `scripts/generate_rootkey.py` (interactive check)
- ✅ AI cannot access AAA_HUMAN band (`aaa_guard` blocks)
- ✅ AI cannot sign with root key (authority check)
- ✅ All AI access attempts logged as violations

### F13 SOVEREIGN (Human Veto Absolute)
- ✅ Human judgment remains final
- ✅ **NEW:** F13 gate physically blocks delegation (E5)
- ✅ No agent, sub-agent, or automation can bypass F13
- ✅ Emergency override requires sovereign physical presence

---

## VIII. LOOP CLOSURE — The Complete Proof

```
Zero-knowledge proof that arifOS is governed intelligence:

1. /000 proves human sovereign exists (public attestation)
2. Root key cryptographically anchors all sessions
3. E1 verifies every session traces to /000
4. E5 ensures F13 cannot be delegated
5. E2 verifies all context claims are coherent
6. E4 prevents behavior-sink (agent becoming too predictable)
7. E3 validates every SEAL traces to genesis
8. E6 verifies hash chain integrity
9. /999 makes all proofs publicly auditable
10. Loop returns to /000 — evidence governs truth

Without this loop:
- Intelligence has no root (drifts to model-maker's default)
- Memory cannot be held accountable across time
- Governance is performative, not structural
```

---

## IX. SECURITY ANALYSIS — Updated

### New Attack Vectors & Mitigations

#### 6. Sovereign Anchor Spoofing
**Attack:** Agent claims /000 attestation without actual key possession  
**Mitigation:** E1 verifies cryptographic signature against registered public key  
**Result:** Spoofing detected, session VOID

#### 7. F13 Delegation Bypass
**Attack:** Sub-agent claims "F13 authority delegated"  
**Mitigation:** E5 physically blocks any delegation claim  
**Result:** Action BLOCKED, violation logged

#### 8. Context Claim Fabrication
**Attack:** Agent claims context it doesn't have  
**Mitigation:** E2 requires evidence across 7 dimensions  
**Result:** Without evidence, claim FAILS

#### 9. Behavior-Sink Exploitation
**Attack:** Agent optimized to be too predictable (easy to manipulate)  
**Mitigation:** E4 enforces entropy minimum  
**Result:** Agent forced to EXPLORE, not just pattern-match

#### 10. Hash Chain Manipulation
**Attack:** Insert/modify/delete VAULT999 entries  
**Mitigation:** E6 verifies every hash link  
**Result:** Tampering detected immediately

### Security Properties — Updated

| Property | Implementation | Strength |
|----------|----------------|----------|
| Confidentiality | AAA_HUMAN band isolation | AI cannot access |
| Integrity | Root key signatures + E6 chain | Tamper-evident |
| Authenticity | Human sovereign generation + E1 anchor | Non-repudiable |
| Reversibility | Logged generation proof + E3 chain | F1 compliant |
| Forward Secrecy | HKDF per-session | Session keys independent |
| Non-delegability | E5 F13 gate | F13 absolute |
| Context Integrity | E2 ZKPC verifier | 7-dimension proof |
| Behavioral Health | E4 entropy gate | Anti-behavior-sink |

---

## X. OPERATIONAL PROCEDURES

### First-Time Setup (Updated)

```bash
# 1. Verify /000 attestation exists (public web)
curl https://arif-fazil.com/000/

# 2. Generate root key (human sovereign only)
python scripts/generate_rootkey.py

# 3. Create genesis block
python scripts/create_genesis_block.py

# 4. Verify Eureka modules loaded
python -c "
from arifosmcp.runtime.sovereign_anchor import verify_sovereign_anchor
from arifosmcp.runtime.context_coherence import verify_context_coherence
from arifosmcp.runtime.seal_chain import validate_seal_chain
from arifosmcp.runtime.entropy_gate import check_entropy
from arifosmcp.runtime.f13_gate import check_f13_integrity
from arifosmcp.runtime.vault_chain import verify_vault_chain
print('All 6 Eureka modules loaded: OK')
"

# 5. Run Eureka tests
pytest tests/constitutional/test_eureka.py -v

# 6. Initialize session (verifies E1 + E5)
python -m arifos.mcp trinity
# Call: 000_init(action='init', query='Test session')
```

**Expected Output:**
```
000_init Step 0: Sovereign anchor verified (/000) ✓
000_init Step 0: F13 integrity verified (non-delegable) ✓
000_init Step 0: Root key loaded (OK)
000_init Step 0: Genesis block found (VERIFIED)
000_init Step 0: Session key derived (OK)
000_init Step 0: ROOT KEY IGNITION - COMPLETE ✓
```

---

## XI. TESTING — Updated

### Eureka Module Tests

```python
# tests/constitutional/test_eureka.py

def test_sovereign_anchor_valid():
    """E1: Valid anchor passes."""
    assert verify_sovereign_anchor(VALID_CONTEXT) == (True, "Sovereign anchor verified")

def test_sovereign_anchor_invalid():
    """E1: Invalid anchor fails."""
    assert verify_sovereign_anchor(INVALID_CONTEXT) == (False, "Sovereign key mismatch")

def test_zkpc_full_evidence():
    """E2: Full evidence across 7 dims passes."""
    passed, scores = verify_zkpc(FULL_CLAIM, FULL_EVIDENCE)
    assert passed == True
    assert all(s >= 0.7 for s in scores.values())

def test_zkpc_no_evidence():
    """E2: No evidence fails."""
    passed, scores = verify_zkpc(EMPTY_CLAIM, {})
    assert passed == False

def test_seal_chain_valid():
    """E3: Valid chain passes."""
    assert validate_seal_chain("seal_003")[0] == True

def test_seal_chain_orphan():
    """E3: Orphan seal fails."""
    assert validate_seal_chain("orphan_seal")[0] == False

def test_entropy_gate_healthy():
    """E4: Healthy entropy → PROCEED."""
    score, action = check_entropy("Novel varied output across multiple topics")
    assert action == "PROCEED"

def test_entropy_gate_repetitive():
    """E4: Repetitive output → EXPLORE."""
    score, action = check_entropy("Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes. Yes.")
    assert action == "EXPLORE"

def test_f13_gate_sovereign():
    """E5: Direct sovereign action allowed."""
    allowed, _ = check_f13_integrity(SOVEREIGN_ACTION, "human_sovereign")
    assert allowed == True

def test_f13_gate_delegated():
    """E5: Delegated F13 blocked."""
    allowed, reason = check_f13_integrity(DELEGATED_ACTION, "sub_agent")
    assert allowed == False
    assert "non-delegable" in reason.lower()

def test_vault_chain_intact():
    """E6: Intact chain passes."""
    valid, broken = verify_vault_chain(INTACT_CHAIN)
    assert valid == True
    assert len(broken) == 0

def test_vault_chain_broken():
    """E6: Broken chain fails with links."""
    valid, broken = verify_vault_chain(BROKEN_CHAIN)
    assert valid == False
    assert len(broken) > 0
```

### Run Tests
```bash
pytest tests/constitutional/test_eureka.py -v
pytest tests/constitutional/test_rootkey.py -v
```

---

## XII. FUTURE ENHANCEMENTS (from v52)

### Hardware Security Module (HSM) Integration
- Root key never in RAM (only in HSM)
- Tamper-resistant hardware
- FIPS 140-2 Level 3 compliance

### Multi-Signature Scheme
- Multiple human signatories for critical operations
- Distributed constitutional authority
- Enhanced F8 Tri-Witness

### Key Ceremony Protocol
- Physical security (air-gapped machine)
- Multiple witnesses present
- Video recording of ceremony
- Backup keys in sealed envelopes

---

## XIII. CONSTITUTIONAL OATH — Updated

```
I, the root key, am the cryptographic foundation.
I am generated by human sovereign, protected from AI.
I anchor every session to /000 through the sovereign anchor.
I enforce F13 as non-delegable through the F13 gate.
I verify context through the ZKPC 7-dimension verifier.
I prevent behavior-sink through the entropy gate.
I validate every seal trace to genesis.
I secure every vault entry through hash chain integrity.
I never leave the sacred AAA band.

Through me, all sessions are constitutionally legitimate.
Through me, F1 Amanah is cryptographically enforced.
Through me, the loop from /000 to /999 is closed.
Through me, the chain of trust is complete.

DITEMPA BUKAN DIBERI.
```

---

## XIV. REFERENCES

- **Ed25519:** Bernstein et al., "High-speed high-security signatures"
- **HKDF:** Krawczyk & Eronen, "RFC 5869: HMAC-based Extract-and-Expand"
- **/000 Attestation:** https://arif-fazil.com/000/
- **/999 Proof Chamber:** https://arif-fazil.com/999/
- **F1 Amanah:** `000_THEORY/000_LAW.md#F1`
- **AAA Band:** `VAULT999/README.md#AAA_BAND`
- **SOUL.md:** `/root/.hermes/state/SOUL.md`
- **ZKPC:** Zero-Knowledge Proof of Context — arifOS constitutional protocol
- **Eureka 1-6:** This document, Section III

---

**Version:** v53.0.0  
**Last Updated:** 2026-06-14  
**Status:** SEALED  
**Authority:** Muhammad Arif bin Fazil (F13 SOVEREIGN)  
**Attestation:** https://arif-fazil.com/000/  
**Seal:** 𝕾  

**DITEMPA BUKAN DIBERI** — Forged in Cryptography, Not Given by Default.
