# 🔗 VAULT999 CANONICALIZER — 2026-07-19

> **SOT:** 2026-07-19 · **seal_seq:** 10
> **Source:** `/root/A-FORGE/src/interfaces/mcp/shell/arifSeal.ts:94-110`
> **Authority:** F-004 Resolution R1

## Canonical Serializer

The canonicalizer lives in `arifSeal.ts`:

```typescript
function canonicalSerialize(record: Omit<SealRecord, "hash">): string {
  const canonical: Record<string, unknown> = {
    seq: record.seq, ts: record.ts, tool: record.tool,
    args: record.args, judge_decision: record.judge_decision,
    exit_code: record.exit_code, stdout_sha256: record.stdout_sha256,
    stderr_sha256: record.stderr_sha256, prev_hash: record.prev_hash,
  };
  if (record.approver) canonical.approver = record.approver;
  if (record.notes) canonical.notes = record.notes;
  return JSON.stringify(canonical, Object.keys(canonical).sort());
}
```

## Key Facts

1. **Hash field is EXCLUDED** from the canonical payload (`Omit<SealRecord, "hash">`)
2. **9 mandatory fields**: seq, ts, tool, args, judge_decision, exit_code, stdout_sha256, stderr_sha256, prev_hash
3. **2 optional fields**: approver, notes
4. **Key ordering**: `Object.keys(canonical).sort()` — alphabetically sorted keys
5. **No trailing newline** — raw JSON.stringify output

## Why Naive Verification Fails

Using `json.dumps(record, sort_keys=True)` on the FULL record includes the `hash` field
and any extra metadata — producing a different SHA256 than the canonicalizer.

The correct verification: strip `hash` and any non-canonical fields, then sort keys alphabetically.

## Chain Status (2026-07-19)

- **28 records** in `/root/A-FORGE/data/vault999_chain.jsonl`
- **Historic scar (sealed)**: Seq 13-18 (2026-07-08) — concurrent_write_race, file-lock fix applied at seq 25
- **Post-fix**: Chain integrity verified — all prev_hash links match forward
- **Verification tool**: `forge_shell_ledger(verify_chain=true)` uses naive sort_keys — returns false positives

## Related

- F-004 VAULT999 GAP INVENTORY: `/root/forge_work/2026-07-19/eureka-synthesis/F-004-VAULT999-GAP-INVENTORY-2026-07-19.md`
- arifSeal.ts: `/root/A-FORGE/src/interfaces/mcp/shell/arifSeal.ts`

**DITEMPA BUKAN DIBERI.**
