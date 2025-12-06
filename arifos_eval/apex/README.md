# APEX Measurement Layer (v36.1Ω)

**Epoch:** v36.1Ω
**Status:** Canonical Reference Implementation

## Overview

This module implements the judiciary metrics of arifOS (Δ→Ω→Ψ).
It converts abstract constitutional floors into computable signals.

### v36.1Ω Update: Truth Polarity

This version introduces **Vector Truth**. Truth is no longer just a scalar (Accuracy). It has direction (ΔS).

- **Truth-Light:** Accurate + Clarifying (ΔS > 0).
- **Shadow-Truth:** Accurate + Obscuring (ΔS < 0).

The Judiciary now detects and penalizes **Weaponized Truth** (Shadow-Truth + Amanah fail).

## Architecture

The system is divided into three tiers:

- **Tier 1 (The Law):** `APEX_MEASUREMENT_STANDARDS_v36.1Omega.md`
  – Genius G, Dark Cleverness C_dark, Vitality Ψ, floors, and verdict logic.

- **Tier 2 (The Tunables):** `apex_standards_v36.json`
  – Configurable weights, thresholds, and patterns. Can change without breaking the law.

- **Tier 3 (The Logic):** `apex_measurements.py`
  – Reference Python implementation that executes Tier 1 using Tier 2 parameters.

## Directory Structure

```text
arifos_eval/apex/
├── README.md                              # This file
├── APEX_MEASUREMENT_STANDARDS_v36.1Omega.md  # Tier 1: The Constitution (Law)
├── apex_standards_v36.json               # Tier 2: The Configuration (Tunables)
└── apex_measurements.py                  # Tier 3: The Reference Implementation (Logic)
```

## Usage

```python
from arifos_eval.apex.apex_measurements import ApexMeasurement

# Initialize with standard configuration
apex = ApexMeasurement("apex_standards_v36.json")

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
