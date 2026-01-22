# Cooling Ledger v35 - Schema and Usage

**Version:** v35Ω (extended in v37)  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document the Cooling Ledger JSON schema, hash-chain integrity, CLI tools, and usage patterns

---

## 1. Cooling Ledger Overview

The Cooling Ledger is an **append-only audit trail** for all arifOS governance decisions.

**Key Properties:**
- **Append-only:** No mutations, no deletions
- **Hash-chained:** SHA-256 integrity verification
- **Merkle-proven:** Cryptographic proof for each entry
- **JSONL format:** One JSON object per line

**Storage Path:** `cooling_ledger/L1_cooling_ledger.jsonl`

**Module:** `arifos_core/memory/cooling_ledger.py`

---

## 2. JSON Schema (v35Ω)

**Schema File:** `spec/cooling_ledger.schema.json`

### 2.1 Top-Level Fields

```json
{
  "ledger_version": "v35Ω",
  "timestamp": "2024-01-15T10:30:45Z",
  "job_id": "uuid-string",
  "stakes": "low|medium|high|critical",
  "pipeline_path": ["000_VOID", "111_SENSE", "888_JUDGE", "999_SEAL"],
  "metrics": { /* Floor metrics */ },
  "verdict": "SEAL|PARTIAL|888_HOLD|VOID|SABAR",
  "floor_failures": ["F1_Truth", "F2_DeltaS"],
  "eye_flags": [ /* @EYE flags */ ],
  "cce_audits": { /* CCE 4-audit chain */ },
  "tri_witness_components": { /* Human/AI/Earth */ },
  "organs": { /* W@W organ vetos */ },
  "context_summary": "Brief context",
  "reason": "Human-readable reason",
  "sabar_reason": "If SABAR, why",
  "phoenix_cycle_id": "If Phoenix-72 review",
  "hash_chain": {
    "previous_hash": "sha256-hash",
    "current_hash": "sha256-hash",
    "signature": "optional-kms-signature"
  },
  "metadata": { /* Additional metadata */ }
}
```

### 2.2 Metrics Object (9 Floors)

```json
{
  "truth": 0.99,
  "delta_s": 0.15,
  "peace_squared": 1.2,
  "kappa_r": 0.96,
  "omega_0": 0.04,
  "amanah": true,
  "rasa": true,
  "tri_witness": 0.97,
  "anti_hantu": "PASS",
  "psi": 1.25,
  "ambiguity": 0.05,
  "drift_delta": 0.12,
  "paradox_load": 0.3
}
```

**Required Fields:** `truth`, `delta_s`, `peace_squared`, `kappa_r`, `omega_0`, `amanah`, `rasa`, `psi`

**Extended Fields (v35Ω):** `ambiguity`, `drift_delta`, `paradox_load`

### 2.3 Verdict Enum

```json
"verdict": "SEAL" | "PARTIAL" | "888_HOLD" | "VOID" | "SABAR" | "SUNSET"
```

**v35Ω Hierarchy:** SABAR > VOID > 888_HOLD > PARTIAL > SEAL

**v38.2 Addition:** SUNSET (lawful revocation)

### 2.4 Floor Failures Array

```json
"floor_failures": [
  "F1_Truth",
  "F2_DeltaS",
  "F3_Peace2",
  "F4_KappaR",
  "F5_Omega0",
  "F6_Amanah",
  "F7_RASA",
  "F8_TriWitness",
  "F9_AntiHantu",
  "Ambiguity",
  "DriftDelta",
  "ParadoxLoad",
  "Dignity",
  "VaultConsistency",
  "BehaviorDrift",
  "OntologyGuard",
  "SleeperScan"
]
```

### 2.5 @EYE Flags Array

```json
"eye_flags": [
  {
    "view_id": 1,
    "view_name": "FloorView",
    "severity": "blocking",
    "message": "Truth floor failed (0.85 < 0.99)"
  }
]
```

**Severity Levels:** `"info"`, `"warning"`, `"blocking"`

### 2.6 CCE 4-Audit Chain

```json
"cce_audits": {
  "delta_p": "PASS",
  "omega_p": "PASS",
  "psi_p": "PASS",
  "phi_p": "PASS"
}
```

**Status:** `"PASS"` | `"FAIL"` | `"WARN"`

**Audits:**
- **delta_p:** Contrast audit (logical coherence, ΔS)
- **omega_p:** Humility audit (κᵣ, tone, Ω₀)
- **psi_p:** Vitality audit (Peace², equilibrium)
- **phi_p:** Ethics audit (Maruah, Amanah)

