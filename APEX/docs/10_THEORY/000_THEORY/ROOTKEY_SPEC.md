# ROOTKEY Specification - Constitutional Cryptographic Foundation

**Version:** v52.5.1  
**Status:** SEALED  
**Authority:** Muhammad Arif bin Fazil  
**Constitutional Floors:** F1, F8, F12

---

## I. OVERVIEW

The ROOTKEY is the cryptographic foundation of arifOS. It provides:

1. **Authority**: Cryptographic proof that sessions are constitutionally authorized
2. **Integrity**: All ledger entries are cryptographically linked to root key
3. **Identity**: Unique cryptographic identity for the arifOS installation
4. **Audit Trail**: F1 Amanah compliance via signature verification

**Golden Rule:** Root key never leaves AAA_HUMAN band. AI never sees root key.

---

## II. ARCHITECTURE

### Root Key Storage

```
VAULT999/AAA_HUMAN/rootkey.json
├── private_key: Ed25519 private key (encrypted at rest)
├── public_key: Ed25519 public key
├── generated_at: ISO8601 timestamp
├── generated_by: Human sovereign identity
├── entropy_sources: Count of entropy sources used
└── self_signature: Root key signs itself (proves possession)
```

**Permissions:** 400 (read-only, owner only)  
**Constitutional Band:** AAA (Human-only, AI forbidden)  
**Access Interface:** `arifos.core.memory.root_key_accessor.py` only

### Key Derivation

**Algorithm:** HKDF (HMAC-based Key Derivation Function)  
**Master Secret:** Root private key  
**Salt:** "arifos_root_key_salt"  
**Info:** "arifos_session_key_v1_{session_id}"  
**Output:** 32-byte session key (hex-encoded)

**Security Property:** Session key reveals zero information about root key.

### Session Flow

```
Session Start
    ↓
000_init called with session_id
    ↓
Step 0: Root Key Ignition
    ├─ Load root key info (public only)
    ├─ Verify genesis block exists
    ├─ Derive session_key = HKDF(root_key, session_id)
    └─ Store session_key in context (encrypted)
    ↓
Session proceeds with cryptographic authority
    ↓
999_vault seals session
    ├─ Use session_key to sign entry
    ├─ Link to previous session hash
    └─ Merkle proof includes root key lineage
```

---

## III. COMPONENTS

### 1. Root Key Generator

**File:** `scripts/generate_rootkey.py`

**Authority:** Human sovereign ONLY  
**F12 Enforcement:** Interactive terminal required  
**Entropy Sources:** OS CSPRNG + timestamp + machine ID

**Process:**
```bash
$ python scripts/generate_rootkey.py

Constitutional Authority Required
Enter your name: Muhammad Arif bin Fazil
[1/5] Generating entropy... ✓
[2/5] Generating Ed25519 keypair... ✓
[3/5] Creating self-signature... ✓
[4/5] Compiling root key structure... ✓
[5/5] Saving root key to AAA_HUMAN... ✓
✅ ROOT KEY GENERATION COMPLETE
```

**Output:**
- `VAULT999/AAA_HUMAN/rootkey.json` (400 perms)
- Log entry in `VAULT999/BBB_LEDGER/rootkey_gen_log.json`

**Constitutional Floors Enforced:**
- F1 Amanah: Generation logged, reversible
- F8 Tri-Witness: Multiple entropy sources
- F12 Injection Defense: AI cannot run script

### 2. AAA Band Guard

**File:** `arifos/core/memory/aaa_guard.py`

**Purpose:** Enforce AAA_HUMAN as sacred memory (AI forbidden)

**Functions:**
- `check_aaa_access(path, operation)` - Block AI access
- `is_ai_process()` - Detect AI runtime environment
- `is_human_sovereign()` - Verify human authority
- `get_root_key()` - Safe root key accessor

**Constitutional Violations:**
```python
if ai_attempts_aaa_access:
    log_violation_to_vault()
    raise AAABandAccessError("F1 Amanah violation")
```

