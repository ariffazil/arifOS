# HOUSEKEEPING BASELINE — 2026-10-29

**Status:** read-only baseline. This file is the ruler. Every later claim is a diff against it.
**Probe path:** `https://mcp.arif-fazil.com/mcp` (public). Local `127.0.0.1:8088/mcp` used only to
prove a defect is *not* remote-specific.
**Agent:** `qwen-fi003` (lane 333-AGI, FI-003). Never `arif` / `arif-fazil`.
**Probed at:** 2026-10-28T16:24–16:43Z (2026-10-29 00:24–00:43 MYT)
**Release probed:** `arifos-7599f1c42cf9` · canon `2026.10.26-83bae89`

---

## 1. arif_init (public path)

| field | value |
|---|---|
| `session_id` | `SEAL-7af0ddd7a4ef4e54` |
| `actor_id` | `qwen-fi003` |
| `actor_verified` | `false` |
| `authority` / `autonomy_band` | `OBSERVE_ONLY` |
| `verdict` / `effective_verdict` | `HOLD` |
| `reason_code` | `NEEDS_REVIEW` |
| `release_id` | `arifos-7599f1c42cf9` |
| `surface_hash` | `sha256:6295a69b2fb7444ce7b75594606c564e07369346cb23b47fbe6ddceb61ff6290` |
| `constitution_hash` | `arifos-constitution-v2026.05.05-SSCT` |
| `trace_id` | `trc-42217bd07832` |
| `call_hash` | `sha256:35f78238ac3bf8ce9ae381faf505cf8f31745e67e4b3c01b21d3fa5361500d43` |

Identity spelling as echoed by the kernel: **one** spelling — `qwen-fi003`. It round-tripped
`actor_id` unchanged through init, and the same string was accepted by all subsequent calls.
A **second** `arif_init` returned a *different* `session_id` (`SEAL-4fbdacb2850346e0`) for the same
actor — two sessions coexist for one actor id (see §7 DECISIONS).

**Identity fields observed across the surface:** `actor_id`, `actor`, `actor_claimed`,
`actor_verified`, `actor_cryptographically_verified`, `canonical_id`, `canonical_actor_id`,
`sovereign_id`, `caller_actor_id`, `executor_actor_id`. All are distinct *fields*, not distinct
*spellings of the same value* — the four spellings named in the brief (`arif` / `arif-fazil` /
`ARIF` / `ARIF_FAZIL`) appear only as **value** variants of the sovereign identity, not as
inconsistent key names. See §3.

---

## 2. Public tool surface — every exported tool, called once

`tools/list` from the public path returns **14** tools.

| # | tool | public-path verdict | latency | call_hash (from response) |
|---|---|---|---|---|
| 1 | `arif_init` | **OK** | 2479 ms | `42c935acad902c52…` |
| 2 | `arif_observe` | **OK** | 1865 ms | `0cbd6706ab68bbad…` |
| 3 | `arif_think` | **OK** | 14781 ms | `5a86a4396d29763e…` |
| 4 | `arif_route` | **OK** | 1744 ms | `3839b9d3c8b3ad7e…` |
| 5 | `arif_memory` | **OK** | 1927 ms | `dd86df7097166111…` |
| 6 | `arif_judge` | **OK** | 1982 ms | `25af8f8047f00ee0…` |
| 7 | `arif_forge` | **OK** | 160 ms | — (dry_run envelope) |
| 8 | `arif_seal` | **OK** | 1550 ms | `fe8020241bdd3468…` |
| 9 | `arif_report` | **OK** | 902 ms | `87c0468b872e753e…` |
| 10 | `read_resource` | **ERROR** | 144 ms | — |
| 11 | `search_resources` | **ERROR** | 189 ms | — |
| 12 | `arif_research` | **ERROR** | 292 ms | — |
| 13 | `arif_recall` | **ERROR** | 146 ms | — |
| 14 | `arif_delegate` | **ERROR** | 270 ms | — |

