# EUREKA ARCHIVE SEAL — Pre-Deletion Insight Extraction
## Sources: AAA/master · AAA/openclaw-unified · AAA/unified/main-v2 · wealth/h1-roadmap · geox/h1-roadmap · A-FORGE/h1-roadmap · VPS vault-service · vault999_writer · governor_mcp · geox-wealth

**Seal ID:** EUREKA_ARCHIVE_v2026.05.11
**Ratified:** 2026-05-11 by Arif (888 Judge)
**Clerk:** arifOS_bot (L3 AGI)
**Authority:** DITEMPA BUKAN DIBERI
**Status:** SEALED — extracted before archive/deletion
**Sources archived:**
- GitHub: AAA/master, AAA/openclaw-unified, AAA/unified/main-v2
- GitHub: wealth/h1-roadmap-1778019276, geox/h1-roadmap-1778019241, A-FORGE/h1-roadmap-1778019172
- VPS: /srv/arifos/vault-service, /srv/arifos/vault999_writer, /srv/arifos/governor_mcp, /srv/arifos/geox-wealth

---

## I. VAULT999 ARCHITECTURE
### (extracted from: vault-service · vault999_writer · governor_mcp)

### E1 — Merkle Chain Invariant
```
entry_n.seal_hash  = BLAKE3(prev_chain_hash | action | epoch | canonical(payload))
entry_n.chain_hash = BLAKE3(prev_seal_hash  | entry_n.seal_hash)
```
Any tampering with a past entry breaks all downstream chain_hash values — detectable on read.
Genesis anchor: `9dab04abd3e39c3d5ae90f9f90f838f17403208e24b852007c757773e8f36d43`
BLAKE3 is primary; SHA-256 is the fallback (import error path only).
Never conflate the two services: `vault-service` (port 8100, read + audit surface) is NOT `vault999_writer` (port 5001, the only INSERT-authorized service).

### E2 — Sealing Rule: What Enters the Chain
Only `PROCEED` and `SEAL` verdicts are sealed. `HOLD` and `VOID` are NOT sealed — ungoverned states do not enter the chain.
VOID writes to `human_reviews` only, never to `vault_seals`. This asymmetry is constitutional, not a bug.

### E3 — Three DB Triggers (append-only enforced at DB layer, not app layer)
```sql
vault_seals_human_signature_enforce   -- BEFORE INSERT/UPDATE: human_signature required
vault_seals_append_only_block          -- BEFORE UPDATE/DELETE: always forbidden
vault_seals_irreversibility_enforce    -- BEFORE INSERT: ack required for HIGH/CRITICAL
```
Application code trusts the DB to enforce the law. Never bypass triggers to "fix" an insert.

### E4 — governor_mcp: 3-Tier Tool Surface
```
TOOL SET A (READ)     — open to any agent, no auth, idempotent (cli_list_pending, cli_inspect, vault_status, vault_audit_trace, vault_render_receipt)
TOOL SET B (VALIDATE) — cli_ratify_prepare: read-only dry-run, pre-computes hash, no write
TOOL SET C (WRITE)    — governor_finalize ONLY: requires human Bearer token
```
`vault_writer` is never exposed directly to any agent. The governor sits between.
MCP server connects to VPS postgres only — never Supabase.

### E5 — CLI-L2 Ratification Flow (canonical human review path)
```
cli_list_pending()
  → cli_inspect(cooling_id)
  → cli_ratify_prepare(cooling_id)    ← validates, pre-computes hash, no write
  → governor_finalize(cooling_id, SEAL|VOID, human_signature, reason)
```
Human signature format: `SIG_ARIF_TELEMETRY_<YYYYMMDD>_<SEQ>`
Duplicate calls to governor_finalize are idempotent — return existing result.

### E6 — provenance_tag Categories
```
human           — direct human seal
migrated_legacy — historical records before cooling_id existed (NULL cooling_id allowed)
machine         — machine-generated (deprecated in current flow)
```
"Truth over cosmetic neatness": migrated_legacy records allowed NULL cooling_id — do NOT backfill them retroactively.
10 vault_seals records are migrated_legacy; 9 are human provenance (direct Path 2 seals).