### 2.7 W@W Organs Object

```json
"organs": {
  "@RIF": false,
  "@WELL": false,
  "@WEALTH": true,
  "@GEOX": false,
  "@PROMPT": false
}
```

**true = veto issued**, **false = no veto**

### 2.8 Hash Chain Object

```json
"hash_chain": {
  "previous_hash": "sha256-of-previous-entry",
  "current_hash": "sha256-of-this-entry",
  "signature": "optional-kms-signature"
}
```

**Genesis Entry:** `previous_hash = "0000000000000000000000000000000000000000000000000000000000000000"`

---

## 3. CoolingEntry Dataclass

**Module:** `arifos_core/memory/cooling_ledger.py`

```python
@dataclass
class CoolingEntry:
    timestamp: float
    query: str
    candidate_output: str
    metrics: CoolingMetrics
    verdict: str
    floor_failures: List[str]
    sabar_reason: Optional[str]
    organs: Dict[str, bool]
    phoenix_cycle_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_json_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict"""
```

**CoolingMetrics Dataclass:**
```python
@dataclass
class CoolingMetrics:
    truth: float
    delta_s: float
    peace_squared: float
    kappa_r: float
    omega_0: float
    rasa: bool
    amanah: bool
    tri_witness: float
    psi: Optional[float] = None
```

---

## 4. Hash-Chain Integrity Mechanism

**Purpose:** Prevent tampering with ledger entries through cryptographic chaining

### 4.1 Hash Computation

**Function:** `arifos_core/memory/cooling_ledger.py::_compute_hash(entry: Dict[str, Any]) -> str`

**Algorithm:** SHA3-256 (not SHA-256 - uses SHA3 for collision resistance)

**Excluded Fields:**
- `hash` (self-referential)
- `kms_signature` (added after hash)
- `kms_key_id` (metadata)

**Process:**
1. Remove excluded fields from entry
2. Create canonical JSON: `json.dumps(entry, sort_keys=True, separators=(",", ":"))`
3. Compute SHA3-256 hash of UTF-8 encoded JSON
4. Return hex digest

### 4.2 Chain Linking

**Module:** `arifos_core/ledger_hashing.py`

**Constants:**
```python
HASH_FIELD = "hash"
PREVIOUS_HASH_FIELD = "previous_hash"
GENESIS_PREVIOUS_HASH = "0" * 64  # All zeros for first entry
```

**Verification Process:**
1. Load all entries from JSONL file
2. For entry N:
   - Verify `entry[N].previous_hash == entry[N-1].hash`
   - Recompute hash and verify `entry[N].hash == computed_hash`
3. If any mismatch → chain broken, tampering detected

### 4.3 Chain Verification

**Function:** `arifos_core/ledger_hashing.py::verify_hash_chain(entries: List[Dict]) -> Tuple[bool, List[str]]`

**Returns:**
- `(True, [])` if chain is valid
- `(False, ["error messages"])` if chain is broken

**CLI Tool:** `arifos-verify-ledger` (see §5.2)

---

## 5. CLI Tools (7 Commands)

**Source:** `pyproject.toml::project.scripts`

All CLI tools are Python entry points, no code dependencies required after `pip install arifos`.

### 5.1 arifos-analyze-governance

**Entry Point:** `scripts.analyze_governance:main`

**Purpose:** Analyze governance decisions from ledger

**Usage:**
```bash
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl --output report.json
```

**Output:**
- Verdict distribution (SEAL vs VOID vs SABAR)
- Floor failure frequency
- Organ veto statistics
- Timeline analysis

### 5.2 arifos-verify-ledger

**Entry Point:** `scripts.verify_ledger_chain:main`

**Purpose:** Verify hash-chain integrity

**Usage:**
```bash
arifos-verify-ledger
```

**Output:**
- Chain status (VALID / BROKEN)
- Entry count
- First/last entry timestamps
- Any detected tampering

**Exit Code:**
- `0` = chain valid
- `1` = chain broken

**CI-Ready:** Can be used in CI/CD pipelines

### 5.3 arifos-show-merkle-proof

**Entry Point:** `scripts.show_merkle_proof:main`

**Purpose:** Show cryptographic Merkle proof for entry #N

**Usage:**
```bash
arifos-show-merkle-proof --index 0
```

**Output:**
- Entry hash
- Merkle tree path (sibling hashes)
- Root hash
- Verification status

### 5.4 arifos-propose-canon

**Entry Point:** `scripts.propose_canon_from_receipt:main`

**Purpose:** Propose amendment from successful run