**BASELINE: OK = 9 · HOLLOW = 0 · ERROR = 5 · total = 14.**
Five of fourteen public tools are dead — **35.7% of the public surface returns an error.**

### 2a. The 5 failures are NOT remote-specific

The identical 5 tools fail the same way against `http://127.0.0.1:8088/mcp`:

```
LOCAL read_resource      isError=True :: Error calling tool 'read_resource'
LOCAL search_resources   isError=True :: Error calling tool 'search_resources'
LOCAL arif_research      isError=True :: Error calling tool 'arif_research'
LOCAL arif_recall        isError=True :: Error calling tool 'arif_recall'
LOCAL arif_delegate      isError=True :: Error calling tool 'arif_delegate'
```

A **fully minimal** call (only the schema-required argument, no envelope fields at all) also fails:

```
MINIMAL read_resource      isError=True
MINIMAL search_resources   isError=True
MINIMAL arif_research      isError=True
MINIMAL arif_recall        isError=True
MINIMAL arif_delegate      isError=True
```

So these tools are dead for **every caller on every path**, not only remote ones.

### 2b. Exact server-side cause

`journalctl -u arifos.service` (the FastMCP traceback is Rich-rendered; flattened here):

```
fastmcp/server/server.py:1497 in call_tool
fastmcp/tools/base.py:452 in _run
fastmcp/tools/function_tool.py:536 in _execute
arifosmcp/server.py:146 in _d3_wrapped_validate_input
    146 │   raise ValueError(_clean) from e.__cause__
ValueError: CONTRACT_VIOLATION: _envelope: Unexpected keyword argument
            [type=unexpected_keyword_argument, input_type=dict];
            actor_id: Unexpected keyword argument [...];
            session_id: Unexpected keyword argument [...];
            session_token: Unexpected keyword argument [...]
```

Mechanism (source-read, not inferred):

- `arifosmcp/runtime/ingress_middleware.py:1641-1645` — for **every** tool call the middleware
  assigns `msg.arguments["_envelope"]` and `setdefault`s `actor_id` / `session_id` **before** FastMCP
  validates the input.
- `arifosmcp/runtime/ingress_middleware.py:1654-1660` — unknown fields are then popped using
  `self._tool_param_sets[tool_name]`, **but only `if known is not None`**.
- `arifosmcp/runtime/tools.py:30104-30107` — `_tool_param_sets` is populated **only** on the
  canonical-tool registration path (`register_tool_params`).
- `arifosmcp/runtime/tools.py:30234-30253` — the 5 failing tools are registered by a *different*
  path (`register_resource_bridge()` / `register_copilot_facade()`), which **never** calls
  `register_tool_params`.

Two consequences, both live:

1. The 5 tools' signatures do not accept `_envelope`/`actor_id`/`session_id` → `CONTRACT_VIOLATION`
   → "Error calling tool".
2. Their param sets are unregistered → the unknown-field filter is **skipped entirely**, so any
   extra field a caller sends (`session_token` above all) reaches FastMCP unfiltered.

The canonical 8 avoid both problems because they declare the envelope fields *and* get registered.

---

## 3. Identity spellings

| spelling | where it appears | verdict |
|---|---|---|
| `arif` | actor_id value; `CANONICAL_ACTORS` key | live value variant |
| `arif-fazil` | DID `did:web:arif-fazil.com`, domains, npm package author | live value variant (identity/DID) |
| `ARIF` | `actor_id.upper() == "ARIF"` sovereign-bypass branch (`runtime/authority.py:225`) | live value variant |
| `ARIF_FAZIL` | `owner: ARIF_FAZIL` on every `arifos://` resource; `resources_index.py:328-333` | live value variant (ownership label) |

Kernel code that resolves these: `arifosmcp/contracts/identity.py` — `CANONICAL_ACTORS` (line 271)
and `normalize_actor_identity()` (line 411) — plus
`arifosmcp/runtime/governance_identity.py:204 normalize_actor_id()` and
`arifosmcp/runtime/session.py:700 _canonical_actor_key()`.

