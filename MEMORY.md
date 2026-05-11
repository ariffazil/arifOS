# MEMORY.md — OPENCLAW Selective Persistence

**Version:** 2026.05.01-KANON
**Last updated:** 2026-05-01 03:55 UTC
**Status:** SEALED

---

## Sealed Facts

### OC-001 — OPENCLAW Runtime Governance Upgrade — SEALED 2026-05-01

**Git commit:** cce9843b

All gap files created and synced to git. OPENCLAW governance is now 000-999 bounded.

| File | Status | Purpose |
|------|--------|---------|
| AGENTS.md | ✅ Updated | ReAct loop → 000-999 governed loop |
| AUTONOMY.md | ✅ Created | L0-L5 permission ladder |
| CHECKPOINT.md | ✅ Created | Session continuity + recovery |
| HEARTBEAT.md | ✅ Rewritten | Live runtime protocol |
| LOOP.md | ✅ Created | 000-999 operational implementation |
| DECISIONS.md | ✅ Created | Sealed decision log |
| TASKS.md | ✅ Created | Active work ledger |
| TOOLS.md | ✅ Populated | Local environment notes |
| RECOVERY.md | ✅ Created | Failure recovery runbook |
| FLOORS.md | ✅ Created | F1-F13 standalone reference |
| SOUL.md | ✅ Updated | Version header added |
| AGENT_STATE.md | ✅ Created | Agent identity and intelligence state |

**Archived (stale):** CLAUDE.md, GEMINI.md, ARIF.md — prepended archive notice.

**Workspace cleaned:** Removed AAA_README.md, tommy_thomas_dossier.md, ARIF-TEMPLATE.md (not governance content).

**Maturity:** 32/75 → ~43/75 (governance-correct, not yet operationally-live).

---

### WEALTH MCP Exposed — 2026-05-01

**Bug fixed:** wealth-organ ran with `transport="sse"` which only exposes GET/POST at non-standard paths. Fixed by changing to `transport="http"` in monolith.py line 4115.

WEALTH MCP live at `https://wealth.arif-fazil.com/mcp` (HTTP transport, session-based).

Added `wealth.arif-fazil.com` → `wealth-organ:8082` route to Caddyfile.

---

### arifOS MCP v0.2 REAL BACKEND — Deployed 2026-04-26

6 governance backend files wired into `server.py`: vault_chain.py, session_state.py, interceptor.py, forge_app.py, judge_app.py, vault_audit.py.

---

### arif-fazil.com .well-known Files — Cloudflare Cache Issue

API token lacks "Cache Purge" permission — manual purge required via Cloudflare Dashboard.

---

## Archived Logs

