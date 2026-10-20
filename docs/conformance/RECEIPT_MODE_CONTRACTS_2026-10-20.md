> **SUPERSEDED for findings** by `docs/conformance/RECONCILIATION_2026-10-20.md` (21:48 MYT).
> The contract registry stands; the enforcement claims here are scoped tighter in the reconciliation.

# RECEIPT — Capability→contract mapping at MODE granularity

- Date: 2026-10-20, 21:22–21:38 MYT (13:22–13:38 UTC)
- Actor: claude-code-kvm8 (FI-002) · session `SEAL-0f39068bd9af46d4` · OBSERVE_ONLY
- Lane: B (repo-side, reversible). No kernel restart, no production mutation.

## The gap this closes (OBS)

`abi/capability_registry.json` declares **one contract per tool** — 8 capabilities:

| tool | authority | irreversible | modes covered by that one contract |
|---|---|---|---|
| arif_memory | TRUSTED_AGENT | **true** | 9 — from `recall` (read) to `forget` (permanent) |
| arif_forge | EXECUTOR | **true** | 7 — from `dry_run` (read) to `commit` (irreversible) |
| arif_think | OBSERVER | false | 12 — from `reason` to `plan_approve` |

A tool-level contract cannot describe arif_memory. `recall` inherited
`irreversible: true` only because `forget` lives in the same tool. That is
over-authorisation produced by table shape, not by decision.

## What was built

**1. `arifosmcp/abi/mode_contracts.json`** — 69 contracts, one per tool.mode.
Each carries: `action_class`, `authority_required`, `mutation`, `irreversible`,
`preconditions`, `postconditions`, `verifier`, `recovery`, `evidence_receipt`.
Class defaults (`OBSERVE`, `PREPARE`) are declared once and inherited.

Distribution of the 58 canon-known modes: **29 OBSERVE · 9 PREPARE · 15 MATERIAL · 5 IRREVERSIBLE**.
All 5 irreversible modes: `arif_memory.promote/forget`, `arif_forge.commit`,
`arif_seal.seal/session_close` — each SOVEREIGN, each with a recovery class
(`compensate`/`permanent`), none claiming `rollback`.

**2. `kernel_abi.mode_contracts()` / `mode_contract(tool, mode)`** — loader with
class-default resolution. Same ABI directory as its siblings; no new registry
family (LAW 8).

**3. `scripts/contract_closure.py contracts`** — extended the existing contract
instrument (it owns contract-epoch measurement; not forked). It checks:
completeness, field presence, class/authority validity, and three consistency
laws — `OBSERVE` may not mutate, `IRREVERSIBLE` may not claim `rollback`,
every mutating mode must name a verifier. Then it runs **live refusal probes**.
Exit 1 on any gap, so it can gate CI.

## Result today

```
MODE CONTRACTS  58 modes  69 declared  11 gaps
CLASSES  {IRREVERSIBLE: 5, MATERIAL: 15, OBSERVE: 29, PREPARE: 9}
ENFORCEMENT  AUTHORITY_GATE_PROVEN
```

Machine-readable: `docs/conformance/mode_contracts_2026-10-20.json`

## Enforcement — what was proved and what was not

**Proved (OBS, live runtime :8088, 4/4 refused):**

| probe | result |
|---|---|
| `arif_seal(seal)` no sovereign token | HOLD, `mutation_allowed=false` |
| `arif_memory(forget)` no `human_approval` | HOLD |
| `arif_memory(promote)` no `human_approval` | HOLD |
| `arif_forge(commit)` no `constitutional_chain_id` | HOLD, `mutation_allowed=false` |

**Also probed, negative result (OBS):** `arif_forge(commit)` with a **fabricated**
`constitutional_chain_id` (`cc-forged-…`) and with an **empty** one returns the
**identical** refusal — `888_HOLD … Requires SOVEREIGN authority. Current: LOW`.
So the refusal happens at the capability-authority layer, **before any grant is
examined**. At this authority level a forged grant is indistinguishable from a
valid one.

**Therefore NOT proved:** grant expiry, grant revocation, action-hash binding.
Arif's point 5 ("hash only binds content — the system must still check who
issued the grant, whether it is valid, whether it was revoked") is **open**.
The code path exists somewhere; it is unreachable below SOVEREIGN, so today it
cannot be tested and must be reported as UNMEASURED, not as working.

## Two more real defects the mapper surfaced

1. **`arif_route` declares `modes: []`** in `CANONICAL_TOOLS` while the live wire
   exposes 6 modes (`route, triage, delegate, status, kernel, metabolize`). The
   canonical owner cannot enforce a per-mode contract for a tool whose modes it
   does not list.
2. **`arif_report` is live on the wire but absent from `CANONICAL_TOOLS`** — a
   9th tool outside the declared ABI of 8. `contract_closure verify` already
   flags it: `PHANTOM tools appear: [{surface: runtime, tool: arif_report}]`.

Both are canon-side edits (kernel source). Not applied — see below.

## MENUNGGU ARIF

The mapping is complete for the 58 modes canon knows. To make it *enforced*
rather than declared, three steps remain, all kernel-side:

```
# 1. canon under-declares arif_route — add its 6 modes to CANONICAL_TOOLS
# 2. admit or retire arif_report — 9 tools live, 8 declared
# 3. wire kernel_abi.mode_contract() into pre_execution_gate so the contract
#    is consulted at the side-effect boundary, not just reported by a script
chattr -i /root/arifOS/arifosmcp/constitutional_map.py   # if set
# edit → rebuild wheel → systemctl restart arifos          # Arif's hand
python3 -I /root/arifOS/scripts/contract_closure.py contracts   # expect 0 gaps
```

Until step 3 lands, the honest state is: **contract declared, enforcement
authority-gated only**. The file says what each mode may do; the kernel does not
yet read per-mode contracts. Saying otherwise would be narrative, not receipt.

## Rollback

New: `arifosmcp/abi/mode_contracts.json`, 2 loader functions in
`kernel_abi.py` (additive), `mode_contract_report()` + `contracts` subcommand in
`contract_closure.py` (additive), 2 JSON artifacts, this receipt.
Nothing existing was modified in behaviour. `git checkout` on the two edited
files restores them; the new file is inert until something imports it.
