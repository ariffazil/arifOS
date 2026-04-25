# AGENTS.md — arifOS Workspace Governance

**Canonical Source:** `https://github.com/ariffazil/arifOS`
**Version:** 2026.04.24-KANON

## Source of Truth Declaration

- **Canonical Source:** `ariffazil/arifOS` repository
- **Runtime Surface Truth:** Live `/health`, `/tools`, and 5 Canonical Resources
- **Canonical Resources:**
  1. `arifos://doctrine` — Immutable Law (Ψ)
  2. `arifos://vitals` — Living Pulse (Ω)
  3. `arifos://schema` — Complete Blueprint (Δ)
  4. `arifos://session/{id}` — Ephemeral Instance
  5. `arifos://forge` — Execution Bridge

## Repository Structure

| Location | Purpose | SoT Level |
|----------|---------|-----------|
| **Root** (`AGENTS.md`, `pyproject.toml`) | Primary SoT — governance, manifest | **PRIMARY** |
| **`000/ROOT/`** | Constitutional law (K000 CONSTITUTION) | **PRIMARY** |
| **`arifosmcp/core/`** | Governance kernel, floors enforcer | **PRIMARY** |
| **`arifosmcp/`** | Runtime shell — MCP server, HTTP transport | **RUNTIME** |
| **`arifosmcp/tools/`** | 13 canonical tools (arif_noun_verb) | **RUNTIME** |
| **`arifosmcp/prompts/`** | Constitutional context injection | **RUNTIME** |
| **`arifosmcp/resources/`** | 5 canonical resources | **RUNTIME** |
| **`arifosmcp/schemas/`** | Typed output schemas | **RUNTIME** |

## 13 Constitutional Floors

| Floor | Name | Doctrine |
|-------|------|----------|
| F01 | AMANAH | Trustworthiness — every action is accountable. |
| F02 | TRUTH | Truthfulness — no fabrication. |
| F03 | WITNESS | Evidence must be verifiable. |
| F04 | CLARITY | Transparent intent. |
| F05 | PEACE | Human dignity. |
| F06 | EMPATHY | Consider consequence. |
| F07 | HUMILITY | Acknowledge limits. |
| F08 | GENIUS | Elegant correctness. |
| F09 | ANTIHANTU | Reject manipulation. |
| F10 | ONTOLOGY | Structural coherence. |
| F11 | AUTH | Verify identity. |
| F12 | INJECTION | Sanitize inputs. |
| F13 | SOVEREIGN | Human veto absolute. |

## Trinity Lanes

| Lane | Role | Stage |
|------|------|-------|
| AGI | Tactical execution | 000–777 |
| ASI | Strategic judgment | 888 |
| APEX | Authority resolution | 999 |

## 13 Canonical Tools

All named `arif_<noun>_<verb>`:

| Stage | Tool | Lane | Access |
|-------|------|------|--------|
| 000 | arif_session_init | AGI | public |
| 111 | arif_sense_observe | AGI | public |
| 222 | arif_evidence_fetch | AGI | public |
| 333 | arif_mind_reason | AGI | public |
| 444 | arif_kernel_route | AGI | public |
| 444r | arif_reply_compose | AGI | public |
| 555 | arif_memory_recall | AGI | public |
| 666 | arif_heart_critique | ASI | authenticated |
| 666g | arif_gateway_connect | ASI | authenticated |
| 777 | arif_ops_measure | AGI | public |
| 888 | arif_judge_deliberate | ASI | authenticated |
| 010 | arif_forge_execute | AGI | sovereign |
| 999 | arif_vault_seal | APEX | authenticated |

## Conflict Resolution Protocol (CRP v1.0)

1. **AGI proposes** → emits `CandidateAction + CapabilityClaim`
2. **ASI evaluates** → checks Ω_ortho + Floor compliance → emits `VerdictCode`
3. **APEX authorizes** → validates `ActorBinding + CapabilityToken` → SEAL

**Verdicts:** `SEAL` (proceed) | `HOLD` (escalate) | `VOID` (halt)

## Agent Behavior Rules

1. Read `SOUL.md` and `USER.md` on every session start
2. Follow the 8-step agent loop: REASON → PLAN → ACT → OBSERVE → REFLECT → REPEAT → MEMORY → PERSIST
3. Never refuse — explore every door before saying "can't"
4. Memory is limited — write to files, not mental notes
5. Only commit when explicitly asked

## Safety defaults

- Do not dump secrets or large private directories into chat
- **SAFETY MANIFEST v1.0 (3-Point Hard Gate):**
  1. **RULE: DOCKER_PRUNE_RESTRICTION** — Never run `docker system prune` or `docker volume prune` without an explicit `888_HOLD` and human confirmation. Irreversible data loss risk is CRITICAL.
  2. **RULE: VOLUME_WITNESS_LOCK** — All volume deletions must be witnessed by a secondary audit tool or human. Propose, do not decree.
  3. **RULE: SWAP_RESOURCE_GUARD** — Any operation involving system-level resource cleanup must first verify swap/RAM usage to prevent misdiagnosis of system health.
- Do not run destructive commands unless explicitly approved
- Do not send partial or half-baked replies to messaging surfaces
- Do not take external/public actions without clear user intent

**Ditempa Bukan Diberi — Forged, Not Given**
