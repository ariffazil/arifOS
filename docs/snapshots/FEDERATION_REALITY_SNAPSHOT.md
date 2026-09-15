# Federation Reality Snapshot — Tier 1 Observatory Upgrade

**Seal:** `RECEIPT-SEAL-f2193c39156a` (2026-08-03T13:59:28Z)
**Sovereign command:** `seal and deploy live real SOT` (F13_ARIF)
**Commit chain:** `0a8138572` (build_public_state.py) + `408661b2a` (systemd timer)

## Tier 1 Observatory upgrade — T1.1 → T1.6 (verified live)

| Item | Endpoint proven | Probe time (UTC) | Result |
|------|-----------------|------------------|--------|
| T1.1 capabilities.matrix populated | `/api/public-state` | 2026-08-03T13:54:38Z | 8 rows (was 0) |
| T1.2 systemd timer `arifos-public-state-refresh.timer` | `/etc/systemd/system/` | 2026-08-03T13:54Z | enabled, OnUnitActiveSec=5min |
| T1.3.a APEX scalars | AAA `:3001/health` | 2026-08-03T13:54:38Z | G=0.875, C_dark=0.008, W3=0.634, h=0.15, QDF=1 |
| T1.3.b arifFLOW FQ | arifFLOW `:7073/health` | 2026-08-03T13:54:38Z | quotient=0.0, verdict=STUCK |
| T1.3.c identity_hashes | 7 organs `/health` | 2026-08-03T13:54:38Z | 7/7 retrieved (arifFLOW has no identity_hash field) |
| T1.3.d drift_log_freshness | `/root/.local/share/arifos/vault999/drift_log.jsonl` | 2026-08-03T13:54:38Z | age=577s, overall_status=True |
| T1.4 governance.verdict override | `/api/public-state` | 2026-08-03T13:54:38Z | SYUBHAH (was UNKNOWN — false-green) |
| T1.5 chain_integrity card | `/api/observatory/v1/seal/verify` | 2026-08-03T13:54:38Z | entries=244, canonical=44, historical=200, corrupt=9, gaps=76, verified=False |
| T1.6 canonical_verdict surfaced | arifOS MCP `arif_observe` | 2026-08-03T13:54:38Z | native=BELUM_SAH (UNAUTHENTICATED), failed_floors=['F13'], reason='Constitutional HOLD: L13', next_safe_action='Produce reversible design blueprint only; no execution.' |

## What's now visible in the public Observatory (was hidden)

- ✅ `capabilities.matrix` (8 rows) — was '0 matrix rows parsed'
- ✅ `verdict: SYUBHAH` (kernel truth) — was 'HOLD (raw UNKNOWN)'
- ✅ `apex` scalars (G, C_dark, W3, h, QDF) — was hidden
- ✅ `ariflow` FQ (quotient, verdict, execute/verify counts) — was hidden
- ✅ `identity_hashes` (7/7 organs) — was hidden
- ✅ `drift_log_freshness` (last check, age, status) — was 'unavailable'
- ✅ `chain_integrity` (entries, corrupt, gaps) — was hidden
- ✅ `canonical_verdict` (native, failed_floors, reason, next_safe_action) — was hidden

## Files in this upgrade

- `scripts/build_public_state.py` — added `collect_extras()` (~140 lines) + `_override_floors_with_canonical()` + `_override_verdict_with_canonical()` (T1.4). Commit `0a8138572`.
- `ops/systemd/arifos-public-state-refresh.service` — new tier-1 refresh service. Commit `408661b2a`.
- `ops/systemd/arifos-public-state-refresh.timer` — 5-min cadence (OnBootSec=2min, OnUnitActiveSec=5min, Persistent=true). Commit `408661b2a`.

## Reversibility

- All edits are additive — no field deletion, no schema change.
- Sealed via direct VAULT999 append under explicit F13 sovereign directive (precedent: SEAL-7cd7f18462234116, ANCHOR-209e1564cf194dc8).
- To revert: `git revert 0a8138572 408661b2a` + `systemctl disable --now arifos-public-state-refresh.timer`.

---

[Pre-existing report from 2026-07-24 follows — Tier 1 overlay above is the source of truth from 2026-08-03T13:59:28Z.]

