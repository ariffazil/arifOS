# Glass-box MCP Surface (`arifos_core/mcp/`)

This surface is designed for **IDE integration, debugging, and forensic research**. It provides full transparency into the constitutional pipeline.

## Overview

Unlike the black-boxauthority (`L4_MCP/`), the glass-box surface exposes the internal metabolic stages of the arifOS pipeline as individual tools. This allows developers and auditors to "step through" the governance process.

## Tools (17 Composable)

| Tool | Phase | Purpose |
|------|-------|---------|
| `mcp_000_reset` | 000 | Initialize governance session |
| `mcp_111_sense` | 111 | Lane classification (HARD/SOFT/PHATIC/REFUSE) |
| `mcp_222_reflect` | 222 | Epistemic honesty & humility prediction |
| `mcp_444_evidence` | 444 | Truth grounding via tri-witness convergence |
| `mcp_555_empathize`| 555 | Power-aware recalibration (Peace² & κᵣ) |
| `mcp_666_align` | 666 | Absolute veto gates (F1, F8, F9) |
| `mcp_777_forge` | 777 | Clarity refinement & humility injection |
| `mcp_888_judge` | 888 | Final verdict aggregation |
| `mcp_889_proof` | 889 | Cryptographic proof (Merkle tree) generation |
| `mcp_999_seal` | 999 | Final verdict sealing & memory routing |
| `arifos_judge` | - | High-level wrapper (Stage 000→999 shortcut) |
| `arifos_recall` | - | Query memory bands (L7) |
| `arifos_audit` | - | Verify ledger integrity |
| `arifos_fag_read` | - | Governed file access (FAG) |
| `APEX_LLAMA` | - | Local un-governed Llama helper |
| `arifos_validate_full` | - | Track A/B/C full floor validation |
| `arifos_meta_select`| - | Track A/B/C consensus aggregation |

## Storage & Ledger

- **Format:** JSON Lines (`.jsonl`) + Merkle Tree pathing.
- **Backend:** File-system based (portable, human-readable).
- **Philosophy:** Auditability over performance.
- **Verdicts:** Supports `PARTIAL` (conditional pass).

## IDE Integration

This surface is the default for:

- **Cursor `.cursorrules`**
- **VS Code Copilot**
- **Aider / Devin**

It allows the AI to explicitly call `reset`, `judge`, and `seal` to demonstrate constitutional compliance to the user.

---

**DITEMPA BUKAN DIBERI**
