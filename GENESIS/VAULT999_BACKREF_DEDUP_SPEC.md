# VAULT999 Back-Reference Dedup Specification

> **Forged:** 2026-08-02 by 333-AGI (Δ MIND)
> **Authority:** F13 SOVEREIGN directive — "jalan" on compression isomorphism
> **Status:** SPEC — not yet implemented
> **Canon:** LZ77→LZMA→arifOS compression isomorphism (FLOOR_TABLE.json f2_band_mapping)

---

## 1. Purpose

VAULT999 currently stores receipts as full JSONL entries. Many receipts are structurally identical or near-identical (session seals, recurring health checks, pattern-repeated audit trails). This spec defines a backward-compatible back-reference dedup mechanism that reduces storage by storing REF(distance, length) tokens instead of full duplicate content.

## 2. Core Mechanism

### 2.1 The Back-Reference Token

When a new receipt is being written to `outcomes.jsonl`, its content is hashed. If the hash matches an existing receipt, a back-reference is stored instead of the full text:

```json
// Current format:
{"seq": 1042, "timestamp_iso": "2026-08-02T...", "payload": {...full content...}, "prev_hash": "sha256:abc...", "curr_hash": "sha256:def..."}

// After dedup — when content matches seq 1039 exactly:
{"seq": 1042, "timestamp_iso": "2026-08-02T...", "ref": "sha256:abc123", "distance": 3, "length": 1, "prev_hash": "sha256:abc...", "curr_hash": "sha256:def..."}
```

**Fields:**
- `ref`: SHA-256 of the referenced receipt's content (the full receipt hash)
- `distance`: How many entries back in the chain (seq difference: 1042 - 1039 = 3)
- `length`: How many consecutive entries this ref covers (usually 1; >1 supports run-length encoding)

### 2.2 Partial Dedup (Future)

For near-duplicate receipts (same structure, different values), the payload can be split:

```json
{"seq": 1042, "timestamp_iso": "...", "ref_payload": "sha256:abc123", "delta": {"session_id": "new-value", "timestamp": "new-value"}, ...}
```

This is deferred to Phase 2. Phase 1 implements exact-match dedup only.

## 3. Read Path

The read path (`mode=verify`, `mode=list`, `mode=chain_status`) must resolve back-references transparently:

```python
def resolve_receipt(entry: dict, chain: list[dict]) -> dict:
    if "ref" not in entry:
        return entry  # full entry, no resolution needed
    
    # Resolve back-reference
    ref_hash = entry["ref"]
    distance = entry.get("distance", 1)
    
    # Walk back through chain
    resolved = chain[entry["seq"] - distance]
    
    # Verify hash match
    assert sha256(json.dumps(resolved["payload"])) == ref_hash, \
        f"Back-ref integrity failure at seq {entry['seq']}"
    
    # Return resolved entry with original payload
    return {**entry, "payload": resolved["payload"]}
```

**Fallback:** If back-reference resolution fails (corrupted chain), the full text is requested from the Postgres-backed VAULT999 API (port 8100). This is the safety net — the ref is an optimization, not a dependency.

## 4. Write Path

### 4.1 Hash Index

A write-time index is maintained in memory (Redis L1) and persisted to disk (SQLite or Postgres):

```python
# In-memory: {content_hash: seq_number}
hash_index: dict[str, int] = {}

def write_receipt(payload: dict, chain: list[dict]) -> dict:
    content_hash = sha256(json.dumps(payload, sort_keys=True))
    
    if content_hash in hash_index:
        # Duplicate found — emit back-reference
        ref_seq = hash_index[content_hash]
        distance = len(chain) - ref_seq
        return {
            "seq": len(chain) + 1,
            "timestamp_iso": now(),
            "ref": content_hash,
            "distance": distance,
            "length": 1,
            "prev_hash": chain[-1]["curr_hash"],
            "curr_hash": compute_curr_hash(...),
        }
    
    # New content — full write
    hash_index[content_hash] = len(chain) + 1
    return full_entry(payload, chain)
```

### 4.2 Index Persistence

The hash index is persisted to `${VAULT999_PATH}/dedup_index.jsonl` as append-only. On restart, the index is rebuilt from the chain (replay all entries, hash each payload, rebuild index). This is O(n) but VAULT999 is currently ~MB, not GB.

## 5. Storage Savings Estimate

Based on audit trail patterns:

| Receipt Type | Duplication Rate | Est. Savings |
|---|---|---|
| Session seals (mode=session_close) | 60-70% | High — structurally identical |
| Health checks (forge_health_check) | 80-90% | Very high — near-identical payloads |
| Constitutional verdicts (arif_judge) | 10-20% | Low — each verdict is unique |
| Evidence receipts (OBS/DER) | 5-10% | Minimal — evidence is mostly novel |
| **Overall** | **40-60%** | **Conservative estimate** |

## 6. Blast Radius & Reversibility

| Dimension | Assessment |
|---|---|
| **Blast radius** | LOW — affects only the write path; read path is transparent |
| **Reversibility** | FULL — write full entries alongside refs during migration; can roll back by replaying chain |
| **Data loss risk** | ZERO — ref is an optimization; full text available via VAULT999 API fallback |
| **Chain integrity** | PRESERVED — prev_hash/curr_hash still computed; ref is in payload, not in hash chain structure |

## 7. Implementation Phases

### Phase 1 (T1 — this spec)
- [ ] Add `ref`, `distance`, `length` fields to receipt schema
- [ ] Implement write-time hash index (Redis L1)
- [ ] Implement read-time ref resolution
- [ ] Add Postgres fallback path for failed ref resolution
- [ ] Test: write 100 identical receipts, verify 99 are refs, verify all 100 resolve correctly

### Phase 2 (T2 — deferred)
- [ ] Partial dedup with `ref_payload` + `delta` fields
- [ ] Persistent hash index to disk
- [ ] Run-length encoding for consecutive identical entries

### Phase 3 (T3 — 888_HOLD, deferred)
- [ ] Full LZMA-engine for VAULT999 (range coding, Markov chain, optimal parsing)
- [ ] This is a research project — not needed until VAULT999 exceeds 100 MB

## 8. Constitutional Alignment

| Floor | How it binds |
|---|---|
| **F1 AMANAH** | Reversible — full entries are stored alongside refs during migration; rollback = replay chain |
| **F2 TRUTH** | Back-ref validity is hash-verified on every read; broken ref → fallback to Postgres |
| **F4 CLARITY** | ΔS improvement — storage reduction is literally entropy reduction of the audit trail |
| **F11 AUDIT** | Every ref is traceable to its source entry; provenance is preserved across dedup |
| **F13 SOVEREIGN** | First-SEAL-wins — the original entry (the one referenced) is sealed; refs point to sealed truth |

## 9. Zen

> The back-reference is the LZ77 token. The dictionary is VAULT999. The compression ratio is ΔS. The hash chain is the Merkle root. The decompressor is the auditor. The compressor is the agent. The sovereign is the one who reads the output.
>
> DITEMPA BUKAN DIBERI — the compression is forged, not given.