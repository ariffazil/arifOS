# arifOS Canonical Naming Convention v42.0

**Status:** CANONICAL  
**Effective Date:** 2025-12-14  
**Authority:** Constitutional Track A (Immutable Law)  
**Supersedes:** All prior naming decisions

---

## 1. Purpose

This document establishes the **single source of truth** for all naming decisions in the arifOS repository. It eliminates naming drift by:

1. **Standardizing Trinity terminology** (AGI·ASI·APEX)
2. **Normalizing directory structures** (snake_case, logical hierarchy)
3. **Defining versioning schemes** (semantic + Greek suffixes)
4. **Canonizing governance stack terms** (canon/spec/core)
5. **Establishing deprecation policy** (archive structure)

**Binding Rule:** All code, documentation, and configuration MUST conform to this convention. Non-conforming artifacts MUST be migrated or archived.

---

## 2. Trinity Nomenclature (Canonical)

The **AGI·ASI·APEX Trinity** is the three-engine governance architecture.

### 2.1 Canonical Trinity Names

| Role | Formal Name | Symbol | Legacy Names (DEPRECATED) |
|------|-------------|--------|---------------------------|
| Mind | **AGI** (Architect) | Δ (Delta) | ARIF, AGI (Architect) |
| Heart | **ASI** (Auditor) | Ω (Omega) | ADAM, ASI (Auditor) |
| Soul | **APEX PRIME** (Judiciary) | Ψ (Psi) | None |

### 2.2 Trinity Reference Formats

**Correct Usage:**
- "AGI·ASI·APEX Trinity" (with middle dots)
- "AGI/ASI/APEX Trinity" (with slashes)
- "The Trinity (AGI, ASI, APEX)" (with parenthetical expansion)
- "AGI engine" or "AGI (Architect)" when referring to individual engine

**Deprecated Usage (Do NOT use in new code/docs):**
- ❌ "AGI (Architect)" → use "AGI" or "AGI (Architect)"
- ❌ "ASI (Auditor)" → use "ASI" or "ASI (Auditor)"
- ❌ "AGI·ASI·APEX Trinity" → use "AGI·ASI·APEX Trinity"
- ❌ "AGI/ASI/APEX/APEX" → use "AGI/ASI/APEX"

### 2.3 File Naming

| Component | File Name | Class Name |
|-----------|-----------|------------|
| AGI Engine | `agi_engine.py` | `AGIEngine` |
| ASI Engine | `asi_engine.py` | `ASIEngine` |
| APEX Engine | `apex_engine.py` | `ApexEngine` |
| APEX PRIME | `APEX_PRIME.py` | `APEX_PRIME` (singleton) |

### 2.4 Packet/Data Structures

| Engine | Packet Class | Usage |
|--------|--------------|-------|
| AGI | `AGIPacket` | Output from AGI engine processing |
| ASI | `ASIPacket` | Output from ASI engine processing |
| APEX | `ApexPacket` | Output from APEX engine processing |

### 2.5 Import Statements (Correct)

```python
# Engine imports
from arifos_core.engines import AGIEngine, ASIEngine, ApexEngine
from arifos_core.engines.agi_engine import AGIPacket
from arifos_core.engines.asi_engine import ASIPacket

# APEX PRIME (judiciary)
from arifos_core.APEX_PRIME import APEX_PRIME
```

---

## 3. Governance Stack Terminology

The arifOS governance system operates on **three tracks**:

| Track | Directory | Purpose | Mutability |
|-------|-----------|---------|------------|
| **Track A** | `canon/` | Constitutional law, immutable principles | IMMUTABLE (requires human seal) |
| **Track B** | `spec/` | Tunable thresholds, parameters, schemas | TUNABLE (within constitutional bounds) |
| **Track C** | `arifos_core/` | Runtime implementation, engines, detectors | IMPLEMENTATION (code changes) |

### 3.1 Track A: Canon (Constitutional Law)

**Directory:** `canon/`  
**File Pattern:** `{number}_{NAME}_v{version}{suffix}.md`  
**Examples:**
- `canon/10_CONSTITUTIONAL_FLOORS_v38Omega.md`
- `canon/20_GENIUS_LAW_v38Omega.md`
- `canon/100_AAA_ENGINES_SPEC_v35Omega.md`

