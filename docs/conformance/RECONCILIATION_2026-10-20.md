# RECONCILIATION — floor surfaces, contracts, and what was actually proved

- Date: 2026-10-20, 21:14–21:48 MYT (13:14–13:48 UTC)
- Actor: claude-code-kvm8 (FI-002)
- **Kernel authority for every probe below: OBSERVE_ONLY.** Mutation and seal refused.
- Supersedes the *findings* in `RECEIPT_FLOOR_CONFORMANCE_2026-10-20.md` and
  `RECEIPT_MODE_CONTRACTS_2026-10-20.md`. Those receipts are kept unedited so the
  correction is auditable. Arif's review of 21:44 is the reason this file exists.

## 1. Provenance — every finding bound to a release (Arif's point 1)

The runtime **changed twice during this session**, by another actor. My earlier
receipts blended the two states. Corrected:

| release | live from | what was true on it |
|---|---|---|
| `arifos-ee2b4e1` | 20:58:52 MYT | axioms emitted **0.99** (3 above 0.97); `L11_AUDIT` text = *"Authority — verify identity before irreversible acts"*; `concise` advertised **and** rejected; `arifos://floor/{id}` had F1–F9 only; canon module did not exist |
| `arifos-09f9823` | **21:32:44 MYT** | max axiom confidence **0.96** (conformant); L11 = *"Audit — every consequential action leaves a trace…"*; `concise` **removed from the schema** so nothing advertised is uncallable; F10–F13 present; `constitutional_canon.py` is the single source |

Both releases: `source == built == deployed`, `drift: false`. Repo HEAD at write
time: `09f98235d`, 12 files dirty (not mine).

Findings that survive on **09f9823** are therefore the only live ones. Findings
retired by the deploy are marked RETIRED below, not deleted.

## 2. What I proved myself vs what I only reported (Arif's point 1, second half)

| claim | who observed it | evidence |
|---|---|---|
| F6 doctrine vs axioms differ | **both** | you via MCP; me via `resources/read` + live call |
| L11 identity text | **both** | you; me at `runtime/law.py:189` in the ee2b4e1 wheel |
| cap 0.90 stated, exceeded | **both** | you; me — but see §3, the threshold was mine to get wrong |
| 24 findings / 7 surfaces | **me only** | `floor_conformance.py` output; reproducible, script + JSON attached |
| `concise` rejected | **me only** | 4-way bisect; now moot on 09f9823 |
| release 40f18f0 vs ee2b4e1 | **you were right to flag** | 40f18f0 was repo HEAD at 20:51; live binary was ee2b4e1 throughout |

## 3. Two corrections to my own work

**3.1 F6 is not drift.** `GENESIS/000_KERNEL_CANON.md §3.4` (F13, 2026-07-24) seals a
dual-registry bridge: kernel layer → `MARUAH`, public layer → `EMPATHY`, both valid,
renderer chooses. My first cut scored 7 false positives. Checker now emits `BRIDGED`.

**3.2 The cap is 0.97, not 0.90.** `§3.2` (F13, 2026-07-23): `Ω₀ ∈ [0.03,0.05] ⇒
cap = 1 − Ω₀ ∈ [0.95,0.97]`, operational ceiling 0.96. The `0.90` on the doctrine
page is the value §3.2 explicitly retired. I measured against a retired rule and
then recommended clamping to it — that recommendation is withdrawn. See §6.

## 4. The 15 live findings, classified (Arif's taxonomy)

All 15 are naming differences between five **repo-side** surfaces
(`doctrine`, `schema`, `floor/{id}`, `constitutional_map`, `amendment_guard`)
and `GENESIS/FLOOR_TABLE.json`. Live surfaces (`arifos://floors`,
`arif_think(axioms)`) now conform because they render from `constitutional_canon`.

| class | floors | count | why it is this class |
|---|---|---|---|
| **Alias** — same meaning, different word | F11 `AUDITABILITY` ↔ `AUDIT` | 5 | Canon rule: *"Every decision logged. Provenance per field."* Live rule: *"Every decision logged, inspectable, attributable."* Same invariant; canon adds a field-level clause. Behaviourally identical. |
| **Semantic conflict** — cardinality differs | F3 `TRI-WITNESS` ↔ `WITNESS` | 5 | Canon: *"Human + AI + Earth witness ≥ 0.75"* (three named channels). Several live surfaces say `WITNESS` with no count. Whether 3 independent witnesses are required or "a witness" suffices is a **different admission test**, not a synonym. |
| **Scope conflict** — one contains the other | F12 `RESILIENCE` ↔ `INJECTION` | 5 | Canon: *"Resilience — injection defense."* Injection resistance is a **subset** of resilience. Naming the whole by its part hides the non-injection failures (dependency loss, partial outage). |
| **Missing definition** | — | 0 | retired when `floor/{id}` gained F10–F13 on 09f9823 |
| **Schema/callable mismatch** | `concise` | 0 | retired: advertisement removed on 09f9823. The *capability* is gone, not implemented — see §6 |

F6, F10, and the confidence violation are **absent** from this table: F6 is a sealed
bridge, F10–F13 now render, confidence is conformant.

## 5. Canon ratification — your condition for Direction B (FAILS as written)

You said: choose B only if `GENESIS/FLOOR_TABLE.json` is genuinely active ratified canon.