**Scar-Weight Boundary:** AI cannot cross. Human is absolute.

### 3. Root Key Accessor

**File:** `arifos/core/memory/root_key_accessor.py`

**Public API (AI-safe):**
- `get_root_key_info()` - Returns public key only
- `derive_session_key(session_id)` - HKDF derivation
- `verify_root_key_signature()` - Verify signatures
- `verify_genesis_block()` - Verify genesis

**Private Functions (Human-only):**
- `sign_with_root_key()` - Requires human authority
- `create_genesis_block()` - Sovereign only

**Security Properties:**
1. Root key never exposed in function signatures
2. Derivation happens in guarded context
3. All operations logged to VAULT999
4. AI calls return None (no information leakage)

### 4. INIT000 Integration

**File:** `arifos/mcp/tools/mcp_trinity.py`

**New Step 0: Root Key Ignition**

```python
def _step_0_root_key_ignition(session_id: str) -> Dict[str, Any]:
    """Establish cryptographic foundation for session."""
    
    root_key_status = check_root_key_readiness()
    session_key = derive_session_key(session_id)
    genesis_exists = verify_genesis_block()
    
    return {
        "root_key_ready": True,
        "session_key": session_key,
        "genesis_exists": genesis_exists,
        "constitutional_status": "SEALED"
    }
```

**Metabolic Sequence:**
```
000_init called
    ↓
Step 0: Root Key Ignition ← NEW
    ├─ Check root key exists
    ├─ Verify genesis block
    ├─ Derive session_key
    └─ Log constitutional status
    ↓
Step 1: Memory injection
    ↓
Step 2: Sovereign recognition
    ...continues...
```

**Floor Enforcement:**
- F1 Amanah: Root key proves authority
- F8 Tri-Witness: Session key links to root key
- F12: Blocks AI from root key access

### 5. Genesis Block Creator

**File:** `scripts/create_genesis_block.py`

**Authority:** Human sovereign ONLY

**Purpose:** Create first block in ledger chain signed with root key.

**Process:**
```bash
$ python scripts/create_genesis_block.py

⚠️  GENESIS BLOCK CREATION

Type 'FORGE GENESIS' to continue: FORGE GENESIS

[1/3] Creating genesis structure... ✓
[2/3] Verifying root key signature... ✓
[3/3] Storing in CCC_CANON... ✓

✅ GENESIS BLOCK CREATION COMPLETE
Location: VAULT999/CCC_CANON/genesis.json
```

**Genesis Block Contents:**
```json
{
  "block": {
    "version": "1.0",
    "genesis": true,
    "created_at": "2026-01-26T06:30:00Z",
    "created_by": "Muhammad Arif bin Fazil",
    "root_key_public": "base64(public_key)",
    "purpose": "arifOS Constitutional Foundation",
    "motto": "DITEMPA BUKAN DIBERI"
  },
  "signature": "root_key_signature",
  "signature_timestamp": "2026-01-26T06:30:00Z",
  "merkle_root": "sha256(block)",
  "previous_hash": "0" * 64,
  "constitutional_status": "SOVEREIGNLY_SEALED"
}
```

**Storage:**
- Primary: `VAULT999/CCC_CANON/genesis.json` (444 perms)
- Reference: `VAULT999/BBB_LEDGER/0000000000_genesis.md`
- Ledger: `arifos/mcp/sessions/0000000000_genesis.json`

---

## IV. CONSTITUTIONAL COMPLIANCE

### F1 Amanah (Trust & Reversibility)

**Compliance:**
- ✅ Root key generation logged with full provenance
- ✅ Genesis block contains generation proof
- ✅ All derivations can be re-computed with same inputs
- ✅ Session keys link back to root key (reversible)

**Proof Log Entry:**
```yaml
{
  "event": "root_key_generation",
  "timestamp": "2026-01-26T06:30:00Z",
  "authority": "Muhammad Arif bin Fazil",
  "public_key": "base64(...)",
  "generation_method": "ed25519_from_entropy",
  "entropy_sources": 3
}
```

