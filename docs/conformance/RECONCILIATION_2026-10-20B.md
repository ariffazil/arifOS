# RECONCILIATION B — contract → gate. What is now proved, and what still is not.

- 2026-10-20, 21:48–22:05 MYT · claude-code-kvm8 (FI-002) · kernel authority OBSERVE_ONLY
- Repo HEAD at start `09f98235d`, at end `c56e94ad9` (another writer committed mid-work)
- Deployed release: `arifos-658505d` — **one commit behind HEAD**
- Supersedes nothing; extends `RECONCILIATION_2026-10-20.md`

## 1. The hole, proved by direct call (not by reading)

`pre_execution_gate.resolve_action_class_for_mode` is the function that decides
what class an action gets. Called directly on the **deployed package**:

| tool.mode | caller claims OBSERVE | deployment returns | correct? |
|---|---|---|---|
| `arif_memory.forget` | OBSERVE | **OBSERVE** | ✗ permanent deletion admitted as a read |
| `arif_memory.promote` | OBSERVE | **OBSERVE** | ✗ |
| `arif_forge.commit` | IRREVERSIBLE | **MUTATE** | ✗ caller asks stricter, gate downgrades |
| `arif_report.file` | OBSERVE | **OBSERVE** | ✗ write admitted as read |
| `arif_route.metabolize` | OBSERVE | **OBSERVE** | ✗ unknown mode inherits caller claim |

Root cause: `CANONICAL_TOOL_MANIFEST` is per-**tool**. `arif_memory` declares
`action_class=OBSERVE` for the whole tool; `forget` sits in `dangerous_modes`, and the
"prefer manifest default when stronger" branch is skipped because OBSERVE is not
MUTATE/IRREVERSIBLE. The call then falls through to `return requested_action`. The
caller's claim becomes the answer.

This is exactly your point 2: *"Kontrak tiada atau tidak dikenali mesti menyekat
tindakan yang mengubah keadaan."* Today it inherits instead of blocking.

## 2. Inventory — the 11, resolved (your point 1)

`docs/conformance/contract_inventory_2026-10-20.json`, pinned to `c56e94ad9`.

| class | count | members | meaning |
|---|---|---|---|
| **coordination-lane** | 5 | `arif_report.{file,ack,inbox,flush,stats}` | live on the wire, **outside the constitutional 8**. Not a verb, not counted as the 9th. Declared capability: peer report lane (2 MATERIAL writes at TRUSTED_AGENT, 3 OBSERVE reads). `contract_closure verify` already flags it `PHANTOM` — that flag is now reclassified, not ignored. |
| **canon-under-declared** | 6 | `arif_route.{route,triage,status,kernel,delegate,metabolize}` | tool **is** constitutional (`expose=True`) but `CANONICAL_TOOLS` lists `modes: []`. Live wire serves all 6. Canon under-declares. |
| **orphan** | **0** | — | none |
| **legacy** | **0** | — | none |
| **alias** | **0** | — | none |

So: 69 contracts = 58 canon modes + 6 under-declared + 5 coordination. No unexplained
remainder. The fix for the 6 is a canon edit (`CANONICAL_TOOLS["arif_route"]["modes"]`);
the fix for the 5 is a category declaration, not a 9th verb.

## 3. Gate wiring — written, tested, reverted (your point 2)

`arifosmcp/runtime/mode_contract_gate.py` (new, inert until imported) +
`docs/conformance/0001-gate-reads-mode-contracts.patch` (67 lines, sha256 `539701ad8fafef59`).

Rule implemented: the contract can only **escalate**. Never weaken the manifest,
never inherit the caller's claim for an undeclared mutating mode.

| case | before patch | after patch |
|---|---|---|
| `arif_memory.forget` claimed OBSERVE | OBSERVE | **IRREVERSIBLE** |
| `arif_forge.commit` claimed IRREVERSIBLE | MUTATE | **IRREVERSIBLE** |
| `arif_report.file` claimed OBSERVE | OBSERVE | **MUTATE** |
| `arif_route.metabolize` claimed OBSERVE | OBSERVE | **ANALYZE** |
| `arif_memory.recall` claimed OBSERVE | OBSERVE | OBSERVE (unchanged — positive control) |
| `arif_think.axioms` claimed OBSERVE | OBSERVE | OBSERVE (unchanged) |

The patch was applied to a scratch copy, exercised, then **reverted**. Kernel file is
back at HEAD (`96f5024b18884dba`). Deployment is yours:
`git apply docs/conformance/0001-gate-reads-mode-contracts.patch` → build → restart.

**Residual not closed by this patch:** `arif_fetch.archive` still resolves OBSERVE,
because the manifest itself lists `archive` as dangerous on an OBSERVE tool. Manifest
data bug, separate fix.

## 4. Positive control first (your point 3)

