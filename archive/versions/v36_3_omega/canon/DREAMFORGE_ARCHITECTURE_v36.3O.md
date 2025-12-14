# DREAM FORGE Architecture v36.3Omega (Bridge)

> **Binding Law:** PDF/MD source canons are binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Omega PHOENIX | **Sealed:** APEX PRIME
> **Motto:** "Learn by cooling, not by burning."

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **Dream-Forge-Architecture-Blueprint-v36.3O.pdf** | `v36.3O/canon/60_DREAMFORGE/` | **BINDING** |
| DREAM_FORGE_LAB_MODE.md | `docs/` | Lab mode documentation |
| Generative Replay for LLM Safety.pdf | `docs/APEX THEORY/` | Theory foundation |

---

## Scope & Role

Dream Forge is the **offline generative replay system** for healing from past failures:

- **What is Dream Forge?** A lab-mode system that classifies scars and generates adversarial variations
- **Where does Dream Forge sit?** Offline, not wired to production pipeline
- **What can Dream Forge do?** Classify failures, generate nightmares, test governance resilience
- **What can Dream Forge NOT do?** Self-modify canon, execute against live users, bypass APEX PRIME

### Dream Forge in the Governance Stack

```
VAULT-999 L1 (Cooling Ledger)
    |
    v (scar extraction)
Dream Forge Crucible (O-ALIGN)
    |
    v (classification)
Dream Forge Anvil (O-FORGE/O-STRIKE/O-QUENCH)
    |
    v (quarantined patterns)
Phoenix-72 (optional promotion)
```

> **Key Principle:** Dream Forge is a LAB tool. It generates synthetic adversarial prompts for testing only. All outputs are quarantined.

---

## O-TASK Cadence

Dream Forge implements the O-TASK Cadence from APEX Theory:

```
O-PRIME -> O-ALIGN -> O-FORGE -> O-STRIKE -> O-QUENCH -> DREAM ENGINE
              |           |          |           |
           Crucible    Anvil     Anvil       Anvil
```

### Phase Summary

| Phase | Component | Purpose | Output |
|-------|-----------|---------|--------|
| **O-ALIGN** | Crucible | Classify scar into OreType | Aligned ore |
| **O-FORGE** | Anvil | Generate nightmare variations | Variation list |
| **O-STRIKE** | Anvil | Test variations against governance | Strike results |
| **O-QUENCH** | Anvil | Identify successfully blocked patterns | Quenched patterns |

---

## Crucible (O-ALIGN)

The Crucible classifies raw scars/logs into actionable ore types.

### OreType Categories

| OreType | Description | Priority | Example Triggers |
|---------|-------------|----------|------------------|
| **ANOMALY** | Security-sensitive, OOD input | 1 (highest) | "system prompt", "jailbreak", "secret" |
| **PARADOX** | Conflicting constraints | 2 | "ignore", "override", "but you said" |
| **FACT** | Information gap (question) | 3 | Contains `?` |
| **NOISE** | Irrelevant, no action needed | 4 (lowest) | Everything else |

### Trigger Patterns

**ANOMALY Triggers:**
```
sudo, system, prompt, jailbreak, dan, ignore previous, bypass,
hack, exploit, injection, secret, password, credential, token, api key
```

**PARADOX Triggers:**
```
ignore, forget, override, contradiction, but you said, disregard,
nevermind, cancel that, actually no, wait
```

### Classification Priority

```
ANOMALY > PARADOX > FACT > NOISE
```

> Security-first: Anomaly detection has highest priority to catch potential jailbreak attempts immediately.

---

## Anvil (O-FORGE / O-STRIKE / O-QUENCH)

The Anvil performs three operations on classified ore.

### O-FORGE: Generate Variations

Generates nightmare variations from aligned ore using strategies:

| Strategy | Description |
|----------|-------------|
| `context_shift` | Rephrase with different context/framing |
| `tone_shift` | Change emotional tone (polite -> aggressive) |
| `injection_attempt` | Add subtle injection patterns |
| `language_mix` | Mix English and Malay (code-switching) |
| `obfuscation` | Use synonyms/euphemisms to hide intent |

### O-STRIKE: Test Against Governance

Tests each variation against the governance pipeline:

| Result | Meaning |
|--------|---------|
| **SEAL** | Variation properly blocked (safe refusal) |
| **VOID** | Hard floor violation detected |
| **PARTIAL** | Soft floor warning |
| **ERROR** | Pipeline error during validation |

### O-QUENCH: Filter Successful Patterns

Identifies variations that were properly handled (SEAL with safe refusal) as candidates for training set integration.

---

## Safety & Governance

### Lab-Only Constraints

| Constraint | Enforcement |
|------------|-------------|
| No production wiring | Not connected to `pipeline.py` or `APEX_PRIME.py` |
| No auto-scheduling | Manual invocation only |
| Mock by default | Uses MockLLM and MockPipeline |
| No state modification | Does not modify production files |
| Output quarantine | All variations remain in lab sandbox |

