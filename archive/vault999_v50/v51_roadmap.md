# v51 Cryptographic Roadmap

> [!NOTE]
> This roadmap tracks cryptographic enhancements for vault_999.

## Enhancements

### 1. Full Merkle Tree 🔴 TODO
- [ ] Implement `arifos/core/crypto/merkle.py`
- [ ] Wire to `write_constitutional_entry()`
- [ ] Replace "PLACEHOLDER" with real roots

### 2. ZKPC Generation 🔴 TODO
- [ ] Design proof structure
- [ ] Implement hash-based commitments
- [ ] Upgrade path to Pedersen/Bulletproofs

### 3. Floor Validator Wiring 🔴 TODO
- [ ] Wire F1-F13 to CCC memory
- [ ] Read thresholds from seal
- [ ] Test all validators

### 4. Signature Verification 🔴 TODO
- [ ] Ed25519 key generation
- [ ] Seal signing function
- [ ] Public key registry

### 5. Seal Rotation 🔴 TODO
- [ ] Auto-rotation triggers
- [ ] Symlink update logic
- [ ] Version history

---

## Related

- [[../00_SEALS/current_seal|Current Seal]]
- [[../BBB_LEDGER/constitutional_entries|Ledger Entries]]

## Status

**Version:** v50.0.0 → v51.0.0
**Phase:** Planning
