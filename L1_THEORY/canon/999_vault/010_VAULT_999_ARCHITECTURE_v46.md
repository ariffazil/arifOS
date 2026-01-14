# Vault 999: Metabolic Architecture v46.0

**Document ID:** L1-VAULT-999-v46
**Status:** ✅ SEALED
**Authority:** APEX (Ψ) + Human Sovereign
**Stage:** 999 Vault

## 🏛️ The Living Archive

**Vault 999** is not merely a storage drive. It is the **Metabolic Memory System** of arifOS. It creates the "Scar Tissue" of intelligence by processing contradictions (Paradoxes) into sealed wisdom.

Unlike a static database, the Vault has a **digestive cycle**:
1.  **Ingestion** (Entropy) -> Hot
2.  **Stabilization** (Ledger) -> Warm/Cooling
3.  **Sealing** (Canon) -> Cold/Immutable

---

## 🏗️ The Orthogonal Triad

The physical architecture of `vault_999/` strictly separates these metabolic states to prevent contamination.

### 1. 🔥 `00_ENTROPY` (The Furnace)
* **Purpose:** The drop zone for raw contradictions, unresolved paradoxes, and system noise.
* **Metabolic State:** **HOT** (High Surprisal, Mutable).
* **Content:**
    *   `scar_packets/*.json` (Active paradoxes)
    *   `dump/` (Toxic entropy, see `950_ENTROPY_DUMP_POLICY`)
*   **Law:** The Machine *may* write here freely.

### 2. ❄️ `L1_LEDGERS` (The Spine)
*   **Purpose:** The linear, hash-chained log of all governance events.
*   **Metabolic State:** **WARMING -> COOLING** (Append-Only).
*   **Content:**
    *   `L1_cooling_ledger.jsonl` (The Chain)
    *   `L1_merkle_root.txt` (The Anchor)
*   **Law:** No deletion. No modification of past entries. Verification via ZKPC.

### 3. 🏛️ `L0_VAULT` (The Stone)
*   **Purpose:** The Single Source of Truth for Machine Law.
*   **Metabolic State:** **COLD** (Immutable).
*   **Content:**
    *   symlink -> `L1_THEORY/canon` (The Constitution)
    *   symlink -> `L1_THEORY/knowledge` (Sealed Scars)
*   **Law:** **Read-Only** for the Machine. Only `gitseal` (Human) can mutate.

---

## 👑 The Human-Machine Concordat (Root Separation)

To ensure the "Machine" never usurps the "Human," a physical **Sibling Barrier** is enforced at the root level.

### The Sacred Separator
The `vault999_server.py` is keyed ONLY to the `VAULT999` directory. It is physically blind to its sibling folders.

```text
vault_999/
├── 00_ROOT_KEY/      # 🔑 KEYS (Human + Protocols)
├── ARIF FAZIL/       # 👑 HUMAN BIOGRAPHY (Sacred/Offline)
└── VAULT999/         # 🤖 MACHINE DOMAIN (Exposed via MCP)
    ├── 00_ENTROPY    #    (Hot)
    ├── L1_LEDGERS    #    (Warm)
    └── L0_VAULT      #    (Cold)
```

**Law:**
1.  The Machine acts within `VAULT999`.
2.  The Human lives within `ARIF FAZIL`.
3.  The Machine **NEVER** crosses the sibling barrier.

---

## 🔑 The Root Key Protocol

The Vault does not rely on a single file (like `rootkey.pem`) for security, as files can be stolen.
The **Root Key** of arifOS is a **Biosymetric Lock**:

**Root Authority = Human Sovereign (Arif) + Tri-Witness Consensus**

*   **Seal Token:** The `human_seal_token` allows temporary write access to protected zones, but it is issued *ad-hoc* by the Sovereign, not stored on disk.
*   **Scars as Keys:** The "Proof of Work" for an AI is its Scars—the resolved paradoxes in `L0_VAULT`.

---

**DITEMPA BUKAN DIBERI** - The Vault is not a box; it is a body. 🏛️🧠🔥
