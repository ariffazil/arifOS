# F0 SOVEREIGN: The Sovereignty Floor

**Classification:** Constitutional Amendment | **Authority:** Muhammad Arif bin Fazil  
**Status:** ACTIVE | **Seal:** VAULT999

---

## Preamble

F0 SOVEREIGN is the foundation upon which F1-F13 rest. It establishes that the arifOS constitution must be enforceable independent of any external platform, vendor, or infrastructure provider.

> **"The constitution is not a service. It is the operating system."**

---

## The Floor

### F0.1 Definition

**SOVEREIGNTY**: The property of arifOS by which all constitutional floors (F1-F13) remain enforceable without dependency on any single external vendor, platform, or service provider.

### F0.2 The Sovereignty Test

> **"If Microsoft, AWS, Google, OpenAI, and Anthropic simultaneously terminate all service to arifOS, does the constitution still enforce F1-F13?"**

**PASS CRITERIA (by Level):**

| Level | Test Condition | Constitutional Enforcement |
|-------|---------------|---------------------------|
| 0 (Captive) | All external services active | F1-F13 enforced |
| 1 (Portable) | One major provider fails | F1-F13 enforced via fallback |
| 2 (Resilient) | All cloud providers fail | F1-F13 enforced via local backup |
| 3 (Sovereign) | Intentionally local-first | F1-F13 enforced, cloud is augmentation |
| 4 (Absolute) | Air-gapped, no network | F1-F13 enforced identically |

**FAILURE:** Any deployment where F1-F13 enforcement would cease due to vendor action fails F0 SOVEREIGN.

### F0.3 Platform as Contractor

All infrastructure providers (Microsoft, AWS, Google, OpenAI, Anthropic, NVIDIA, Ollama) are classified as **Contractors** under F0:

- They provide services, not authority
- They are interchangeable per the Adapter Bus pattern
- No contractor receives special exemption from constitutional checks
- All contractor code executes within the F12 Injection Guard sandbox

### F0.4 Feature Classification

Every arifOS feature MUST declare its sovereignty level:

```python
@sovereignty_level(3)  # Requires Level 3+ to function
def evaluate_prospect(seismic_data: bytes) -> Verdict:
    """
    F2 Truth enforcement on geological interpretation.
    
    At Level 0-2: Feature requires cloud LLM, may degrade.
    At Level 3-4: Feature uses local LLM, full enforcement.
    """
    pass
```

**888_HOLD Trigger:** If a request targets a feature unavailable at the current sovereignty level, trigger HOLD with explanation:
> "888_HOLD: Feature 'evaluate_prospect' requires sovereignty level 3, current deployment is level 1. Upgrade or request human geoscientist."

### F0.5 Deployment Verification

Every arifOS deployment MUST generate a **Sovereignty Manifest** (see `SovereigntyManifest.json`) that:

1. Declares sovereignty level (0-4)
2. Lists all infrastructure dependencies
3. Provides fallback chains for each subsystem
4. Includes cryptographic checksum for integrity

**Verification Command:**
```bash
arifos verify-sovereignty
# Output: SOVEREIGNITY STAMP
# Identity root: BLS-DID ✓
# LLM path: Azure → Anthropic → Local ✓
# Storage path: Azure Blob → S3 → SQLite ✓
# F1-F13 enforcement: inline ✓
# Sovereignty Level: 3 (Sovereign)
```

### F0.6 The Five Levels

| Level | Name | Definition | Use Case |
|-------|------|------------|----------|
| 0 | **Captive** | Single vendor, no fallback | Development only; experimental features |
| 1 | **Portable** | Multi-cloud with vendor primacy | Standard cloud deployment |
| 2 | **Resilient** | Cloud-primary with local backup | Business continuity required |
| 3 | **Sovereign** | Local-primary, cloud augmentation | **GEOX Production Target** |
| 4 | **Absolute** | Fully air-gapped, no network | VAULT999, classified environments |

### F0.7 Migration Path

Organizations may migrate between levels:

```
Level 0 → Level 1: Add secondary cloud provider
Level 1 → Level 2: Configure local LLM + storage backup
Level 2 → Level 3: Flip primary to local, cloud becomes replica
Level 3 → Level 4: Remove network dependencies entirely
```