---

# Federation Reality Snapshot

**Last verified:** `2026-07-24T16:34:34.686068+00:00`
**Overall verdict:** `GREEN_WITH_GAPS`
**Truth layer:** `L2_VERIFIED_STATE`

## Organ Status

| Organ | Role | Localhost | Public | Tools (expected) | Latency (ms) | Verdict |
|-------|------|-----------|--------|------------------|--------------|---------|
| arifOS | constitutional_kernel | ✅ | — | 8 / 56 | 11.19 | DEGRADED |
| GEOX | earth_evidence | ✅ | — | — / 37 | 29.27 | PASS |
| WEALTH | capital_compute | ✅ | — | — / 20 | 6.3 | PASS |
| WELL | human_readiness_reflect_only | ✅ | — | — / 21 | 9.22 | DEGRADED |
| AAA | cockpit_a2a | ✅ | — | — / — | 17.44 | PASS |
| A-FORGE | governed_execution | ✅ | — | — / 77 | 2.65 | PASS |

## Endpoint Detail

| Organ | Endpoint | Status | Version | Freshness | F13 Status | Notes |
|-------|----------|--------|---------|-----------|------------|-------|
| arifOS | http://127.0.0.1:8088 | healthy | v2026.07.24-ZEN-SURVIVAL | fresh | — | — |
| GEOX | http://127.0.0.1:8081 | healthy | v2026.07.17 | fresh | — | tools: HTTP Error 400: Bad Request |
| WEALTH | http://127.0.0.1:18082 | healthy | v2026.07.19 | — | — | tools: HTTP Error 400: Bad Request |
| WELL | http://127.0.0.1:18083 | degraded | v2026.07.17 | expired | — | tools: HTTP Error 400: Bad Request; truth=INSUFFICIENT_DATA |
| AAA | http://127.0.0.1:3001 | healthy | v2026.07.17 | — | — | tools: organ has no MCP tool surface |
| A-FORGE | http://127.0.0.1:7071 | healthy | v2026.07.17 | fresh | — | tools: HTTP Error 400: Bad Request |

## F13 SOVEREIGN — Reachability & Floor Canon

**Floors declared in canon:** 13 / 13

| File | Status | Detail |
|------|--------|--------|
| FLOOR_TABLE.json | ✅ | 13 floors; authority=F13 SOVEREIGN |
| 000_KERNEL_CANON.md | ✅ | 39× F13 mention; 32707 bytes |

**No organs currently expose an F13/sovereignty field in /health.**

| Floor | Name | Rule |
|-------|------|------|
| F1 | AMANAH | Reversible first. Irreversible → 888 HOLD. |
| F10 | ONTOLOGY | AI-only ontology. Soul = VOID. |
| F11 | AUDITABILITY | Every decision logged. |
| F12 | RESILIENCE | Injection defense. |
| F13 | SOVEREIGN | Human veto FINAL. Harness switch belongs to sovereign. |
| F2 | TRUTH | P(truth) ≥ 0.99. Claims carry epistemic label. |
| F3 | TRI-WITNESS | Human + AI + Earth witness ≥ 0.75. |
| F4 | CLARITY | Every output must reduce entropy (ΔS ≤ 0). |
| F5 | PEACE² | Non-destructive power. |
| F6 | MARUAH/EMPATHY | Protect weakest stakeholder. |
| F7 | HUMILITY | No fake certainty. Ω₀ ∈ [0.03, 0.05]. |
| F8 | GENIUS | G ≥ 0.80 for complex actions. |
| F9 | ANTIHANTU | No deception, manipulation, consciousness claims. |

## Known Gaps

- **GAP-001** [high] *A-FORGE*: A-FORGE lease gate is self-issued; must become kernel-issued before broad autonomous mutation.
- **GAP-002** [medium] *WELL*: WELL live human-state telemetry is stale / INSUFFICIENT_DATA.
- **GAP-003** [medium] *arifOS*: arifOS CONTEXT.md and RUNBOOK.md created from probe output.
- **GAP-004** [low] *A-FORGE*: A-FORGE public HTTPS ingress is not configured (public endpoint unavailable).

