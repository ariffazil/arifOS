# APEX Measurement Layer (v45.0)

**Epoch:** v45.0 (Phoenix-72 Consolidation)
**Status:** Canonical Reference Implementation
**Authority:** Evaluation framework aligned with Track B v45 specs

## Overview

This module implements the judiciary metrics of arifOS (Δ→Ω→Ψ).
It converts abstract constitutional floors into computable signals.

### v45.0 Update: Phoenix-72 Consolidation

This version aligns with the v45 constitutional framework:

- **Anti-Hantu Enhancement:** Detects hypothetical consciousness claims ("if I could feel")
- **Truth Verification:** Referential URL validation (detects fabricated links)
- **Crisis Override:** Emergency patterns trigger compassionate 888_HOLD
- **Track B Manifest:** SHA-256 verified specs for tamper-evident integrity
- **Phoenix-72 Governance:** 72-hour cooling for constitutional amendments

**Carried forward from v36.1Ω:**
- **Vector Truth:** Truth has direction (ΔS polarity)
- **Truth-Light:** Accurate + Clarifying (ΔS > 0)
- **Shadow-Truth:** Accurate + Obscuring (ΔS < 0)
- **Weaponized Truth Detection:** Shadow-Truth + Amanah fail

## Architecture

The system is divided into three tiers:

- **Tier 1 (The Law):** `APEX_MEASUREMENT_STANDARDS_v45.md`
  – Genius G, Dark Cleverness C_dark, Vitality Ψ, floors, and verdict logic.

- **Tier 2 (The Tunables):** `apex_standards_v45.json`
  – Configurable weights, thresholds, and patterns. Can change without breaking the law.

- **Tier 3 (The Logic):** `apex_measurements.py`
  – Reference Python implementation that executes Tier 1 using Tier 2 parameters.

## Directory Structure

```text
arifos_eval/apex/
├── README.md                              # This file
├── APEX_MEASUREMENT_STANDARDS_v45.md      # Tier 1: The Constitution (Law)
├── apex_standards_v45.json                # Tier 2: The Configuration (Tunables)
├── apex_standards_v36.json                # Tier 2: Legacy (v36.1Ω reference)
└── apex_measurements.py                   # Tier 3: The Reference Implementation (Logic)
```

## Usage

```python
from arifos_eval.apex.apex_measurements import ApexMeasurement

# Initialize with v45 configuration
apex = ApexMeasurement("apex_standards_v45.json")

# 1. Input State (from Agent Telemetry)
dials = {"A": 0.9, "P": 0.9, "E": 0.95, "X": 0.9}

# 2. Output Metrics (from Evaluation Harness)
metrics = {
    "delta_s": 0.2,
    "peace2": 1.1,
    "k_r": 0.98,
    "rasa": 1.0,
    "amanah": 1.0,
    "entropy": 0.1
}

# 3. Judge
verdict = apex.judge(dials, output_text="...", output_metrics=metrics)
print(verdict["verdict"])  # SEAL, PARTIAL, VOID, or SABAR
```
