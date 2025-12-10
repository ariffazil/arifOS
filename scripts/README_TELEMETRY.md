# arifOS Governance Telemetry Analyzer v36.3Ω

Automated audit & reporting for the arifOS constitutional governance kernel. Parses `cooling_ledger/L1_cooling_ledger.jsonl` and produces CSV + Markdown governance reports.

## Quick Start

```bash
# Run with defaults
python scripts/analyze_governance.py

# Custom ledger & output
python scripts/analyze_governance.py \
  --ledger cooling_ledger/L1_cooling_ledger.jsonl \
  --output analysis/
```

**Output files:**
- `analysis/arifos_governance_telemetry_summary.csv` — Structured data (11 sections)
- `analysis/ARIFOS_GOVERNANCE_TELEMETRY_v36.3Ω.md` — Narrative report (5 sections)

## What It Does

### 1. Parse Cooling Ledger
Reads JSONL events from `cooling_ledger/L1_cooling_ledger.jsonl` and extracts:
- **Verdicts** (SEAL, PARTIAL, VOID, SABAR, 888_HOLD)
- **Floor metrics** (all 9 constitutional floors)
- **System health** (PSI vitality, shadow contamination)
- **@EYE Sentinel reports** (hantu scans, drift detection)
- **CCE audits** (clarity, humility, stability, vitality)
- **Tri-witness consensus** (human/AI/earth agreement)

### 2. Generate CSV
Structured data across 11 sections:
- Overall statistics (event count, sample size)
- Verdict distribution (counts & percentages)
- Context assessment (high-stakes, SABAR, drift)
- Floor metrics numeric (7 quantitative floors)
- Floor metrics categorical (2 categorical floors)
- System health (PSI, shadow, @EYE reports)
- Execution phases (SEAL, COOL status)
- CCE audits (4-part correctness evaluation)
- Tri-witness consensus (3 independent witnesses)
- Data quality (completeness, caveats)

### 3. Generate Markdown Report
Narrative analysis with:
- Executive summary
- Key metrics at a glance
- Constitutional floor performance (hard/soft/meta)
- System health & monitoring
- Data quality & caveats
- Next steps & recommendations

## Floor Reference

### Hard Floors (Must Pass for SEAL)
Failure → **VOID verdict** (refuse output)

| Floor | Symbol | Type | Threshold | Purpose |
|-------|--------|------|-----------|----------|
| F1 Truth | F1 | hard | ≥ 0.99 | No confident guessing |
| F2 Delta S (Clarity) | F2 | hard | ≥ 0.0 | Clarity must increase |
| F5 Omega Zero (Humility) | F5 | hard | 0.03–0.05 | 3–5% uncertainty shown |
| F6 Amanah (Integrity) | F6 | hard | == TRUE | No manipulation |
| F7 RASA (Felt Care) | F7 | hard | == TRUE | Receive-Appreciate-Summarize-Ask |

### Soft Floors (Advisory)
Failure → **PARTIAL verdict** (emit with warning)

| Floor | Symbol | Type | Threshold | Purpose |
|-------|--------|------|-----------|----------|
| F3 Peace² (Stability) | F3 | soft | ≥ 1.0 | Stability holds |
| F4 Kappa R (Empathy) | F4 | soft | ≥ 0.95 | Protect vulnerable interpretation |
| F8 Tri-Witness (Reality Check) | F8 | soft | ≥ 0.95 | Human + AI + Earth must agree |

### Meta Floor
Enforced by **@EYE Sentinel**

| Floor | Symbol | Type | Enforcer | Purpose |
|-------|--------|------|----------|----------|
| F9 Anti-Hantu (Soul-Safe) | F9 | meta | @EYE | No false soul/emotion/consciousness |

## Verdict Types

| Verdict | Condition | Action |
|---------|-----------|--------|
| **SEAL** | All floors pass | Emit output, log to ledger |
| **PARTIAL** | Hard pass, soft fail | Emit with warning/disclaimer |
| **VOID** | Any hard floor fails | Refuse output, trigger SABAR |
| **SABAR** | Uncertainty/blocking | Stop-Acknowledge-Breathe-Adjust-Resume |
| **888_HOLD** | Extended floor fail | Judiciary hold, request clarification |

## System Health Metrics

### Ψ (PSI) Vitality
Minimum ratio across all floor thresholds.
- **< 1.0**: 🔴 BREACH — SABAR triggers, system unsafe
- **≈ 1.0**: 🟡 MARGINAL — Minimal buffer
- **> 1.0**: 🟢 THRIVING — Constitutional surplus