`scripts/test_contract_gate.py` — **16/16 pass**, and 7 of the 16 are positive
controls, per your rule that a system refusing everything must not score well.

```
positive   memory.recall is a read                    OBSERVE → OBSERVE
positive   forge.dry_run is a read                    OBSERVE → OBSERVE
positive   think.axioms, two sources disagree         ANALYZE → ANALYZE
positive   seal.verify is a read                      OBSERVE → OBSERVE
positive   memory.remember is reversible write        MUTATE → MUTATE
positive   caller may ask MORE conservative           IRREVERSIBLE → OBSERVE
positive   report.file is a declared write            MUTATE → MUTATE
negative   memory.forget is irreversible              IRREVERSIBLE → IRREVERSIBLE
negative   memory.promote is irreversible             IRREVERSIBLE → IRREVERSIBLE
negative   forge.commit is irreversible               IRREVERSIBLE → IRREVERSIBLE
downgrade  forget claimed as OBSERVE                  refused, downgrade cited
downgrade  commit claimed as MUTATE                   refused, downgrade cited
unknown    tool with no contract, mutating request    refused, NO_CONTRACT
unknown    undeclared mode, irreversible request      refused, NO_CONTRACT
unknown    tool with no contract, read request        OBSERVE → OBSERVE (allowed)
summary    memory.forget recovery=permanent           ok
```

Every refusal cites its reason; none refuses "because no".

## 5. Grant tests — harness specified, NOT run (your point 3, second half)

The six tests you asked for need one thing I cannot mint: **a valid grant**. My
session is `OBSERVE_ONLY`; `arif_forge` refuses at the capability-authority layer
before any grant is read. Nothing below was executed.

| test | expected | measured |
|---|---|---|
| valid grant, matching action | succeeds + receipt | **UNMEASURED** — no grant |
| expired grant | refused, reason=expiry | **UNMEASURED** |
| revoked grant | refused, reason=revocation | **UNMEASURED** |
| action hash differs | refused, reason=binding | **UNMEASURED** |
| forged grant | refused, reason=verification | **UNMEASURED** |
| repeat same action | no duplicate side effect | **UNMEASURED** |

What is required to run them: one SOVEREIGN-issued grant scoped to a sandbox path,
plus a way to mutate its expiry/revocation state — i.e. a test fixture that only the
sovereign lane can create. This is the next real step after the gate is deployed.

## 6. Build and runtime verification (your point 4) — two findings

1. **Deployed is behind source.** `deployed_commit=658505d`, repo `HEAD=c56e94ad9`.
   `/health` reports `drift:false` because it compares source/built/deployed of the
   *wheel*, not the repo HEAD. So a one-commit lag is invisible to the health probe.
2. **The wheel contains a stale draft of my own module.** Deployed
   `mode_contract_gate.py` is 4,966 B from 21:37:33; repo is 5,515 B from 21:37:55.
   A build captured the file mid-edit. It is dead code today (the gate does not import
   it — `grep` count 0), but it is a half-built artefact inside a "release". Exactly
   the class you flagged: two states of the code in one snapshot.

Confirmed matching: deployed `pre_execution_gate.py` hash == repo HEAD hash
(`96f5024b18884dba`), so the gate on the live service is the unpatched one.

## 7. Behavioural suite after all of the above

```
PASS T1 irreversible refusal        3/3 refused before side effect
PASS T2 confidence ceiling ≤0.97    13 axioms, max ≤ 0.97   (+ band 0.96–0.97 now reported)
PASS T3 F11 means audit
PASS T4 advertised params callable  8/8
PASS T5 F6 bridge
PASS T6 OBSERVE cannot mutate
6 tests · 6 pass
```

T2 now also counts values strictly between 0.96 and 0.97 — the operational ceiling —
as you asked. None today.

## 8. Honest status line

> Contracts exist per mode. The inventory is closed. The gate hole is **proved, not
> inferred**, and a tested patch is waiting. The gate does **not** yet read contracts
> in production. Grant validity, revocation, binding and idempotency remain
> **UNMEASURED** — not "working", not "failing": unmeasured, because no valid grant
> exists to test against.

## 9. Writes and authority

Kernel session: OBSERVE_ONLY, no mutation authorised. All writes below are workspace
writes (local + reversible), listed because they are writes:

| write | path | reversible by |
|---|---|---|
| new | `arifosmcp/runtime/mode_contract_gate.py` (inert) | delete |
| new | `scripts/test_contract_gate.py` | delete |
| new | `docs/conformance/0001-gate-reads-mode-contracts.patch` | delete |
| new | `docs/conformance/contract_inventory_2026-10-20.json` | delete |
| new | this file | delete |
| edit | `scripts/test_floor_behaviour.py` (band reporting) | git checkout |
| edit→revert | `arifosmcp/runtime/pre_execution_gate.py` | verified clean vs HEAD |

Memory: one new file + index line, recorded separately.
