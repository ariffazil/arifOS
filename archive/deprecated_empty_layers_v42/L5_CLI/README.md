# L5_CLI — Command Line Tools

**Layer:** L5
**Purpose:** Unified CLI for governance operations
**License:** AGPL-3.0

---

## What Lives Here

| Directory | Contents |
|-----------|----------|
| `arifos_cli/` | Main CLI package |
| `arifos_cli/commands/` | Individual command implementations |
| `arifos_cli/utils/` | CLI utilities |
| `tests/` | CLI-specific tests |

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| `arifos verify` | Verify ledger hash-chain integrity |
| `arifos analyze` | Analyze governance decisions |
| `arifos merkle` | Show Merkle proof for entry |
| `arifos propose` | List/propose canon amendments |
| `arifos seal` | Phoenix-72 finalization |
| `arifos read` | FAG-governed file read |
| `arifos organize` | Organize repo structure |

---

## Dependency Rules

```
L5_CLI ← Users interact via CLI
       → Imports from L3_KERNEL (arifos_core)
       → May use L4_MCP tools
       → NEVER imports from higher layers
```

---

## Usage

```bash
# Install
pip install arifos

# Unified CLI
arifos --help

# Verify ledger integrity
arifos verify --ledger cooling_ledger/L1_cooling_ledger.jsonl

# Analyze governance
arifos analyze --output report.json

# Show Merkle proof
arifos merkle --index 0

# List amendment proposals
arifos propose --list

# Safe file read
arifos read path/to/file.py
```

---

## Legacy Commands (Backward Compatibility)

These legacy commands still work but emit deprecation warnings:

```bash
arifos-verify-ledger        # → arifos verify
arifos-analyze-governance   # → arifos analyze
arifos-show-merkle-proof    # → arifos merkle
arifos-propose-canon        # → arifos propose
arifos-seal-canon           # → arifos seal
arifos-safe-read            # → arifos read
```

---

**DITEMPA BUKAN DIBERI** — Command-line governance for the terminal.