**Probed behaviour:** the kernel echoed `actor_id` **verbatim** as `qwen-fi003` through init →
observe → think → route → memory → judge → forge → seal → report. No spelling drift observed for a
non-sovereign actor. The four spellings are distinct *roles* (actor id / DID / sovereign branch /
resource ownership), and the A-FORGE TS side is a separate implementation that must be checked
against the Python one — see §7.

**Not proven:** that the four sovereign spellings converge to one canonical id across
arifOS (Python) → A-FORGE (TypeScript). That is measured in item 3, not here.

---

## 4. Organ health (public path where exposed, organ MCP otherwise)

| organ | probe | result |
|---|---|---|
| GEOX | `geox_surface_status` | **healthy** · `REGISTRY_PASS` · 27/27 public tools · 52 resources · 16 prompts · sha `geox-ff1b79bd` |
| WEALTH | `capital_registry mode=health` | **ALIVE** · v`2026.07.24` · 15 canonical / 15 public tools · `federated-15-canonical` |
| WELL | `well_registry_status` | **REGISTRY_PASS** · 10 intended / 10 registered / 10 exported / 10 callable · 0 phantom · `OPERATOR_VETO_INTACT` |
| A-FORGE | `forge_health_check` | **healthy** · v`2.0.0-genome-stable` · ledger `VAULT999_MERKLE_SEALED` · immune `F9_ANTI_HANTU_ACTIVE` · 172 telemetry events · 1 failure (`forge_journalctl` ×1) |
| A-FORGE | `forge_chain_state` | **UNREACHABLE** — `SESSION_REQUIRED` / `STATELESS_WHITELIST` gate over HTTP; refuses both actor-only and actor+session_id calls |

`/api/build-info`: sha `7599f1c`, branch `main`, version `2026.10.26-83bae89`, `tool_count` 63.
`/health?detail=1`: `tools_loaded` 14 · `canonical_tools_loaded` 8 · `coordination_tools` 6 ·
`tools_registry_size` 63 · `diagnostic_tools` 40 · `total_declared_tools` 54.

---

## 5. `arif_seal` — what `mode=verify` actually returns

**The brief expects `arif_seal mode=verify` → ledger_size, vault_dir, integrity. It does not
produce those.** All four modes (`verify`, `ledger`, `audit`, `changelog`) return the *same*
session-authority payload:

```json
{"session_id":"SEAL-7af0ddd7a4ef4e54","actor_id":"qwen-fi003",
 "autonomy_band":"OBSERVE_ONLY","mutation_allowed":false,"seal_allowed":false,
 "reasons":["L11 AUTH: session_id not found or expired"],
 "allowed_next_verbs":["arif_init","arif_observe","arif_think","arif_route","arif_memory","arif_judge"]}
```

There is **no** vault ledger read in `mode=verify`. Any vault-integrity number quoted from this
tool would be fabricated. Vault truth must be read from the filesystem (§6).

---

## 6. Vault paths (item 5 — report only)

| path | files | lines | size | note |
|---|---|---|---|---|
| `/root/.local/share/arifos/vault999` | 789 | 24 272 | 73 M | path named in the brief as the `arif_seal verify` target |
| `/root/arifOS/VAULT999` | 9 694 | 846 320 | **13 G** | in-repo vault; 15% of the whole filesystem |
| `/var/lib/arifos/vault999` | 37 | 6 328 | 34 M | systemd-written path (10 units reference `vault999`) |
| `/root/VAULT999` | 0 | 846 320 | 0 | symlink → `/root/arifOS/VAULT999` |

Four paths, three distinct contents, 73 M + 13 G + 34 M. **Arif decides which is canonical.**
Not merged, not moved, not deleted by this baseline.

---

## 7. Disk (item 6 — report only, nothing deleted)

`/` → 387 G total, **355 G used, 33 G free, 92% used**.

Top consumers (largest first):