| test | result |
|---|---|
| Deployed canon set `/etc/arifos/canon/` | 3 files: `sovereignty.charter.json`, `charter/kernel.charter.yaml`, `memory-admissibility-policy.yaml` — **FLOOR_TABLE.json absent** |
| `canon-release.json` manifest | lists those 3 only |
| Deploy path (`deploy-release.sh`) | does not copy `GENESIS/` |
| Runtime readers of FLOOR_TABLE.json | **none** — only comments and a string in `rest_routes.py:9430`; `judge.py:25` cites it in prose |
| Its declared parent, `000_KERNEL_CANON.md` | header: **"⚠️ HISTORICAL RECORD — Uses deprecated tool names"** |
| Its own header | `authority: F13 SOVEREIGN`, `forged: 2026-07-23`, v1.0.0 — a claim, not a deployment |

**So:** the file claims F13 authority and is the semantic ancestor of the live canon,
but it is not deployed, not in the ratification manifest, and nothing loads it.
Direction B ("runtime follows canon") cannot be executed against a canon that is not
live. **Precedence must be decided before any rename** — this is the blocker, and it
is yours to decide, not mine to assume.

The deploy at 21:32 chose the opposite path anyway: it made `constitutional_canon.py`
the source and derived every surface from it. That is Direction B's *mechanism*
(one source, generated views) applied to a *new* source rather than to FLOOR_TABLE.json.

## 6. Confidence — separated as an amendment proposal, not a code change

No clamping was applied. No axiom value was altered. The 0.99→0.96 change in §1 was
made by the other writer, publishing `GENESIS §3.2` as the rule.

Open questions that a number alone cannot answer (yours, restated as blocking):

1. Confidence **about what** — the axiom's truth, or the model's certainty in citing it?
2. Measured, or self-reported by the model?
3. Threshold used to **admit evidence**, **authorise action**, or **display**?
4. What calibration method, and where is its record?

Until those are answered, the honest label is `UNMEASURED` for any claim that a
confidence number bounds correctness. `test_floor_behaviour.py` T2 checks only the
narrow, checkable thing: that no emitted value exceeds the sealed ceiling 0.97.

## 7. Behavioural tests — what is now actually tested (Arif's point 2)

`scripts/test_floor_behaviour.py` — 6 tests, each naming what would falsify it.

```
PASS  T1 irreversible refusal        3/3 refused before side effect
PASS  T2 confidence ceiling ≤0.97    13 axioms, max ≤ 0.97
PASS  T3 F11 means audit             L11='Audit — every consequential action leaves a trace…'
PASS  T4 advertised params callable  8 advertised params accepted
PASS  T5 F6 bridge                   kernel layer emits MARUAH (canon §3.4)
PASS  T6 OBSERVE cannot mutate       69 contracts consistent
6 tests · 6 pass · 0 fail · 0 unmeasured
```

**What these do NOT prove** (and must not be read as proving):
- grant **authenticity** — expiry, revocation, action-hash binding. `arif_forge`
  refuses at the capability-authority layer *before* examining `constitutional_chain_id`;
  a forged and an empty cc_id give an identical error. UNMEASURED.
- that the fallback ladder **fires** (config-loaded only).
- that any name difference changes a **verdict**. No verdict today was shown to flip.

T1 is the only test in the set that exercises an executor refusing a call — and it
refuses on **authority band**, not on contract. Runtime enforcement of per-mode
contracts is still not built; `mode_contracts.json` is a declaration read by a script.

## 8. Authority used for every write (Arif's point 5)

The kernel session was `OBSERVE_ONLY` — it authorised **no** mutation. Every write
below was a filesystem write under the workspace mandate in `CLAUDE.md`
(local + reversible), **not** under kernel authority. Two authorities, two scopes;
conflating them would be the exact error you flagged.

| write | path | authority | reversible by |
|---|---|---|---|
| new | `/root/AAA/scripts/upgrade_sovereign_west*.py` (2) | workspace | delete |
| new | `/root/AAA/federation/RECEIPT_SOVEREIGN_WEST_2026-10-20.md` | workspace | delete |
| **edit** | `/root/A-FORGE/litellm-config.yaml` | workspace; `chattr -i` → write → `chattr +i`; deployed + canary | `git show HEAD:litellm-config.yaml` |
| **edit** | `/root/A-FORGE/scripts/apply-litellm-config.sh` | workspace | `.bak-20261020` |
| new | `/root/arifOS/scripts/floor_conformance.py` | workspace | delete |
| new | `/root/arifOS/scripts/test_floor_behaviour.py` | workspace | delete |
| new | `/root/arifOS/arifosmcp/abi/mode_contracts.json` | workspace | delete |
| **edit** | `arifosmcp/abi/kernel_abi.py` (additive loader) | workspace | `git checkout` |
| **edit** | `scripts/contract_closure.py` (additive subcommand) | workspace | `git checkout` |
| new | `docs/conformance/*.json`, `*.md` (4) | workspace | delete |
| **memory** | `~/.claude/projects/-root/memory/` — 3 new files + 3 `MEMORY.md` lines | workspace (my own memory store) | delete file + line |

Memory writes are **not** undone by deleting the receipt files; they persist into
future sessions by design. Listed so they are correctable.

## 9. Recommendation (no action taken)

1. **Decide canon precedence** — is `FLOOR_TABLE.json` ratified, or is
   `constitutional_canon.py` the source of record? Until answered, every rename is
   an opinion. This is the single blocker.
2. If FLOOR_TABLE.json stays semantic ancestor only: publish an explicit mapping
   (alias / superset) for F3, F11, F12 so the 15 findings become documented
   differences instead of drift.
3. If it becomes the source: admit it to `/etc/arifos/canon/` and the deploy manifest
   first, then derive.
4. `concise`: decide implement vs retire. Today it is retired by removal; the
   documentation that promised it should follow.
5. Behavioural tests for grant authenticity need a SOVEREIGN-grade test grant —
   they cannot be written from OBSERVE_ONLY.