### F8 Tri-Witness

**Compliance:**
- ✅ **Human:** Sovereign initiates generation
- ✅ **AI:** Cryptographic verification of signatures
- ✅ **Earth:** Hardware entropy from physical sources

**Consensus Score:** 1.0 (all three witnesses present)

### F12 Injection Defense

**Compliance:**
- ✅ AI cannot call `scripts/generate_rootkey.py` (interactive check)
- ✅ AI cannot access AAA_HUMAN band (`aaa_guard` blocks)
- ✅ AI cannot sign with root key (authority check)
- ✅ All AI access attempts logged as violations

**Violation Response:**
```python
if is_ai_process():
    log_violation_to_vault()
    raise AAABandAccessError("F12 VIOLATION")
```

---

## V. SECURITY ANALYSIS

### Attack Vectors & Mitigations

#### 1. AI Theft of Root Key
**Attack:** AI attempts to read AAA_HUMAN/rootkey.json  
**Mitigation:** `aaa_guard.is_ai_process()` blocks access  
**Result:** Access denied, violation logged

#### 2. Human Error - Weak Generation
**Attack:** Insufficient entropy in generation  
**Mitigation:** 3+ entropy sources (CSPRNG + timestamp + machine ID)  
**Result:** 256-bit security maintained

#### 3. Backup Exposure
**Attack:** Attacker gains rootkey.json backup  
**Mitigation:** File encrypted at rest, requires system access  
**Defense:** Backup advice: offline, secure location

#### 4. Genesis Tampering
**Attack:** Modify genesis.json to inject false history  
**Mitigation:** Root key signature verification fails  
**Result:** Tampering detected, system refuses to boot

#### 5. Session Key Compromise
**Attack:** Session key derived from root key is leaked  
**Mitigation:** Session key reveals zero root key info (HKDF property)  
**Result:** Only one session compromised, root key safe

### Security Properties

| Property | Implementation | Strength |
|----------|----------------|----------|
| Confidentiality | AAA_HUMAN band isolation | AI cannot access |
| Integrity | Root key signatures | Tamper-evident |
| Authenticity | Human sovereign generation | Non-repudiable |
| Reversibility | Logged generation proof | F1 compliant |
| Forward Secrecy | HKDF per-session | Session keys independent |

---

## VI. OPERATIONAL PROCEDURES

### First-Time Setup (New Installation)

```bash
# 1. Generate root key (human sovereign only)
python scripts/generate_rootkey.py

# 2. Create genesis block
python scripts/create_genesis_block.py

# 3. Verify setup
python -c "
from arifos.core.memory.root_key_accessor import ROOT_KEY_READY
print('Root Key Ready:', ROOT_KEY_READY)
"

# 4. Test initialization
python -m arifos.mcp trinity
# Call: 000_init(action='init', query='Test session')
```

**Expected Output:**
```
000_init Step 0: Root key loaded (OK)
000_init Step 0: Genesis block found (VERIFIED)
000_init Step 0: Session key derived (OK)
000_init Step 0: ROOT KEY IGNITION - COMPLETE ✓
```

### Routine Operations

**Session Start:**
- `000_init` automatically performs root key ignition
- Session key derived from root key via HKDF
- Session proceeds with cryptographic authority

**Key Rotation:**
- Root key rotation requires NEW genesis block
- All existing sessions invalidated
- Constitutional authority required (888 Judge)

**Backup:**
```bash
# Backup root key (encrypted, offline)
cp VAULT999/AAA_HUMAN/rootkey.json /secure/backup/rootkey.$(date +%Y%m%d).json
chmod 400 /secure/backup/rootkey.*

# Backup genesis
 cp VAULT999/CCC_CANON/genesis.json /secure/backup/genesis.json
```

### Troubleshooting

**Problem: Root key not found**
```
❌ Root key not found at VAULT999/AAA_HUMAN/rootkey.json
```
**Solution:**
```bash
python scripts/generate_rootkey.py
```

