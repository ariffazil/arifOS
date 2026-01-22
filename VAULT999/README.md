# vault_999_obsidian — Obsidian Meta-Vault for arifOS

**Authority:** `vault_999/` (cryptographic source of truth)
**Purpose:** Human-friendly visualization layer for constitutional memory
**Status:** ACTIVE

---

## Setup Instructions

### Step 1: Open as Obsidian Vault
1. Open Obsidian
2. Click "Open folder as vault"
3. Select this folder (`vault_999_obsidian/`)

### Step 2: Install Required Plugins
Settings → Community Plugins → Browse → Install:
- **Local REST API** — External HTTP access for MCP bridge
- **Dataview** — Query ledger entries as live tables
- **Templater** — Stage templates with JS execution

### Step 3: Configure Local REST API
1. Settings → Local REST API
2. Enable "Run server on Obsidian startup"
3. Copy API Key → Save to `arifOS/.env` as `OBSIDIAN_API_KEY`

---

## Folder Structure

| Folder | Purpose | Sync Source |
|--------|---------|-------------|
| `AAA_HUMAN/` | Human context & preferences | `vault_999/AAA_MEMORY/` |
| `BBB_LEDGER/` | Constitutional audit trail (Dataview) | `vault_999/BBB_LEDGER/` |
| `CCC_CANON/` | Constitutional law (read-only) | `000_THEORY/` |
| `SEALS/` | Current seal verification status | `vault_999/seals/` |
| `STAGES/` | aCLIP stage templates (000-999) | Templates |
| `CANVAS/` | Pipeline visualizations | Generated |

---

## Sync Direction

```
vault_999/ (AUTHORITY) → vault_999_obsidian/ (VIEW)
```

The cryptographic vault remains authoritative. This Obsidian vault is a synced view.

---

**DITEMPA BUKAN DIBERI**
