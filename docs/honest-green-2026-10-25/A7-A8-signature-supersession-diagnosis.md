# A7 + A8 Diagnosis — SIGNATURE_FAIL gaps & beliefs_superseded (branch fix/honest-green-2026-10-25)

Read-only diagnosis. NO sealer patch (that is Lane B2, ARIF GO).
observed_at: 2026-10-24T18:55Z (2026-10-25 02:55 +08).

## A7 — the 5 canonical gaps (3 new after cutover)

Evidence sources:
- chain: `/root/.local/share/arifos/vault999/seal_chain.jsonl` — 277 rows, sha256 `51aa8638ba79f5121277a9a7a3bbdbf4fe89f98bc938944ec1cd0d8930f2b292` (mtime 2026-10-24T09:46:44+08)
- observatory: `/var/www/html/arifos/.well-known/observatory-chain-health.json` — file sha256 `fc431de30c86d5ee5ed43faf9290784eefee4ca4208a2194b24ccc72e11c42d0` (mtime 2026-10-25 02:24 +08)
- scope: `scope_canonical` — entries 75, head_seq 58, gap_count 5, cutover_seq 31, sig_enforce true, sig_epoch VAULT-SIG-1, signed_entries 24, signed_unverifiable 0, annotations_loaded 182

| seq | line | written | actor | signature evidence | class |
|---|---|---|---|---|---|
| 43 | 261 | (old) | — | recomputed receipt_hash mismatch + `hmac-sha256:85decab2…` fail | HASH_MISMATCH + SIGNATURE_FAIL (pair, OUT_OF_BAND_APPEND) |
| 38 | 256 | 2026-09-16T03:21:43Z | arif | `signature='verified'` (literal status word), `sig_key_id=''` | SIGNATURE_FAIL — unsigned after cutover (31) |
| 39 | 257 | 2026-09-16T03:39:07Z | arif | `signature='verified'`, `sig_key_id=''` | SIGNATURE_FAIL — unsigned after cutover |
| 57 | 276 | 2026-10-24T09:08:54Z | 333-AGI | `sig_method='unsigned'`, `signature=''`, `sig_key_id=''`, idempotency `plugin-fix-validation-2026-10-24` | SIGNATURE_FAIL — unsigned after cutover |
| 58 | — | 2026-10-24T09:46:44Z | 333-AGI | `sig_method='hmac-sha256'`, `sig_key_id='vault-hmac-1'` — SIGNED ✓ | (control: same session CAN sign) |

Arithmetic closes: post-cutover seqs 32..58 = 27; unsigned = {38, 39, 57} → 24 signed ✓.

### Root cause (code paths, not narrative)
1. **seq38/39 — legacy placeholder writer.** `arifosmcp/runtime/tools.py:21869`:
   `signature="" if not signature_verified else "verified"` — the field carries a
   STATUS WORD, not a signature, and `sig_key_id` is empty. The chain verifier
   (enforce mode since cutover seq 31, 2026-09-11) classifies presence-of-string
   without key binding as unsigned-after-cutover. `canonical_vault_chain.py:1601`
   already documents the legacy `"verified"` shape as caller-supplied.
2. **seq57 — unguarded append.** Writer appended an explicit unsigned canonical
   entry (`sig_method='unsigned'`, empty signature) despite `sig_enforce=true`.
   The same session appended seq58 38 minutes later FULLY SIGNED, and seq58's
   `decision_reference` states: "SIGNED SUPERSEDE of rcpt-d4dbbfb195c7431a/seq57
   (unsigned, keyless writer, pre-enforce)" — the supersede exists but did NOT
   clear the gap: annotation consumption currently explains CHAIN_BREAK only
   (`explained_gaps` = 5, all CHAIN_BREAK; SIGNATURE_FAIL records all have
   `explained_by: null`).
3. **key_id story:** legacy family `ed25519:sha256:698cc1ab26357272` (old signed
   rows), VAULT-SIG-1 family `vault-hmac-1` (post-cutover rows incl seq31/58).
   The 3 unsigned rows carry NO usable key_id — that is precisely what the
   verifier is detecting (this is a working control, not a broken one).

### Proposed guard (PREPARED FOR B2 — NOT applied)
- Fail-closed at canonical append: when `sig_enforce` is true and the record is
  canonical-envelope, REFUSE when signature is missing/placeholder in
  `{"", "verified"}` OR `sig_key_id` is empty. Reject at write time with an
  error naming the missing key binding (never silently append unsigned).
- Extend annotation consumption so a signed supersede (seq58 → seq57) reclassifies
  the target's SIGNATURE_FAIL as explained — mirrors the existing CHAIN_BREAK
  annotation path (`test_chain_annotation_consumption.py`).
- Rollback: revert the single guard commit. Risk: legacy recovery writes that
  genuinely cannot sign would be blocked — mitigation is the explicit signed
  annotation path, not an unsigned append.
- Invariant check: append-only preserved (guard refuses NEW bad rows; no
  rewrite, no drop of existing rows).

## A8 — beliefs_superseded never increments (diagnosis only)

Evidence: `flow_fq_g` live (2026-10-24T18:44Z): `beliefs_born 37225,
beliefs_superseded 0, supersession_events 0, revision_rate 0, receipts_scanned 37225`.

Path audit:
- **Counter EXISTS** — `arifFlow/src/lineage_query.rs:813-840` counts ledger rows
  with non-empty `supersedes_receipt_ids` (`beliefs_superseded`).
- **Write side EXISTS** — `receipt.rs:904-910` (fields), `receipt.rs:1021-1025`
  (`with_supersedes` builder); `main.rs:990` POST /ingest deserializes the FULL
  `FlowReceipt` via serde, so JSON keys `supersedes_receipt_ids/_hashes` are
  accepted on the wire; the arifflow MCP bridge exposes matching params
  (`flow_ingest` schema: `supersedes_receipt_ids`, `supersedes_receipt_hashes`).
- **Never invoked** — `with_supersedes` has ZERO callers outside `receipt.rs`
  (grep across src/), and no ledger row carries supersedes (counter 0).
- Persistence of a supplied supersedes field is INFERRED (whole-struct serde
  serialization), not witnessed — no receipt has ever carried the fields.

Verdict: the mechanism is COMPLETE end-to-end (bridge → ingest → receipt →
ledger → counter) but NEVER USED by any minter. Zero-superseded is a
**behavioural truth**, not a broken counter. Fixing F8's institutional-learning
story via supersession requires lanes to actually mint supersession receipts —
a policy/behaviour decision (routes to Arif), not a code patch.