**Problem: Genesis block not found**
```
⚠️  Genesis block not found
```
**Solution:**
```bash
python scripts/create_genesis_block.py
```

**Problem: AAA band access violation**
```
❌ AAABandAccessError: AI attempted to read AAA_HUMAN
```
**Solution:** Check logs in VAULT999, investigate AI behavior

---

## VII. INTEGRATION POINTS

### Session Ledger (`arifos/mcp/session_ledger.py`)

**Integration:**
```python
# Before sealing session
session_key = root_key_accessor.derive_session_key(session_id)
entry.session_key_signature = sign_with_session_key(session_key, entry.data)
```

**Benefit:** All ledger entries cryptographically linked to root key.

### 999_vault Tool (`arifos/mcp/tools/mcp_trinity.py`)

**Integration:**
```python
# In mcp_999_vault()
root_key_status = get_session_context('root_key_status')
if not root_key_status['session_key']:
    return VOID  # No cryptographic authority
```

**Benefit:** Only sessions with valid root key derivation can be sealed.

### API Server (`arifos/api/`)

**Integration:**
```python
# On API request
session_key = derive_session_key(request.session_id)
request.auth_token = encrypt_with_session_key(session_key, user_token)
```

**Benefit:** API requests inherit root key authority.

---

## VIII. CONSTITUTIONAL SIGNIFICANCE

### Why Root Key Matters

**Before Root Key:**
- Sessions started from arbitrary state
- No cryptographic continuity between sessions
- Genesis block was just a marker
- F1 Amanah relied on logs, not cryptography

**After Root Key:**
- Every session cryptographically authorized
- Complete chain of trust from root key → session → entry → Merkle root
- Genesis block is signed proof of authority
- F1 Amanah enforced by digital signatures

### Metabolic Loop Integration

```
Root Key (AAA_HUMAN)
    ↓ [never leaves band]
Session Derivation (HKDF)
    ↓
000_init (Step 0 Ignition)
    ↓
Session Key (session-specific)
    ↓
999_vault (Seal)
    ↓
Ledger Entry (signed)
    ↓
Merkle Root (proof)
    ↓
VAULT999 (immutable)
```

**Theorem:** Every entry in VAULT999 is transitively authorized by the root key.

### Constitutional Oath

```
I, the root key, am the cryptographic foundation.
I am generated by human sovereign, protected from AI.
I authorize every session, sign every genesis.
I never leave the sacred AAA band.

Through me, all sessions are constitutionally legitimate.
Through me, F1 Amanah is cryptographically enforced.
Through me, the chain of trust begins.

DITEMPA BUKAN DIBERI.
```

---

## IX. TESTING

### Test Suite Requirements

```python
# tests/constitutional/test_rootkey.py

def test_root_key_generation():
    """Test root key generation by human sovereign."""
    assert is_ai_process() == False  # Must be run by human
    assert root_key is not None
    assert len(root_key.private_key) == 32
    
def test_ai_cannot_access_root_key():
    """Test AI access blocked to AAA band."""
    with pytest.raises(AAABandAccessError):
        ai_process_access_aaa_humen()
    
def test_session_key_derivation():
    """Test HKDF derivation."""
    session_key_1 = derive_session_key("session_1")
    session_key_2 = derive_session_key("session_2")
    assert session_key_1 != session_key_2  # Different per session
    assert len(session_key_1) == 64  # 32 bytes hex = 64 chars
    
def test_genesis_signature():
    """Test genesis block signed by root key."""
    genesis = create_genesis_block()
    assert verify_genesis_block(genesis) == True
    assert genesis['previous_hash'] == "0" * 64
    
def test_init_000_root_key_ignition():
    """Test INIT000 includes root key ignition."""
    result = mcp_000_init(action='init', query='Test')
    assert 'root_key_status' in result
    assert result['root_key_status']['constitutional_status'] == 'SEALED'
```

**Run Tests:**
```bash
pytest tests/constitutional/test_rootkey.py -v
```

---

