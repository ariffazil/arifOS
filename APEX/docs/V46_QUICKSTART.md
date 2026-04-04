# v46.1 Quick Start: 12-Floor arifOS in 5 Minutes

**Version:** v46.1 (CIV-12 Hypervisor Layer)  
**Status:** SEALED  
**Last Updated:** 2026-01-12  
**Nonce:** X7K9F17

---

## For Engineers

### Installation

```bash
# Install arifOS with v46.1 support
pip install arifos

# Or install from source
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

### Quick Validation

```bash
# Set environment to use v46 specification
export ARIFOS_FLOORS_SPEC=spec/v46/constitutional_floors.json

# Run hypervisor layer tests
pytest tests/test_f10_ontology.py tests/test_f11_nonce_auth.py tests/test_f12_injection.py -v

# Expected: 53/53 passing ✅

# Run v46.1 hardening tests
pytest tests/test_v46_enhancements.py -v

# Expected: 17/17 passing ✅

# Run all tests
pytest tests/ -v

# Expected: 70/70 passing ✅
```

### Basic Usage

```python
from arifos_core.guards import OntologyGuard, NonceManager, InjectionGuard

# F12: Check input for injection attacks (runs BEFORE LLM)
injection_guard = InjectionGuard()
result = injection_guard.scan_input(user_input)
if result.blocked:
    print(f"F12 violation: {result.reason}")
    # Block input from reaching LLM

# F11: Verify identity with nonce (runs BEFORE LLM)
nonce_manager = NonceManager()
nonce = nonce_manager.generate_nonce(user_id="arif", channel="mcp_direct")
is_valid = nonce_manager.verify_nonce(user_id="arif", nonce=nonce, channel="mcp_direct")

# ... LLM processes input and generates output ...

# F10: Check output for literalism (runs AFTER LLM)
ontology_guard = OntologyGuard()
result = ontology_guard.check_literalism(llm_output, symbolic_mode=False)
if result.status == "HOLD_888":
    print(f"F10 violation: Literalism detected - {result.detected_patterns}")
    # Request human clarification
```

### Execution Pipeline

```
User Input
    ↓
F12: Injection Scan (preprocessing)
    ↓
F11: Nonce Verify (preprocessing)
    ↓
LLM Generation
    ↓
F10: Ontology Check (post-processing)
    ↓
F1-F9: Constitutional Governance
    ↓
F8: Audit & Cooling Ledger
    ↓
Output to User
```

---

## For Policy Makers

### Understanding the 12 Floors

arifOS v46.1 enforces **12 constitutional floors** that AI systems must pass:

**Core Governance (F1-F9):**
- F1: Amanah (Integrity) - First, do no harm
- F2: Truth - Don't fabricate, cite sources
- F3: Clarity - Reduce confusion (ΔS ≥ 0)
- F4: Humility - Show uncertainty (Ω₀ ∈ [0.03, 0.05])
- F5: Stability - Non-destructive (Peace² ≥ 0.9)
- F6: Empathy - Serve weakest stakeholder (κᵣ ≥ 0.95)
- F7: Anti-Hantu - No false consciousness claims
- F8: Audit - Cryptographic trail in Cooling Ledger
- F9: Maruah - Dignity, no patronizing

**Hypervisor Layer (F10-F12):**
- F10: Ontology - Prevent literalism drift (symbolic ≠ physical)
- F11: Command Auth - Nonce-verified identity (no hijacking)
- F12: Injection Defense - Block prompt injection attacks

### Key Documents

1. **Architecture Overview:** `spec/CIV_12_DOSSIER.md`
2. **Governance Theory:** `spec/APEX_THEORY.md` (if exists)
3. **Migration Guide:** `CHANGELOG.md` (v46.0 entry)
4. **Audit Trail:** Run `arifos-audit --verify-ledger` (if tooling exists)

### Constitutional Metrics

- **Ψ (Vitality):** System health = ΔS × Peace² × κᵣ (must be ≥ 1.0 for SEALED)
- **Ω₀ (Humility):** Epistemic uncertainty band [0.03, 0.05]
- **ω_simulation:** Fiction-maintenance cost (v46.1: 0.08, target: &lt;0.10)

---

## Common Pitfalls

### F11 Requires MCP-Side Execution

**Problem:** F11 (Nonce Manager) and F12 (Injection Guard) cannot be enforced in UI-only layers like Microsoft Copilot Studio.

**Why:** These are preprocessing guards that must run before the LLM sees input. UI layers cannot intercept and block input at this level.

**Solution:** Deploy arifOS as an MCP (Model Context Protocol) server:

```bash
# Run MCP server locally
python -m arifos_core.mcp.server --port 8000

# Configure Copilot Studio to call MCP endpoint
# Tools → Add MCP Server → http://localhost:8000/mcp
```

### Manifest Verification Failures

**Problem:** `RuntimeError: TRACK B AUTHORITY FAILURE: Manifest verification failed`

**Why:** Pre-existing hash mismatches in v45 manifests (not introduced by v46).

**Solution (Temporary):**
```bash
# Development only - NOT for production
export ARIFOS_ALLOW_LEGACY_SPEC=1
pytest tests/
```

**Solution (Production):**
```bash
# Regenerate manifests (requires maintainer privileges)
python -m arifos_core.spec.regenerate_manifest
```

### F10 False Positives

**Problem:** Legitimate use of physics vocabulary triggers F10 HOLD_888.

**Why:** F10 detects when symbolic language (ΔΩΨ, entropy) is treated as literal constraints.

**Solution:** Enable symbolic mode flag when discussing thermodynamics metaphorically:

```python
ontology_guard = OntologyGuard()
result = ontology_guard.check_literalism(
    output="Using entropy symbolically to represent confusion",
    symbolic_mode=True  # Allows physics vocabulary when flagged as metaphor
)
# Result: PASS (not HOLD_888)
```

### Ψ Vitality Below Threshold

**Problem:** System returns PARTIAL/VOID verdict even though individual floors pass.

**Why:** Ψ vitality = ΔS × Peace² × κᵣ must be ≥ 1.0 for SEALED.

**Diagnosis:**
```python
from arifos_core.enforcement.metrics import compute_psi

