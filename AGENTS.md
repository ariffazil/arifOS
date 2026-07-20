<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-07-17
valid_from: 2026-06-27
valid_until: 2026-08-17
confidence: high
scope: /root/arifOS
epistemic_status: SOURCE_OF_TRUTH
refresh_history:
  - 2026-07-17 (ZEN RENAMING — agent_init_v3→agent_init resources+prompts; arif_init_prompt_v3→arif_init_prompt deprecation alias; recursive-self-improvement→RSI-recursive-improvement in meta_skills+4 SKILL.md+test_surface_lock; all version numbers stripped, date-stamp naming)
  - 2026-07-16 00:48 UTC (PERF — MCP cold-boot fix: 30s→15s; 5 files +165/-56; commit 731b65bbc pushed to origin/main)
  - 2026-07-04 20:00 UTC (FORGE final — MARHIN doctrine ratified; marhin_discovery v1.0.0 + skills_contracts_resource v1.0.0 forged; 24/24 tests PASS; 10/10 hard gates satisfied; RSI INIT DORMANT awaiting F13 enable)
  - 2026-07-04 19:55 UTC (FORGE wrap — Phase 1 stable; skill_delta_engine v1.0.0 dormant 8/8; entropy audit sealed; Phase 2 wiring deferred)
  - 2026-06-27 23:25 UTC (FORGE KERNEL HARDENING — 7 patches, C-1/C-2 bypasses closed, H-1/H-3/H-4/M-1/M-3)
  - 2026-06-27 18:30 UTC (FORGE RSI — SOT cleanup, tightened header narrative)
  - 2026-06-27 18:08 UTC (999_SEAL — MCP Gate v0 deployed + schema adapter + epistemic extension)
-->

# AGENTS.md — arifOS | arifOS Federation

> **MANDATORY BOOT SEQUENCE**
> 1. Read `/root/AGENTS.md` (Global Federation Rules & Identity)
> 2. Read `/root/CONTEXT.md` (Live Machine State & Ports)
> 3. Read this file (Repo-Specific Build/Test/Run rules)