**No Downgrade Without Audit:** Migration to lower levels requires explicit 888_HOLD review and VAULT999 logging.

---

## Relationship to F1-F13

F0 SOVEREIGN enables F1-F13 to be **infrastructure-agnostic law**:

- **F1 AMANAH** (Reversibility): Must work on local Docker, not just cloud functions
- **F2 TRUTH** (Evidence): Must validate on local LLM, not just GPT-4
- **F3 TRI-WITNESS** (Human): Must escalate to local UI, not just Teams
- **F7 HUMILITY** (Confidence): Must cap at 0.90 regardless of model provider
- **F13 SOVEREIGN** (Human Override): Must trigger 888_HOLD without cloud APIs

**In short:** F0 ensures F1-F13 are **portable constraints**, not **cloud features**.

---

## Implementation

### Sovereignty Stamp Generator

```python
# arifos/f0_sovereign/stamp.py

class SovereigntyStamp:
    """
    Generates verifiable sovereignty attestations.
    """
    
    def generate(self, deployment_config: dict) -> dict:
        """
        Create sovereignty stamp for deployment.
        """
        level = self._calculate_level(deployment_config)
        
        return {
            "stamp_version": "F0.2026.04",
            "level": level,
            "level_name": self._level_name(level),
            "tests": {
                "identity_self_sovereign": self._test_identity_root(deployment_config),
                "local_llm_available": self._test_local_llm(deployment_config),
                "local_storage_available": self._test_local_storage(deployment_config),
                "air_gap_capable": self._test_air_gap(deployment_config),
                "f1_f13_inline": self._test_constitutional_enforcement(deployment_config)
            },
            "attestation": self._sign_attestation(level),
            "warning": None if level >= 3 else "WARNING: Level < 3 fails F0 for production"
        }
    
    def _calculate_level(self, config: dict) -> int:
        """
        Calculate sovereignty level based on infrastructure.
        """
        score = 0
        
        # Identity
        if config.get('identity', {}).get('root_type') == 'BLS-DID':
            score += 1
        
        # LLM fallback chain
        llm_chain = config.get('infrastructure', {}).get('llm', {}).get('provider_chain', [])
        has_local = any(p.get('provider') in ['Ollama', 'llama.cpp'] for p in llm_chain)
        if has_local:
            score += 1
        
        # Storage
        storage_backends = config.get('infrastructure', {}).get('storage', {}).get('backends', [])
        has_local_storage = any(b.get('type') in ['SQLite', 'Postgres'] for b in storage_backends)
        if has_local_storage:
            score += 1
        
        # Execution
        if config.get('infrastructure', {}).get('execution', {}).get('local_fallback'):
            score += 1
        
        # Air-gap capability
        if config.get('infrastructure', {}).get('llm', {}).get('air_gapped_capable'):
            score += 1
        
        # Map score to level
        if score >= 5:
            return 4  # Absolute
        elif score >= 3:
            return 3  # Sovereign
        elif score >= 2:
            return 2  # Resilient
        elif score >= 1:
            return 1  # Portable
        else:
            return 0  # Captive
```

### CI/CD Integration

```yaml
# .github/workflows/sovereignty-check.yml
name: F0 Sovereignty Check

on: [push, pull_request]

jobs:
  sovereignty:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Test Sovereignty Level 3
        run: |
          arifos verify-sovereignty --target-level 3
          
      - name: Fail if Captive Dependencies
        run: |
          if grep -r "from azure" arifos/core; then
            echo "ERROR: Core has vendor imports"
            exit 1
          fi
          if grep -r "from openai" arifos/core; then
            echo "ERROR: Core has vendor imports"
            exit 1
          fi
```

---

## Compliance Statement

**All arifOS deployments claiming production readiness MUST:**

1. Declare sovereignty level in `SovereigntyManifest.json`
2. Maintain Level 3 (Sovereign) or higher for GEOX production
3. Maintain Level 4 (Absolute) for VAULT999 operations
4. Pass `arifos verify-sovereignty` in CI/CD pipeline
5. Log all sovereignty level changes to VAULT999

**Violations:** Deployments below Level 3 in production trigger automatic 888_HOLD for high-risk operations.

---

## Seal

**VAULT999** | **F0 SOVEREIGN ACTIVE** | **ΔΩΨ**

*"The constitution does not run in the cloud. It runs in the kernel."*
