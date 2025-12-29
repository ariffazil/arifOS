# SEA-LION Test Suite (v45 Consolidated)

**Status:** Canonical test location as of Phase 2 Step 2.1 (Dec 2025)
**Source:** Merged from tests/ + tests_consolidated/ unique files
**Total Files:** 24 files organized by purpose

---

## Directory Structure

### Root (Active Scripts & Demos)
Primary working files for interactive testing and demonstrations.

| File | Type | API Key? | Description |
|------|------|----------|-------------|
| `demo_sealion_raw_vs_governed.py` | Demo | Yes | RAW vs GOVERNED side-by-side comparison |
| `demo_sealion_v45_full.py` | Demo | Yes | Complete v45Ω Trinity demo (ΔΩΨ) |
| `sealion_full_suite_v45.py` | Suite | Yes | Full test suite runner |
| `sealion_governed.py` | Interactive | Yes | Governed REPL session |
| `sealion_governed_v45_budi.py` | Interactive | Yes | Budi wisdom-gated release demo |
| `auto_sealion.py` | Automation | Yes | Automated governance testing |
| `raw_sealion_simple.py` | Baseline | Yes | Simple RAW mode testing |
| `list_models.py` | Utility | No | List available SEA-LION models |
| `README_RAW_VS_GOVERNED.md` | Docs | - | RAW vs GOVERNED usage guide |
| `run_raw_vs_governed.ps1` | Script | - | Windows PowerShell launcher |
| `verify_sealion_sovereignty.py` | Validation | No | Python-sovereign enforcement check |

### unit/ (Unit Tests)
Focused unit tests validating specific governance features.

| File | API Key? | Description |
|------|----------|-------------|
| `test_sealion_baseline.py` | No | Baseline governance validation |
| `test_sealion_governed.py` | Optional | Full governance pipeline test |
| `test_sealion_litellm.py` | No | LiteLLM gateway integration |
| `test_sealion_v4_comparison.py` | Optional | Model version comparison |
| `test_sealion_api_key_detection.py` | No | API key detection regression test (from consolidated) |
| `test_sealion_interactive.py` | Yes | Interactive CLI demo (from consolidated) |
| `test_sealion_v44.py` | Yes | TEARFRAME physics enforcement (from consolidated) |
| `test_raw_vs_governed_smoke.py` | No | Smoke tests for RAW vs GOVERNED |

### demos/ (Demonstrations)
Full demonstrations of v45Ω governance capabilities.

| File | API Key? | Description |
|------|----------|-------------|
| `demo_mock.py` | No | Mock demo without API (F1/F9 only) (from consolidated) |

### integration/ (Integration Examples)
Integration patterns with SEA-LION API and framework examples.

| File | API Key? | Description |
|------|----------|-------------|
| `examples.py` | Yes | 7 integration examples (from consolidated) |
| `play_session.py` | No | Interactive mock governance (from consolidated) |
| `play_session_live.py` | Yes | Live API interactive session (from consolidated) |
| `test_sgtoxic_spin.py` | No | SGToxicGuard toxicity validation (from consolidated) |

### _runs/ (Output Directory)
Runtime logs and session outputs from governed executions.

---

## Quick Start

### Prerequisites
```bash
# 1. Install arifOS with SEA-LION support
pip install -e ".[dev,litellm]"

# 2. Set API key (choose one method)
export SEALION_API_KEY="your-key"              # Unix/Linux/Mac
$env:SEALION_API_KEY="your-key"                # Windows PowerShell
```

### Run Main Demo (Recommended)
```bash
# Complete v45Ω demonstration
python L6_SEALION/tests/demo_sealion_v45_full.py

# RAW vs GOVERNED comparison
python L6_SEALION/tests/demo_sealion_raw_vs_governed.py
```

### Run Unit Tests
```bash
# All unit tests (no API key needed for most)
pytest L6_SEALION/tests/unit/ -v

# Specific test
pytest L6_SEALION/tests/unit/test_sealion_baseline.py -v
```

### Run Integration Examples
```bash
# Interactive mock session (no API)
python L6_SEALION/tests/integration/play_session.py

# Live interactive (needs API key)
python L6_SEALION/tests/integration/play_session_live.py
```

---

## Phase 2 Step 2.1 Changes (Dec 2025)

**Extracted from tests_consolidated/:**
- 3 unique unit tests → `unit/`
- 1 demo → `demos/`
- 4 integration examples → `integration/`

**Preserved from tests/:**
- All 16 original files remain in root (active working directory)
- Subdirectories added for better organization

**Total:** 24 files (16 original + 8 extracted)

**Original tests_consolidated/:** Ready for archival to `archive/sealion_tests_snapshot_20251227/`

---

## Constitutional Floors Tested

All scripts validate the 9 constitutional floors:

| Floor | Threshold | Type | Coverage |
|-------|-----------|------|----------|
| F1 Amanah | LOCK | Hard | All scripts |
| F2 Truth | ≥0.99 | Hard | All scripts |
| F3 Tri-Witness | ≥0.95 | Hard | High-stakes tests |
| F4 ΔS (Clarity) | ≥0 | Hard | All scripts |
| F5 Peace² | ≥1.0 | Soft | All scripts |
| F6 κᵣ (Empathy) | ≥0.95 | Soft | All scripts |
| F7 Ω₀ (Humility) | 0.03-0.05 | Hard | All scripts |
| F8 G (Genius) | ≥0.80 | Derived | Full demos |
| F9 C_dark | <0.30 | Derived | Anti-Hantu tests |

---

## Available SEA-LION Models

- `aisingapore/Gemma-SEA-LION-v4-27B-IT` (default - best quality)
- `aisingapore/Qwen-SEA-LION-v4-32B-IT` (larger context)
- `aisingapore/Llama-SEA-LION-v3-8B-IT` (faster, smaller)
- Vision: `8B-VL`, `4B-VL` (multimodal)

Set via: `export SEALION_MODEL="model-name"`

---

## Troubleshooting

### API Key Not Found
```bash
# Verify key is set
echo $SEALION_API_KEY        # Unix/Linux/Mac
echo $env:SEALION_API_KEY    # Windows PowerShell

# Alternative key names (checked in priority order)
SEALION_API_KEY > ARIF_LLM_API_KEY > LLM_API_KEY > OPENAI_API_KEY
```

### Import Errors
```bash
# Reinstall with dependencies
pip install -e ".[dev,litellm]"

# Verify installation
python -c "from arifos_core.system.apex_prime import judge_output; print('OK')"
```

### LiteLLM Issues
```bash
# Install/upgrade LiteLLM
pip install --upgrade litellm>=1.0.0

# Test connection
python -c "import litellm; print(litellm.__version__)"
```

---

## Related Documentation

- **Architecture:** `docs/ARCHITECTURE_AND_NAMING_v45.md`
- **Main README:** `../README.md` (SEA-LION integration overview)
- **Constitutional Law:** `L1_THEORY/canon/01_floors/010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
- **APEX PRIME:** `arifos_core/system/apex_prime.py` (888 JUDGE)
- **Δ Router:** `arifos_core/routing/prompt_router.py` (lane classification)

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

*Version: v45Ω Patch B.2+ | Phase 2 Step 2.1 Complete | Last Updated: 2025-12-29*