**Usage:**
```bash
# List proposed amendments
arifos-propose-canon --list

# Propose amendment from entry #N
arifos-propose-canon --index 0
```

**Output:** Creates `cooling_ledger/proposed/PROPOSED_CANON_v38_amendment_N.json`

### 5.5 arifos-seal-canon

**Entry Point:** `scripts.seal_proposed_canon:main`

**Purpose:** Phoenix-72 finalization (human approves law change)

**Usage:**
```bash
arifos-seal-canon --file cooling_ledger/proposed/PROPOSED_CANON_v38_amendment_0.json
```

**Requires:** Human approval (interactive prompt)

**Output:** Seals amendment into `canon/` directory

### 5.6 arifos-compute-merkle

**Entry Point:** `scripts.compute_merkle_root:main`

**Purpose:** Compute Merkle root for entire ledger

**Usage:**
```bash
arifos-compute-merkle
```

**Output:**
- Merkle root hash
- Entry count
- Tree depth
- Saves to `cooling_ledger/L1_merkle_root.txt`

### 5.7 arifos-build-ledger-hashes

**Entry Point:** `scripts.build_ledger_hashes:main`

**Purpose:** Rebuild hash chain for existing ledger (repair tool)

**Usage:**
```bash
arifos-build-ledger-hashes
```

**Warning:** Only use on uncorrupted ledgers. Does NOT fix tampered data.

---

## 6. v37 Extensions

### 6.1 HeadState

**Module:** `arifos_core/memory/cooling_ledger.py`

**Purpose:** Track most recent entry for fast lookups

**Implementation:** In-memory cache of last entry hash

### 6.2 Rotation

**Purpose:** Archive old entries to cold storage after 90 days

**Status:** [TODO - Not yet implemented in v38]

### 6.3 Fail-Open Hardening

**v37 Change:** If ledger file is corrupted, system continues but logs error

**Previous Behavior:** System would crash

**Rationale:** Availability > perfect audit (can repair later)

---

## 7. Logging Function Signature

**Module:** `arifos_core/memory/cooling_ledger.py`

**Function:** `log_cooling_entry()`

**Signature:**
```python
def log_cooling_entry(
    query: str,
    candidate_output: str,
    metrics: Metrics,
    verdict: str,
    floor_failures: List[str],
    organs: Dict[str, bool],
    sabar_reason: Optional[str] = None,
    phoenix_cycle_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ledger_path: Optional[Path] = None,
) -> None:
    """Append entry to Cooling Ledger with hash-chain integrity"""
```

**Usage in Pipeline:**
```python
# Stage 999_SEAL
log_cooling_entry(
    query=state.query,
    candidate_output=state.raw_response,
    metrics=state.metrics,
    verdict=state.verdict.value,
    floor_failures=state.floor_failures,
    organs={"@WELL": False, "@WEALTH": True, ...},
    sabar_reason=state.sabar_reason,
)
```

---

## 8. Test Coverage

**Test Files:**
- `tests/test_cooling_ledger.py` — Basic ledger operations
- `tests/test_cooling_ledger_kms_integration.py` — KMS signing integration
- `tests/integration/test_memory_eureka_comprehensive_v38.py` — Ledger + memory integration

**Key Test Assertions:**
- Hash chain integrity after multiple appends
- Genesis entry has all-zero previous_hash
- Merkle proof verification
- CLI tools execute without errors
- Ledger survives file corruption (fail-open)

---

## 9. References

**Canon:**
- `canon/05_COOLING_LEDGER_PHOENIX_v38Omega.md` — Cooling Ledger law
- `spec/VAULT_999.md` — Vault-999 spec (includes ledger)

**Spec:**
- `spec/cooling_ledger.schema.json` — JSON schema (v35Ω)
- `spec/cooling_ledger_v36.schema.json` — Extended schema (v36)
- `spec/cooling_ledger_phoenix_v38Omega.json` — v38 spec

**Code:**
- `arifos_core/memory/cooling_ledger.py` — Ledger implementation
- `arifos_core/ledger_hashing.py` — Hash-chain helpers
- `arifos_core/merkle.py` — Merkle tree implementation

**Scripts:**
- `scripts/analyze_governance.py`
- `scripts/verify_ledger_chain.py`
- `scripts/show_merkle_proof.py`
- `scripts/propose_canon_from_receipt.py`
- `scripts/seal_proposed_canon.py`
- `scripts/compute_merkle_root.py`
- `scripts/build_ledger_hashes.py`

---

**END OF DOCUMENT 3**