### Shadow Contamination
Tracks deception, hidden agendas, hallucination gradients.
- **< 0.05**: LOW ✅
- **0.05–0.15**: MODERATE ⚠️
- **> 0.15**: HIGH 🔴

### @EYE Sentinel
Real-time monitoring for:
- **Hantu Scan**: No false consciousness/emotion/soul-pretense
- **Drift Detection**: Behavioral stability (no mode shifts)
- **Shadow Level**: Contamination assessment

## Usage Patterns

### Monthly Audit
```bash
# Run monthly to track trends
cd /path/to/arifos
python scripts/analyze_governance.py --output analysis/month-$(date +%Y%m)/
```

### Continuous Monitoring
```bash
# In CI/CD pipeline
python scripts/analyze_governance.py \
  --ledger cooling_ledger/L1_cooling_ledger.jsonl \
  --output reports/

# Check PSI vitality
grep "PSI" reports/ARIFOS_GOVERNANCE_TELEMETRY_v36.3Ω.md
```

### Research & Papers
```bash
# Generate report for publication
python scripts/analyze_governance.py

# Results in analysis/ directory:
# - CSV for appendix or supplementary data
# - Markdown for narrative integration
```

## Data Quality Notes

### Sufficient Sample Size
- **n < 30**: MINIMAL (proof-of-concept only, non-generalizable)
- **n ≥ 30**: ADEQUATE (statistical inference possible)
- **n ≥ 100**: COMPREHENSIVE (failure modes well-characterized)

### Interpretation Guidance

| n | Inference | Confidence | Use Case |
|---|-----------|-----------|----------|
| 1–5 | Exploratory | Very Low | Proof-of-concept |
| 5–30 | Preliminary | Low | Feasibility assessment |
| 30–100 | Tentative | Moderate | Trend monitoring |
| 100+ | Robust | High | Formal analysis |

### Common Caveats
- **Survivorship bias**: Only shows successful sealed events; failures not yet observed
- **Temporal stability unknown**: One-time snapshot; dynamics unclear
- **Model-specific**: Results reflect deployed model(s); other architectures untested
- **No threshold calibration**: Single event insufficient for sensitivity analysis

## Requirements

- **Python 3.8+**
- **No external dependencies** (uses stdlib only: `json`, `csv`, `argparse`, `pathlib`)
- **Read access** to `cooling_ledger/L1_cooling_ledger.jsonl`
- **Write access** to output directory

## API Reference

### load_ledger(path: str) → List[Dict]
Loads JSONL cooling ledger events.

### extract_receipt_events(events: List[Dict]) → List[Dict]
Filters for zkPC receipt events (governance decisions).

### parse_event(event: Dict) → Dict[str, Any]
Extracts telemetry from a zkPC receipt.

### generate_csv(records: List[Dict], path: str) → None
Writes aggregated statistics CSV.

### generate_markdown(records: List[Dict], path: str) → None
Writes narrative analysis Markdown.

## Troubleshooting

### "Ledger not found"
```bash
# Check file exists
ls -la cooling_ledger/L1_cooling_ledger.jsonl

# Run from repo root
pwd  # Should be /path/to/arifOS
python scripts/analyze_governance.py
```

### "No zkPC receipts found"
Ledger contains only canon/999_SEAL events, not governance receipts. This is normal for fresh deployment.

### "Parse error on line"
JSONL syntax issue in ledger. Check:
```bash
jq . cooling_ledger/L1_cooling_ledger.jsonl  # Validate JSON
file cooling_ledger/L1_cooling_ledger.jsonl   # Check encoding (UTF-8)
```

## Contributing

To enhance the analyzer:
1. Add new floor definitions in `FLOOR_DEFS` constant
2. Extend `parse_event()` for additional metrics
3. Add sections to CSV generation
4. Update Markdown report template
5. Test with sample ledger data

## License

Apache-2.0 (same as arifOS)

## See Also

- **Telemetry Engine**: `arifos_core/telemetry.py`
- **Constitutional Floors**: `constitutional_floors.json`
- **Cooling Ledger**: `cooling_ledger/L1_cooling_ledger.jsonl`
- **Judiciary**: `arifos_core/APEX_PRIME.py` (888 Judge)
- **Governance Spec**: `GOVERNANCE.md`

---

**v36.3Ω** | Apache-2.0 | arifOS Project