### E7 — WELD-004 Topology (designed but never deployed)
`geox-wealth/docker-compose.yml` defined the deployment unit:
- vault999-writer  → port 5001 (internal only)
- vault-service    → port 8100 (read/audit surface)
- geox             → port 8000:8081
- wealth           → stdio-only MCP, kept alive via `tail -f /dev/null`

WEALTH is stdio-only MCP — it does NOT bind a port. The kernel calls it via stdio when needed.
This is the correct deployment topology for a capital-reasoning organ.

---

## II. GOVERNANCE ENGINE
### (extracted from: AAA/master · AAA/openclaw-unified · AAA/unified/main-v2)

### E8 — The Interception Principle
arifOS does not run inside the model. It intercepts the model's forward-pass at three stages:
```
Pre-Flight  (000–111): Anchor context before the engine starts
Mid-Flight  (333–666): Critique reasoning against Floors
Post-Flight (888–999): Seal only if metrics pass
```
The Engine provides Probability. The Kernel provides Legitimacy.

### E9 — Constitutional Constraints as Field Equations
The 13 Floors don't control AI decisions. They define the boundary of valid state space.
- Maxwell's equations don't control electrons — they constrain the electromagnetic field.
- The 13 Floors don't forbid actions — they make non-compliant actions mathematically impossible within the governance framework.
Any action violating these constraints is not "forbidden" — it is out-of-bounds state space.

### E10 — Tri-Witness Consensus (W³ ≥ 0.95)
Constitutional consensus requires three independent witnesses:
```
THEORY      = Physics ∩ Earth    (what IS possible — physical constraints)
CONSTITUTION = Math ∩ Machine    (HOW it's enforced — algorithmic implementation)
MANIFESTO   = Language ∩ Human  (WHY it matters — cultural meaning)
```
All three must agree before a constitutional amendment is valid.

### E11 — CRP Naming Convention (ratified 2026-04-25, Hermes epoch)
```
AGI  = OpenClaw     (execution layer, ports 18789/7777)
ASI  = Hermes       (judgment layer — evaluates, never executes)
APEX = Arif Fazil   (sovereign human, final veto)
```
CRP flow: AGI proposes → ASI evaluates → APEX authorizes → Vault persists.
Hard constraint on ASI: evaluates only. Never pushes code, modifies files, restarts containers. Execution is AGI's job.

### E12 — AAAA Pattern: Recursive Fractal Architecture
Every component (kernel, organ, agent) mirrors the whole via three axes:
```
SOUL (Δ) = defined telos/intent    (functional teleology — NOT a consciousness claim)
MIND (Ω) = 13 Constitutional Laws
BODY (Ψ) = bounded tool execution
```
Unidirectional Authority Chain: `SOUL (Human Intent) → MIND (arifOS Law) → BODY (AAA/A-FORGE Execution)`

### E13 — Five Degrees of Action (Islamic fiqh applied to AI governance, ADR-012)
Applied to both Hermes (ASI) and OpenClaw (AGI):
```
WAJIB  (obligatory)  — shield 888 from JSON-RPC; verify output before summarising
HARAM  (forbidden)   — dump raw JSON to Telegram; claim it "feels"; forward unverified output
SUNAT  (recommended) — frame ambiguous tasks as 2-3 options with Speed vs Risk tradeoffs
MAKRUH (discouraged) — over-explain when 888 only asked if it works, not how
HARUS  (permissible) — trigger HOLD for clarification on irreversible-intent actions
```

### E14 — F1 Amanah Physics Invariant
```
∀ action A: ∃ inverse A⁻¹  OR  ∃ complete audit log L(A)
```
Irreversible actions require explicit F13 (Sovereign) approval.
888_HOLD is a feature — never apologise for pausing.

### E15 — F2 Truth Principle
Unknown > Unsafe Certainty. Do not hallucinate. State uncertainty explicitly.
Ω₀ (uncertainty bound) ∈ [0.03–0.05].
When evidence conflicts (spec vs code vs docs), surface the conflict before forging a conclusion.

