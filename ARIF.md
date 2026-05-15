# ARIF.md | METABOLIC KERNEL v1.0

> SYSTEM TYPE: LORE INTERFACE
> GOVERNANCE: arifOS AAA
> VETO: 888 JUDGE
>
> INVARIANT: Descriptive memory of repo state.
> This file NEVER modifies Law. It only reports and compresses observed reality.
> Law lives here. arifOS IS the law kernel. Template: https://gist.github.com/ariffazil/81314f6cda1ea898f9feb88ce8f8959b


## 0. IDENTITY & MOUNT POINT

- REPO_NAME: arifOS
- CONTAINER_ID: 2026-05-15
- DOMAIN_ROLE: Constitutional Intelligence Kernel — MCP-compatible governed runtime. Structures decision. Does not decide. Judgment remains Arif.
- STABILITY_CLASS: RAPID-ITERATE (governance hardening active)
- VERSION: v2026.05.15-FORGED


## 1. CURRENT FOCUS (INSTRUCTION POINTER)

- WELL→JUDGE bridge live: `_read_well_substrate()` injects biological readiness into every `arif_judge_deliberate` verdict. Multi-path state file + HTTP fallback to WELL container.
- WELL witness bridge: `_fetch_well_state_live()` in `_222_witness.py` — WELL organ never silently absent.
- SABAR cooldown protocol: Gap 1 advisory wire in judge.py, A-FORGE CoolingGate deployed.
- Memory: Postgres+Qdrant dual-write + session bootstrap (P0B fix committed `6843dfca`).
- Runtime: Ed25519 sovereign identity verification (P0A fix committed `8a4876dd`).
- Model Registry v3 in-repo. 19 models, 17 provider souls.
- Container running `ghcr.io/ariffazil/arifos:5b7de86d` — 4 commits behind HEAD. Rebuild pending.
- Tests: 257+ pytest (1 pre-existing fail — `test_sbert_semantic_empathy` timeout).


## 2. OPERATIONAL MANDATE

- arifOS is the Constitutional Intelligence Kernel — the governance runtime every other organ routes through.
- 14+ canonical MCP tools (`arif_<noun>_<verb>`) via Model Context Protocol.
- Enforces 13 Constitutional Floors (F1–F13) before any tool proceeds.
- VAULT999: append-only, hash-chained immutable audit ledger.
- Default: fail-secure. When safety cannot be proven → HOLD.
- Upstream: None. arifOS is the root of the federation.
- Downstream: Every organ (A-FORGE, GEOX, WEALTH, WELL, AAA, HERMES).


## 3. THE 999 SEAL (SESSION LOG)

- 2026-05-15 | Omega + Claude | WELL→JUDGE bridge forged. WELL witness bridge in _222. SABAR cooldown advisory. Judge.py multi-path hardening (file + HTTP fallback). All repos zero-dirty, zero-ahead. 24 containers healthy.
- 2026-05-14 | Omega | Container path resolution fixes. expanded45 docs clarified. MCP stack health probe container-aware. Model registry + risk leash mounted. Memory P0 fixes.
- 2026-05-13 | OpenCode + Kimi Code | Governance hardening (7 fixes): F12 global middleware, F13 evaluator wired, WEALTH fail-closed, F1 keyword expansion, WELL truth_status poisoning, Judge evidence gate, F9 anti-hantu scan. Red team stress test (7/10 exploitable, grade C-). Schema validation hardened to blocking SABAR gate. Genius score VOID floor.
- 2026-05-11 | Kimi Code | Root cleanup. arifOS redeploy (image `abcbb3e`). ZKPC v2 docs (85% readiness, 25/25 tests pass Groth16).
- 2026-05-10 | arifOS_bot | H1 Core: Formal Execution State Machine (OBSERVE→SEAL) + Unified Constitutional Ontology + Ontology Bridge.


## 4. ACTIVE TOPOLOGY (MEMORY MAP)