| size | path | note |
|---|---|---|
| 21 G | `/root/.cache` | largest single reclaimable class |
| 19 G | `/root/runtime` | |
| 15 G | `/root/arifOS` | of which **13 G is `VAULT999`** |
| 6.7 G | `/root/.codex` | |
| 4.8 G | `/root/.npm-global` | |
| 3.9 G | `/root/.rustup` | |
| 3.5 G | `/root/GEOX` | |
| 3.2 G | `/root/.npm` | |
| 2.4 G | `/root/arifFlow` | |
| 1.8 G | `/root/.kimi-code` | |
| 1.8 G | `/root/.config` | |
| 1.6 G | `/root/.grok` | |
| 1.5 G | `/root/.venvs` | |
| 1.3 G | `/root/xerj-data` | |
| 1.3 G | `/root/.qwen` | |
| 1.1 G | `/root/arifFlow-rg2-verify` | |
| 1013 M | `/root/.hermes-backups` | |
| 789 M | `/root/thinkingbox-eval` | |
| 727 M | `/root/xerj-work` | |
| 710 M | `/root/privacy-rewrite-20260930` | |

Nothing was deleted. Candidate classes for Arif to approve: `.cache` (21 G), `.npm` (3.2 G),
`VAULT999` (13 G, but it is the immutable ledger — needs a separate decision), `*.rg2-verify`
/ `*-rewrite-*` / `*-eval` worktree-shaped directories.

---

## 8. Repo census

### 8a. AGENTS.md sizes — **item 7 premise is FALSE**

No `AGENTS.md` anywhere in the three repos exceeds 32 KB. Repo-root sizes:

| repo | `AGENTS.md` | files named AGENTS.md in tree | any > 32 KB |
|---|---|---|---|
| arifOS | 2 883 B | 5 | **no** |
| AAA | 4 075 B | 29 | **no** |
| A-FORGE | 3 693 B | 3 | **no** |

There is no 32 KB trimming job to do. Item 7 is a **non-finding**.

### 8b. Open PRs / issues