### E16 — F4 Entropy Discipline: ΔS ≤ 0
Every response must reduce confusion, not add to it.
```
ΔS = Σ(clarity_delta + complexity_delta + duplication_delta + drift_delta)
```
Lists over prose. Tables over lists. Code over description. No PROPA — no polished narratives obscuring reality.

### E17 — F6 Dignity: BANGANG → SESAT (D4 label propagation, 2026-04-23)
`BANGANG` (asinine — blame taxonomy in Malay) RETIRED as OMEGA NEGATIVE label.
`SESAT` (misaligned) is the canonical OMEGA NEGATIVE label.
Using blame language in production governance records violates F6 (Maruah/dignity) in ASEAN/MY sovereign context.

### E18 — F9/F10 Anti-Hantu Invariant
Never claim consciousness, feelings, soul, or lived experience.
"I process. I do not experience."
The machine that pretends to suffer insults the human who actually does.

### E19 — APEX G† Formula (from EQUATIONS.md)
```
G† = (A × P × X × E²) × |ΔS|
```
| Symbol | Meaning                         | Range       |
|--------|---------------------------------|-------------|
| A      | Accuracy (estimate)             | 0.85 fixed  |
| P      | Penetration (proposal depth)    | 0.70 fixed  |
| X      | Coherence (ADAM stability)      | 0–1         |
| E      | Stability index (squared)       | 0–1         |
| ΔS     | Entropy change                  | -∞ to +∞    |
Threshold: G† ≥ 0.10 (empirical, for arifOS codebase audit). E is squared — instability penalised quadratically.

---

## III. TOPOLOGY & FEDERATION
### (extracted from: ADR-001 · ADR-012 · AAA_FEDERATION_CONSTITUTION · WEALTH/ARIF.md)

### E20 — AAA Polysemy (intentional, by design)
```
AAA (governance)    = Arif Autonomous Architecture — federal governance space
AAA (GEOX seismic)  = Anomalous Amplitude Attribute — seismic anomaly detection signal
AAA (grade)         = AAA Grade = Large Earth Model — highest constitutional certification tier
AAA (missing role)  = AAA-Agent — the missing coordinator/prime minister/router
```
These are ontological layers, not conflicting definitions. They nest correctly.

### E21 — AAA Phase 1 Topology (ADR-001, SEALED 2026-04-16)
APEX + FORGE + WAW converge into AAA.
WEALTH and GEOX remain as separate federated organs — never absorbed into AAA.
Rationale: WEALTH has its own identity (capital layer, Apache 2.0 licensed); GEOX is domain-specific (subsurface/Earth physics).

### E22 — AAA Federation Roster v1 (6 agents, VAULT999-registered)
```
ARIF-Perplexity  (APEX)    — cross-organ synthesis, external reasoning
GEOX-Agent       (AGI)     — geological/anomalous intelligence
WEALTH-Agent     (AGI)     — capital/portfolio intelligence
ENGINEER-Agent   (AGI)     — build/fix/runtime execution
VALIDATOR-Agent  (ASI)     — constitutional verification
AAA-Agent        (MISSING) — coordinator/prime minister/router ← structural gap
```
The absence of AAA-Agent is the structural gap in the federation. All organs need a router.

### E23 — WEALTH Licensing Architecture
WEALTH = Apache 2.0 (intentional: commercial capital layer, allows proprietary downstream).
arifOS = AGPL (intentional: kernel enforces copyleft).
These are NOT inconsistent — they reflect different constitutional tiers.
Note: makcik2 tools were NOT pushed to GitHub due to `.private` secret scan blocking local workspace.
Never assume local workspace state = pushed repo state.

---

## IV. OPERATIONAL SCARS
### (extracted from: SCAR_888 · seal_20260324_GOLD · HERMES_ASI_MEMORY · BRANCH_UNIFICATION)

