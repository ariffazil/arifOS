# arifOS CLI Tools — Command Reference

After `pip install arifos`, you can run these governance tools from any directory:

## Telemetry & Audit

### `arifos-analyze-governance`
Analyze cooling ledger events and generate governance audit reports.

```bash
arifos-analyze-governance \
  --ledger cooling_ledger/L1_cooling_ledger.jsonl \
  --output analysis/
```

**Output:**
- `analysis/arifos_governance_telemetry_summary.csv` — Structured audit data (11 sections)
- `analysis/ARIFOS_GOVERNANCE_TELEMETRY_v36.3Ω.md` — Narrative governance report

**Caveat:** Requires n≥30 events for statistical validity (n<30 = proof-of-concept only).

See: `scripts/README_TELEMETRY.md`

---

## Ledger & Chain Verification

### `arifos-verify-ledger`
Verify cooling ledger SHA-256 hash chain integrity.

```bash
arifos-verify-ledger
```

**Exit codes:**
- `0` — Chain verified, no tampering detected
- `1` — Chain broken or ledger corrupted
- `2` — Ledger file not found

**Usage in CI/CD:**
```bash
arifos-verify-ledger || { echo "Ledger integrity breach"; exit 1; }
```

### `arifos-compute-merkle`
Compute SHA-256 Merkle root from cooling ledger entries.

```bash
arifos-compute-merkle
```

**Output:** Merkle root hash (stdout)

### `arifos-build-ledger-hashes`
Rebuild SHA-256 hash chain for cooling ledger.

```bash
arifos-build-ledger-hashes
```

**Use when:** Ledger entries added manually or chain needs refresh.

### `arifos-show-merkle-proof`
Display Merkle proof for a specific cooling ledger entry.

```bash
arifos-show-merkle-proof --index 0
```

**Output:** Merkle proof path + root hash.

---

## Governance & Canon

### `arifos-propose-canon`
888 Judge tool: propose constitutional amendments from zkPC receipts.

```bash
# List zkPC receipts in ledger
arifos-propose-canon --list

# Propose canon from receipt at index 0
arifos-propose-canon --index 0

# Output: cooling_ledger/proposed/PROPOSED_CANON_<receipt_id>.json
```

**Workflow:**
1. Review proposed canon file
2. Edit as needed (human governance)
3. Pass file to `arifos-seal-canon` to finalize

### `arifos-seal-canon`
Phoenix-72 SEAL tool: finalize and commit proposed canon.

```bash
arifos-seal-canon --file cooling_ledger/proposed/PROPOSED_CANON_XXX.json
```

**Effect:**
- Moves proposed canon to `canon/SEALED_CANON_<receipt_id>.md`
- Writes 999_SEAL entry to cooling ledger
- Commits to Git (optional flag: `--no-git`)

**Permission:** Human-only (no AI auto-seal)

---

## Installation & Setup

### From PyPI (Recommended)

```bash
pip install arifos
```

All CLI commands become available immediately.

### From Source (Development)

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .[dev]
```

CLI commands are registered via `pyproject.toml [project.scripts]`.

### From Cloned Repo (Legacy)

```bash
python scripts/analyze_governance.py --ledger cooling_ledger/L1_cooling_ledger.jsonl
```

Works without `pip install`, but tools not in `$PATH`.

---

## Environment Variables

### `ARIFOS_LEDGER_PATH`
Default cooling ledger location (overrides `--ledger`).

```bash
export ARIFOS_LEDGER_PATH=/path/to/cooling_ledger/L1_cooling_ledger.jsonl
arifos-analyze-governance
```

### `ARIFOS_CANON_DIR`
Default canon directory for seal operations (overrides `canon/`).

```bash
export ARIFOS_CANON_DIR=/path/to/canon
arifos-seal-canon --file proposed/PROPOSED_CANON_XXX.json
```

---

## Troubleshooting

### "Command not found: arifos-analyze-governance"

1. Verify installation:
   ```bash
   pip show arifos | grep Location
   ```

2. Check if `scripts` package is in site-packages:
   ```bash
   python -c "import scripts; print(scripts.__file__)"
   ```

3. Reinstall if missing:
   ```bash
   pip install --force-reinstall arifos
   ```

### "Ledger file not found"

```bash
# Run from repo root
cd /path/to/arifOS
arifos-analyze-governance --ledger cooling_ledger/L1_cooling_ledger.jsonl

# Or set env var
export ARIFOS_LEDGER_PATH=$(pwd)/cooling_ledger/L1_cooling_ledger.jsonl
arifos-analyze-governance
```

### "No zkPC receipts found"

Ledger contains only canon events, not governance receipts. This is normal for a fresh deployment.

**Remedy:** Feed queries through the governance kernel to populate receipts:
```bash
python scripts/arifos_caged_llm_zkpc_demo.py --query "Explain Amanah" --high-stakes
```

---

## API Usage (Programmatic)

```python
from scripts.analyze_governance import main
import sys

# Run analyzer with custom arguments
sys.argv = [
    'arifos-analyze-governance',
    '--ledger', 'cooling_ledger/L1_cooling_ledger.jsonl',
    '--output', 'analysis/',
]
main()
```

---

## See Also

- **Telemetry Reference:** `scripts/README_TELEMETRY.md`
- **Governance Spec:** `GOVERNANCE.md`
- **zkPC Protocol:** `canon/011_ZKPC_PROTOCOL_v35Omega.md`
- **Phoenix-72 Workflow:** `README.md` (zkPC + Phoenix-72 Workflow section)

---

**Version:** 36.3.0 | **License:** Apache-2.0 | **Last Updated:** 2025-12-10
