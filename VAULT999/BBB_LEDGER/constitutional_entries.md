# Constitutional Ledger (Live View)

> [!NOTE]
> This view requires **Dataview** plugin and sync from `vault_999/BBB_LEDGER/`.

## Recent Entries

```dataview
TABLE
  verdict as "Verdict",
  session_id as "Session",
  dateformat(timestamp, "yyyy-MM-dd HH:mm") as "Time"
FROM "BBB_LEDGER/entries"
SORT timestamp DESC
LIMIT 20
```

## Ledger Statistics

| Metric | Value |
|--------|-------|
| Total Entries | `$= dv.pages('"BBB_LEDGER/entries"').length` |
| Latest Verdict | See above table |
| Hash Chain | [[hash_chain]] |

## Quick Filters

### SEAL Verdicts Only
```dataview
LIST
FROM "BBB_LEDGER/entries"
WHERE verdict = "SEAL"
SORT timestamp DESC
LIMIT 10
```

### VOID/SABAR Verdicts (Requires Attention)
```dataview
LIST
FROM "BBB_LEDGER/entries"
WHERE verdict = "VOID" OR verdict = "SABAR"
SORT timestamp DESC
LIMIT 10
```

---

## Source

Synced from: `vault_999/BBB_LEDGER/LAYER_3_AUDIT/constitutional_ledger.jsonl`

**Sync Command:**
```bash
python scripts/sync_vault_to_obsidian.py
```