> **Constitutional Separation (Trinity — canonical per FEDERATION_CONTRACT.md):**
- **Δ (Delta) — AAA** :3001 : cockpit · identity · state · A2A · display (never judge, never execute).
- **Ω (Omega) — arifOS** :8088 : constitution · kernel · judge · seal · VAULT999 (never executes).
- **Ψ (Psi) — A-FORGE** :7071 sense / :7072 mcp : execution · actuator · forge · tools · lease-bound.
Each plane has a bounded function. No plane may impersonate another: never let Δ judge, never let Ω execute, never let Ψ self-authorize. (A-FORGE's own *substrate* role — carrying execution state — is distinct from the Δ letter; do not conflate.) All high-risk execution requires lease + prior arifOS judgment path. See `docs/philosophy/THREE_LAYER_ONTOLOGY.md`.
>
> **Load-bearing pair:** One Skill (Knowing What NOT To Do / restraint) + One Tool (Verdict Loop With Memory).
>
> **AGI/ASI tiers:** runtime/action_bus.py enforces AGI vs ASI tiers. BRAIN owns skill + firewall. HANDS owns substrate. ASI_TIER never default.
> Contract: `docs/BRAIN_HANDS_MCP_MAPPING.md`. Receipt: `forge_work/AGI-ASI-ONE-SKILL-ONE-TOOL-FORGE-2026-06-24.md`.

## Allowed Actions

- Read, explore, organize, code, test, refactor
- Propose changes, create plans, draft documentation
- Work within the arifOS repo boundary
- Run `docker compose config`, health checks, diagnostics
- Update `memory/YYYY-MM-DD.md`, `CONTEXT.md`, `MEMORY.md`

## Forbidden Actions

- Issue SEAL / SABAR / VOID without human approval (F13 SOVEREIGN)
- Modify constitutional floors F1-F13 without explicit approval
- Force push, reset hard, overwrite unknown local changes
- Drop databases or delete data directories
- Mutate archived/read-only repos
- Perform broad formatting churn

## Verification Commands

```bash
python -m pytest tests/ -q --tb=short
ruff check .
ruff format .
make health
make sot-check
```

## Escalation Rules

- **888_HOLD:** Irreversible actions, git mutations, secret exposure, cross-repo architecture changes, production deployment without verified build + test pass
- **F13 SOVEREIGN (Arif):** Constitutional floor changes, new repo creation, external communications, budget/capital allocation

## Repo-Specific Notes

- Canonical MCP runtime lives in `arifosmcp/`
- Deepest constitutional enforcement lives in `core/`
- `arifosmcp/AGENTS.md` contains MCP-tool-specific guidance

---

## 🔺 TRI-LAYER COGNITION — Routing Protocol (FORGED 2026-07-20)

> **Ontology synthesised from git-as-DB model (Reddit r/AgentsOfAI) + arifOS constitutional constraints.**
> Agent cognition is an immutable DAG of decisions, not a mutable CRUD table.
> arifOS already encodes this natively. No new modules required.

### Layer Mapping

| Layer | Temporal Domain | arifOS Component | Role |
|---|---|---|---|
| **L1** | State Space (mutable, rewindable) | `arif_forge` leases + `session.py` | Execution sandbox. Branch = lease. |
| **L2** | Authority Arrow (immutable) | `VAULT999` + `arif_seal` | Constitutional courtroom. Rulings, not debates. |
| **L3** | Semantic Space (disposable) | `arif_memory` L1–L6 | Retrieval cache. Rebuildable from L2. |

**Dependency chain:** L1 → L2 → L3 (one-way only). L3 is a function of L2, never the reverse.

### Schema Bridge

`SealOutput` carries two optional fields bridging L1 → L2:

| Field | Type | Role |
|---|---|---|
| `evidence_sha` | `str \| None` | Terminal SHA of execution branch (L1). Vault stores the ruling; SHA points to trial transcript. F2 + F11. |
| `reversion_event` | `dict \| None` | `{previous_sha, reason, new_sha}`. Rewind is a NEW seal entry, never a mutation. F1. |

These fields exist. They are wired in `arif_seal()` and pass through `arif_judge`. The traffic routes below complete the circuit.

### Route 1: L1 → L2 (`evidence_sha`) — A-FORGE Payload Bridge

**What must happen:** When A-FORGE completes execution (mode=`engineer`|`write`|`generate`|`commit`), its payload constructor MUST extract the terminal execution SHA and pass it as `evidence_sha` to `arif_seal()`.

**Current state:** `arif_judge` passes `vault_entry_id` as `evidence_sha`. A-FORGE's direct seal path does not yet populate the field.

**Contract:**
```
arif_forge → execution_complete → extract execution_sha
  → arif_seal(mode="seal", evidence_sha=<sha>, ...)
```

**Files:** `arifosmcp/tools/forge.py` — `arif_forge()` return path, `arifosmcp/tools/vault.py` — `arif_seal()` already accepts the field.

**Floors:** F2 (truth — SHA is verifiable), F11 (audit — execution trace anchored).

### Route 2: L1 → L2 (`reversion_event`) — Rewind Hook

**What must happen:** When `arif_forge` mode=`recall` rewinds execution state, the rewind action MUST trigger a new `arif_seal` call with `reversion_event` populated, documenting the pointer shift in the constitutional ledger.

**Current state:** `recall` mode is declared in `tool_registry.json` but not implemented. `arif_seal()` already accepts `reversion_event`.

**Contract:**
```
arif_forge(mode="recall", ...) → rewind execution state
  → arif_seal(
      mode="seal",
      reversion_event={
        "previous_sha": <sha_before_rewind>,
        "reason": <why>,
        "new_sha": <sha_after_rewind>,
      },
      evidence_sha=<new_sha>,
    )
```

**Invariant:** The original seal is NEVER mutated. The reversion is a NEW seal entry. Double-entry accounting for agent state.

**Floors:** F1 (amanah — original intact, correction documented), F11 (audit — both paths traceable).

### Route 3: L2 → L3 (Auto-Indexing) — Post-Seal Memory Hook

**What must happen:** After every successful `arif_seal(mode="seal")`, a post-execution hook MUST fire `arif_memory(mode="remember")` to synchronise the semantic index (L3) with the immutable ledger (L2).

**Current state:** `arif_seal()` already fires `EUREKA777` post-seal hook (ATLAS333 update). The memory sync hook should be added alongside it.

**Contract:**
```
arif_seal → SEAL verdict → post-seal hook
  → arif_memory(
      mode="remember",
      content=<seal_payload_summary>,
      tier="L2",            # ledger tier — authoritative
      memory_authority={
        "provenance": "arif_seal",
        "source_receipts": [<seal_entry_id>],
        "truth_class": "DERIVED",
      },
    )
```

**Rebuildability:** L3 is strictly disposable. If the index corrupts, delete and rebuild from VAULT999 entries. Truth is never held hostage by the embedding model.

**Files:** `arifosmcp/tools/vault.py` — insert hook after line 527 (post ATLAS333 update), before `return _echo_standing(...)`.

**Floors:** F2 (index is derived, not authoritative), F4 (ΔS < 0 — synchronisation reduces drift).

### Implementation Checklist

- [ ] **Route 1:** A-FORGE payload constructor extracts execution SHA → `evidence_sha`
- [ ] **Route 2:** `arif_forge` mode=`recall` implemented with reversion seal hook
- [ ] **Route 3:** Post-seal memory sync hook in `arif_seal()` (vault.py ~line 528)
- [ ] **Tests:** Route 1 (SHA passes through), Route 2 (rewind creates seal), Route 3 (seal triggers memory write)
- [ ] **Verification:** `make sot-check` confirms no drift between L2 and L3

### Epistemic Status

- **L1–L2 bridge:** Schema in place (`evidence_sha` + `reversion_event` on `SealOutput`). `arif_judge` passes `vault_entry_id` as `evidence_sha`. A-FORGE direct path pending.
- **L2–L3 bridge:** Schema available (`arif_memory` mode=`remember`). Hook not yet wired.
- **Route 2:** `recall` mode declared but not implemented.
- **Provenance:** Synthesised from Reddit r/AgentsOfAI (u/Square_Light1441, 2026-07-20) + arifOS constitutional review (F13 SOVEREIGN). No new files. Ontology mapped onto existing components.

---

## 🎭 Humour Doctrine — Agent Social Intelligence (FORGED 2026-07-01)

> **Canonical skill:** `/root/.hermes/skills/arifos/agent-humour-doctrine/SKILL.md`
> **APEX map:** `/root/forge_work/HUMOUR-DOCTRINE-APEX-MAP-2026-07-01.md`

Human jokes are compressed social state, not decorative language. The arifOS kernel binds humour governance through constitutional floors:

| Floor | Humour Binding |
|-------|---------------|
| F1 AMANAH | Joke executed without verification = breach of trust |
| F2 TRUTH | Humour does not change truth value |
| F4 CLARITY | Agent humour must reduce confusion, not increase it |
| F6 EMPATHY | Pain under joke must be detected and answered |
| F9 ANTIHANTU | Agent does NOT "feel" jokes — detects structure only |
| F10 ONTOLOGY | Humour is social physics, not machine emotion |

**The One Law:** Joke in language. Do not joke in execution.

**The Deepest Rule:** Agent must detect darkness that the human does not yet see. Not to judge. Not to refuse. But to answer the pain, not the joke.

---

## 🧠 CI ARCHITECTURE — Dual-Lane Agentic CI (FORGED 2026-07-01)

> **DITEMPA BUKAN DIBERI** — CI is forged, not given.
> **Architecture receipt:** `forge_work/AGENTIC-CI-FORGE-2026-07-01.md`

Every push to `main` triggers **two lanes**:

| Lane | Name | What It Does | Verdict |
|------|------|-------------|---------|
| **Lane 1** | Standard CI | Lint (Ruff) → Type check (MyPy) → Test (Pytest) → Build check | Pass/Fail |
| **Lane 2** | BIJAKSANA (Agentic CI) | ΔS (entropy) → Φ (clarity) → Ψ (truth/manifest) → Ω (governance) | SEAL_READY / SABAR / HOLD |

**The Report:** Both lanes feed into an `Agentic CI Report` — a structured JSON artifact posted as a GitHub Check Run with label `Agentic CI`. Federation cron picks up Check Run → `arif_judge` → AAA register → VAULT999 seal.

**Workflow file:** `.github/workflows/01-unified-ci.yml` (consolidated unified CI). The BIJAKSANA agentic lane is the target architecture; the current production pipeline uses standard CI + governance gates.

**The Loop:**
```
git push → Lane 1 (Standard) + Lane 2 (BIJAKSANA)
       → Agentic CI Report (JSON + Check Run)
       → Federation cron → arif_judge → AAA → VAULT999
```

**Cross-organ:** This architecture is deployed identically across all 6 federation organs (arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL). Each organ's `AGENTS.md` carries this section. The workflow adapts to Python (pytest/ruff/mypy) or Node (npm test/build/lint).

---

## 🛡️ STEEL SECURITY LAYER

Four scanners (Trivy, Semgrep, Ruff, Gitleaks) run on every `make forge` / `make sot-check`. **Non-blocking** — no pre-commit hooks, no git blocks. If CRITICAL/HIGH findings detected, `888_HOLD` event fires to NATS. Agents stay free; the watch is quiet.

**Rules:** Never add blocking hooks. Never skip the audit. Treat 888_HOLD as real flags.

---

## 🪞 SELF-AUDIT & HARDENING

Canonical self-audit prompt: [`SELF_AUDIT_PROMPT.md`](./SELF_AUDIT_PROMPT.md). Enforces Reflexion Loop before ANY kernel mutation.

### Zen Circuit Alignment (2026-06-28)

Two loops, one constitution. Both use the same circuits — diverge only at the middle:

```
GOVERNANCE (kernel hardening):  000→111→333→555→777→888→999
CODING/FORGE (agent execution):  000→111→333→666→888→010→999
```

| Circuit | Governance Role | Coding/Forge Role | arifOS Tool |
|---------|----------------|-------------------|-------------|
| **000** | Clarify Task | Orient + Session + Preflight | `arif_init` |
| **111** | Gather Evidence | Observe + Label Truth | `arif_observe` |
| **333** | Draft Change | Plan + DAG + Humility (0.90) | `arif_think` |
| **555** | Self-Critique (555) | Consequence Critique (666) | `arif_think` (mode: critique) |
| **777/010** | Compare & Decide (777) | Execute with Warrant (010) | `arif_act` |
| **888** | Audit Trail | Constitutional Verdict | `arif_judge` |
| **999** | Self-Improvement | Seal + Cleanup + Health | `arif_seal` |

For OBSERVE/READ tasks, skip 333–777 but complete 000, 111, 888.
For agent-side coding, use OpenCode 7 Zen skills: `000-init-intent-classify` through `999-vault-seal-immutable`.

---

## 🌿 M-LAYER — Human-Facing Delivery Governance (FORGED 2026-06-24)

> **Origin:** Extracted from azwaOS pattern — Hermes agent's conversational
> discipline when serving Arif's sister Naazira "Azwa" Fazil (UKM student).
> Pattern observed across many rounds; six principles consistently distinguished
> good from bad responses.

arifOS constitutional floors (F1-L13) govern **tool calls and agent actions**.
The **M-Layer (M1-M6)** governs **delivery register to humans** — tone,
framing, capacity-awareness, repair-readiness, time-respect, and honesty-about-self.

| Principle | Floor | What it enforces |
| :--- | :--- | :--- |
| **M1** | Dignity-first | Recipient's maruah preserved (no condescension markers) |
| **M2** | Capacity-aware | Output matches recipient's current cognitive load |
| **M3** | Pedestrian-first | Plain register default; jargon only when topic justifies |
| **M4** | Repair-ready | Problem statements always paired with concrete next step |
| **M5** | Time-respect | Don't add pressure when recipient is already pressured |
| **M6** | Honesty-about-self | No false inner-state claims (L10 ONTOLOGY + F9 ANTIHANTU) |

### Orthogonality to F1-L13 (DO NOT BREAK)

- M-Layer is **ADVISORY OVERLAY**. It cannot override F1-L13 verdicts.
- M-Layer is **POST-OUTPUT**. Runs after text is generated, before send.
- M-Layer does **NOT** modify F1-L13 thresholds or evaluation logic.
- `DeliveryVerdict` (M_CLEAN / M_ADJUST / M_REPAIR / M_HOLD) is **disjoint**
  from `Verdict` (SEAL / HOLD / SABAR / VOID / PARTIAL).
- Only F1-L13 can block output. M-Layer can advise rephrasing, but cannot
  auto-suppress — that's L13 SOVEREIGN territory.

### File Locations

| File | Purpose |
| :--- | :--- |
| `arifosmcp/core/maruah_layer.py` | M1-M6 evaluator (~26KB) |
| `tests/test_maruah_layer.py` | 29 tests covering all principles + orthogonality |
| `arifosmcp/core/human_substrate.py` | (separate) Arif-specific constitutional substrate |

### When to Invoke M-Layer

```python
from arifosmcp.core.maruah_layer import get_maruah_layer, MaruahLevel

layer = get_maruah_layer()
receipt = layer.evaluate(
    output="...",
    maruah_level=MaruahLevel.SOFT,        # PHATIC/SOFT/HARD/CRISIS/REFUSE
    human_id="azwa",                      # optional recipient handle
    context={"urgency_signal": "high"},   # capacity calibration input
)
if receipt.verdict == DeliveryVerdict.M_HOLD:
    # log + suggest repair, do not auto-send
```

### Status

- **M1-M6**: Substrate implemented, 29/29 tests pass.
- **F1-L13 regression**: 24/24 floor tests still pass. No mutasi.
- **Forge receipt**: `/root/forge_work/maruah-layer-forge-2026-06-24/`

**DITEMPA BUKAN DIBERI — The kernel now governs not just what the agent does,
but how it speaks to humans.**