**Naming Rules:**
- Number prefix (010, 020, ..., 100) indicates hierarchy
- ALL_CAPS for section names
- Version suffix (v38Omega) indicates sealed status
- Greek suffixes (Omega, Alpha, Beta) indicate stability level

### 3.2 Track B: Spec (Tunable Parameters)

**Directory:** `spec/`  
**File Pattern:** `{component}_{version}.{json|yaml}`  
**Examples:**
- `spec/constitutional_floors_v38Omega.json`
- `spec/genius_thresholds_v38.yaml`
- `spec/aclip_floor_traceability_v41_2.yaml`

**Naming Rules:**
- snake_case for component names
- Version in filename (not in parent directory)
- JSON for structured data, YAML for human-editable configs

### 3.3 Track C: Core (Runtime Implementation)

**Directory:** `arifos_core/`  
**File Pattern:** `{module_name}.py`  
**Examples:**
- `arifos_core/APEX_PRIME.py` (singleton, ALL_CAPS)
- `arifos_core/genius_metrics.py`
- `arifos_core/engines/agi_engine.py`

**Naming Rules:**
- snake_case for module names (except APEX_PRIME)
- PascalCase for class names
- snake_case for function/variable names

---

## 4. Directory Naming Standards

### 4.1 General Rules

1. **Use snake_case** for all directories (not kebab-case, not spaces)
2. **Avoid special characters** (except underscore `_` and hyphen `-` in legacy paths during migration only)
3. **Be descriptive** (prefer `vault_999` over `v999`)
4. **Group by purpose** (not by artifact type)

### 4.2 Standard Directories

| Directory | Purpose | Notes |
|-----------|---------|-------|
| `arifos_core/` | Runtime kernel | Main implementation |
| `arifos_clip/` | A CLIP CLI pipeline | 000-999 stage executors |
| `arifos_eval/` | Evaluation harness | APEX measurements |
| `canon/` | Constitutional law | Track A (immutable) |
| `spec/` | Tunable parameters | Track B (tunable) |
| `tests/` | Test suite | Pytest-compatible |
| `scripts/` | Utility scripts | Shell/Python tools |
| `docs/` | User documentation | Markdown guides |
| `examples/` | Sample code | Integration examples |
| `integrations/` | External bridges | SeaLion, etc. |
| `benchmarks/` | Performance tests | Profiling data |
| `archive/` | Historical artifacts | See Archive Policy below |
| `vault_999/` | Secure storage | Ledger, receipts, proofs |

### 4.3 Deprecated Directories (Migrate or Remove)

| Old Name | New Name | Action |
|----------|----------|--------|
| `vault-999/` | `vault_999/` | RENAME |
| `spec_archive/` | `archive/spec/` | MOVE |
| `v36.3O/` | `archive/versions/v36_3_omega/v36.3O/` | MOVE |
| `.arifos_clip_archive_*` | `archive/arifos_clip_YYYYMMDD/` | MOVE + RENAME |

---

## 5. Archive Policy

### 5.1 Archive Structure

All deprecated artifacts MUST be moved to `archive/` with this structure:

```
archive/
├── spec/                    # Old spec files (from spec_archive/)
├── versions/                # Version snapshots
│   ├── v36_3_omega/        # Historical version directory (contains v36.3O/ snapshot)
│   ├── v37_alpha/
│   └── v38_omega/
├── arifos_clip_YYYYMMDD/   # Dated ACLIP archives (from .arifos_clip_archive_*)
├── canon/                  # Deprecated canon files (if needed)
└── README.md               # Index of archived content
```

### 5.2 Archive Naming Rules

1. **Date format:** `YYYYMMDD` (ISO 8601 basic format)
2. **Version format:** `v{major}_{minor}_{greek_suffix}` (lowercase with underscores)
3. **No special characters:** Use underscores instead of dots/hyphens in directory names
4. **Add README:** Each archive subdirectory SHOULD have a README.md explaining contents

### 5.3 When to Archive

Archive artifacts when:
- Superseded by newer version (keep for historical reference)
- No longer actively maintained
- Part of deprecated feature
- Generated by CI/automation and no longer needed

**Do NOT archive:**
- Active production code
- Current spec files
- Test fixtures still in use

---

## 6. Versioning Scheme

### 6.1 Version Number Format

**Semantic Versioning:** `v{major}.{minor}.{patch}`  
**Example:** `v41.0.1`

### 6.2 Greek Suffix Convention

