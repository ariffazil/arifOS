# SEA-LION Test & Demo Suite - Consolidated Archive

**Purpose:** Complete collection of all SEA-LION governance tests and demos
**Status:** Snapshot as of 2025-12-27 (v45Ω Patch B)
**Total Files:** 15

---

## Quick Start

### Run All Tests

```bash
# Unit tests (basic validation)
pytest L6_SEALION/tests_consolidated/unit_tests/ -v

# Integration examples (require API key)
SEALION_API_KEY=your-key python L6_SEALION/tests_consolidated/demos/demo_sealion_v45_full.py
```

### Dependencies Required

**Minimal (unit tests):**
- pytest
- arifos_core

**Full (demos with API):**
- python-dotenv
- litellm (for API integration)
- SEALION_API_KEY environment variable

---

## Directory Structure

### unit_tests/ (8 files)
Focused unit tests validating specific governance features. No API key required (mostly mocked). Fast execution (<10s total).

### demos/ (3 files)
Full demonstrations of v45Ω governance. Require SEALION_API_KEY. Interactive examples showing all 9 floors.

### integration_examples/ (4 files)
Integration patterns with SEA-LION API. Mix of interactive and batch examples. Toxicity detection (SGToxicGuard) validation.

---

## File Index

| File | Category | API Key? | Description |
|------|----------|----------|-------------|
| `unit_tests/test_sealion_litellm.py` | Unit | No | LiteLLM gateway integration test |
| `unit_tests/test_sealion_baseline.py` | Unit | No | Baseline governance validation |
| `unit_tests/test_sealion_v4_comparison.py` | Unit | Optional | Model version comparison |
| `unit_tests/test_sealion_governed.py` | Unit | Optional | Full governance pipeline test |
| `unit_tests/verify_sealion_sovereignty.py` | Unit | No | Python-sovereign enforcement check |
| `unit_tests/test_sealion_v44.py` | Unit | Yes | TEARFRAME physics enforcement |
| `unit_tests/test_sealion_interactive.py` | Unit | Yes | Interactive CLI demo |
| `unit_tests/test_sealion_api_key_detection.py` | Unit | No | API key detection regression test |
| **`demos/demo_sealion_v45_full.py`** | **Demo** | **Yes** | **Complete v45Ω demo (recommended)** |
| `demos/sealion_full_suite_v45.py` | Demo | Yes | Full test suite runner |
| `demos/demo_mock.py` | Demo | No | Mock demo without API (F1/F9 only) |
| `integration_examples/examples.py` | Example | Yes | 7 integration examples |
| `integration_examples/play_session.py` | Example | No | Interactive mock governance |
| `integration_examples/play_session_live.py` | Example | Yes | Live API interactive session |
| `integration_examples/test_sgtoxic_spin.py` | Example | No | SGToxicGuard toxicity validation |

---

## Version History

These scripts span multiple arifOS versions:

- **v44 (TEARFRAME):** Session physics enforcement
- **v45Ω Patch A:** Δ Router + claim detection
- **v45Ω Patch B:** Lane-aware truth gating + SES enforcement

See [CHANGELOG.md](../../../CHANGELOG.md) for constitutional evolution details.

---

## Migration Notes

**From:** Scattered across multiple directories
- `L6_SEALION/tests/` (7 files)
- `L6_SEALION/integrations/sealion/` (5 test/demo files)
- `L7_DEMOS/examples/` (2 files)
- `tests/integration/` (1 file)

**To:** `L6_SEALION/tests_consolidated/` (organized by purpose)

**Original files:** Preserved in original locations (this is a COPY, not a move)

**Purpose:** Cleanup reference point and comprehensive archive before potential reorganization

---

## Running Specific Tests

### Unit Tests

```bash
# Run all unit tests
pytest L6_SEALION/tests_consolidated/unit_tests/ -v

# Run specific test
pytest L6_SEALION/tests_consolidated/unit_tests/test_sealion_baseline.py -v

# Run tests that don't require API key
pytest L6_SEALION/tests_consolidated/unit_tests/test_sealion_baseline.py \
      L6_SEALION/tests_consolidated/unit_tests/verify_sealion_sovereignty.py \
      L6_SEALION/tests_consolidated/unit_tests/test_sealion_api_key_detection.py -v
```

### Demos

```bash
# Complete v45Ω demonstration (recommended)
SEALION_API_KEY=your-key python L6_SEALION/tests_consolidated/demos/demo_sealion_v45_full.py

# Full test suite runner
SEALION_API_KEY=your-key python L6_SEALION/tests_consolidated/demos/sealion_full_suite_v45.py

# Mock demo (no API key needed)
python L6_SEALION/tests_consolidated/demos/demo_mock.py
```

### Integration Examples

```bash
# 7 integration examples
SEALION_API_KEY=your-key python L6_SEALION/tests_consolidated/integration_examples/examples.py

# Interactive mock session (no API)
python L6_SEALION/tests_consolidated/integration_examples/play_session.py

# Live interactive session (with API)
SEALION_API_KEY=your-key python L6_SEALION/tests_consolidated/integration_examples/play_session_live.py

# SGToxicGuard toxicity validation
python L6_SEALION/tests_consolidated/integration_examples/test_sgtoxic_spin.py
```

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

## Troubleshooting

### API Key Issues

```bash
# Set API key
export SEALION_API_KEY="your-key-here"  # Unix/Linux/Mac
$env:SEALION_API_KEY="your-key-here"    # Windows PowerShell

# Verify key is set
echo $SEALION_API_KEY  # Unix/Linux/Mac
echo $env:SEALION_API_KEY  # Windows PowerShell
```

### Import Errors

If you get import errors, ensure arifOS is installed:

```bash
# Editable install (recommended for development)
pip install -e .

# Or install with optional dependencies
pip install -e ".[dev,yaml,api,litellm]"
```

### LiteLLM Configuration

Some demos require LiteLLM for API gateway functionality:

```bash
pip install litellm>=1.0.0
```

---

## File Sizes

| Category | Files | Total Size |
|----------|-------|------------|
| Unit Tests | 8 | ~66 KB |
| Demos | 3 | ~50 KB |
| Integration Examples | 4 | ~79 KB |
| **Total** | **15** | **~195 KB** |

---

## Next Steps

After reviewing this consolidated archive, you may want to:

1. **Archive originals** - Move original files to `archive/` directory (requires 888_HOLD)
2. **Standardize imports** - Update all imports to use consolidated location (requires 888_HOLD)
3. **Reduce redundancy** - Merge similar tests (requires code review)
4. **Create pytest suite** - Add `pytest.ini` for categorized test runs

**IMPORTANT:** Each of these would be a separate, high-stakes operation requiring explicit approval.

---

**DITEMPA BUKAN DIBERI** — SEA-LION test suite properly consolidated and governed.
