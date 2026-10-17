# VAULT_CENSUS.md — how the ledger is counted (and why the numbers differ)
> Moved verbatim from the pre-doctrine README (2026-10-16 restructure).
> Source archive: `docs/archive/README-2026-10-16-pre-doctrine.md`.

## What VAULT999 is

Every consequential verdict, evidence chain and execution receipt is written to VAULT999 — a hash-chained, append-only JSONL ledger set, **tamper-evident by construction, not tamper-proof**.

**What it stores** is provenance, not copies. An entry carries its payload hash, entry hash, previous entry hash, trace root, actor, session, decision context and evidence references. Source payloads are not duplicated into the ledger — auditability here means provenance + integrity + reconstructability, which is both stronger and safer than copying everything forever (evidence can contain sensitive material).

**A hash chain proves internal consistency.** It does NOT prove that the chain was not recomputed by whoever controls the ledger. External anchoring — periodic publication of the chain head, or signing by a key the kernel does not hold — is not yet implemented. **Treat VAULT999 today as self-verifiable, not independently attestable.**

## Census — measured 2026-09-21

241,765 lines across 24 JSONL ledgers in VAULT999/ (largest: `outcomes.jsonl` 93,266 · `arifflow_sealed.jsonl` 52,056 · `apex-zen-receipts.jsonl` 30,977).

## Census — re-counted 2026-10-11

**471,067 lines across 58 JSONL ledgers** — method: `find` including subdirectories. The README SOT-MANIFEST header re-stamps a **different object** (top-level `*.jsonl` glob → 457K+). **The two figures are not interchangeable; neither should be quoted without its method.**

Composition: the majority is operational telemetry and receipt ingestion; constitutional verdict count is published separately (`scripts/verify_vault_chain.py --verdict-count-only`) — a 2026-10-11 re-count found `outcomes.jsonl` at 95,091 lines, of which 89,509 carry a verdict/decision field and 344 are `HOLD`. The chain report returns overall: `INTACT` for the active ledgers, reporting 2 strict link breaks in the frozen v1 legacy ledger as historical facts rather than hiding or rewriting them.

## Two denominators, both correct (2026-09-30T07:44:35Z)

| Method | Population | Count |
|---|---|---|
| (a) recursive whole-estate: `find <root> -name '*.jsonl'`, non-blank lines | `arifOS/VAULT999` 60/354,283 · `/var/lib/arifos/vault` 7/20,986 · `~/.local/share/arifos/vault999` 66/16,555 · `AAA/VAULT999` 1/238 | **134 ledgers / 392,062 lines** |
| (b) generated SOT-MANIFEST header (`scripts/update_readme_sot.py`, top-level `VAULT999/*.jsonl`, non-recursive) | 24 files | **342,582 lines** (`342K+ records`) |

Neither is wrong; they have different populations. The vault is append-only and live, so every figure here is a snapshot — quote the timestamp with it.

## Two witness surfaces — do not transfer verdicts between them

The VAULT999 **verdict ledger** (`outcomes.jsonl`) is a **different object** from the **invocation-telemetry ledger** (`/var/lib/arifos/metrics/tool_invocations.jsonl`). They share a shape and not a schema. A verdict is not transferable between them (measured 2026-10-11: telemetry ledger 194,243 lines with 0 governance fields; a call whose kernel verdict was `HOLD` was persisted as `ok:true`).