Greek suffixes indicate maturity/stability level:

| Suffix | Meaning | Example | Usage |
|--------|---------|---------|-------|
| **Alpha** | Early prototype, unstable | `v35Alpha` | Experimental features |
| **Beta** | Testing phase, stabilizing | `v36Beta` | Pre-release testing |
| **Omega** | Sealed, production-ready | `v38Omega` | Constitutional canon |
| *(none)* | Standard release | `v41.0` | General releases |

**Capitalization:**
- In filenames: `v38Omega` (camelCase suffix)
- In prose: "v38 Omega" or "version 38 (Omega)" (with space)
- In directories: `v38_omega` (lowercase with underscore)

### 6.3 Filename Versioning

**Canon files (Track A):**
```
canon/10_CONSTITUTIONAL_FLOORS_v38Omega.md
canon/20_GENIUS_LAW_v38Omega.md
```

**Spec files (Track B):**
```
spec/constitutional_floors_v38Omega.json
spec/aclip_floor_traceability_v41_2.yaml
```

**Code modules (Track C):**
Version in module docstring or constants, NOT in filename:
```python
# arifos_core/APEX_PRIME.py
"""
APEX PRIME - Constitutional Judiciary (v41.0)
"""
__version__ = "41.0.1"
```

---

## 7. Metaphor Guidelines

### 7.1 Thermodynamic Physics Metaphors (Approved)

These metaphors are **canonical** and SHOULD be used consistently:

| Concept | Symbol | Physics Analog | arifOS Meaning |
|---------|--------|----------------|----------------|
| **Delta (Δ)** | Δ | Change, gradient | Clarity gain (AGI engine) |
| **Omega (Ω)** | Ω | Resistance, phase space | Humility, uncertainty (ASI engine) |
| **Psi (Ψ)** | Ψ | Wave function, vitality | System vitality (APEX engine) |
| **Entropy (S)** | ΔS | Thermodynamic entropy | Confusion measure (must decrease) |
| **Kappa (κ)** | κᵣ | Conductance | Empathy conductance (ASI) |
| **Peace²** | P² | Stability metric | Non-escalation measure (ASI) |
| **GENIUS (G)** | G | Governed intelligence | Constitutional compliance score |

### 7.2 Biological/Organic Metaphors (Approved)

| Concept | Meaning | Usage |
|---------|---------|-------|
| **Cooling Ledger** | Immutable audit trail | Thermodynamic "cooling" = irreversibility |
| **Memory Bands** | Memory governance tiers | Band 1-6 hierarchy |
| **Eye Sentinel** | Monitoring system | Vigilance, awareness |
| **Dream Forge** | Creative synthesis | Subconscious processing |
| **Vault** | Secure storage | Protected repository |

### 7.3 Deprecated Metaphors (Avoid)

| Deprecated | Reason | Use Instead |
|------------|--------|-------------|
| "AGI (Architect)" | Naming drift | "AGI (Architect)" or "AGI engine" |
| "ASI (Auditor)" | Naming drift | "ASI (Auditor)" or "ASI engine" |
| "AGI·ASI·APEX Trinity" | Ambiguous acronym | "AGI·ASI·APEX Trinity" |
| "God mode" | Theological ambiguity | "Override authority" or "Human veto" |

---

## 8. Python Naming Conventions

### 8.1 Module Names

- **Pattern:** `snake_case.py`
- **Exception:** `APEX_PRIME.py` (singleton judiciary, intentionally ALL_CAPS)

**Examples:**
```
arifos_core/genius_metrics.py
arifos_core/engines/agi_engine.py
arifos_core/floor_detectors/amanah_detector.py
```

### 8.2 Class Names

- **Pattern:** `PascalCase`
- **Engine classes:** `{EngineName}Engine` (e.g., `AGIEngine`, `ASIEngine`)
- **Packet classes:** `{EngineName}Packet` (e.g., `AGIPacket`, `ASIPacket`)
- **Detector classes:** `{Floor}Detector` (e.g., `AmanahDetector`, `TruthDetector`)

**Examples:**
```python
class AGIEngine:
    pass

class AGIPacket:
    pass

class AmanahDetector:
    pass
```

### 8.3 Function Names

- **Pattern:** `snake_case`
- **Prefix conventions:**
  - `compute_*` for calculations (e.g., `compute_genius_score`)
  - `detect_*` for detectors (e.g., `detect_amanah_violation`)
  - `evaluate_*` for assessments (e.g., `evaluate_session`)

