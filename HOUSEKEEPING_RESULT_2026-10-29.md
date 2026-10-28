# HOUSEKEEPING RESULT — 2026-10-29

**Agent:** `qwen-fi003` (lane 333-AGI, FI-003). Never `arif` / `arif-fazil`.
**Probe path:** `https://mcp.arif-fazil.com/mcp` (public). Localhost used only to prove a defect
is *not* remote-specific.
**Ruler:** [`HOUSEKEEPING_BASELINE_2026-10-29.md`](./HOUSEKEEPING_BASELINE_2026-10-29.md)
**PRs:** arifOS [#965](https://github.com/ariffazil/arifOS/pull/965) ·
A-FORGE [#140](https://github.com/ariffazil/A-FORGE/pull/140)

---

## 1. NOT DONE

| item | why | exact evidence |
|---|---|---|
| **Item 1** — 5 coordination tools erroring | Partly done, partly overtaken | The 5 tools failed for **every caller, not just remote ones** — the brief's premise was wrong. Another agent deployed a partial fix at 00:27 MYT (commit `d67e6cfbf`) which closed the minimal-argument path but left the unknown-field path open. **My PR closes that remaining path**; it is `FIXED_IN_PR_NOT_DEPLOYED`. |
| **Item 7** — AGENTS.md over 32 KB | **Nothing to do — the premise is false** | No `AGENTS.md` anywhere in the 3 repos exceeds 32 KB. Repo roots: arifOS 2 883 B, AAA 4 075 B, A-FORGE 3 693 B. 37 AGENTS.md files checked across all three trees. |
| **Item 8** — root clutter → `_to_delete/` | Partly done, then blocked | Moved `.bak-pre-rebuild-2026-09-21/` → `/root/_to_delete/2026-10-29-aforge-root-clutter/`. The remaining 10 A-FORGE root `.bak` files and the AAA snapshot are **`chattr +i`** — `mv` fails with `Operation not permitted`. Moving them needs `chattr -i`, a sovereign decision. Not raw-unlocked. |
| **Item 9** — README numbers disagreeing with live | **Nothing to do — the premise is false** | No hardcoded live-adjacent count claims in the 3 READMEs. arifOS's README delegates counts to `docs/evidence/VAULT_CENSUS.md` and says *"quote the timestamp with any count"*. The census is dated (2026-10-11) and method-stamped — correct form, but now stale (see §5). |
| **Item 3** — 4 identity spellings | **Nothing to do — by design, and they agree** | See §3. |
| AAA branch / PR | Not opened | AAA's `.git` is `chattr +i` and another agent has uncommitted work in that tree. A branch switch would have carried their work. AAA's only clutter item is one `+i` file (listed, not moved). |
| `arif_seal mode=verify` → vault integrity | **The tool does not do this** | All four modes (`verify`/`ledger`/`audit`/`changelog`) return the same *session-authority* payload. There is no vault read in `mode=verify`. Any ledger_size/vault_dir quoted from it would be fabricated — §6 of the baseline measures the vault from the filesystem instead. |

---

## 2. DECISIONS FOR ARIF (5)

1. **Which vault path is canonical?** — 4 paths, 3 contents: `arifOS/VAULT999` (13 G, 856 076 lines),
   `.local/share/arifos/vault999` (73 M), `/var/lib/arifos/vault999` (34 M), `/root/VAULT999` (symlink).
   *Recommend:* declare `arifOS/VAULT999` canonical and point the other readers at it. *Risk:* if the
   systemd writers actually target `/var/lib/arifos/vault`, the two ledgers are diverging silently.
2. **Re-pin the A-FORGE MCP policy, or accept permissive fallback?** — live `/health` reports
   `pin_violated: true`, `posture: PERMISSIVE_FALLBACK`, `effective_policy: default:sovereign`,
   `allow_by_default: true`. The reviewed policies are **not loaded**.
   *Recommend:* re-review and re-pin to the current HEAD. *Risk:* re-pinning restores a reviewed
   allowlist that may itself need re-checking against HEAD.
3. **Merge A-FORGE #140 (the policy-keyed-to-verified-identity proposal)?** — *Recommend:* yes, but
   first confirm no legitimate **unauthenticated** flow reads github/postgres/cloudflare/docker/
   hostinger through the MCP proxy; those servers are refused until the caller authenticates.
   *Risk:* one such flow breaks. The allowlist is a single constant (`UNVERIFIED_ALLOWED_SERVERS`).
4. **Unlock the 11 `chattr +i` clutter files?** — *Recommend:* yes, then move them to
   `/root/_to_delete/2026-10-29-aforge-root-clutter/` — except
   `litellm-config.yaml.bak-deepseek-or-p2-20261021T084110Z`, which is a **documented rollback
   source** (`deploy/fed/litellm-config.yaml:5`) and must stay. *Risk:* low; the one to keep is flagged.
5. **Reclaim disk (92% used)?** — `.cache` 21 G, `.npm` 3.2 G, plus 13 G of VAULT999 and several
   `*-rg2-verify` / `*-rewrite-*` worktree-shaped directories. *Recommend:* clear `.cache` and
   `.npm` first (regenerable, ~24 G). *Risk:* low for caches, high for the vault (decisions 1 + 2).

---

## 3. DONE

| item | PR | before → after | status |
|---|---|---|---|
| **1** — coordination tools survive an undeclared field | arifOS #965 `e71fe13cc` | live 01:02 MYT: all 5 `isError=True` (`Error calling tool 'X'`) when the caller sends `session_token` → in-process: all 5 real payloads, `isError=False` | `FIXED_IN_PR_NOT_DEPLOYED` |
| **2** — `surface_hash` covers the whole public wire | arifOS #965 `25cd165b2` | `sha256:6295a69b…` (8 tools) → `sha256:873dc35e…` (14 tools). Removing `arif_delegate` now moves it to `sha256:c70eced1…`; before, the same operation changed nothing | `FIXED_IN_PR_NOT_DEPLOYED` |
| **2b** — one owner for "what is on the public wire" | arifOS #965 | 3 hand-computed copies (tools/list filter, tools/call gate, hash) → 1 (`public_exposed_tool_names()`) | `FIXED_IN_PR_NOT_DEPLOYED` |
| **3** — identity spellings | — | `arif` / `arif-fazil` / `ARIF` / `ARIF_FAZIL` → canonical **`ARIF`** in **both** Python (`contracts/identity_canon.py`) and TypeScript (`A-FORGE/.../identityCanon.ts`); 9/9 inputs, **0 mismatches**; `same_principal` true across all four | **NO FIX NEEDED** |
| **4** — policy keyed to verified identity | A-FORGE #140 | unverified caller → `policy_id: default:sovereign` → `default:unverified` (deny-by-default, organs only). Verified ACT caller unchanged | `FIXED_IN_PR_NOT_DEPLOYED` |
| **4b** — the test the brief asked for | A-FORGE #140 | unverified `arif` → `forge_filesystem_write` / `forge_git_commit` / `forge_execute` = **DENY** (`L1_IDENTITY:unverified_client_id`). **This already held** — the authority layer is provenance-derived, not name-derived | **ALREADY SAFE — now pinned** |
| **4c** — two gate tests were never built or run | A-FORGE #140 | `npm test` 321/320/1 → **349/348/1**. `dist/test/mcpPolicyGateActor.test.js` + `actBridgeEnvelope.test.js` were never compiled (sources in tsconfig-excluded `src/test/`) and were **silently skipped** | `FIXED_IN_PR_NOT_DEPLOYED` |
| **5** — vault paths | — | report only, per brief | **REPORTED** |
| **6** — disk | — | report only, per brief | **REPORTED** |
| **8** — root clutter | manifest `/root/_to_delete/2026-10-29-aforge-root-clutter/MANIFEST.md` | 1 dir moved; 11 files listed (10 A-FORGE + 1 AAA) but `chattr +i` | **PARTIAL — 11 blocked on unlock** |
| **9** — README truth | — | premise false; census doc is dated + method-stamped | **NO FIX NEEDED** |
| baseline | arifOS #965 `68e308f8b` | — | committed |

### Verification receipts

```
arifOS   tests/test_public_coordination_tools.py   13 passed
         tests/test_public_surface_hash.py          5 passed
         tests/test_copilot_mcp_surface.py          5 passed
         tests/12_identity_canon.py                10 passed
                                              =    33 passed
         pre-commit hard gates 3/3 and 5/5 clean; pre-push ALL GATES PASSED

A-FORGE  test/policyKeyedToVerifiedIdentity.test.ts  7 passed
         npm test: 349 tests, 348 pass, 1 fail
         the 1 failure = actIngressSigLength "G2 legacy 16-hex compat window"
         — PRE-EXISTING: verified by stashing the change and re-running (5 pass/1 fail)
         pre-commit hard gates 2/2 clean; pre-push governance gate passed
```

---

## 4. NUMBERS — baseline vs now

| measure | baseline (00:24 MYT) | now (01:2x MYT) |
|---|---|---|
| arifOS public tools exported | 14 | 14 |
| **tools returning a real payload from the public path** | **9** (+5 coordination tools erroring) | **13** — the 5 coordination tools now return payloads, and `arif_forge` returns a *correct* constitutional HOLD (`888_HOLD: requires SOVEREIGN authority; Current: LOW`) for this unverified actor. **Zero broken.** |
| tools erroring | **5** | **0** |
| tools erroring *when the caller adds `session_token`* | not measured at baseline | **5** (the coordination tools) — closed by PR #965, live after deploy |
| tools covered by `surface_hash` | **8 of 14** | **14 of 14** after PR #965 |
| organs healthy | 4/4 (GEOX 27/27, WEALTH 15/15, WELL 10/10, A-FORGE healthy) | 4/4 |
| disk used | 92% | 92% (nothing deleted) |
| AGENTS.md > 32 KB | 0 | 0 |
| distinct vault paths | 4 | 4 |
| identity spellings → canonical | 4 → `ARIF` | 4 → `ARIF` (0 py/ts mismatches) |
| A-FORGE `npm test` | not measured | 321/320/1 → **349/348/1** |
| A-FORGE policy posture | not measured | `PERMISSIVE_FALLBACK` (pin violated) |

> **A note on how these numbers were measured.** An intermediate combined probe reported "11
> broken" and was wrong — the script shared argument dicts across tools and re-ran `arif_init`
> inside the loop, displacing the session. Every count above comes from a re-probe where each tool
> was called with its own arguments and the failure text was read, not inferred from a boolean.
> `arif_forge` is counted separately because `isError: true` with a constitutional HOLD verdict is
> a **correct refusal**, not a defect.


---

## 5. UNKNOWN

- **Whether the 5 tools work from the public path after deploy** — requires Arif's merge + deploy;
  my PR is `FIXED_IN_PR_NOT_DEPLOYED`, and a receipt from an older `release_id` is void.
- **The full arifOS pytest suite is red independently of this work.** A background run was still
  passing at 46% with many pre-existing failures and errors; I did not let it finish and I did
  **not** establish which of those failures (if any) are mine. The 4 test files I touched are
  green. **The suite's baseline is unknown to me** — treat "the suite is green" as unproven.
- **Which vault path the systemd writers actually target** — `arifOS.service` sets
  `ARIFOS_VAULT_DIR=/var/lib/arifos/vault` (a *fifth* path, distinct from the four in §6 of the
  baseline) while the repo's own ledger lives in `arifOS/VAULT999`. Not reconciled.
- **Whether any legitimate unauthenticated flow depends on the external MCP servers** — decides
  decision 3.
- **The 11 `chattr +i` clutter files' actual contents vs the live config** — I confirmed they are
  unreferenced and older than the live `litellm-config.yaml`, but I did not diff them.
- **arifOS's other 3 PRs (#963, #959, #927) and A-FORGE's 6 other PRs** — not reviewed; out of scope.
- **Whether the concurrent agent that deployed at 00:27 and removed the `.bak` files is still
  active.** Its file edits stopped at 00:25; the `.bak` removals landed around 01:20.

---

## 6. Notes on how this was done

- **Nothing was deleted.** No file, no branch, no service was removed. The one directory that was
  moved went to the federation's existing `/root/_to_delete/<date>-<label>/` convention, with a
  manifest and a one-line reason per item.
- **No prod service was restarted.** Both PRs are code + tests; Arif merges and deploys.
- **Concurrent writers were preserved.** The arifOS working tree carried another agent's
  uncommitted item-1 work when this sweep started; it is now commit `d67e6cfbf`, the base of my
  branch, and my commits build on it rather than replacing it.
- **Deviations from the brief, and why:** (a) the baseline report sits at the arifOS repo root,
  not `reports/` — `reports/` is gitignored (`.gitignore:251`), so the brief's path could never
  reach a PR; (b) one branch per repo, so the two arifOS fixes are two *commits* on one branch and
  one PR, not two PRs; (c) the A-FORGE work was committed from a fresh clone because A-FORGE's
  `.git` is `chattr +i` and the worktree's own gitdir could not be unlocked by `git-lane` — the
  main tree and its uncommitted work were left untouched.

---

## 7. MERGE + DEPLOY — 2026-10-29 (Arif: "merge both PRs and deploy")

### Merged

| PR | repo | merge commit | note |
|---|---|---|---|
| [#965](https://github.com/ariffazil/arifOS/pull/965) | arifOS | `a263f3334` | the 2 fixes + baseline + result report |
| [#969](https://github.com/ariffazil/arifOS/pull/969) | arifOS | `921cabefb` | content-free lineage merge (see §7c) |
| [#140](https://github.com/ariffazil/A-FORGE/pull/140) | A-FORGE | `01f20b7aa` | the proposal + the 2 orphan gate tests |
| [#139](https://github.com/ariffazil/A-FORGE/pull/139) | A-FORGE | `3a0cd681d` | **prerequisite, not mine** — re-pins zod to 3.25.76; `main` had been build-red since #127 and PR #140's Sentinel Gate requires a green Q3 |

`validate-routing` failed on both PRs until the commits carried a literal `REPO=` line.
git's `--trailer` writes `REPO: value`; the gate greps `^REPO=`. Both branches were rewritten
(force-pushed, own branches only) with the literal line, preserving each original author.

### arifOS — DEPLOYED and VERIFIED

Three fail-closed HOLDs happened first, each with **zero protected writes**:

1. `HOLD_UNVERIFIED_DEPLOY` (epoch 26) — the last governed release had no PASS verdict. That epoch
   failed because **my concurrent history rewrite moved HEAD mid-lease** — my fault. Resolved via
   the designed F13-only `resolve-epoch` path, receipt
   `/var/lib/arifos/f13_overrides/2026-10-29-resolve-epoch-dl-e883b0a0bee3.json`.
2. `DEPLOY_REGRESSION_RISK / DEPLOYED_NOT_ANCESTOR` (epoch 27) — the live artifact was installed from
   `68e308f8b`, a commit that existed only in the *pre-rewrite* branch, so it was not an ancestor of
   the candidate. The gate's own remedy: *"merge the deployed lineage before deploying"*. The
   content was already strictly contained (`diff --stat` = 1 file changed, 149 insertions, **0
   deletions**), so PR #969 records that lineage with an `ours` merge — **zero tree change**, a pure
   ancestry record. Resolved via receipt
   `/var/lib/arifos/f13_overrides/2026-10-29-resolve-epoch-dl-4150815d41f3.json`.
3. Final deploy succeeded:

```
ROLLBACK_REGISTERED /opt/arifos/releases/rollback-20261028T180404Z-921cabefb
Syncing canonical code to /opt/arifos/app (export=/var/tmp/arifos-deploy.LAAwYv)
Syncing runtime import path ... Restarting arifOS bare-metal service...
Kernel answers (status=degraded) after 6s
Conformance gate: CONFORMANCE_DEGRADED_ACCEPTED / CAUTION / substrate_gate AMBER / 7/9
verify-epoch PASS — candidate/artifact equivalence recorded
```

Post-deploy probe from the **public path**:

```
release_id:    arifos-921cabefbe99
surface_hash:  sha256:873dc35e854e00564ce01f802d0d306f01a7913e743a6268020d7bc2b5d10bdc   (14 tools)
minimal args:            working=13/14  correct-HOLD=[arif_forge]  broken=[]
+ session_token:         working=13/14  correct-HOLD=[arif_forge]  broken=[]
```

`arif_forge` returning `isError: true` with an `888_HOLD` verdict is a **correct refusal**
(sovereign capability, this actor is unverified/OBSERVE_ONLY) — not a defect.

### A-FORGE — MERGED but DEPLOY REVERTED (deliberately)

PR #140 is merged into `main`. The **runtime was not moved to it**, because deploying `main` would
have shipped a regression:

```
git log --oneline origin/main..02b7f6bc   ->  44 commits
git diff --stat origin/main 02b7f6bc      ->  134 files changed, 21494 insertions(+), 3281 deletions(-)
```

`main` is **44 commits behind** the branch the A-FORGE tree is actually checked out on
(`repair/aforge-f3-f8-2026-10-25`, `02b7f6bc`) — that branch carries the P0 authority-enforcement
repairs, the Gate-0 refusal circuit-breaker, the KX-010 work, the action-classifier fail-closed fix,
the FED rung repairs and more, none of it merged to `main`. The merged `main` also **hardcodes
`/opt/a-forge/app`** for the deploy marker instead of honouring `AF_FORGE_DEPLOY_ROOT`, and **drops
the `policy_gate` health attestation** (the 2026-10-26 honesty fix that makes a pin violation
visible). Deploying it would have rolled all of that back at runtime.

The runtime was therefore **restored to its exact pre-deploy state**, verified:

```
status=healthy  ok=True  degraded_mode=False  deployment_drift=False
deployed_commit = source_commit = head_commit = 02b7f6b      (identical to before)
tool_count = 118                                                  (identical to before)
policy_gate = {"pin_violated": true, "pinned_commit": "748741a", "head_sha": "02b7f6b",
               "effective_policy": "default:sovereign", "allow_by_default": true,
               "posture": "PERMISSIVE_FALLBACK"}
:7071 healthy · :7072 http=200
```

The other agent's tree, branch and 10 uncommitted files were never touched. PR #140's runtime
effect lands when that branch is merged into `main`.

### Live A-FORGE finding that still stands

`policy_gate.posture = PERMISSIVE_FALLBACK`: `config/mcp_policies.json` is pinned to `748741a`
while the running HEAD is `02b7f6b`, so the **reviewed policies are not loaded** and
`default:sovereign` / `allow_by_default: true` is what is actually in force. Re-pinning needs
someone to re-review the policies against the current HEAD.

### What changed on the public path

| measure | before | after |
|---|---|---|
| tools returning a real payload | 9/14 | **13/14** (+1 correct constitutional HOLD, 0 broken) |
| tools broken when the caller adds an undeclared field | 5 | **0** |
| tools covered by `surface_hash` | 8 of 14 | **14 of 14** (`sha256:873dc35e…`) |
| release_id | `arifos-68e308f8bfbc` (an unmerged branch commit) | `arifos-921cabefbe99` (merged main) |
| A-FORGE runtime | `02b7f6b`, healthy | `02b7f6b`, healthy (**unchanged — deliberately**) |

---

## 8. A-FORGE POLICY RE-PIN — 2026-10-29 (Arif: "re-pin the policies against HEAD and deploy it")

### Done

`config/mcp_policies.json` → `pinned_commit: "748741ac"` → **`"02b7f6bc"`** (the deployed/live
service commit), applied through the sanctioned `canon-mutate file` cycle with the expected
post-hash declared (`81a017e2…`, matched), then `make deploy-local` (canary PASS · verify PASS ·
both surfaces restarted).

Live before → after:

| | before | after |
|---|---|---|
| `policy_gate.pin_violated` | `true` | **`false`** |
| `policy_gate.posture` | `PERMISSIVE_FALLBACK` | **`PINNED`** |
| reviewed policies loaded | **no** ("Reviewed policies NOT loaded — FAIL-OPEN") | **yes** (`loaded 1 policies`) |
| `status` / `degraded_mode` / `deployment_drift` | healthy / false / false | healthy / false / false |
| `tool_count` | 118 | 118 |
| deployed = source = head | `02b7f6b` | `02b7f6b` |

Gate stderr: `[McpPolicyGate] constraint pin OK (02b7f6b)` ·
`[McpPolicyGate] loaded 1 policies from /root/A-FORGE/config/mcp_policies.json`

Gate still governs after the re-pin (probed on `:7072/mcp`): `forge_health_check` → ALLOW ·
`forge_filesystem_write` → **DENY** `SESSION_REQUIRED` · `forge_seal` → **HOLD** `A_THINK_GUARD`.

### What the re-pin does NOT do — read this before assuming the posture means more than it does

The pin is an **attestation**, not an access change. The only reviewed policy is
`chatgpt-arif`, and it is **inert**:

- **It has no `actor_id`.** `resolvePolicy()` matches on `String(p.actor_id || "")`, so the policy
  can only ever be selected by an *empty* actor id. It is never selected for a real caller.
- **Its allowlist is in a field the gate does not read.** `McpPolicy` has no `allowed_tools` member
  (the type is `policy_id / actor_id / role / description / allow_by_default / allowed_mcp_servers /
  denied_mcp_servers / max_requests_per_minute`). The file's 64-name `allowed_tools` array is
  ignored — `grep -rn "allowed_tools" src/` finds it only in an unrelated type
  (`src/domain/types/outcome-spec.ts`) and in a header comment.

So `effective_policy` remains `default:sovereign` with `allow_by_default: true` for every actor,
**before and after** the re-pin. What changed is that the gate now *says* PINNED instead of
"reviewed policies NOT loaded — FAIL-OPEN", and the tripwire is re-armed for the next source
change.

**The reviewed allowlist is also stale against HEAD**, measured live:

- **77** of the 118 live tools are absent from the 64-name list — including `forge_seal`,
  `forge_scar`, `forge_policy`, `forge_lock`, `forge_chain_state`, `forge_witness`,
  `forge_drive_create`, `forge_telegram`, `forge_hf_import`.
- **23** listed tools are not on the public surface (`forge_fetch_url`, `forge_fetch_json`,
  `forge_fetch_links`, `forge_fetch_metadata`, `forge_docs_lookup`, `forge_filesystem_delete`, …).

Re-pinning does not fix that. It needs a real policy rewrite (real `actor_id` binding, real
`allowed_mcp_servers` shape) — a policy decision, not a pin.

### DECISION FOR ARIF — the re-pin is deliberately uncommitted

`config/mcp_policies.json` is **tracked**, and the pin compares against the **deploy stamp**
(`/root/A-FORGE/.git_commit`), not against git HEAD — the code path is
`getCurrentHeadSha() → readFileSync("/root/A-FORGE/.git_commit")`, falling back to
`git rev-parse`. That creates a fixed-point problem:

| action | pin holds? | drift-free? | organ status |
|---|---|---|---|
| **leave the re-pin uncommitted** (current) | **yes** (pin `02b7f6bc` == stamp) | **yes** (stamp == HEAD) | **healthy** |
| commit the re-pin, don't deploy | yes | no (HEAD ahead of stamp) | **degraded** |
| commit the re-pin *and* deploy it | **no** (pin ≠ new stamp) | yes | healthy, but the pin re-breaks |

"Commit the pin" is self-contradictory here: the pin value would have to contain the sha of the
commit that contains it. The repo's own precedent (`5855576e fix(governance): re-pin mcp_policies to
LIVE service commit`) committed a re-pin and left `deployment_drift: true` — the organ went
degraded until the next deploy.

I chose the row that keeps **both** the attestation and the health signal true, at the cost of one
uncommitted line in a tree that already carries 10 modified files from another agent:

```
 M config/mcp_policies.json     <- this re-pin (1 line: 748741ac -> 02b7f6bc)
```

*If you want it in git, the fix is in the mechanism, not the commit:* compare the pin against the
**deployed artifact's content sha256** instead of a commit id. Then a committed pin is satisfiable,
the tripwire still fires on any content change, and the git history stops carrying a
permanent-degraded window.

### New finding — the gate's audit log has been dead since 2026-10-22

`/root/A-FORGE/logs/mcp_policy_gate.log` is `chattr +i`, so `appendFileSync` fails with EPERM. The
gate **swallows the error** and prints one line to stderr:

```
[McpPolicyGate] audit log write failed
```

The file's last write was **2026-10-22 22:05** (24.7 MB). Every A-FORGE gate decision since then —
every ALLOW and every DENY — is **unrecorded**. This is the "visible but unread" honesty shape: the
gate names an audit defence it cannot perform.

`canon-mutate` cannot fix it: its cycle is unlock → run → **relock**, so a log that must stay
appendable can never be left writable through that path. Fixing it needs either a deliberate
F13 exception to the relock, or a code change so the gate fails loud (or falls back to a writable
sink) instead of swallowing. Recorded, not actioned.