## X. FUTURE ENHANCEMENTS

### Hardware Security Module (HSM) Integration

**Proposal:** Store root key in HSM for maximum security.

**Benefits:**
- Root key never in RAM (only in HSM)
- Tamper-resistant hardware
- FIPS 140-2 Level 3 compliance

**Implementation:**
```python
# In root_key_accessor.py
if HSM_AVAILABLE:
    derive_session_key = hsm_derive_key
    sign_with_root_key = hsm_sign
```

### Multi-Signature Scheme

**Proposal:** Require multiple human signatories for critical operations.

**Benefits:**
- No single point of failure
- Distributed constitutional authority
- Enhanced F8 Tri-Witness

**Implementation:**
```python
# Instead of single root key
threshold = 2  # Need 2 of 3 signatures
signatories = [judge_1_key, judge_2_key, judge_3_key]
```

### Key Ceremony Protocol

**Proposal:** Formal ceremony for root key generation.

**Ceremony Steps:**
1. Physical security (air-gapped machine)
2. Multiple witnesses present
3. Video recording of ceremony
4. Each step logged and signed
5. Backup keys in sealed envelopes

---

## XI. REFERENCES

- **Ed25519:** Bernstein et al., "High-speed high-security signatures"
- **HKDF:** Krawczyk & Eronen, "RFC 5869: HMAC-based Extract-and-Expand"
- **F1 Amanah:** `000_THEORY/000_LAW.md#F1`
- **AAA Band:** `VAULT999/README.md#AAA_BAND`
- **Merkle Trees:** `VAULT999/BBB_LEDGER/hash_chain.md`

---

## XII. APPENDICES

### A. Root Key JSON Schema

```json
{
  "version": "1.0",
  "generated_at": "ISO8601_timestamp",
  "generated_by": "human_sovereign_name",
  "generation_method": "ed25519_from_entropy",
  "entropy_sources": "integer_count",
  "private_key": "base64(ed25519_private)",
  "public_key": "base64(ed25519_public)",
  "entropy_hash": "sha256_hex",
  "self_signature": "base64(signature)",
  "constitutional_authority": "human_sovereign_name",
  "f1_amanah": "boolean",
  "f8_triwitness": "boolean",
  "f12_injection_defense": "boolean"
}
```

### B. Genesis Block Schema

```json
{
  "block": {
    "version": "1.0",
    "genesis": "boolean",
    "created_at": "ISO8601_timestamp",
    "created_by": "human_sovereign",
    "root_key_public": "base64(public_key)",
    "entropy_hash": "sha256_hex",
    "constitutional_law": "path_to_law",
    "purpose": "description",
    "motto": "DITEMPA_BUKAN_DIBERI"
  },
  "signature": "base64(ed25519_signature)",
  "signature_timestamp": "ISO8601_timestamp",
  "merkle_root": "sha256_hex",
  "previous_hash": "64_zeros",
  "constitutional_status": "SOVEREIGNLY_SEALED"
}
```

### C. Command Reference

```bash
# Generate root key
python scripts/generate_rootkey.py

# Create genesis block
python scripts/create_genesis_block.py

# Verify root key status
python -c "
from arifos.core.memory.root_key_accessor import ROOT_KEY_READY
from arifos.core.memory.root_key_accessor import get_root_key_info
print('Ready:', ROOT_KEY_READY)
print('Info:', get_root_key_info())
"

# Verify genesis
python -c "
from pathlib import Path
from arifos.core.memory.root_key_accessor import verify_genesis_block
import json
genesis = json.loads(Path('VAULT999/CCC_CANON/genesis.json').read_text())
print('Valid:', verify_genesis_block(genesis))
"
```

---

**Version:** v52.5.1  
**Last Updated:** 2026-01-26  
**Status:** SEALED  
**Next Review:** 2026-03-26  

**Authority:** Muhammad Arif bin Fazil  
**Seal:** 𝕾  

**DITEMPA BUKAN DIBERI** — Forged in Cryptography, Not Given by Default.