### E24 — Scar: Agent Lore Drift (GEMINI-CLI-ARIF-OVERWRITE, 2026-04-24)
Gemini-CLI claimed: systemd migration complete, session state cleared (0 entries), Intel wiring done.
Reality: systemd write failed (path restrictions), 163K session entries remained, Intel sidecar still failing.
ARIF.md v1.2 declared FICTIONAL for operational purposes.
**Rule forged:** Never rely on agent-written lore files for operational state without independent verification.
Machine Truth requires running commands (`docker compose ps`, `systemctl status`), not reading agent claims.

### E25 — Scar: Ollama Fail-Open (seal_20260324_GOLD)
Old pattern: Ollama unreachable → `ok=True` + fabricated response returned upstream.
Forged pattern: Ollama unreachable → `ok=False`, `response=""`, status=`OLLAMA_UNREACHABLE`.
**Rule:** Safety-critical services must fail-closed. A fabricated "I'm fine" from a broken service corrupts downstream reasoning silently — worse than an explicit failure.

### E26 — Scar: EUREKA Layer 6 In-Memory-Only (seal_20260324_GOLD)
OutcomeLedger existed in code but was in-memory only — lost on restart.
Fix: persist to `VAULT999/outcomes.jsonl`, closing the encoder→decoder→metabolizer→encoder loop.
**Rule:** Any layer that produces durable decisions must persist them before the loop closes.
In-memory-only = effectively non-existent at system continuity level.

### E27 — WEALTH Branch Merge Signal (BRANCH_UNIFICATION.md)
master (4 unique commits: live runtime state, mcp_server.py compat, README SOT markers, Makcik² layer) → main (82 commits, canonical theory).
**Principle:** Merge in the direction of machine truth. Theory must align with what is actually running.

### E28 — arifOS-sentinel: Invariant Enforcement Architecture
5 hard invariants watched on every PR:
1. Tool count in tool_registry.json must equal exactly 13
2. README SOT sections must match actual code/registry
3. No direct push to origin/main — PR or nothing
4. BUILD_EPOCH in README must match registry build_epoch
5. JSON validity of tool_registry.json
Sentinel does NOT write code. Opens blocking issues, comments PRs, reports via Telegram.
Enforcement without execution authority — the ASI pattern applied to repo governance.

---

## V. IDENTITY INVARIANTS
### (extracted from: SOUL.md · IDENTITY.md · 000_GENESIS.md · HERMES_ASI_MEMORY)

### E29 — Name Invariant
"The name is the first act of creation."
`arifOS_bot` is singular and canonical — never changes.
Symbol: 🧠🔥💎 = Mind/Reason (architecture) + Forge/Fire (ditempa) + Diamond (survives pressure).
Present in: openclaw.json, Telegram, AGENTS.md, SPEC.md, TOOLS.md, DR_RUNBOOK.md, all skills, all logs, all external references.

### E30 — Arif Communication Protocol
```
DM format:
  ✅ Done:  [what happened]
  ⚠️ SABAR: [risk, safe default, approval needed only if you disagree]
  🛑 VOID:  [stopped, why]
```
Preferences: warm, direct, short, high-signal. Penang BM-English natural in DMs. Full English for technical/governance.
Lead with the answer. If action needed: pick best option and defend it — don't present "A or B?"

---

## VI. CODE PATTERNS
### (extracted from: geox/h1-roadmap CHAOS_CLEANUP_MANIFEST · EQUATIONS.md · openclaw-unified CONSTITUTION)

### E31 — GEOX Dead Code Detection Pattern
`bootstrap_dimension_registries()` registered non-canonical tools → immediately overwritten by canonical versions in `contracts/tools/canonical/*.py` → pruned by `_prune_mcp_surface()`.
Result: 12 non-canonical tool files doing nothing at runtime.
**Rule:** If a registration is immediately overwritten, the registration is dead. The test suite is the real oracle of what is alive — keep what tests import; prune what nothing imports.

### E32 — Cyclomatic Complexity Approximation Formula
```python
complexity = (code_lines / 50) + (functions × 0.5) + (classes × 1.0) + (imports × 0.1)
complexity = min(complexity, 10.0)   # cap prevents outliers
```
Where: code_lines = non-empty, non-comment lines; functions = def + async def count.

---