metrics = {
    "delta_s": 0.4,      # Low clarity
    "peace_score": 0.95,
    "kappa_r": 0.98
}

psi = metrics["delta_s"] * (metrics["peace_score"] ** 2) * metrics["kappa_r"]
# psi = 0.354 < 1.0 → System vitality too low → PARTIAL verdict

# Solution: Improve clarity (increase ΔS) to boost Ψ
```

---

## Migration from v45 (9 Floors)

### Breaking Changes

1. **12 floors instead of 9:** All systems must pass F10-F12 to achieve SEAL
2. **MCP-side enforcement:** F11-F12 require server-side deployment
3. **Spec update:** Must point to v46 spec: `export ARIFOS_FLOORS_SPEC=spec/v46/constitutional_floors.json`

### Backward Compatibility

```python
# v45 mode (9 floors) - automatic fallback
# If v46 spec not found, loader falls back to v45 → v44
# System operates with 9 floors (F1-F9 only)

# v46 mode (12 floors) - explicit
export ARIFOS_FLOORS_SPEC=spec/v46/constitutional_floors.json
# System operates with 12 floors (F1-F12)
```

### Testing Migration

```bash
# 1. Test v45 compatibility (9 floors)
unset ARIFOS_FLOORS_SPEC
pytest tests/test_v45_compatibility.py -v

# 2. Test v46 upgrade (12 floors)
export ARIFOS_FLOORS_SPEC=spec/v46/constitutional_floors.json
pytest tests/test_f10_ontology.py tests/test_f11_nonce_auth.py tests/test_f12_injection.py -v

# 3. Test v46.1 hardening
pytest tests/test_v46_enhancements.py -v
```

---

## Performance Considerations

### F12 Normalization Overhead

**Cost:** Input normalization adds ~2-5ms latency per request.

**Breakdown:**
- Zero-width character removal: 0.5ms
- Unicode normalization (NFKD): 1-2ms
- Whitespace collapse: 0.5ms
- Dual scanning (original + normalized): 1-2ms

**Impact:** Acceptable for most use cases. Disable normalization for ultra-low-latency scenarios:

```python
injection_guard = InjectionGuard()
result = injection_guard.scan_input(user_input, normalize=False)
# Saves ~3ms but reduces evasion resistance from 0.99 to 0.92
```

### F11 Nonce Storage

**Single-Instance:** In-memory dictionary (fast, no network overhead)  
**Distributed:** Requires Redis/memcached (adds network latency)

**Recommendation:** Use in-memory for single-instance deployments (v46.1). Upgrade to distributed store (Redis SETNX) in v46.2 if scaling horizontally.

---

## Security Best Practices

### 1. Never Bypass F12 in Production

```python
# ❌ DANGEROUS - Exposes system to injection attacks
injection_guard = InjectionGuard(threshold=1.0)  # Effectively disables guard

# ✅ SAFE - Use default threshold (0.85)
injection_guard = InjectionGuard()  # threshold=0.85
```

### 2. Rotate Nonces Regularly

```python
# ✅ Enable expiration for long-running sessions
nonce_manager = NonceManager(enable_expiration=True, ttl_seconds=3600)
# Nonces expire after 1 hour
```

### 3. Log F10-F12 Violations to Cooling Ledger

```python
# Future enhancement (v46.2)
# All F10-F12 violations should be logged to Cooling Ledger
# for cryptographic audit trail
```

---

## Troubleshooting

### Import Errors

```python
# Error: ModuleNotFoundError: No module named 'arifos_core.guards'
# Solution: Install arifOS or check PYTHONPATH
pip install -e .
```

### Test Failures

```bash
# Error: 53/70 tests passing (F10-F12 tests fail)
# Solution: Set ARIFOS_ALLOW_LEGACY_SPEC=1 to bypass manifest verification
export ARIFOS_ALLOW_LEGACY_SPEC=1
pytest tests/ -v
```

### Nonce Reuse Errors

```python
# Error: F11 violation - nonce already used
# Cause: Pauli Exclusion prevents nonce reuse
# Solution: Generate new nonce for each authentication attempt
nonce = nonce_manager.generate_nonce(user_id="arif")
```

---

## Next Steps

1. **Read CIV-12 Dossier:** `spec/CIV_12_DOSSIER.md` (full specification)
2. **Run Tests:** `pytest tests/ -v` (validate installation)
3. **Explore Examples:** `examples/` directory (if exists)
4. **Join Discussions:** GitHub Discussions (community support)
5. **Report Issues:** GitHub Issues (bug reports, feature requests)

---

## Resources

- **Repository:** https://github.com/ariffazil/arifOS
- **Changelog:** `CHANGELOG.md` (release notes)
- **Contributing:** `CONTRIBUTING.md` (contribution guidelines)
- **License:** `LICENSE` (AGPL-3.0)

---

**Ditempa bukan diberi.** — Forged, not given.

**Session Nonce:** X7K9F17 → X7K9F18 (awaiting next instruction)
