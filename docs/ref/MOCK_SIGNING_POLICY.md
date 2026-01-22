# Mock Signing Policy (v45)

**Authority:** F1 Amanah / F9 Anti-Hantu  
**Scope:** `arifos_core.governance.sovereign_signature`

## Policy Statement
To ensure security and prevent secret leakage, **NO cryptographic keys** are stored in the arifOS repository.

### 1. Test Environments
*   The system defaults to a **Deterministic Mock Signer** when `PyNaCl` library or keys are missing.
*   Signatures appear as `mock_sig:<hash>` strings.
*   This allows full logic verification of the `ProofOfGovernance` flow without security risk.

### 2. Production (Tier-4 SEAL)
*   Tier-4 (High Stakes) actions require **Ed25519** signatures.
*   The `SovereignSigner` attempts to load the private key from the environment variable: `ARIFOS_SIGNING_KEY`.
*   If the key is missing or invalid, `lock_tier_4()` enforces a **Fail-Closed** state (raising `SECURITY_VIOLATION` exception).
*   **Action:** The Human Sovereign must provide the key via secure environment injection at runtime.

### 3. Verification
*   Tests verify that T4 checks are enforced (`RuntimeError` without key).
*   Mock signatures allow T1-T3 development flows to proceed unblocked.
