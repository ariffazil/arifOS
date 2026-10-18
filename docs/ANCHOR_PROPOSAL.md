---
title: External Anchor Proposal — daily signed tag of VAULT999 chain head
status: PROPOSAL (NOT ENABLED)
owner: ARIF (F13)
drafted_by: FI-003 (qwen) — receipt executor
drafted_on: 2026-10-18
gate: BLOCKED on T7 = MATCH
cron: NONE — this proposal does not schedule anything
---

# External Anchor Proposal

> **Proposal only. No cron. No automation. No mutation.** The chain head below is
> a point-in-time observation, not a seal.

## 1. Problem

The canonical ledger `/root/.local/share/arifos/vault999/seal_chain.jsonl` is a
hash chain. A hash chain proves *internal* consistency; it does not prove the head
was not rewritten by whoever controls the file. The README already states this:
"External anchoring ... is not implemented: VAULT999 today is self-verifiable, not
independently attestable."

## 2. Observed head at proposal time

| Field | Value |
|---|---|
| Ledger | `/root/.local/share/arifos/vault999/seal_chain.jsonl` |
| Lines | 274 |
| Head `seq` / `sequence` | **55** |
| Head `timestamp` | `2026-10-15T09:48:35.316634Z` |
| Head `receipt_id` | `rcpt-0b3ec9520b7c4e59` |
| Head `this_hash` | `sha256:53ebb372495669aa348a82538f620974c985d2065a17072b42048557ef01fb73` |
| File SHA-256 | `1073ce80d90e0a70691360b973d11ebcd13a810e6977f5e7ebe436974f739d40` |

Discrepancy against oracle v2: the report expected head `seq 72`; the live head is
`seq 55`. Recorded, not reconciled.

## 3. Proposal

Once T7 is a clean MATCH (one canonical private key ↔ registered public key):

1. A daily job reads the canonical head (`seq`, `this_hash`, `timestamp`).
2. It creates an **annotated, signed git tag** on the public arifOS repository:
   `vault-anchor-YYYYMMDD-<seq>` with a message containing the head hash + seq.
3. It pushes only the tag (`git push origin <tag>`), never a branch.
4. It writes a local receipt line to `docs/anchors/ANCHOR_LOG.jsonl`.

This makes the head independently attestable: any later rewrite of the ledger
produces a head whose history cannot match the published tag.

## 4. Draft script (DO NOT SCHEDULE)

```bash
#!/usr/bin/env bash
# vault999-anchor.sh — PROPOSAL ONLY. Not installed. Not in cron.
set -euo pipefail

LEDGER="/root/.local/share/arifos/vault999/seal_chain.jsonl"
REPO="/root/arifOS"
LOG="$REPO/docs/anchors/ANCHOR_LOG.jsonl"

head_json="$(tail -1 "$LEDGER")"
seq="$(printf '%s' "$head_json" | python3 -c 'import sys,json;print(json.load(sys.stdin)["seq"])')"
thash="$(printf '%s' "$head_json" | python3 -c 'import sys,json;print(json.load(sys.stdin)["this_hash"])')"
ts="$(printf '%s' "$head_json" | python3 -c 'import sys,json;print(json.load(sys.stdin)["timestamp"])')"
day="$(date -u +%Y%m%d)"
tag="vault-anchor-${day}-${seq}"

# Refuse if the tag already exists (idempotent, never force).
git -C "$REPO" rev-parse -q --verify "refs/tags/$tag" >/dev/null && {
  echo "tag $tag already exists — no-op"; exit 0; }

mkdir -p "$(dirname "$LOG")"
printf '{"tag":"%s","seq":%s,"this_hash":"%s","head_timestamp":"%s","anchored_at":"%s"}\n' \
  "$tag" "$seq" "$thash" "$ts" "$(date -u +%FT%TZ)" >> "$LOG"

git -C "$REPO" add docs/anchors/ANCHOR_LOG.jsonl
git -C "$REPO" -c user.name="anchor-bot" -c user.email="anchor@arifos.local" \
  commit -m "[ANCHOR] ${tag} seq=${seq}"
git -C "$REPO" tag -s "$tag" -m "VAULT999 anchor seq=${seq} hash=${thash} ts=${ts}"
git -C "$REPO" push origin "$tag"
```

**Signing:** `tag -s` uses the operator's signing key. Do not run this draft until
T7 identifies exactly one canonical key. If per-lane keys are used, the anchor
must use a dedicated anchor key, not a lane key.

## 5. Gate

| Gate | State |
|---|---|
| T7 canonical private↔public MATCH | **NOT CLEAN** — primary `/root/compose/sekrits/arifos_sovereign.key` missing; three sovereign pairs MISMATCH; kernel-preferred public key matches `/opt/arifos/secrets/did_arifos_private.key` only as a fallback |
| F13 approval to publish tags | PENDING |
| Cron enablement | **NOT REQUESTED** |

## 6. Falsifiers

- If a published tag exists whose head hash cannot be reproduced from the ledger
  prefix, the ledger was rewritten after anchoring.
- If the same `seq` appears with two different `this_hash` values across tags,
  the chain forked.
- If the anchor script ever force-pushes or moves a tag, the anchor is void.

---

*Proposal. Awaiting F13. No cron created. No SEAL implied.*