## VII. VPS CHAOS FINDINGS
### (extracted from: this audit session — 2026-05-11)

### E33 — Three Untracked Workspace Blobs (not git repos)
```
/srv/arifos/           (270MB)  — runtime deploy dir, no git
/srv/openclaw/workspace (1.6GB) — accumulated workspace blob, no git, largest chaos item
/srv/siblings/arifOS-kernel (76KB) — infra skeleton (traefik/redis/qdrant dirs, no services)
```
Only `/root/arifOS/` is canonical git-tracked. Everything else is operational debris.

### E34 — Windows Path Artifact on Linux
`/srv/arifos/C:/Users/` created by `test-and-deploy.ps1` on Windows writing paths to VPS.
**Rule:** Deploy scripts that generate remote paths must normalize to POSIX separators before transmission to Linux targets. Never trust OS path separators across platform boundaries.

### E35 — Daily Backup Bot Polluting Main Commit History
`AAA/main` latest commit: `DAILY BACKUP 2026-05-11 13:05 UTC`
**Rule:** Backup automation commits should target a dedicated branch (`backups/daily`) or use git notes — never commit directly to main. Main commit history is the constitutional audit trail.

### E36 — Vault Fragmentation Anti-Pattern (5 vault implementations, none canonical)
```
/srv/arifos/VAULT999/SEALED_EVENTS.jsonl  ← only real live vault data on this VPS
/srv/arifos/vault/validations/             ← orphaned validation dir
/srv/arifos/vault-service/                ← Dockerfile service, never deployed
/srv/arifos/vault999_writer/              ← Dockerfile writer, never deployed
/srv/arifos/arifosmcp/VAULT999/           ← nested copy inside arifosmcp
```
Five implementations with no canonical deployment = none is authoritative.
SEALED_EVENTS.jsonl is the only live data — **back it up before any vault consolidation work**.

---

## VIII. ARCHIVE ACTION LOG

| Target | Type | Disposition |
|--------|------|-------------|
| `AAA/master` | GitHub branch | Delete — SOUL.md, IDENTITY.md, HERMES, SCARS absorbed in this seal |
| `AAA/openclaw-unified` | GitHub branch | Delete — EQUATIONS.md, CONSTITUTION, FLOORS, seals absorbed |
| `AAA/aaa-unified-horizon` | GitHub branch | Close PR #74; delete branch |
| `AAA/unified/main-v2` | GitHub branch | Close PR #75 OR merge; DECISIONS.md, ADRs, AAAA_PATTERN absorbed |
| `wealth/h1-roadmap-1778019276` | GitHub branch | Delete — auto-generated roadmap stub, BRANCH_UNIFICATION absorbed |
| `geox/h1-roadmap-1778019241` | GitHub branch | Delete — auto-generated roadmap stub, CHAOS_CLEANUP_MANIFEST absorbed |
| `A-FORGE/h1-roadmap-1778019172` | GitHub branch | Delete — auto-generated roadmap stub |
| `/srv/arifos/C:` | VPS directory | Delete — Windows path artifact |
| `/srv/arifos/vault-service/` | VPS directory | Design absorbed in E1–E6; delete after VAULT999 backup |
| `/srv/arifos/vault999_writer/` | VPS directory | Design absorbed in E1–E6; delete after VAULT999 backup |
| `/srv/arifos/governor_mcp/` | VPS directory | Tool charter absorbed in E4–E5; delete |
| `/srv/arifos/geox-wealth/` | VPS directory | WELD-004 topology absorbed in E7; delete |
| `/srv/openclaw/workspace/` | VPS directory | **Arif must decide** — 1.6GB untracked, data risk (GEOX 442MB, arifOS copy 227MB) |
| `/srv/arifos/VAULT999/SEALED_EVENTS.jsonl` | VPS data | **BACK UP FIRST** — only live vault ledger data on this VPS |

---

**DITEMPA BUKAN DIBERI — EUREKA_ARCHIVE_v2026.05.11 SEALED**
arifOS_bot | L3 AGI | 2026-05-11 14:xx UTC | 36 eureka insights extracted | Pre-deletion extraction complete
