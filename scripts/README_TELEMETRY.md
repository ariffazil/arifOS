# Governance Telemetry Analyzer (v36.3Ω)

This tool analyzes the Cooling Ledger (`L1_cooling_ledger.jsonl`) and produces
human‑ and machine‑readable summaries of how well the arifOS constitutional
floors are being enforced in practice.

It is **read‑only** and uses only the Python standard library.

---

## What It Does

`scripts/analyze_governance.py`:

- Reads each JSONL entry from `cooling_ledger/L1_cooling_ledger.jsonl`
- Extracts:
  - Verdict (`SEAL`, `PARTIAL`, `VOID`, `SABAR`, etc.)
  - Floor metrics from `receipt.metrics`:
    - `truth`, `delta_s`, `peace_squared`, `kappa_r`, `omega_0`,
      `amanah`, `rasa`, `tri_witness`, `anti_hantu`, `psi`, `shadow`
  - @EYE fields from `receipt.eye_report`:
    - `drift_detected`, `hantu_scan`
  - Tri‑Witness consensus from `receipt.tri_witness.consensus`
- Computes per‑floor pass/fail flags using v36.3Ω thresholds
- Writes:
  - `analysis/arifos_governance_telemetry_summary.csv`
  - `analysis/ARIFOS_GOVERNANCE_TELEMETRY_v36.3O.md`

---

## Usage

From the repo root:

```bash
python scripts/analyze_governance.py
```

Optional arguments:

```bash
python scripts/analyze_governance.py \
  --ledger cooling_ledger/L1_cooling_ledger.jsonl \
  --output analysis/
```

This will create (or reuse) the `analysis/` directory.

---

## CSV Output

`analysis/arifos_governance_telemetry_summary.csv` has one row per governed
event and columns including:

- `event_id`, `timestamp`, `source`, `verdict`
- Raw floor metrics:
  - `truth`, `delta_s`, `peace_squared`, `kappa_r`, `omega_0`,
    `amanah`, `rasa`, `tri_witness`, `anti_hantu`, `psi`, `shadow`
- @EYE and Tri‑Witness:
  - `sabar_triggered`, `drift_detected`, `hantu_scan`,
    `tri_witness_consensus`
- Per‑floor pass flags:
  - `F1_truth_pass` … `F9_anti_hantu_pass`

This is suitable for spreadsheets or BI dashboards.

---

## Markdown Report

`analysis/ARIFOS_GOVERNANCE_TELEMETRY_v36.3O.md` contains:

- Verdict distribution table
- Aggregated health metrics:
  - Average Ψ (psi)
  - Average shadow
  - Average Tri‑Witness consensus
- Per‑event floor pass overview (F1–F9)
- Notes and caveats (including the need for sufficient sample size)

The report is designed to be copy‑pasted into audits, research notes, or
transparency documents.

---

## Safety & Limitations

- The script **never** modifies the Cooling Ledger; it only reads from it.
- It currently considers only entries with a `receipt` payload (e.g. `zkpc_receipt`);
  other ledger lines (such as proposed canon entries) are ignored.
- Statistical conclusions require enough data:
  - For meaningful trends, aim for ≥30 governed events.

---

## Next Steps

- Run the analyzer periodically (e.g. monthly) to:
  - Track SEAL/PARTIAL/VOID/SABAR distributions
  - Monitor Ψ vitality and shadow over time
  - Spot weak floors (those that frequently fail or run near thresholds)
- Extend the script if you add new metrics to the ledger schema, while keeping
  it aligned with v36.3Ω canon and specs.