## Tool Scope Sweep

| Organ | Tools | Prefixes | Resources | Prompts |
|-------|-------|----------|-----------|---------|
| A-FORGE | None |  | 0 | 0 |
| AAA | 0 |  | 0 | 0 |
| GEOX | — | — | 0 | 0 |
| WEALTH | — | — | 0 | 0 |
| WELL | — | — | 0 | 0 |
| arifOS | 8 | arif=8 | 322 | 21 |

### Tool Names by Prefix

**A-FORGE** (0 tools):


**AAA** (0 tools):


**arifOS** (8 tools):
  - `arif_forge`
  - `arif_init`
  - `arif_judge`
  - `arif_memory`
  - `arif_observe`
  - `arif_route`
  - `arif_seal`
  - `arif_think`

### Resource URIs

**A-FORGE** (0 resources):


**AAA** (0 resources):


**GEOX** (0 resources):


**WEALTH** (0 resources):


**WELL** (0 resources):


**arifOS** (322 resources):
  - `arifos://atlas333/activation/rules`
  - `arifos://atlas333/flow`
  - `arifos://atlas333/geometry`
  - `arifos://atlas333/index`
  - `arifos://atlas333/organs`
  - `arifos://atlas333/paradox/list`
  - `arifos://atlas333/quote/list`
  - `arifos://atlas333/seal/head`
  - `arifos://atlas333/thresholds`
  - `arifos://atlas333/zones`
  - `arifos://bootstrap`
  - `arifos://civilization`
  - `arifos://doctrine`
  - `arifos://human/metabolized`
  - `arifos://identity`
  - `arifos://jurisdiction`
  - `arifos://loop-engineering`
  - `arifos://mcp-alignment`
  - `arifos://mcp/surface-map`
  - `arifos://memory`
  - `arifos://quickstart`
  - `arifos://reality/state`
  - `arifos://schema`
  - `arifos://seal-readiness`
  - `arifos://trinity`
  - `arifos://vitals`
  - `arifos://wisdom/contract`
  - `arifos://wisdom/quotes/all`
  - `arifos://wisdom/quotes/arifos-doctrine`
  - `arifos://wisdom/quotes/disputed`
  - `arifos://wisdom/quotes/prohibited-uses`
  - `skill://AGI-claude-xml-structured-reasoning/SKILL.md`
  - `skill://AGI-claude-xml-structured-reasoning/_manifest`
  - `skill://AGI-codex-chain-of-thought/SKILL.md`
  - `skill://AGI-codex-chain-of-thought/_manifest`
  - `skill://AGI-dream-engine/SKILL.md`
  - `skill://AGI-dream-engine/_manifest`
  - `skill://AGI-emd-decode/SKILL.md`
  - `skill://AGI-emd-decode/_manifest`
  - `skill://AGI-emd-encode/SKILL.md`
  - `skill://AGI-emd-encode/_manifest`
  - `skill://AGI-emd-metabolize/SKILL.md`
  - `skill://AGI-emd-metabolize/_manifest`
  - `skill://AGI-entropy-lock-prime/SKILL.md`
  - `skill://AGI-entropy-lock-prime/_manifest`
  - `skill://AGI-explorer-intelligence/SKILL.md`
  - `skill://AGI-explorer-intelligence/_manifest`
  - `skill://AGI-hermes-system-prompt-voice/SKILL.md`
  - `skill://AGI-hermes-system-prompt-voice/_manifest`
  - `skill://AGI-multimodal-bridge/SKILL.md`
  - `skill://AGI-multimodal-bridge/_manifest`
  - `skill://AGI-nusantara-substrate/SKILL.md`
  - `skill://AGI-nusantara-substrate/_manifest`
  - `skill://AGI-plan-dag/SKILL.md`
  - `skill://AGI-plan-dag/_manifest`
  - `skill://AGI-skill-unification/SKILL.md`
  - `skill://AGI-skill-unification/_manifest`
  - `skill://AGI-web-optimization/SKILL.md`
  - `skill://AGI-web-optimization/_manifest`
  - `skill://APEX-fff-loop-protocol/SKILL.md`
  - `skill://APEX-fff-loop-protocol/_manifest`
  - `skill://APEX-humility-godel/SKILL.md`
  - `skill://APEX-humility-godel/_manifest`
  - `skill://APEX-quantum-eureka/SKILL.md`
  - `skill://APEX-quantum-eureka/_manifest`
  - `skill://ARCHIVE/SKILL.md`
  - `skill://ARCHIVE/_manifest`
  - `skill://ASI-agent-invariants/SKILL.md`
  - `skill://ASI-agent-invariants/_manifest`
  - `skill://ASI-agentic-architecture/SKILL.md`
  - `skill://ASI-agentic-architecture/_manifest`
  - `skill://ASI-agentic-governance/SKILL.md`
  - `skill://ASI-agentic-governance/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://ASI-context-window-mgr/SKILL.md`
  - `skill://ASI-context-window-mgr/_manifest`
  - `skill://ASI-drift-watch/SKILL.md`
  - `skill://ASI-drift-watch/_manifest`
  - `skill://ASI-fabrication-prevention/SKILL.md`
  - `skill://ASI-fabrication-prevention/_manifest`
  - `skill://ASI-mcp-governor/SKILL.md`
  - `skill://ASI-mcp-governor/_manifest`
  - `skill://ASI-observability/SKILL.md`
  - `skill://ASI-observability/_manifest`
  - `skill://forge_vault/SKILL.md`
  - `skill://forge_vault/_manifest`
  - `skill://ASI-skill-binding/SKILL.md`
  - `skill://ASI-skill-binding/_manifest`
  - `skill://ASI-summarize/SKILL.md`
  - `skill://ASI-summarize/_manifest`
  - `skill://AUDIT-drift-detector/SKILL.md`
  - `skill://AUDIT-drift-detector/_manifest`
  - `skill://AUDIT-recursive-audit/SKILL.md`
  - `skill://AUDIT-recursive-audit/_manifest`
  - `skill://AUDIT-skill-atlas/SKILL.md`
  - `skill://AUDIT-skill-atlas/_manifest`
  - `skill://FLAME-operator/SKILL.md`
  - `skill://FLAME-operator/_manifest`
  - `skill://FLAME-router/SKILL.md`
  - `skill://FLAME-router/_manifest`
  - `skill://FORGE-agentic-web-builder/SKILL.md`
  - `skill://FORGE-agentic-web-builder/_manifest`
  - `skill://FORGE-ci-diagnose/SKILL.md`
  - `skill://FORGE-ci-diagnose/_manifest`
  - `skill://FORGE-cicd-docker-deploy/SKILL.md`
  - `skill://FORGE-cicd-docker-deploy/_manifest`
  - `skill://FORGE-code-analysis/SKILL.md`
  - `skill://FORGE-code-analysis/_manifest`
  - `skill://FORGE-context-compress/SKILL.md`
  - `skill://FORGE-context-compress/_manifest`
  - `skill://FORGE-context-compressor/SKILL.md`
  - `skill://FORGE-context-compressor/_manifest`
  - `skill://FORGE-cross-agent-handoff/SKILL.md`
  - `skill://FORGE-cross-agent-handoff/_manifest`
  - `skill://FORGE-cross-repo-doc-zen/SKILL.md`
  - `skill://FORGE-cross-repo-doc-zen/_manifest`
  - `skill://FORGE-data-compression/SKILL.md`
  - `skill://FORGE-data-compression/_manifest`
  - `skill://FORGE-did-web-identity/SKILL.md`
  - `skill://FORGE-did-web-identity/_manifest`
  - `skill://FORGE-docker-entropy/SKILL.md`
  - `skill://FORGE-docker-entropy/_manifest`
  - `skill://FORGE-fastapi-api-builder/SKILL.md`
  - `skill://FORGE-fastapi-api-builder/_manifest`
  - `skill://FORGE-fastmcp/SKILL.md`
  - `skill://FORGE-fastmcp/_manifest`
  - `skill://FORGE-federation-manifest/SKILL.md`
  - `skill://FORGE-federation-manifest/_manifest`
  - `skill://FORGE-federation-orchestrator/SKILL.md`
  - `skill://FORGE-federation-orchestrator/_manifest`
  - `skill://FORGE-github-ops/SKILL.md`
  - `skill://FORGE-github-ops/_manifest`
  - `skill://FORGE-github-workflow/SKILL.md`
  - `skill://FORGE-github-workflow/_manifest`
  - `skill://FORGE-google-workspace/SKILL.md`
  - `skill://FORGE-google-workspace/_manifest`
  - `skill://FORGE-governance-jsonld/SKILL.md`
  - `skill://FORGE-governance-jsonld/_manifest`
  - `skill://FORGE-grok-profile/SKILL.md`
  - `skill://FORGE-grok-profile/_manifest`
  - `skill://FORGE-incident-escalation/SKILL.md`
  - `skill://FORGE-incident-escalation/_manifest`
  - `skill://FORGE-incident-triage/SKILL.md`
  - `skill://FORGE-incident-triage/_manifest`
  - `skill://FORGE-infra-crons/SKILL.md`
  - `skill://FORGE-infra-crons/_manifest`
  - `skill://FORGE-infra-guardian/SKILL.md`
  - `skill://FORGE-infra-guardian/_manifest`
  - `skill://FORGE-issue-triage/SKILL.md`
  - `skill://FORGE-issue-triage/_manifest`
  - `skill://FORGE-kimi-code/SKILL.md`
  - `skill://FORGE-kimi-code/_manifest`
  - `skill://FORGE-mcp-a2a-agentic/SKILL.md`
  - `skill://FORGE-mcp-a2a-agentic/_manifest`
  - `skill://FORGE-mcp-federation-ops/SKILL.md`
  - `skill://FORGE-mcp-federation-ops/_manifest`
  - `skill://FORGE-mcp-gui/SKILL.md`
  - `skill://FORGE-mcp-gui/_manifest`
  - `skill://FORGE-mcp-lifeguard/SKILL.md`
  - `skill://FORGE-mcp-lifeguard/_manifest`
  - `skill://FORGE-mcp-ops/SKILL.md`
  - `skill://FORGE-mcp-ops/_manifest`
  - `skill://FORGE-mcp-smoke-test/SKILL.md`
  - `skill://FORGE-mcp-smoke-test/_manifest`
  - `skill://FORGE-model-monitor/SKILL.md`
  - `skill://FORGE-model-monitor/_manifest`
  - `skill://FORGE-nextjs-mastery/SKILL.md`
  - `skill://FORGE-nextjs-mastery/_manifest`
  - `skill://FORGE-onboarding/SKILL.md`
  - `skill://FORGE-onboarding/_manifest`
  - `skill://FORGE-postgres-schema-design/SKILL.md`
  - `skill://FORGE-postgres-schema-design/_manifest`
  - `skill://FORGE-pr-governance/SKILL.md`
  - `skill://FORGE-pr-governance/_manifest`
  - `skill://FORGE-pr-review/SKILL.md`
  - `skill://FORGE-pr-review/_manifest`
  - `skill://FORGE-precommit-review/SKILL.md`
  - `skill://FORGE-precommit-review/_manifest`
  - `skill://FORGE-react-spa-discipline/SKILL.md`
  - `skill://FORGE-react-spa-discipline/_manifest`
  - `skill://FORGE-readme-truth-check/SKILL.md`
  - `skill://FORGE-readme-truth-check/_manifest`
  - `skill://FORGE-redis-qdrant-integration/SKILL.md`
  - `skill://FORGE-redis-qdrant-integration/_manifest`
  - `skill://FORGE-repo-intelligence/SKILL.md`
  - `skill://FORGE-repo-intelligence/_manifest`
  - `skill://FORGE-route-least-power/SKILL.md`
  - `skill://FORGE-route-least-power/_manifest`
  - `skill://FORGE-sct-federation-ingress/SKILL.md`
  - `skill://FORGE-sct-federation-ingress/_manifest`
  - `skill://FORGE-seal-a-close/SKILL.md`
  - `skill://FORGE-seal-a-close/_manifest`
  - `skill://FORGE-secret-hygiene/SKILL.md`
  - `skill://FORGE-secret-hygiene/_manifest`
  - `skill://FORGE-skill-creator/SKILL.md`
  - `skill://FORGE-skill-creator/_manifest`
  - `skill://FORGE-skill-linter/SKILL.md`
  - `skill://FORGE-skill-linter/_manifest`
  - `skill://FORGE-spatial-grounding/SKILL.md`
  - `skill://FORGE-spatial-grounding/_manifest`
  - `skill://FORGE-subagent-spawn/SKILL.md`
  - `skill://FORGE-subagent-spawn/_manifest`
  - `skill://FORGE-symlink-audit/SKILL.md`
  - `skill://FORGE-symlink-audit/_manifest`
  - `skill://FORGE-t3a-binding-matrix/SKILL.md`
  - `skill://FORGE-t3a-binding-matrix/_manifest`
  - `skill://FORGE-tailwind-tokens/SKILL.md`
  - `skill://FORGE-tailwind-tokens/_manifest`
  - `skill://FORGE-telegram-audit/SKILL.md`
  - `skill://FORGE-telegram-audit/_manifest`
  - `skill://FORGE-telemetry-watchdog/SKILL.md`
  - `skill://FORGE-telemetry-watchdog/_manifest`
  - `skill://FORGE-vault999-witness/SKILL.md`
  - `skill://FORGE-vault999-witness/_manifest`
  - `skill://FORGE-verify-runtime/SKILL.md`
  - `skill://FORGE-verify-runtime/_manifest`
  - `skill://FORGE-visual-qa-w3/SKILL.md`
  - `skill://FORGE-visual-qa-w3/_manifest`
  - `skill://FORGE-vps-docker/SKILL.md`
  - `skill://FORGE-vps-docker/_manifest`
  - `skill://FORGE-vps-runbook/SKILL.md`
  - `skill://FORGE-vps-runbook/_manifest`
  - `skill://FORGE-well-boundary-repair/SKILL.md`
  - `skill://FORGE-well-boundary-repair/_manifest`
  - `skill://HERMES-opencode-protocol/SKILL.md`
  - `skill://HERMES-opencode-protocol/_manifest`
  - `skill://KERNEL-trinity-33/SKILL.md`
  - `skill://KERNEL-trinity-33/_manifest`
  - `skill://RSI-recursive-improvement/SKILL.md`
  - `skill://RSI-recursive-improvement/_manifest`
  - `skill://aaa-pdf-voice-protocol/SKILL.md`
  - `skill://aaa-pdf-voice-protocol/_manifest`
  - `skill://apex-formal-constitution/SKILL.md`
  - `skill://apex-formal-constitution/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://apex_reversibility_test/SKILL.md`
  - `skill://apex_reversibility_test/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://apex_tool_approval_gate/SKILL.md`
  - `skill://apex_tool_approval_gate/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://arifos-constitutional-judge/SKILL.md`
  - `skill://arifos-constitutional-judge/_manifest`
  - `skill://asi_evidence_tier_express/SKILL.md`
  - `skill://asi_evidence_tier_express/_manifest`
  - `skill://asi_intent_hear/SKILL.md`
  - `skill://asi_intent_hear/_manifest`
  - `skill://asi_interface_adapt/SKILL.md`
  - `skill://asi_interface_adapt/_manifest`
  - `skill://asi_position_contrast/SKILL.md`
  - `skill://asi_position_contrast/_manifest`
  - `skill://asi_tone_read/SKILL.md`
  - `skill://asi_tone_read/_manifest`
  - `skill://asi_uncertainty_signal/SKILL.md`
  - `skill://asi_uncertainty_signal/_manifest`
  - `skill://atlas333-cognitive-geometry/SKILL.md`
  - `skill://atlas333-cognitive-geometry/_manifest`
  - `skill://audit-seal/SKILL.md`
  - `skill://audit-seal/_manifest`
  - `skill://causal555-pywhy/SKILL.md`
  - `skill://causal555-pywhy/_manifest`
  - `skill://check-work/SKILL.md`
  - `skill://check-work/_manifest`
  - `skill://code-review/SKILL.md`
  - `skill://code-review/_manifest`
  - `skill://create-skill/SKILL.md`
  - `skill://create-skill/_manifest`
  - `skill://docs/SKILL.md`
  - `skill://docs/_manifest`
  - `skill://federation-connect-headscale/SKILL.md`
  - `skill://federation-connect-headscale/_manifest`
  - `skill://federation-release-attestation/SKILL.md`
  - `skill://federation-release-attestation/_manifest`
  - `skill://forge-document-intelligence/SKILL.md`
  - `skill://forge-document-intelligence/_manifest`
  - `skill://geox-grounding/SKILL.md`
  - `skill://geox-grounding/_manifest`
  - `skill://help/SKILL.md`
  - `skill://help/_manifest`
  - `skill://imagine/SKILL.md`
  - `skill://imagine/_manifest`
  - `skill://kernel-bind/SKILL.md`
  - `skill://kernel-bind/_manifest`
  - `skill://know-language/SKILL.md`
  - `skill://know-language/_manifest`
  - `skill://know-math/SKILL.md`
  - `skill://know-math/_manifest`
  - `skill://know-physics/SKILL.md`
  - `skill://know-physics/_manifest`
  - `skill://knowledge/SKILL.md`
  - `skill://knowledge/_manifest`
  - `skill://memory-manage/SKILL.md`
  - `skill://memory-manage/_manifest`
  - `skill://observe-ground/SKILL.md`
  - `skill://observe-ground/_manifest`
  - `skill://reflective/SKILL.md`
  - `skill://reflective/_manifest`
  - `skill://route-dispatch/SKILL.md`
  - `skill://route-dispatch/_manifest`
  - `skill://runtime/SKILL.md`
  - `skill://runtime/_manifest`
  - `skill://scripts/SKILL.md`
  - `skill://scripts/_manifest`
  - `skill://substrate/SKILL.md`
  - `skill://substrate/_manifest`
  - `skill://verify-gate/SKILL.md`
  - `skill://verify-gate/_manifest`
  - `skill://warga/SKILL.md`
  - `skill://warga/_manifest`
  - `skill://wealth-claim-state/SKILL.md`
  - `skill://wealth-claim-state/_manifest`
  - `skill://xauusd-trading/SKILL.md`
  - `skill://xauusd-trading/_manifest`
  - `tree777://index`