| repo | open PRs | open issues |
|---|---|---|
| arifOS | 8 (newest #963, 2026-10-26) | 4 (newest #958) |
| AAA | 0 | 0 |
| A-FORGE | 8 (newest #139, 2026-10-28) | 2 (#129 flaky, #128 Weekly Repo Hygiene) |

### 8c. Branches older than 30 days

- **arifOS** — 15 shown, oldest `federation/terminology-alignment` 2026-09-14.
  Most recent stale: `feat/record-seal`, `feat/record-append` (2026-09-27),
  `deploy-20260923` (2026-09-23).
- **AAA** — 15 shown, oldest `origin/backup-secret-redaction-20260903T085753Z` 2026-09-03.
- **A-FORGE** — 10 shown, oldest `chore/2026-08-11-remove-minimax-and-audit-tools` 2026-08-12.

None were deleted or moved by this baseline.

### 8d. Root clutter (`.bak` / snapshot)

| repo | file | size | mtime |
|---|---|---|---|
| arifOS | `requirements.txt.bak-20261026T014804` | 385 KB | 2026-10-25 |
| arifOS | `uv.lock.bak-20261026T014804` | 1.4 MB | 2026-10-17 |
| AAA | `codex-home-inversion-2026-10-19.snapshot.txt` | 5.8 KB | 2026-10-19 |
| A-FORGE | `litellm-config.yaml.bak-20261026-pre-dropinclude` | 91 KB | 2026-10-26 |
| A-FORGE | `litellm-config.yaml.bak-20261026-qfree` | 78 KB | 2026-10-26 |
| A-FORGE | `litellm-config.yaml.bak-888-override-20261019T003058Z` | 78 KB | 2026-10-19 |
| A-FORGE | `litellm-config.yaml.bak-aliasfix-20261019T010948Z` | 79 KB | 2026-10-19 |
| A-FORGE | `litellm-config.yaml.bak-deepseek-or-p2-20261021T084110Z` | 85 KB | 2026-10-21 |
| A-FORGE | `litellm-config.yaml.bak-deepseek-responses-20261027T190337Z` | 106 KB | 2026-10-27 |
| A-FORGE | `litellm-config.yaml.bak-glmfix-20261027` | 102 KB | 2026-10-27 |
| A-FORGE | `.bak-pre-rebuild-2026-09-21/` (dir) | — | 2026-09-21 |
| A-FORGE | `.git_commit.bak-20261027T184944Z` | 9 B | 2026-10-28 |

### 8e. Tracked files over 1 MB

- arifOS: `uv.lock` (1 M), `static/arifos/APEX FORGE.png` (1 M), `arifosmcp/runtime/tools.py` (1 M),
  `.ua/intermediate/batches.json` (1 M).
- AAA: `research/mcp-registry-company-export-2026-09-25.json` (**9 M**),
  `research/mcp-registry-company-export-2026-09-25.v1.bak.json` (6 M),
  `reflections/sado-night-truth/2026-10-18.wav` (8 M),
  `forge_work/2026-10-17-gema-bumantara/ig-story.png` (8 M),
  `deliverables/Lebah-Emas-Kartun-2026-10-19.pdf` (8 M), + 5 more 3 M entries.
- A-FORGE: none.

---

## 9. `surface_hash` coverage (item 2 — the ruler for item 2)

The released `surface_hash` is computed **at runtime** by
`arifosmcp/runtime/build.py:170 _compute_tool_surface_hash()`:
SHA-256 over `{name: {"name": name}}` for every name in
`arifosmcp/runtime/public_registry.py:1213 public_tool_names()`.

Reproduced against the live server:

```
GET http://127.0.0.1:8088/tools.json  →  8 tools
hash over those 8 = sha256:6295a69b2fb7444ce7b75594606c564e07369346cb23b47fbe6ddceb61ff6290
LIVE release surface_hash = sha256:6295a69b2fb7444ce7b75594606c564e07369346cb23b47fbe6ddceb61ff6290
MATCH: True
```

The 8 hashed names are exactly:
`arif_forge, arif_init, arif_judge, arif_memory, arif_observe, arif_route, arif_seal, arif_think`.

The live public surface exposes **14**. The **6 tools outside the hash** are:

```
arif_report, read_resource, search_resources, arif_research, arif_recall, arif_delegate
```

**Therefore: removing any of those 6 from the public surface leaves `surface_hash` unchanged.**
Five of the six are exactly the five broken tools from §2 — a caller has no way to detect that the
surface changed, or that the coordination tools are dead, from the release attestation.

The hash mechanism itself is sound — adding a tool to its input set changes it:

```
compute_surface_hash() = sha256:9a3bd15ae3adcde65d3927bb225d2b662cdab20c477967d442d919f8fd07091b
after adding 1 tool     = sha256:5dcb60e96a4411ed7b50d819d22dce8eda84e052104f23ca979600fc883ad7fb
changed: True
```

(The defect is in the **input set**, not the hash function.)

Secondary finding — the kernel's own consistency verifier cannot see this drift:

```
verify_surface_consistency():
  canonical_hash: c78bcb13dc536590   canonical_count: 6   verdict: CONSISTENT   divergences: []
  vantages: active_surface(public_agent) 6 · CANONICAL_13 8 · CANONICAL_TOOLS(mode) 6
            CANONICAL_TOOLS(full) 25 · public_tool_specs 6 · tool_registry.json 8
```

It compares **internal** vantages only. It never compares against the tool set the public
`tools/list` actually returns. A 6-vs-14 divergence is reported as `CONSISTENT`.

---

## 10. Working-tree state at baseline time (other agents' work)

The arifOS working tree already carried **uncommitted** changes from another agent when this
baseline started. They are item-1 work (envelope tolerance for the 5 dead tools) and were left
untouched by the baseline:

```
 M arifosmcp/tools/copilot_facade.py   (mtime 2026-10-29 00:25)
 M arifosmcp/tools/resource_bridge.py  (mtime 2026-10-29 00:09)
 M arifosmcp/tools/sense.py            (mtime 2026-10-29 00:23)
 M tests/test_copilot_mcp_surface.py   (mtime 2026-10-29 00:16)
```

`tests/test_copilot_mcp_surface.py` → **5 passed** at baseline time (43 s). The in-flight fix
covers the injected triple but not `session_token`, and still leaves the 5 tools unregistered with
the ingress middleware (§2b consequence 2).

AAA and A-FORGE also carry uncommitted work from other agents — untouched.

---

## 11. Baseline summary numbers

| measure | baseline (2026-10-29) |
|---|---|
| public tools exported | 14 |
| tools OK from public path | **9** |
| tools HOLLOW | 0 |
| tools ERROR | **5** (`read_resource`, `search_resources`, `arif_research`, `arif_recall`, `arif_delegate`) |
| tools covered by `surface_hash` | **8 of 14** |
| organs healthy | 4 / 4 (GEOX, WEALTH, WELL, A-FORGE) |
| `arif_seal mode=verify` returns vault integrity | **no** |
| disk used | **92%** (355 G / 387 G) |
| AGENTS.md over 32 KB | **0** (item 7 is a non-finding) |
| distinct vault paths | 4 (73 M / 13 G / 34 M / symlink) |
| identity spellings of the sovereign value | 4 (`arif`, `arif-fazil`, `ARIF`, `ARIF_FAZIL`) |
| identity *field* names | 11 distinct |
| actor-id drift observed end-to-end | **none** |

---

## 12. Post-baseline movement (recorded, not folded into the baseline)

The baseline above is a point-in-time ruler taken at 00:24–00:26 MYT. Three things
happened after it, and are recorded here rather than rewriting the baseline.

### 12a. Another agent deployed a partial fix at 00:27 MYT

Commit `d67e6cfbf` ("fix(mcp): envelope-tolerant coordination tools +
degraded-not-ok facade honesty") was deployed at 00:27 MYT — *after* the baseline
probe — from the working tree, before the commit existed
(receipt `/opt/arifos/current/receipts/2026-10-28T16:27:16Z.json`).

Re-probe at 00:59 MYT from the public path, minimal arguments:

| tool | baseline 00:25 | re-probe 00:59 |
|---|---|---|
| `read_resource` | ERROR | **OK** (`status: ok`) |
| `search_resources` | ERROR | **OK** (`count: 1`) |
| `arif_research` | ERROR | **degraded** (honest: `no_evidence_gathered`) |
| `arif_recall` | ERROR | **degraded** (honest: `no_matching_evidence`) |
| `arif_delegate` | ERROR | **degraded** (honest: `intent_unclassified`) |

So the five-tool error class was largely closed by that deploy. Note the release
id did **not** change: `arifos-7599f1c42cf9` still, because the release id is the
source SHA and the deploy shipped an uncommitted tree.

### 12b. The unknown-field path was still open after that deploy

Re-probe at 01:02 MYT, same five tools, **adding one undeclared field**
(`session_token`) — the field the canonical tools all accept:

```
read_resource      isError=True  Error calling tool 'read_resource'
search_resources   isError=True  Error calling tool 'search_resources'
arif_research      isError=True  Error calling tool 'arif_research'
arif_recall        isError=True  Error calling tool 'arif_recall'
arif_delegate      isError=True  Error calling tool 'arif_delegate'
```

`d67e6cfbf` made the five tools tolerate the fields the middleware *injects*
(`_envelope` / `actor_id` / `session_id`). It did not close the path where a
*caller* supplies an extra field, because those five tools were still never
registered with the ingress middleware, so the unknown-field filter was skipped.
That is the gap closed by the first commit on this branch.

### 12c. Live providers are exhausted (not a code defect)

During the in-process verification the evidence layer reported:
Groq `429 quota exhausted`, Cerebras `402 payment required`, Gemini transport
error, and `Postgres password authentication failed for user arifos_admin`.
This is why `arif_research` / `arif_recall` / `arif_delegate` return `degraded`
rather than `ok` — the honesty contract working as intended, not a regression.