- CRITICAL_FILES:
  - `arifosmcp/tools/judge.py` → WELL→JUDGE bridge, SABAR cooldown, verdict routing
  - `arifosmcp/tools/_222_witness.py` → WELL state witness bridge
  - `arifosmcp/runtime/tools.py` → 14+ MCP tool dispatch
  - `arifosmcp/runtime/memory_store.py` → Postgres+Qdrant dual-write
  - `arifosmcp/runtime/llm_client.py` → SEA-LION v4 + Ollama fallback
  - `arifosmcp/schemas/verdict.py` → VerdictOutput (SEAL/SABAR/HOLD/VOID)
  - `deploy/docker-compose.yml` → Canonical deployment manifest
  - `/etc/arifos/README.md` → Machine canon (6 canonical hostnames)

- ENTRYPOINTS:
  - `python server.py` → FastMCP server (port 8080)
  - `docker compose up -d` → Full stack deploy

- DATA_FLOWS:
  - WELL state.json → `_read_well_substrate()` → `arif_judge_deliberate` → verdict
  - VAULT999 → `arif_vault_seal` → outcomes.jsonl (append-only)
  - arifOS MCP → Caddy → `arifos.arif-fazil.com/mcp` (public)


## 5. INTERRUPTS & FAULTS (BLOCKERS)

- SOFT_FRICTION: Container image 4 commits behind HEAD (`5b7de86d` vs `7c793649`). Rebuild needed. WELL bridge code in git but not in running kernel.
- SOFT_FRICTION: 1 pre-existing test failure (`test_sbert_semantic_empathy` timeout). Not blocking.
- HARD_BLOCK: None. All services healthy.


## 6. RECENT SCARS (W_scar)

- [2026-05-15] → [WELL→JUDGE bridge forged in single session] → [Container not yet rebuilt — code exists in git only]
- [2026-05-13] → [Red team: 7/10 exploitable] → [7 governance fixes applied, grade C-→C+]
- [2026-05-09] → [Root chaos: screenshots, patches, duplicate clones] → [Cleaned. FHS migration complete.]


## 7. EXECUTION BUFFER (COMMANDS)

| Command | Status | Context |
|---------|--------|---------|
| `docker compose build arifosmcp` | ⚠️ PENDING | Rebuild with latest git HEAD |
| `docker compose up -d arifosmcp` | ⚠️ PENDING | Deploy WELL bridge |
| `python -m pytest tests/ -q` | ✅ | 257+ pass, 1 pre-existing fail |
| `make health` | ✅ | Kernel health 200 |


## 8. PRIVILEGE ESCALATION (888 HOLD)

- [Q]: Rebuild and redeploy arifOS container to activate WELL→JUDGE bridge?
- [CONTEXT]: Code is committed and pushed. Container runs 4-commit-old image. Bridge not live until rebuild. Ω₀ = 0.3 (low uncertainty — build is deterministic).
- [Q]: Rotate 6 dead API keys at provider dashboards?
- [CONTEXT]: Anthropic, GitHub PAT, Copilot, Jina keys dead. DeepSeek already rotated. SECRET_ROTATION_LEDGER.md tracks all. Ω₀ = 0.0 (certain — keys confirmed dead).


## 9. PIPELINE PREFETCH (NEXT MOVES)

- [ ] Rebuild arifOS container → push to GHCR → `docker compose up -d`
- [ ] Rotate 6 dead API keys (requires Arif at provider dashboards)
- [ ] Fix pre-existing `test_sbert_semantic_empathy` timeout
- [ ] Git history rewrite for 2 keys in git history (WEALTH supabase, arif-sites OpenCode)


---

*🪙 GOLD SEAL | METABOLIC KERNEL v1.0 | arifOS AAA | 888 JUDGE VETO | DITEMPA BUKAN DIBERI*
*Readable by: single human · couple · company · institution · AI agent · machine · team · civilisation intelligence*