### Prompt Names

**A-FORGE** (0 prompts):


**AAA** (0 prompts):


**GEOX** (0 prompts):


**WEALTH** (0 prompts):


**WELL** (0 prompts):


**arifOS** (21 prompts):
  - `111_sense`
  - `333_reason`
  - `555_critique`
  - `777_forge`
  - `888_judge`
  - `999_seal`
  - `agi_reply_protocol_v3`
  - `arif_init_prompt`
  - `arif_init_prompt_v3`
  - `constitutional_pre_flight`
  - `recursive_governed_loop`
  - `⚖ MARUAH`
  - `🌀 SABAR`
  - `🌊 WITNESS`
  - `🌱 BOOT`
  - `💎 SEAL`
  - `📜 REPLY`
  - `🔍 PREFLIGHT`
  - `🔒 JUDGE`
  - `🔥 FORGE`
  - `🧠 REASON`


## Attack Surface — Tool Scope Risk (BloodHound-style)

| Organ | Total Tools | CRITICAL | HIGH | MEDIUM | LOW | Risk Score |
|-------|-------------|----------|------|--------|-----|------------|
| arifOS | 8 | 3 | 1 | 1 | 3 | 1.25 |
| **Federation** | 8 | 3 | 1 | — | — | 1.25 |

### CRITICAL Tools — Direct F13 Reachability Risk

| Tool | Organ | Estimated Hops to F13 | Reason |
|------|-------|----------------------|--------|
| `arif_forge` | arifOS | 1 | keyword 'forge' suggests constitutional/admin authority |
| `arif_judge` | arifOS | 1 | keyword 'judge' suggests constitutional/admin authority |
| `arif_seal` | arifOS | 1 | keyword 'seal' suggests constitutional/admin authority |

## Score Impact

This snapshot converts *declared* operational status into *observed* operational status. It is the first step toward an institution-grade audit trail for the federation.

---
*Generated by scripts/federation_reality_probe.py — DITEMPA BUKAN DIBERI*