*Older entries in memory/*.md*

## OpenCode MCP Wiring — 2026-05-11

OpenCode local config now distinguishes between the canonical constitutional kernel and the unified intelligence surface.

- `.opencode.json`:
  - `arifOS-Kernel` → `.venv/bin/python -m arifosmcp.runtime stdio`
  - `arifOS-Intelligence` → `.venv/bin/python -m arifosmcp.opencode_mcp intelligence`
  - `arifOS-Public` → `https://mcp.arif-fazil.com/mcp` (disabled by default)
- `docs/reference/spec/opencode.json` updated to match the same split.
- `docs/reference/spec/opencode-mcp-wiring.md` added as the direct operator note.

Decision: use `stdio` as the trusted local OpenCode transport, and keep `https` as the federation/public transport.

Extension: added `arifOS-Sovereign` as the default OpenCode bundle plus dedicated `arifOS-WELL`, `arifOS-WEALTH`, and `arifOS-GEOX` local surfaces. Intelligence now routes through a dedicated OpenCode launcher with G02 mounted.

Observatory upgrade: federation probe now exposes runtime evidence fields (`probe_method`, `probe_endpoint`, `error`), the Apex dashboard updates organ/site dots from live probe state, and contradicted legacy dossier notes are moved out of `Known Gaps` into `Historical Notes`.


## Charter Naming Unification — 2026-05-11

Active authored declaration files now use `charter` as the canonical singular term.

- `federation_manifest.json` -> `federation.charter.json`
- `arifosmcp/sites/apex-dashboard/federation-manifest.json` -> `federation.charter.json`
- `deploy/stack.manifest.json` -> `deploy/stack.charter.json`
- `config/manifest/canonical_manifest.yaml` -> `config/charter/kernel.charter.yaml`
- `docs/reference/spec/mcp-manifest.json` -> `docs/reference/spec/mcp.charter.json`
- `docs/reference/spec/arif_manifest.yaml` -> `docs/reference/spec/arif.charter.yaml`
- `CONFIG/SovereigntyManifest.json` -> `CONFIG/sovereignty.charter.json`
- `docs/SovereigntyManifest.json` -> `docs/sovereignty.charter.json`
- `arifosmcp/tool_manifest.py` -> `arifosmcp/tool_charter.py`
- `arifosmcp/tools/manifests/tool_manifest.json` -> `arifosmcp/tools/charters/tool.charter.json`

Naming canon: use `charter` for authored declarative truth. Keep `server.json`, `registry.json`, `agent.json`, and similar protocol terms unchanged because they are semantically distinct surfaces, not naming drift.

Completion pass: renamed safe internal identifiers such as `tool_manifest` -> `tool_charter`, added `CHARTERS.md`, and added `docs/deployment/VPS_CHARTER_MIGRATION.md`. Remaining active `manifest` references are limited to migration search strings, historical memory, protocol/schema phrases, or intentionally stable external API contracts like forge manifests.

## 777_WITNESS — LLM Output Envelope (committed 2026-05-06)

**Commits:** d83d0f1b (envelope + 3 tools), e90b0256 (judge/vault wired)

**Eureka:** "LLM output is entropy-shaped testimony — not truth, not command, not verdict."

**Full constitutional membrane (complete):**
  LLM → wrap_llm_output() → LLMOutputEnvelope (SHA-256 tamper evidence)
    → 333_MIND / 444r_REPLY / 666_HEART tool logic
    → evidence_receipt (mind_envelope + heart_envelope attached)
    → 888_JUDGE: _777_invariants records LLM output hashes
    → invariants_checked (F01–F13 + 777_witness_mind/heart hash prefixes)
    → 999_VAULT: _777_witness block in payload (mind_raw_hash, heart_raw_hash,
      mind_evidence_level, heart_evidence_level, human_decision_required)
    → Human 888 final decision

**What was built:**

d83d0f1b — envelope creation + 3 tools wired:
- llm_output_envelope.py: Canonical Pydantic envelope (LLMOutputEnvelope)
  Fields: provider, model, tool_origin, mode, raw_output, raw_output_hash (SHA-256),
  parsed_output, schema_valid, confidence_claimed, evidence_level (F2: claimed/cited/
  verified), uncertainty[] (F7 Humility), risk_flags[] (F6/F9/F13), prompt_hash,
  timestamp, human_decision_required (always True), authority_level (always
  instrument_only per F13), wrapper_version. Factories: wrap_llm_output(),
  wrap_llm_error(). Helpers: envelope_to_judge_summary(), envelope_to_memory_storable().

- witness_packet.py: Bugfixed parallel envelope (html.normalize_idna → re.sub;
  F12 injection scanner fixed; model ID pragma allowlist added).

- llm_client.py: call_llm() now returns LLMOutputEnvelope automatically.
  wrap_llm_output() wraps every response. call_llm_raw() deprecated.

- mind_reason.py (333_MIND): async, envelope-wrapped.
- reply_compose.py (444r_REPLY): async, envelope-wrapped.
- tools/heart.py (666_HEART): async, envelope-wrapped.

e90b0256 — judge and vault integration:
- tools.py _arif_judge_deliberate_tool: auto-chain extracts _envelope from
  mind_reason + heart_critique outputs, attaches to evidence_receipt as
  mind_envelope + heart_envelope, _777_invariants records SHA-256 hashes.
- tools.py _arif_judge_deliberate (sync): reads _777_invariants from
  evidence_receipt, appends to top-level invariants_checked.
- tools.py _arif_vault_seal_tool (auto-seal): vault payload now includes
  _777_witness block with mind_raw_hash, heart_raw_hash, evidence_levels.
- 555_MEMORY auto-chain store: structured content dict with _envelope_hash
  and _evidence_level (not raw LLM output), tags include 777_WITNESS.
- B104 nosec on SSRF validation (false positive), B007 fixed, F401 cleaned.

**Evidence level (F2 Truth):**
- claimed: LLM self-reported, no citation
- cited: LLM cited external evidence
- verified: arifOS F-WEB deterministic gate passed

**Authority level (F13 Sovereign):**
- All LLM output: always "instrument_only" — never sovereign, never command

**Correct placement by floor:**
  333_MIND  ✅ Reasoning witness (envelope at LLM output)
  444r_REPLY ✅ Language shaping (envelope at LLM output)
  666_HEART  ✅ Risk witness (envelope at LLM output)
  555_MEMORY ⚠️ Only after envelope (stores envelope hash, not raw output)
  888_JUDGE  ✅ Reads envelope hashes via _777_invariants
  999_VAULT  ⚠️ Anchors envelope SHA-256 in payload (post-hoc verifiable)
  010_FORGE  ❌ Never directly — always through 888_HOLD

**GitHub push:** d83d0f1b → e90b0256 → main

## 777_WITNESS — Constitutional Epistemology (2026-05-06)

### The shift: "AI tool orchestration" → constitutional epistemology

arifOS no longer treats LLM output as function results.
Every LLM output is **witness testimony** — it must answer:
- **What** did it claim? (parsed_output)
- **Under what prompt**? (prompt_hash)
- **With what uncertainty**? (uncertainty[])
- **Under what model identity**? (model + governance_card authority)
- **At what cost**? (latency_ms)
- **With what risk**? (risk_flags[] + injection_detected)

This turns arifOS from "MCP with AI tools" into a constitutional epistemology system.

### Canonical structures

**LLMOutputEnvelope** (Pydantic, arifosmcp/runtime/llm_output_envelope.py):
The WitnessPacket. 19 fields: provider, model, tool_origin, mode, raw_output,
raw_output_hash, parsed_output, schema_valid, confidence_claimed, evidence_level,
uncertainty[], risk_flags[], injection_detected, latency_ms, prompt_hash,
timestamp, human_decision_required, authority_level, wrapper_version.

**call_llm()** → always returns LLMOutputEnvelope. Never raw JSON.

**witness_packet.py** (dataclass WitnessPacket) — parallel implementation.
Two implementations of the same concept. Current: LLMOutputEnvelope is canonical.

**model_governance.yaml** (arifosmcp/core/):
F11 Model Governance SoT. SEA-LION, Ollama, Deterministic cards.
get_governance_card(model) → authority, allowed_tools, forbidden_roles.

**model_governance.py**: YAML loader with lazy cache, case-insensitive lookup,
unknown-model safe default (instrument_only + all forbidden roles).

### Quarantine pipeline
LLM output → _scan_injection() → schema validation → _assess_uncertainty_and_risk()
→ envelope → human_decision_required gate → release or HOLD.

### Eureka moments addressed
- Eureka 1-6: All implemented in envelope + call_llm + model_governance
- Eureka 2: WitnessPacket = LLMOutputEnvelope (atomic unit ✅)
- Eureka 3: Generate → Interpret → Judge separated (333_MIND → 888_JUDGE)
- Eureka 4: model_governance.yaml + get_governance_card() ✅
- Eureka 5: _scan_injection() gates every LLM output ✅
- Eureka 6: Two outputs (human answer + governance envelope) ✅

## Partial SEAL Close-out (2026-05-06 21:00 UTC)

Arif's verdict: "Partial SEAL — architecturally approved as a reversible blueprint.
Execution should wait until F11 model governance card binding is fixed."

**Status**: F11 binding is LIVE.
- get_governance_card("SEA-LION-MODEL-ID") → instrument_only  # pragma: allowlist secret
- _governance_of(model) in envelope.py → reads from model_governance.yaml ✅
- Unknown models: conservative default (instrument_only + all forbidden) ✅
- 15-pattern F12 injection scan: active on every LLM output ✅
- latency_ms tracking: active at Tier 1 (SEA-LION) and Tier 2 (Ollama) ✅

No AI output enters memory, judge, vault, forge, gateway, or user reply
unless wrapped, hashed, schema-validated, risk-scanned, and authority-bounded.

Partial SEAL → **FULL SEAL** pending deployment verification.

## Checkpoint - 2026-05-11T18:12:23Z
- session_id: OC-006
- stage: 999_SEAL
- task: Hermes gateway restart-loop diagnosis and stabilization
- last_action: Fixed aaa-governance F13 substring bug (`rm` falsely matching `terminal`), rebuilt corrupted `/root/AAA/.hermes/state.db`, removed duplicate root user gateway unit file, verified system service healthy.
- entropy_delta: 0.08
