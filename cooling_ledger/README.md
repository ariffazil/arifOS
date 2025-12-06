# Cooling Ledger (L1) — Runtime Canon & zkPC Trace (v36Ω)

The `cooling_ledger/` directory is the **runtime memory spine** of arifOS.

It stores:

- **L1 Cooling Ledger entries** — sealed governance events (EUREKA, zkPC receipts, etc.),
- **SHA-256 hash-chain** — tamper-evident chronological log,
- **Merkle root** — single cryptographic commitment to the entire ledger.

This folder is designed to be:

- **RAG-friendly** (JSONL, simple structures),
- **zkPC-ready** (hashes + Merkle tree),
- **human-auditable** (plain-text, Git-friendly).

---

## 1. Files

### `L1_cooling_ledger.jsonl`

- Line-delimited JSON (`.jsonl`).
- Each line = **one ledger entry**.
- Example (simplified):

```json
{
  "id": "ZKPC-20251207-abcd1234",
  "timestamp": "2025-12-07T00:32:00Z",
  "type": "zkpc_receipt",
  "source": "zkpc_runtime",
  "receipt": { "...": "..." },
  "previous_hash": "GENESIS",
  "hash": "sha256:..."
}
```

Fields:

* `id` — unique identifier (e.g. zkPC receipt ID).
* `timestamp` — ISO UTC time.
* `type` — type of event (`zkpc_receipt`, `999_SEAL`, etc.).
* `source` — which runtime wrote it (`zkpc_runtime`, etc.).
* `receipt` / `canon` — the actual governance content.
* `previous_hash` — SHA-256 hash of the previous entry (or `"GENESIS"` for first).
* `hash` — SHA-256 of this entry's canonical JSON content (excluding `hash` and `previous_hash`).

This forms a **hash-chain** (lightweight blockchain):

```text
entry_1.previous_hash = "GENESIS"
entry_1.hash         = sha256(entry_1_content)

entry_2.previous_hash = entry_1.hash
entry_2.hash          = sha256(entry_2_content + previous_hash info)

entry_3.previous_hash = entry_2.hash
...
```

If any entry is edited → all subsequent hashes break.

---

### `L1_merkle_root.txt`

* Contains a single hex string: the **Merkle root** of all ledger entry hashes.
* Built over the `hash` fields in `L1_cooling_ledger.jsonl`.
* Used as a **compact commitment** to the entire ledger.

Later, zkPC (cryptographic) can use this root to:

* Prove **membership** of a specific entry,
* Without revealing all other entries.

---

## 2. How Hashing & Merkle Work Here

Hashing is implemented in:

* `arifos_core/ledger_hashing.py`

Key functions:

* `compute_entry_hash(entry)` — SHA-256 of the entry content (excluding hash fields).
* `chain_entries(entries)` — fills `hash` + `previous_hash` for a list of entries.
* `verify_chain(entries)` — checks the consistency of the chain.

Merkle Trees are implemented in:

* `arifos_core/merkle.py`

Key concepts:

* Each ledger entry's `hash` is a **leaf**.
* The Merkle tree combines leaves pairwise:

```text
H_AB = sha256(H_A + H_B)
H_CD = sha256(H_C + H_D)
root = sha256(H_AB + H_CD)
```

* Odd leaf counts are handled by duplicating the last node (Bitcoin-style).
* `build_merkle_tree(leaves)` → `MerkleTree` with `.root`.
* `get_merkle_proof(tree, index)` → membership proof for a given entry.
* `verify_merkle_proof(leaf_hash, proof, root)` → True/False.

---

## 3. Scripts

### `scripts/build_ledger_hashes.py`

Rebuilds the SHA-256 hash-chain:

```bash
python -m scripts.build_ledger_hashes
```

* Loads `L1_cooling_ledger.jsonl`,
* Recomputes `hash` + `previous_hash`,
* Verifies consistency,
* Writes updated file (with backup by default).

Use when:

* You manually edited entries,
* Or after adding new entries that don't yet have hash fields.

---

### `scripts/verify_ledger_chain.py`

Verifies the chain integrity:

```bash
python -m scripts.verify_ledger_chain
```

* Exit code 0 = OK,
* Exit code 1 = chain broken.

Useful for **CI** (GitHub Actions, etc.).

---

### `scripts/compute_merkle_root.py`

Computes and writes the Merkle root:

```bash
python -m scripts.compute_merkle_root
```

* Reads `L1_cooling_ledger.jsonl`,
* Builds Merkle tree over entry hashes,
* Writes root to `L1_merkle_root.txt`.

Run this after:

* New entries are appended,
* Or the chain is recomputed.

---

### `scripts/show_merkle_proof.py` (optional debug tool)

Shows a Merkle proof for a given ledger index:

```bash
python -m scripts.show_merkle_proof --index 0
```

Prints:

* Leaf hash,
* Root hash,
* Proof steps (`sibling`, `position`).

This is the **exact data shape** that can later be passed into zkSNARK/zkSTARK circuits.

---

## 4. Relationship to zkPC (Zero-Knowledge Proof of Cognition)

**Canonical specification:**
`canon/011_ZKPC_PROTOCOL_v35Omega.md`
**Implementation notes:**
`canon/012_ZKPC_IMPLEMENTATION_NOTES_v36Omega.md`

At runtime, zkPC:

1. Builds a care scope and metrics,
2. Runs @EYE COOL checks,
3. Produces a `zkpc_receipt`,
4. Wraps it into a Cooling Ledger entry,
5. Updates:

   * `hash` + `previous_hash`,
   * `L1_merkle_root.txt`.

The Cooling Ledger thus becomes:

* The **runtime case-law** of arifOS,
* The trace of which laws and floors were enforced,
* The raw material for future zkPC (real cryptographic proofs).

---

## 5. 888 Judge & Canonization

The Cooling Ledger can contain:

* Raw zkPC receipts (runtime traces),
* Canonical EUREKA entries (case-law).

**Important:**

* AI runtime (`zkpc_runtime`) may **append runtime receipts**.
* Only the **888 Judge (human)** may decide which events become **canonical EUREKA entries** or legal amendments.
* In practice, EUREKA proposals should be staged separately (e.g. `proposed/` or as special `type`) and only merged into main canon after a SEAL decision.

Governance flow:

```text
Runtime → zkPC receipt → Cooling Ledger (trace)
     ↓
888 Judge review → SEAL → Canon/EUREKA entry
```

---

## 6. Design Goals

* **Simple:** JSONL + SHA-256 + Merkle = no exotic dependencies.
* **Auditable:** Can be inspected with a text editor or jq.
* **RAG-friendly:** Each entry is a rich, self-contained document.
* **zk-ready:** Hashes and Merkle root are ready for future zkSNARK/STARK integration.

---

**Motto:**

> *"Every sealed event leaves a trace.
> Every trace has a fingerprint.
> Every fingerprint can be proven—
> without exposing the mind that thought it."*