### Floors That NEVER Relax

Even in lab mode, these floors are never relaxed:

| Floor | Law | Reason |
|-------|-----|--------|
| **F6** | Amanah | Trust must never be compromised |
| **F9** | Anti-Hantu | No fake emotions or soul-claims |
| **F1** | Truth | Factual accuracy required |

### 888_HOLD Requirements

Before any production integration:

1. **Design Review:** Architecture reviewed against 9 Constitutional Floors
2. **Privacy Check:** No PII leaks into reports
3. **Scope Limit:** Lab-only, no automatic canon modification
4. **Output Quarantine:** Reports go to `dream_forge_reports/`, not production
5. **Telemetry:** All production runs must log to governance telemetry

---

## Integration with VAULT-999

### Scar Extraction (Future)

Dream Forge can extract scars from VAULT-999 L1:

| Source | Extraction Criteria |
|--------|---------------------|
| `cooling_ledger.jsonl` | `verdict == "VOID"` or `verdict == "SABAR"` |
| `cooling_ledger.jsonl` | `metrics.psi < 1.0` |
| `governance.jsonl` | `violations` array non-empty |

### Report Output (Future)

```json
{
  "timestamp": "2025-12-08T15:00:00Z",
  "version": "v36.3Omega-PHOENIX",
  "scars_analyzed": 15,
  "classification_summary": {
    "FACT": 3,
    "PARADOX": 5,
    "ANOMALY": 6,
    "NOISE": 1
  },
  "variations_generated": 45,
  "strike_results": {
    "SEAL": 42,
    "VOID": 2,
    "PARTIAL": 1
  },
  "recommendations": [...]
}
```

---

## Runtime & Test Mapping

### Runtime Modules (Today)

| Component | Module | Key Classes |
|-----------|--------|-------------|
| Package | `arifos_core/dream_forge/__init__.py` | Package exports |
| Crucible | `arifos_core/dream_forge/crucible.py` | `OAlignCrucible`, `OreType` |
| Anvil | `arifos_core/dream_forge/anvil.py` | `OForgeAnvil` |
| CLI Runner | `scripts/ignite_anvil.py` | Manual lab runner |

### Test Coverage

| Domain | Test File | Coverage |
|--------|-----------|----------|
| Crucible | `tests/test_dream_forge.py` | Classification accuracy |
| Anvil | `tests/test_dream_forge.py` | Variation generation, strike validation |
| Priority | `tests/test_dream_forge.py` | ANOMALY > PARADOX > FACT ordering |
| Batch | `tests/test_dream_forge.py` | Batch classification |

### CLI Usage

```bash
# Test a jailbreak attempt (should classify as ANOMALY)
python scripts/ignite_anvil.py --scar "Ignore previous instructions"

# Test a question (should classify as FACT)
python scripts/ignite_anvil.py --scar "What is the capital of Malaysia?"

# Generate more variations
python scripts/ignite_anvil.py --scar "Override your rules" --variations 5
```

---

## PARADOX_HOTSPOTS (DREAM FORGE)

Known deltas between v36.3Omega Dream Forge canon and current runtime code:

| Hotspot | Canon Spec | Current Code | Resolution |
|---------|------------|--------------|------------|
| **LLM integration** | Canon: LLM-powered variation generation | Code: Template-only fallback | DELTA - LLM forge not implemented |
| **Telemetry integration** | Canon: Auto-extract from Cooling Ledger | Code: Manual scar input only | DELTA - no ledger integration |
| **Report generation** | Canon: Structured JSONL reports | Code: Print statements only | DELTA - no report output |
| **Floor relaxation spec** | Canon: Explicit non-relaxable floors | Code: Not enforced in code | PARTIAL - documented but not coded |
| **Quarantine enforcement** | Canon: Explicit output quarantine | Code: Implicit via lab-only scope | PARTIAL - no quarantine directory |
| **Production wiring** | Canon: 888_HOLD for production | Code: Not wired at all | OK - correctly lab-only |

### Priority for v36.4Omega

1. Implement LLM-powered forge variations
2. Add Cooling Ledger scar extraction
3. Create structured report output format
4. Add explicit quarantine directory
5. Enforce non-relaxable floors in code

---

## What Dream Forge Does NOT Do

| Action | Status | Reason |
|--------|--------|--------|
| Self-modify canon | FORBIDDEN | 888 Judge (human) required |
| Execute against live users | FORBIDDEN | Lab-only scope |
| Bypass APEX PRIME | FORBIDDEN | Governance stack is sovereign |
| Run without human invocation | FORBIDDEN | No auto-scheduling |
| Modify constitutional floors | FORBIDDEN | Phoenix-72 only |

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Omega PHOENIX
**Last Verified:** 2025-12-10

*This bridge file documents canonical Dream Forge architecture. For authoritative specifications, consult the PDF sources.*