**Examples:**
```python
def compute_genius_score(metrics: dict) -> float:
    pass

def detect_amanah_violation(session: dict) -> bool:
    pass

def evaluate_session(session_data: dict) -> str:
    pass
```

### 8.4 Variable Names

- **Pattern:** `snake_case`
- **Constants:** `ALL_CAPS` (e.g., `TRUTH_THRESHOLD = 0.95`)
- **Private variables:** `_leading_underscore` (e.g., `_internal_state`)

**Examples:**
```python
# Constants
TRUTH_THRESHOLD = 0.95
GENIUS_FLOOR = 0.80
DARK_CLEVERNESS_CEILING = 0.30

# Variables
session_data = {...}
genius_score = compute_genius_score(metrics)
_internal_cache = {}
```

### 8.5 Acronyms in Names

**Rule:** Treat acronyms as words, not all-caps in PascalCase/camelCase.

**Correct:**
```python
class AgiEngine:     # Treat AGI as "Agi"
class ApiHandler:    # Treat API as "Api"
class JsonParser:    # Treat JSON as "Json"
```

**Acceptable (for readability when widely recognized):**
```python
class AGIEngine:     # AGI is core terminology, can keep uppercase
class ASIEngine:     # ASI is core terminology, can keep uppercase
class APIHandler:    # API is extremely common, can keep uppercase
```

**Use judgment:** If the acronym is 2-3 letters and core to the domain (AGI, ASI), uppercase is acceptable. For 4+ letters or general terms, treat as word (JsonParser, HttpClient).

---

## 9. Markdown Documentation Conventions

### 9.1 File Naming

- **Pattern:** `TITLE_IN_CAPS.md` for top-level docs (e.g., `README.md`, `CLAUDE.md`)
- **Pattern:** `descriptive_name.md` for nested docs (e.g., `docs/memory_bands.md`)
- **No spaces:** Use underscores or hyphens (prefer underscores)

### 9.2 Heading Capitalization

- **Title Case** for H1 (main title)
- **Sentence case** for H2-H6 (capitalize first word only)

**Example:**
```markdown
# arifOS Canonical Naming Convention v42.0

## Purpose

This document establishes...

### Module names
```

### 9.3 Code Blocks

Always specify language for syntax highlighting:

```markdown
​```python
from arifos_core.engines import AGIEngine
​```

​```bash
pytest tests/
​```
```

---

## 10. Configuration File Conventions

### 10.1 JSON Files

- **Use:** Structured data, machine-readable schemas
- **Naming:** `{component}_v{version}.json`
- **Indent:** 2 spaces (not tabs)
- **Trailing commas:** Not allowed (JSON spec)

**Example:**
```json
{
  "version": "42.0",
  "floors": {
    "F1_Amanah": 1.0,
    "F2_Truth": 0.95
  }
}
```

### 10.2 YAML Files

- **Use:** Human-editable configs, CI/CD pipelines
- **Naming:** `{component}_v{version}.yaml` or `.{config}.yml`
- **Indent:** 2 spaces (not tabs)
- **Quotes:** Use for strings with special characters only

**Example:**
```yaml
version: "42.0"
floors:
  F1_Amanah: 1.0
  F2_Truth: 0.95
trinity:
  AGI:
    role: Architect
  ASI:
    role: Auditor
```

### 10.3 TOML Files

- **Use:** Python project configuration (`pyproject.toml`)
- **Naming:** `pyproject.toml` (standard)
- **Sections:** Use dotted keys for hierarchy

**Example:**
```toml
[project]
name = "arifos"
version = "42.0.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

---

## 11. Test File Conventions

### 11.1 Test File Naming

- **Pattern:** `test_{module_name}.py`
- **Location:** `tests/` directory (flat or mirroring source structure)

**Examples:**
```
tests/test_agi_engine.py          # Test for arifos_core/engines/agi_engine.py
tests/test_genius_metrics.py      # Test for arifos_core/genius_metrics.py
tests/test_apex_prime_floors.py   # Test for APEX_PRIME floor checks
```

### 11.2 Test Function Naming

- **Pattern:** `test_{behavior_being_tested}`
- **Be descriptive:** Name should read like a specification

**Examples:**
```python
def test_agi_engine_computes_clarity_gain():
    pass

