# MCP Blueprint Audit — Critique of Claude Analysis vs Live arifOS/A-FORGE Reality (2026-06-23)

**Author role:** Grok (Constitutional Clerk / Forge / acting under 888 context for analysis + reversible execution). Arif = F13 SOVEREIGN + 888 Judge.

**Source:** Claude apps audit (repeated in prompt) + live MCP spec fetch (SEP-986 Final, 2025-11-25 Tools spec, annotations, listChanged, outputSchema, _meta, sampling deprecation SEP-2577, taskSupport, transports, auth tutorial) + full codebase exploration (arifOS/arifosmcp/, A-FORGE/src/, connected aforge MCP, constitutional_map.py, runtime/tools.py, contracts/, etc.) + AGENTS.md federation doctrine.

**User directive:** Agree all except OAuth for my MCP. "password or whatnot we do" (localhost-is-password, no OAuth 2.1 on arifOS kernel). Execute autonomously with tools + reality.

---

## 1. Live MCP Spec Grounding (confirmed)

- **SEP-986 (Final):** Tool names 1–64 SHOULD (some pages 128), case-sensitive, [A-Za-z0-9_-. /]. Dots and / legal at protocol. SEP notes hierarchical namespacing ok. But: downstream LLM function-call bridges (OpenAI/Anthropic etc.) typically restrict to `^[a-zA-Z0-9_-]{1,64}$`. Intersection rule + <=64 is durable wisdom (Claude PART B #1 correct).
- **Tools spec (2025-11-25):** 
  - `listChanged` capability + `notifications/tools/list_changed` for dynamic surfaces. Stage-gating structurally possible.
  - `annotations`: readOnlyHint, destructiveHint, idempotentHint, openWorldHint (hints only). "Clients MUST consider tool annotations to be untrusted unless they come from trusted servers." (Claude #8 exact).
  - `outputSchema`: servers MUST conform structured results; clients SHOULD validate. Perfect for verdict contract (SEAL/SABAR/VOID... as typed product, not isError).
  - `execution.taskSupport`: forbidden/optional/required. Long jobs belong in Tasks.
  - Tool discovery is description + inputSchema driven (model-controlled). Name tokens secondary (Claude A correct).
  - isError: for execution errors (actionable retry by model). Verdicts/refusals should be success results (isError:false) to prevent "retry to farm SEAL".
- **Sampling:** Deprecated SEP-2577 (Roots/Sampling/Logging). Direct LLM API instead. arif_mind_reason path is debt.
- **Auth/Transport:** Streamable HTTP for networked (OAuth 2.1 recommended in tutorials for public). stdio for local co-located FS actuator. Local stdio: env/other, no mandatory OAuth. Origin validation, localhost bind still valid patterns.
- **_meta:** Standard extension point for protocol + app metadata (tool_id stable key, arifos.* constitutional address). Never key vault to transient wire name (multi-host prefixing real, e.g. aforge__...).

Claude's "spec vs field" is accurate.

---

## 2. Current arifOS MCP State (Reality, not assumed)

**Naming (C1):** 
- Already largely the recommended form. CANONICAL_TOOLS (constitutional_map.py): "arif_judge", "arif_seal", "arif_forge", "arif_critique", "arif_init", "arif_observe", "arif_think", "arif_measure", "arif_memory_recall" (with deprecated_aliases), etc.
- Explicit `modes` arrays per tool + "mode" param in impls for orthogonality (e.g. arif_judge mode=judge|validate|hold|...).
- 2-term underscore + mode. Dotted forms live only in docs/metadata. 
- Legacy: arif_judge_deliberate in adapters, tests, A-FORGE proxy, some resources. Alias pattern already exists ("arif_memory_recall" deprecated).
- Matches "arif_<axis>" law exactly. The "dot wins" debate was already resolved in favor of underscore in the live kernel.

**Stage / pipeline (INV-5, C4, listChanged):**
- ToolStage enum + metabolic map (000 INIT → 111 OBSERVE ... 888 JUDGE → 999 SEAL) wired in constitutional_map.
- Some listChanged: True declared in resources/resources_index.py capabilities.
- Stage awareness in geometry/mind_geometry.py (next_tool = arif_judge etc).
- **Gap:** Dynamic `tools/list` filtering + notifications/list_changed not yet structurally hiding `arif_seal` pre-SEAL in-session. Prompt/embodied still does a lot. listChanged declared but surface mostly static.

**cc_id / constitutional chain (INV-4, C4 core):**
- `constitutional_chain_id` param documented in arif_judge / arif_seal / arif_forge descriptions.
- Contracts (contracts/, msap/, A-FORGE mcp/core.ts) use it.
- A-FORGE: refuses self-judge ("route to arifOS arif_judge_deliberate"); uses hold_id / peer_contract in pipeline.
- Leases + Amanah locks + vault receipts provide chain-of-custody.
- **Gap:** No hard "all forge_* mutations return VOID without valid judge-signed cc_id" gate yet (flag-guarded enforcement missing in places). Proxy is soft. "Physics not prompts" is aspirational here.

**Annotations + affordance (C2, INV-6):**
- A-FORGE: partial (some registerTool have `annotations: { title: "...", destructiveHint: true }`).
- arifOS: rich embodied manifests (ToolManifest: risk_tier, reversibility, blast_radius, floors, cognitive_axis) + ARIFOS_TOOL_CHARTERS. Not yet mapped 1:1 to MCP `annotations` (readOnly/destructive/idempotent/openWorld) + `_meta.arifos.*` on wire.
- Good foundation, incomplete wire surface.

**Verdict contract + outputSchema (C3, INV-3):**
- Strong: GovernanceStatus (APPROVED/SEAL, VOID, HOLD, SABAR/PAUSE, PARTIAL), VerdictDetail model, apex_envelope, contracts/verdicts.py.
- Descriptions promise "verdict ∈ {SEAL, SABAR, VOID, PARTIAL, HOLD_888}".
- **Gap:** No explicit `outputSchema` on the MCP tool defs for judge/seal. Results often text/JSON envelope, not schema-enforced structuredContent. VOID treated correctly as non-error in many paths (isError:false semantics in places), but not universal contract.

**Transport & separation (C4):**
- arifOS (kernel): streamable-http primary (8088/mcp), patched for spec GET/POST, stateful session notes. Origin validation middleware. No OAuth (see below).
- A-FORGE (hands): stdio + http, co-located FS mutation, job/pipeline/lease/task support. Stateless+idempotent posture for many tools. Proxies judge to arifOS.
- Matches blueprint. "Live coded transport" observation in Claude is echoed in arifOS server.py comments (2026-06-23 patch notes).
- Tasks: A-FORGE has forge_job_submit/status, pipeline; partial taskSupport alignment.

**Other PART B wisdom match:**
- Manifest tax: ~13 canonical + diagnostics + A-FORGE 31 (registry) vs claims of 77. Context pressure real; mode collapse on core 13+ is context win.
- Double-prefixing: observed (aforge__*, wealth__* via host).
- VAULT999 keys on stable ids/receipts in practice (not wire names).
- Sampling in arif_mind_reason (runtime/mind_reason.py paths) — deprecated.
- Annotations untrusted: doctrine already "kernel enforces, annotations advertise".
- VOID != error: conceptual yes (refusal is product); wire enforcement spotty.

**Tool count / surface:**
- arifOS: 13 canonical + DIAGNOSTIC (arif_*), some organ bridge optional.
- A-FORGE MCP (live via tool): 31 listed (arif_* bridges + forge_*). Leaks present: request_amanah_lock / release_amanah_lock, forge_pipeline, forge_research (as flagged).

**Auth reality (user exception):**
- No OAuth anywhere on arifOS MCP. Per AGENTS.md + doctrine: "Localhost IS the password." Bind 127.0.0.1 internals, Cloudflare Tunnel + Caddy for public MCPs, UFW, origin validation. F13 sovereign + cc chain + leases + 888 judgment is the authz model.
- Claude assumed "OAuth 2.1 / client-credentials" for kernel stateful service. **Explicitly rejected per Arif.** Do not add. Passwords/local/trust or tunnel only. (Matches "we do" in query.)

---

## 3. Critique of Claude Analysis ("not so full reality context")

**Accurate / High value:**
- Naming is low-stakes vs load-bearing (cc gate, stage gate via listChanged, verdict-as-schema, annotations as hints). Correct priority.
- Mode enum > separator for orthogonality. arif_judge + mode wins (and is what we have).
- Multi-host prefixing + wire vs stable id (INV-2).
- Context tax + mode-overload silent failure rule.
- VOID as successful structured result (isError:false).
- outputSchema makes contract.
- listChanged for structural 000→999 enforcement (big unlock).
- Annotations client-untrusted.
- Sampling deprecation.
- Transport = kernel (stateful http) vs hands (stdio local) split. "The last row is the whole game."
- Execution sequence reversible-first + 888 HOLD on Phase 5 (live rename) correct.
- Leaks flagged: request_amanah_lock, forge_pipeline/forge_research naming.

**Incomplete / Off vs codebase (Claude didn't see full live tree + MCP live calls):**
- arifOS naming: already arif_* underscore 2-term + mode. Not "target 2-term dot". Dotted only in meta/docs. The "inversion" win is already mostly landed.
- constitutional_chain_id / cc_id: already in CANONICAL_TOOLS descriptions, contracts, some A-FORGE schemas, msap, leases. Not invented from zero; enforcement is the missing piece.
- Affordance/embodied: rich internal (reversibility, floors, blast, risk) — just needs mapping to MCP annotations + _meta, not new primitive.
- Stage machine: ToolStage + transitions + next_tool logic already in constitutional_map + geometry. listChanged declared in places. Dynamic surface gating is the gap, not absence of concept.
- A-FORGE already refuses self-authorize, proxies judge, has some destructiveHint annotations, uses chain_id in paths, has pipeline/lease for long jobs.
- "Collapse 22+ → 13": already happened (constitutional_map: "SOLE SOURCE OF TRUTH for the 13 canonical").
- Transport observation correct, but "live coded" patches already in server.py (stateless http, GET 405, origin).
- arif_mind_reason / sampling: exists, matches the debt flag.
- Overall "document optimizes paint": true for the prior doc Claude critiqued, but current kernel is already past much of the paint into the walls (names + stages + cc params + verdicts + separation). The audit is valuable for the remaining wiring (INV-1..6 enforcement).

**Claude strengths:** Excellent field truths + spec grounding. Blueprint (C1-4, phases, invariants) is solid and directly actionable.

**Claude weaknesses (from full context):** Assumed less existing machinery than is present; overstated OAuth as necessary for kernel (user veto); some tool names in A-FORGE surface were current (31 in live registry) vs assumed 77.

---

## 4. Adopted Blueprint Adjustments (per Arif + reality)

**C1 Naming law (final, adapted):**
- Kernel (arifOS): `arif_<axis>` (already) underscore, <=64, [a-zA-Z0-9_-]. `_meta.arifos.axis = "arif.judge"`, stage, lane. Dispatch via `mode` enum. Keep 3-term/ _deliberate as deprecated aliases (spec-blessed).
- Hands (A-FORGE): `forge_<domain>_<action>` preferred. Kill leaks: `request_amanah_lock` → alias `forge_lock_acquire` (or primary migrate), `release_amanah_lock` → `forge_lock_release`; `forge_pipeline` → keep + alias or `forge_pipeline_run`; `forge_research` → `forge_research_query`. Verb-first 2-term bugs addressed via registration shim.
- INV-1: enforce on wire registration.

**C2 affordance → wire:**
- Map embodied (reversibility, irreversible flag, readOnly from stage, openWorld from external tools) → annotations + _meta.arifos.{action_class, floors, requires_cc_id, autonomy_safe}.
- Pure additive on registration.

**C3 Verdict contract:**
- Every governance tool (arif_judge, arif_seal, key forge mutators) declare outputSchema.
- `{ verdict: "SEAL"|"SABAR"|"VOID"|"PARTIAL"|"HOLD_888", floors_evaluated: [...], reason, cc_id: string|null, constitution_hash, ... }`
- isError: false for all (VOID is successful judgment).
- Servers enforce; clients can validate.

**C4 Kernel vs hands (real separation, already close):**
- arifOS: streamable-http, stateful, issues cc_id on SEAL, stage-gated surface.
- A-FORGE: stdio primary for mutation, refuses without valid cc_id (harden), task support, flat catalog + lease scope.
- INV-4: gate mutations.

**Phases (reversible-first):**
- 0-4,6: do now (additive, aliases, flag guards).
- 5: rename/hide old from tools/list → 888 HOLD only. Do not execute.

**Invariants (enforce progressively):**
- INV-1 to INV-6 as listed in prompt.

**OAuth exception:** Explicit. arifOS MCP does **not** use OAuth 2.1. Current model stands (localhost bind + tunnel + origin + F13 + 888 + cc chain + leases). Update any docs claiming otherwise.

---

## 5. Execution Status (this run)

See todo tracker + subsequent commits/edits. Changes are additive or alias-based where possible. All non-Phase-5.

Tests / MCP smoke / health / git status will be used to verify.

**888 HOLD** declared on live surface rename (Phase 5).

DITEMPA BUKAN DIBERI.

---

*Receipt candidate for VAULT999 on significant wiring changes.*
