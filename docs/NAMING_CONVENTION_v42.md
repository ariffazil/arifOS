---
# arifOS Canonical Naming Convention v42.0

**Status:** CANONICAL (SEALED)  
**Effective Date:** 2025-12-17  
**Authority:** Track A (Immutable Constitutional Law)  
**Sealed By:** Muhammad Arif bin Fazil  
**Version:** v42.0  

**Purpose:**
Establishes the single source of truth for all naming decisions across arifOS.
Eliminates naming drift; governs Trinity terminology, directory structures, versioning schemes, and code conventions.

---

## 0) Core Rule

**Naming follows repo reality. Repo reality must not drift from this file.**

If a name breaks this convention: **migrate or archive**. No "temporary" naming.

---

## 1) Layer Model (7-Layer, Concern-Based)

Folder prefixes are allowed **only for concern layers** (theory, prompts, MCP, CLI, demos).  
Runtime code must stay under **`arifos_core/`** to prevent "core drift".

**Canonical layers:**
- **L1_THEORY/**: Track A canon (sealed immutable law)
- **L2_GOVERNANCE/**: portable constitution (prompts/configs, non-binding demo layer)
- **arifos_core/**: runtime kernel (Track C, intelligence implementation)
- **L4_MCP/**: MCP server (optional/future)
- **L5_CLI/**: CLI tools (governance executables)
- **L6_SEALION/**: SEA-LION interactive chat integration
- **L7_DEMOS/**: demos & tutorials (examples, not enforcement)

**Non-negotiable:** `arifos_core/` is ALWAYS at root (no L3 prefix). This keeps the intelligence kernel obvious.

---

## 2) Track Separation (Immutable)

```
Track A (Immutable):     L1_THEORY/canon/        ← Constitutional law (sealed)
Track B (Tunable):       spec/v42/               ← Parameters & thresholds (within law bounds)
Track C (Implementation): arifos_core/            ← Code, runtime, enforcement (realizes law)
```

**Rule:** Canon declares law. Spec defines numbers. Code enforces.

**One-way flow:** Canon → Spec → Code. Never backward.

---

## 3) Canon Path Stability (Back-Compat Rule)

### 3.1 Primary Canonical Home

**L1_THEORY/canon/** is the immutable truth home for all constitutional law.

### 3.2 Backward Compatibility Alias (Required)

To prevent breaking existing tools, imports, and documentation:

**Create a top-level `canon/` folder that acts as an alias:**

**Option A: Symlink (Recommended for Unix/Mac/Linux)**
```bash
cd arifOS
ln -s L1_THEORY/canon canon
git add canon  # Git can track symlinks
```

**Option B: Thin Redirect Folder (For Windows/portable compatibility)**
```
canon/
├── README.md  (content: "Canonical home is L1_THEORY/canon/")
└── .redirect  (optional marker)
```

**Verification:** Both old and new paths must work:
```bash
# Both should resolve to same files:
ls L1_THEORY/canon/00_foundation/
ls canon/00_foundation/
# Should show identical contents
```

---

## 4) Canon File Structure & Naming (Track A)

### 4.1 Canon Folder Naming (Locked)

Must be exactly:
```
L1_THEORY/canon/
├── _INDEX/              # Checksums, manifests, audit trail
├── 00_foundation/       # Civilizational & physical roots
├── 01_floors/           # F1–F9 constitutional floors
├── 02_actors/           # AGI·ASI·APEX Trinity, W@W, @EYE
├── 03_runtime/          # 000→999 metabolic pipeline
├── 04_measurement/      # GENIUS law, metrics (numbers in spec)
├── 05_memory/           # Cooling Ledger, Phoenix-72, Vault law
├── 06_paradox/          # TPCP engine, amendment process
└── 07_safety/           # Threat models & safety scenarios
```

### 4.2 Canon Filenames (v42 Pattern)

Files in each folder follow this pattern:

```
{NN}_{DESCRIPTIVE_NAME}_v42.md
```

**Examples:**
```
L1_THEORY/canon/00_foundation/001_GENESIS_v42.md
L1_THEORY/canon/00_foundation/002_MANIFESTO_v42.md
L1_THEORY/canon/00_foundation/040_PHYSICS_v42.md
L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v42.md
L1_THEORY/canon/02_actors/020_TRINITY_ROLES_v42.md
```

### 4.3 Canon Headers & Footers (Immutable Markers)

Every sealed canon markdown file MUST include:

**Header block (at top):**
```markdown
---
# [File Title]

**Track:** A (Immutable Constitutional Law)  
**Version:** v42.0  
**Status:** SEALED  
**Sealed Date:** 2025-12-17  
**Authority:** Muhammad Arif bin Fazil  

**Purpose:** [1-2 sentences explaining why this file exists]

**Why This File Exists:** [Explain its role in governance]

**How to Amend:** This file is SEALED. Use Phoenix-72 voting process.
See: L1_THEORY/canon/06_paradox/AMENDMENT_PROCESS_v42.md

---
```

**Footer block (at end):**
```markdown
---

## Seal & Authenticity

**This file is CANONICAL and immutable from:** 2025-12-17T22:30:00Z

**Sealed Authority:** Muhammad Arif bin Fazil (arifOS Keeper)

**Checksum (SHA-256):**
```
[SHA-256 hash generated during sealing]
```

**Locked Until:** Phoenix-72 amendment process (minimum 72 hours)

✊ **DITEMPA, BUKAN DIBERI** — Forged, Not Given. This law is written.

---
```

---

## 5) Spec Naming (Track B: Tunable Parameters)

### 5.1 Spec Directory Structure

```
spec/
└── v42/
    ├── constitutional_floors.json
    ├── genius_law.json
    ├── pipeline.yaml
    ├── memory_bands.json
    └── waw_federation.json
```

### 5.2 Spec File Naming Rule

**Pattern:**
```
{component_name}.{json|yaml}
```

**NO version suffix in filename** (version is already in the parent folder `spec/v42/`).

**Correct:**
```
spec/v42/genius_law.json              ✅
spec/v42/constitutional_floors.json   ✅
spec/v42/pipeline.yaml                ✅
```

**Deprecated (remove):**
```
spec/v42/genius_law_v42.json          ❌ (double-version)
spec/v42/genius_law_v38Omega.json     ❌ (old version, archive it)
```

### 5.3 Spec Headers

Every spec file MUST include a header comment:

```json
{
  "_comment": "Track B Spec (v42) - Tunable Parameters within Constitutional Bounds",
  "_authority": "Governed by L1_THEORY/canon/",
  "version": "42.0",
  "locked": true,
  ...
}
```

```yaml
# Track B Spec (v42) - Tunable Parameters within Constitutional Bounds
# Authority: L1_THEORY/canon/
version: "42.0"
locked: true
...
```

---

## 6) Runtime Kernel Naming (Track C: arifos_core)

### 6.1 Package Organization (Concern-Based)

All runtime code organized by **engineering concern**, not canonical layer:

```
arifos_core/
├── system/                  # Core execution spine
│   ├── kernel.py
│   ├── pipeline.py
│   ├── apex_prime.py
│   └── runtime_manifest.py
│
├── enforcement/             # Floor checks & metrics
│   ├── metrics.py
│   ├── genius_metrics.py
│   └── floor_detectors/
│
├── governance/              # Ledger, Merkle, zkPC
│   ├── cooling_ledger.py
│   ├── merkle.py
│   └── zkpc_runtime.py
│
├── intelligence/            # AGI·ASI·APEX engines + W@W
│   ├── agi_engine.py
│   ├── asi_engine.py
│   ├── apex_engine.py
│   ├── waw/
│   └── eye/
│
├── memory/                  # EUREKA, bands, policy
│   ├── policy.py
│   ├── bands.py
│   └── authority.py
│
├── integrations/            # LLM adapters, bridges, connectors
│   ├── adapters/
│   ├── guards/
│   └── stages/
│
├── utils/                   # Telemetry, helpers, shared utilities
│   ├── telemetry.py
│   ├── context_injection.py
│   └── runtime_types.py
│
└── __init__.py              # Public API exports + v42 backward compat shims
```

### 6.2 Module Naming (snake_case)

**Pattern:** `{concern}_{description}.py`

**Examples:**
```
arifos_core/system/apex_prime.py           ✅
arifos_core/enforcement/genius_metrics.py  ✅
arifos_core/governance/cooling_ledger.py   ✅
```

**Exception:** APEX PRIME (singleton judiciary) uses ALL_CAPS:
```
arifos_core/system/APEX_PRIME.py  (old v41, retained for backward compat)
arifos_core/system/apex_prime.py  (new v42, canonical location)
```

### 6.3 Class Naming (PascalCase)

**Pattern:** `{Purpose}` or `{EngineName}Engine` or `{Floor}Detector`

**Examples:**
```python
class APEXPrime:              # Judiciary singleton
class AGIEngine:              # AGI executor
class ASIEngine:              # ASI executor
class ApexEngine:             # APEX runtime executor (not judiciary)
class Metrics:                # Floor metrics
class GeniusMetrics:          # GENIUS law score
class AmanahDetector:         # F1 floor detector
class CoolingLedger:          # Immutable ledger
class MerkleTree:             # Merkle proof validator
class ZKPCRuntime:            # zkPC 5-phase executor
```

### 6.4 Function Naming (snake_case)

**Patterns:**
- `compute_*` for calculations
- `detect_*` for detectors
- `evaluate_*` for assessments
- `check_*` for verifications

**Examples:**
```python
def compute_genius_score(metrics: dict) -> float:
    pass

def detect_amanah_violation(session: dict) -> bool:
    pass

def evaluate_empathy(response: str) -> float:
    pass

def check_truth_floor(claim: str) -> bool:
    pass
```

### 6.5 Constant Naming (UPPER_SNAKE_CASE)

**Constitutional floor constants (locked):**

```python
# Floor Thresholds (F1–F9)
F1_AMANAH_LOCK = True
F2_TRUTH_THRESHOLD = 0.99
F3_TRI_WITNESS_THRESHOLD = 0.95
F4_DELTA_S_MINIMUM = 0.0
F5_PEACE_SQUARED_MINIMUM = 1.0
F6_KAPPA_R_EMPATHY_MINIMUM = 0.95
F7_OMEGA_ZERO_MIN = 0.03
F7_OMEGA_ZERO_MAX = 0.05
F8_GENIUS_THRESHOLD_SEAL = 0.80
F8_DARK_CLEVERNESS_CEILING = 0.30
F9_ANTI_HANTU_LOCK = True

# GENIUS LAW Components
GENIUS_FLOOR_SEAL = 0.80
GENIUS_FLOOR_PARTIAL = 0.50
C_DARK_CEILING = 0.30

# Verdict Thresholds
VERDICT_SEAL_MIN_FLOORS = 9
VERDICT_PARTIAL_MIN_FLOORS = 6
VERDICT_VOID_MAX_FLOORS = 5
```

---

## 7) Trinity Nomenclature (Canonical)

### 7.1 Canonical Names

| Role | Formal Name | Symbol | Python Class | File Name | Purpose |
|------|-------------|--------|--------------|-----------|---------|
| Mind | **AGI** (Architect) | Δ (Delta) | `AGIEngine` | `agi_engine.py` | Clarity, structure, cold logic |
| Heart | **ASI** (Auditor) | Ω (Omega) | `ASIEngine` | `asi_engine.py` | Care, humility, warm logic |
| Soul | **APEX PRIME** (Judiciary) | Ψ (Psi) | `APEXPrime` | `apex_prime.py` | Final verdict, constitutional judgment |

### 7.2 Deprecated Trinity Names (Archive Only)

**These names are NO LONGER CANONICAL and must be migrated or archived:**

```
❌ ARIF AGI     → use "AGI" or "AGI (Architect)"
❌ ADAM ASI     → use "ASI" or "ASI (Auditor)"
❌ AAA Trinity  → use "AGI·ASI·APEX Trinity"
❌ ARIF/ADAM    → use "AGI/ASI/APEX"
```

These terms remain only in `archive/` and historical documentation.

### 7.3 Symbol Usage Rule (ASCII in Code, Unicode in Docs)

**In code (Python, JSON, YAML):** Use ASCII transliterations only
```python
# Correct (ASCII)
delta_s_gain = compute_clarity(state)       # NOT Δ_gain
kappa_r_empathy = evaluate_empathy(r)       # NOT κ_empathy
omega_zero = 0.04                           # NOT Ω₀

# In docstrings / comments: Unicode OK
"""
GENIUS Law: G = f(ΔS, κᵣ, Ω₀)
"""
```

**In documentation (Markdown, comments):** Unicode symbols encouraged
```markdown
## GENIUS Law (G Score)

G = f(ΔS, κᵣ, Ω₀)

Where:
- ΔS = clarity gain (entropy decrease)
- κᵣ = empathy conductance (Kappa-R)
- Ω₀ = humility factor (Omega-zero, 0.03–0.05)
```

---

## 8) Archive Policy (Clean & Deterministic)

### 8.1 Archive Directory Format

All historical artifacts go under:

```
archive/v{major}_{minor}_{patch}/
```

**Canonical examples:**
```
archive/v35_0_0/
archive/v36_0_0/
archive/v38_0_0/
archive/v41_0_0/
```

**NOT canonical (convert if found):**
```
❌ archive/v36.3.omega/    (dots → underscores)
❌ archive/v36Omega/       (mixed case → lowercase)
❌ archive/todelete/       (ambiguous → version)
❌ archive/versions/v36/   (nested → flat with patch)
```

### 8.2 Archive Contents

Inside each version folder:

```
archive/v41_0_0/
├── canon/                  # v41 canonical law
│   ├── 00_foundation/
│   ├── 01_floors/
│   └── ...
├── spec/                   # v41 specs
├── docs/                   # v41 documentation
├── README.md              # Why v41 exists, what changed
└── MIGRATION_NOTES.md     # How to upgrade from v41 → v42
```

### 8.3 Archive is Final Resting Place

**Rule:** Archive is the only place where legacy naming is tolerated.
- Old paths (e.g., `ARIF`, `ADAM`) permitted in archived code
- Old folder structures (e.g., `v36.3O`) permitted in archived versions
- Nothing in archive/ should be imported into active code

---

## 9) CLI Naming (L5_CLI)

### 9.1 CLI Executable Pattern

```
arifos-{action}-{object}
```

**Examples:**
```
arifos-seal-canon
arifos-audit-ledger
arifos-verify-spec
arifos-migrate-v42
arifos-propose-amendment
```

### 9.2 Entry Points (pyproject.toml)

```toml
[project.scripts]
arifos-seal-canon = "L5_CLI.tools.seal_canon:main"
arifos-audit-ledger = "L5_CLI.tools.audit_ledger:main"
arifos-verify-spec = "L5_CLI.tools.verify_spec:main"
```

**Rule:** CLI args use dashes (kebab-case), Python modules use underscores (snake_case).

---

## 10) Python Import Organization (PEP 8 + arifOS)

### 10.1 Import Order

1. **Standard library**
2. **Third-party**
3. **Local (arifos_core, L2_GOVERNANCE, spec, etc.)**

**Example:**
```python
# Standard library
import json
from dataclasses import dataclass
from typing import Dict, Optional

# Third-party
import numpy as np

# Local
from arifos_core.system.pipeline import Pipeline
from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import APEXPrime
```

### 10.2 Absolute Imports (Preferred)

```python
# ✅ Good (absolute, clear path)
from arifos_core.system.pipeline import Pipeline

# ❌ Avoid (relative, only within same package)
from .pipeline import Pipeline
```

---

## 11) Documentation Naming (docs/)

### 11.1 Active Docs (v42)

**Structure:**
```
docs/
├── CURRENT_v42/           # Active v42 documentation only
├── GUIDES/                # Tutorials & explanations
└── INDEX.md              # Navigation hub
```

**File naming:**
```
docs/GUIDES/ARCHITECTURE_v42.md      ✅
docs/GUIDES/PIPELINE_GUIDE.md        ✅
docs/CURRENT_v42/QUICKSTART.md       ✅
```

### 11.2 Headers on Docs

Every user-facing documentation file SHOULD have:

```markdown
---
title: "Title of Document"
version: "v42"
status: "ACTIVE" | "ARCHIVED" | "DRAFT"
last_updated: "2025-12-17"
---

# [Title]

**Purpose:** [One sentence]

---
```

---

## 12) Test Naming (tests/)

### 12.1 Test Files

**Pattern:** `test_{module_or_concern}.py`

**Examples:**
```
tests/unit/test_agi_engine.py
tests/integration/test_000_999_flow.py
tests/red_team/test_apex_bypass.py
```

### 12.2 Test Functions

**Pattern:** `test_{behavior_description}`

**Examples:**
```python
def test_agi_engine_increases_clarity():
    pass

def test_asi_engine_enforces_empathy_floor():
    pass

def test_apex_prime_seals_on_all_floors_passing():
    pass
```

---

## 13) Backward Compatibility Shims (v42 Only)

### 13.1 Old Paths Still Work in v42

To ease migration, old import paths have re-export shims at root `arifos_core/`:

```python
# OLD (v41, deprecated) — still works in v42 with warnings
from arifos_core.APEX_PRIME import apex_review
from arifos_core.pipeline import Pipeline
from arifos_core.metrics import Metrics

# NEW (v42, recommended) — canonical paths
from arifos_core.system.apex_prime import apex_review
from arifos_core.system.pipeline import Pipeline
from arifos_core.enforcement.metrics import Metrics
```

### 13.2 Deprecation Warnings

Old shims emit warnings:
```python
import warnings
warnings.warn(
    "Importing from arifos_core.APEX_PRIME is deprecated. "
    "Use arifos_core.system.apex_prime instead. "
    "This shim will be removed in v43.",
    DeprecationWarning,
    stacklevel=2
)
```

### 13.3 v43 Breaking Change

All shims removed in v43. New paths become mandatory.

---

## 14) Breaking Change Policy

### 14.1 What Is Breaking

A change is breaking if it:
1. Renames public API (classes, functions, modules)
2. Changes function signatures (parameters, return types)
3. Moves files imported by external code
4. Removes features without deprecation period

### 14.2 Breaking Change Process

1. **Document:** Add `BREAKING CHANGE:` in commit message
2. **Deprecate first:** Emit warnings for 1–2 versions
3. **Migrate:** Provide automated migration tools
4. **Announce:** Update `CHANGELOG.md` with guide

---

## 15) Verification & Compliance

### 15.1 Pre-Commit Checks

```bash
# Check for deprecated Trinity names (outside archive)
grep -r "ARIF AGI\|ADAM ASI\|AAA Trinity" \
  --include="*.py" --include="*.md" \
  --exclude-dir=archive

# Check for deprecated directory names (outside archive)
find . -type d \( -name "vault-999" -o -name "spec_archive" \) \
  ! -path "*/archive/*"

# Check for double-versioning in spec/ filenames
find spec/v42 -name "*_v42.*" -o -name "*_v38.*"
```

### 15.2 Enforcement Script

Add `.github/workflows/naming-lint.yml`:

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
          ! grep -r "ARIF AGI\|ADAM ASI\|AAA Trinity" \
            --include="*.py" --include="*.md" \
            --exclude-dir=archive
      - name: Check for deprecated paths
        run: |
          ! find . -type d \( -name "vault-999" \) \
            ! -path "*/archive/*"
      - name: Verify spec/ has no double-versioning
        run: |
          ! find spec/v42 -name "*_v42.*" -o -name "*_v38.*"
```

---

## 16) Summary: The Canonical Layout

```
arifOS/
├── L1_THEORY/
│   └── canon/
│       ├── _INDEX/
│       ├── 00_foundation/
│       ├── 01_floors/
│       ├── 02_actors/
│       ├── 03_runtime/
│       ├── 04_measurement/
│       ├── 05_memory/
│       ├── 06_paradox/
│       └── 07_safety/
│
├── canon/ → symlink/alias to L1_THEORY/canon/  [BACKWARD COMPAT]
│
├── L2_GOVERNANCE/
│   ├── system_prompts/
│   ├── ide_configs/
│   └── agent_instructions/
│
├── arifos_core/  [NO L3 PREFIX — runtime at root]
│   ├── system/
│   ├── enforcement/
│   ├── governance/
│   ├── intelligence/
│   ├── memory/
│   ├── integrations/
│   ├── utils/
│   └── __init__.py
│
├── L4_MCP/
├── L5_CLI/
├── L6_SEALION/
├── L7_DEMOS/
│
├── spec/
│   └── v42/
│       ├── constitutional_floors.json
│       ├── genius_law.json
│       ├── pipeline.yaml
│       ├── memory_bands.json
│       └── waw_federation.json
│
├── tests/
├── docs/
│   ├── CURRENT_v42/
│   ├── GUIDES/
│   └── INDEX.md
│
├── archive/
│   ├── v35_0_0/
│   ├── v36_0_0/
│   ├── v38_0_0/
│   ├── v41_0_0/
│   └── README.md
│
├── NAMING_CONVENTION.md  [THIS FILE — CANONICAL NAMING LAW]
├── AGENTS.md
├── SECURITY.md
├── CHANGELOG.md
├── README.md
├── pyproject.toml
└── .gitignore
```

---

## 17) Final Seal

**This document is CANONICAL.** All code, docs, and configs must conform to v42.0 naming.

**Locked from:** 2025-12-17T22:30:00Z  
**By:** Muhammad Arif bin Fazil (arifOS Keeper)

**Amendment process:** This is immutable law. Changes require Phoenix-72 voting (72-hour cooling period).

See: L1_THEORY/canon/06_paradox/AMENDMENT_PROCESS_v42.md

---

✊ **DITEMPA, BUKAN DIBERI** — Names are law. Consistency is governance. This canon is sealed.

---