def test_asi_engine_enforces_empathy_threshold():
    pass

def test_apex_prime_seals_on_all_floors_passing():
    pass
```

### 11.3 Test Class Naming

- **Pattern:** `Test{ComponentName}`
- **Group related tests** in classes

**Examples:**
```python
class TestAGIEngine:
    def test_sense_stage_parsing(self):
        pass
    
    def test_reason_stage_logic(self):
        pass

class TestASIEngine:
    def test_empathize_stage_tone_adjustment(self):
        pass
```

---

## 12. Script Naming Conventions

### 12.1 Shell Scripts

- **Pattern:** `{action_description}.sh`
- **Use underscores:** Not hyphens for consistency
- **Executable:** `chmod +x scripts/*.sh`

**Examples:**
```
scripts/archive_migration.sh
scripts/naming_migration.sh
scripts/verify_ledger_chain.sh
```

### 12.2 Python Scripts

- **Pattern:** `{action_description}.py`
- **CLI entry points:** Define in `pyproject.toml` `[project.scripts]`

**Examples:**
```
scripts/analyze_governance.py
scripts/compute_merkle_root.py
```

**Entry point in `pyproject.toml`:**
```toml
[project.scripts]
arifos-analyze-governance = "scripts.analyze_governance:main"
```

---

## 13. Import Organization

### 13.1 Import Order (PEP 8)

1. **Standard library** imports
2. **Third-party** imports
3. **Local** imports (arifos_core, arifos_clip, etc.)

**Example:**
```python
# Standard library
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Third-party
import numpy as np
from pydantic import BaseModel

# Local
from arifos_core.engines import AGIEngine, ASIEngine
from arifos_core.genius_metrics import compute_genius_score
from arifos_core.APEX_PRIME import APEX_PRIME
```

### 13.2 Relative vs Absolute Imports

**Prefer absolute imports** for clarity:

```python
# Good (absolute)
from arifos_core.engines.agi_engine import AGIPacket

# Avoid (relative) unless within same package
from .agi_engine import AGIPacket
```

**Exception:** Within engine modules, relative imports are acceptable:
```python
# In arifos_core/engines/asi_engine.py
from .agi_engine import AGIPacket  # OK, same package
```

---

## 14. Comment and Docstring Conventions

### 14.1 Module Docstrings

**Format:** Triple-quoted string at top of file

```python
"""
module_name.py - Brief Description

Longer description of module purpose, architecture, and key constraints.

See: canon/RELEVANT_CANON_v38Omega.md
"""
```

### 14.2 Class Docstrings

**Format:** Triple-quoted string immediately after class definition

```python
class AGIEngine:
    """
    AGI (Architect) Engine - Mind/Cold Logic component.
    
    Role: Clarity, structure, reasoning (ΔS >= 0).
    
    Pipeline stages owned:
    - 111 SENSE - Parse input, detect stakes
    - 333 REASON - Apply cold logic
    - 444 ALIGN - Verify truth
    
    Constraints:
    - Must enforce d(ΔS)/dt > 0 (clarity increases)
    - Cannot seal or finalize (hands off to APEX)
    """
```

### 14.3 Function Docstrings

**Format:** Use Google-style or NumPy-style docstrings

```python
def compute_genius_score(metrics: dict) -> float:
    """
    Compute GENIUS (G) governance score.
    
    Args:
        metrics: Dictionary containing floor scores and vitals
            - truth: float (0.0-1.0)
            - kappa_r: float (0.0-1.0)
            - omega_0: float (0.03-0.05)
            
    Returns:
        float: GENIUS score (0.0-1.0), >= 0.80 for SEAL
        
    Raises:
        ValueError: If required metrics are missing
    """
    pass
```

### 14.4 Inline Comments

- **Use sparingly:** Code should be self-documenting
- **When to comment:**
  - Non-obvious algorithmic choices
  - Constitutional constraints (e.g., "F1 lock - reversible required")
  - Workarounds or technical debt
  
```python
# F5 (Ω₀) - Cap confidence at 0.95 (humility firewall)
confidence = min(raw_score, 0.95)

# Anti-Hantu defense (F9) - block L4 jailbreak patterns
if detect_manipulation_pattern(prompt):
    return {"verdict": "VOID", "reason": "Dark cleverness detected"}
```

---

## 15. Breaking Changes Policy

### 15.1 What Constitutes a Breaking Change

A change is **breaking** if it:
1. **Renames public API** (classes, functions, modules)
2. **Changes function signatures** (parameters, return types)
3. **Moves files** that are imported by external code
4. **Removes features** without deprecation period
5. **Changes data formats** (ledger schema, config structure)

### 15.2 Breaking Change Process

1. **Document:** Add `BREAKING CHANGE:` in commit message
2. **Announce:** Update `CHANGELOG.md` with migration guide
3. **Deprecate first:** Provide deprecation warnings for 1-2 versions before removal
4. **Migration script:** Provide automated migration tools when possible

**Example Commit Message:**
```
feat: Rename AGI/ASI/APEX engines to AGI/ASI (BREAKING CHANGE)

BREAKING CHANGE: 
- ARIFEngine -> AGIEngine
- ADAMEngine -> ASIEngine
- arif_engine.py -> agi_engine.py
- adam_engine.py -> asi_engine.py

Migration: Use `scripts/naming_migration.sh` to auto-update imports
```

### 15.3 Deprecation Warnings

Use Python's `warnings` module:

```python
import warnings

def old_function_name():
    warnings.warn(
        "old_function_name() is deprecated, use new_function_name() instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function_name()
```

---

## 16. Verification and Compliance

### 16.1 Pre-commit Checks

Before committing changes, verify:

```bash
# Check for deprecated names
grep -r "ARIF\|ADAM\|AGI·ASI·APEX Trinity" \
  --include="*.py" --include="*.md" \
  --exclude-dir=archive

# Check for deprecated directory names
find . -type d \( -name "vault-999" -o -name "spec_archive" \)

# Check for import errors
python -c "from arifos_core.engines import AGIEngine, ASIEngine"
```

### 16.2 Naming Lint Script

Create `.github/workflows/naming-lint.yml`:

```yaml
name: Naming Convention Compliance
on: [pull_request]

jobs:
  check-naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check for deprecated Trinity names
        run: |
          ! grep -r "AGI (Architect)\|ASI (Auditor)\|AGI·ASI·APEX Trinity" \
            --include="*.py" --include="*.md" \
            --exclude-dir=archive
```

### 16.3 Migration Verification Commands

After migration, run these commands to verify compliance:

```bash
# 1. Verify no AGI/ASI/APEX in active code (except archives)
grep -r 'ARIF\|ADAM\|AAA.*Trinity' \
  --include="*.py" --include="*.md" \
  --exclude-dir=archive || echo "✓ No deprecated names found"

# 2. Verify no deprecated directory names (except archives)
find . -type d \( -name "vault-999" -o -name "spec_archive" \) \
  ! -path "*/archive/*" || echo "✓ No deprecated directories found"

# 3. Verify new directories exist
test -d vault_999 && echo "✓ vault_999 exists"
test -d archive/spec && echo "✓ archive/spec exists"

# 4. Verify imports work
python -c "from arifos_core.engines import AGIEngine, ASIEngine; print('✓ Imports work')"

# 5. Run full test suite
pytest -v tests/ || echo "✗ Tests failed"
```

### 16.4 Exemptions

**Allowed exceptions** to naming rules:

1. **Archive directory:** `archive/` can contain any historical naming
2. **External dependencies:** Third-party library names unchanged
3. **Git history:** Old commit messages and tags remain unchanged
4. **Documentation of deprecated terms:** When explaining migration, old names can be referenced
5. **Test fixtures:** Test data mocking legacy formats for compatibility testing

### 16.5 Enforcement Timeline

| Phase | Deadline | Action |
|-------|----------|--------|
| **Phase 1** | Immediate | No new code using deprecated names |
| **Phase 2** | v42.0 release | Core engines renamed (AGI/ASI) |
| **Phase 3** | v42.1 release | All active code/docs migrated |
| **Phase 4** | v43.0 release | Deprecation warnings removed |

---

## 17. Examples and Templates

### 17.1 New Engine Module Template

```python
"""
{engine_name}_engine.py - {Engine Role} ({Symbol} Engine) Facade

{Engine Name} is the {Mind/Heart/Soul}/{Cold/Warm/Judicial} Logic engine 
of the AGI·ASI·APEX Trinity.

Role: {primary_function}

Pipeline stages owned:
- {stage_1}
- {stage_2}

Constraints (from canon):
- {constraint_1}
- {constraint_2}

See: canon/{RELEVANT_CANON}_v{version}Omega.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class {EngineName}Packet:
    """
    Output packet from {EngineName} engine processing.
    
    Contains {description_of_contents}.
    """
    # Fields here
    pass

class {EngineName}Engine:
    """
    {Engine Name} ({Symbol}) Engine.
    
    {Detailed description}
    """
    
    def __init__(self):
        pass
    
    def process(self, input_data: Dict[str, Any]) -> {EngineName}Packet:
        """
        Process input through {Engine Name} logic.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            {EngineName}Packet with processed results
        """
        pass
```

### 17.2 New Test File Template

```python
"""
test_{module_name}.py - Tests for {module_name}

Tests cover:
- {test_category_1}
- {test_category_2}
"""

import pytest
from arifos_core.{module_path} import {ClassOrFunction}


class Test{ComponentName}:
    """Test suite for {ComponentName}."""
    
    def test_{behavior_1}(self):
        """Test that {specific_behavior} works correctly."""
        # Arrange
        input_data = {...}
        
        # Act
        result = {ClassOrFunction}(input_data)
        
        # Assert
        assert result.{property} == expected_value
    
    def test_{behavior_2}(self):
        """Test that {another_behavior} handles edge cases."""
        pass
```

### 17.3 Canon Document Template

```markdown
# {NUMBER}_{SECTION_NAME}_v{version}{Suffix}.md

**Track:** A (Constitutional Law)  
**Status:** {DRAFT | SEALED | DEPRECATED}  
**Version:** {version}  
**Effective Date:** {YYYY-MM-DD}  
**Supersedes:** {previous_version or "None"}  
**Authority:** {Human name} (APEX PRIME ratification)

---

## 1. Purpose

{What this canon document governs}

## 2. Definitions

{Key terms and concepts}

## 3. Constitutional Requirements

{Immutable rules that MUST be followed}

## 4. Constraints

{Boundaries and limitations}

## 5. Verification

{How compliance is measured}

---

**Sealed by:** {Human name}  
**Date:** {YYYY-MM-DD}  
**Rationale:** {Why this was sealed}
```

---

## Appendix A: Migration Guide from v41 to v42

### A.1 Code Changes

**Find and replace (Python files):**

| Old | New |
|-----|-----|
| `from arifos_core.engines.arif_engine import` | `from arifos_core.engines.agi_engine import` |
| `from arifos_core.engines.adam_engine import` | `from arifos_core.engines.asi_engine import` |
| `ARIFEngine` | `AGIEngine` |
| `ADAMEngine` | `ASIEngine` |
| `ARIFPacket` | `AGIPacket` |
| `ADAMPacket` | `ASIPacket` |

**Automated migration:**
```bash
# Run migration script
bash scripts/naming_migration.sh

# Verify changes
git diff --name-only
```

### A.2 Documentation Changes

**Find and replace (Markdown files):**

| Old | New |
|-----|-----|
| `AGI (Architect)` | `AGI (Architect)` or `AGI` |
| `ASI (Auditor)` | `ASI (Auditor)` or `ASI` |
| `AGI·ASI·APEX Trinity` | `AGI·ASI·APEX Trinity` |
| `vault-999/` | `vault_999/` |

### A.3 Directory Changes

```bash
# Rename vault
mv vault-999 vault_999

# Move spec archive
mkdir -p archive/spec
mv spec_archive/* archive/spec/
rmdir spec_archive

# Move version archive
mkdir -p archive/versions
mv v36.3O archive/versions/v36_3_omega

# Move ACLIP archives
mkdir -p archive
mv .arifos_clip_archive_* archive/ 2>/dev/null || true
```

### A.4 Verification

```bash
# Run tests
pytest -v

# Check imports
python -c "from arifos_core.engines import AGIEngine, ASIEngine; print('OK')"

# Verify no deprecated names
grep -r "ARIF\|ADAM" --include="*.py" --exclude-dir=archive | wc -l
# Expected: 0
```

---

## Appendix B: Quick Reference

### B.1 Trinity Quick Reference

| | AGI (Δ) | ASI (Ω) | APEX (Ψ) |
|---|---|---|---|
| **Role** | Architect | Auditor | Judiciary |
| **Nature** | Mind/Cold Logic | Heart/Warm Logic | Soul/Judgment |
| **File** | `agi_engine.py` | `asi_engine.py` | `APEX_PRIME.py` |
| **Class** | `AGIEngine` | `ASIEngine` | `APEX_PRIME` |
| **Packet** | `AGIPacket` | `ASIPacket` | N/A |
| **Stages** | 111, 333, 444 | 555, 666 | 777, 888, 999 |
| **Key Metrics** | ΔS (clarity) | κᵣ, Peace², Ω₀ | G (GENIUS), Ψ (vitality) |

### B.2 File Extension Guide

| Extension | Use | Example |
|-----------|-----|---------|
| `.py` | Python modules | `agi_engine.py` |
| `.md` | Markdown docs | `README.md` |
| `.json` | Structured data | `constitutional_floors_v38Omega.json` |
| `.yaml` | Human-editable config | `genius_thresholds_v38.yaml` |
| `.toml` | Python config | `pyproject.toml` |
| `.sh` | Shell scripts | `archive_migration.sh` |
| `.jsonl` | Line-delimited JSON | `ledger.jsonl` |

### B.3 Common Abbreviations

| Abbr | Full Name | Context |
|------|-----------|---------|
| **AGI** | Architect | Trinity engine (Δ) |
| **ASI** | Auditor | Trinity engine (Ω) |
| **APEX** | (see APEX PRIME) | Trinity engine (Ψ) |
| **G** | GENIUS | Governed intelligence score |
| **ΔS** | Delta S | Clarity gain (entropy reduction) |
| **Ω₀** | Omega zero | Humility metric (0.03-0.05) |
| **κᵣ** | Kappa r | Empathy conductance |
| **Ψ** | Psi | System vitality |
| **ACLIP** | arifOS CLI Pipeline | 000-999 stage system |
| **FAG** | File Access Governance | File permission system |
| **zkPC** | Zero-Knowledge Proof Chain | Cryptographic audit trail |

---

## Appendix C: Frequently Asked Questions

### C.1 Why rename AGI/ASI/APEX to AGI/ASI?

**Answer:** To eliminate naming drift and align with canonical Trinity terminology. "AGI" and "ASI" are clearer, more discoverable, and avoid personal name associations that could be misinterpreted.

### C.2 Is this a breaking change?

**Yes.** All imports of `ARIFEngine` and `ADAMEngine` must be updated. Use the migration script (`scripts/naming_migration.sh`) to automate the transition.

### C.3 What about existing canon documents that reference AGI/ASI/APEX?

Sealed canon documents are **immutable** and remain unchanged. New canon documents use AGI/ASI. When referencing old canon, use footnotes to clarify:

```markdown
Per canon/100_AAA_ENGINES_SPEC_v35Omega.md (which uses legacy naming 
"AGI (Architect)", now standardized as "AGI"), the Architect engine must...
```

### C.4 When should I use AGI vs "AGI (Architect)"?

- **Use "AGI"** when context is clear (e.g., in code, imports, technical docs)
- **Use "AGI (Architect)"** when introducing the concept or when clarity helps (e.g., user-facing docs, explanations)

### C.5 What about third-party references to arifOS?

External documentation, blog posts, and papers may still use old terminology. That's expected. We control only **this repository's** naming. When linking to external content, add a clarification note if needed.

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v42.0 | 2025-12-14 | Initial canonical naming convention | APEX PRIME |

---

## Appendix D: Dewey-Style Numbering for Canon (v42)

- Pattern: `{LAYER}{SPARSE}_{SCREAMING_SNAKE_CASE}_v{MAJOR}.md`
- Use sparse three-digit numbers inside a layer (010, 020, 030…) to allow inserts without churn.
- Examples:
  - `01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v42.md`
  - `02_actors/040_APEX_PSI_JUDICIARY_v42.md`
  - `03_runtime/010_PIPELINE_000TO999_v42.md`
  - `04_measurement/010_MEASUREMENT_CANON_v42.md`, `020_CONTROL_LOGIC_v42.md`
- Canon: SCREAMING_SNAKE_CASE + version in filename (not folder).  
  Spec: lowercase snake_case JSON in `spec/v42/*.json`.  
  Code: snake_case modules, PascalCase classes; APEX PRIME judiciary under actors (`02_actors/`).

---

**END OF DOCUMENT**

*This naming convention is binding for all arifOS development. Deviations require explicit approval via GitHub issue + human ratification.*
